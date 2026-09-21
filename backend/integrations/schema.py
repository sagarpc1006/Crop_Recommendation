"""Normalized internal plant data format.

All external API responses are transformed into this schema before
reaching any other part of the application. Flask routes, the recommendation
engine, and services ONLY interact with this normalized format — never
with raw external API payloads.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NormalizedPlant:
    """Internal, provider-agnostic plant data record.

    Fields map to the minimum information required by the application.
    Optional fields default to None and must be handled gracefully by consumers.
    """
    # Identity
    name: str
    scientific_name: str | None = None
    common_names: list[str] = field(default_factory=list)

    # Media
    image_url: str | None = None
    thumbnail_url: str | None = None

    # Characteristics (match Plant ORM field names for easy merging)
    soil_type: str | None = None
    climate: str | None = None
    sunlight: str | None = None
    water_needs: str | None = None
    space_requirement: str | None = None

    # Care information
    description: str | None = None
    watering_frequency: str | None = None
    fertilizer_notes: str | None = None
    pruning_notes: str | None = None
    hardiness_zone: str | None = None
    indoor_suitable: bool | None = None
    poisonous_to_pets: bool | None = None

    # Provenance
    source: str = "local"          # "perenual" | "trefle" | "local"
    external_id: str | None = None  # Provider's own record ID for deduplication

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-compatible dictionary."""
        return {
            "name": self.name,
            "scientific_name": self.scientific_name,
            "common_names": self.common_names,
            "image_url": self.image_url,
            "thumbnail_url": self.thumbnail_url,
            "soil_type": self.soil_type,
            "climate": self.climate,
            "sunlight": self.sunlight,
            "water_needs": self.water_needs,
            "space_requirement": self.space_requirement,
            "description": self.description,
            "watering_frequency": self.watering_frequency,
            "fertilizer_notes": self.fertilizer_notes,
            "pruning_notes": self.pruning_notes,
            "hardiness_zone": self.hardiness_zone,
            "indoor_suitable": self.indoor_suitable,
            "poisonous_to_pets": self.poisonous_to_pets,
            "source": self.source,
            "external_id": self.external_id,
        }
