#!/usr/bin/env python3
"""
Test Script for Phase 2 Foundation
Validates extended database models and vector store implementation.
"""

import asyncio
import os
import sys
import tempfile
from uuid import uuid4

import pytest

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))


def test_new_models():
    """Test the new Phase 2 data models."""
    print("🧪 Testing Phase 2 Data Models...")

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
        print(f"   ✅ JobSource model: {job_source.display_name}")

        # Test JobSourceListing
        job_id = uuid4()
        job_source_listing = JobSourceListing(
            job_id=job_id,
            source_id=job_source.id,
            source_job_id="linkedin-12345",
            source_url="https://www.linkedin.com/jobs/view/12345",
            source_metadata={"sponsored": False, "premium": True},
        )
        print(f"   ✅ JobSourceListing model: {job_source_listing.source_job_id}")

        # Test JobEmbedding
        job_embedding = JobEmbedding(
            job_id=job_id,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            content_hash="abc123def456",
            embedding_vector=[0.1, 0.2, 0.3] * 128,  # 384 dimensions
            embedding_dimension=384,
            content_type="job_description",
        )
        print(f"   ✅ JobEmbedding model: {job_embedding.embedding_model}")

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
        print(f"   ✅ JobDeduplication model: confidence {job_dedup.confidence_score}")

        # Test enhanced JobListing
        enhanced_job = JobListing(
            title="Senior Software Engineer",
            company="TechCorp",
            location="San Francisco, CA",
            description="Build amazing software",
            requirements="5+ years Python experience",
            # New enhanced fields
            verification_status=VerificationStatus.ACTIVE,
            company_size_category=CompanySizeCategory.LARGE,
            seniority_level=SeniorityLevel.MANAGER,  # Use MANAGER instead of SENIOR_LEVEL
            tech_stack=["Python", "Django", "React"],
            data_quality_score=0.85,
            source_count=2,
        )
        print(f"   ✅ Enhanced JobListing model: {enhanced_job.title}")

        print("   🎉 All new data models validated successfully!")
        return True

    except Exception as e:
        print(f"   ❌ Data models test failed: {e}")
        return False


