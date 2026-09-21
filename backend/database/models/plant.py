"""Plant entity ORM model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, synonym
from backend.database.connection import Base


class Plant(Base):
    """Represents a plant entity in the PostgreSQL database."""
    
    __tablename__ = "plants"
    __table_args__ = (
        UniqueConstraint("name", name="uq_plants_name"),
    )

    plant_id = Column(Integer, primary_key=True, autoincrement=True)
    id = synonym("plant_id")

    name = Column(String(150), nullable=False, unique=True, index=True)
    scientific_name = Column(String(200), nullable=True)
    soil_type = Column(String(100), nullable=False, index=True)
    climate = Column(String(100), nullable=False, index=True)
    sunlight = Column(String(100), nullable=False, index=True)
    water_needs = Column(String(100), nullable=False, index=True)
    space_requirement = Column(String(100), nullable=True, index=True, default="Moderate")
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    recommendations = relationship(
        "Recommendation",
        back_populates="plant",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Serialize model instance to a JSON-compatible dictionary."""
        return {
            "plant_id": self.plant_id,
            "id": self.plant_id,
            "name": self.name,
            "scientific_name": self.scientific_name,
            "soil_type": self.soil_type,
            "climate": self.climate,
            "sunlight": self.sunlight,
            "space_requirement": self.space_requirement,
            "water_needs": self.water_needs,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Plant plant_id={self.plant_id} name='{self.name}'>"
