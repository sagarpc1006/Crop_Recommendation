"""Unit tests for the transparent, explainable Plant Recommendation Engine."""

import unittest
from backend.recommendation.engine import RecommendationEngine, RecommendationCriteria
from backend.database.seed import SAMPLE_PLANTS


class TestRecommendationEngine(unittest.TestCase):
    """Test suite verifying transparent scoring, explainability, and ranking."""

    def setUp(self):
        self.engine = RecommendationEngine()
        self.plants = [dict(p) for p in SAMPLE_PLANTS]

    def test_perfect_match_aloe_vera(self):
        """Aloe Vera should receive a 100% score when all 4 conditions match exactly."""
        criteria = RecommendationCriteria(
            soil_type="Sandy",
            climate="Warm/Dry",
            sunlight="Full Sun",
            space="Minimal"
        )
        recommendations = self.engine.recommend(criteria, self.plants, top_k=5)
        top_plant = recommendations[0]

        self.assertEqual(top_plant["name"], "Aloe Vera")
        self.assertEqual(top_plant["compatibility_score"], 100)
        self.assertEqual(len(top_plant["matched_factors"]), 4)
        self.assertEqual(len(top_plant["unmatched_factors"]), 0)
        self.assertIn("water_needs", top_plant["basic_care"])
        self.assertEqual(top_plant["basic_care"]["water_needs"], "Low")

    def test_user_example_query_money_plant(self):
        """User example: Loamy soil, Tropical climate, Partial Shade, Small space."""
        criteria = RecommendationCriteria(
            soil_type="Loamy",
            climate="Tropical",
            sunlight="Partial Shade",
            space="Small"
        )
        recommendations = self.engine.recommend(criteria, self.plants, top_k=5)
        top_plant = recommendations[0]

        # Money Plant thrives in Loamy soil, Humid/Tropical, Partial Shade, climbing/compact space
        self.assertEqual(top_plant["name"], "Money Plant")
        self.assertGreaterEqual(top_plant["compatibility_score"], 85)
        self.assertTrue(any("Soil matches" in m for m in top_plant["matched_factors"]))
        self.assertTrue(any("Sunlight matches" in m for m in top_plant["matched_factors"]))
        self.assertTrue(any("Climate matches" in m for m in top_plant["matched_factors"]))

    def test_snake_plant_low_light_and_considerations(self):
        """Snake Plant matches low light and small space, but notes soil differences."""
        criteria = RecommendationCriteria(
            soil_type="Clay",
            climate="Any/Indoor",
            sunlight="Low Light",
            space="Small"
        )
        scored = self.engine.calculate_score(
            next(p for p in self.plants if p["name"] == "Snake Plant"),
            criteria
        )
        self.assertGreater(scored.compatibility_score, 70)
        # Should have matches for light, climate, space
        self.assertTrue(any("Low Light" in m or "Sunlight" in m for m in scored.matched_factors))
        self.assertTrue(any("Space" in m for m in scored.matched_factors))
        # Should note soil difference in unmatched_factors
        self.assertTrue(any("Soil preference differs" in u for u in scored.unmatched_factors))

    def test_ranking_descending_order(self):
        """Recommendations must always be returned in descending order of compatibility."""
        criteria = RecommendationCriteria(
            soil_type="Loamy",
            climate="Warm/Tropical",
            sunlight="Full Sun",
            space="Compact"
        )
        recommendations = self.engine.recommend(criteria, self.plants, top_k=5)
        scores = [r["compatibility_score"] for r in recommendations]

        # Ensure sorted descending
        self.assertEqual(scores, sorted(scores, reverse=True))
        # Tulsi should be top match for Loamy + Warm/Tropical + Full Sun + Compact
        self.assertEqual(recommendations[0]["name"], "Tulsi")
        self.assertEqual(recommendations[0]["compatibility_score"], 100)

    def test_explainability_structure(self):
        """Every recommendation must contain complete explainable fields."""
        criteria = RecommendationCriteria.from_dict({
            "soil_type": "Sandy",
            "climate": "Temperate",
            "sunlight": "Partial Shade",
            "space": "Garden"
        })
        recommendations = self.engine.recommend(criteria, self.plants, top_k=3)
        for rec in recommendations:
            self.assertIn("plant_id", rec)
            self.assertIn("name", rec)
            self.assertIn("compatibility_score", rec)
            self.assertIsInstance(rec["matched_factors"], list)
            self.assertIsInstance(rec["unmatched_factors"], list)
            self.assertIn("basic_care", rec)
            self.assertIn("sunlight", rec["basic_care"])
            self.assertIn("water_needs", rec["basic_care"])


if __name__ == "__main__":
    unittest.main()
