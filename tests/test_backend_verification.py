"""Comprehensive Backend Verification Test Suite.

Verifies the 11 key backend scenarios requested for project sign-off:
1. Valid recommendation request
2. Missing soil type
3. Missing climate
4. Invalid sunlight
5. Invalid space
6. No matching plants
7. Plant search
8. Plant details
9. Database unavailable fallback
10. External API unavailable fallback
11. Recommendation history persistence & retrieval
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError

from backend.app import create_app
from backend.config import TestingConfig
from backend.database.connection import get_session_factory, Base, get_engine
from backend.database.models import User, Plant, Recommendation, SearchHistory
from backend.recommendation.engine import RecommendationEngine, RecommendationCriteria
from backend.services.recommendation_service import RecommendationService
from backend.services.plant_api_service import PlantApiService


class TestBackendVerification(unittest.TestCase):
    """Automated test suite verifying critical backend functionality and edge cases."""

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()

        self.engine = get_engine()
        Base.metadata.create_all(bind=self.engine)
        self.SessionFactory = get_session_factory()
        self.session = self.SessionFactory()

        # Seed test user
        self.user = User(
            name="Botanical Explorer",
            email="explorer@example.com",
            location="Austin, TX"
        )
        self.session.add(self.user)

        # Seed test plants
        self.plant1 = Plant(
            name="Aloe Vera",
            scientific_name="Aloe barbadensis miller",
            soil_type="Sandy",
            climate="Warm/Dry",
            sunlight="Full Sun",
            water_needs="Low",
            space_requirement="Minimal",
            description="Succulent with thick fleshy leaves."
        )
        self.plant2 = Plant(
            name="Money Plant",
            scientific_name="Epipremnum aureum",
            soil_type="Loamy",
            climate="Humid/Tropical",
            sunlight="Partial Shade",
            water_needs="Medium",
            space_requirement="Climbing / Hanging",
            description="Hardy indoor vine."
        )
        self.session.add_all([self.plant1, self.plant2])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)
        self.app_ctx.pop()

    # 1. Valid recommendation request
    def test_valid_recommendation_request(self):
        """Verify standard recommendation request returns 200 with ranked explainable items."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal",
            "limit": 2
        }
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        recs = data["data"]["recommendations"]
        self.assertGreaterEqual(len(recs), 1)

        top = recs[0]
        self.assertEqual(top["name"], "Aloe Vera")
        self.assertEqual(top["compatibility_score"], 100)
        self.assertIn("matched_factors", top)
        self.assertIn("unmatched_factors", top)
        self.assertIn("basic_care", top)

    # 2. Missing soil type
    def test_missing_soil_type(self):
        """Verify recommendation engine gracefully handles request missing soil_type."""
        payload = {
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal"
        }
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("recommendations", data["data"])

    # 3. Missing climate
    def test_missing_climate(self):
        """Verify recommendation engine gracefully handles request missing climate."""
        payload = {
            "soil_type": "Sandy",
            "sunlight": "Full Sun",
            "space": "Minimal"
        }
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("recommendations", data["data"])

    # 4. Invalid sunlight
    def test_invalid_sunlight(self):
        """Verify unknown or invalid sunlight criteria does not crash and reflects unmatched."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Quantum Fluorescent Gamma Light",
            "space": "Minimal"
        }
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        top = data["data"]["recommendations"][0]
        # Should record an unmatched factor for the invalid light
        unmatched_str = " ".join(top.get("unmatched_factors", [])).lower()
        self.assertTrue("light" in unmatched_str or "sun" in unmatched_str)

    # 5. Invalid space
    def test_invalid_space(self):
        """Verify invalid or unusual space specification handles gracefully."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Galactic Asteroid Belt 42"
        }
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["data"]["recommendations"]), 0)

    # 6. No matching plants
    def test_no_matching_plants(self):
        """Verify recommendation engine safely returns empty list when no plants are available."""
        engine = RecommendationEngine()
        criteria = RecommendationCriteria(
            soil_type="Clay",
            climate="Arctic",
            sunlight="Pitch Black",
            space="Infinite"
        )
        # Empty candidate list
        results = engine.recommend(criteria=criteria, plants=[], top_k=5)
        self.assertEqual(results, [])

    # 7. Plant search
    def test_plant_search(self):
        """Verify GET /api/plants/search filters correctly by query string."""
        # Search by name
        res_name = self.client.get("/api/plants/search?q=Aloe")
        self.assertEqual(res_name.status_code, 200)
        data_name = res_name.get_json()["data"]
        self.assertTrue(any("Aloe" in p["name"] for p in data_name))

        # Search by soil type
        res_soil = self.client.get("/api/plants/search?q=Loamy")
        self.assertEqual(res_soil.status_code, 200)
        data_soil = res_soil.get_json()["data"]
        self.assertTrue(any("Loamy" in p.get("soil_type", "") for p in data_soil))

    # 8. Plant details
    def test_plant_details(self):
        """Verify GET /api/plants/<id> returns complete details and 404 for invalid ID."""
        # Valid plant ID
        res_valid = self.client.get(f"/api/plants/{self.plant1.plant_id}")
        self.assertEqual(res_valid.status_code, 200)
        plant_data = res_valid.get_json()["data"]
        self.assertEqual(plant_data["name"], "Aloe Vera")
        self.assertEqual(plant_data["soil_type"], "Sandy")
        self.assertEqual(plant_data["sunlight"], "Full Sun")

        # Invalid plant ID
        res_invalid = self.client.get("/api/plants/99999")
        self.assertEqual(res_invalid.status_code, 404)
        self.assertFalse(res_invalid.get_json()["success"])

    # 9. Database unavailable
    def test_database_unavailable_fallback(self):
        """Verify service falls back to SAMPLE_PLANTS when database raises OperationalError."""
        # Create mock db session that raises OperationalError when queried
        mock_session = MagicMock()
        mock_session.query.side_effect = OperationalError("SELECT 1", {}, Exception("DB down"))

        service = RecommendationService(db_session=mock_session)
        result = service.generate_recommendations(
            criteria_data={"soil_type": "Sandy", "climate": "Warm/Dry", "sunlight": "Full Sun", "space": "Minimal"},
            limit=3
        )
        # Should succeed using SAMPLE_PLANTS without raising unhandled exception
        self.assertIn("recommendations", result)
        self.assertGreater(len(result["recommendations"]), 0)

    # 10. External API unavailable
    def test_external_api_unavailable_fallback(self):
        """Verify service functions without error when external plant API is unconfigured."""
        service = PlantApiService()
        service._client._api_key = None
        self.assertFalse(service.is_available())

        # Enrich should return local record unchanged with flag
        local_plant = {"name": "Aloe Vera", "plant_id": 1, "soil_type": "Sandy"}
        enriched = service.enrich_plant_record(local_plant)
        self.assertEqual(enriched["name"], "Aloe Vera")
        self.assertFalse(enriched["external_enriched"])

    # 11. Recommendation history
    def test_recommendation_history_persistence_and_retrieval(self):
        """Verify recommendations persist to DB and GET /api/recommendations/<user_id> returns them."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal",
            "limit": 1,
            "user_id": self.user.user_id
        }
        # 1. Generate recommendation
        gen_res = self.client.post("/api/recommendations/generate", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(gen_res.status_code, 200)

        # 2. Retrieve history for user
        hist_res = self.client.get(f"/api/recommendations/{self.user.user_id}")
        self.assertEqual(hist_res.status_code, 200)
        hist_body = hist_res.get_json()
        self.assertTrue(hist_body["success"])
        recs = hist_body["data"]
        self.assertGreaterEqual(len(recs), 1)

        entry = recs[0]
        # Check all required fields: User, Plant, Timestamp, Score, Preferences
        self.assertEqual(entry["user"]["user_id"], self.user.user_id)
        self.assertEqual(entry["plant"]["name"], "Aloe Vera")
        self.assertIsNotNone(entry["timestamp"])
        self.assertEqual(entry["compatibility_score"], 100)
        self.assertEqual(entry["user_preferences"]["soil_type"], "Sandy")


if __name__ == "__main__":
    unittest.main()
