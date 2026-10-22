"""HTTP API Client connecting the Streamlit frontend to the Flask REST API.

All methods return safe, structured dicts or lists — never raise exceptions.
Encapsulates timeout handling, backend availability detection, and error categorization.
Provides both an object-oriented BackendApiClient class and reusable module-level functions.
"""

from typing import Any
import requests
from frontend.config import BACKEND_API_URL, API_TIMEOUT_SECONDS


class BackendApiClient:
    """Reusable HTTP client interface to the Flask REST recommendation backend."""

    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        raw_url = (base_url or BACKEND_API_URL).rstrip("/")
        # Normalize base_url so it targets the /api or /api/v1 prefix safely
        if not (raw_url.endswith("/api") or raw_url.endswith("/api/v1")):
            raw_url = f"{raw_url}/api/v1"
        self.base_url = raw_url
        self.timeout = timeout if timeout is not None else API_TIMEOUT_SECONDS

    # ------------------------------------------------------------------
    # Internal Request Helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        """GET request with timeout, connection error, and HTTP status handling."""
        url = f"{self.base_url}{path}"
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            try:
                body = r.json()
            except Exception:
                body = {}

            if r.status_code == 200:
                return {
                    "ok": True,
                    "data": body.get("data", body),
                    "status_code": 200,
                    "message": body.get("message", "Success"),
                    "error_type": None,
                    "meta": body.get("meta", {}),
                }

            return {
                "ok": False,
                "data": None,
                "status_code": r.status_code,
                "error_type": "http_error",
                "message": body.get("message", f"Backend returned HTTP {r.status_code}"),
                "meta": {},
            }
        except requests.exceptions.ConnectionError:
            return {
                "ok": False,
                "data": None,
                "status_code": None,
                "error_type": "backend_unavailable",
                "message": f"Cannot connect to Flask backend at {self.base_url}. Please ensure the server is running.",
                "meta": {},
            }
        except requests.exceptions.Timeout:
            return {
                "ok": False,
                "data": None,
                "status_code": None,
                "error_type": "timeout",
                "message": f"Request timed out after {self.timeout}s waiting for the backend.",
                "meta": {},
            }
        except Exception as exc:
            return {
                "ok": False,
                "data": None,
                "status_code": None,
                "error_type": "unknown",
                "message": str(exc),
                "meta": {},
            }

    def _post(self, path: str, payload: dict) -> dict[str, Any]:
        """POST request with timeout, connection error, and HTTP status handling."""
        url = f"{self.base_url}{path}"
        try:
            r = requests.post(url, json=payload, timeout=self.timeout)
            try:
                body = r.json()
            except Exception:
                body = {}

            if r.status_code in (200, 201):
                return {
                    "ok": True,
                    "data": body.get("data", body),
                    "status_code": r.status_code,
                    "message": body.get("message", "Success"),
                    "error_type": None,
                    "meta": body.get("meta", {}),
                }

            return {
                "ok": False,
                "data": None,
                "status_code": r.status_code,
                "error_type": "http_error",
                "message": body.get("message", f"Backend returned HTTP {r.status_code}"),
                "meta": {},
            }
        except requests.exceptions.ConnectionError:
            return {
                "ok": False,
                "data": None,
                "status_code": None,
                "error_type": "backend_unavailable",
                "message": f"Cannot connect to Flask backend at {self.base_url}. Please ensure the server is running.",
                "meta": {},
            }
        except requests.exceptions.Timeout:
            return {
                "ok": False,
                "data": None,
                "status_code": None,
                "error_type": "timeout",
                "message": f"Recommendation request timed out after {self.timeout}s.",
                "meta": {},
            }
        except Exception as exc:
            return {
                "ok": False,
                "data": None,
                "status_code": None,
                "error_type": "unknown",
                "message": str(exc),
                "meta": {},
            }

    # ------------------------------------------------------------------
    # Health & System Info
    # ------------------------------------------------------------------

    def check_health(self) -> dict[str, Any]:
        """Check Flask API and PostgreSQL database health status."""
        result = self._get("/health")
        if result["ok"]:
            return {
                "available": True,
                "status_code": 200,
                "data": result["data"],
                "message": result["message"],
                "error_type": None,
            }
        return {
            "available": False,
            "status_code": result["status_code"],
            "data": {},
            "message": result["message"],
            "error_type": result["error_type"],
        }

    def get_system_info(self) -> dict[str, Any]:
        """Fetch metadata about backend capabilities, endpoints, and external APIs."""
        result = self._get("/info")
        return result["data"] if result["ok"] and isinstance(result["data"], dict) else {}

    # ------------------------------------------------------------------
    # Plant Catalog & Search
    # ------------------------------------------------------------------

    def get_plants(self, limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
        """Retrieve paginated plant catalog from the backend database."""
        result = self._get("/plants", params={"limit": limit, "offset": offset})
        if result["ok"] and isinstance(result["data"], list):
            return result["data"]
        return []

    def search_plants(self, query: str, source: str = "all", page: int = 1) -> list[dict[str, Any]]:
        """Search plants across name, soil, climate, or sunlight."""
        if not query or not query.strip():
            return []
        result = self._get(
            "/plants/search",
            params={"q": query.strip(), "source": source, "page": page}
        )
        if result["ok"] and isinstance(result["data"], list):
            return result["data"]
        return []

    def get_plant_details(self, plant_id: int, enrich: bool = True) -> dict[str, Any] | None:
        """Retrieve detailed plant information by ID, optionally with external enrichment."""
        if enrich:
            result = self._get(f"/plants/{plant_id}/enrich")
            if result["ok"] and isinstance(result["data"], dict):
                return result["data"]

        result = self._get(f"/plants/{plant_id}")
        return result["data"] if result["ok"] and isinstance(result["data"], dict) else None

    # Alias for get_plant_details
    get_plant = get_plant_details

    def enrich_plant(self, plant_id: int) -> dict[str, Any] | None:
        """Fetch plant record overlaid with external API care and media data."""
        result = self._get(f"/plants/{plant_id}/enrich")
        return result["data"] if result["ok"] and isinstance(result["data"], dict) else None

    # ------------------------------------------------------------------
    # Recommendation Generation
    # ------------------------------------------------------------------

    def generate_recommendations(
        self,
        soil_type: str | None = None,
        climate: str | None = None,
        sunlight: str | None = None,
        space: str | None = None,
        limit: int = 5,
        user_id: int | None = None,
        enrich: bool = False,
        criteria: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send environmental parameters to Flask recommendation API and receive ranked plant matches.

        Accepts either explicit keyword arguments or a criteria dictionary.

        Args:
            soil_type: Soil texture (Sandy, Loamy, Clay, etc.)
            climate: Climate zone (Tropical, Warm/Dry, etc.)
            sunlight: Daily sun exposure (Full Sun, Partial Shade, etc.)
            space: Available growing space (Small, Medium, Large, etc.)
            limit: Maximum recommendations to return (default 5)
            user_id: Optional user ID for recording recommendation history
            enrich: Whether to pull external media and care data
            criteria: Optional dictionary containing criteria fields

        Returns:
            Dict containing:
                - ok (bool): True if API responded with valid recommendations
                - recommendations (list[dict]): Ranked plant recommendations
                - criteria (dict): Confirmed criteria evaluated by engine
                - total_plants_evaluated (int): Candidate count evaluated
                - message (str): Human-readable status or error description
                - error_type (str|None): "backend_unavailable", "timeout", "http_error", or None
        """
        crit = criteria or {}
        resolved_soil = soil_type or crit.get("soil_type") or crit.get("soil") or "Loamy"
        resolved_climate = climate or crit.get("climate") or "Tropical"
        resolved_sunlight = sunlight or crit.get("sunlight") or crit.get("sun") or "Partial Shade"
        resolved_space = space or crit.get("space") or crit.get("space_requirement") or "Small"
        resolved_limit = limit if limit is not None else crit.get("limit", 5)
        resolved_enrich = enrich or bool(crit.get("enrich", False))

        payload = {
            "soil_type": resolved_soil,
            "climate": resolved_climate,
            "sunlight": resolved_sunlight,
            "space": resolved_space,
            "limit": resolved_limit,
            "enrich": resolved_enrich,
        }
        if user_id is not None or "user_id" in crit:
            payload["user_id"] = user_id if user_id is not None else crit.get("user_id")
        for k in ("user_name", "user_email", "user_location"):
            val = kwargs.get(k) or crit.get(k)
            if val:
                payload[k] = val

        result = self._post("/recommendations/generate", payload)
        if result["ok"] and result["data"]:
            data = result["data"]
            recs = data.get("recommendations", [])
            total_evaluated = data.get("total_candidates", data.get("total_plants_evaluated", len(recs)))
            return {
                "ok": True,
                "recommendations": recs,
                "criteria": data.get("input_criteria", data.get("criteria", payload)),
                "total_plants_evaluated": total_evaluated,
                "message": result.get("message", f"Found {len(recs)} matches"),
                "error_type": None,
                "status_code": result.get("status_code", 200),
            }

        return {
            "ok": False,
            "recommendations": [],
            "criteria": payload,
            "total_plants_evaluated": 0,
            "message": result.get("message", "Recommendation request failed."),
            "error_type": result.get("error_type", "unknown"),
            "status_code": result.get("status_code"),
        }

    # Alias for backwards compatibility
    get_recommendations = generate_recommendations

    # ------------------------------------------------------------------
    # Recommendation History
    # ------------------------------------------------------------------

    def get_user_recommendations(self, user_id: int, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve individual recommendation records for a user from the backend database.

        Args:
            user_id: User ID to fetch recommendation records for.
            limit: Maximum number of records to return.

        Returns:
            List of recommendation dicts, or empty list if unavailable.
        """
        result = self._get(f"/recommendations/{user_id}", params={"limit": limit})
        if result["ok"] and isinstance(result["data"], list):
            return result["data"]
        return []

    def get_history(self, user_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve recent recommendation history from the backend database.

        Args:
            user_id: Optional user ID to filter recommendation history.
            limit: Maximum number of history entries to return.

        Returns:
            List of history records, or empty list if unavailable.
        """
        if user_id is not None:
            return self.get_user_recommendations(user_id=user_id, limit=limit)
        result = self._get("/recommendations/history", params={"limit": limit})
        if result["ok"] and isinstance(result["data"], list):
            return result["data"]
        return []


# ----------------------------------------------------------------------
# Reusable Module-Level Functions
# ----------------------------------------------------------------------

_default_client: BackendApiClient | None = None


def get_default_client() -> BackendApiClient:
    """Return the shared default API client instance."""
    global _default_client
    if _default_client is None:
        _default_client = BackendApiClient()
    return _default_client


def check_health() -> dict[str, Any]:
    """Check backend API and PostgreSQL database health status."""
    return get_default_client().check_health()


def get_system_info() -> dict[str, Any]:
    """Fetch metadata about backend capabilities, endpoints, and external APIs."""
    return get_default_client().get_system_info()


def get_plants(limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
    """Retrieve paginated plant catalog from the backend database."""
    return get_default_client().get_plants(limit=limit, offset=offset)


def search_plants(query: str, source: str = "all", page: int = 1) -> list[dict[str, Any]]:
    """Search plants across name, soil, climate, or sunlight."""
    return get_default_client().search_plants(query=query, source=source, page=page)


def get_plant_details(plant_id: int, enrich: bool = True) -> dict[str, Any] | None:
    """Retrieve detailed plant information by ID, optionally with external enrichment."""
    return get_default_client().get_plant_details(plant_id=plant_id, enrich=enrich)


def get_plant(plant_id: int, enrich: bool = True) -> dict[str, Any] | None:
    """Alias for get_plant_details."""
    return get_plant_details(plant_id=plant_id, enrich=enrich)


def generate_recommendations(
    soil_type: str | None = None,
    climate: str | None = None,
    sunlight: str | None = None,
    space: str | None = None,
    limit: int = 5,
    user_id: int | None = None,
    enrich: bool = False,
    criteria: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate ranked recommendations using the Flask recommendation backend."""
    return get_default_client().generate_recommendations(
        soil_type=soil_type,
        climate=climate,
        sunlight=sunlight,
        space=space,
        limit=limit,
        user_id=user_id,
        enrich=enrich,
        criteria=criteria,
        **kwargs,
    )


def get_recommendations(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Alias for generate_recommendations."""
    return generate_recommendations(*args, **kwargs)


def get_history(user_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve recent recommendation search history from the backend database."""
    return get_default_client().get_history(user_id=user_id, limit=limit)


def get_user_recommendations(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve recommendation records for a user from the backend database."""
    return get_default_client().get_user_recommendations(user_id=user_id, limit=limit)

