"""
FastAPI Endpoints Integration Test Suite.
Validates HTTP request/response payloads, error handling, and research mode output.
"""

import unittest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app


class TestAEGISApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("Statistical Linguistic Analysis", data["active_detectors"])

    def test_analyze_insufficient_text(self):
        """Rule 7: Returns INSUFFICIENT_EVIDENCE for short inputs."""
        response = self.client.post(
            "/api/v1/analyze",
            json={"text": "A brief text sample.", "operating_mode": "balanced"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(data["has_sufficient_evidence"])

    def test_analyze_full_ai_text_with_research_mode(self):
        ai_text = (
            "In today's fast-paced digital landscape, artificial intelligence plays a crucial role in transforming "
            "traditional educational methodologies. It is important to remember that technology does not merely "
            "replace the instructor; rather, it fosters a vibrant and multifaceted learning environment tailored to "
            "diverse student needs. Delving into the pedagogical implications, one observes a profound synergy "
            "between machine learning algorithms and personalized curriculum delivery. Furthermore, modern adaptive "
            "platforms provide nuanced insights into cognitive retention. Ultimately, the integration of these "
            "sophisticated systems stands as a testament to the ever-evolving nature of global education."
        )
        # Exploratory screening flags synthetic markers even in concise paragraphs
        response = self.client.post(
            "/api/v1/analyze",
            json={
                "text": ai_text,
                "operating_mode": "exploratory",
                "research_mode": True
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["verdict"], "AI_GENERATED")
        self.assertGreater(data["calibrated_ai_likelihood"], 0.50)
        self.assertIsNotNone(data["research_diagnostics"])
        self.assertIn("all_extracted_features", data["research_diagnostics"])
        self.assertIn("forensic_report", data)
        self.assertGreaterEqual(len(data["passage_evaluations"]), 1)

    def test_stress_test_endpoint(self):
        text = (
            "Delving into the pedagogical implications, one observes a profound synergy between machine learning "
            "algorithms and personalized curriculum delivery. Furthermore, modern adaptive platforms provide "
            "nuanced insights into cognitive retention. Ultimately, this stands as a testament to progress."
        )
        response = self.client.post(
            "/api/v1/stress-test",
            json={"text": text, "operating_mode": "balanced"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("mean_adversarial_drift", data)
        self.assertIn("perturbation_evaluations", data)
        self.assertEqual(len(data["perturbation_evaluations"]), 4)


if __name__ == "__main__":
    unittest.main()
