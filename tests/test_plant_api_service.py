"""Tests for PlantApiService and PerenualClient.

These tests run without network access by mocking the requests library.
No real API keys are required.
"""

import unittest
from unittest.mock import MagicMock, patch

from backend.integrations.schema import NormalizedPlant
from backend.integrations.perenual_client import PerenualClient
from backend.services.plant_api_service import PlantApiService


# ---------------------------------------------------------------------------
# NormalizedPlant schema tests
# ---------------------------------------------------------------------------
class TestNormalizedPlant(unittest.TestCase):
    def test_to_dict_contains_expected_keys(self):
        plant = NormalizedPlant(name="Aloe Vera", source="perenual")
        d = plant.to_dict()
        self.assertEqual(d["name"], "Aloe Vera")
        self.assertEqual(d["source"], "perenual")
        self.assertIn("image_url", d)
        self.assertIn("description", d)
        self.assertIsNone(d["external_id"])

    def test_defaults_are_safe_types(self):
        plant = NormalizedPlant(name="Test")
        self.assertIsInstance(plant.common_names, list)
        self.assertIsNone(plant.scientific_name)


# ---------------------------------------------------------------------------
# PerenualClient — unconfigured behaviour
# ---------------------------------------------------------------------------
class TestPerenualClientUnconfigured(unittest.TestCase):
    def setUp(self):
        self.client = PerenualClient(api_key=None)

    def test_is_configured_false_when_no_key(self):
        self.assertFalse(self.client.is_configured())

    def test_search_returns_empty_list_without_key(self):
        results = self.client.search_plants("rose")
        self.assertEqual(results, [])

    def test_get_plant_details_returns_none_without_key(self):
        result = self.client.get_plant_details(123)
        self.assertIsNone(result)

    def test_enrich_plant_returns_none_without_key(self):
        result = self.client.enrich_plant("Tulsi")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# PerenualClient — mocked API responses
# ---------------------------------------------------------------------------
MOCK_SEARCH_RESPONSE = {
    "data": [
        {
            "id": 42,
            "common_name": "Aloe Vera",
            "scientific_name": ["Aloe barbadensis miller"],
            "other_name": ["True Aloe"],
            "sunlight": ["part_shade"],
            "watering": "minimum",
            "indoor": 1,
            "poisonous_to_pets": 0,
            "default_image": {
                "original_url": "https://example.com/aloe.jpg",
                "small_url": "https://example.com/aloe_thumb.jpg",
            },
        }
    ]
}

MOCK_DETAIL_RESPONSE = {
    "id": 42,
    "common_name": "Aloe Vera",
    "scientific_name": ["Aloe barbadensis miller"],
    "sunlight": ["part_shade"],
    "watering": "minimum",
    "description": "A succulent plant species.",
    "indoor": 1,
    "default_image": {
        "original_url": "https://example.com/aloe.jpg",
        "small_url": "https://example.com/aloe_thumb.jpg",
    },
}


