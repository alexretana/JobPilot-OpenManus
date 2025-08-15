#!/usr/bin/env python3
"""
Simplified Test Script for Phase 2 Models
Tests the new data models and database schema without vector store dependencies.
"""

import os
import sys
import tempfile
from uuid import uuid4


# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))


def test_new_pydantic_models():
    """Test the new Phase 2 Pydantic models."""
    print("🧪 Testing Phase 2 Pydantic Models...")

    try:
        from app.data.models import (
            CompanySizeCategory,
            JobDeduplication,
            JobEmbedding,
            JobListing,
            JobSource,
            JobSourceListing,
            SeniorityLevel,
            VerificationStatus,
        )

        # Test JobSource
        job_source = JobSource(
            name="linkedin",
            display_name="LinkedIn Jobs",
            base_url="https://www.linkedin.com/jobs",
            api_available=False,
            rate_limit_config={"requests_per_minute": 30},
            is_active=True,
        )
        print(f"   ✅ JobSource: {job_source.display_name}")
        assert job_source.name == "linkedin"

        # Test JobSourceListing
        job_id = uuid4()
        job_source_listing = JobSourceListing(
            job_id=job_id,
            source_id=job_source.id,
            source_job_id="linkedin-12345",
            source_url="https://www.linkedin.com/jobs/view/12345",
            source_metadata={"sponsored": False, "premium": True},
        )
        print(f"   ✅ JobSourceListing: {job_source_listing.source_job_id}")
        assert job_source_listing.source_metadata["premium"] == True

        # Test JobEmbedding
        job_embedding = JobEmbedding(
            job_id=job_id,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            content_hash="abc123def456",
            embedding_vector=[0.1, 0.2, 0.3] * 128,  # 384 dimensions
            embedding_dimension=384,
            content_type="job_description",
        )
        print(f"   ✅ JobEmbedding: {len(job_embedding.embedding_vector)} dimensions")
        assert len(job_embedding.embedding_vector) == 384

        # Test JobDeduplication
        canonical_job_id = uuid4()
        duplicate_job_id = uuid4()
        job_dedup = JobDeduplication(
            canonical_job_id=canonical_job_id,
            duplicate_job_id=duplicate_job_id,
            confidence_score=0.95,
            matching_fields=["title", "company", "location"],
            merge_strategy="keep_canonical",
            reviewed=False,
        )
        print(f"   ✅ JobDeduplication: {job_dedup.confidence_score} confidence")
        assert job_dedup.confidence_score == 0.95

        # Test enhanced JobListing with new enums
        enhanced_job = JobListing(
            title="Senior Software Engineer",
            company="TechCorp",
            location="San Francisco, CA",
            description="Build amazing software",
            requirements="5+ years Python experience",
            # Test new enhanced fields
            verification_status=VerificationStatus.ACTIVE,
            company_size_category=CompanySizeCategory.LARGE,
            seniority_level=SeniorityLevel.MANAGER,
            tech_stack=["Python", "Django", "React"],
            data_quality_score=0.85,
            source_count=2,
        )
        print(f"   ✅ Enhanced JobListing: {enhanced_job.title}")
        assert enhanced_job.verification_status == VerificationStatus.ACTIVE
        assert enhanced_job.company_size_category == CompanySizeCategory.LARGE
        assert enhanced_job.data_quality_score == 0.85

        # Test enum values
        print(f"   ✅ VerificationStatus: {len(VerificationStatus)} values")
        print(f"   ✅ CompanySizeCategory: {len(CompanySizeCategory)} values")
        print(f"   ✅ SeniorityLevel: {len(SeniorityLevel)} values")

        print("   🎉 All Pydantic models validated successfully!")
        return True

    except Exception as e:
        print(f"   ❌ Pydantic models test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_sqlalchemy_models():
    """Test the new SQLAlchemy database models."""
    print("\n🏗️ Testing SQLAlchemy Database Models...")

    try:
        from app.data.models import create_database_engine, create_tables

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_url = f"sqlite:///{tmp_db.name}"

        print(f"   📂 Using temp database: {tmp_db.name}")

        # Create engine and tables
        engine = create_database_engine(db_url)
        create_tables(engine)
        print("   ✅ Database tables created successfully")

        # Check that all tables exist
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_new_tables = [
            "job_sources",
            "job_source_listings",
            "job_embeddings",
            "job_duplications",
        ]

        existing_tables = [
            "job_listings",
            "user_profiles",
            "applications",
            "saved_jobs",
            "companies",
            "timeline_events",
        ]

        all_expected = expected_new_tables + existing_tables

        for table in all_expected:
            if table in tables:
                print(f"   ✅ Table '{table}' exists")
            else:
                print(f"   ❌ Table '{table}' missing")
                return False

        # Test enhanced job_listings table schema
        job_listings_columns = [
            col["name"] for col in inspector.get_columns("job_listings")
        ]
        new_columns = [
            "canonical_id",
            "source_count",
            "data_quality_score",
            "scraped_at",
            "last_verified",
            "verification_status",
            "company_size_category",
            "seniority_level",
            "tech_stack",
            "benefits_parsed",
        ]

        print("   📋 Checking enhanced job_listings columns:")
        for column in new_columns:
            if column in job_listings_columns:
                print(f"      ✅ Column '{column}' exists")
            else:
                print(f"      ❌ Column '{column}' missing")
                return False

        # Test foreign key relationships
        foreign_keys = inspector.get_foreign_keys("job_source_listings")
        print(f"   🔗 job_source_listings has {len(foreign_keys)} foreign keys")

        foreign_keys = inspector.get_foreign_keys("job_embeddings")
        print(f"   🔗 job_embeddings has {len(foreign_keys)} foreign keys")

        foreign_keys = inspector.get_foreign_keys("job_duplications")
        print(f"   🔗 job_duplications has {len(foreign_keys)} foreign keys")

        # Close engine connection
        engine.dispose()

        # Cleanup
        try:
            os.unlink(tmp_db.name)
            print("   🧹 Temporary database cleaned up")
        except:
            print("   ⚠️ Could not clean up temporary database (file may be in use)")

        print("   🎉 Database schema validation completed!")
        return True

    except Exception as e:
        print(f"   ❌ Database models test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_model_conversions():
    """Test conversion between Pydantic and SQLAlchemy models."""
    print("\n🔄 Testing Model Conversions...")

    try:
        from app.data.models import (
            JobSource,
            JobSourceDB,
            pydantic_to_sqlalchemy,
            sqlalchemy_to_pydantic,
        )

        # Create Pydantic model
        pydantic_source = JobSource(
            name="indeed",
            display_name="Indeed Jobs",
            base_url="https://indeed.com",
            api_available=True,
            rate_limit_config={"requests_per_minute": 60},
            is_active=True,
        )
        print(f"   ✅ Created Pydantic JobSource: {pydantic_source.name}")

        # Convert to SQLAlchemy
        sqlalchemy_source = pydantic_to_sqlalchemy(pydantic_source, JobSourceDB)
        print(f"   ✅ Converted to SQLAlchemy: {sqlalchemy_source.display_name}")

        # Convert back to Pydantic
        converted_back = sqlalchemy_to_pydantic(sqlalchemy_source, JobSource)
        print(f"   ✅ Converted back to Pydantic: {converted_back.name}")

        # Verify data integrity
        assert pydantic_source.name == converted_back.name
        assert pydantic_source.display_name == converted_back.display_name
        assert pydantic_source.api_available == converted_back.api_available

        print("   🎉 Model conversion validation completed!")
        return True

    except Exception as e:
        print(f"   ❌ Model conversion test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_enum_functionality():
    """Test the new enum classes."""
    print("\n🏷️ Testing Enum Functionality...")

    try:
        from app.data.models import (
            CompanySizeCategory,
            SeniorityLevel,
            VerificationStatus,
        )

        # Test VerificationStatus
        statuses = [
            VerificationStatus.UNVERIFIED,
            VerificationStatus.ACTIVE,
            VerificationStatus.EXPIRED,
            VerificationStatus.INVALID,
            VerificationStatus.REMOVED,
        ]
        print(
            f"   ✅ VerificationStatus has {len(statuses)} values: {[s.value for s in statuses]}"
        )

        # Test CompanySizeCategory
        sizes = [
            CompanySizeCategory.STARTUP,
            CompanySizeCategory.SMALL,
            CompanySizeCategory.MEDIUM,
            CompanySizeCategory.LARGE,
            CompanySizeCategory.ENTERPRISE,
        ]
        print(
            f"   ✅ CompanySizeCategory has {len(sizes)} values: {[s.value for s in sizes]}"
        )

        # Test SeniorityLevel
        levels = [
            SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
            SeniorityLevel.TEAM_LEAD,
            SeniorityLevel.MANAGER,
            SeniorityLevel.DIRECTOR,
            SeniorityLevel.VP,
            SeniorityLevel.C_LEVEL,
        ]
        print(
            f"   ✅ SeniorityLevel has {len(levels)} values: {[s.value for s in levels]}"
        )

        # Test enum usage in models
        from app.data.models import JobListing

        job = JobListing(
            title="Test Job",
            company="Test Company",
            verification_status=VerificationStatus.ACTIVE,
            company_size_category=CompanySizeCategory.STARTUP,
            seniority_level=SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
        )

        assert job.verification_status == VerificationStatus.ACTIVE
        assert job.company_size_category == CompanySizeCategory.STARTUP
        assert job.seniority_level == SeniorityLevel.INDIVIDUAL_CONTRIBUTOR

        print("   🎉 Enum functionality validation completed!")
        return True

    except Exception as e:
        print(f"   ❌ Enum functionality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all Phase 2 model tests."""
    print("🚀 JobPilot Phase 2 Models Test Suite")
    print("=" * 50)

    test_results = []

    # Test 1: Pydantic Models
    test_results.append(test_new_pydantic_models())

    # Test 2: SQLAlchemy Models
    test_results.append(test_sqlalchemy_models())

    # Test 3: Model Conversions
    test_results.append(test_model_conversions())

    # Test 4: Enum Functionality
    test_results.append(test_enum_functionality())

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")

    test_names = [
        "Phase 2 Pydantic Models",
        "SQLAlchemy Database Models",
        "Model Conversions",
        "Enum Functionality",
    ]

    passed_tests = 0
    for test_name, result in zip(test_names, test_results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed_tests += 1

    print(f"\n🎯 Results: {passed_tests}/{len(test_results)} tests passed")

    if all(test_results):
        print("🎉 All Phase 2 model tests passed! Data models are ready.")
        return True
    else:
        print("🔧 Some tests failed. Please check the model implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
