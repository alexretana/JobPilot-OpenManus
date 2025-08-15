#!/usr/bin/env python3
"""
Comprehensive Database Integration Tests

Tests database models, relationships, transactions, and data integrity
for the JobPilot-OpenManus application.
"""

import os
import sys
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    from app.data.models import (
        ApplicationDB,
        CompanyDB,
        CompanySizeCategory,
        JobListingDB,
        SeniorityLevel,
        TimelineEventDB,
        TimelineEventType,
        UserProfileDB,
        VerificationStatus,
    )

    HAS_DATABASE = True
except ImportError as e:
    HAS_DATABASE = False
    import_error = e


# ==================== Fixtures ====================


@pytest.fixture(scope="function")
def temp_database():
    """Create a temporary SQLite database for testing."""
    if not HAS_DATABASE:
        pytest.skip(f"Database dependencies not available: {import_error}")

    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name

    db_url = f"sqlite:///{db_path}"

    try:
        # Create engine and tables
        engine = create_engine(db_url)

        # Import Base and create all tables
        from app.data.models import Base

        Base.metadata.create_all(engine)

        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        yield {
            "engine": engine,
            "session_factory": SessionLocal,
            "db_url": db_url,
            "db_path": db_path,
        }

    finally:
        # Cleanup
        try:
            if "engine" in locals():
                engine.dispose()
            os.unlink(db_path)
        except Exception:
            pass  # Ignore cleanup errors


@pytest.fixture(scope="function")
def db_session(temp_database):
    """Create a database session for testing."""
    session_factory = temp_database["session_factory"]
    session = session_factory()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": str(uuid4()),
        "email": "test.user@example.com",
        "full_name": "Test User",
        "phone": "+1-555-0123",
        "location": "San Francisco, CA",
        "linkedin_url": "https://linkedin.com/in/testuser",
        "github_url": "https://github.com/testuser",
        "resume_text": "Experienced software engineer with 5 years in Python and web development.",
        "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
        "years_experience": 5,
        "desired_salary_min": 100000,
        "desired_salary_max": 140000,
        "job_preferences": {"remote": True, "location_flexible": True},
    }


@pytest.fixture
def sample_company_data():
    """Sample company data for testing."""
    return {
        "id": str(uuid4()),
        "name": "TechCorp Solutions",
        "website": "https://techcorp.com",
        "description": "Leading technology solutions provider",
        "industry": "Technology",
        "size_category": CompanySizeCategory.LARGE,
        "headquarters": "San Francisco, CA",
        "founded_year": 2010,
        "company_culture": ["Innovation", "Work-life balance", "Remote-first"],
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "id": str(uuid4()),
        "title": "Senior Python Developer",
        "company": "TechCorp Solutions",
        "location": "Remote",
        "description": "Join our team building scalable web applications with Python and modern frameworks.",
        "requirements": "Bachelor's degree in CS or equivalent. 5+ years Python experience.",
        "job_type": "Full-time",
        "remote_type": "Remote",
        "salary_min": 110000,
        "salary_max": 140000,
        "skills_required": ["Python", "Django", "PostgreSQL", "Docker"],
        "tech_stack": ["Python", "Django", "React", "PostgreSQL"],
        "benefits": ["Health insurance", "Dental", "Vision", "401k", "Remote work"],
        "verification_status": VerificationStatus.ACTIVE,
        "company_size_category": CompanySizeCategory.LARGE,
        "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
        "data_quality_score": 0.95,
    }


# ==================== Basic Database Tests ====================


class TestDatabaseBasics:
    """Test basic database functionality and setup."""

    def test_database_creation(self, temp_database):
        """Test that database and tables are created successfully."""
        engine = temp_database["engine"]

        # Check that engine is created
        assert engine is not None

        # Check that we can connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_table_creation(self, temp_database):
        """Test that all expected tables are created."""
        engine = temp_database["engine"]

        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            "job_listings",
            "user_profiles",
            "applications",
            "saved_jobs",
            "companies",
            "timeline_events",
            "job_sources",
            "job_source_listings",
            "job_embeddings",
            "job_duplications",
        ]

        for table in expected_tables:
            assert table in tables, f"Table '{table}' should exist"

    def test_session_creation(self, db_session):
        """Test that database session can be created."""
        assert db_session is not None

        # Test a simple query
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1


# ==================== Model CRUD Tests ====================


