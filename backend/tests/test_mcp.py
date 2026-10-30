"""
AEGIS MCP Server Test Suite.
Validates MCP tools, resources, prompts, execution payloads, and safety invariants.
"""

import unittest
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.mcp.server import (
    mcp_server,
    analyze_text,
    analyze_document,
    analyze_passages,
    compare_text_samples,
    get_analysis_report,
    get_detector_capabilities,
    health_check,
    resource_capabilities,
    resource_methodology,
    resource_limitations,
    resource_model_registry,
    resource_evaluation_summary,
    prompt_forensic_text_review,
    prompt_academic_writing_review,
    prompt_hybrid_authorship_review,
    prompt_stylometric_comparison,
    prompt_research_evaluation_review
)


class TestAegisMcpServer(unittest.TestCase):
    def test_health_check_tool(self):
        res = health_check()
        self.assertEqual(res["status"], "healthy")
        self.assertTrue(res["database_connected"])
        self.assertIn("device", res)

    def test_get_detector_capabilities_tool(self):
        res = get_detector_capabilities()
        self.assertEqual(res["system_name"], "AEGIS Forensic AI Detection Engine")
        self.assertIn("en", res["supported_languages"])
        self.assertGreaterEqual(len(res["active_modules"]), 6)
        self.assertEqual(res["minimum_word_threshold"], 60)
        self.assertIn("evaluation_status", res)
        self.assertEqual(res["evaluation_status"]["auroc"], 1.0)

    def test_analyze_text_insufficient_evidence(self):
        """Rule 7: Returns INSUFFICIENT_EVIDENCE on short inputs (<60 words)."""
        res = analyze_text("This snippet is too short to establish statistical confidence.")
        self.assertEqual(res["classification"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(res["evidence_sufficiency"]["has_sufficient_evidence"])
        self.assertIn("execution_time_ms", res)

    def test_analyze_text_full_flow(self):
        ai_sample = (
            "In today's fast-paced digital landscape, artificial intelligence plays a crucial role in transforming "
            "traditional educational methodologies. It is important to remember that technology does not merely "
            "replace the instructor; rather, it fosters a vibrant and multifaceted learning environment tailored to "
            "diverse student needs. Delving into the pedagogical implications, one observes a profound synergy "
            "between machine learning algorithms and personalized curriculum delivery. Furthermore, modern adaptive "
            "platforms provide nuanced insights into cognitive retention. Ultimately, the integration of these "
            "sophisticated systems stands as a testament to the ever-evolving nature of global education."
        )
        res = analyze_text(
            text=ai_sample,
            analysis_depth="standard",
            include_passages=True
        )
        self.assertIn("analysis_id", res)
        self.assertIn("classification", res)
        self.assertIn("calibrated_ai_likelihood", res)
        self.assertIn("uncertainty_interval", res)
        self.assertIn("detector_outputs", res)
        self.assertGreater(len(res["passage_level_findings"]), 0)
        self.assertGreater(len(res["limitations"]), 0)
        self.assertGreater(res["execution_time_ms"], 0)

        # Test report retrieval by ID
        report = get_analysis_report(res["analysis_id"])
        self.assertEqual(report["analysis_id"], res["analysis_id"])

    def test_analyze_passages_tool(self):
        text = (
            "The regulation of mitochondrial dynamics is critical for cellular metabolic homeostasis in eukaryotic organisms. "
            "We investigated the interaction between mitofusin-2 and optic atrophy 1 under induced hypoxic stress in cultured neurons. "
            "When cells were subjected to one percent oxygen tension for six hours, total ATP concentration plummeted significantly. "
            "Intriguingly, exogenous supplementation with NAD+ precursors rescued cristae junction morphology effectively."
        )
        res = analyze_passages(text=text, passage_window_words=60, passage_stride_words=30)
        self.assertIn("passages", res)
        self.assertGreaterEqual(res["total_passages"], 1)
        for p in res["passages"]:
            self.assertIn("passage_id", p)
            self.assertIn("calibrated_ai_score", p)
            self.assertIn("color_category", p)

    def test_compare_text_samples_tool(self):
        sample_a = (
            "Old man Henderson smelled like damp wool and turpentine. He didn't speak much on Tuesdays—that was his routine, "
            "something to do with the ferry schedules or an old superstition from his tugboat years on the bay. We sat on the crates."
        )
        sample_b = (
            "In today's fast-paced digital landscape, artificial intelligence plays a crucial role in transforming "
            "traditional educational methodologies. Delving into the pedagogical implications, one observes a profound synergy."
        )
        res = compare_text_samples(sample_a, sample_b)
        self.assertIn("stylistic_divergence_index", res)
        self.assertIn("sample_a_features", res)
        self.assertIn("sample_b_features", res)
        self.assertIn("assessment", res)

    def test_mcp_resources(self):
        cap = resource_capabilities()
        self.assertIn("Capabilities", cap)
        meth = resource_methodology()
        self.assertIn("Methodology", meth)
        lim = resource_limitations()
        self.assertIn("Limitations", lim)
        reg = resource_model_registry()
        self.assertIn("Model Registry", reg)
        eval_sum = resource_evaluation_summary()
        self.assertIn("Validation Summary", eval_sum)

    def test_mcp_prompts(self):
        p1 = prompt_forensic_text_review("Sample text to review")
        self.assertIn("user", p1[0]["role"])
        self.assertIn("probabilistic", p1[0]["content"])

        p2 = prompt_academic_writing_review("Essay text")
        self.assertIn("academic", p2[0]["content"])

        p3 = prompt_hybrid_authorship_review("Hybrid text")
        self.assertIn("hybrid", p3[0]["content"].lower())

        p4 = prompt_stylometric_comparison("Sample A", "Sample B")
        self.assertIn("stylometric", p4[0]["content"])

        p5 = prompt_research_evaluation_review()
        self.assertIn("calibration", p5[0]["content"])


if __name__ == "__main__":
    unittest.main()
