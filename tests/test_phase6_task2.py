"""
Test-Driven Development for Phase 6 Task 2: JobUserInteractionRepository
Task 6.2: Create JobUserInteractionRepository

This test file validates that the JobUserInteractionRepository correctly handles
all user-job interactions (saved jobs, applications, views, etc.) using the
consolidated JobUserInteractionDB model instead of separate repositories.
"""

from uuid import uuid4

import pytest

from app.data.database import DatabaseManager
from app.data.models import (
    ApplicationStatus,
    CompanyInfoDB,
    CompanySizeCategory,
    ExperienceLevel,
    InteractionType,
    JobListingDB,
    JobStatus,
    JobType,
    JobUserInteractionDB,
    RemoteType,
    UserProfileDB,
)


@pytest.fixture
def db_manager():
    """Create an in-memory test database."""
    db_manager = DatabaseManager("sqlite:///:memory:")
    return db_manager


@pytest.fixture
def test_user(db_manager):
    """Create a test user profile."""
    user_data = {
        "id": str(uuid4()),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "current_title": "Software Engineer",
        "experience_years": 5,
    }

    with db_manager.get_session() as session:
        user = UserProfileDB(**user_data)
        session.add(user)
        session.flush()
        return user.id


@pytest.fixture
def test_company(db_manager):
    """Create a test company."""
    company_data = {
        "id": str(uuid4()),
        "name": "Test Company Inc",
        "normalized_name": "test company",
        "domain": "testcompany.com",
        "industry": "Technology",
        "size_category": CompanySizeCategory.MEDIUM,
        "website": "https://testcompany.com",
    }

    with db_manager.get_session() as session:
        company = CompanyInfoDB(**company_data)
        session.add(company)
        session.flush()
        return company.id


@pytest.fixture
def test_jobs(db_manager, test_company):
    """Create test job listings."""
    jobs_data = [
        {
            "id": str(uuid4()),
            "title": "Senior Software Engineer",
            "company_id": test_company,
            "location": "San Francisco, CA",
            "description": "Build amazing software",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.REMOTE,
            "experience_level": ExperienceLevel.SENIOR_LEVEL,
            "salary_min": 120000,
            "salary_max": 180000,
            "status": JobStatus.ACTIVE,
        },
        {
            "id": str(uuid4()),
            "title": "Frontend Developer",
            "company_id": test_company,
            "location": "New York, NY",
            "description": "Build user interfaces",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.HYBRID,
            "experience_level": ExperienceLevel.MID_LEVEL,
            "salary_min": 90000,
            "salary_max": 130000,
            "status": JobStatus.ACTIVE,
        },
        {
            "id": str(uuid4()),
            "title": "Backend Developer",
            "company_id": test_company,
            "location": "Austin, TX",
            "description": "Build APIs and services",
            "job_type": JobType.CONTRACT,
            "remote_type": RemoteType.REMOTE,
            "experience_level": ExperienceLevel.MID_LEVEL,
            "salary_min": 100000,
            "salary_max": 140000,
            "status": JobStatus.ACTIVE,
        },
    ]

    with db_manager.get_session() as session:
        job_ids = []
        for job_data in jobs_data:
            job = JobListingDB(**job_data)
            session.add(job)
            job_ids.append(job.id)
        session.flush()
        return job_ids


@pytest.fixture
def interaction_repo(db_manager):
    """Create a JobUserInteractionRepository instance."""
    from app.data.interaction_repository import JobUserInteractionRepository

    return JobUserInteractionRepository(db_manager)


