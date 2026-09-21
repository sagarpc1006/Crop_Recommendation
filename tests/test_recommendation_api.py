"""Integration tests for POST /api/recommendations/generate endpoint."""

import json
import unittest
from backend.app import create_app
from backend.config import TestingConfig


class TestRecommendationAPI(unittest.TestCase):
    """Test suite for recommendation generation REST endpoint."""

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    def test_health_check(self):
        """Verify GET /api/health works."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "online")

    def test_generate_recommendations_endpoint(self):
        """Verify POST /api/recommendations/generate returns ranked explainable results."""
        payload = {
            "soil_type": "Loamy",
            "climate": "Tropical",
            "sunlight": "Partial Shade",
            "space": "Small",
            "limit": 3
        }
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertIn("recommendations", body["data"])
        recs = body["data"]["recommendations"]
        self.assertLessEqual(len(recs), 3)
        self.assertGreater(len(recs), 0)

        # Check top recommendation properties
        top = recs[0]
        self.assertIn("name", top)
        self.assertIn("compatibility_score", top)
        self.assertIn("matched_factors", top)
        self.assertIn("unmatched_factors", top)
        self.assertIn("basic_care", top)

    def test_generate_recommendations_aliased_endpoint(self):
        """Verify POST /api/v1/recommendations/generate also works via blueprint alias."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal"
        }
        res = self.client.post(
            "/api/v1/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        top = body["data"]["recommendations"][0]
        self.assertEqual(top["name"], "Aloe Vera")
        self.assertEqual(top["compatibility_score"], 100)


if __name__ == "__main__":
    unittest.main()
