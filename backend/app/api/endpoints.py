"""
AEGIS REST API Endpoints.
Provides forensic analysis, file parsing, adversarial stress-testing, and benchmark telemetry.
"""

import uuid
from typing import Optional, List, Dict, Any
import numpy as np
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.models import (
    AnalyzeTextRequest,
    AnalysisResponse,
    StressTestRequest,
    SystemHealthResponse,
    ModuleContributionView
)
from app.core.preprocessor import ForensicPreprocessor
from app.core.file_parser import DocumentParser, DocumentParserError
from app.core.explanation import ForensicExplanationEngine
from app.detectors.registry import get_detectors
from app.ensemble.fusion import ForensicEnsembleEngine, OperatingMode
from app.evaluation.adversarial import AdversarialAttackSimulator
from app.evaluation.benchmark import ForensicBenchmarkRunner
from app.config import config
import torch

router = APIRouter(prefix="/api/v1")

# Initialize shared engines
preprocessor = ForensicPreprocessor(
    min_words_sufficient=config.length_limits.min_word_count_insufficient,
    passage_window_words=config.length_limits.passage_window_words,
    passage_stride_words=config.length_limits.passage_stride_words
)
file_parser = DocumentParser(max_size_bytes=config.max_upload_size_bytes)
explanation_engine = ForensicExplanationEngine()
ensemble_engine = ForensicEnsembleEngine()
adversarial_simulator = AdversarialAttackSimulator()

detectors = get_detectors()


def _execute_pipeline(
    text: str,
    mode: OperatingMode = OperatingMode.BALANCED,
    research_mode: bool = False
) -> AnalysisResponse:
    """Core pipeline execution shared between text and file endpoints."""
    analysis_id = str(uuid.uuid4())
    doc = preprocessor.process(text)

    # Execute all active detectors
    outputs = [detector.analyze(doc) for detector in detectors]

    # Calibrated ensemble fusion
    decision = ensemble_engine.fuse(doc, outputs, mode=mode)

    # Forensic structured report generation
    report = explanation_engine.generate_report(analysis_id, doc, decision, outputs)

    # Research diagnostics (if research mode enabled)
    research_diagnostics = None
    if research_mode:
        research_diagnostics = {
            "all_extracted_features": {
                out.module_name: out.features for out in outputs
            },
            "uncalibrated_raw_scores": {
                out.module_name: out.raw_score for out in outputs
            },
            "detector_confidences": {
                out.module_name: out.confidence for out in outputs
            },
            "passage_breakdown_matrix": [
                {
                    "passage_id": pe.passage_id,
                    "index": pe.index,
                    "calibrated_score": pe.calibrated_ai_score,
                    "color_category": pe.color_category,
                    "supporting_signals": pe.supporting_signals
                }
                for pe in decision.passage_evaluations
            ]
        }

    contrib_views = {
        k: ModuleContributionView(
            display_name=v["display_name"],
            score=v["score"],
            confidence=v["confidence"],
            weight_applied=v["weight_applied"],
            observations=v["observations"]
        )
        for k, v in decision.module_contributions.items()
    }

    return AnalysisResponse(
        analysis_id=analysis_id,
        verdict=decision.verdict,
        calibrated_ai_likelihood=decision.calibrated_ai_likelihood,
        confidence=decision.confidence,
        uncertainty_interval=decision.uncertainty_interval,
        operating_mode=decision.operating_mode,
        has_sufficient_evidence=doc.has_sufficient_evidence,
        word_count=doc.total_words,
        sentence_count=doc.total_sentences,
        passage_count=len(doc.passages),
        inter_module_disagreement=decision.inter_module_disagreement,
        module_contributions=contrib_views,
        passage_evaluations=decision.passage_evaluations,
        contradictory_signals=decision.contradictory_signals,
        forensic_notes=decision.forensic_notes,
        forensic_report=report,
        research_diagnostics=research_diagnostics
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalyzeTextRequest):
    """Analyzes raw text through the full multi-layer forensic detection pipeline."""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
    return _execute_pipeline(
        text=request.text,
        mode=request.operating_mode,
        research_mode=request.research_mode
    )


@router.post("/analyze-file", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    operating_mode: str = Form("balanced"),
    research_mode: bool = Form(False)
):
    """Extracts text from uploaded PDF, DOCX, TXT, or MD file and runs forensic analysis."""
    try:
        content = await file.read()
        extracted_text, _ = file_parser.parse(file.filename, content)
    except DocumentParserError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

    if not extracted_text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in uploaded file.")

    try:
        mode_enum = OperatingMode(operating_mode)
    except ValueError:
        mode_enum = OperatingMode.BALANCED

    return _execute_pipeline(
        text=extracted_text,
        mode=mode_enum,
        research_mode=research_mode
    )


@router.post("/stress-test")
async def run_stress_test(request: StressTestRequest):
    """
    Simulates adversarial evasion attacks against the input text.
    Measures detector sensitivity and score drift.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")

    clean_response = _execute_pipeline(request.text, mode=request.operating_mode)
    clean_score = clean_response.calibrated_ai_likelihood

    attacks = adversarial_simulator.generate_all_attacks(request.text)
    attack_results = []
    drifts = []

    for atk in attacks:
        perturbed_response = _execute_pipeline(atk.perturbed_text, mode=request.operating_mode)
        drift = abs(clean_score - perturbed_response.calibrated_ai_likelihood)
        drifts.append(drift)

        attack_results.append({
            "attack_type": atk.attack_type,
            "description": atk.description,
            "perturbed_excerpt": atk.perturbed_text[:140] + "...",
            "original_score": clean_score,
            "perturbed_score": perturbed_response.calibrated_ai_likelihood,
            "score_drift": round(drift, 4),
            "original_verdict": clean_response.verdict.value,
            "perturbed_verdict": perturbed_response.verdict.value
        })

    avg_drift = float(np.mean(drifts)) if drifts else 0.0

    return {
        "original_ai_likelihood": clean_score,
        "original_verdict": clean_response.verdict.value,
        "mean_adversarial_drift": round(avg_drift, 4),
        "robustness_summary": (
            "Resilient against adversarial perturbations" if avg_drift < 0.12
            else "Moderate sensitivity to paraphrasing / restructuring"
        ),
        "perturbation_evaluations": attack_results
    }


@router.get("/benchmarks")
async def get_benchmark_results(mode: str = Query("balanced")):
    """Runs or returns cached scientific benchmark evaluations across multi-domain datasets."""
    try:
        mode_enum = OperatingMode(mode)
    except ValueError:
        mode_enum = OperatingMode.BALANCED

    runner = ForensicBenchmarkRunner()
    results = runner.run_benchmark(mode=mode_enum)
    return results


@router.get("/health", response_model=SystemHealthResponse)
async def system_health():
    """Returns system diagnostic status, CUDA hardware availability, and active detectors."""
    cuda_avail = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU"

    return SystemHealthResponse(
        status="healthy",
        version=config.version,
        device=f"{config.device} ({device_name})",
        cuda_available=cuda_avail,
        active_detectors=[d.display_name for d in detectors],
        supported_file_types=config.allowed_file_extensions
    )
