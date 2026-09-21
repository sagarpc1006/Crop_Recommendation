"""Plant Recommendation Engine architecture.

Defines input criteria schemas and the modular engine interface.
The actual matching algorithms / scoring heuristic will be integrated in future phases.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class RecommendationCriteria:
    """User input criteria for recommending suitable plants."""
    soil_type: str
    climate: str
    sunlight: str
    space_requirement: str


class RecommendationEngine:
    """Core recommendation engine orchestrator.
    
    Modularly designed to accommodate rule-based filtering, weighted scoring,
    or machine learning algorithms in future development stages.
    """

    def __init__(self, candidates: list[dict[str, Any]] | None = None):
        self.candidates = candidates or []

    def recommend(
        self, criteria: RecommendationCriteria, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Compute matching plants based on soil, climate, sunlight, and space.
        
        Note: Foundation stub. Algorithm will be implemented in subsequent stage.
        """
        # Architectural placeholder for matching algorithm
        return []
