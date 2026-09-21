"""User entity ORM model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, synonym
from backend.database.connection import Base


class User(Base):
    """Represents a registered or identified user in the PostgreSQL database."""

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    id = synonym("user_id")

    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    location = Column(String(150), nullable=True)

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
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(Recommendation.timestamp)"
    )
    search_history = relationship(
        "SearchHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(SearchHistory.timestamp)"
    )

    def to_dict(self) -> dict:
        """Serialize user instance to a JSON-compatible dictionary."""
        return {
            "user_id": self.user_id,
            "id": self.user_id,
            "name": self.name,
            "email": self.email,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id} email='{self.email}'>"