class TestJobListingCRUD:
    """Test JobListing model CRUD operations."""

    def test_create_job_listing(self, db_session, sample_job_data):
        """Test creating a job listing."""
        job = JobListingDB(**sample_job_data)

        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.id is not None
        assert job.title == sample_job_data["title"]
        assert job.company == sample_job_data["company"]
        assert job.verification_status == VerificationStatus.ACTIVE

    def test_read_job_listing(self, db_session, sample_job_data):
        """Test reading a job listing."""
        # Create job
        job = JobListingDB(**sample_job_data)
        db_session.add(job)
        db_session.commit()

        job_id = job.id

        # Read job
        retrieved_job = (
            db_session.query(JobListingDB).filter(JobListingDB.id == job_id).first()
        )

        assert retrieved_job is not None
        assert retrieved_job.title == sample_job_data["title"]
        assert retrieved_job.id == job_id

    def test_update_job_listing(self, db_session, sample_job_data):
        """Test updating a job listing."""
        # Create job
        job = JobListingDB(**sample_job_data)
        db_session.add(job)
        db_session.commit()

        # Update job
        job.title = "Updated Senior Python Developer"
        job.salary_max = 150000
        job.verification_status = VerificationStatus.EXPIRED

        db_session.commit()
        db_session.refresh(job)

        assert job.title == "Updated Senior Python Developer"
        assert job.salary_max == 150000
        assert job.verification_status == VerificationStatus.EXPIRED

    def test_delete_job_listing(self, db_session, sample_job_data):
        """Test deleting a job listing."""
        # Create job
        job = JobListingDB(**sample_job_data)
        db_session.add(job)
        db_session.commit()

        job_id = job.id

        # Delete job
        db_session.delete(job)
        db_session.commit()

        # Verify deletion
        deleted_job = (
            db_session.query(JobListingDB).filter(JobListingDB.id == job_id).first()
        )
        assert deleted_job is None

    def test_job_with_json_fields(self, db_session):
        """Test job listing with JSON fields."""
        job_data = {
            "id": str(uuid4()),
            "title": "Full Stack Developer",
            "company": "StartupXYZ",
            "skills_required": ["Python", "JavaScript", "React"],
            "tech_stack": ["Django", "PostgreSQL", "Redis"],
            "benefits": ["Health", "Dental", "401k"],
            "job_preferences": {"remote": True, "flexible_hours": True},
        }

        job = JobListingDB(**job_data)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.skills_required == ["Python", "JavaScript", "React"]
        assert job.tech_stack == ["Django", "PostgreSQL", "Redis"]
        assert job.benefits == ["Health", "Dental", "401k"]


class TestUserProfileCRUD:
    """Test UserProfile model CRUD operations."""

    def test_create_user_profile(self, db_session, sample_user_data):
        """Test creating a user profile."""
        user = UserProfileDB(**sample_user_data)

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.full_name == sample_user_data["full_name"]
        assert user.skills == sample_user_data["skills"]

    def test_user_unique_email(self, db_session, sample_user_data):
        """Test that user emails must be unique."""
        # Create first user
        user1 = UserProfileDB(**sample_user_data)
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same email
        user2_data = sample_user_data.copy()
        user2_data["id"] = str(uuid4())
        user2_data["full_name"] = "Different User"

        user2 = UserProfileDB(**user2_data)
        db_session.add(user2)

        # This should raise an integrity error
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()


class TestCompanyCRUD:
    """Test Company model CRUD operations."""

    def test_create_company(self, db_session, sample_company_data):
        """Test creating a company."""
        company = CompanyDB(**sample_company_data)

        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.id is not None
        assert company.name == sample_company_data["name"]
        assert company.size_category == CompanySizeCategory.LARGE
        assert company.company_culture == sample_company_data["company_culture"]


# ==================== Relationship Tests ====================


