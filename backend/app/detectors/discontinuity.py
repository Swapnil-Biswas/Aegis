"""
Module F: Human Editing and Paraphrasing Detection.
Identifies passage-level stylistic discontinuities, boundary transitions,
hybrid composition (alternating human/AI passages), and post-generation human edits.
"""

import math
import re
from collections import Counter
from typing import Dict, List, Any, Tuple
import numpy as np
from scipy.spatial.distance import jensenshannon

from app.core.preprocessor import PreprocessedDocument, PassageChunk, TextSpan
from app.detectors.base import BaseDetector, DetectorOutput, PassageScore


class DiscontinuityDetector(BaseDetector):
    """
    Forensic discontinuity and hybrid text engine.
    Measures Jensen-Shannon divergence between adjacent passages,
    detects style boundaries, and estimates hybrid composition ratios.
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(
            name="discontinuity_analysis",
            display_name="Discontinuity & Hybrid Text Analysis",
            weight=weight
        )

    def _get_char_distribution(self, text: str) -> Dict[str, float]:
        """Calculates normalized character 2-gram frequencies."""
        text = text.lower()
        if len(text) < 2:
            return {}
        bigrams = [text[i:i+2] for i in range(len(text)-1) if text[i].isalnum() or text[i+1].isalnum()]
        counts = Counter(bigrams)
        total = max(1, sum(counts.values()))
        return {bg: cnt / total for bg, cnt in counts.items()}

    def _compute_js_divergence(self, p1_text: str, p2_text: str) -> float:
        """
        Computes Jensen-Shannon Divergence (JSD) between character n-gram
        distributions of two consecutive passages.
        """
        dist1 = self._get_char_distribution(p1_text)
        dist2 = self._get_char_distribution(p2_text)

        vocab = sorted(list(set(dist1.keys()).union(set(dist2.keys()))))
        if not vocab:
            return 0.0

        vec1 = np.array([dist1.get(k, 1e-7) for k in vocab])
        vec2 = np.array([dist2.get(k, 1e-7) for k in vocab])

        vec1 = vec1 / np.sum(vec1)
        vec2 = vec2 / np.sum(vec2)

        jsd = jensenshannon(vec1, vec2, base=2)
        return float(jsd) if not math.isnan(jsd) else 0.0

    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        passages = doc.passages
        n_passages = len(passages)

        if n_passages < 2:
            return DetectorOutput(
                module_name=self.name,
                display_name=self.display_name,
                raw_score=0.5,
                calibrated_score=0.5,
                confidence=0.2,
                observations=["Single passage document; inter-passage discontinuity cannot be evaluated."],
                features={
                    "passage_count": float(n_passages),
                    "discontinuity_index": 0.0,
                    "boundary_shift_count": 0.0
                }
            )

        # 1. Compute pairwise JSD between adjacent passages
        jsd_values: List[float] = []
        boundary_shifts: List[Dict[str, Any]] = []

        for i in range(n_passages - 1):
            p_curr = passages[i]
            p_next = passages[i + 1]
            jsd = self._compute_js_divergence(p_curr.text, p_next.text)
            jsd_values.append(jsd)

            # High JSD between adjacent passages indicates an authorial or generation shift
            if jsd > 0.45:
                boundary_shifts.append({
                    "between_passages": (p_curr.passage_id, p_next.passage_id),
                    "char_boundary": p_next.start_char,
                    "js_divergence": round(jsd, 4)
                })

        mean_jsd = float(np.mean(jsd_values)) if jsd_values else 0.0
        max_jsd = float(np.max(jsd_values)) if jsd_values else 0.0
        std_jsd = float(np.std(jsd_values)) if jsd_values else 0.0

        # Discontinuity index: combination of peak shift and variance
        discontinuity_index = round(0.6 * max_jsd + 0.4 * (std_jsd * 2.0), 4)

        features: Dict[str, float] = {
            "passage_count": float(n_passages),
            "mean_js_divergence": round(mean_jsd, 4),
            "max_js_divergence": round(max_jsd, 4),
            "std_js_divergence": round(std_jsd, 4),
            "boundary_shift_count": float(len(boundary_shifts)),
            "discontinuity_index": discontinuity_index
        }

        # Scoring: High discontinuity indicates hybrid text (mixture of human and AI)
        # Moderate discontinuity indicates uniform author
        if discontinuity_index > 0.55:
            # Significant hybrid signature
            raw_score = 0.70
            verdict_note = "High stylistic discontinuity; probable composite text (human/AI mixture)."
        elif discontinuity_index < 0.25:
            raw_score = 0.40
            verdict_note = "Homogeneous stylistic texture throughout passages."
        else:
            raw_score = 0.50
            verdict_note = "Moderate inter-passage stylistic variation."

        calibrated_score = 1.0 / (1.0 + math.exp(-3.5 * (raw_score - 0.50)))
        confidence = 0.5 if n_passages < 3 else 0.85

        observations: List[str] = [verdict_note]
        if boundary_shifts:
            observations.append(
                f"Located {len(boundary_shifts)} significant stylistic shift point(s) "
                f"exceeding JSD threshold (peak JSD = {max_jsd:.2f})."
            )

        # Passage scores
        passage_scores: List[PassageScore] = []
        for idx, p in enumerate(passages):
            # Assign score based on neighboring transition JSD
            local_jsd = jsd_values[idx] if idx < len(jsd_values) else (jsd_values[-1] if jsd_values else 0.0)
            passage_scores.append(
                PassageScore(
                    passage_id=p.passage_id,
                    index=p.index,
                    score=round(min(1.0, local_jsd * 1.5), 3),
                    confidence=round(confidence, 3),
                    key_signals={"local_jsd": round(local_jsd, 4)},
                    summary=f"Adjacent JSD: {local_jsd:.3f}"
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
            contradictions=[],
            passage_scores=passage_scores,
            metadata={"boundary_shifts": boundary_shifts}
        )

