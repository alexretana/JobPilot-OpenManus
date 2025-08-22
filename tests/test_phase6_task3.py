"""
Test-Driven Development for Phase 6 Task 3: Update get_database_manager Function
Task 6.3: Update get_database_manager Function

This test file validates that the database manager module correctly provides
access to all repositories including the new JobUserInteractionRepository
and CompanyRepository (to be created in Task 6.4).
"""

from app.data import database


class TestDatabaseManagerInitialization:
    """Test database manager initialization with all repositories."""

    def test_initialize_database_creates_all_repositories(self):
        """Test that initialize_database creates all repository instances."""
        # Initialize database (should create all global repository instances)
        database.initialize_database("sqlite:///:memory:")

        # Verify all repository globals are created
        assert database.db_manager is not None
        assert database.job_repo is not None
        assert database.user_repo is not None
        assert database.saved_job_repo is not None
        assert database.application_repo is not None
        assert database.resume_repo is not None

        # NEW: Verify new repositories are created
        assert database.interaction_repo is not None
        # Note: company_repo will be tested in Task 6.4 when we create CompanyRepository

        # Verify repository types
        from app.data.database import (
            ApplicationRepository,
            JobRepository,
            ResumeRepository,
            SavedJobRepository,
            UserRepository,
        )
        from app.data.interaction_repository import JobUserInteractionRepository

        assert isinstance(database.job_repo, JobRepository)
        assert isinstance(database.user_repo, UserRepository)
        assert isinstance(database.saved_job_repo, SavedJobRepository)
        assert isinstance(database.application_repo, ApplicationRepository)
        assert isinstance(database.resume_repo, ResumeRepository)
        assert isinstance(database.interaction_repo, JobUserInteractionRepository)

    def test_multiple_initialize_calls_are_safe(self):
        """Test that calling initialize_database multiple times doesn't break anything."""
        # Initialize multiple times
        database.initialize_database("sqlite:///:memory:")
        first_db_manager = database.db_manager
        first_job_repo = database.job_repo
        first_interaction_repo = database.interaction_repo

        database.initialize_database("sqlite:///:memory:")  # Second call
        second_db_manager = database.db_manager
        second_job_repo = database.job_repo
        second_interaction_repo = database.interaction_repo

        # Should have new instances (not the same objects)
        assert first_db_manager is not second_db_manager
        assert first_job_repo is not second_job_repo
        assert first_interaction_repo is not second_interaction_repo

        # But they should still be valid instances
        assert database.db_manager is not None
        assert database.job_repo is not None
        assert database.interaction_repo is not None


class TestRepositoryGetterFunctions:
    """Test repository getter functions."""

    def test_get_database_manager_returns_instance(self):
        """Test that get_database_manager returns a DatabaseManager instance."""
        db_manager = database.get_database_manager()

        assert db_manager is not None
        from app.data.database import DatabaseManager

        assert isinstance(db_manager, DatabaseManager)

    def test_get_database_manager_initializes_if_needed(self):
        """Test that get_database_manager initializes database if not already done."""
        # Clear global state
        database.db_manager = None
        database.job_repo = None
        database.interaction_repo = None

        # Should initialize when called
        db_manager = database.get_database_manager()

        assert db_manager is not None
        assert database.db_manager is not None
        assert database.job_repo is not None
        assert database.interaction_repo is not None

    def test_get_job_repository_returns_instance(self):
        """Test that get_job_repository returns a JobRepository instance."""
        job_repo = database.get_job_repository()

        assert job_repo is not None
        from app.data.database import JobRepository

        assert isinstance(job_repo, JobRepository)

    def test_get_user_repository_returns_instance(self):
        """Test that get_user_repository returns a UserRepository instance."""
        user_repo = database.get_user_repository()

        assert user_repo is not None
        from app.data.database import UserRepository

        assert isinstance(user_repo, UserRepository)

    def test_get_saved_job_repository_returns_instance(self):
        """Test that get_saved_job_repository returns a SavedJobRepository instance."""
        saved_job_repo = database.get_saved_job_repository()

        assert saved_job_repo is not None
        from app.data.database import SavedJobRepository

        assert isinstance(saved_job_repo, SavedJobRepository)

    def test_get_application_repository_returns_instance(self):
        """Test that get_application_repository returns an ApplicationRepository instance."""
        app_repo = database.get_application_repository()

        assert app_repo is not None
        from app.data.database import ApplicationRepository

        assert isinstance(app_repo, ApplicationRepository)

    def test_get_resume_repository_returns_instance(self):
        """Test that get_resume_repository returns a ResumeRepository instance."""
        resume_repo = database.get_resume_repository()

        assert resume_repo is not None
        from app.data.database import ResumeRepository

        assert isinstance(resume_repo, ResumeRepository)

    def test_get_interaction_repository_returns_instance(self):
        """Test that get_interaction_repository returns a JobUserInteractionRepository instance."""
        interaction_repo = database.get_interaction_repository()

        assert interaction_repo is not None
        from app.data.interaction_repository import JobUserInteractionRepository

        assert isinstance(interaction_repo, JobUserInteractionRepository)

    def test_get_interaction_repository_initializes_if_needed(self):
        """Test that get_interaction_repository initializes database if not already done."""
        # Clear global state
        database.interaction_repo = None
        database.db_manager = None

        # Should initialize when called
        interaction_repo = database.get_interaction_repository()

        assert interaction_repo is not None
        assert database.interaction_repo is not None
        assert database.db_manager is not None


