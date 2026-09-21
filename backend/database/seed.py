"""Database seeding script for Plant Recommendation System.

Populates initial sample plants, demonstration user, search history,
and recommendation records while enforcing idempotency (no duplicates).
"""

import sys
import logging
from sqlalchemy.orm import Session
from backend.database.connection import get_session_factory, init_db
from backend.database.models import User, Plant, Recommendation, SearchHistory

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Initial sample plant dataset matching prompt specifications
SAMPLE_PLANTS = [
    {
        "name": "Aloe Vera",
        "scientific_name": "Aloe barbadensis miller",
        "soil_type": "Sandy",
        "climate": "Warm/Dry",
        "sunlight": "Full Sun",
        "water_needs": "Low",
        "space_requirement": "Minimal",
        "description": "A succulent plant renowned for its therapeutic and soothing gel. Thrives in dry, sunny environments with minimal watering.",
        "image_url": "https://images.unsplash.com/photo-1596547609652-9cf5d8d76921?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Money Plant",
        "scientific_name": "Epipremnum aureum",
        "soil_type": "Loamy",
        "climate": "Humid/Tropical",
        "sunlight": "Partial Shade",
        "water_needs": "Medium",
        "space_requirement": "Climbing / Hanging",
        "description": "A hardy indoor vine known for heart-shaped variegated leaves. Excels at indoor air purification and adapts well to partial shade.",
        "image_url": "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Tulsi",
        "scientific_name": "Ocimum tenuiflorum",
        "soil_type": "Loamy",
        "climate": "Warm/Tropical",
        "sunlight": "Full Sun",
        "water_needs": "Medium",
        "space_requirement": "Compact",
        "description": "Holy Basil is a sacred aromatic herb celebrated in Ayurvedic medicine. Enjoys sunny conditions and rich loamy soil.",
        "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Snake Plant",
        "scientific_name": "Sansevieria trifasciata",
        "soil_type": "Well-drained",
        "climate": "Any/Indoor",
        "sunlight": "Low Light",
        "water_needs": "Low",
        "space_requirement": "Minimal",
        "description": "An architectural, resilient houseplant with upright sword-like leaves. Thrives in virtually any light setting and requires infrequent watering.",
        "image_url": "https://images.unsplash.com/photo-1593482892290-f54927ae1bf6?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Marigold",
        "scientific_name": "Tagetes erecta",
        "soil_type": "Loamy",
        "climate": "Warm/Temperate",
        "sunlight": "Full Sun",
        "water_needs": "Medium",
        "space_requirement": "Moderate",
        "description": "Bright golden and orange flowering annuals that deter garden pests and flourish in fertile loamy soil under full sun.",
        "image_url": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=600&q=80",
    },
]

DEMO_USER = {
    "name": "Botanical Explorer",
    "email": "explorer@example.com",
    "location": "Austin, TX",
}


def seed_database(session: Session | None = None) -> dict[str, int]:
    """Populates the database with initial plants and demonstration data.
    
    Ensures idempotency: will not create duplicate plant records or users.
    
    Args:
        session: Optional SQLAlchemy Session. If None, a new session is opened.
        
    Returns:
        dict: Counts of seeded entities.
    """
    owns_session = False
    if session is None:
        session_factory = get_session_factory()
        session = session_factory()
        owns_session = True

    stats = {
        "plants_created": 0,
        "plants_updated": 0,
        "users_created": 0,
        "search_history_created": 0,
        "recommendations_created": 0,
    }

    try:
        # 1. Seed Plants (idempotent upsert by name)
        logger.info("Seeding plant catalog...")
        created_plants = {}
        for plant_data in SAMPLE_PLANTS:
            existing_plant = session.query(Plant).filter(Plant.name == plant_data["name"]).first()
            if existing_plant:
                # Update characteristics to ensure latest values
                for key, value in plant_data.items():
                    setattr(existing_plant, key, value)
                created_plants[plant_data["name"]] = existing_plant
                stats["plants_updated"] += 1
                logger.info(f"Updated existing plant: {plant_data['name']}")
            else:
                new_plant = Plant(**plant_data)
                session.add(new_plant)
                session.flush()  # Flush to generate plant_id
                created_plants[plant_data["name"]] = new_plant
                stats["plants_created"] += 1
                logger.info(f"Created new plant: {plant_data['name']} (ID: {new_plant.plant_id})")

        # 2. Seed Demo User (idempotent by email)
        logger.info("Seeding demonstration user...")
        demo_user = session.query(User).filter(User.email == DEMO_USER["email"]).first()
        if not demo_user:
            demo_user = User(**DEMO_USER)
            session.add(demo_user)
            session.flush()
            stats["users_created"] += 1
            logger.info(f"Created demo user: {demo_user.name} ({demo_user.email})")
        else:
            logger.info(f"Demo user already exists: {demo_user.email}")

        # 3. Seed Sample Search Query & Recommendation (if user has none)
        existing_history = session.query(SearchHistory).filter(SearchHistory.user_id == demo_user.user_id).first()
        if not existing_history:
            search_record = SearchHistory(
                user_id=demo_user.user_id,
                soil_type="Sandy",
                climate="Warm/Dry",
                sunlight="Full Sun",
                water_needs="Low",
                space_requirement="Minimal",
                location="Austin, TX",
                query_text="Indoor succulent or desert plant",
                results_count=1,
            )
            session.add(search_record)
            session.flush()
            stats["search_history_created"] += 1

            aloe = created_plants.get("Aloe Vera")
            if aloe:
                rec_record = Recommendation(
                    user_id=demo_user.user_id,
                    plant_id=aloe.plant_id,
                    search_id=search_record.history_id,
                    match_score=0.98,
                    notes="Excellent match for warm/dry climate and sandy soil conditions.",
                )
                session.add(rec_record)
                stats["recommendations_created"] += 1
                logger.info(f"Created sample recommendation: User {demo_user.user_id} -> {aloe.name}")

        session.commit()
        logger.info(f"Seeding completed successfully: {stats}")
        return stats

    except Exception as e:
        session.rollback()
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        if owns_session:
            session.close()


if __name__ == "__main__":
    logger.info("Ensuring database tables exist before seeding...")
    init_db()
    try:
        results = seed_database()
        print("\nSeed Summary:")
        for k, v in results.items():
            print(f" - {k}: {v}")
    except Exception as exc:
        print(f"Error seeding database: {exc}", file=sys.stderr)
        sys.exit(1)