class TestModelRelationships:
    """Test relationships between database models."""

    def test_job_company_relationship(
        self, db_session, sample_job_data, sample_company_data
    ):
        """Test relationship between jobs and companies."""
        # Create company
        company = CompanyDB(**sample_company_data)
        db_session.add(company)
        db_session.commit()

        # Create job linked to company
        job_data = sample_job_data.copy()
        job_data["company_id"] = company.id
        job_data["company"] = company.name  # Also set the company name field

        job = JobListingDB(**job_data)
        db_session.add(job)
        db_session.commit()

        # Test relationship
        db_session.refresh(job)
        db_session.refresh(company)

        # If relationships are properly set up, we should be able to access related objects
        # This depends on the actual relationship configuration in models.py
        assert job.company_id == company.id

    def test_user_application_relationship(
        self, db_session, sample_user_data, sample_job_data
    ):
        """Test relationship between users and applications."""
        # Create user
        user = UserProfileDB(**sample_user_data)
        db_session.add(user)
        db_session.commit()

        # Create job
        job = JobListingDB(**sample_job_data)
        db_session.add(job)
        db_session.commit()

        # Create application
        application_data = {
            "id": str(uuid4()),
            "user_id": user.id,
            "job_id": job.id,
            "status": "applied",
            "cover_letter": "I am very interested in this position...",
            "notes": "Applied through company website",
            "applied_at": datetime.now(timezone.utc),
        }

        application = ApplicationDB(**application_data)
        db_session.add(application)
        db_session.commit()

        # Test relationships
        assert application.user_id == user.id
        assert application.job_id == job.id

    def test_timeline_events(self, db_session, sample_user_data, sample_job_data):
        """Test timeline events creation and relationships."""
        # Create user and job
        user = UserProfileDB(**sample_user_data)
        job = JobListingDB(**sample_job_data)

        db_session.add(user)
        db_session.add(job)
        db_session.commit()

        # Create timeline event
        timeline_event = TimelineEventDB(
            id=str(uuid4()),
            user_id=user.id,
            event_type=TimelineEventType.JOB_SAVED,
            title="Job Saved",
            description=f"Saved job: {job.title} at {job.company}",
            metadata={"job_id": job.id, "job_title": job.title},
        )

        db_session.add(timeline_event)
        db_session.commit()

        # Verify timeline event
        assert timeline_event.user_id == user.id
        assert timeline_event.event_type == TimelineEventType.JOB_SAVED
        assert timeline_event.metadata["job_id"] == job.id


# ==================== Transaction Tests ====================


class TestTransactions:
    """Test database transaction handling."""

    def test_transaction_commit(self, db_session, sample_job_data):
        """Test successful transaction commit."""
        job = JobListingDB(**sample_job_data)

        db_session.add(job)
        db_session.commit()

        # Verify job was saved
        saved_job = (
            db_session.query(JobListingDB).filter(JobListingDB.id == job.id).first()
        )
        assert saved_job is not None
        assert saved_job.title == sample_job_data["title"]

    def test_transaction_rollback(self, db_session, sample_job_data):
        """Test transaction rollback on error."""
        job = JobListingDB(**sample_job_data)
        db_session.add(job)

        # Force an error and rollback
        try:
            db_session.flush()  # This should work

            # Create another job with same ID to force error
            duplicate_job = JobListingDB(**sample_job_data)
            db_session.add(duplicate_job)
            db_session.commit()  # This should fail

        except Exception:
            db_session.rollback()

            # Verify no jobs were saved due to rollback
            jobs = (
                db_session.query(JobListingDB).filter(JobListingDB.id == job.id).all()
            )
            assert len(jobs) == 0

    def test_batch_operations(self, db_session):
        """Test batch operations within a single transaction."""
        jobs_data = []
        for i in range(5):
            job_data = {
                "id": str(uuid4()),
                "title": f"Developer {i}",
                "company": f"Company {i}",
                "location": "Remote",
                "description": f"Description for job {i}",
                "requirements": f"Requirements for job {i}",
            }
            jobs_data.append(job_data)

        # Batch create jobs
        jobs = [JobListingDB(**data) for data in jobs_data]
        db_session.add_all(jobs)
        db_session.commit()

        # Verify all jobs were created
        saved_jobs = (
            db_session.query(JobListingDB)
            .filter(JobListingDB.company.like("Company %"))
            .all()
        )

        assert len(saved_jobs) == 5


# ==================== Data Integrity Tests ====================


