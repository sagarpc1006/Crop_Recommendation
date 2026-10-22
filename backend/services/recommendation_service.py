"""Recommendation Service coordinating recommendation engine and database persistence."""

import logging
from datetime import datetime, timezone, timedelta
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

        # 3. Log to Database if database session is active
        if self.db:
            try:
                # Resolve target user and profile details
                user_name = criteria_data.get("user_name")
                user_email = criteria_data.get("user_email")
                user_location = criteria_data.get("user_location")

                user = None
                if user_id is not None:
                    user = self.db.query(User).filter(User.user_id == user_id).first()
                if not user and user_email:
                    user = self.db.query(User).filter(User.email == user_email).first()
                if not user:
                    # Fallback to first existing user or create demo user
                    user = self.db.query(User).first()
                    if not user:
                        user = User(
                            name=user_name or "Botanical Explorer",
                            email=user_email or "explorer@example.com",
                            location=user_location or "Austin, TX",
                        )
                        self.db.add(user)
                        self.db.flush()

                # Update user profile information if provided
                if user:
                    if user_name and user.name != user_name:
                        user.name = user_name
                    if user_location and user.location != user_location:
                        user.location = user_location

                # Duplicate Prevention for Searches:
                # Check if an identical search was logged recently (within 60s)
                cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
                recent_search = (
                    self.db.query(SearchHistory)
                    .filter(
                        SearchHistory.user_id == user.user_id,
                        SearchHistory.soil_type == criteria.soil_type,
                        SearchHistory.climate == criteria.climate,
                        SearchHistory.sunlight == criteria.sunlight,
                        SearchHistory.space_requirement == criteria.space,
                        SearchHistory.timestamp >= cutoff,
                    )
                    .order_by(SearchHistory.timestamp.desc())
                    .first()
                )

                if recent_search:
                    search_record = recent_search
                else:
                    search_record = SearchHistory(
                        user_id=user.user_id,
                        soil_type=criteria.soil_type,
                        climate=criteria.climate,
                        sunlight=criteria.sunlight,
                        space_requirement=criteria.space,
                        location=user.location or user_location,
                        results_count=len(ranked_recommendations),
                    )
                    self.db.add(search_record)
                    self.db.flush()

                # Persist relevant recommendations (prevent duplicate records)
                for rec in ranked_recommendations:
                    plant_id = rec.get("plant_id")
                    if not plant_id:
                        continue

                    existing_rec = (
                        self.db.query(Recommendation)
                        .filter(
                            Recommendation.user_id == user.user_id,
                            Recommendation.plant_id == plant_id,
                            Recommendation.search_id == search_record.history_id,
                        )
                        .first()
                    )
                    if existing_rec:
                        continue

                    score_val = round((rec.get("compatibility_score", 0)) / 100.0, 2)
                    matched_summary = ", ".join(rec.get("matched_factors", [])[:3])
                    notes_text = (
                        f"Score: {rec.get('compatibility_score')}%. Matched: {matched_summary}"
                        if matched_summary
                        else f"Score: {rec.get('compatibility_score')}%."
                    )

                    rec_record = Recommendation(
                        user_id=user.user_id,
                        plant_id=plant_id,
                        search_id=search_record.history_id,
                        match_score=score_val,
                        notes=notes_text,
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

    def get_user_recommendations(
        self,
        user_id: int,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """Retrieve individual recommendation records for a specific user.

        Args:
            user_id: User ID to filter recommendations for.
            limit: Maximum records to return.

        Returns:
            List of serialized recommendation records with plant, user, timestamp, score, and preferences.
        """
        if not self.db:
            return []
        try:
            records = (
                self.db.query(Recommendation)
                .filter(Recommendation.user_id == user_id)
                .order_by(Recommendation.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [r.to_dict() for r in records]
        except Exception as e:
            logger.warning(f"Failed to query recommendations for user {user_id}: {e}")
            return []

    def get_all_recommendations(
        self,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """Retrieve recent recommendation records across all users.

        Args:
            limit: Maximum records to return.

        Returns:
            List of serialized recommendation records ordered by most recent.
        """
        if not self.db:
            return []
        try:
            records = (
                self.db.query(Recommendation)
                .order_by(Recommendation.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [r.to_dict() for r in records]
        except Exception as e:
            logger.warning(f"Failed to query all recommendations: {e}")
            return []

    def get_recommendation_history(
        self,
        user_id: int | None = None,
        limit: int = 20
    ) -> list[dict[str, Any]]:
        """Retrieve recent search history sessions with associated recommendations.

        Args:
            user_id: Optional user ID to filter by.
            limit: Maximum records to return.

        Returns:
            List of search history dictionaries with associated recommendations.
        """
        if not self.db:
            return []
        try:
            query = self.db.query(SearchHistory)
            if user_id is not None:
                query = query.filter(SearchHistory.user_id == user_id)
            records = query.order_by(SearchHistory.timestamp.desc()).limit(limit).all()
            results = []
            for r in records:
                item = r.to_dict()
                item["recommendations"] = [rec.to_dict() for rec in r.recommendations]
                results.append(item)
            return results
        except Exception as e:
            logger.warning(f"Failed to query recommendation history: {e}")
            return []
