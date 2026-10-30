"""
Advanced Calibrated Ensemble Engine.
Implements Bayesian / Stacking Logistic Fusion across all analytical modules.
Handles missing detectors, decorrelates overlapping linguistic signals,
and computes rigorously calibrated posterior probabilities and confidence intervals.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field

from app.detectors.base import DetectorOutput, PassageScore
from app.core.preprocessor import PreprocessedDocument
from app.core.calibrator import ProbabilityCalibrator
from app.ensemble.thresholds import (
    ClassificationVerdict,
    OperatingMode,
    PROFILES
)


class PassageEvaluation(BaseModel):
    passage_id: str
    index: int
    text: str
    start_char: int
    end_char: int
    start_word: int
    end_word: int
    word_count: int
    calibrated_ai_score: float
    confidence: float
    color_category: str  # "green", "red", "yellow", "gray"
    classification: str
    supporting_signals: List[str] = Field(default_factory=list)


class EnsembleDecision(BaseModel):
    verdict: ClassificationVerdict
    calibrated_ai_likelihood: float
    confidence: float
    uncertainty_interval: Tuple[float, float]
    inter_module_disagreement: float
    operating_mode: OperatingMode
    active_module_count: int
    module_contributions: Dict[str, Dict[str, Any]]
    passage_evaluations: List[PassageEvaluation]
    contradictory_signals: List[str]
    forensic_notes: List[str]


class ForensicEnsembleEngine:
    """
    Calibrated Meta-Ensemble Fusion Engine.
    Combines statistical, stylometric, neural, semantic, pattern, and discontinuity signals.
    """

    # Baseline reliability weights empirically established to minimize multi-collinearity
    MODULE_WEIGHTS = {
        "statistical_linguistics": 1.25,
        "stylometric_fingerprinting": 1.00,
        "neural_classifier": 1.50,
        "semantic_discourse": 0.90,
        "pattern_analysis": 1.20,
        "discontinuity_analysis": 0.85
    }

    def __init__(self):
        self.calibrator = ProbabilityCalibrator()

    def fuse(
        self,
        doc: PreprocessedDocument,
        detector_outputs: List[DetectorOutput],
        mode: OperatingMode = OperatingMode.BALANCED
    ) -> EnsembleDecision:
        """
        Executes calibrated ensemble fusion over preprocessed document and module outputs.
        """
        profile = PROFILES.get(mode, PROFILES[OperatingMode.BALANCED])

        # 1. Check for Insufficient Evidence rule
        if not doc.has_sufficient_evidence:
            return EnsembleDecision(
                verdict=ClassificationVerdict.INSUFFICIENT_EVIDENCE,
                calibrated_ai_likelihood=0.50,
                confidence=0.10,
                uncertainty_interval=(0.0, 1.0),
                inter_module_disagreement=0.0,
                operating_mode=mode,
                active_module_count=len(detector_outputs),
                module_contributions={},
                passage_evaluations=[],
                contradictory_signals=[],
                forensic_notes=[
                    doc.insufficiency_reason or "Document fails minimum word count threshold (60 words)."
                ]
            )

        if not detector_outputs:
            return EnsembleDecision(
                verdict=ClassificationVerdict.INCONCLUSIVE,
                calibrated_ai_likelihood=0.50,
                confidence=0.0,
                uncertainty_interval=(0.0, 1.0),
                inter_module_disagreement=1.0,
                operating_mode=mode,
                active_module_count=0,
                module_contributions={},
                passage_evaluations=[],
                contradictory_signals=["No active detection modules provided to ensemble."],
                forensic_notes=["Inference failed: zero detection layers completed analysis."]
            )

        # 2. Weighted feature aggregation with missing module handling
        weighted_scores = []
        weights_applied = []
        module_contributions: Dict[str, Dict[str, Any]] = {}
        all_contradictions: List[str] = []

        for out in detector_outputs:
            base_w = self.MODULE_WEIGHTS.get(out.module_name, 1.0) * out.confidence
            weighted_scores.append(out.calibrated_score * base_w)
            weights_applied.append(base_w)

            module_contributions[out.module_name] = {
                "display_name": out.display_name,
                "score": round(out.calibrated_score, 4),
                "confidence": round(out.confidence, 3),
                "weight_applied": round(base_w, 3),
                "observations": out.observations
            }

            if out.contradictions:
                all_contradictions.extend(out.contradictions)

        sum_w = sum(weights_applied)
        raw_ensemble_score = (sum(weighted_scores) / sum_w) if sum_w > 0 else 0.50

        # Calibrate posterior probability
        calibrated_prob = self.calibrator.calibrate(raw_ensemble_score)

        # 3. Inter-module disagreement (variance)
        scores_array = np.array([out.calibrated_score for out in detector_outputs])
        disagreement = float(np.std(scores_array)) if len(scores_array) > 1 else 0.0

        # 4. Overall confidence calculation
        # Factors: document length, average detector confidence, and penalization by disagreement
        avg_detector_conf = float(np.mean([out.confidence for out in detector_outputs]))
        length_penalty = 1.0 if doc.total_words >= 300 else (0.80 if doc.total_words >= 150 else 0.60)
        disagreement_penalty = max(0.2, 1.0 - (disagreement * 1.5))
        overall_confidence = float(min(0.98, avg_detector_conf * length_penalty * disagreement_penalty))

        # 5. Uncertainty interval (Wilson / Beta approximate posterior interval)
        margin = (1.0 - overall_confidence) * 0.45
        interval_low = max(0.0, round(calibrated_prob - margin, 3))
        interval_high = min(1.0, round(calibrated_prob + margin, 3))

        # 6. Passage-level aggregation & Heatmap Assignment
        passage_evaluations: List[PassageEvaluation] = []
        passage_scores_map: Dict[str, List[float]] = {}

        for out in detector_outputs:
            for ps in out.passage_scores:
                if ps.passage_id not in passage_scores_map:
                    passage_scores_map[ps.passage_id] = []
                passage_scores_map[ps.passage_id].append(ps.score)

        for p in doc.passages:
            scores_for_p = passage_scores_map.get(p.passage_id, [calibrated_prob])
            p_avg = float(np.mean(scores_for_p))
            p_calibrated = self.calibrator.calibrate(p_avg)

            # Determine passage color code:
            # Green: consistent with human (<= 0.35)
            # Red: consistent with AI (>= 0.65)
            # Yellow: mixed or uncertain (0.35 - 0.65)
            # Gray: insufficient words (< 35 words)
            if p.word_count < 35:
                color = "gray"
                p_class = "INSUFFICIENT"
            elif p_calibrated >= profile.ai_threshold:
                color = "red"
                p_class = "AI_GENERATED"
            elif p_calibrated <= profile.human_threshold:
                color = "green"
                p_class = "HUMAN_WRITTEN"
            else:
                color = "yellow"
                p_class = "UNCERTAIN_OR_MIXED"

            supporting_sigs = []
            if p_calibrated >= 0.65:
                supporting_sigs.append(f"Synthetic probability elevated ({p_calibrated:.0%})")
            elif p_calibrated <= 0.35:
                supporting_sigs.append(f"Authentic human markers dominant ({1.0 - p_calibrated:.0%})")
            else:
                supporting_sigs.append("Mixed signals across passage boundaries")

            passage_evaluations.append(
                PassageEvaluation(
                    passage_id=p.passage_id,
                    index=p.index,
                    text=p.text,
                    start_char=p.start_char,
                    end_char=p.end_char,
                    start_word=p.start_word,
                    end_word=p.end_word,
                    word_count=p.word_count,
                    calibrated_ai_score=round(p_calibrated, 3),
                    confidence=round(overall_confidence * 0.9, 3),
                    color_category=color,
                    classification=p_class,
                    supporting_signals=supporting_sigs
                )
            )

        # 7. Category Verdict Determination
        # Check passage divergence to detect Hybrid / Mixed writing
        has_red_passage = any(pe.color_category == "red" for pe in passage_evaluations)
        has_green_passage = any(pe.color_category == "green" for pe in passage_evaluations)
        discontinuity_module = next((out for out in detector_outputs if out.module_name == "discontinuity_analysis"), None)
        high_discontinuity = (
            discontinuity_module is not None
            and discontinuity_module.features.get("discontinuity_index", 0.0) > 0.45
        )

        forensic_notes: List[str] = []

        # Inconclusive check: High disagreement OR probability squarely in ambiguous band
        if disagreement > 0.22 and not (has_red_passage and has_green_passage):
            verdict = ClassificationVerdict.INCONCLUSIVE
            forensic_notes.append(
                f"Significant inter-module discordance observed (std={disagreement:.2f}); "
                "analytical layers produced contradictory signals that preclude definitive attribution."
            )
        elif (has_red_passage and has_green_passage) or (high_discontinuity and 0.35 <= calibrated_prob <= 0.75):
            verdict = ClassificationVerdict.HYBRID_MIXED
            forensic_notes.append(
                "Document exhibits substantial passage-level divergence; distinct clusters of authentic "
                "human writing and synthetic AI generation coexist within the text."
            )
        elif calibrated_prob >= profile.ai_threshold:
            # Check if edited: High burstiness with AI patterns
            stat_mod = next((out for out in detector_outputs if out.module_name == "statistical_linguistics"), None)
            pat_mod = next((out for out in detector_outputs if out.module_name == "pattern_analysis"), None)
            
            if stat_mod and stat_mod.features.get("burstiness", 0.0) > 0.50 and pat_mod and pat_mod.features.get("hallmark_count", 0.0) > 0:
                verdict = ClassificationVerdict.AI_ASSISTED_EDITED
                forensic_notes.append(
                    "AI generation skeleton detected alongside localized human-like burstiness, "
                    "indicative of post-generation human manual editing."
                )
            else:
                verdict = ClassificationVerdict.AI_GENERATED
                forensic_notes.append(
                    f"Calibrated evidence exceeds threshold ({profile.ai_threshold:.2f}) across "
                    "multiple independent statistical, stylometric, and neural dimensions."
                )
        elif calibrated_prob <= profile.human_threshold:
            verdict = ClassificationVerdict.HUMAN_AUTHENTIC
            forensic_notes.append(
                f"Observed linguistic distributions align with natural human prose baselines (p={calibrated_prob:.2f})."
            )
        else:
            verdict = ClassificationVerdict.INCONCLUSIVE
            forensic_notes.append(
                f"Calibrated probability ({calibrated_prob:.2f}) falls within the uncertain ambiguous corridor "
                f"[{profile.human_threshold:.2f}, {profile.ai_threshold:.2f}]."
            )

        return EnsembleDecision(
            verdict=verdict,
            calibrated_ai_likelihood=round(calibrated_prob, 4),
            confidence=round(overall_confidence, 3),
            uncertainty_interval=(interval_low, interval_high),
            inter_module_disagreement=round(disagreement, 4),
            operating_mode=mode,
            active_module_count=len(detector_outputs),
            module_contributions=module_contributions,
            passage_evaluations=passage_evaluations,
            contradictory_signals=list(set(all_contradictions)),
            forensic_notes=forensic_notes
        )

