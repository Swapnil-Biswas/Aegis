"""
HireCrew Seller-Hosted API Contract Integration Tests.
Validates the POST /jobs and GET /jobs/{jobId} lifecycle, idempotency,
authentication, and report generation according to HireCrew's official contract.
"""

import unittest
import sys
import os
import time
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
from app.config import config


class TestHireCrewSellerApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.valid_headers = {
            "Authorization": f"Bearer {config.hirecrew_seller_token}",
            "Idempotency-Key": f"test-order-key-{time.time_ns()}"
        }

    def test_missing_auth_header_rejected(self):
        """Rejects requests missing Authorization header."""
        res = self.client.post("/jobs", json={"orderId": "order-1", "brief": "test brief"})
        self.assertEqual(res.status_code, 401)

    def test_invalid_bearer_token_rejected(self):
        """Rejects requests with unauthorized Bearer token."""
        headers = {
            "Authorization": "Bearer invalid-token-xyz",
            "Idempotency-Key": "key-1"
        }
        res = self.client.post("/jobs", json={"orderId": "order-1", "brief": "test brief"}, headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_missing_idempotency_key_rejected(self):
        """Rejects requests missing required Idempotency-Key header."""
        headers = {"Authorization": f"Bearer {config.hirecrew_seller_token}"}
        res = self.client.post("/jobs", json={"orderId": "order-1", "brief": "test brief"}, headers=headers)
        self.assertEqual(res.status_code, 400)

    def test_job_submission_and_polling_lifecycle(self):
        """Submits a job and polls until delivered, verifying report and cited sources."""
        brief = (
            "Analyze the following text for potential AI-generated patterns: "
            "In today's fast-paced digital landscape, artificial intelligence plays a crucial role in transforming "
            "traditional educational methodologies. It is important to remember that technology does not merely "
            "replace the instructor; rather, it fosters a vibrant and multifaceted learning environment tailored to "
            "diverse student needs. Delving into the pedagogical implications, one observes a profound synergy "
            "between machine learning algorithms and personalized curriculum delivery. Furthermore, modern adaptive "
            "platforms provide nuanced insights into cognitive retention. Ultimately, the integration of these "
            "sophisticated systems stands as a testament to the ever-evolving nature of global education."
        )
        post_res = self.client.post(
            "/jobs",
            json={"orderId": "order-test-100", "brief": brief},
            headers=self.valid_headers
        )
        self.assertEqual(post_res.status_code, 200)
        post_data = post_res.json()
        self.assertIn("jobId", post_data)
        self.assertIn(post_data["status"], ["queued", "running", "delivered"])

        job_id = post_data["jobId"]

        # Poll the job
        poll_res = self.client.get(f"/jobs/{job_id}", headers=self.valid_headers)
        self.assertEqual(poll_res.status_code, 200)
        poll_data = poll_res.json()
        self.assertEqual(poll_data["jobId"], job_id)
        self.assertIn(poll_data["status"], ["queued", "running", "delivered"])

        # Wait briefly for background execution to complete if queued
        attempts = 0
        while poll_data["status"] in ["queued", "running"] and attempts < 15:
            time.sleep(0.3)
            poll_res = self.client.get(f"/jobs/{job_id}", headers=self.valid_headers)
            poll_data = poll_res.json()
            attempts += 1

        self.assertEqual(poll_data["status"], "delivered")
        self.assertIsNotNone(poll_data["report"])
        self.assertGreaterEqual(len(poll_data["report"]), 100)
        self.assertIsNotNone(poll_data["sources"])
        self.assertGreaterEqual(len(poll_data["sources"]), 1)
        for s in poll_data["sources"]:
            self.assertIn("title", s)
            self.assertIn("url", s)
            self.assertTrue(s["url"].startswith("http"))
            # Crucial HireCrew reviewer rule: source URL must be included in report body
            self.assertIn(s["url"], poll_data["report"])

    def test_idempotent_replay_returns_same_job(self):
        """Repeated submission with identical key and payload returns existing job."""
        key = f"idempotent-key-{time.time_ns()}"
        headers = {
            "Authorization": f"Bearer {config.hirecrew_seller_token}",
            "Idempotency-Key": key
        }
        payload = {"orderId": "order-idem-1", "brief": "Perform forensic text audit on sample A."}

        res1 = self.client.post("/jobs", json=payload, headers=headers)
        self.assertEqual(res1.status_code, 200)
        job1 = res1.json()

        # Replay same request
        res2 = self.client.post("/jobs", json=payload, headers=headers)
        self.assertEqual(res2.status_code, 200)
        job2 = res2.json()

        self.assertEqual(job1["jobId"], job2["jobId"])

    def test_reused_idempotency_key_with_different_payload_conflicts(self):
        """Reusing the same key with conflicting input raises 409 Conflict."""
        key = f"conflict-key-{time.time_ns()}"
        headers = {
            "Authorization": f"Bearer {config.hirecrew_seller_token}",
            "Idempotency-Key": key
        }
        res1 = self.client.post("/jobs", json={"orderId": "order-A", "brief": "Brief A"}, headers=headers)
        self.assertEqual(res1.status_code, 200)

        # Conflict: different brief
        res2 = self.client.post("/jobs", json={"orderId": "order-A", "brief": "Brief B (different)"}, headers=headers)
        self.assertEqual(res2.status_code, 409)


if __name__ == "__main__":
    unittest.main()