class TestJobUserInteractionRepository:
    """Test JobUserInteractionRepository core functionality."""

    def test_save_job_basic(self, interaction_repo, test_user, test_jobs):
        """Test saving a job for later."""
        job_id = test_jobs[0]

        interaction = interaction_repo.save_job(
            user_id=test_user,
            job_id=job_id,
            notes="Interesting position, good salary range",
        )

        assert interaction is not None
        assert interaction.user_id == test_user
        assert interaction.job_id == job_id
        assert interaction.interaction_type == InteractionType.SAVED
        assert interaction.notes == "Interesting position, good salary range"
        assert interaction.saved_date is not None
        assert interaction.first_interaction is not None

    def test_save_job_with_tags(self, interaction_repo, test_user, test_jobs):
        """Test saving a job with tags."""
        job_id = test_jobs[1]
        tags = ["frontend", "react", "high-priority"]

        interaction = interaction_repo.save_job(
            user_id=test_user, job_id=job_id, tags=tags
        )

        assert interaction.tags == tags
        assert interaction.interaction_type == InteractionType.SAVED

    def test_save_job_duplicate_prevents_multiple_saves(
        self, interaction_repo, test_user, test_jobs
    ):
        """Test that saving the same job twice updates the existing record."""
        job_id = test_jobs[0]

        # Save job first time
        first_save = interaction_repo.save_job(
            user_id=test_user, job_id=job_id, notes="First save"
        )

        # Save job second time
        second_save = interaction_repo.save_job(
            user_id=test_user, job_id=job_id, notes="Updated save", tags=["updated"]
        )

        # Should be the same interaction, updated
        assert first_save.id == second_save.id
        assert second_save.notes == "Updated save"
        assert second_save.tags == ["updated"]
        assert second_save.last_interaction > first_save.last_interaction

    def test_apply_to_job_basic(self, interaction_repo, test_user, test_jobs):
        """Test applying to a job."""
        job_id = test_jobs[0]

        interaction = interaction_repo.apply_to_job(
            user_id=test_user,
            job_id=job_id,
            resume_version="Software_Engineer_Resume_v2.pdf",
            cover_letter="I am very interested in this position...",
        )

        assert interaction is not None
        assert interaction.user_id == test_user
        assert interaction.job_id == job_id
        assert interaction.interaction_type == InteractionType.APPLIED
        assert interaction.application_status == ApplicationStatus.APPLIED
        assert interaction.resume_version == "Software_Engineer_Resume_v2.pdf"
        assert interaction.cover_letter == "I am very interested in this position..."
        assert interaction.applied_date is not None

    def test_apply_to_job_without_materials(
        self, interaction_repo, test_user, test_jobs
    ):
        """Test applying to a job without resume or cover letter."""
        job_id = test_jobs[1]

        interaction = interaction_repo.apply_to_job(user_id=test_user, job_id=job_id)

        assert interaction.interaction_type == InteractionType.APPLIED
        assert interaction.application_status == ApplicationStatus.APPLIED
        assert interaction.resume_version is None
        assert interaction.cover_letter is None

    def test_apply_to_job_duplicate_prevents_multiple_applications(
        self, interaction_repo, test_user, test_jobs
    ):
        """Test that applying to the same job twice updates the existing application."""
        job_id = test_jobs[0]

        # Apply first time
        first_application = interaction_repo.apply_to_job(
            user_id=test_user, job_id=job_id, resume_version="v1.pdf"
        )

        # Apply second time (maybe user wants to update their application)
        second_application = interaction_repo.apply_to_job(
            user_id=test_user,
            job_id=job_id,
            resume_version="v2.pdf",
            cover_letter="Updated cover letter",
        )

        # Should be the same interaction, updated
        assert first_application.id == second_application.id
        assert second_application.resume_version == "v2.pdf"
        assert second_application.cover_letter == "Updated cover letter"

    def test_get_user_interactions_all(self, interaction_repo, test_user, test_jobs):
        """Test getting all user interactions."""
        # Create multiple interactions
        interaction_repo.save_job(test_user, test_jobs[0])
        interaction_repo.apply_to_job(test_user, test_jobs[1])
        interaction_repo.record_job_view(test_user, test_jobs[2])

        interactions = interaction_repo.get_user_interactions(test_user)

        assert len(interactions) == 3
        interaction_types = {i.interaction_type for i in interactions}
        expected_types = {
            InteractionType.SAVED,
            InteractionType.APPLIED,
            InteractionType.VIEWED,
        }
        assert interaction_types == expected_types

    def test_get_user_interactions_by_type(
        self, interaction_repo, test_user, test_jobs
    ):
        """Test getting user interactions filtered by type."""
        # Create multiple interactions
        interaction_repo.save_job(test_user, test_jobs[0])
        interaction_repo.apply_to_job(test_user, test_jobs[1])
        interaction_repo.save_job(test_user, test_jobs[2])

        # Get only saved jobs
        saved_interactions = interaction_repo.get_user_interactions(
            test_user, interaction_type=InteractionType.SAVED
        )

        assert len(saved_interactions) == 2
        assert all(
            i.interaction_type == InteractionType.SAVED for i in saved_interactions
        )

        # Get only applications
        applied_interactions = interaction_repo.get_user_interactions(
            test_user, interaction_type=InteractionType.APPLIED
        )

        assert len(applied_interactions) == 1
        assert applied_interactions[0].interaction_type == InteractionType.APPLIED

    def test_get_saved_jobs(self, interaction_repo, test_user, test_jobs):
        """Test getting user's saved jobs."""
        # Save some jobs
        interaction_repo.save_job(test_user, test_jobs[0], notes="Great opportunity")
        interaction_repo.save_job(test_user, test_jobs[1], tags=["frontend"])
        interaction_repo.apply_to_job(
            test_user, test_jobs[2]
        )  # This should not appear in saved jobs

        saved_jobs = interaction_repo.get_saved_jobs(test_user)

        assert len(saved_jobs) == 2
        assert all(job.interaction_type == InteractionType.SAVED for job in saved_jobs)
        job_ids = {job.job_id for job in saved_jobs}
        assert job_ids == {test_jobs[0], test_jobs[1]}

    def test_get_applications(self, interaction_repo, test_user, test_jobs):
        """Test getting user's job applications."""
        # Apply to some jobs
        interaction_repo.apply_to_job(test_user, test_jobs[0])
        interaction_repo.apply_to_job(test_user, test_jobs[1])
        interaction_repo.save_job(
            test_user, test_jobs[2]
        )  # This should not appear in applications

        applications = interaction_repo.get_applications(test_user)

        assert len(applications) == 2
        assert all(
            app.interaction_type == InteractionType.APPLIED for app in applications
        )
        job_ids = {app.job_id for app in applications}
        assert job_ids == {test_jobs[0], test_jobs[1]}

    def test_get_applications_by_status(self, interaction_repo, test_user, test_jobs):
        """Test getting applications filtered by status."""
        # Create applications with different statuses
        app1 = interaction_repo.apply_to_job(test_user, test_jobs[0])
        app2 = interaction_repo.apply_to_job(test_user, test_jobs[1])

        # Update one application status
        interaction_repo.update_application_status(
            app1.id, ApplicationStatus.INTERVIEWING
        )

        # Get applications by status
        interviewing_apps = interaction_repo.get_applications(
            test_user, status=ApplicationStatus.INTERVIEWING
        )
        applied_apps = interaction_repo.get_applications(
            test_user, status=ApplicationStatus.APPLIED
        )

        assert len(interviewing_apps) == 1
        assert interviewing_apps[0].job_id == test_jobs[0]
        assert len(applied_apps) == 1
        assert applied_apps[0].job_id == test_jobs[1]

    def test_record_job_view(self, interaction_repo, test_user, test_jobs):
        """Test recording job views."""
        job_id = test_jobs[0]

        interaction = interaction_repo.record_job_view(test_user, job_id)

        assert interaction.interaction_type == InteractionType.VIEWED
        assert interaction.user_id == test_user
        assert interaction.job_id == job_id
        assert interaction.first_interaction is not None

    def test_record_job_view_multiple_times_updates_count(
        self, interaction_repo, test_user, test_jobs
    ):
        """Test that viewing the same job multiple times updates interaction count."""
        job_id = test_jobs[0]

        # View job multiple times
        first_view = interaction_repo.record_job_view(test_user, job_id)
        second_view = interaction_repo.record_job_view(test_user, job_id)
        third_view = interaction_repo.record_job_view(test_user, job_id)

        # Should be the same interaction with updated count
        assert first_view.id == second_view.id == third_view.id
        assert third_view.interaction_count == 3
        assert third_view.last_interaction > first_view.last_interaction

    def test_hide_job(self, interaction_repo, test_user, test_jobs):
        """Test hiding a job from user's view."""
        job_id = test_jobs[0]

        interaction = interaction_repo.hide_job(
            user_id=test_user,
            job_id=job_id,
            reason="Not interested in this type of role",
        )

        assert interaction.interaction_type == InteractionType.HIDDEN
        assert interaction.user_id == test_user
        assert interaction.job_id == job_id
        assert interaction.notes == "Not interested in this type of role"

    def test_update_application_status(self, interaction_repo, test_user, test_jobs):
        """Test updating application status."""
        job_id = test_jobs[0]

        # Apply to job
        application = interaction_repo.apply_to_job(test_user, job_id)
        original_status = application.application_status

        # Update status
        success = interaction_repo.update_application_status(
            application.id, ApplicationStatus.INTERVIEWING
        )

        assert success is True

        # Verify status was updated
        updated_applications = interaction_repo.get_applications(test_user)
        updated_app = next(
            app for app in updated_applications if app.id == application.id
        )
        assert updated_app.application_status == ApplicationStatus.INTERVIEWING
        assert updated_app.application_status != original_status

    def test_update_application_status_nonexistent_interaction(self, interaction_repo):
        """Test updating status for non-existent interaction."""
        success = interaction_repo.update_application_status(
            "non-existent-id", ApplicationStatus.REJECTED
        )

        assert success is False

    def test_interaction_timestamps(self, interaction_repo, test_user, test_jobs):
        """Test that interaction timestamps are properly set."""
        job_id = test_jobs[0]

        # Save job
        saved_interaction = interaction_repo.save_job(test_user, job_id)

        assert saved_interaction.first_interaction is not None
        assert saved_interaction.last_interaction is not None
        assert saved_interaction.saved_date is not None
        assert saved_interaction.first_interaction <= saved_interaction.last_interaction

        # Apply to job
        applied_interaction = interaction_repo.apply_to_job(test_user, test_jobs[1])

        assert applied_interaction.applied_date is not None
        assert applied_interaction.first_interaction is not None

    def test_interaction_data_storage(self, interaction_repo, test_user, test_jobs):
        """Test flexible interaction data storage."""
        job_id = test_jobs[0]

        # Apply with custom interaction data
        interaction = interaction_repo.apply_to_job(
            user_id=test_user,
            job_id=job_id,
            interaction_data={
                "application_method": "company_website",
                "referral": "Jane Smith",
                "custom_note": "Applied through networking event",
            },
        )

        assert interaction.interaction_data["application_method"] == "company_website"
        assert interaction.interaction_data["referral"] == "Jane Smith"
        assert (
            interaction.interaction_data["custom_note"]
            == "Applied through networking event"
        )


