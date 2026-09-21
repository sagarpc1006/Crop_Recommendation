"""Plant Service layer handling database interactions and business logic."""

from typing import Any
from sqlalchemy.orm import Session
from backend.database.models.plant import Plant


class PlantService:
    """Service class encapsulating plant-related business operations.
    
    Provides clean separation between API routes and database queries.
    """

    def __init__(self, db_session: Session | None = None):
        self.db = db_session

    def get_all_plants(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Retrieve paginated plants from the database."""
        if not self.db:
            return []
        plants = self.db.query(Plant).offset(offset).limit(limit).all()
        return [p.to_dict() for p in plants]

    def get_plant_by_id(self, plant_id: int) -> dict[str, Any] | None:
        """Retrieve a specific plant by its identifier."""
        if not self.db:
            return None
        plant = self.db.query(Plant).filter(Plant.id == plant_id).first()
        return plant.to_dict() if plant else None

    def create_plant(self, plant_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new plant record in the database."""
        if not self.db:
            return None
        plant = Plant(**plant_data)
        self.db.add(plant)
        self.db.commit()
        self.db.refresh(plant)
        return plant.to_dict()
