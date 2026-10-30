"""
AEGIS Configuration and System Parameters.
Defines thresholds, model paths, operating modes, and calibration constants.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os
import secrets


def _resolve_device(requested: str) -> str:
    """'auto' picks CUDA when available; 'cuda' falls back to CPU if no GPU is present."""
    if requested == "cpu":
        return "cpu"
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


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
    version: str = "1.1.0"
    debug: bool = False
    
    # Thresholds
    thresholds: OperatingThresholds = Field(default_factory=OperatingThresholds)
    length_limits: TextLengthThresholds = Field(default_factory=TextLengthThresholds)
    
    # File limits
    max_upload_size_bytes: int = 25 * 1024 * 1024  # 25 MB
    allowed_file_extensions: List[str] = [".txt", ".pdf", ".docx", ".md"]
    
    # Compute settings
    device: str = _resolve_device(os.getenv("AEGIS_DEVICE", "auto"))
    batch_size: int = 16
    enable_neural_engine: bool = os.getenv("AEGIS_ENABLE_NEURAL", "1") != "0"
    neural_model_name: str = os.getenv("AEGIS_NEURAL_MODEL", "fakespot-ai/roberta-base-ai-text-detection-v1")
    perplexity_model_name: str = os.getenv("AEGIS_PERPLEXITY_MODEL", "HuggingFaceTB/SmolLM2-135M")
    
    # Data & Model paths
    model_cache_dir: str = os.path.join(os.path.dirname(__file__), "data", "models")
    benchmark_data_dir: str = os.path.join(os.path.dirname(__file__), "data")
    database_path: str = os.getenv(
        "AEGIS_DB_PATH",
        os.path.join(os.path.dirname(__file__), "data", "aegis_jobs.db")
    )

    # HireCrew Seller API Settings
    # No hardcoded fallback: if unset, a random per-process token is used so the
    # seller API is never reachable with a token published in the repository.
    hirecrew_seller_token: str = os.getenv("HIRECREW_SELLER_TOKEN") or secrets.token_urlsafe(32)
    hirecrew_max_brief_length: int = 50000
    hirecrew_job_timeout_seconds: int = 300
    hirecrew_job_retention_hours: int = 72

    # MCP Server Settings
    mcp_auth_token: Optional[str] = os.getenv("AEGIS_MCP_TOKEN", None)
    # Reading arbitrary server-side paths is only safe for the local STDIO transport.
    mcp_allow_local_files: bool = os.getenv("AEGIS_MCP_ALLOW_LOCAL_FILES", "0") == "1"
    mcp_server_name: str = "aegis-forensics-mcp"
    mcp_server_version: str = "1.1.0"


config = AegisConfig()

