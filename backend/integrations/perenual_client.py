"""Perenual Plant API client.

Fetches species data from https://perenual.com/docs/api
and normalizes responses into the application's internal NormalizedPlant schema.

API key is read exclusively from the PERENUAL_API_KEY environment variable.
No keys are ever hardcoded.
"""

import logging
import requests
from typing import Any

from backend.integrations.schema import NormalizedPlant

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Perenual sunlight / watering vocabulary → internal vocabulary mappers
# ---------------------------------------------------------------------------
_SUNLIGHT_MAP: dict[str, str] = {
    "full_shade":        "Low Light",
    "part_shade":        "Partial Shade",
    "sun-part_shade":    "Partial Shade",
    "full_sun":          "Full Sun",
}

_WATER_MAP: dict[str, str] = {
    "minimum":  "Low",
    "average":  "Medium",
    "frequent": "High",
    "none":     "Low",
}


def _normalize_sunlight(raw: list[str] | str | None) -> str | None:
    """Convert Perenual's sunlight list to internal vocabulary."""
    if not raw:
        return None
    values = raw if isinstance(raw, list) else [raw]
    for v in values:
        mapped = _SUNLIGHT_MAP.get(str(v).lower().replace(" ", "_"))
        if mapped:
            return mapped
    return str(values[0]).title() if values else None


def _normalize_watering(raw: str | None) -> str | None:
    """Convert Perenual's watering string to internal vocabulary."""
    if not raw:
        return None
    return _WATER_MAP.get(raw.lower(), raw.title())


class PerenualClient:
    """HTTP client for the Perenual Plant API (https://perenual.com/docs/api).

    Public API returns up to 3 pages for free-tier keys (max ~90 records).
    All network calls include configurable timeout and structured error handling.
    """

    BASE_URL = "https://perenual.com/api"

    def __init__(self, api_key: str | None = None, timeout: int = 8):
        self.api_key = api_key
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def is_configured(self) -> bool:
        """Return True when a valid API key is present."""
        return bool(self.api_key)

    def search_plants(self, query: str, page: int = 1) -> list[NormalizedPlant]:
        """Search for plants by common name and return normalized records.

        Falls back to an empty list if the API is unavailable or unconfigured.
        """
        if not self.is_configured():
            logger.debug("Perenual API key not set — search_plants skipped.")
            return []

        url = f"{self.BASE_URL}/species-list"
        params = {"key": self.api_key, "q": query, "page": page}
        raw_list = self._get_json(url, params).get("data", [])
        return [self._normalize(item) for item in raw_list if isinstance(item, dict)]

    def get_plant_details(self, species_id: int) -> NormalizedPlant | None:
        """Fetch full care details for a single species by Perenual species ID.

        Returns None on any error so callers can gracefully fall back.
        """
        if not self.is_configured():
            return None

        url = f"{self.BASE_URL}/species/details/{species_id}"
        params = {"key": self.api_key}
        data = self._get_json(url, params)
        if not data:
            return None
        return self._normalize(data)

    def enrich_plant(self, plant_name: str) -> NormalizedPlant | None:
        """Convenience helper: search by name and return the best match with details.

        Returns None when no match is found or the API is unavailable.
        """
        results = self.search_plants(plant_name, page=1)
        if not results:
            return None

        # Pick the top hit (Perenual returns results ordered by relevance)
        top = results[0]
        if top.external_id:
            try:
                detailed = self.get_plant_details(int(top.external_id))
                if detailed:
                    return detailed
            except Exception:
                pass
        return top

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a GET request and return the parsed JSON body.

        Returns an empty dict on any network or parse error so callers
        never need to handle exceptions.
        """
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.warning("Perenual API request timed out after %ds: %s", self.timeout, url)
        except requests.exceptions.ConnectionError:
            logger.warning("Perenual API unreachable: %s", url)
        except requests.exceptions.HTTPError as exc:
            logger.warning("Perenual API HTTP error %s: %s", exc.response.status_code, url)
        except Exception as exc:
            logger.warning("Perenual API unexpected error: %s", exc)
        return {}

    def _normalize(self, raw: dict[str, Any]) -> NormalizedPlant:
        """Transform a raw Perenual species dict into a NormalizedPlant."""
        # Image — Perenual nests images under default_image
        default_img: dict = raw.get("default_image") or {}
        image_url   = default_img.get("original_url") or default_img.get("regular_url")
        thumbnail   = default_img.get("small_url") or default_img.get("thumbnail")

        # Description — prefer long description, fall back to shorter one
        description = (
            raw.get("description")
            or raw.get("short_description")
            or None
        )

        # Pruning
        pruning_raw = raw.get("pruning_description") or raw.get("pruning_month")
        pruning_notes = (
            ", ".join(pruning_raw) if isinstance(pruning_raw, list) else pruning_raw
        )

        # Indoor
        indoor_val = raw.get("indoor")
        indoor_suitable = bool(indoor_val) if indoor_val is not None else None

        # Poisonous
        poisonous_val = raw.get("poisonous_to_pets") or raw.get("poisonous_to_humans")
        poisonous_to_pets = bool(poisonous_val) if poisonous_val is not None else None

        return NormalizedPlant(
            name            = raw.get("common_name") or raw.get("name") or "Unknown",
            scientific_name = (raw.get("scientific_name") or [""])[0]
                              if isinstance(raw.get("scientific_name"), list)
                              else raw.get("scientific_name"),
            common_names    = raw.get("other_name") or [],
            image_url       = image_url,
            thumbnail_url   = thumbnail,
            sunlight        = _normalize_sunlight(raw.get("sunlight")),
            water_needs     = _normalize_watering(raw.get("watering")),
            hardiness_zone  = raw.get("hardiness", {}).get("min") if isinstance(raw.get("hardiness"), dict) else None,
            description     = description,
            watering_frequency = raw.get("watering_general_benchmark", {}).get("value")
                                if isinstance(raw.get("watering_general_benchmark"), dict) else None,
            pruning_notes   = pruning_notes,
            indoor_suitable = indoor_suitable,
            poisonous_to_pets = poisonous_to_pets,
            source          = "perenual",
            external_id     = str(raw.get("id")) if raw.get("id") else None,
        )
