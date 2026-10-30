"""
Shared detector suite.
Every entry point (REST, MCP, HireCrew worker, benchmark runner) uses the same
instances so transformer weights are loaded only once per process.
"""

from typing import List

from app.detectors.base import BaseDetector
from app.detectors.statistical import StatisticalLinguisticDetector
from app.detectors.stylometric import StylometricFingerprintDetector
from app.detectors.neural import NeuralClassifierDetector
from app.detectors.perplexity import LanguageModelPerplexityDetector
from app.detectors.semantic import SemanticDiscourseDetector
from app.detectors.pattern_analyzer import AIPatternDetector
from app.detectors.discontinuity import DiscontinuityDetector

_DETECTORS: List[BaseDetector] = []


def get_detectors() -> List[BaseDetector]:
    if not _DETECTORS:
        _DETECTORS.extend([
            StatisticalLinguisticDetector(),
            StylometricFingerprintDetector(),
            NeuralClassifierDetector(),
            LanguageModelPerplexityDetector(),
            SemanticDiscourseDetector(),
            AIPatternDetector(),
            DiscontinuityDetector(),
        ])
    return _DETECTORS
