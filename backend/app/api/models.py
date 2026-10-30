"""
Pydantic API Request and Response Models for AEGIS Forensic API.
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from app.ensemble.thresholds import OperatingMode, ClassificationVerdict
from app.ensemble.fusion import PassageEvaluation
from app.core.explanation import ForensicReport, ForensicObservation


class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., description="Text content to analyze for forensic authorship.")
    operating_mode: OperatingMode = Field(
        default=OperatingMode.BALANCED,
        description="Threshold profile: 'high_precision', 'balanced', or 'exploratory'."
    )
    research_mode: bool = Field(
        default=False,
        description="If True, includes raw uncalibrated feature matrices and diagnostic internals."
    )


class StressTestRequest(BaseModel):
    text: str = Field(..., description="Target text to subject to adversarial perturbation stress tests.")
    operating_mode: OperatingMode = Field(default=OperatingMode.BALANCED)


class ModuleContributionView(BaseModel):
    display_name: str
    score: float
    confidence: float
    weight_applied: float
    observations: List[str]


class AnalysisResponse(BaseModel):
    analysis_id: str
    verdict: ClassificationVerdict
    calibrated_ai_likelihood: float
    confidence: float
    uncertainty_interval: Tuple[float, float]
    operating_mode: OperatingMode
    has_sufficient_evidence: bool
    word_count: int
    sentence_count: int
    passage_count: int
    inter_module_disagreement: float
    module_contributions: Dict[str, ModuleContributionView]
    passage_evaluations: List[PassageEvaluation]
    contradictory_signals: List[str]
    forensic_notes: List[str]
    forensic_report: ForensicReport
    research_diagnostics: Optional[Dict[str, Any]] = None


class SystemHealthResponse(BaseModel):
    status: str
    version: str
    device: str
    cuda_available: bool
    active_detectors: List[str]
    supported_file_types: List[str]

