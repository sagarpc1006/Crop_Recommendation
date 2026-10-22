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


    def test_get_plant_by_id_endpoint(self):
        """Verify dedicated GET /api/plants/<plant_id> returns plant data combining external data when available."""
        res = self.client.get("/api/plants/1")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        plant = body["data"]
        self.assertEqual(plant["name"], "Aloe Vera")
        self.assertIn("soil_type", plant)
        self.assertIn("sunlight", plant)
        self.assertIn("water_needs", plant)
        self.assertIn("climate", plant)
        self.assertIn("space_requirement", plant)

    def test_get_plant_by_id_aliased_and_404(self):
        """Verify GET /api/v1/plants/<plant_id> alias works and 404 is handled gracefully."""
        res_alias = self.client.get("/api/v1/plants/1")
        self.assertEqual(res_alias.status_code, 200)
        self.assertTrue(res_alias.get_json()["success"])

        res_404 = self.client.get("/api/plants/99999")
        self.assertEqual(res_404.status_code, 404)
        body_404 = res_404.get_json()
        self.assertFalse(body_404["success"])
        self.assertIn("not found", body_404["message"].lower())

    def test_search_plants_by_name_soil_climate_sunlight(self):
        """Verify GET /api/plants/search supports searching across name, soil, climate, and sunlight."""
        # 1. Search by plant name
        res_name = self.client.get("/api/plants/search?q=Aloe")
        self.assertEqual(res_name.status_code, 200)
        data_name = res_name.get_json()["data"]
        self.assertTrue(any("Aloe" in p["name"] for p in data_name))

        # 2. Search by soil
        res_soil = self.client.get("/api/plants/search?q=Sandy")
        self.assertEqual(res_soil.status_code, 200)
        data_soil = res_soil.get_json()["data"]
        self.assertTrue(len(data_soil) > 0)
        self.assertTrue(any("Sandy" in p.get("soil_type", "") for p in data_soil))

        # 3. Search by climate
        res_clim = self.client.get("/api/plants/search?q=Tropical")
        self.assertEqual(res_clim.status_code, 200)
        data_clim = res_clim.get_json()["data"]
        self.assertTrue(len(data_clim) > 0)

        # 4. Search by sunlight
        res_sun = self.client.get("/api/plants/search?q=Full Sun")
        self.assertEqual(res_sun.status_code, 200)
        data_sun = res_sun.get_json()["data"]
        self.assertTrue(len(data_sun) > 0)

    def test_invalid_recommendation_content_type(self):
        """Verify non-JSON payload returns 400."""
        res = self.client.post(
            "/api/recommendations/generate",
            data="not a json payload",
            content_type="text/plain"
        )
        self.assertEqual(res.status_code, 400)
        body = res.get_json()
        self.assertFalse(body["success"])

    def test_invalid_recommendation_payload_not_dict(self):
        """Verify non-object JSON payload returns 400."""
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps([1, 2, 3]),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        body = res.get_json()
        self.assertFalse(body["success"])

    def test_search_plants_missing_query(self):
        """Verify search without query returns 400."""
        res = self.client.get("/api/plants/search")
        self.assertEqual(res.status_code, 400)
        body = res.get_json()
        self.assertFalse(body["success"])

    def test_health_check_growit_branding(self):
        """Verify health check reports GROWIT brand."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertIn("GROWIT", data["service"])


if __name__ == "__main__":
    unittest.main()