def test_database_schema():
    """Test the new database schema with SQLAlchemy models."""
    print("\n🏗️ Testing Database Schema...")

    try:
        from app.data.models import create_database_engine, create_tables

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_url = f"sqlite:///{tmp_db.name}"

        # Create engine and tables
        engine = create_database_engine(db_url)
        create_tables(engine)
        print("   ✅ Database tables created successfully")

        # Check that all new tables exist
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            "job_sources",
            "job_source_listings",
            "job_embeddings",
            "job_duplications",
            "job_listings",
            "user_profiles",
            "applications",
            "saved_jobs",
            "companies",
            "timeline_events",
        ]

        for table in expected_tables:
            if table in tables:
                print(f"   ✅ Table '{table}' exists")
            else:
                print(f"   ❌ Table '{table}' missing")
                return False

        # Test table schema
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

        for column in new_columns:
            if column in job_listings_columns:
                print(f"   ✅ Enhanced column '{column}' exists")
            else:
                print(f"   ❌ Enhanced column '{column}' missing")

        # Cleanup
        os.unlink(tmp_db.name)

        print("   🎉 Database schema validation completed!")
        return True

    except Exception as e:
        print(f"   ❌ Database schema test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_vector_store():
    """Test the vector store implementation."""
    print("\n🔍 Testing Vector Store...")

    try:
        from app.data.models import JobListing
        from app.tool.semantic_search.vector_store import VectorStore

        # Create test vector store (simple backend for testing)
        vector_store = VectorStore(
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            storage_backend="simple",  # Use simple storage for testing
        )
        print("   ✅ Vector store initialized")

        # Create test job listings
        test_jobs = [
            JobListing(
                title="Senior Python Developer",
                company="DataTech Inc",
                description="Build scalable data processing systems using Python and Django",
                requirements="5+ years Python, Django, PostgreSQL",
                skills_required=["Python", "Django", "PostgreSQL"],
                tech_stack=["Python", "Django", "PostgreSQL", "Docker"],
            ),
            JobListing(
                title="Frontend React Developer",
                company="WebCorp",
                description="Create beautiful user interfaces with React and TypeScript",
                requirements="3+ years React, TypeScript, CSS",
                skills_required=["React", "TypeScript", "JavaScript", "CSS"],
                tech_stack=["React", "TypeScript", "Node.js", "Webpack"],
            ),
            JobListing(
                title="Full Stack Engineer",
                company="StartupXYZ",
                description="Work on both frontend and backend with Python and React",
                requirements="Versatile engineer with Python and React experience",
                skills_required=["Python", "React", "JavaScript", "API Design"],
                tech_stack=["Python", "React", "FastAPI", "PostgreSQL"],
            ),
        ]

        print("   📝 Created test job listings")

        # Store embeddings
        embeddings = await vector_store.batch_store_embeddings(test_jobs)
        print(f"   ✅ Stored {len(embeddings)} job embeddings")

        # Test similarity search
        search_queries = [
            "Python backend developer",
            "React frontend engineer",
            "Full stack developer with Python and React",
        ]

        for query in search_queries:
            matches = await vector_store.find_similar_jobs(query, limit=3)
            print(f"   🔍 Query '{query}': {len(matches)} matches found")

            if matches:
                best_match = matches[0]
                print(f"      Top match: {best_match.overall_score:.3f} similarity")

        # Test hybrid search
        hybrid_matches = await vector_store.hybrid_search(
            "Python developer with database experience", limit=2
        )
        print(f"   🔗 Hybrid search: {len(hybrid_matches)} matches")

        # Test stats and health check
        stats = await vector_store.get_embedding_stats()
        print(f"   📊 Vector store stats: {stats['total_embeddings']} embeddings")

        health = await vector_store.health_check()
        print(f"   💚 Health check: {health['status']}")

        print("   🎉 Vector store validation completed!")
        return True

    except Exception as e:
        print(f"   ❌ Vector store test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_integration():
    """Test integration between database and vector store."""
    print("\n🔗 Testing Database-VectorStore Integration...")

    try:
        from app.data.database import get_database_manager
        from app.data.models import JobListing
        from app.tool.semantic_search.vector_store import create_vector_store

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_url = f"sqlite:///{tmp_db.name}"

        # Initialize database manager
        db_manager = get_database_manager(db_url)
        print("   ✅ Database manager initialized")

        # Create vector store with database integration
        vector_store = create_vector_store(
            storage_backend="simple", db_manager=db_manager
        )
        print("   ✅ Vector store with database integration initialized")

        # Create and store test job
        test_job = JobListing(
            title="Machine Learning Engineer",
            company="AI Innovations",
            description="Build ML models using Python, TensorFlow, and PyTorch",
            requirements="PhD in CS or 5+ years ML experience",
            skills_required=["Python", "TensorFlow", "PyTorch", "ML"],
            tech_stack=["Python", "TensorFlow", "PyTorch", "Jupyter"],
            verification_status="active",
            data_quality_score=0.9,
        )

        # Store job in database
        db_manager.create_job(test_job)
        print("   ✅ Job stored in database")

        # Create embedding (this should also store in database)
        await vector_store.store_job_embedding(test_job)
        print("   ✅ Embedding created and stored")

        # Test search
        matches = await vector_store.find_similar_jobs(
            "machine learning python", limit=1
        )
        if matches:
            print(f"   🎯 Search successful: {matches[0].overall_score:.3f} similarity")
        else:
            print("   ❌ No search matches found")
            return False

        # Cleanup
        os.unlink(tmp_db.name)

        print("   🎉 Integration test completed!")
        return True

    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all Phase 2 foundation tests."""
    print("🚀 JobPilot Phase 2 Foundation Test Suite")
    print("=" * 50)

    test_results = []

    # Test 1: New Data Models
    test_results.append(test_new_models())

    # Test 2: Database Schema
    test_results.append(test_database_schema())

    # Test 3: Vector Store
    test_results.append(await test_vector_store())

    # Test 4: Integration
    test_results.append(await test_integration())

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")

    test_names = [
        "Phase 2 Data Models",
        "Database Schema",
        "Vector Store",
        "Database-Vector Integration",
    ]

    passed_tests = 0
    for i, (test_name, result) in enumerate(
        zip(test_names, test_results, strict=False)
    ):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed_tests += 1

    print(f"\n🎯 Results: {passed_tests}/{len(test_results)} tests passed")

    if all(test_results):
        print("🎉 All Phase 2 foundation tests passed! Ready for Week 2.")
        return True
    else:
        print("🔧 Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    # Install required packages if not available
    try:
        pass
    except ImportError:
        print("📦 Installing required packages...")
        os.system("pip install sentence-transformers scikit-learn")

    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
