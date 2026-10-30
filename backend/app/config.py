"""
AEGIS Configuration and System Parameters.
Defines thresholds, model paths, operating modes, and calibration constants.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os


class OperatingThresholds(BaseModel):
    """
    Threshold configurations for different risk profiles.
    Forensic analysis must avoid a single arbitrary cutoff.
    """
    # High-precision mode: Prioritizes minimal false-positive rate (FPR < 0.01)
    high_precision_ai_cutoff: float = 0.82
    high_precision_human_cutoff: float = 0.20
    
    # Balanced mode: Equal weight to false positives and false negatives
    balanced_ai_cutoff: float = 0.65
    balanced_human_cutoff: float = 0.35
    
    # Exploratory screening: Sensitive flagger for suspicious text
    exploratory_ai_cutoff: float = 0.50
    exploratory_human_cutoff: float = 0.50
    
    # Uncertainty / Inconclusive boundaries
    inconclusive_low: float = 0.40
    inconclusive_high: float = 0.60
    inter_module_disagreement_threshold: float = 0.18


class TextLengthThresholds(BaseModel):
    """
    Minimum length criteria. Short texts are mathematically unreliable.
    """
    min_word_count_insufficient: int = 60
    min_word_count_low_confidence: int = 150
    min_word_count_optimal: int = 300
    
    # Passage chunking parameters
    passage_window_words: int = 120
    passage_stride_words: int = 50
    min_passage_words: int = 35


class AegisConfig(BaseModel):
    app_name: str = "AEGIS Forensic AI Detection Engine"
    version: str = "1.0.0"
    debug: bool = False
    
    # Thresholds
    thresholds: OperatingThresholds = Field(default_factory=OperatingThresholds)
    length_limits: TextLengthThresholds = Field(default_factory=TextLengthThresholds)
    
    # File limits
    max_upload_size_bytes: int = 25 * 1024 * 1024  # 25 MB
    allowed_file_extensions: List[str] = [".txt", ".pdf", ".docx", ".md"]
    
    # Compute settings
    device: str = "cuda" if os.getenv("AEGIS_DEVICE", "auto") == "cuda" else "cpu"
    batch_size: int = 16
    enable_neural_engine: bool = True
    
    # Data & Model paths
    model_cache_dir: str = os.path.join(os.path.dirname(__file__), "data", "models")
    benchmark_data_dir: str = os.path.join(os.path.dirname(__file__), "data")


config = AegisConfig()

