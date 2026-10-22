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

    def test_soil_matching(self):
        """Verify soil factor evaluation for exact, compatible, and mismatched soils."""
        plant = {"name": "Test Plant", "soil_type": "Sandy", "climate": "Warm/Dry", "sunlight": "Full Sun", "space_requirement": "Small"}
        
        # Exact match
        crit_exact = RecommendationCriteria(soil_type="Sandy")
        res_exact = self.engine.calculate_score(plant, crit_exact)
        self.assertTrue(any("Soil matches" in m for m in res_exact.matched_factors))

        # Well-drained plant with Sandy user soil
        plant_wd = {"name": "Test WD", "soil_type": "Well-drained", "climate": "Warm/Dry", "sunlight": "Full Sun", "space_requirement": "Small"}
        crit_sandy = RecommendationCriteria(soil_type="Sandy")
        res_wd = self.engine.calculate_score(plant_wd, crit_sandy)
        self.assertTrue(any("Soil compatible" in m for m in res_wd.matched_factors))

        # Mismatched soil (Clay vs Sandy)
        crit_clay = RecommendationCriteria(soil_type="Clay")
        res_mismatch = self.engine.calculate_score(plant, crit_clay)
        self.assertTrue(any("Soil preference differs" in u for u in res_mismatch.unmatched_factors))

    def test_climate_matching(self):
        """Verify climate factor evaluation for exact match, compatible zones, and mismatch."""
        plant = {"name": "Test Plant", "soil_type": "Sandy", "climate": "Warm/Dry", "sunlight": "Full Sun", "space_requirement": "Small"}

        # Exact match
        crit_exact = RecommendationCriteria(climate="Warm/Dry")
        res_exact = self.engine.calculate_score(plant, crit_exact)
        self.assertTrue(any("Climate matches" in m for m in res_exact.matched_factors))

        # Compatible warm zone
        crit_warm = RecommendationCriteria(climate="Tropical")
        res_warm = self.engine.calculate_score(plant, crit_warm)
        self.assertTrue(any("Climate compatible" in m for m in res_warm.matched_factors))

        # Incompatible cold climate
        crit_cold = RecommendationCriteria(climate="Arctic")
        res_cold = self.engine.calculate_score(plant, crit_cold)
        self.assertTrue(any("Climate preference differs" in u for u in res_cold.unmatched_factors))

    def test_sunlight_matching(self):
        """Verify sunlight factor evaluation for exact match, tolerances, and mismatch."""
        plant = {"name": "Test Plant", "soil_type": "Sandy", "climate": "Warm/Dry", "sunlight": "Full Sun", "space_requirement": "Small"}

        # Exact match
        crit_exact = RecommendationCriteria(sunlight="Full Sun")
        res_exact = self.engine.calculate_score(plant, crit_exact)
        self.assertTrue(any("Sunlight matches" in m for m in res_exact.matched_factors))

        # Mismatch
        crit_shade = RecommendationCriteria(sunlight="Low Light")
        res_shade = self.engine.calculate_score(plant, crit_shade)
        self.assertTrue(any("Sunlight preference differs" in u for u in res_shade.unmatched_factors))

    def test_space_matching(self):
        """Verify space factor evaluation for various space footprints."""
        plant_compact = {"name": "Compact Plant", "soil_type": "Sandy", "climate": "Warm/Dry", "sunlight": "Full Sun", "space_requirement": "Compact"}
        plant_large = {"name": "Large Plant", "soil_type": "Sandy", "climate": "Warm/Dry", "sunlight": "Full Sun", "space_requirement": "Large"}

        # Small user space with compact plant
        crit_small = RecommendationCriteria(space="Small")
        res_compact = self.engine.calculate_score(plant_compact, crit_small)
        self.assertTrue(any("Space fits" in m for m in res_compact.matched_factors))

        # Small user space with large plant
        res_large = self.engine.calculate_score(plant_large, crit_small)
        self.assertTrue(any("Space differs" in u for u in res_large.unmatched_factors))

        # Expansive user space accommodates any plant
        crit_expansive = RecommendationCriteria(space="Expansive")
        res_exp = self.engine.calculate_score(plant_large, crit_expansive)
        self.assertTrue(any("Space fits" in m for m in res_exp.matched_factors))


if __name__ == "__main__":
    unittest.main()
