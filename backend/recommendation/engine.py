"""Plant Recommendation Engine.

Provides a transparent, explainable scoring-based recommendation algorithm
evaluating soil type, climate, sunlight, and available space.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecommendationCriteria:
    """User input criteria for recommending suitable plants."""
    soil_type: str = "Loamy"
    climate: str = "Tropical"
    sunlight: str = "Partial Shade"
    space: str = "Small"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecommendationCriteria":
        """Create criteria instance from dictionary, handling field aliases."""
        return cls(
            soil_type=str(data.get("soil_type") or data.get("soil") or "Loamy").strip(),
            climate=str(data.get("climate") or "Tropical").strip(),
            sunlight=str(data.get("sunlight") or data.get("sun") or "Partial Shade").strip(),
            space=str(data.get("space") or data.get("space_requirement") or "Small").strip(),
        )


@dataclass
class ScoredRecommendation:
    """Structured, explainable plant recommendation with compatibility score."""
    plant_id: int | None
    name: str
    scientific_name: str | None
    compatibility_score: int
    matched_factors: list[str] = field(default_factory=list)
    unmatched_factors: list[str] = field(default_factory=list)
    basic_care: dict[str, str] = field(default_factory=dict)
    description: str | None = None
    image_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert recommendation to JSON-compatible dictionary."""
        return {
            "plant_id": self.plant_id,
            "name": self.name,
            "scientific_name": self.scientific_name,
            "compatibility_score": self.compatibility_score,
            "matched_factors": self.matched_factors,
            "unmatched_factors": self.unmatched_factors,
            "basic_care": self.basic_care,
            "description": self.description,
            "image_url": self.image_url,
        }