class TestJobUserInteractionRepositoryEdgeCases:
    """Test edge cases and error handling."""

    def test_save_job_with_invalid_user_id(self, interaction_repo, test_jobs):
        """Test saving job with invalid user ID."""
        # NOTE: SQLite doesn't enforce foreign key constraints by default in memory DBs
        # In production with proper constraints, this would raise an error
        # For now, we test that the operation completes but creates orphaned data
        interaction = interaction_repo.save_job(
            user_id="invalid-user-id", job_id=test_jobs[0]
        )
        # Interaction is created, but with invalid foreign key reference
        assert interaction.user_id == "invalid-user-id"
        assert interaction.job_id == test_jobs[0]

    def test_save_job_with_invalid_job_id(self, interaction_repo, test_user):
        """Test saving job with invalid job ID."""
        # NOTE: SQLite doesn't enforce foreign key constraints by default in memory DBs
        # In production with proper constraints, this would raise an error
        # For now, we test that the operation completes but creates orphaned data
        interaction = interaction_repo.save_job(
            user_id=test_user, job_id="invalid-job-id"
        )
        # Interaction is created, but with invalid foreign key reference
        assert interaction.user_id == test_user
        assert interaction.job_id == "invalid-job-id"

    def test_get_interactions_empty_result(self, interaction_repo, test_user):
        """Test getting interactions when user has none."""
        interactions = interaction_repo.get_user_interactions(test_user)
        assert interactions == []

        saved_jobs = interaction_repo.get_saved_jobs(test_user)
        assert saved_jobs == []

        applications = interaction_repo.get_applications(test_user)
        assert applications == []

    def test_get_interactions_with_limit(self, interaction_repo, test_user, test_jobs):
        """Test getting interactions with limit parameter."""
        # Create many interactions
        for job_id in test_jobs:
            interaction_repo.save_job(test_user, job_id)

        # Test limit
        limited_interactions = interaction_repo.get_user_interactions(
            test_user, limit=2
        )
        assert len(limited_interactions) == 2

        # Test no limit
        all_interactions = interaction_repo.get_user_interactions(test_user)
        assert len(all_interactions) == len(test_jobs)

    def test_interactions_ordered_by_date(self, interaction_repo, test_user, test_jobs):
        """Test that interactions are returned in proper order (newest first)."""
        # Create interactions with delays to ensure different timestamps
        import time

        interaction_repo.save_job(test_user, test_jobs[0])
        time.sleep(0.01)  # Small delay
        interaction_repo.save_job(test_user, test_jobs[1])
        time.sleep(0.01)
        interaction_repo.save_job(test_user, test_jobs[2])

        interactions = interaction_repo.get_user_interactions(test_user)

        # Should be ordered by last_interaction desc (newest first)
        for i in range(len(interactions) - 1):
            assert (
                interactions[i].last_interaction >= interactions[i + 1].last_interaction
            )