class TestRepositoryConsistency:
    """Test that all repositories share the same database manager."""

    def test_all_repositories_share_same_database_manager(self):
        """Test that all repositories use the same DatabaseManager instance."""
        # Get all repositories
        db_manager = database.get_database_manager()
        job_repo = database.get_job_repository()
        user_repo = database.get_user_repository()
        interaction_repo = database.get_interaction_repository()
        saved_job_repo = database.get_saved_job_repository()

        # All repositories should share the same database manager
        assert job_repo.db_manager is db_manager
        assert user_repo.db_manager is db_manager
        assert interaction_repo.db_manager is db_manager
        assert saved_job_repo.db_manager is db_manager

    def test_repositories_are_singletons(self):
        """Test that getter functions return the same instances on multiple calls."""
        # Get repositories twice
        job_repo1 = database.get_job_repository()
        job_repo2 = database.get_job_repository()

        interaction_repo1 = database.get_interaction_repository()
        interaction_repo2 = database.get_interaction_repository()

        user_repo1 = database.get_user_repository()
        user_repo2 = database.get_user_repository()

        # Should be the same instances (singleton pattern)
        assert job_repo1 is job_repo2
        assert interaction_repo1 is interaction_repo2
        assert user_repo1 is user_repo2


class TestDatabaseManagerConfiguration:
    """Test database manager configuration and setup."""

    def test_initialize_database_with_custom_url(self):
        """Test initializing database with custom URL."""
        custom_url = "sqlite:///test_custom.db"
        database.initialize_database(custom_url)

        db_manager = database.get_database_manager()
        assert db_manager.database_url == custom_url

    def test_initialize_database_without_url_uses_default(self):
        """Test that initializing without URL uses default."""
        database.initialize_database()

        db_manager = database.get_database_manager()
        # Should have some default URL (exact value depends on implementation)
        assert db_manager.database_url is not None
        assert db_manager.database_url != ""

    def test_database_health_check_works(self):
        """Test that database health check works through the manager."""
        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()

        # Health check should pass for in-memory database
        assert db_manager.health_check() is True


