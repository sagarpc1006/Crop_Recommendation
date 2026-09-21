"""Plant Service layer handling database interactions and business logic."""

import logging
from typing import Any
from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.database.models.plant import Plant
from backend.database.seed import SAMPLE_PLANTS

logger = logging.getLogger(__name__)


def _sample_plants_with_ids() -> list[dict[str, Any]]:
    """Return SAMPLE_PLANTS with synthesized positive integer plant_id values."""
    res = []
    for idx, p in enumerate(SAMPLE_PLANTS, start=1):
        d = dict(p)
        d["plant_id"] = idx
        res.append(d)
    return res


class PlantService:
    """Service class encapsulating plant-related business operations.

    Provides clean separation between API routes and database queries,
    with automatic fallback to curated botanical sample records when
    PostgreSQL is offline or unseeded.
    """

    def __init__(self, db_session: Session | None = None):
        self.db = db_session

    def get_all_plants(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Retrieve paginated plants from the database, falling back to SAMPLE_PLANTS."""
        if self.db:
            try:
                plants = self.db.query(Plant).offset(offset).limit(limit).all()
                if plants:
                    return [p.to_dict() for p in plants]
            except Exception as e:
                logger.warning(f"Database query failed in get_all_plants, falling back to sample plants: {e}")

        samples = _sample_plants_with_ids()
        return samples[offset : offset + limit]

    def get_plant_by_id(self, plant_id: int) -> dict[str, Any] | None:
        """Retrieve a specific plant by its identifier."""
        if self.db:
            try:
                plant = self.db.query(Plant).filter(Plant.plant_id == plant_id).first()
                if plant:
                    return plant.to_dict()
            except Exception as e:
                logger.warning(f"Database query failed in get_plant_by_id({plant_id}): {e}")

        # Fallback to SAMPLE_PLANTS by synthesized ID or index
        samples = _sample_plants_with_ids()
        for p in samples:
            if p.get("plant_id") == plant_id:
                return p
        return None

    def search_plants(self, query: str) -> list[dict[str, Any]]:
        """Search plants by name, soil_type, climate, or sunlight.

        Performs a case-insensitive substring match across key text columns.
        Falls back to SAMPLE_PLANTS if database is unreachable.
        """
        if not query or not query.strip():
            return []

        q_clean = query.strip()

        if self.db:
            try:
                like_pattern = f"%{q_clean}%"
                plants = (
                    self.db.query(Plant)
                    .filter(
                        or_(
                            Plant.name.ilike(like_pattern),
                            Plant.soil_type.ilike(like_pattern),
                            Plant.climate.ilike(like_pattern),
                            Plant.sunlight.ilike(like_pattern),
                        )
                    )
                    .limit(50)
                    .all()
                )
                if plants:
                    return [p.to_dict() for p in plants]
            except Exception as e:
                logger.warning(f"Database query failed in search_plants('{query}'): {e}")

        # Fallback: in-memory substring match against SAMPLE_PLANTS
        matches = []
        q_lower = q_clean.lower()
        for p in _sample_plants_with_ids():
            name = p.get("name", "").lower()
            soil = p.get("soil_type", "").lower()
            clim = p.get("climate", "").lower()
            sun = p.get("sunlight", "").lower()
            if q_lower in name or q_lower in soil or q_lower in clim or q_lower in sun:
                matches.append(p)
        return matches[:50]

    def create_plant(self, plant_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new plant record in the database."""
        if not self.db:
            return None
        plant = Plant(**plant_data)
        self.db.add(plant)
        self.db.commit()
        self.db.refresh(plant)
        return plant.to_dict()
