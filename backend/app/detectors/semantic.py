"""
Module D: Semantic and Discourse Analysis.
Evaluates discourse cohesion, sentence-to-sentence semantic similarity trajectories,
topical drift, semantic redundancy, and repetitive conclusion patterns.
"""

import math
import re
from collections import Counter
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.preprocessor import PreprocessedDocument, PassageChunk, TextSpan
from app.detectors.base import BaseDetector, DetectorOutput, PassageScore


class SemanticDiscourseDetector(BaseDetector):
    """
    Forensic semantic and discourse flow engine.
    Analyzes thematic progression, argument development, and semantic entropy.
    AI generation often presents an unnaturally smooth, predictable semantic corridor.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(
            name="semantic_discourse",
            display_name="Semantic & Discourse Analysis",
            weight=weight
        )
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            max_features=500
        )

    def _compute_consecutive_similarities(self, sentences: List[TextSpan]) -> Dict[str, float]:
        """
        Calculates cosine similarity trajectory between consecutive sentences.
        Human writing typically has high variance (varied jumps and pivots).
        AI text typically maintains a tight, uniform semantic similarity corridor (mean 0.35-0.65, low std).
        """
        if len(sentences) < 3:
            return {
                "mean_consecutive_similarity": 0.30,
                "std_consecutive_similarity": 0.20,
                "smoothness_index": 0.50
            }

        texts = [s.text for s in sentences if s.word_count >= 3]
        if len(texts) < 3:
            return {
                "mean_consecutive_similarity": 0.30,
                "std_consecutive_similarity": 0.20,
                "smoothness_index": 0.50
            }

        try:
            tfidf_mat = self.vectorizer.fit_transform(texts).toarray()
            # Cosine similarity between sentence i and sentence i+1
            similarities = []
            for i in range(len(tfidf_mat) - 1):
                vec_a = tfidf_mat[i]
                vec_b = tfidf_mat[i + 1]
                norm_a = np.linalg.norm(vec_a)
                norm_b = np.linalg.norm(vec_b)
                if norm_a > 0 and norm_b > 0:
                    sim = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
                else:
                    sim = 0.0
                similarities.append(sim)

            if not similarities:
                return {
                    "mean_consecutive_similarity": 0.30,
                    "std_consecutive_similarity": 0.20,
                    "smoothness_index": 0.50
                }

            mean_sim = float(np.mean(similarities))
            std_sim = float(np.std(similarities))
            # Smoothness index: higher indicates unnaturally steady coherence
            smoothness = mean_sim * (1.0 / (std_sim + 0.05))

            return {
                "mean_consecutive_similarity": round(mean_sim, 4),
                "std_consecutive_similarity": round(std_sim, 4),
                "smoothness_index": round(float(smoothness), 4)
            }
        except Exception:
            return {
                "mean_consecutive_similarity": 0.30,
                "std_consecutive_similarity": 0.20,
                "smoothness_index": 0.50
            }

    def _compute_semantic_redundancy(self, paragraphs: List[TextSpan]) -> Dict[str, float]:
        """
        Detects repetitive explanations and redundant conclusion patterns
        where the final paragraph recycles earlier vocabulary without new concepts.
        """
        if len(paragraphs) < 2:
            return {"conclusion_redundancy": 0.0, "inter_paragraph_overlap": 0.0}

        para_texts = [p.text for p in paragraphs if p.word_count >= 10]
        if len(para_texts) < 2:
            return {"conclusion_redundancy": 0.0, "inter_paragraph_overlap": 0.0}

        try:
            p_vecs = self.vectorizer.fit_transform(para_texts).toarray()
            # Compare final paragraph with prior paragraphs
            last_vec = p_vecs[-1]
            last_norm = np.linalg.norm(last_vec)
            
            overlaps = []
            for i in range(len(p_vecs) - 1):
                norm_i = np.linalg.norm(p_vecs[i])
                if norm_i > 0 and last_norm > 0:
                    sim = float(np.dot(p_vecs[i], last_vec) / (norm_i * last_norm))
                    overlaps.append(sim)

            conclusion_redundancy = float(np.max(overlaps)) if overlaps else 0.0
            avg_overlap = float(np.mean(overlaps)) if overlaps else 0.0

            return {
                "conclusion_redundancy": round(conclusion_redundancy, 4),
                "inter_paragraph_overlap": round(avg_overlap, 4)
            }
        except Exception:
            return {"conclusion_redundancy": 0.0, "inter_paragraph_overlap": 0.0}

    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        n_words = doc.total_words
        if n_words < 20:
            return DetectorOutput(
                module_name=self.name,
                display_name=self.display_name,
                raw_score=0.5,
                calibrated_score=0.5,
                confidence=0.1,
                observations=["Insufficient discourse length to evaluate semantic progression."],
                features={"word_count": float(n_words)}
            )

        sim_stats = self._compute_consecutive_similarities(doc.sentences)
        redundancy_stats = self._compute_semantic_redundancy(doc.paragraphs)

        features: Dict[str, float] = {
            **sim_stats,
            **redundancy_stats
        }

        # Scoring logic
        # AI hallmarks in discourse:
        # - High smoothness index (> 2.5), indicating steady semantic drift without sharp narrative shifts
        # - High conclusion redundancy (> 0.65), summarizing prior points formulaically
        # - Low std of consecutive similarity (< 0.08)

        ai_score = 0.0
        weights = 0.0

        smooth = sim_stats["smoothness_index"]
        if smooth > 2.8:
            ai_score += 2.0 * 0.85
        elif smooth > 1.8:
            ai_score += 2.0 * 0.65
        elif smooth < 0.9:
            ai_score += 2.0 * 0.25
        else:
            ai_score += 2.0 * 0.45
        weights += 2.0

        conc_red = redundancy_stats["conclusion_redundancy"]
        if conc_red > 0.65:
            ai_score += 1.5 * 0.80
        elif conc_red > 0.45:
            ai_score += 1.5 * 0.60
        else:
            ai_score += 1.5 * 0.35
        weights += 1.5

        raw_score = ai_score / weights
        calibrated_score = 1.0 / (1.0 + math.exp(-3.5 * (raw_score - 0.50)))
        confidence = 0.35 if n_words < 80 else (0.70 if n_words < 200 else 0.88)

        observations: List[str] = []
        contradictions: List[str] = []

        if smooth > 2.5:
            observations.append(
                f"Consecutive sentence semantic smoothness index is high ({smooth:.2f}), "
                "demonstrating synthetic topic corridor stability."
            )
        elif smooth < 1.0:
            observations.append(
                f"High discourse transition variance ({sim_stats['std_consecutive_similarity']:.2f}) "
                "indicates natural human narrative pivot dynamics."
            )

        if conc_red > 0.60:
            observations.append(
                f"Final paragraph exhibits significant semantic repetition ({conc_red:.1%}) with earlier sections, "
                "a common marker of model conclusion synthesis."
            )

        # Passage scores
        passage_scores: List[PassageScore] = []
        for p in doc.passages:
            p_sents = [doc.sentences[i] for i in p.sentence_indices if i < len(doc.sentences)]
            p_stats = self._compute_consecutive_similarities(p_sents)
            p_score = 0.5
            if p_stats["smoothness_index"] > 2.2:
                p_score = 0.72
            elif p_stats["smoothness_index"] < 1.0:
                p_score = 0.30

            passage_scores.append(
                PassageScore(
                    passage_id=p.passage_id,
                    index=p.index,
                    score=round(p_score, 3),
                    confidence=round(confidence * 0.85, 3),
                    key_signals={"smoothness_index": p_stats["smoothness_index"]},
                    summary=f"Smoothness Index = {p_stats['smoothness_index']:.2f}"
                )
            )

        return DetectorOutput(
            module_name=self.name,
            display_name=self.display_name,
            raw_score=round(float(raw_score), 4),
            calibrated_score=round(float(calibrated_score), 4),
            confidence=round(float(confidence), 3),
            features=features,
            observations=observations,
            contradictions=contradictions,
            passage_scores=passage_scores
        )

