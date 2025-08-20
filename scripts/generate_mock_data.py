#!/usr/bin/env python3
"""
Generate Mock Data Script
Standalone script to populate the database with comprehensive mock data for development/testing.

Usage:
1. Start the web server to create database tables
2. Stop the web server
3. Run this script to populate with mock data
4. Restart the web server for testing

Example:
    python scripts/generate_mock_data.py
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.data.database import DatabaseManager
from app.data.mock_data_generator import MockDataGenerator


async def main():
    """Generate mock data for the database."""
    print("🎭 JobPilot Mock Data Generator")
    print("=" * 40)

    try:
        # Check if database directory exists
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        db_file = data_dir / "jobpilot.db"

        if not db_file.exists():
            print("💡 Database file not found - will create it automatically")
            print(f"   Database location: {db_file}")
        else:
            print(f"✅ Found existing database at: {db_file}")

        # Initialize database manager
        print("\n📊 Connecting to database...")
        db_manager = DatabaseManager()

        # Check database health
        if not db_manager.health_check():
            print("❌ Database health check failed!")
            return

        # Get current table stats
        print("\n📈 Current database state:")
        stats = db_manager.get_table_stats()
        for table, count in stats.items():
            print(f"   {table}: {count} records")

        # Ask for confirmation if data exists
        total_records = sum(count for count in stats.values() if isinstance(count, int))
        if total_records > 0:
            print(f"\n⚠️  Database contains {total_records} existing records.")
            confirm = input("Continue and add mock data? (y/N): ").strip().lower()
            if confirm not in ["y", "yes"]:
                print("❌ Operation cancelled.")
                return

        # Create mock data generator
        print("\n🎭 Initializing mock data generator...")
        mock_generator = MockDataGenerator(db_manager)

        # Generate mock data
        print("\n🚀 Generating comprehensive mock data...")
        print("   This will create:")
        print("   - 3 sample users with different roles")
        print("   - Complete skill banks with skills, experiences, education")
        print("   - Projects, certifications, and summary variations")

        result = await mock_generator.initialize_database_with_mock_data()

        # Display results
        print("\n" + "=" * 40)
        print("📋 MOCK DATA GENERATION RESULTS")
        print("=" * 40)

        summary = result["summary"]
        print(f"✅ Successfully created {summary['total_users_created']} users")
        print(
            f"✅ Successfully created {summary['total_skill_banks_created']} skill banks"
        )
        print(f"📊 Success rate: {summary['success_rate']:.1%}")

        if summary["total_errors"] > 0:
            print(f"⚠️  Encountered {summary['total_errors']} errors:")
            for error in result["errors"]:
                print(f"   - {error['error']}")

        # Display created users
        print("\n👤 Created Users:")
        for user in result["created_users"]:
            print(
                f"   - {user['name']} ({user['role']}) - ID: {user['user_id'][:8]}..."
            )

        # Display skill bank details
        print("\n🏦 Skill Bank Summary:")
        for sb in result["created_skill_banks"]:
            print(
                f"   - User {sb['user_id'][:8]}...: "
                f"{sb['skills_count']} skills, "
                f"{sb['experiences_count']} experiences, "
                f"{sb['projects_count']} projects, "
                f"{sb['certifications_count']} certifications"
            )

        # Show updated database stats
        print("\n📈 Updated database state:")
        updated_stats = db_manager.get_table_stats()
        for table, count in updated_stats.items():
            old_count = stats.get(table, 0)
            if isinstance(count, int) and isinstance(old_count, int):
                change = count - old_count
                change_str = f" (+{change})" if change > 0 else ""
                print(f"   {table}: {count} records{change_str}")

        print("\n🎉 Mock data generation completed!")
        print(f"   📅 Generated at: {result['timestamp']}")
        print("\n💡 Next steps:")
        print("   1. Start the web server: python web_server.py")
        print("   2. Navigate to http://localhost:8080")
        print("   3. Test the Skill Bank and Resume Builder features")

    except Exception as e:
        print("\n❌ ERROR: Failed to generate mock data")
        print(f"   Details: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check for help flag
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    # Run the mock data generation
    asyncio.run(main())
