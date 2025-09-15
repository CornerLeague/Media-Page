"""Database setup and initialization script for Corner League Media."""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.database import (
    init_database, check_database_connection, get_database_info,
    reset_database, health_check
)
from app.database.seed_data.load_teams import load_all_teams
from app.database.utils.maintenance import DatabaseMaintenance


def setup_database(reset: bool = False, load_seed_data: bool = True) -> None:
    """Set up the database with tables and initial data."""
    print("🏟️ Corner League Media Database Setup")
    print("=" * 50)

    # Check database connection
    print("1. Checking database connection...")
    if not check_database_connection():
        print("❌ Database connection failed!")
        print("Please check your database configuration in .env file")
        return

    print("✅ Database connection successful!")

    # Get database info
    db_info = get_database_info()
    print(f"   Database: {db_info['database_name']}")
    print(f"   PostgreSQL: {db_info['postgres_version']}")
    print(f"   User: {db_info['current_user']}")
    print(f"   Supabase: {'Yes' if db_info['is_supabase'] else 'No'}")

    # Initialize database
    print("\n2. Setting up database tables...")
    if reset:
        print("⚠️  Resetting database (dropping all tables)...")
        reset_database()
    else:
        init_database()

    print("✅ Database tables created successfully!")

    # Load seed data
    if load_seed_data:
        print("\n3. Loading seed data...")
        try:
            results = load_all_teams(force=reset)
            total_loaded = sum(results.values())

            if total_loaded > 0:
                print(f"✅ Loaded {total_loaded} teams:")
                for sport, count in results.items():
                    if count > 0:
                        print(f"   - {sport.upper()}: {count} teams")
            else:
                print("ℹ️  No new teams loaded (already exist)")

        except Exception as e:
            print(f"⚠️  Error loading seed data: {e}")

    # Run initial maintenance
    print("\n4. Running initial maintenance...")
    try:
        maintenance_results = DatabaseMaintenance.vacuum_analyze()
        success_count = sum(1 for result in maintenance_results.values() if result == "success")
        print(f"✅ VACUUM ANALYZE completed on {success_count} tables")

        DatabaseMaintenance.update_table_statistics()
        print("✅ Table statistics updated")

    except Exception as e:
        print(f"⚠️  Maintenance warning: {e}")

    # Health check
    print("\n5. Running health check...")
    health = health_check()

    if health['status'] == 'healthy':
        print("✅ Database health check passed!")
    elif health['status'] == 'warning':
        print("⚠️  Database health check passed with warnings:")
        for warning in health.get('warnings', []):
            print(f"   - {warning}")
    else:
        print("❌ Database health check failed:")
        for issue in health.get('issues', []):
            print(f"   - {issue}")

    # Final summary
    print("\n" + "=" * 50)
    print("🎉 Database setup completed!")
    print("\nNext steps:")
    print("1. Configure your Supabase environment variables in .env")
    print("2. Set up Row Level Security (RLS) policies in Supabase dashboard")
    print("3. Run the FastAPI backend: python start_backend.py")
    print("4. Configure feed sources for content ingestion")

    # Display table counts
    if 'table_counts' in health:
        print(f"\nCurrent data:")
        for table, count in health['table_counts'].items():
            print(f"   - {table}: {count} records")


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print("Checking prerequisites...")

    # Check environment variables
    required_vars = ['DATABASE_URL']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please configure these in your .env file")
        return False

    # Check database connection
    if not check_database_connection():
        print("❌ Cannot connect to database")
        return False

    print("✅ All prerequisites met")
    return True


def main():
    """Main setup function."""
    import argparse

    parser = argparse.ArgumentParser(description="Database setup for Corner League Media")
    parser.add_argument("--reset", action="store_true", help="Reset database (drop all tables)")
    parser.add_argument("--no-seed", action="store_true", help="Skip loading seed data")
    parser.add_argument("--check-only", action="store_true", help="Only check database health")

    args = parser.parse_args()

    if args.check_only:
        print("Running database health check...")
        health = health_check()
        print(f"Status: {health['status']}")

        if health.get('issues'):
            print("Issues:")
            for issue in health['issues']:
                print(f"  - {issue}")

        if health.get('warnings'):
            print("Warnings:")
            for warning in health['warnings']:
                print(f"  - {warning}")

        if health.get('table_counts'):
            print("Table counts:")
            for table, count in health['table_counts'].items():
                print(f"  - {table}: {count}")

        return

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Run setup
    try:
        setup_database(
            reset=args.reset,
            load_seed_data=not args.no_seed
        )
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()