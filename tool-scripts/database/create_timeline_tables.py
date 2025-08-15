#!/usr/bin/env python3
"""
Database migration script to create timeline events table.
Run this script to add timeline tracking functionality to the database.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.data.models import TimelineEventDB, create_database_engine
from app.logger import logger


def create_timeline_tables():
    """Create timeline events table in the database."""

    try:
        # Create database engine
        database_url = "sqlite:///jobpilot.db"  # Default database location
        engine = create_database_engine(database_url)

        logger.info(f"Connected to database: {database_url}")

        # Create all tables (including new timeline_events table)
        logger.info("Creating timeline events table...")
        TimelineEventDB.metadata.create_all(engine)

        logger.info("✅ Timeline events table created successfully!")

        # Verify table exists
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if "timeline_events" in tables:
            logger.info("📊 Timeline events table verified in database")

            # Show table columns
            columns = inspector.get_columns("timeline_events")
            logger.info("📋 Timeline events table columns:")
            for column in columns:
                logger.info(f"  - {column['name']}: {column['type']}")
        else:
            logger.error("❌ Timeline events table not found after creation")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Error creating timeline tables: {e}")
        return False


if __name__ == "__main__":
    logger.info("🚀 Starting timeline database migration...")

    success = create_timeline_tables()

    if success:
        logger.info("✅ Timeline database migration completed successfully!")
    else:
        logger.error("❌ Timeline database migration failed!")
        sys.exit(1)
