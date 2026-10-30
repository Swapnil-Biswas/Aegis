"""
Ensemble Operating Thresholds and Classification Verdict Categories.
"""

from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel


class ClassificationVerdict(str, Enum):
    HUMAN_AUTHENTIC = "HUMAN_AUTHENTIC"
    AI_GENERATED = "AI_GENERATED"
    AI_ASSISTED_EDITED = "AI_ASSISTED_EDITED"
    HUMAN_PARAPHRASED_BY_AI = "HUMAN_PARAPHRASED_BY_AI"
    HYBRID_MIXED = "HYBRID_MIXED"
    INCONCLUSIVE = "INCONCLUSIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class OperatingMode(str, Enum):
    HIGH_PRECISION = "high_precision"  # Minimizes False Positives (FPR < 1%)
    BALANCED = "balanced"              # Balanced F1 / Equal Error Rate
    EXPLORATORY = "exploratory"        # High Sensitivity screening


class ThresholdProfile(BaseModel):
    mode: OperatingMode
    ai_threshold: float
    human_threshold: float
    description: str


PROFILES: Dict[OperatingMode, ThresholdProfile] = {
    OperatingMode.HIGH_PRECISION: ThresholdProfile(
        mode=OperatingMode.HIGH_PRECISION,
        ai_threshold=0.82,
        human_threshold=0.20,
        description="High Precision: Minimizes false accusations. Requires overwhelming multi-layer evidence to flag AI."
    ),
    OperatingMode.BALANCED: ThresholdProfile(
        mode=OperatingMode.BALANCED,
        ai_threshold=0.65,
        human_threshold=0.35,
        description="Balanced: Calibrated for general editorial and investigative screening with equalized trade-offs."
    ),
    OperatingMode.EXPLORATORY: ThresholdProfile(
        mode=OperatingMode.EXPLORATORY,
        ai_threshold=0.50,
        human_threshold=0.50,
        description="Exploratory: Sensitive flagger for preliminary auditing. Generates flags for further human inspection."
    )
}