class TestPerenualClientMocked(unittest.TestCase):
    def setUp(self):
        self.client = PerenualClient(api_key="test-key-abc")

    def _mock_get(self, json_data: dict):
        mock_resp = MagicMock()
        mock_resp.json.return_value = json_data
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    def test_is_configured_true_with_key(self):
        self.assertTrue(self.client.is_configured())

    @patch("backend.integrations.perenual_client.requests.get")
    def test_search_returns_normalized_plant(self, mock_get):
        mock_get.return_value = self._mock_get(MOCK_SEARCH_RESPONSE)
        results = self.client.search_plants("aloe")
        self.assertEqual(len(results), 1)
        plant = results[0]
        self.assertIsInstance(plant, NormalizedPlant)
        self.assertEqual(plant.name, "Aloe Vera")
        self.assertEqual(plant.sunlight, "Partial Shade")
        self.assertEqual(plant.water_needs, "Low")
        self.assertEqual(plant.source, "perenual")
        self.assertEqual(plant.external_id, "42")

    @patch("backend.integrations.perenual_client.requests.get")
    def test_get_plant_details_returns_normalized_plant(self, mock_get):
        mock_get.return_value = self._mock_get(MOCK_DETAIL_RESPONSE)
        plant = self.client.get_plant_details(42)
        self.assertIsNotNone(plant)
        self.assertEqual(plant.description, "A succulent plant species.")
        self.assertEqual(plant.image_url, "https://example.com/aloe.jpg")

    @patch("backend.integrations.perenual_client.requests.get")
    def test_timeout_returns_empty(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.Timeout
        results = self.client.search_plants("rose")
        self.assertEqual(results, [])

    @patch("backend.integrations.perenual_client.requests.get")
    def test_connection_error_returns_empty(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError
        results = self.client.search_plants("rose")
        self.assertEqual(results, [])


# ---------------------------------------------------------------------------
# PlantApiService — configured / unconfigured behaviour
# ---------------------------------------------------------------------------
class TestPlantApiServiceUnconfigured(unittest.TestCase):
    """Test service behaviour with no API key (fallback path)."""

    def setUp(self):
        # Patch env so no key is present
        with patch.dict("os.environ", {"PLANT_API_KEY": "", "PERENUAL_API_KEY": ""}):
            self.service = PlantApiService()

    def test_is_available_false_without_key(self):
        self.assertFalse(self.service.is_available())

    def test_enrich_plant_returns_none(self):
        result = self.service.enrich_plant("Aloe Vera")
        self.assertIsNone(result)

    def test_search_plants_returns_empty(self):
        results = self.service.search_plants("cactus")
        self.assertEqual(results, [])

    def test_enrich_plant_record_returns_local_data_unchanged(self):
        local = {"name": "Snake Plant", "soil_type": "Sandy"}
        result = self.service.enrich_plant_record(local)
        self.assertEqual(result["name"], "Snake Plant")
        self.assertFalse(result["external_enriched"])


class TestPlantApiServiceMerge(unittest.TestCase):
    """Test merge_with_local logic without network calls."""

    def setUp(self):
        with patch.dict("os.environ", {"PLANT_API_KEY": "", "PERENUAL_API_KEY": ""}):
            self.service = PlantApiService()

    def test_merge_fills_gaps_from_external(self):
        local = {"name": "Aloe Vera", "soil_type": "Sandy", "image_url": None}
        external = {
            "image_url": "https://example.com/aloe.jpg",
            "description": "A succulent.",
            "source": "perenual",
            "external_id": "42",
        }
        merged = self.service.merge_with_local(local, external)
        self.assertEqual(merged["image_url"], "https://example.com/aloe.jpg")
        self.assertEqual(merged["description"], "A succulent.")
        self.assertTrue(merged["external_enriched"])

    def test_merge_local_values_take_precedence(self):
        local = {"name": "Aloe Vera", "soil_type": "Sandy"}
        external = {"soil_type": "Clay", "source": "perenual", "external_id": "1"}
        merged = self.service.merge_with_local(local, external)
        # soil_type is NOT in FILL_FROM_EXTERNAL — local value must remain
        self.assertEqual(merged["soil_type"], "Sandy")

    def test_merge_with_none_external_returns_local_with_flag(self):
        local = {"name": "Tulsi"}
        merged = self.service.merge_with_local(local, None)
        self.assertFalse(merged["external_enriched"])
        self.assertEqual(merged["name"], "Tulsi")

    def test_cache_info_structure(self):
        info = self.service.cache_info()
        self.assertIn("provider_configured", info)
        self.assertIn("cache_entries", info)
        self.assertIn("cache_ttl_seconds", info)

    def test_clear_cache_resets_entries(self):
        self.service._plant_api if hasattr(self.service, "_plant_api") else None
        self.service.clear_cache()
        self.assertEqual(self.service.cache_info()["cache_entries"], 0)


# ---------------------------------------------------------------------------
class TestPlantApiServiceCaching(unittest.TestCase):
    """Verify that caching prevents duplicate API calls."""

    @patch("backend.integrations.perenual_client.requests.get")
    def test_second_call_hits_cache(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_SEARCH_RESPONSE
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        with patch.dict("os.environ", {"PLANT_API_KEY": "test-key-xyz", "PERENUAL_API_KEY": ""}):
            svc = PlantApiService()
            svc.clear_cache()

            _ = svc.search_plants("aloe", page=1)
            _ = svc.search_plants("aloe", page=1)  # second call — should use cache

        # requests.get should only be called once
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
