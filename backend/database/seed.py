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

# Initial sample plant dataset matching prompt specifications (30 curated plants)
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
        "image_url": "https://images.unsplash.com/photo-1572688484438-313a6e50c333?auto=format&fit=crop&w=600&q=80",
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
    {
        "name": "Peace Lily",
        "scientific_name": "Spathiphyllum wallisii",
        "soil_type": "Loamy",
        "climate": "Any/Indoor",
        "sunlight": "Low Light",
        "water_needs": "Medium",
        "space_requirement": "Compact",
        "description": "An elegant indoor plant with glossy dark leaves and striking white spathes. Filters airborne toxins and thrives in sheltered, low-light spaces.",
        "image_url": "https://images.unsplash.com/photo-1593691509543-c55fb32e7355?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Jade Plant",
        "scientific_name": "Crassula ovata",
        "soil_type": "Sandy",
        "climate": "Warm/Dry",
        "sunlight": "Bright Indirect",
        "water_needs": "Low",
        "space_requirement": "Compact",
        "description": "A classic succulent shrub featuring thick fleshy leaves and woody stems. Requires porous sandy potting soil and infrequent watering.",
        "image_url": "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Spider Plant",
        "scientific_name": "Chlorophytum comosum",
        "soil_type": "Loamy",
        "climate": "Any/Indoor",
        "sunlight": "Partial Shade",
        "water_needs": "Medium",
        "space_requirement": "Climbing / Hanging",
        "description": "Graceful arching foliage with cascading plantlets. Remarkably forgiving, excellent at purifying indoor air, and ideal for hanging baskets.",
        "image_url": "https://images.unsplash.com/photo-1572688484438-313a6e50c333?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Lavender",
        "scientific_name": "Lavandula angustifolia",
        "soil_type": "Sandy",
        "climate": "Warm/Temperate",
        "sunlight": "Full Sun",
        "water_needs": "Low",
        "space_requirement": "Moderate",
        "description": "A fragrant Mediterranean herb bearing purple flower spikes. Requires lean, sharply drained sandy soil and abundant direct sunlight.",
        "image_url": "https://images.unsplash.com/photo-1499002238440-d264edd596ec?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Rosemary",
        "scientific_name": "Salvia rosmarinus",
        "soil_type": "Sandy",
        "climate": "Warm/Dry",
        "sunlight": "Full Sun",
        "water_needs": "Low",
        "space_requirement": "Moderate",
        "description": "A hardy evergreen culinary shrub with needle-like aromatic foliage. Highly drought tolerant once established in porous sandy ground.",
        "image_url": "https://images.unsplash.com/photo-1515586000433-45406d8e6662?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Basil",
        "scientific_name": "Ocimum basilicum",
        "soil_type": "Loamy",
        "climate": "Warm/Temperate",
        "sunlight": "Full Sun",
        "water_needs": "Medium",
        "space_requirement": "Compact",
        "description": "Popular culinary herb with lush, fragrant green leaves. Thrives in warm temperate sunshine and fertile, moisture-retentive loamy soil.",
        "image_url": "https://images.unsplash.com/photo-1618375569909-38f75acb0ffc?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Mint",
        "scientific_name": "Mentha spicata",
        "soil_type": "Loamy",
        "climate": "Warm/Temperate",
        "sunlight": "Partial Shade",
        "water_needs": "High",
        "space_requirement": "Moderate",
        "description": "Vigorous perennial herb with refreshing aromatic leaves. Prefers rich, moist loamy ground and flourishes in partial sun or dappled light.",
        "image_url": "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Boston Fern",
        "scientific_name": "Nephrolepis exaltata",
        "soil_type": "Peaty",
        "climate": "Humid/Tropical",
        "sunlight": "Partial Shade",
        "water_needs": "High",
        "space_requirement": "Medium",
        "description": "Lush cascading fronds that demand high humidity and consistent moisture. Thrives in organic, peaty soil out of direct scorching sunlight.",
        "image_url": "https://images.unsplash.com/photo-1592150621744-aca64f48394a?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Prickly Pear Cactus",
        "scientific_name": "Opuntia ficus-indica",
        "soil_type": "Sandy",
        "climate": "Warm/Dry",
        "sunlight": "Full Sun",
        "water_needs": "Low",
        "space_requirement": "Minimal",
        "description": "Desert-adapted succulent with flat fleshy pads and vivid blooms. Exceptional drought tolerance, suited for gravelly or sandy substrates.",
        "image_url": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Areca Palm",
        "scientific_name": "Dypsis lutescens",
        "soil_type": "Loamy",
        "climate": "Humid/Tropical",
        "sunlight": "Partial Shade",
        "water_needs": "Medium",
        "space_requirement": "Large",
        "description": "Feathery clustering palm known for graceful golden-green fronds. Natural air humidifier that excels in bright, humid indoor or sheltered tropical spaces.",
        "image_url": "https://images.unsplash.com/photo-1545241047-6083a3684587?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Rubber Plant",
        "scientific_name": "Ficus elastica",
        "soil_type": "Loamy",
        "climate": "Warm/Tropical",
        "sunlight": "Bright Indirect",
        "water_needs": "Medium",
        "space_requirement": "Medium",
        "description": "Bold indoor tree characterized by large glossy leathery leaves. Thrives in well-drained loamy compost with generous bright filtered light.",
        "image_url": "https://images.unsplash.com/photo-1602923668104-8f9e03e77e62?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "ZZ Plant",
        "scientific_name": "Zamioculcas zamiifolia",
        "soil_type": "Well-drained",
        "climate": "Any/Indoor",
        "sunlight": "Low Light",
        "water_needs": "Low",
        "space_requirement": "Compact",
        "description": "Virtually indestructible houseplant with glossy compound leaflets. Stores water in tuberous rhizomes and tolerates heavy shade and dry indoor air.",
        "image_url": "https://images.unsplash.com/photo-1632207691143-643e2a9a9361?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Chrysanthemum",
        "scientific_name": "Chrysanthemum morifolium",
        "soil_type": "Loamy",
        "climate": "Warm/Temperate",
        "sunlight": "Full Sun",
        "water_needs": "Medium",
        "space_requirement": "Moderate",
        "description": "Vibrant autumn-blooming floral perennial. Needs rich, moist loamy ground and direct sunlight to produce prolific decorative blossom heads.",
        "image_url": "https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Hibiscus",
        "scientific_name": "Hibiscus rosa-sinensis",
        "soil_type": "Loamy",
        "climate": "Warm/Tropical",
        "sunlight": "Full Sun",
        "water_needs": "High",
        "space_requirement": "Large",
        "description": "Tropical shrub admired for its showy, trumpet-shaped blossoms. Demands abundant sunshine, warm weather, and regular deep watering.",
        "image_url": "https://images.unsplash.com/photo-1592806088932-05058af0ad8d?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Jasmine",
        "scientific_name": "Jasminum officinale",
        "soil_type": "Well-drained",
        "climate": "Warm/Temperate",
        "sunlight": "Full Sun",
        "water_needs": "Medium",
        "space_requirement": "Climbing / Hanging",
        "description": "Fragrant climbing vine adorned with delicate star-like white blossoms. Excellent along trellises and pergolas in sunny, well-aerated soil.",
        "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4f44baee?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "English Ivy",
        "scientific_name": "Hedera helix",
        "soil_type": "Loamy",
        "climate": "Cold/Temperate",
        "sunlight": "Partial Shade",
        "water_needs": "Medium",
        "space_requirement": "Climbing / Hanging",
        "description": "Classic evergreen climber that thrives in cooler temperate climates. Adapts to varied soils and provides superb trailing wall or trellis coverage.",
        "image_url": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Sunflower",
        "scientific_name": "Helianthus annuus",
        "soil_type": "Loamy",
        "climate": "Warm/Temperate",
        "sunlight": "Full Sun",
        "water_needs": "Medium",
        "space_requirement": "Large",
        "description": "Towering annual famous for its massive cheerful yellow flower heads. Needs deep fertile loamy soil and uninterrupted full sunshine.",
        "image_url": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "soil_type": "Loamy",
        "climate": "Warm/Temperate",
        "sunlight": "Full Sun",
        "water_needs": "High",
        "space_requirement": "Medium",
        "description": "Warm-season garden favorite producing juicy edible fruits. Requires nutrient-rich, well-draining loamy soil and daily direct sunlight.",
        "image_url": "https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Chili Pepper",
        "scientific_name": "Capsicum annuum",
        "soil_type": "Well-drained",
        "climate": "Warm/Tropical",
        "sunlight": "Full Sun",
        "water_needs": "Medium",
        "space_requirement": "Moderate",
        "description": "Productive warm-climate nightshade bearing spicy pods. Relishes warmth, plenty of sunshine, and fertile, well-draining garden soil.",
        "image_url": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Bougainvillea",
        "scientific_name": "Bougainvillea spectabilis",
        "soil_type": "Sandy",
        "climate": "Warm/Dry",
        "sunlight": "Full Sun",
        "water_needs": "Low",
        "space_requirement": "Expansive",
        "description": "Sprawling drought-hardy ornamental vine renowned for cascading neon-colored flower bracts. Revels in dry, sunny conditions and sandy loam.",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Moth Orchid",
        "scientific_name": "Phalaenopsis amabilis",
        "soil_type": "Well-drained",
        "climate": "Humid/Tropical",
        "sunlight": "Bright Indirect",
        "water_needs": "Medium",
        "space_requirement": "Minimal",
        "description": "Epiphytic orchid with long-lasting elegant blooms. Best potted in loose bark or well-drained media under warm, humid, indirect lighting.",
        "image_url": "https://images.unsplash.com/photo-1566907225472-514dc5789a0c?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Fiddle Leaf Fig",
        "scientific_name": "Ficus lyrata",
        "soil_type": "Loamy",
        "climate": "Warm/Tropical",
        "sunlight": "Bright Indirect",
        "water_needs": "Medium",
        "space_requirement": "Large",
        "description": "Dramatic statement houseplant with broad, violin-shaped waxy foliage. Enjoys consistent moisture and generous indirect sunshine.",
        "image_url": "https://images.unsplash.com/photo-1545241047-6083a3684587?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Croton",
        "scientific_name": "Codiaeum variegatum",
        "soil_type": "Loamy",
        "climate": "Humid/Tropical",
        "sunlight": "Bright Indirect",
        "water_needs": "Medium",
        "space_requirement": "Moderate",
        "description": "Vivid tropical shrub featuring kaleidoscope foliage patterned in red, yellow, and green. Needs high humidity and steady bright illumination.",
        "image_url": "https://images.unsplash.com/photo-1602923668104-8f9e03e77e62?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Anthurium",
        "scientific_name": "Anthurium andraeanum",
        "soil_type": "Peaty",
        "climate": "Humid/Tropical",
        "sunlight": "Bright Indirect",
        "water_needs": "Medium",
        "space_requirement": "Compact",
        "description": "Exotic flamingo flower noted for glossy heart-shaped red spathes with yellow spadices. Flourishes in loose, moist, peaty soil.",
        "image_url": "https://images.unsplash.com/photo-1616690002498-e67cdc024983?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Boston Ivy",
        "scientific_name": "Parthenocissus tricuspidata",
        "soil_type": "Clay",
        "climate": "Cold/Temperate",
        "sunlight": "Partial Shade",
        "water_needs": "Medium",
        "space_requirement": "Expansive",
        "description": "Vigorous deciduous woody vine that clings securely to masonry. Adapts well to heavier clay soils and provides spectacular scarlet autumn color.",
        "image_url": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=600&q=80",
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
