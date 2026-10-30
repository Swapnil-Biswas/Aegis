"""
Forensic Explanation Engine.
Generates structured, scientifically audited forensic reports.
Strictly distinguishes computed empirical facts, statistical correlations,
model predictions, and epistemic boundaries. Never fabricates evidence.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.preprocessor import PreprocessedDocument
from app.ensemble.fusion import EnsembleDecision
from app.detectors.base import DetectorOutput


class ForensicObservation(BaseModel):
    category: str  # "FACT", "STATISTICAL_CORRELATION", "MODEL_PREDICTION", "LIMITATION"
    dimension: str  # "Linguistics", "Stylometry", "Neural", "Discourse", "Integrity"
    statement: str
    empirical_metric: Optional[str] = None
    metric_value: Optional[float] = None


class ForensicReport(BaseModel):
    report_id: str
    document_summary: Dict[str, Any]
    verdict: str
    verdict_description: str
    calibrated_ai_likelihood: float
    confidence: float
    confidence_interval: List[float]
    reliability_tier: str  # "VERY_HIGH", "HIGH", "MODERATE", "LOW", "INSUFFICIENT"
    operating_mode: str
    observations: List[ForensicObservation]
    contradictory_evidence: List[str]
    passage_level_findings: List[Dict[str, Any]]
    epistemic_limitations: List[str]
    disclaimer: str


class ForensicExplanationEngine:
    """
    Rigorously constructs forensic audit reports adhering to international
    evidence standards and zero-fabrication rules.
    """

    KNOWN_LIMITATIONS = [
        "AI detection models are probabilistic and cannot provide absolute mathematical certainty.",
        "Short texts (< 150 words) possess naturally wide confidence bounds.",
        "Highly specialized technical, legal, or mathematical writing naturally exhibits lower perplexity and low lexical variation.",
        "Deliberate adversarial paraphrasing or heavy human rewriting can compress synthetic markers.",
        "Authors writing in a second language (ESL) may exhibit stylized, formulaic structures that superficially resemble model patterns.",
        "Detector outputs should serve as corroborative forensic indicators, never sole disciplinary or legal proof."
    ]

    def generate_report(
        self,
        report_id: str,
        doc: PreprocessedDocument,
        decision: EnsembleDecision,
        outputs: List[DetectorOutput]
    ) -> ForensicReport:
        """Assembles comprehensive, non-fabricated forensic report."""

        # 1. Document summary metrics (Observed Facts)
        doc_summary = {
            "total_characters": doc.total_characters,
            "total_words": doc.total_words,
            "total_sentences": doc.total_sentences,
            "total_paragraphs": doc.total_paragraphs,
            "total_passages": len(doc.passages),
            "has_sufficient_evidence": doc.has_sufficient_evidence
        }

        # 2. Determine reliability tier
        w_count = doc.total_words
        conf = decision.confidence
        if not doc.has_sufficient_evidence:
            reliability_tier = "INSUFFICIENT"
        elif w_count >= 300 and conf >= 0.85:
            reliability_tier = "VERY_HIGH"
        elif w_count >= 180 and conf >= 0.70:
            reliability_tier = "HIGH"
        elif w_count >= 80 and conf >= 0.50:
            reliability_tier = "MODERATE"
        else:
            reliability_tier = "LOW"

        # 3. Compile categorized observations
        observations: List[ForensicObservation] = []

        # (a) Observed structural facts
        observations.append(
            ForensicObservation(
                category="FACT",
                dimension="Structure",
                statement=f"Document contains {doc.total_words} words distributed across {doc.total_sentences} sentences.",
                empirical_metric="total_words",
                metric_value=float(doc.total_words)
            )
        )

        # (b) Statistical correlations from Module A
        stat_out = next((o for o in outputs if o.module_name == "statistical_linguistics"), None)
        if stat_out:
            b_val = stat_out.features.get("burstiness")
            h_val = stat_out.features.get("hapax_ratio")
            if b_val is not None:
                observations.append(
                    ForensicObservation(
                        category="STATISTICAL_CORRELATION",
                        dimension="Linguistics",
                        statement=f"Sentence length burstiness measured at B={b_val:.3f} (natural human baseline typical: >0.45).",
                        empirical_metric="burstiness",
                        metric_value=b_val
                    )
                )
            if h_val is not None:
                observations.append(
                    ForensicObservation(
                        category="STATISTICAL_CORRELATION",
                        dimension="Linguistics",
                        statement=f"Hapax legomena ratio calculated at {h_val:.1%} of vocabulary.",
                        empirical_metric="hapax_ratio",
                        metric_value=h_val
                    )
                )

        # (c) Stylometric correlations from Module B
        sty_out = next((o for o in outputs if o.module_name == "stylometric_fingerprinting"), None)
        if sty_out:
            tr_val = sty_out.features.get("formal_transition_ratio")
            contra_val = sty_out.features.get("contraction_density")
            if tr_val is not None:
                observations.append(
                    ForensicObservation(
                        category="STATISTICAL_CORRELATION",
                        dimension="Stylometry",
                        statement=f"Formal rhetorical transition marker density is {tr_val:.2%}.",
                        empirical_metric="formal_transition_ratio",
                        metric_value=tr_val
                    )
                )
            if contra_val is not None:
                observations.append(
                    ForensicObservation(
                        category="FACT",
                        dimension="Stylometry",
                        statement=f"Contraction density is {contra_val:.2f} occurrences per 100 words.",
                        empirical_metric="contraction_density",
                        metric_value=contra_val
                    )
                )

        # (d) Pattern observations from Module E
        pat_out = next((o for o in outputs if o.module_name == "pattern_analysis"), None)
        if pat_out:
            dens_val = pat_out.features.get("pattern_density_per_100w")
            if dens_val is not None:
                observations.append(
                    ForensicObservation(
                        category="STATISTICAL_CORRELATION",
                        dimension="Patterns",
                        statement=f"AI hallmark phrasing density is {dens_val:.2f} patterns per 100 words.",
                        empirical_metric="pattern_density_per_100w",
                        metric_value=dens_val
                    )
                )

        # (e) Model predictions from Neural Module C
        neural_out = next((o for o in outputs if o.module_name == "neural_classifier"), None)
        if neural_out:
            p_val = neural_out.features.get("calibrated_ai_probability")
            if p_val is not None:
                observations.append(
                    ForensicObservation(
                        category="MODEL_PREDICTION",
                        dimension="Neural",
                        statement=f"Neural transformer latent sequence classifier estimated p(AI) = {p_val:.2%}.",
                        empirical_metric="calibrated_ai_probability",
                        metric_value=p_val
                    )
                )

        # 4. Passage-level summaries
        passage_findings = [
            {
                "passage_id": pe.passage_id,
                "index": pe.index,
                "word_count": pe.word_count,
                "start_char": pe.start_char,
                "end_char": pe.end_char,
                "ai_score": pe.calibrated_ai_score,
                "color_category": pe.color_category,
                "classification": pe.classification,
                "excerpt": pe.text[:120] + ("..." if len(pe.text) > 120 else "")
            }
            for pe in decision.passage_evaluations
        ]

        # 5. Verdict descriptions
        verdict_descriptions = {
            "HUMAN_AUTHENTIC": "Evidence is overwhelmingly consistent with authentic human authorship across all analytical dimensions.",
            "AI_GENERATED": "Multiple independent statistical, stylometric, and neural indicators converge to demonstrate synthetic AI generation.",
            "AI_ASSISTED_EDITED": "Identified synthetic generation foundation accompanied by human post-generation editing or stylistic smoothing.",
            "HUMAN_PARAPHRASED_BY_AI": "Human-like thematic argument progression rewritten or paraphrased through an AI model.",
            "HYBRID_MIXED": "Document exhibits clear composition heterogeneity, featuring both authentic human and synthetic AI passages.",
            "INCONCLUSIVE": "Available linguistic signals exhibit high contradiction or fall within an ambiguous probability range.",
            "INSUFFICIENT_EVIDENCE": "Text is too short to establish scientifically defensible statistical attribution."
        }

        disclaimer = (
            "NOTICE OF FORENSIC INTEGRITY: This report represents probabilistic forensic analysis based on "
            "computational linguistics, stylometric fingerprinting, and neural modeling. It must not be "
            "interpreted as a definitive accusation of academic or professional misconduct. Findings must be "
            "evaluated in context alongside human review."
        )

        return ForensicReport(
            report_id=report_id,
            document_summary=doc_summary,
            verdict=decision.verdict.value,
            verdict_description=verdict_descriptions.get(decision.verdict.value, "Forensic assessment complete."),
            calibrated_ai_likelihood=decision.calibrated_ai_likelihood,
            confidence=decision.confidence,
            confidence_interval=[decision.uncertainty_interval[0], decision.uncertainty_interval[1]],
            reliability_tier=reliability_tier,
            operating_mode=decision.operating_mode.value,
            observations=observations,
            contradictory_evidence=decision.contradictory_signals,
            passage_level_findings=passage_findings,
            epistemic_limitations=self.KNOWN_LIMITATIONS,
            disclaimer=disclaimer
        )

