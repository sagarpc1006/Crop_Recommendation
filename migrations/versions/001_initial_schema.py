"""Initial relational schema: users, plants, search_history, recommendations.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-21 19:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create 'users' table
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. Create 'plants' table
    op.create_table(
        "plants",
        sa.Column("plant_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("scientific_name", sa.String(length=200), nullable=True),
        sa.Column("soil_type", sa.String(length=100), nullable=False),
        sa.Column("climate", sa.String(length=100), nullable=False),
        sa.Column("sunlight", sa.String(length=100), nullable=False),
        sa.Column("water_needs", sa.String(length=100), nullable=False),
        sa.Column("space_requirement", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("plant_id"),
        sa.UniqueConstraint("name", name="uq_plants_name"),
    )
    op.create_index("ix_plants_name", "plants", ["name"], unique=True)
    op.create_index("ix_plants_soil_type", "plants", ["soil_type"], unique=False)
    op.create_index("ix_plants_climate", "plants", ["climate"], unique=False)
    op.create_index("ix_plants_sunlight", "plants", ["sunlight"], unique=False)
    op.create_index("ix_plants_water_needs", "plants", ["water_needs"], unique=False)
    op.create_index("ix_plants_space_requirement", "plants", ["space_requirement"], unique=False)

    # 3. Create 'search_history' table
    op.create_table(
        "search_history",
        sa.Column("history_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("soil_type", sa.String(length=100), nullable=True),
        sa.Column("climate", sa.String(length=100), nullable=True),
        sa.Column("sunlight", sa.String(length=100), nullable=True),
        sa.Column("water_needs", sa.String(length=100), nullable=True),
        sa.Column("space_requirement", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("query_text", sa.String(length=255), nullable=True),
        sa.Column("results_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("history_id"),
    )
    op.create_index("ix_search_history_user_id", "search_history", ["user_id"], unique=False)
    op.create_index("ix_search_history_timestamp", "search_history", ["timestamp"], unique=False)

    # 4. Create 'recommendations' table
    op.create_table(
        "recommendations",
        sa.Column("rec_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("search_id", sa.Integer(), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.plant_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["search_id"], ["search_history.history_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("rec_id"),
    )
    op.create_index("ix_recommendations_user_id", "recommendations", ["user_id"], unique=False)
    op.create_index("ix_recommendations_plant_id", "recommendations", ["plant_id"], unique=False)
    op.create_index("ix_recommendations_search_id", "recommendations", ["search_id"], unique=False)
    op.create_index("ix_recommendations_timestamp", "recommendations", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recommendations_timestamp", table_name="recommendations")
    op.drop_index("ix_recommendations_search_id", table_name="recommendations")
    op.drop_index("ix_recommendations_plant_id", table_name="recommendations")
    op.drop_index("ix_recommendations_user_id", table_name="recommendations")
    op.drop_table("recommendations")

    op.drop_index("ix_search_history_timestamp", table_name="search_history")
    op.drop_index("ix_search_history_user_id", table_name="search_history")
    op.drop_table("search_history")

    op.drop_index("ix_plants_space_requirement", table_name="plants")
    op.drop_index("ix_plants_water_needs", table_name="plants")
    op.drop_index("ix_plants_sunlight", table_name="plants")
    op.drop_index("ix_plants_climate", table_name="plants")
    op.drop_index("ix_plants_soil_type", table_name="plants")
    op.drop_index("ix_plants_name", table_name="plants")
    op.drop_table("plants")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