class RecommendationEngine:
    """Transparent, scoring-based plant recommendation engine.
    
    Scores plants against user criteria using deterministic weights:
    - Climate compatibility: 30%
    - Sunlight compatibility: 30%
    - Soil compatibility: 20%
    - Space compatibility: 20%
    Total compatibility score: 0% to 100%.
    """

    WEIGHT_CLIMATE = 30
    WEIGHT_SUNLIGHT = 30
    WEIGHT_SOIL = 20
    WEIGHT_SPACE = 20

    def calculate_score(
        self, plant: dict[str, Any], criteria: RecommendationCriteria
    ) -> ScoredRecommendation:
        """Calculate compatibility score and identify matched/unmatched factors."""
        matched_factors: list[str] = []
        unmatched_factors: list[str] = []

        # 1. Climate Compatibility (30 pts)
        climate_score, c_matched, c_msg = self._evaluate_climate(
            plant_climate=plant.get("climate", ""),
            user_climate=criteria.climate
        )
        if c_matched:
            matched_factors.append(c_msg)
        else:
            unmatched_factors.append(c_msg)

        # 2. Sunlight Compatibility (30 pts)
        sun_score, s_matched, s_msg = self._evaluate_sunlight(
            plant_sunlight=plant.get("sunlight", ""),
            plant_name=plant.get("name", ""),
            user_sunlight=criteria.sunlight
        )
        if s_matched:
            matched_factors.append(s_msg)
        else:
            unmatched_factors.append(s_msg)

        # 3. Soil Compatibility (20 pts)
        soil_score, so_matched, so_msg = self._evaluate_soil(
            plant_soil=plant.get("soil_type", ""),
            user_soil=criteria.soil_type
        )
        if so_matched:
            matched_factors.append(so_msg)
        else:
            unmatched_factors.append(so_msg)

        # 4. Space Compatibility (20 pts)
        space_score, sp_matched, sp_msg = self._evaluate_space(
            plant_space=plant.get("space_requirement", ""),
            user_space=criteria.space
        )
        if sp_matched:
            matched_factors.append(sp_msg)
        else:
            unmatched_factors.append(sp_msg)

        total_score = climate_score + sun_score + soil_score + space_score
        normalized_score = min(100, max(0, int(round(total_score))))

        basic_care = {
            "water_needs": plant.get("water_needs") or "Medium",
            "sunlight": plant.get("sunlight") or "Full Sun",
            "soil_type": plant.get("soil_type") or "Loamy",
            "climate": plant.get("climate") or "Tropical",
            "space_requirement": plant.get("space_requirement") or "Moderate",
        }

        return ScoredRecommendation(
            plant_id=plant.get("plant_id") or plant.get("id"),
            name=plant.get("name", "Unknown Plant"),
            scientific_name=plant.get("scientific_name"),
            compatibility_score=normalized_score,
            matched_factors=matched_factors,
            unmatched_factors=unmatched_factors,
            basic_care=basic_care,
            description=plant.get("description"),
            image_url=plant.get("image_url"),
        )

    def recommend(
        self,
        criteria: RecommendationCriteria,
        plants: list[dict[str, Any]],
        top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Rank candidate plants by compatibility score and return top matches."""
        scored = [self.calculate_score(p, criteria) for p in plants]
        # Sort primarily by score descending, secondarily by name
        scored.sort(key=lambda item: (-item.compatibility_score, item.name))
        top_matches = scored[:top_k]
        return [item.to_dict() for item in top_matches]

    # --- Internal Factor Evaluators ---

    def _evaluate_climate(
        self, plant_climate: str, user_climate: str
    ) -> tuple[float, bool, str]:
        p_c = plant_climate.lower()
        u_c = user_climate.lower()

        # Exact or bidirectional substring match
        if u_c in p_c or p_c in u_c or "any" in p_c or "any" in u_c:
            return (
                self.WEIGHT_CLIMATE,
                True,
                f"Climate matches: well-suited for {plant_climate} environment"
            )

        # Related thermal conditions (e.g. Warm/Tropical vs Tropical or Warm/Dry vs Warm)
        warm_zones = ["warm", "tropical", "humid", "temperate"]
        u_warm = any(w in u_c for w in warm_zones)
        p_warm = any(w in p_c for w in warm_zones)
        if u_warm and p_warm:
            # Partial match (e.g. Warm/Temperate vs Tropical)
            partial = self.WEIGHT_CLIMATE * 0.65
            return (
                partial,
                True,
                f"Climate compatible: {plant_climate} adapts with temperature control"
            )

        return (
            0.0,
            False,
            f"Climate preference differs: plant prefers {plant_climate} conditions"
        )

    def _evaluate_sunlight(
        self, plant_sunlight: str, plant_name: str, user_sunlight: str
    ) -> tuple[float, bool, str]:
        p_s = plant_sunlight.lower()
        u_s = user_sunlight.lower()

        # Exact or substring match
        if u_s in p_s or p_s in u_s:
            return (
                self.WEIGHT_SUNLIGHT,
                True,
                f"Sunlight matches: thrives in {plant_sunlight}"
            )

        # Snake Plant special shade tolerance
        if "snake plant" in plant_name.lower() and ("shade" in u_s or "indirect" in u_s or "low" in u_s):
            return (
                self.WEIGHT_SUNLIGHT * 0.85,
                True,
                f"Sunlight compatible: highly tolerant of {user_sunlight}"
            )

        # Partial light tolerances (Partial Shade vs Full Sun / Low Light)
        if ("partial" in p_s and "indirect" in u_s) or ("indirect" in p_s and "partial" in u_s):
            return (
                self.WEIGHT_SUNLIGHT * 0.80,
                True,
                f"Sunlight compatible: handles {user_sunlight} effectively"
            )

        if ("partial" in p_s and "sun" in u_s) or ("sun" in p_s and "partial" in u_s):
            return (
                self.WEIGHT_SUNLIGHT * 0.50,
                True,
                f"Sunlight compatible: tolerates {user_sunlight} with moderate exposure"
            )

        return (
            0.0,
            False,
            f"Sunlight preference differs: thrives in {plant_sunlight}"
        )

    def _evaluate_soil(
        self, plant_soil: str, user_soil: str
    ) -> tuple[float, bool, str]:
        p_s = plant_soil.lower()
        u_s = user_soil.lower()

        if u_s in p_s or p_s in u_s:
            return (
                self.WEIGHT_SOIL,
                True,
                f"Soil matches: thrives in {plant_soil} soil"
            )

        # "Well-drained" accepts Loamy, Sandy, or Peaty
        if "well-drained" in p_s and ("sandy" in u_s or "loamy" in u_s):
            return (
                self.WEIGHT_SOIL * 0.90,
                True,
                f"Soil compatible: {user_soil} provides required drainage"
            )
        if "well-drained" in u_s and ("sandy" in p_s or "loamy" in p_s):
            return (
                self.WEIGHT_SOIL * 0.90,
                True,
                f"Soil compatible: well-drained medium suits {plant_soil} preference"
            )

        # Loamy and Peaty partial compatibility
        if ("loamy" in p_s and "peat" in u_s) or ("peat" in p_s and "loamy" in u_s):
            return (
                self.WEIGHT_SOIL * 0.60,
                True,
                f"Soil compatible: {plant_soil} can be amended to suit {user_soil}"
            )

        return (
            0.0,
            False,
            f"Soil preference differs: prefers {plant_soil} soil"
        )

    def _evaluate_space(
        self, plant_space: str, user_space: str
    ) -> tuple[float, bool, str]:
        p_sp = plant_space.lower()
        u_sp = user_space.lower()

        # If user has large/expansive space or any
        if any(w in u_sp for w in ["large", "expansive", "garden", "field", "any"]):
            return (
                self.WEIGHT_SPACE,
                True,
                f"Space fits: abundant room for {plant_space} footprint"
            )

        # If user specifies small / compact / minimal / pot / desktop / balcony
        is_user_small = any(w in u_sp for w in ["small", "minimal", "pot", "desktop", "compact", "balcony", "window"])

        if is_user_small:
            if any(w in p_sp for w in ["minimal", "compact", "small", "desk", "pot"]):
                return (
                    self.WEIGHT_SPACE,
                    True,
                    f"Space fits: compact {plant_space} footprint ideal for small spaces"
                )
            if any(w in p_sp for w in ["climbing", "hanging", "vertical"]):
                return (
                    self.WEIGHT_SPACE * 0.85,
                    True,
                    f"Space fits: {plant_space} utilizes vertical footprint efficiently"
                )
            if "moderate" in p_sp:
                return (
                    self.WEIGHT_SPACE * 0.50,
                    True,
                    f"Space manageable: {plant_space} footprint manageable with container pruning"
                )
            return (
                0.0,
                False,
                f"Space differs: requires {plant_space} space, may outgrow small area"
            )

        # Medium / Moderate user space
        if any(w in u_sp for w in ["medium", "moderate"]):
            if any(w in p_sp for w in ["minimal", "compact", "moderate", "climbing", "hanging"]):
                return (
                    self.WEIGHT_SPACE,
                    True,
                    f"Space fits: comfortably accommodates {plant_space} footprint"
                )
            return (
                self.WEIGHT_SPACE * 0.50,
                True,
                f"Space manageable: requires careful placement for {plant_space}"
            )

        return (
            self.WEIGHT_SPACE * 0.50,
            True,
            f"Space manageable for {plant_space}"
        )
