"""
Module C: Neural Detection Engine.
Fine-tuned RoBERTa sequence classifier (default: fakespot-ai/roberta-base-ai-text-detection-v1,
Apache-2.0) applied over 512-token windows. The model is loaded lazily and shared
across the process; if it cannot be loaded the module reports itself unavailable
and the ensemble falls back to the remaining layers.
"""

import os
import re
import threading
from html import unescape
from typing import Dict, List, Optional, Tuple

from app.core.preprocessor import PreprocessedDocument
from app.detectors.base import BaseDetector, DetectorOutput, PassageScore
from app.config import config


def clean_text(t: str) -> str:
    """Input normalisation recommended by the model authors (markdown stripped, single-spaced)."""
    t = re.sub(r'```.*?```', '', t, flags=re.DOTALL)
    t = re.sub(r'`[^`]*`', '', t)
    t = re.sub(r'!\[.*?\]\(.*?\)', '', t)
    t = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', t)
    t = re.sub(r'(\*\*|__)(.*?)\1', r'\2', t)
    t = re.sub(r'#+ ', '', t)
    t = re.sub(r'<.*?>', '', t)
    t = unescape(t)
    t = re.sub(r'[\n\t\r]', ' ', t).replace(" ,", ",")
    return re.sub(r' +', ' ', t).strip()


class _SharedClassifier:
    """Process-wide lazy holder so every pipeline shares one copy of the weights."""

    _lock = threading.Lock()
    _loaded = False
    tokenizer = None
    model = None
    device = "cpu"
    ai_label_index = 1
    load_error: Optional[str] = None

    @classmethod
    def get(cls):
        if cls._loaded:
            return cls
        with cls._lock:
            if cls._loaded:
                return cls
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification

                name = config.neural_model_name
                cls.tokenizer = AutoTokenizer.from_pretrained(name)
                cls.model = AutoModelForSequenceClassification.from_pretrained(name)
                # We window long inputs ourselves; silence the "longer than max length" warning.
                cls.tokenizer.model_max_length = 10 ** 9
                cls.device = config.device
                cls.model.to(cls.device).eval()
                labels = {v.lower(): k for k, v in cls.model.config.id2label.items()}
                cls.ai_label_index = int(labels.get("ai", labels.get("fake", labels.get("chatgpt", 1))))
            except Exception as e:  # network/offline/missing weights
                cls.model = None
                cls.load_error = f"{type(e).__name__}: {e}"
            cls._loaded = True
        return cls


class NeuralClassifierDetector(BaseDetector):
    """
    Dedicated Neural Detection Engine backed by a fine-tuned transformer classifier.
    """

    MAX_TOKENS = 512

    def __init__(self, weight: float = 1.5, device: Optional[str] = None):
        super().__init__(
            name="neural_classifier",
            display_name="Neural Transformer Classifier",
            weight=weight
        )
        self._requested_device = device

    @property
    def available(self) -> bool:
        return config.enable_neural_engine and _SharedClassifier.get().model is not None

    def _score_texts(self, texts: List[str]) -> List[Tuple[float, int]]:
        """Returns (p_ai, token_count) for each text, averaging over 512-token windows."""
        import torch

        clf = _SharedClassifier.get()
        results: List[Tuple[float, int]] = []
        for text in texts:
            ids = clf.tokenizer(clean_text(text), add_special_tokens=False)["input_ids"]
            if not ids:
                results.append((0.5, 0))
                continue
            win = self.MAX_TOKENS - 2
            windows = [ids[i:i + win] for i in range(0, len(ids), win)]
            # Drop a tiny trailing window; it is mostly noise.
            if len(windows) > 1 and len(windows[-1]) < 64:
                windows = windows[:-1]
            probs, weights = [], []
            for w in windows:
                inp = torch.tensor([[clf.tokenizer.cls_token_id] + w + [clf.tokenizer.sep_token_id]], device=clf.device)
                with torch.inference_mode():
                    logits = clf.model(input_ids=inp).logits[0]
                probs.append(float(torch.softmax(logits, -1)[clf.ai_label_index]))
                weights.append(len(w))
            p = sum(pr * wt for pr, wt in zip(probs, weights)) / sum(weights)
            results.append((p, len(ids)))
        return results

    def _unavailable(self, n_words: int, reason: str) -> DetectorOutput:
        return DetectorOutput(
            module_name=self.name,
            display_name=self.display_name,
            raw_score=0.5,
            calibrated_score=0.5,
            confidence=0.0,
            observations=[reason],
            features={"word_count": float(n_words)},
            metadata={"available": False}
        )

    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        n_words = doc.total_words
        if not config.enable_neural_engine:
            return self._unavailable(n_words, "Neural classifier disabled by configuration (AEGIS_ENABLE_NEURAL=0).")
        if not self.available:
            return self._unavailable(
                n_words,
                f"Neural classifier unavailable ({_SharedClassifier.load_error}); ensemble used remaining layers."
            )
        if n_words < 15:
            return self._unavailable(n_words, "Insufficient text length for transformer neural classification.")

        (p_ai, n_tokens), = self._score_texts([doc.sanitized_text])
        dist_from_margin = abs(p_ai - 0.5) * 2.0
        length_conf = min(1.0, n_words / 250.0)
        confidence = float(min(0.95, 0.5 * dist_from_margin + 0.5 * length_conf))

        features: Dict[str, float] = {
            "classifier_ai_probability": round(p_ai, 4),
            "token_count": float(n_tokens),
        }

        observations: List[str] = []
        if p_ai > 0.75:
            observations.append(
                f"Fine-tuned transformer classifier assigns high probability to machine generation (p={p_ai:.2f})."
            )
        elif p_ai < 0.25:
            observations.append(
                f"Fine-tuned transformer classifier output aligns with human-authored text (p={p_ai:.2f})."
            )
        else:
            observations.append(
                f"Transformer classifier output is ambiguous (p={p_ai:.2f})."
            )

        passage_scores: List[PassageScore] = []
        if len(doc.passages) > 1:
            scored = self._score_texts([p.text for p in doc.passages])
            for p, (p_score, _) in zip(doc.passages, scored):
                passage_scores.append(
                    PassageScore(
                        passage_id=p.passage_id,
                        index=p.index,
                        score=round(p_score, 4),
                        confidence=round(min(1.0, p.word_count / 120.0) * 0.9, 3),
                        key_signals={"p_ai": round(p_score, 3)},
                        summary=f"Neural p(AI) = {p_score:.2f}"
                    )
                )
        elif doc.passages:
            p = doc.passages[0]
            passage_scores.append(
                PassageScore(passage_id=p.passage_id, index=p.index, score=round(p_ai, 4),
                             confidence=round(confidence, 3), key_signals={"p_ai": round(p_ai, 3)},
                             summary=f"Neural p(AI) = {p_ai:.2f}")
            )

        return DetectorOutput(
            module_name=self.name,
            display_name=self.display_name,
            raw_score=round(p_ai, 4),
            calibrated_score=round(p_ai, 4),
            confidence=round(confidence, 3),
            features=features,
            observations=observations,
            contradictions=[],
            passage_scores=passage_scores,
            metadata={"device": _SharedClassifier.device, "model": config.neural_model_name, "available": True}
        )
