"""Plant API Service — central service layer for external plant data enrichment.

This is the only module that Flask routes, the recommendation engine, or any
other part of the application should call when it needs external plant data.
All provider-specific logic is encapsulated inside the integration clients.

Responsibilities
----------------
- Choose the correct external API provider (currently Perenual).
- Apply an in-process TTL cache to avoid redundant API calls.
- Merge external enrichment with local database records.
- Provide an automatic fallback to local/seed data when the API is unavailable
  or unconfigured, so the application never becomes non-functional.

Configuration (all via environment variables, never hardcoded)
--------------------------------------------------------------
  PLANT_API_KEY         Primary API key (alias for PERENUAL_API_KEY)
  PLANT_API_BASE_URL    Override the provider base URL (optional)
  PLANT_API_TIMEOUT     Request timeout in seconds (default 8)
  PLANT_API_CACHE_TTL   Cache TTL in seconds (default 300 = 5 minutes)
  PERENUAL_API_KEY      Perenual-specific API key (used if PLANT_API_KEY absent)
"""

import logging
import os
import time
from typing import Any

from backend.integrations.perenual_client import PerenualClient
from backend.integrations.schema import NormalizedPlant

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Simple thread-safe in-process TTL cache (no Redis dependency required)
# ---------------------------------------------------------------------------
class _TTLCache:
    """Lightweight dictionary-backed cache with per-entry TTL expiry."""

    def __init__(self, default_ttl: int = 300):
        self._store: dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Any:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        self._store[key] = (value, time.monotonic() + ttl)

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)


# Module-level shared cache instance
_cache = _TTLCache(
    default_ttl=int(os.getenv("PLANT_API_CACHE_TTL", "300"))
)


# ---------------------------------------------------------------------------
# PlantApiService
# ---------------------------------------------------------------------------
class PlantApiService:
    """Provider-agnostic service for fetching and enriching plant data.

    Usage example (in a Flask route or service)::

        from backend.services.plant_api_service import PlantApiService

        api_svc = PlantApiService()
        enriched = api_svc.enrich_plant("Aloe Vera")
        if enriched:
            # Merge enriched data with local DB record
            ...
    """

    def __init__(self):
        # Resolve API key from either generic or Perenual-specific env var
        api_key = (
            os.getenv("PLANT_API_KEY")
            or os.getenv("PERENUAL_API_KEY")
            or None
        )
        base_url  = os.getenv("PLANT_API_BASE_URL")
        timeout   = int(os.getenv("PLANT_API_TIMEOUT", "8"))

        self._client = PerenualClient(api_key=api_key, timeout=timeout)

        # Allow base URL override (e.g., for testing with a mock server)
        if base_url:
            self._client.BASE_URL = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True when an external API provider is configured."""
        return self._client.is_configured()

    def enrich_plant(self, plant_name: str) -> dict[str, Any] | None:
        """Fetch external enrichment data for a single plant by name.

        Returns a NormalizedPlant-derived dict, or None when the API is
        unavailable / the plant is not found — callers must handle None.

        Results are cached for PLANT_API_CACHE_TTL seconds.
        """
        if not self.is_available():
            logger.debug("External plant API not configured — enrichment skipped.")
            return None

        cache_key = f"enrich:{plant_name.lower().strip()}"
        cached = _cache.get(cache_key)
        if cached is not None:
            logger.debug("Cache hit for plant enrichment: %s", plant_name)
            return cached

        try:
            result: NormalizedPlant | None = self._client.enrich_plant(plant_name)
        except Exception as exc:
            logger.warning("External API error during enrich_plant('%s'): %s", plant_name, exc)
            return None

        if result is None:
            return None

        data = result.to_dict()
        _cache.set(cache_key, data)
        logger.info("Enriched plant data fetched for '%s' (source: %s)", plant_name, result.source)
        return data

    def search_plants(self, query: str, page: int = 1) -> list[dict[str, Any]]:
        """Search external API for plants matching query.

        Returns a (possibly empty) list of normalized plant dicts.
        Results are cached per (query, page) pair.
        """
        if not self.is_available():
            return []

        cache_key = f"search:{query.lower().strip()}:{page}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            results = self._client.search_plants(query, page=page)
        except Exception as exc:
            logger.warning("External API error during search_plants('%s'): %s", query, exc)
            return []

        normalized = [r.to_dict() for r in results]
        _cache.set(cache_key, normalized)
        return normalized

    def merge_with_local(
        self,
        local_plant: dict[str, Any],
        external_data: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Merge external enrichment into a local plant dict.

        Strategy: local PostgreSQL data takes precedence for critical
        identification fields (name, soil_type, climate, sunlight, water_needs).
        External data fills in gaps (image, description, care notes).

        This ensures the recommendation engine always scores against reliable
        local data, while the UI benefits from richer content when available.
        """
        if not external_data:
            return {**local_plant, "external_enriched": False}

        # Fields to pull from external ONLY when local value is absent/None
        FILL_FROM_EXTERNAL = [
            "image_url", "thumbnail_url", "description",
            "watering_frequency", "fertilizer_notes", "pruning_notes",
            "hardiness_zone", "indoor_suitable", "poisonous_to_pets",
            "scientific_name", "common_names",
        ]

        merged = dict(local_plant)
        for field in FILL_FROM_EXTERNAL:
            if not merged.get(field) and external_data.get(field):
                merged[field] = external_data[field]

        merged["external_enriched"] = True
        merged["external_source"]   = external_data.get("source", "external")
        merged["external_id"]       = external_data.get("external_id")
        return merged

    def enrich_plant_record(self, local_plant: dict[str, Any]) -> dict[str, Any]:
        """High-level helper: fetch enrichment and merge with a local plant dict.

        Guarantees a fallback to the original local_plant dict on any error.
        """
        name = local_plant.get("name", "")
        if not name:
            return {**local_plant, "external_enriched": False}

        external = self.enrich_plant(name)
        return self.merge_with_local(local_plant, external)

    def cache_info(self) -> dict[str, Any]:
        """Return cache statistics for debugging / health endpoints."""
        return {
            "provider_configured": self.is_available(),
            "cache_entries": len(_cache),
            "cache_ttl_seconds": _cache.default_ttl,
        }

    def clear_cache(self) -> None:
        """Manually invalidate the in-process cache (useful in tests)."""
        _cache.clear()
        logger.info("PlantApiService cache cleared.")