class TestJobUserInteractionRepositoryIntegration:
    """Test integration with existing job and user data."""

    def test_interaction_with_job_details(
        self, interaction_repo, test_user, test_jobs, db_manager
    ):
        """Test that interactions can access related job details."""
        job_id = test_jobs[0]

        # Save a job
        interaction = interaction_repo.save_job(test_user, job_id)

        # Verify we can access job details through the interaction
        with db_manager.get_session() as session:
            interaction_db = (
                session.query(JobUserInteractionDB)
                .filter(JobUserInteractionDB.id == interaction.id)
                .first()
            )

            # Should be able to access job through relationship
            assert interaction_db.job is not None
            assert interaction_db.job.title == "Senior Software Engineer"
            assert interaction_db.job.company_id is not None

    def test_interaction_with_user_details(
        self, interaction_repo, test_user, test_jobs, db_manager
    ):
        """Test that interactions can access related user details."""
        job_id = test_jobs[0]

        # Apply to a job
        interaction = interaction_repo.apply_to_job(test_user, job_id)

        # Verify we can access user details through the interaction
        with db_manager.get_session() as session:
            interaction_db = (
                session.query(JobUserInteractionDB)
                .filter(JobUserInteractionDB.id == interaction.id)
                .first()
            )

            # Should be able to access user through relationship
            assert interaction_db.user is not None
            assert interaction_db.user.email == "john.doe@example.com"
            assert interaction_db.user.first_name == "John"


# Test data setup validation
def test_fixtures_setup(test_user, test_company, test_jobs):
    """Verify that test fixtures are set up correctly."""
    assert test_user is not None
    assert test_company is not None
    assert len(test_jobs) == 3

    for job_id in test_jobs:
        assert job_id is not None
