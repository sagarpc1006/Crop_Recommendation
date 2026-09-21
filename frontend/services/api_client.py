"""HTTP API Client connecting the Streamlit frontend to the Flask REST API."""

import requests
from frontend.config import BACKEND_API_URL, API_TIMEOUT_SECONDS


class BackendApiClient:
    """Encapsulates HTTP operations to the Flask REST backend."""

    def __init__(self, base_url: str = BACKEND_API_URL, timeout: int = API_TIMEOUT_SECONDS):
        self.base_url = base_url
        self.timeout = timeout

    def check_health(self) -> dict:
        """Call the backend health check endpoint.
        
        Returns:
            dict containing status, error flags, and backend/database details.
        """
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                body = response.json()
                return {
                    "available": True,
                    "status_code": 200,
                    "data": body.get("data", {}),
                    "message": body.get("message", "Connected"),
                }
            return {
                "available": False,
                "status_code": response.status_code,
                "message": f"Backend returned HTTP {response.status_code}",
                "data": {},
            }
        except requests.exceptions.ConnectionError:
            return {
                "available": False,
                "status_code": None,
                "message": f"Cannot connect to backend at {url}. Ensure Flask server is running.",
                "data": {},
            }
        except Exception as e:
            return {
                "available": False,
                "status_code": None,
                "message": f"Request failed: {str(e)}",
                "data": {},
            }

    def get_system_info(self) -> dict:
        """Fetch system capability information from backend."""
        url = f"{self.base_url}/info"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json().get("data", {})
        except Exception:
            pass
        return {}