class TestRepositoryIntegration:
    """Test integration between repositories."""

    def test_job_and_interaction_repositories_work_together(self):
        """Test that JobRepository and JobUserInteractionRepository can work together."""
        from uuid import uuid4

        from app.data.models import (
            CompanyInfoDB,
            CompanySizeCategory,
            ExperienceLevel,
            JobListingDB,
            JobStatus,
            JobType,
            RemoteType,
            UserProfileDB,
        )

        # Initialize repositories
        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        job_repo = database.get_job_repository()
        interaction_repo = database.get_interaction_repository()

        # Create test data
        with db_manager.get_session() as session:
            # Create company
            company = CompanyInfoDB(
                id=str(uuid4()),
                name="Test Company",
                normalized_name="test company",
                domain="testcompany.com",
                size_category=CompanySizeCategory.MEDIUM,
            )
            session.add(company)
            session.flush()

            # Create user
            user = UserProfileDB(
                id=str(uuid4()),
                first_name="Test",
                last_name="User",
                email="test@example.com",
            )
            session.add(user)
            session.flush()

            # Create job
            job = JobListingDB(
                id=str(uuid4()),
                title="Software Engineer",
                company_id=company.id,
                job_type=JobType.FULL_TIME,
                remote_type=RemoteType.REMOTE,
                experience_level=ExperienceLevel.MID_LEVEL,
                status=JobStatus.ACTIVE,
            )
            session.add(job)
            session.flush()

            # Test that interaction repository can interact with the job
            interaction = interaction_repo.save_job(
                user_id=user.id, job_id=job.id, notes="Looks interesting"
            )

            assert interaction is not None
            assert interaction.user_id == user.id
            assert interaction.job_id == job.id
            assert interaction.notes == "Looks interesting"

    def test_repositories_handle_transactions_correctly(self):
        """Test that repositories handle database transactions correctly."""
        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()

        # Test that database manager can handle multiple repository operations
        # in the same transaction context (basic smoke test)
        with db_manager.get_session() as session:
            # This should not raise an exception
            from sqlalchemy import text

            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_existing_repository_functions_still_work(self):
        """Test that all existing repository getter functions still work."""
        # These functions should all work without errors
        db_manager = database.get_database_manager()
        job_repo = database.get_job_repository()
        user_repo = database.get_user_repository()
        saved_job_repo = database.get_saved_job_repository()
        application_repo = database.get_application_repository()
        resume_repo = database.get_resume_repository()

        # All should be valid instances
        assert db_manager is not None
        assert job_repo is not None
        assert user_repo is not None
        assert saved_job_repo is not None
        assert application_repo is not None
        assert resume_repo is not None

    def test_database_manager_table_stats_includes_interactions(self):
        """Test that database manager can handle the new interactions table."""
        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()

        # Should be able to get stats without errors
        # (Even if interactions table is empty, it should not crash)
        stats = db_manager.get_table_stats()
        assert isinstance(stats, dict)
        assert "job_listings" in stats
        assert "user_profiles" in stats


# Integration test with actual database operations
class TestEndToEndIntegration:
    """Test end-to-end integration scenarios."""

    def test_complete_user_job_interaction_flow(self):
        """Test a complete flow: create job, create user, interact with job."""
        from app.data.models import (
            ExperienceLevel,
            InteractionType,
            JobListing,
            JobType,
            RemoteType,
            UserProfile,
        )

        # Initialize everything
        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        job_repo = database.get_job_repository()
        user_repo = database.get_user_repository()
        interaction_repo = database.get_interaction_repository()

        # Create company first
        company = job_repo.get_or_create_company(
            name="Integration Test Company", domain="integrationtest.com"
        )

        # Create job through JobRepository
        job_data = JobListing(
            title="Test Engineer",
            company_id=company.id,
            location="Remote",
            description="Test job for integration testing",
            job_type=JobType.FULL_TIME,
            remote_type=RemoteType.REMOTE,
            experience_level=ExperienceLevel.MID_LEVEL,
        )
        job = job_repo.create_job(job_data)

        # Create user through UserRepository
        user_data = UserProfile(
            first_name="Integration", last_name="Tester", email="integration@test.com"
        )
        user = user_repo.create_user(user_data)

        # Interact with job through InteractionRepository
        saved_interaction = interaction_repo.save_job(
            user_id=str(user.id),
            job_id=str(job.id),
            notes="Saved during integration test",
        )

        applied_interaction = interaction_repo.apply_to_job(
            user_id=str(user.id),
            job_id=str(job.id),
            resume_version="integration_test_resume.pdf",
        )

        # Verify everything worked
        assert saved_interaction.interaction_type == InteractionType.SAVED
        assert applied_interaction.interaction_type == InteractionType.APPLIED

        # Verify we can retrieve the interactions
        user_interactions = interaction_repo.get_user_interactions(str(user.id))
        assert len(user_interactions) == 2

        interaction_types = {i.interaction_type for i in user_interactions}
        assert InteractionType.SAVED in interaction_types
        assert InteractionType.APPLIED in interaction_types