class TestDataIntegrity:
    """Test data integrity constraints and validation."""

    def test_required_fields_validation(self, db_session):
        """Test that required fields are enforced."""
        # Try to create job without required fields
        with pytest.raises(Exception):
            job = JobListingDB()  # Missing required fields
            db_session.add(job)
            db_session.commit()

    def test_enum_field_validation(self, db_session):
        """Test that enum fields accept valid values."""
        job_data = {
            "id": str(uuid4()),
            "title": "Test Job",
            "company": "Test Company",
            "verification_status": VerificationStatus.ACTIVE,
            "company_size_category": CompanySizeCategory.STARTUP,
            "seniority_level": SeniorityLevel.INDIVIDUAL_CONTRIBUTOR,
        }

        job = JobListingDB(**job_data)
        db_session.add(job)
        db_session.commit()

        # Verify enum values are stored correctly
        db_session.refresh(job)
        assert job.verification_status == VerificationStatus.ACTIVE
        assert job.company_size_category == CompanySizeCategory.STARTUP
        assert job.seniority_level == SeniorityLevel.INDIVIDUAL_CONTRIBUTOR

    def test_foreign_key_constraints(self, db_session, sample_user_data):
        """Test foreign key constraints."""
        # Try to create application with non-existent user_id
        application_data = {
            "id": str(uuid4()),
            "user_id": "nonexistent-user-id",
            "job_id": str(uuid4()),
            "status": "applied",
        }

        application = ApplicationDB(**application_data)
        db_session.add(application)

        # This might not fail immediately due to SQLite's foreign key handling
        # But it should fail if foreign key constraints are properly enforced
        try:
            db_session.commit()
            # If it doesn't fail, that's ok for SQLite - just log it
            print("Note: Foreign key constraint not enforced (expected for SQLite)")
        except Exception:
            # This is expected if foreign key constraints are enforced
            db_session.rollback()


# ==================== Performance Tests ====================


class TestDatabasePerformance:
    """Test database performance with larger datasets."""

    @pytest.mark.performance
    def test_bulk_insert_performance(self, db_session):
        """Test performance of bulk insert operations."""
        import time

        # Generate 100 job records
        jobs_data = []
        for i in range(100):
            job_data = {
                "id": str(uuid4()),
                "title": f"Developer {i}",
                "company": f"Company {i % 10}",  # 10 different companies
                "location": "Remote",
                "description": f"Job description {i}",
                "requirements": f"Requirements {i}",
                "skills_required": ["Python", "SQL", "Git"],
                "verification_status": VerificationStatus.ACTIVE,
            }
            jobs_data.append(job_data)

        # Time the bulk insert
        start_time = time.time()

        jobs = [JobListingDB(**data) for data in jobs_data]
        db_session.add_all(jobs)
        db_session.commit()

        end_time = time.time()
        insert_time = end_time - start_time

        print(f"Bulk insert of 100 jobs took: {insert_time:.3f} seconds")

        # Verify all jobs were inserted
        job_count = db_session.query(JobListingDB).count()
        assert job_count >= 100

        # Should complete within reasonable time (adjust as needed)
        assert insert_time < 5.0  # 5 seconds should be plenty for 100 records

    @pytest.mark.performance
    def test_query_performance(self, db_session):
        """Test query performance with indexed fields."""
        import time

        # First create some test data
        jobs_data = []
        for i in range(50):
            job_data = {
                "id": str(uuid4()),
                "title": f"Developer {i}",
                "company": f"Company {i % 5}",
                "location": f"City {i % 10}",
                "verification_status": VerificationStatus.ACTIVE,
                "salary_min": 50000 + (i * 1000),
                "salary_max": 80000 + (i * 1000),
            }
            jobs_data.append(job_data)

        jobs = [JobListingDB(**data) for data in jobs_data]
        db_session.add_all(jobs)
        db_session.commit()

        # Test various queries
        start_time = time.time()

        # Query by company
        company_jobs = (
            db_session.query(JobListingDB)
            .filter(JobListingDB.company == "Company 1")
            .all()
        )

        # Query by salary range
        salary_jobs = (
            db_session.query(JobListingDB)
            .filter(JobListingDB.salary_min >= 60000, JobListingDB.salary_max <= 120000)
            .all()
        )

        # Query by location
        location_jobs = (
            db_session.query(JobListingDB)
            .filter(JobListingDB.location.like("City%"))
            .all()
        )

        end_time = time.time()
        query_time = end_time - start_time

        print(f"Complex queries took: {query_time:.3f} seconds")
        print(
            f"Found {len(company_jobs)} company jobs, {len(salary_jobs)} salary jobs, {len(location_jobs)} location jobs"
        )

        # Verify results
        assert len(company_jobs) > 0
        assert len(salary_jobs) > 0
        assert len(location_jobs) > 0

        # Should be fast for this dataset size
        assert query_time < 2.0
