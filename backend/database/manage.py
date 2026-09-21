"""Unified Database Management CLI.

Provides command-line actions to initialize tables, run Alembic migrations,
seed initial data, inspect status and record counts, and reset the schema.
"""

import sys
import argparse
import logging
from sqlalchemy import text
from backend.database.connection import get_engine, get_session_factory, Base, check_db_connection
from backend.database.models import User, Plant, Recommendation, SearchHistory
from backend.database.seed import seed_database
from backend.config import get_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def command_init(args):
    """Initialize database tables directly via SQLAlchemy DDL."""
    print("Connecting to database and creating tables...")
    try:
        engine = get_engine()
        # Ensure all models are registered on Base
        import backend.database.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: All database tables created successfully.")
    except Exception as e:
        print(f"FAILED: Could not initialize database tables: {e}", file=sys.stderr)
        sys.exit(1)


def command_migrate(args):
    """Run Alembic migrations to upgrade to head."""
    print("Running Alembic migrations (upgrade head)...")
    try:
        from alembic.config import Config
        from alembic import command
        from pathlib import Path

        project_root = Path(__file__).resolve().parent.parent.parent
        alembic_ini_path = project_root / "alembic.ini"
        
        if not alembic_ini_path.exists():
            print(f"Error: alembic.ini not found at {alembic_ini_path}", file=sys.stderr)
            sys.exit(1)

        alembic_cfg = Config(str(alembic_ini_path))
        command.upgrade(alembic_cfg, "head")
        print("SUCCESS: Database migrated to latest revision (head).")
    except Exception as e:
        print(f"FAILED: Migration error: {e}", file=sys.stderr)
        sys.exit(1)


def command_seed(args):
    """Seed sample plants and demonstration data into the database."""
    print("Seeding database with sample plants and demo records...")
    try:
        command_init(args)  # Ensure tables exist first
        stats = seed_database()
        print("SUCCESS: Seeding completed.")
        for key, val in stats.items():
            print(f"  - {key}: {val}")
    except Exception as e:
        print(f"FAILED: Seeding failed: {e}", file=sys.stderr)
        sys.exit(1)


def command_status(args):
    """Inspect database connection and display record counts."""
    config = get_config()
    print("Database Configuration Status:")
    # Mask password in URL for display
    url = config.DATABASE_URL
    if "@" in url and "://" in url:
        prefix, rest = url.split("://", 1)
        user_pass, host_db = rest.split("@", 1)
        user = user_pass.split(":")[0]
        masked_url = f"{prefix}://{user}:****@{host_db}"
    else:
        masked_url = url
    print(f"  Target URL: {masked_url}")

    conn_check = check_db_connection()
    print(f"  Connected:  {conn_check['connected']}")
    print(f"  Message:    {conn_check['message']}")

    if not conn_check["connected"]:
        sys.exit(1)

    try:
        session_factory = get_session_factory()
        session = session_factory()
        try:
            users_count = session.query(User).count()
            plants_count = session.query(Plant).count()
            search_count = session.query(SearchHistory).count()
            recs_count = session.query(Recommendation).count()

            print("\nTable Record Summary:")
            print(f"  Users:           {users_count}")
            print(f"  Plants:          {plants_count}")
            print(f"  Search History:  {search_count}")
            print(f"  Recommendations: {recs_count}")

            if plants_count > 0:
                print("\nSample Plants in Catalog:")
                for plant in session.query(Plant).limit(10).all():
                    print(
                        f"  [ID: {plant.plant_id}] {plant.name} "
                        f"({plant.scientific_name or 'N/A'}) - "
                        f"Soil: {plant.soil_type}, Sunlight: {plant.sunlight}, Water: {plant.water_needs}"
                    )
        finally:
            session.close()
    except Exception as e:
        print(f"Error querying table statistics: {e}", file=sys.stderr)
        sys.exit(1)


def command_reset(args):
    """Drop and recreate all database tables."""
    if not args.yes:
        confirm = input("Are you sure you want to DROP and recreate all database tables? (y/N): ")
        if confirm.lower() != "y":
            print("Operation aborted.")
            return

    print("Dropping all tables...")
    try:
        engine = get_engine()
        import backend.database.models  # noqa: F401
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped.")
        print("Recreating tables...")
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: Tables recreated.")
        if args.seed:
            print("Seeding new tables...")
            seed_database()
            print("SUCCESS: Tables seeded.")
    except Exception as e:
        print(f"FAILED: Reset operation error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Plant Recommendation Database Management Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    parser_init = subparsers.add_parser("init", help="Create database tables directly")
    parser_init.set_defaults(func=command_init)

    # migrate
    parser_migrate = subparsers.add_parser("migrate", help="Run Alembic migrations")
    parser_migrate.set_defaults(func=command_migrate)

    # seed
    parser_seed = subparsers.add_parser("seed", help="Seed database with sample plants & users")
    parser_seed.set_defaults(func=command_seed)

    # status
    parser_status = subparsers.add_parser("status", help="Inspect database status & record counts")
    parser_status.set_defaults(func=command_status)

    # reset
    parser_reset = subparsers.add_parser("reset", help="Drop and recreate database tables")
    parser_reset.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    parser_reset.add_argument("--seed", action="store_true", help="Seed data immediately after recreation")
    parser_reset.set_defaults(func=command_reset)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
