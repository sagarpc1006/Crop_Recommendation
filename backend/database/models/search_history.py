"""User search / recommendation history ORM model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, synonym
from backend.database.connection import Base


class SearchHistory(Base):
    """Tracks user search criteria and recommendation query history."""

    __tablename__ = "search_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    id = synonym("history_id")

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    soil_type = Column(String(100), nullable=True)
    climate = Column(String(100), nullable=True)
    sunlight = Column(String(100), nullable=True)
    water_needs = Column(String(100), nullable=True)
    space_requirement = Column(String(100), nullable=True)
    location = Column(String(150), nullable=True)
    query_text = Column(String(255), nullable=True)
    results_count = Column(Integer, default=0, nullable=False)

    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship("User", back_populates="search_history")
    recommendations = relationship(
        "Recommendation",
        back_populates="search_history",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Serialize search history record to dictionary."""
        return {
            "history_id": self.history_id,
            "id": self.history_id,
            "user_id": self.user_id,
            "soil_type": self.soil_type,
            "climate": self.climate,
            "sunlight": self.sunlight,
            "water_needs": self.water_needs,
            "space_requirement": self.space_requirement,
            "location": self.location,
            "query_text": self.query_text,
            "results_count": self.results_count,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    def __repr__(self) -> str:
        return f"<SearchHistory history_id={self.history_id} user_id={self.user_id} timestamp='{self.timestamp}'>"
