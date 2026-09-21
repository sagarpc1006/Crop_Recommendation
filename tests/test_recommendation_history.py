"""Integration and unit tests for Recommendation History and persistence."""

import json
import unittest
from backend.app import create_app
from backend.config import TestingConfig
from backend.database.connection import get_session_factory, Base, get_engine
from backend.database.models import User, Plant, Recommendation, SearchHistory


class TestRecommendationHistory(unittest.TestCase):
    """Test suite covering recommendation history persistence, duplicate prevention, and retrieval."""

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()

        self.engine = get_engine()
        Base.metadata.create_all(bind=self.engine)
        self.SessionFactory = get_session_factory()
        self.session = self.SessionFactory()

        # Seed a test user
        self.user = User(
            name="Alice Gardener",
            email="alice.test@example.com",
            location="Portland, OR"
        )
        self.session.add(self.user)

        # Seed test plants
        self.plant1 = Plant(
            name="Test Aloe",
            scientific_name="Aloe barbadensis",
            soil_type="Sandy",
            climate="Warm/Dry",
            sunlight="Full Sun",
            water_needs="Low",
            space_requirement="Minimal",
            description="Succulent test plant"
        )
        self.plant2 = Plant(
            name="Test Fern",
            scientific_name="Nephrolepis exaltata",
            soil_type="Loamy",
            climate="Humid/Tropical",
            sunlight="Partial Shade",
            water_needs="Medium",
            space_requirement="Compact",
            description="Fern test plant"
        )
        self.session.add_all([self.plant1, self.plant2])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)
        self.app_ctx.pop()

    def test_recommendation_persists_to_database(self):
        """Verify generating recommendations with user_id saves records to PostgreSQL."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal",
            "limit": 2,
            "user_id": self.user.user_id
        }
        res = self.client.post(
            "/api/recommendations/generate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)

        # Verify SearchHistory was saved
        searches = self.session.query(SearchHistory).filter(SearchHistory.user_id == self.user.user_id).all()
        self.assertGreaterEqual(len(searches), 1)
        self.assertEqual(searches[0].soil_type, "Sandy")
        self.assertEqual(searches[0].sunlight, "Full Sun")

        # Verify Recommendation records were saved
        recs = self.session.query(Recommendation).filter(Recommendation.user_id == self.user.user_id).all()
        self.assertGreaterEqual(len(recs), 1)
        self.assertEqual(recs[0].plant_id, self.plant1.plant_id)
        self.assertGreaterEqual(recs[0].match_score, 0.9)

    def test_duplicate_recommendation_prevention(self):
        """Verify duplicate recommendation records are not created unnecessarily."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal",
            "limit": 2,
            "user_id": self.user.user_id
        }
        # First submission
        self.client.post("/api/recommendations/generate", data=json.dumps(payload), content_type="application/json")
        initial_rec_count = self.session.query(Recommendation).filter(Recommendation.user_id == self.user.user_id).count()

        # Immediate repeated submission (simulating double-click / re-submission)
        self.client.post("/api/recommendations/generate", data=json.dumps(payload), content_type="application/json")
        after_rec_count = self.session.query(Recommendation).filter(Recommendation.user_id == self.user.user_id).count()

        # Count should remain unchanged due to duplicate prevention
        self.assertEqual(initial_rec_count, after_rec_count)

    def test_get_user_recommendations_endpoint(self):
        """Verify GET /api/recommendations/<user_id> returns user, plant, timestamp, score, and preferences."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal",
            "limit": 1,
            "user_id": self.user.user_id
        }
        self.client.post("/api/recommendations/generate", data=json.dumps(payload), content_type="application/json")

        # Call GET /api/recommendations/<user_id>
        res = self.client.get(f"/api/recommendations/{self.user.user_id}")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertIsInstance(body["data"], list)
        self.assertGreaterEqual(len(body["data"]), 1)

        item = body["data"][0]
        # 1. User
        self.assertIn("user", item)
        self.assertEqual(item["user"]["user_id"], self.user.user_id)
        self.assertEqual(item["user"]["name"], "Alice Gardener")

        # 2. Plant
        self.assertIn("plant", item)
        self.assertEqual(item["plant"]["name"], "Test Aloe")
        self.assertEqual(item["plant"]["scientific_name"], "Aloe barbadensis")

        # 3. Recommendation date/time
        self.assertIn("timestamp", item)
        self.assertIsNotNone(item["timestamp"])

        # 4. Compatibility score
        self.assertIn("compatibility_score", item)
        self.assertIn("match_score", item)
        self.assertEqual(item["compatibility_score"], 100)

        # 5. User preference information
        self.assertIn("user_preferences", item)
        self.assertEqual(item["user_preferences"]["soil_type"], "Sandy")
        self.assertEqual(item["user_preferences"]["climate"], "Warm/Dry")
        self.assertEqual(item["user_preferences"]["sunlight"], "Full Sun")

    def test_empty_history_returns_empty_list(self):
        """Verify users with no recommendations return an empty list gracefully."""
        # Non-existent user ID
        res = self.client.get("/api/recommendations/9999")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"], [])

    def test_recommendations_history_endpoint_with_user_filter(self):
        """Verify GET /api/recommendations/history?user_id=<id> filters properly."""
        payload = {
            "soil_type": "Sandy",
            "climate": "Warm/Dry",
            "sunlight": "Full Sun",
            "space": "Minimal",
            "limit": 1,
            "user_id": self.user.user_id
        }
        self.client.post("/api/recommendations/generate", data=json.dumps(payload), content_type="application/json")

        res = self.client.get(f"/api/recommendations/history?user_id={self.user.user_id}")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        self.assertGreaterEqual(len(body["data"]), 1)


if __name__ == "__main__":
    unittest.main()
