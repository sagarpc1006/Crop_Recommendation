"""Recommendation Service coordinating recommendation engine and database persistence."""

import logging
from typing import Any
from sqlalchemy.orm import Session

from backend.database.models import User, Plant, Recommendation, SearchHistory
from backend.database.seed import SAMPLE_PLANTS
from backend.recommendation.engine import RecommendationEngine, RecommendationCriteria

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service encapsulating plant recommendation generation and database logging."""

    def __init__(self, db_session: Session | None = None):
        self.db = db_session
        self.engine = RecommendationEngine()

    def generate_recommendations(
        self,
        criteria_data: dict[str, Any],
        limit: int = 5,
        user_id: int | None = None
    ) -> dict[str, Any]:
        """Generate ranked plant recommendations based on environmental criteria.
        
        Args:
            criteria_data: Dictionary containing soil_type, climate, sunlight, space.
            limit: Maximum number of recommendations to return.
            user_id: Optional user identifier to log search history and recommendations.
            
        Returns:
            dict containing input criteria and ranked list of ScoredRecommendation dicts.
        """
        criteria = RecommendationCriteria.from_dict(criteria_data)

        # 1. Fetch Candidate Plants
        candidates: list[dict[str, Any]] = []
        if self.db:
            try:
                db_plants = self.db.query(Plant).all()
                candidates = [p.to_dict() for p in db_plants]
            except Exception as e:
                logger.warning(f"Failed to query plants from database: {e}")

        # Fallback to SAMPLE_PLANTS if database is empty or offline
        if not candidates:
            candidates = [dict(p) for p in SAMPLE_PLANTS]

        # 2. Execute Recommendation Engine
        ranked_recommendations = self.engine.recommend(
            criteria=criteria,
            plants=candidates,
            top_k=limit
        )

        # 3. Log to Database if user_id is provided and database session is active
        if self.db and user_id is not None:
            try:
                user = self.db.query(User).filter(User.user_id == user_id).first()
                if user:
                    search_record = SearchHistory(
                        user_id=user.user_id,
                        soil_type=criteria.soil_type,
                        climate=criteria.climate,
                        sunlight=criteria.sunlight,
                        space_requirement=criteria.space,
                        results_count=len(ranked_recommendations),
                    )
                    self.db.add(search_record)
                    self.db.flush()

                    # Save top recommendation if a plant match exists
                    if ranked_recommendations:
                        top_rec = ranked_recommendations[0]
                        plant_id = top_rec.get("plant_id")
                        if plant_id:
                            rec_record = Recommendation(
                                user_id=user.user_id,
                                plant_id=plant_id,
                                search_id=search_record.history_id,
                                match_score=round(top_rec["compatibility_score"] / 100.0, 2),
                                notes=f"Score: {top_rec['compatibility_score']}%. "
                                      f"Matched: {', '.join(top_rec['matched_factors'][:2])}",
                            )
                            self.db.add(rec_record)

                    self.db.commit()
            except Exception as log_err:
                self.db.rollback()
                logger.warning(f"Could not persist recommendation history: {log_err}")

        return {
            "input_criteria": {
                "soil_type": criteria.soil_type,
                "climate": criteria.climate,
                "sunlight": criteria.sunlight,
                "space": criteria.space,
            },
            "total_candidates": len(candidates),
            "recommendations": ranked_recommendations,
        }
