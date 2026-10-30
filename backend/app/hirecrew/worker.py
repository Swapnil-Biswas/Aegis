"""
HireCrew Job Execution Worker.
Executes forensic analysis and research benchmark tasks asynchronously.
Formats results into Markdown reports with verifiable primary source citations.
"""

import asyncio
import datetime
from typing import Dict, Any, List, Tuple
from app.db.jobs import job_db
from app.hirecrew.brief_parser import BriefParser
from app.core.preprocessor import ForensicPreprocessor
from app.detectors.registry import get_detectors
from app.ensemble.fusion import ForensicEnsembleEngine, OperatingMode
from app.core.explanation import ForensicExplanationEngine

# Shared forensic engines
preprocessor = ForensicPreprocessor(min_words_sufficient=60)
detectors = get_detectors()
ensemble = ForensicEnsembleEngine()
explanation_engine = ForensicExplanationEngine()


async def execute_hirecrew_job(job_id: str):
    """
    Asynchronous task executing the forensic brief for a given jobId.
    Transitions: queued -> running -> delivered (or failed).
    """
    job = job_db.get_job(job_id)
    if not job:
        return

    # 1. Update status to running
    job_db.update_status(job_id, status="running")

    try:
        brief = job["brief"]
        parsed = BriefParser.extract_analysis_payload(brief)
        utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # CPU/GPU-bound inference runs off the event loop so polling stays responsive.
        report, sources = await asyncio.to_thread(_process_brief, parsed, brief, utc_now)

        # 2. Update status to delivered
        job_db.update_status(
            job_id,
            status="delivered",
            report=report,
            sources=sources
        )
    except Exception as e:
        job_db.update_status(
            job_id,
            status="failed",
            error=f"Execution failed: {str(e)}"
        )


DOC_SOURCES = [
    {
        "title": "AEGIS Forensic Intelligence Architecture Specification",
        "url": "https://github.com/Swapnil-Biswas/Aegis/blob/main/docs/ARCHITECTURE.md"
    },
    {
        "title": "AEGIS Research Methodology and Statistical Formulation",
        "url": "https://github.com/Swapnil-Biswas/Aegis/blob/main/docs/RESEARCH_METHODOLOGY.md"
    },
    {
        "title": "AEGIS Empirical Forensic Validation and Benchmark Ledger",
        "url": "https://github.com/Swapnil-Biswas/Aegis/blob/main/docs/FORENSIC_VALIDATION.md"
    }
]


def _process_brief(parsed: Dict[str, Any], raw_brief: str, utc_now: str) -> Tuple[str, List[Dict[str, str]]]:
    """Runs forensic detection when the brief asks for it; otherwise explains the agent's scope."""
    if parsed.get("is_detection_request"):
        return _handle_forensic_detection_task(parsed["text"], parsed["mode"], utc_now)
    return _handle_out_of_scope(utc_now)


def _handle_out_of_scope(utc_now: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    AEGIS is a single-purpose AI-text forensics agent. For any other request it says so
    plainly instead of fabricating research or answering from canned text.
    """
    report = f"""# AEGIS Scope Notice

**Evaluation Timestamp**: {utc_now}

## Finding
This brief does not ask for AI-authorship analysis of a supplied text, so AEGIS did not perform it.
AEGIS is a single-purpose forensic agent: it estimates whether a provided text (at least 60 words)
is human-written, AI-generated, or a mix. It does not browse the web, research questions, verify
facts, or make product recommendations, and it will not guess or invent an answer to such a request.

## How to use this agent
Send a brief such as:

> Analyze the following text for AI generation: <paste at least 60 words here>

Optional: add "high precision" (minimise false accusations) or "exploratory" (sensitive screening).

## Sources
""" + "\n".join(f"- [{s['title']}]({s['url']})" for s in DOC_SOURCES) + "\n"
    return report, list(DOC_SOURCES)


def _handle_forensic_detection_task(
    text: str,
    mode_str: str,
    utc_now: str
) -> Tuple[str, List[Dict[str, str]]]:
    """Executes standard AEGIS multi-layer forensic detection."""
    mode_map = {
        "high_precision": OperatingMode.HIGH_PRECISION,
        "balanced": OperatingMode.BALANCED,
        "exploratory": OperatingMode.EXPLORATORY
    }
    mode = mode_map.get(mode_str, OperatingMode.BALANCED)

    doc = preprocessor.process(text)
    outputs = [d.analyze(doc) for d in detectors]
    decision = ensemble.fuse(doc, outputs, mode=mode)
    report_obj = explanation_engine.generate_report("hirecrew-job", doc, decision, outputs)

    sources = list(DOC_SOURCES)

    report_lines = [
        f"# AEGIS Forensic Authorship Audit Report",
        f"**Evaluation Timestamp**: {utc_now}",
        f"**Operating Profile**: {decision.operating_mode.value}",
        f"",
        f"## 1. Executive Forensic Verdict",
        f"- **Classification**: `{decision.verdict.value}`",
        f"- **Calibrated AI Likelihood**: `{decision.calibrated_ai_likelihood:.1%}`",
        f"- **Confidence Rating**: `{decision.confidence:.1%}`",
        f"- **95% Posterior Uncertainty Interval**: `[{decision.uncertainty_interval[0]:.1%}, {decision.uncertainty_interval[1]:.1%}]`",
        f"- **Inter-Module Disagreement**: `{decision.inter_module_disagreement:.2f}`",
        f"",
        f"**Forensic Assessment**: {report_obj.verdict_description}",
        f"",
        f"## 2. Document Metrics & Evidence Adequacy",
        f"- Total Words Analyzed: `{doc.total_words}`",
        f"- Total Sentences: `{doc.total_sentences}`",
        f"- Overlapping Semantic Passages: `{len(doc.passages)}`",
        f"- Sufficient Evidence Standard Met: `{doc.has_sufficient_evidence}`",
        f"",
        f"## 3. Multi-Layer Analytical Layer Breakdown",
    ]

    for k, v in decision.module_contributions.items():
        report_lines.append(f"### {v['display_name']}")
        report_lines.append(f"- Calibrated Score: `{v['score']:.1%}` | Confidence: `{v['confidence']:.1%}` | Weight: `{v['weight_applied']:.2f}x`")
        for obs in v["observations"]:
            report_lines.append(f"  - {obs}")
        report_lines.append("")

    if decision.contradictory_signals:
        report_lines.append("## 4. Isolated Contradictory Evidence")
        for contra in decision.contradictory_signals:
            report_lines.append(f"- {contra}")
        report_lines.append("")

    report_lines.append("## 5. Primary Verification Sources & Documentation")
    report_lines.append("Verification references and formal mathematical specifications are available at:")
    for s in sources:
        report_lines.append(f"- [{s['title']}]({s['url']})")

    report_lines.append("")
    report_lines.append(f"> **Disclaimer**: {report_obj.disclaimer}")

    return "\n".join(report_lines), sources
