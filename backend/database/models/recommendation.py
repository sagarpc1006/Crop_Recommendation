"""Recommendation entity ORM model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, synonym
from backend.database.connection import Base


class Recommendation(Base):
    """Represents a generated plant recommendation record for a user or session."""

    __tablename__ = "recommendations"

    rec_id = Column(Integer, primary_key=True, autoincrement=True)
    id = synonym("rec_id")

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    plant_id = Column(
        Integer,
        ForeignKey("plants.plant_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    search_id = Column(
        Integer,
        ForeignKey("search_history.history_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    match_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship("User", back_populates="recommendations")
    plant = relationship("Plant", back_populates="recommendations")
    search_history = relationship("SearchHistory", back_populates="recommendations")

    def to_dict(self) -> dict:
        """Serialize recommendation instance to a JSON-compatible dictionary."""
        return {
            "rec_id": self.rec_id,
            "id": self.rec_id,
            "user_id": self.user_id,
            "plant_id": self.plant_id,
            "search_id": self.search_id,
            "match_score": self.match_score,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "plant": self.plant.to_dict() if self.plant else None,
        }

    def __repr__(self) -> str:
        return f"<Recommendation rec_id={self.rec_id} user_id={self.user_id} plant_id={self.plant_id}>"
