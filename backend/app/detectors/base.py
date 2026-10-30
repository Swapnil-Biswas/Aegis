"""
Base Detector Interface and Shared Data Models.
Establishes standardized inputs, outputs, and contracts for all analytical layers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.core.preprocessor import PreprocessedDocument, PassageChunk


class PassageScore(BaseModel):
    passage_id: str
    index: int
    score: float
    confidence: float
    key_signals: Dict[str, Any] = Field(default_factory=dict)
    summary: str = ""


class DetectorOutput(BaseModel):
    module_name: str
    display_name: str
    raw_score: float  # [0.0 = Highly Human, 1.0 = Highly AI]
    calibrated_score: float  # Calibrated probability
    confidence: float  # [0.0 = Low, 1.0 = High]
    weight: float = 1.0
    features: Dict[str, float] = Field(default_factory=dict)
    observations: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    passage_scores: List[PassageScore] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseDetector(ABC):
    """
    Abstract Base Class for all AEGIS forensic detection modules.
    Every module must operate independently and support missing-data graceful degradation.
    """

    def __init__(self, name: str, display_name: str, weight: float = 1.0):
        self.name = name
        self.display_name = display_name
        self.weight = weight

    @abstractmethod
    def analyze(self, doc: PreprocessedDocument) -> DetectorOutput:
        """
        Executes forensic analysis on the preprocessed document.
        Must return structured DetectorOutput.
        """
        pass

