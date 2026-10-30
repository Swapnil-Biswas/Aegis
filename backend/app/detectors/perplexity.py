"""
Module H: Language-Model Perplexity Analysis.
Zero-shot signal: scores the text under a small causal language model
(default: HuggingFaceTB/SmolLM2-135M, Apache-2.0). Machine-generated text tends to
have lower token-level negative log-likelihood (NLL) than human writing, and lower
NLL relative to the model's own predictive entropy. Because it is not trained on
any detection dataset it complements the fine-tuned classifier.
"""

import math
import threading
from typing import Dict, List, Optional, Tuple

from app.core.preprocessor import PreprocessedDocument
from app.detectors.base import BaseDetector, DetectorOutput, PassageScore
from app.config import config


class _SharedLM:
    _lock = threading.Lock()
    _loaded = False
    tokenizer = None
    model = None
    device = "cpu"
    load_error: Optional[str] = None

    @classmethod
    def get(cls):
        if cls._loaded:
            return cls
        with cls._lock:
            if cls._loaded:
                return cls
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM

                cls.tokenizer = AutoTokenizer.from_pretrained(config.perplexity_model_name)
                cls.model = AutoModelForCausalLM.from_pretrained(config.perplexity_model_name)
                cls.device = config.device
                cls.model.to(cls.device).eval()
            except Exception as e:
                cls.model = None
                cls.load_error = f"{type(e).__name__}: {e}"
            cls._loaded = True
        return cls


class LanguageModelPerplexityDetector(BaseDetector):
    """Token-level likelihood analysis under a reference causal language model."""

    MAX_TOKENS = 512
    # Logistic mapping fitted on the AEGIS development split (see app/evaluation/fit_fusion.py):
    # z = A_NLL * mean_nll + A_RATIO * (mean_nll / mean_entropy) + B
    A_NLL = -2.3451
    A_RATIO = -0.5091
    B = 6.6799

    def __init__(self, weight: float = 1.0):
        super().__init__(
            name="lm_perplexity",
            display_name="Language-Model Perplexity Analysis",
            weight=weight
        )

    @property
    def available(self) -> bool:
        return config.enable_neural_engine and _SharedLM.get().model is not None

    def _measure(self, text: str) -> Tuple[float, float, int]:
        """Returns (mean NLL, mean predictive entropy, scored token count)."""
        import torch

        lm = _SharedLM.get()
        ids = lm.tokenizer(text, return_tensors="pt", truncation=True, max_length=self.MAX_TOKENS).input_ids
        if ids.shape[1] < 8:
            return float("nan"), float("nan"), int(ids.shape[1])
        ids = ids.to(lm.device)
        with torch.no_grad():
            logits = lm.model(ids).logits[0, :-1].float()
        logp = torch.log_softmax(logits, -1)
        nll = float(-logp.gather(1, ids[0, 1:, None]).mean())
        ent = float(-(logp.exp() * logp).sum(-1).mean())
        return nll, ent, int(ids.shape[1])

    def score_from_features(self, nll: float, ent: float) -> float:
        ratio = nll / max(ent, 1e-3)
        z = self.A_NLL * nll + self.A_RATIO * ratio + self.B
        return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))

    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        n_words = doc.total_words
        if not self.available or n_words < 15:
            if self.available:
                reason = "Insufficient text length for language-model likelihood analysis."
            else:
                reason = (f"Reference language model unavailable ({_SharedLM.load_error or 'disabled'}); "
                          "ensemble used remaining layers.")
            return DetectorOutput(
                module_name=self.name, display_name=self.display_name,
                raw_score=0.5, calibrated_score=0.5, confidence=0.0,
                observations=[reason], features={"word_count": float(n_words)},
                metadata={"available": False}
            )

        nll, ent, n_tok = self._measure(doc.sanitized_text)
        score = self.score_from_features(nll, ent)
        confidence = float(min(0.9, 0.3 + 0.6 * min(1.0, n_tok / 300.0)))

        features: Dict[str, float] = {
            "mean_token_nll": round(nll, 4),
            "perplexity": round(math.exp(nll), 3),
            "mean_predictive_entropy": round(ent, 4),
            "nll_entropy_ratio": round(nll / max(ent, 1e-3), 4),
            "scored_tokens": float(n_tok),
        }

        observations: List[str] = []
        if score > 0.7:
            observations.append(
                f"Text is unusually predictable under the reference language model "
                f"(perplexity {math.exp(nll):.1f}), a pattern typical of machine generation."
            )
        elif score < 0.3:
            observations.append(
                f"Token choices are less predictable than typical model output "
                f"(perplexity {math.exp(nll):.1f}), consistent with human writing."
            )
        else:
            observations.append(f"Language-model perplexity ({math.exp(nll):.1f}) is in the overlapping range.")

        passage_scores: List[PassageScore] = []
        for p in doc.passages if len(doc.passages) > 1 else []:
            p_nll, p_ent, p_tok = self._measure(p.text)
            if math.isnan(p_nll):
                continue
            p_score = self.score_from_features(p_nll, p_ent)
            passage_scores.append(
                PassageScore(
                    passage_id=p.passage_id, index=p.index, score=round(p_score, 4),
                    confidence=round(min(0.85, p_tok / 200.0), 3),
                    key_signals={"perplexity": round(math.exp(p_nll), 2)},
                    summary=f"Perplexity {math.exp(p_nll):.1f}"
                )
            )

        return DetectorOutput(
            module_name=self.name, display_name=self.display_name,
            raw_score=round(score, 4), calibrated_score=round(score, 4),
            confidence=round(confidence, 3), features=features,
            observations=observations, contradictions=[],
            passage_scores=passage_scores,
            metadata={"model": config.perplexity_model_name, "available": True}
        )
