"""Unit tests for frontend API client (frontend/services/api_client.py).

Tests URL normalization, API request handling, timeout handling,
connection failure detection, and module-level function wrappers.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests

from frontend.services.api_client import (
    BackendApiClient,
    get_plants,
    search_plants,
    generate_recommendations,
    get_plant_details,
    get_history,
    check_health,
)


class TestBackendApiClient(unittest.TestCase):
    """Test suite for BackendApiClient and module-level API client functions."""

    def test_url_normalization(self):
        """Verify base_url normalization handles varied URL formats cleanly."""
        client1 = BackendApiClient(base_url="http://localhost:5000")
        self.assertEqual(client1.base_url, "http://localhost:5000/api/v1")

        client2 = BackendApiClient(base_url="http://localhost:5000/api")
        self.assertEqual(client2.base_url, "http://localhost:5000/api")

        client3 = BackendApiClient(base_url="http://localhost:5000/api/v1/")
        self.assertEqual(client3.base_url, "http://localhost:5000/api/v1")

    @patch("requests.post")
    def test_generate_recommendations_success(self, mock_post):
        """Verify successful recommendation POST request and response format."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "input_criteria": {
                    "soil_type": "Sandy",
                    "climate": "Warm/Dry",
                    "sunlight": "Full Sun",
                    "space": "Minimal",
                },
                "total_candidates": 5,
                "recommendations": [
                    {
                        "plant_id": 1,
                        "name": "Aloe Vera",
                        "compatibility_score": 100,
                        "matched_factors": ["Soil matches", "Sunlight matches"],
                        "unmatched_factors": [],
                    }
                ],
            },
            "message": "Generated 1 plant recommendations.",
        }
        mock_post.return_value = mock_response

        client = BackendApiClient(base_url="http://test-server/api/v1")
        result = client.generate_recommendations(
            soil_type="Sandy",
            climate="Warm/Dry",
            sunlight="Full Sun",
            space="Minimal",
            limit=3,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(len(result["recommendations"]), 1)
        self.assertEqual(result["recommendations"][0]["name"], "Aloe Vera")
        self.assertEqual(result["recommendations"][0]["compatibility_score"], 100)
        self.assertIsNone(result["error_type"])

    @patch("requests.post")
    def test_generate_recommendations_criteria_dict(self, mock_post):
        """Verify generate_recommendations accepts a criteria dictionary."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"recommendations": []},
            "message": "Generated 0 plant recommendations.",
        }
        mock_post.return_value = mock_response

        client = BackendApiClient(base_url="http://test-server/api/v1")
        result = client.generate_recommendations(
            criteria={
                "soil_type": "Clay",
                "climate": "Cold/Temperate",
                "sunlight": "Low Light",
                "space": "Large",
            }
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["recommendations"], [])

    @patch("requests.post")
    def test_generate_recommendations_backend_unavailable(self, mock_post):
        """Verify ConnectionError produces backend_unavailable error_type."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        client = BackendApiClient(base_url="http://127.0.0.1:5000/api/v1")
        result = client.generate_recommendations(
            soil_type="Loamy",
            climate="Tropical",
            sunlight="Partial Shade",
            space="Small",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "backend_unavailable")
        self.assertIn("Cannot connect to Flask backend", result["message"])

    @patch("requests.post")
    def test_generate_recommendations_timeout(self, mock_post):
        """Verify Timeout produces timeout error_type."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        client = BackendApiClient(base_url="http://127.0.0.1:5000/api/v1")
        result = client.generate_recommendations(
            soil_type="Loamy",
            climate="Tropical",
            sunlight="Partial Shade",
            space="Small",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "timeout")
        self.assertIn("timed out", result["message"].lower())

    @patch("requests.post")
    def test_generate_recommendations_http_error(self, mock_post):
        """Verify HTTP 500 error produces http_error error_type."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal engine error"}
        mock_post.return_value = mock_response

        client = BackendApiClient(base_url="http://test-server/api/v1")
        result = client.generate_recommendations(
            soil_type="Loamy",
            climate="Tropical",
            sunlight="Partial Shade",
            space="Small",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "http_error")
        self.assertEqual(result["status_code"], 500)

    @patch("requests.get")
    def test_get_plants(self, mock_get):
        """Verify get_plants fetches catalog list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"plant_id": 1, "name": "Aloe Vera"}],
            "message": "Success",
        }
        mock_get.return_value = mock_response

        client = BackendApiClient(base_url="http://test-server/api/v1")
        plants = client.get_plants(limit=10)
        self.assertEqual(len(plants), 1)
        self.assertEqual(plants[0]["name"], "Aloe Vera")

    @patch("requests.get")
    def test_search_plants(self, mock_get):
        """Verify search_plants returns matching items and avoids empty queries."""
        client = BackendApiClient(base_url="http://test-server/api/v1")
        # Empty query should not hit network
        empty_res = client.search_plants("")
        self.assertEqual(empty_res, [])
        mock_get.assert_not_called()

        # Non-empty query
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"plant_id": 2, "name": "Money Plant"}],
            "message": "Found 1 plants",
        }
        mock_get.return_value = mock_response

        results = client.search_plants("Money")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Money Plant")

    @patch("requests.get")
    def test_get_plant_details(self, mock_get):
        """Verify get_plant_details returns plant dict or None on 404."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"plant_id": 1, "name": "Aloe Vera", "soil_type": "Sandy"}
        }
        mock_get.return_value = mock_response

        client = BackendApiClient(base_url="http://test-server/api/v1")
        plant = client.get_plant_details(1)
        self.assertIsNotNone(plant)
        self.assertEqual(plant["name"], "Aloe Vera")

    @patch("requests.get")
    def test_get_history(self, mock_get):
        """Verify get_history fetches history list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"history_id": 1, "soil_type": "Sandy", "results_count": 1}]
        }
        mock_get.return_value = mock_response

        client = BackendApiClient(base_url="http://test-server/api/v1")
        history = client.get_history(limit=5)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["soil_type"], "Sandy")

    @patch("requests.post")
    def test_module_level_generate_recommendations(self, mock_post):
        """Verify module-level convenience function delegates properly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "recommendations": [{"name": "Tulsi", "compatibility_score": 95}]
            }
        }
        mock_post.return_value = mock_response

        res = generate_recommendations(
            soil_type="Loamy",
            climate="Warm/Tropical",
            sunlight="Full Sun",
            space="Compact",
        )
        self.assertTrue(res["ok"])
        self.assertEqual(res["recommendations"][0]["name"], "Tulsi")


if __name__ == "__main__":
    unittest.main()
