#!/usr/bin/env python3
"""
Database Migration Script
Upgrades existing JobPilot database to include Phase 2 enhanced columns.
"""

import os
import sqlite3


def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)


def migrate_database():
    """Migrate the database to add new Phase 2 columns."""
    db_path = "data/jobpilot.db"

    if not os.path.exists(db_path):
        print(
            "❌ Database not found. Run the application first to create the database."
        )
        return False

    print("🔄 Starting database migration...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # List of new columns to add to job_listings table
        new_columns = [
            ("canonical_id", "VARCHAR", None),
            ("source_count", "INTEGER", "1"),
            ("data_quality_score", "FLOAT", "0.5"),
            ("scraped_at", "DATETIME", None),
            ("last_verified", "DATETIME", None),
            ("verification_status", "VARCHAR(10)", "'ACTIVE'"),
            ("company_size_category", "VARCHAR(8)", "'UNKNOWN'"),
            ("seniority_level", "VARCHAR(12)", "'UNKNOWN'"),
            ("tech_stack", "JSON", "'[]'"),
            ("benefits_parsed", "JSON", "'[]'"),
        ]

        columns_added = 0

        for column_name, column_type, default_value in new_columns:
            if not check_column_exists(cursor, "job_listings", column_name):
                # Add the column
                if default_value:
                    sql = f"ALTER TABLE job_listings ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                else:
                    sql = f"ALTER TABLE job_listings ADD COLUMN {column_name} {column_type}"

                print(f"   Adding column: {column_name}")
                cursor.execute(sql)
                columns_added += 1
            else:
                print(f"   Column {column_name} already exists, skipping")

        # Set default values for existing rows where needed
        if columns_added > 0:
            print("🔄 Setting default values for existing rows...")

            # Update scraped_at to created_at for existing jobs
            cursor.execute(
                """
                UPDATE job_listings
                SET scraped_at = created_at
                WHERE scraped_at IS NULL
            """
            )

            # Update last_verified to created_at for existing jobs
            cursor.execute(
                """
                UPDATE job_listings
                SET last_verified = created_at
                WHERE last_verified IS NULL
            """
            )

            rows_updated = cursor.rowcount
            print(f"   Updated {rows_updated} existing rows with default values")

        conn.commit()
        conn.close()

        print("✅ Migration completed successfully!")
        print(f"   Added {columns_added} new columns")
        print("   Database is now compatible with Phase 2 enhanced features")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def verify_migration():
    """Verify the migration was successful."""
    db_path = "data/jobpilot.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check table schema
        cursor.execute("PRAGMA table_info(job_listings)")
        columns = cursor.fetchall()

        print("\\n📋 Current job_listings table schema:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")

        # Count total columns
        print(f"\\n📊 Total columns: {len(columns)}")

        # Check if we have data
        cursor.execute("SELECT COUNT(*) FROM job_listings")
        job_count = cursor.fetchone()[0]
        print(f"📊 Total jobs in database: {job_count}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 JobPilot Database Migration Tool")
    print("=" * 50)

    # Run migration
    success = migrate_database()

    if success:
        # Verify migration
        print("\\n🔍 Verifying migration...")
        verify_migration()

        print("\\n🎉 Migration completed successfully!")
        print("\\n📝 Next steps:")
        print("   1. Restart your backend server")
        print("   2. The frontend should now display jobs correctly")
        print(
            "   3. You can run the ETL system to collect new jobs with enhanced features"
        )
    else:
        print("\\n❌ Migration failed. Please check the error messages above.")
