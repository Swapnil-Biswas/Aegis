"""
Advanced Calibrated Ensemble Engine.
Implements stacking logistic fusion across all analytical modules.
Handles missing detectors with dedicated weight tiers and computes calibrated
posterior probabilities and confidence intervals.
"""

import json
import math
import os
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field

from app.detectors.base import DetectorOutput
from app.core.preprocessor import PreprocessedDocument
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


WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fusion_weights.json")

# Used only if fusion_weights.json is missing (e.g. a stripped-down install).
_FALLBACK_TIERS = {
    "heuristic_only": {
        "intercept": 0.0,
        "coefficients": {
            "statistical_linguistics": 1.0, "stylometric_fingerprinting": 1.0,
            "semantic_discourse": 0.5, "pattern_analysis": 0.5,
        },
    }
}


def _logit(p: float) -> float:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1.0 - p))


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))


class ForensicEnsembleEngine:
    """
    Calibrated stacking fusion.
    A logistic-regression meta-model (fitted by app/evaluation/fit_fusion.py on a
    labelled development split) combines the logit of each module score. A separate
    weight tier is used when the transformer modules are unavailable, so a missing
    model degrades accuracy instead of silently injecting a neutral 0.5.
    """

    def __init__(self, weights_path: Optional[str] = None):
        path = weights_path or WEIGHTS_PATH
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.tiers: Dict[str, Dict[str, Any]] = json.load(f)["tiers"]
        except (OSError, ValueError, KeyError):
            self.tiers = _FALLBACK_TIERS

    @staticmethod
    def _is_active(out: DetectorOutput) -> bool:
        return out.metadata.get("available", True) and out.confidence > 0.0

    def _select_tier(self, active: set) -> Tuple[str, Dict[str, Any]]:
        for name in ("full", "no_classifier", "heuristic_only"):
            tier = self.tiers.get(name)
            if tier and set(tier["coefficients"]).issubset(active):
                return name, tier
        name = next(iter(self.tiers))
        return name, self.tiers[name]

    @staticmethod
    def _stack(tier: Dict[str, Any], scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        contributions = {
            m: c * _logit(scores.get(m, 0.5)) for m, c in tier["coefficients"].items()
        }
        # Never report absolute certainty in either direction.
        prob = min(0.999, max(0.001, _sigmoid(tier["intercept"] + sum(contributions.values()))))
        return prob, contributions

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

        active_outputs = [o for o in detector_outputs if self._is_active(o)]
        if not active_outputs:
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

        # 2. Stacked fusion over the modules that actually ran
        doc_scores = {o.module_name: o.calibrated_score for o in active_outputs}
        tier_name, tier = self._select_tier(set(doc_scores))
        calibrated_prob, contributions = self._stack(tier, doc_scores)

        module_contributions: Dict[str, Dict[str, Any]] = {}
        all_contradictions: List[str] = []
        for out in detector_outputs:
            module_contributions[out.module_name] = {
                "display_name": out.display_name,
                "score": round(out.calibrated_score, 4),
                "confidence": round(out.confidence, 3),
                "weight_applied": round(tier["coefficients"].get(out.module_name, 0.0), 3),
                "logit_contribution": round(contributions.get(out.module_name, 0.0), 3),
                "active": out.module_name in contributions,
                "observations": out.observations
            }
            if out.contradictions:
                all_contradictions.extend(out.contradictions)

        # 3. Inter-module disagreement: share of weighted evidence (including the prior
        # intercept) pointing against the verdict. On the held-out split, documents above
        # 0.45 were misclassified ~43% of the time versus ~3% below it.
        direction = 1.0 if calibrated_prob >= 0.5 else -1.0
        evidence = list(contributions.values()) + [tier["intercept"]]
        total_mass = sum(abs(v) for v in evidence)
        opposing = sum(abs(v) for v in evidence if v * direction < 0)
        disagreement = float(opposing / total_mass) if total_mass > 0 else 0.0

        # 4. Overall confidence: decisiveness of the posterior, evidence length, agreement
        decisiveness = abs(calibrated_prob - 0.5) * 2.0
        length_factor = 1.0 if doc.total_words >= 300 else (0.85 if doc.total_words >= 150 else 0.65)
        tier_factor = {"full": 1.0, "no_classifier": 0.85}.get(tier_name, 0.65)
        overall_confidence = float(min(
            0.98,
            (0.35 + 0.65 * decisiveness) * length_factor * tier_factor * (1.0 - 0.5 * disagreement)
        ))

        # 5. Uncertainty interval (approximate, widened for low confidence)
        margin = (1.0 - overall_confidence) * 0.45
        interval_low = max(0.001, round(calibrated_prob - margin, 3))
        interval_high = min(0.999, round(calibrated_prob + margin, 3))

        # 6. Passage-level stacking. Discontinuity passage values are divergence
        # measurements, not AI likelihoods, so they are never averaged in.
        passage_scores_map: Dict[str, Dict[str, float]] = {}
        for out in active_outputs:
            if out.module_name == "discontinuity_analysis":
                continue
            for ps in out.passage_scores:
                passage_scores_map.setdefault(ps.passage_id, {})[out.module_name] = ps.score

        passage_evaluations: List[PassageEvaluation] = []
        for p in doc.passages:
            if len(doc.passages) == 1:
                p_calibrated = calibrated_prob
            else:
                p_scores = dict(doc_scores)
                p_scores.update(passage_scores_map.get(p.passage_id, {}))
                p_calibrated = self._stack(tier, p_scores)[0]

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
        # Hybrid requires confidently-scored passages on both sides, well past the thresholds.
        has_red_passage = any(
            pe.color_category == "red" and pe.calibrated_ai_score >= 0.85 for pe in passage_evaluations
        )
        has_green_passage = any(
            pe.color_category == "green" and pe.calibrated_ai_score <= 0.15 for pe in passage_evaluations
        )
        discontinuity_module = next((out for out in detector_outputs if out.module_name == "discontinuity_analysis"), None)
        high_discontinuity = (
            discontinuity_module is not None
            and discontinuity_module.features.get("discontinuity_index", 0.0) > 0.45
        )

        forensic_notes: List[str] = []
        if tier_name != "full":
            forensic_notes.append(
                f"Transformer layer(s) unavailable; fused with reduced '{tier_name}' weight tier (lower accuracy)."
            )

        # Inconclusive check: strongly conflicting evidence or probability in the ambiguous band
        if disagreement > 0.45 and not (has_red_passage and has_green_passage):
            verdict = ClassificationVerdict.INCONCLUSIVE
            forensic_notes.append(
                f"Significant inter-module discordance observed ({disagreement:.0%} of weighted evidence "
                "opposes the majority); analytical layers produced contradictory signals that preclude "
                "definitive attribution."
            )
        elif (has_red_passage and has_green_passage) or (high_discontinuity and 0.35 <= calibrated_prob <= 0.75):
            verdict = ClassificationVerdict.HYBRID_MIXED
            forensic_notes.append(
                "Document exhibits substantial passage-level divergence; distinct clusters of authentic "
                "human writing and synthetic AI generation coexist within the text."
            )
        elif calibrated_prob >= profile.ai_threshold:
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
            active_module_count=len(active_outputs),
            module_contributions=module_contributions,
            passage_evaluations=passage_evaluations,
            contradictory_signals=list(set(all_contradictions)),
            forensic_notes=forensic_notes
        )
