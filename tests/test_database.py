"""Unit tests for the PostgreSQL database layer and ORM models."""

import os
import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from backend.database.connection import Base
from backend.database.models import User, Plant, Recommendation, SearchHistory
from backend.database.seed import seed_database, SAMPLE_PLANTS
from backend.services.plant_service import PlantService


class TestDatabaseLayer(unittest.TestCase):
    """Test suite verifying schemas, relationships, constraints, and seeding."""

    def setUp(self):
        """Set up an isolated in-memory SQLite database for test execution."""
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """Clean up test database session."""
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_table_creation(self):
        """Verify all 4 core tables are successfully created."""
        table_names = list(Base.metadata.tables.keys())
        self.assertIn("users", table_names)
        self.assertIn("plants", table_names)
        self.assertIn("search_history", table_names)
        self.assertIn("recommendations", table_names)

    def test_plant_model_and_synonym(self):
        """Verify Plant attributes, primary key, and id synonym."""
        plant = Plant(
            name="Test Fern",
            soil_type="Loamy",
            climate="Temperate",
            sunlight="Partial Shade",
            water_needs="Medium",
        )
        self.session.add(plant)
        self.session.commit()

        self.assertIsNotNone(plant.plant_id)
        # Verify synonym 'id' returns the same value as 'plant_id'
        self.assertEqual(plant.id, plant.plant_id)
        
        # Verify dictionary serialization contains both keys
        d = plant.to_dict()
        self.assertEqual(d["plant_id"], plant.plant_id)
        self.assertEqual(d["id"], plant.plant_id)
        self.assertEqual(d["name"], "Test Fern")

    def test_duplicate_plant_name_prevented(self):
        """Verify unique constraint prevents duplicate plant records."""
        p1 = Plant(
            name="Duplicate Specimen",
            soil_type="Sandy",
            climate="Warm/Dry",
            sunlight="Full Sun",
            water_needs="Low"
        )
        self.session.add(p1)
        self.session.commit()

        p2 = Plant(
            name="Duplicate Specimen",
            soil_type="Loamy",
            climate="Humid",
            sunlight="Low Light",
            water_needs="High"
        )
        self.session.add(p2)
        with self.assertRaises(IntegrityError):
            self.session.commit()
        self.session.rollback()

    def test_user_and_relationships(self):
        """Verify User model, foreign keys, and relationships."""
        user = User(
            name="Alice Gardner",
            email="alice@example.com",
            location="Seattle, WA"
        )
        self.session.add(user)
        self.session.commit()
        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.id, user.user_id)

        plant = Plant(
            name="Monstera Deliciosa",
            soil_type="Peat",
            climate="Tropical",
            sunlight="Bright Indirect",
            water_needs="Medium"
        )
        self.session.add(plant)
        self.session.commit()

        # Create SearchHistory
        search = SearchHistory(
            user_id=user.user_id,
            soil_type="Peat",
            climate="Tropical",
            sunlight="Bright Indirect",
            results_count=1
        )
        self.session.add(search)
        self.session.commit()

        # Create Recommendation
        rec = Recommendation(
            user_id=user.user_id,
            plant_id=plant.plant_id,
            search_id=search.history_id,
            match_score=0.95
        )
        self.session.add(rec)
        self.session.commit()

        # Verify relationship access
        self.assertEqual(len(user.recommendations), 1)
        self.assertEqual(user.recommendations[0].plant.name, "Monstera Deliciosa")
        self.assertEqual(len(user.search_history), 1)
        self.assertEqual(user.search_history[0].climate, "Tropical")

    def test_seed_database_execution_and_idempotency(self):
        """Verify seeding populates the sample plants and is idempotent."""
        # Initial seed
        stats1 = seed_database(self.session)
        self.assertEqual(stats1["plants_created"], len(SAMPLE_PLANTS))
        self.assertEqual(stats1["users_created"], 1)

        total_plants = self.session.query(Plant).count()
        self.assertEqual(total_plants, len(SAMPLE_PLANTS))

        # Verify each specified plant exists with exact expected criteria
        aloe = self.session.query(Plant).filter(Plant.name == "Aloe Vera").first()
        self.assertIsNotNone(aloe)
        self.assertEqual(aloe.soil_type, "Sandy")
        self.assertEqual(aloe.sunlight, "Full Sun")
        self.assertEqual(aloe.water_needs, "Low")
        self.assertEqual(aloe.climate, "Warm/Dry")

        money = self.session.query(Plant).filter(Plant.name == "Money Plant").first()
        self.assertIsNotNone(money)
        self.assertEqual(money.soil_type, "Loamy")
        self.assertEqual(money.sunlight, "Partial Shade")
        self.assertEqual(money.water_needs, "Medium")
        self.assertEqual(money.climate, "Humid/Tropical")

        tulsi = self.session.query(Plant).filter(Plant.name == "Tulsi").first()
        self.assertIsNotNone(tulsi)
        self.assertEqual(tulsi.soil_type, "Loamy")
        self.assertEqual(tulsi.sunlight, "Full Sun")
        self.assertEqual(tulsi.water_needs, "Medium")
        self.assertEqual(tulsi.climate, "Warm/Tropical")

        snake = self.session.query(Plant).filter(Plant.name == "Snake Plant").first()
        self.assertIsNotNone(snake)
        self.assertEqual(snake.soil_type, "Well-drained")
        self.assertEqual(snake.sunlight, "Low Light")
        self.assertEqual(snake.water_needs, "Low")
        self.assertEqual(snake.climate, "Any/Indoor")

        marigold = self.session.query(Plant).filter(Plant.name == "Marigold").first()
        self.assertIsNotNone(marigold)
        self.assertEqual(marigold.soil_type, "Loamy")
        self.assertEqual(marigold.sunlight, "Full Sun")
        self.assertEqual(marigold.water_needs, "Medium")
        self.assertEqual(marigold.climate, "Warm/Temperate")

        # Second seed (must NOT duplicate records)
        stats2 = seed_database(self.session)
        self.assertEqual(stats2["plants_created"], 0)
        self.assertEqual(stats2["plants_updated"], len(SAMPLE_PLANTS))
        self.assertEqual(self.session.query(Plant).count(), len(SAMPLE_PLANTS))

    def test_plant_service_integration(self):
        """Verify PlantService works seamlessly with the enhanced Plant model."""
        seed_database(self.session)
        service = PlantService(self.session)

        plants = service.get_all_plants(limit=100)
        self.assertEqual(len(plants), len(SAMPLE_PLANTS))

        first_plant_id = plants[0]["plant_id"]
        fetched = service.get_plant_by_id(first_plant_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["plant_id"], first_plant_id)
        self.assertEqual(fetched["id"], first_plant_id)


if __name__ == "__main__":
    unittest.main()
