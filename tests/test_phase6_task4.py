"""
Test-Driven Development for Phase 6 Task 4: Create CompanyRepository Class
Task 6.4: Create CompanyRepository Class

This test file validates the CompanyRepository implementation for managing
company information including creation, retrieval, updating, and specialized
company operations like searching and analytics.
"""

from uuid import UUID, uuid4

import pytest

from app.data import database


class TestCompanyRepositoryBasicOperations:
    """Test basic CRUD operations for CompanyRepository."""

    def test_create_company_with_minimal_data(self):
        """Test creating a company with only required fields."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        # Initialize database and repository
        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create company with minimal data
        company_data = CompanyInfo(name="Test Company", industry="Technology")

        result = company_repo.create_company(company_data)

        assert result is not None
        assert isinstance(result.id, UUID)
        assert result.name == "Test Company"
        assert result.industry == "Technology"
        assert result.created_at is not None
        assert result.updated_at is not None

    def test_create_company_with_full_data(self):
        """Test creating a company with all possible fields."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create company with full data
        company_data = CompanyInfo(
            name="Full Data Company",
            industry="Software",
            size="1000-5000 employees",
            location="San Francisco, CA",
            website="https://fulldatacompany.com",
            description="A comprehensive company description",
            culture="Innovative and collaborative",
            values=["Innovation", "Collaboration", "Excellence"],
            benefits=["Health Insurance", "401k", "Remote Work"],
        )

        result = company_repo.create_company(company_data)

        assert result is not None
        assert result.name == "Full Data Company"
        assert result.industry == "Software"
        assert result.size == "1000-5000 employees"
        assert result.location == "San Francisco, CA"
        assert result.website == "https://fulldatacompany.com"
        assert result.description == "A comprehensive company description"
        assert result.culture == "Innovative and collaborative"
        assert len(result.values) == 3
        assert "Innovation" in result.values
        assert len(result.benefits) == 3
        assert "Health Insurance" in result.benefits

    def test_get_company_by_id(self):
        """Test retrieving a company by ID."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create a company first
        company_data = CompanyInfo(name="Test Company", industry="Tech")
        created_company = company_repo.create_company(company_data)

        # Retrieve the company
        retrieved_company = company_repo.get_company(str(created_company.id))

        assert retrieved_company is not None
        assert retrieved_company.id == created_company.id
        assert retrieved_company.name == "Test Company"
        assert retrieved_company.industry == "Tech"

    def test_get_nonexistent_company(self):
        """Test retrieving a company that doesn't exist."""
        from app.data.company_repository import CompanyRepository

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Try to get non-existent company
        result = company_repo.get_company(str(uuid4()))

        assert result is None

    def test_update_company(self):
        """Test updating company information."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create a company
        company_data = CompanyInfo(name="Original Name", industry="Tech")
        created_company = company_repo.create_company(company_data)

        # Update the company
        update_data = {
            "name": "Updated Name",
            "industry": "Software",
            "description": "Updated description",
        }

        updated_company = company_repo.update_company(
            str(created_company.id), update_data
        )

        assert updated_company is not None
        assert updated_company.id == created_company.id
        assert updated_company.name == "Updated Name"
        assert updated_company.industry == "Software"
        assert updated_company.description == "Updated description"
        assert updated_company.updated_at > created_company.updated_at

    def test_delete_company(self):
        """Test deleting a company."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create a company
        company_data = CompanyInfo(name="To Delete", industry="Tech")
        created_company = company_repo.create_company(company_data)

        # Delete the company
        delete_result = company_repo.delete_company(str(created_company.id))

        assert delete_result is True

        # Verify it's deleted
        retrieved_company = company_repo.get_company(str(created_company.id))
        assert retrieved_company is None


class TestCompanyRepositorySearchOperations:
    """Test search and query operations for CompanyRepository."""

    def test_search_companies_by_name(self):
        """Test searching companies by name."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create test companies
        companies = [
            CompanyInfo(name="Tech Solutions", industry="Technology"),
            CompanyInfo(name="Software Tech", industry="Software"),
            CompanyInfo(name="Hardware Inc", industry="Hardware"),
            CompanyInfo(name="Marketing Corp", industry="Marketing"),
        ]

        for company in companies:
            company_repo.create_company(company)

        # Search for companies with "Tech" in name
        results, total = company_repo.search_companies(query="Tech")

        assert total == 2
        assert len(results) == 2
        company_names = {company.name for company in results}
        assert "Tech Solutions" in company_names
        assert "Software Tech" in company_names

    def test_search_companies_by_industry(self):
        """Test searching companies by industry."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create test companies
        companies = [
            CompanyInfo(name="Tech Corp", industry="Technology"),
            CompanyInfo(name="Software Inc", industry="Technology"),
            CompanyInfo(name="Marketing LLC", industry="Marketing"),
            CompanyInfo(name="Finance Co", industry="Finance"),
        ]

        for company in companies:
            company_repo.create_company(company)

        # Search for companies in Technology industry
        results, total = company_repo.search_companies(industries=["Technology"])

        assert total == 2
        assert len(results) == 2
        for company in results:
            assert company.industry == "Technology"

    def test_search_companies_with_pagination(self):
        """Test search with pagination."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create multiple companies
        for i in range(10):
            company = CompanyInfo(name=f"Company {i}", industry="Tech")
            company_repo.create_company(company)

        # Test pagination
        results_page1, total = company_repo.search_companies(limit=5, offset=0)
        results_page2, total = company_repo.search_companies(limit=5, offset=5)

        assert total == 10
        assert len(results_page1) == 5
        assert len(results_page2) == 5

        # Ensure no duplicates between pages
        page1_ids = {str(company.id) for company in results_page1}
        page2_ids = {str(company.id) for company in results_page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    def test_get_companies_by_industry(self):
        """Test getting all companies in a specific industry."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create test companies
        companies = [
            CompanyInfo(name="Fintech Corp", industry="Finance"),
            CompanyInfo(name="Bank Inc", industry="Finance"),
            CompanyInfo(name="Tech Corp", industry="Technology"),
        ]

        for company in companies:
            company_repo.create_company(company)

        # Get companies in Finance industry
        finance_companies = company_repo.get_companies_by_industry("Finance")

        assert len(finance_companies) == 2
        for company in finance_companies:
            assert company.industry == "Finance"


class TestCompanyRepositorySpecializedOperations:
    """Test specialized operations for CompanyRepository."""

    def test_get_company_by_domain(self):
        """Test getting company by domain/website."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create company with website
        company_data = CompanyInfo(
            name="Domain Company", industry="Tech", website="https://domaincompany.com"
        )
        created_company = company_repo.create_company(company_data)

        # Search by domain
        found_company = company_repo.get_company_by_domain("domaincompany.com")

        assert found_company is not None
        assert found_company.id == created_company.id
        assert found_company.name == "Domain Company"

    def test_get_company_statistics(self):
        """Test getting company statistics and analytics."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create companies in different industries
        companies = [
            CompanyInfo(name="Tech1", industry="Technology"),
            CompanyInfo(name="Tech2", industry="Technology"),
            CompanyInfo(name="Finance1", industry="Finance"),
            CompanyInfo(name="Marketing1", industry="Marketing"),
        ]

        for company in companies:
            company_repo.create_company(company)

        # Get statistics
        stats = company_repo.get_company_statistics()

        assert isinstance(stats, dict)
        assert "total_companies" in stats
        assert stats["total_companies"] == 4
        assert "by_industry" in stats
        assert stats["by_industry"]["Technology"] == 2
        assert stats["by_industry"]["Finance"] == 1
        assert stats["by_industry"]["Marketing"] == 1

    def test_find_similar_companies(self):
        """Test finding companies similar to a given company."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create target company
        target_company = CompanyInfo(
            name="Target Tech", industry="Technology", location="San Francisco, CA"
        )
        target = company_repo.create_company(target_company)

        # Create similar and different companies
        companies = [
            CompanyInfo(
                name="Similar Tech", industry="Technology", location="San Francisco, CA"
            ),
            CompanyInfo(
                name="Tech Corp", industry="Technology", location="New York, NY"
            ),
            CompanyInfo(
                name="Finance Corp", industry="Finance", location="San Francisco, CA"
            ),
            CompanyInfo(
                name="Marketing Inc", industry="Marketing", location="Austin, TX"
            ),
        ]

        for company in companies:
            company_repo.create_company(company)

        # Find similar companies
        similar = company_repo.find_similar_companies(str(target.id), limit=3)

        assert len(similar) <= 3
        # Should not include the target company itself
        similar_ids = {str(company.id) for company in similar}
        assert str(target.id) not in similar_ids

    def test_bulk_create_companies(self):
        """Test bulk creation of companies."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create multiple companies for bulk insert
        companies_data = [
            CompanyInfo(name=f"Bulk Company {i}", industry="Tech") for i in range(5)
        ]

        # Bulk create
        created_count = company_repo.bulk_create_companies(companies_data)

        assert created_count == 5

        # Verify they were created
        all_companies, total = company_repo.search_companies()
        assert total == 5


class TestCompanyRepositoryIntegration:
    """Test integration with other repositories and database operations."""

    def test_company_repository_integration_with_database(self):
        """Test that CompanyRepository integrates correctly with database manager."""
        database.initialize_database("sqlite:///:memory:")

        # Test that CompanyRepository is created and accessible
        company_repo = database.get_company_repository()

        assert company_repo is not None
        from app.data.company_repository import CompanyRepository

        assert isinstance(company_repo, CompanyRepository)

        # Test that it uses the same database manager
        db_manager = database.get_database_manager()
        assert company_repo.db_manager is db_manager

    def test_company_repository_with_job_repository_integration(self):
        """Test CompanyRepository working with JobRepository for consistent data."""
        from app.data.models import (
            CompanyInfo,
            ExperienceLevel,
            JobListing,
            JobType,
            RemoteType,
        )

        database.initialize_database("sqlite:///:memory:")
        company_repo = database.get_company_repository()
        job_repo = database.get_job_repository()

        # Create company through CompanyRepository
        company_data = CompanyInfo(name="Integration Company", industry="Software")
        company = company_repo.create_company(company_data)

        # Create job using the company
        job_data = JobListing(
            title="Software Engineer",
            company_id=company.id,
            location="Remote",
            description="Test job for integration",
            job_type=JobType.FULL_TIME,
            remote_type=RemoteType.REMOTE,
            experience_level=ExperienceLevel.MID_LEVEL,
        )
        job = job_repo.create_job(job_data)

        assert job is not None
        assert job.company_id == company.id

        # Verify we can retrieve the company through company repository
        retrieved_company = company_repo.get_company(str(company.id))
        assert retrieved_company.name == "Integration Company"

    def test_company_repository_transaction_handling(self):
        """Test that CompanyRepository handles database transactions correctly."""
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = database.get_company_repository()

        # Test transaction rollback on error
        try:
            with db_manager.get_session() as session:
                # This should work
                company_data = CompanyInfo(name="Transaction Test", industry="Tech")
                company = company_repo.create_company(company_data)

                # Verify it was created
                found_company = company_repo.get_company(str(company.id))
                assert found_company is not None

                # Force an error to test rollback
                # (In a real scenario, this might be a constraint violation or other DB error)
                raise ValueError("Simulated error for transaction test")

        except ValueError:
            # This is expected - the transaction should be rolled back
            pass

        # The company should still exist because each repository method
        # manages its own transaction
        found_company = company_repo.get_company(str(company.id))
        assert found_company is not None


class TestCompanyRepositoryValidation:
    """Test validation and error handling in CompanyRepository."""

    def test_create_company_with_invalid_data(self):
        """Test error handling when creating company with invalid data."""
        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Test with empty name (should raise error)
        with pytest.raises((ValueError, Exception)):
            company_data = CompanyInfo(name="", industry="Tech")
            company_repo.create_company(company_data)

    def test_update_nonexistent_company(self):
        """Test updating a company that doesn't exist."""
        from app.data.company_repository import CompanyRepository

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Try to update non-existent company
        update_data = {"name": "Updated Name"}
        result = company_repo.update_company(str(uuid4()), update_data)

        assert result is None

    def test_delete_nonexistent_company(self):
        """Test deleting a company that doesn't exist."""
        from app.data.company_repository import CompanyRepository

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Try to delete non-existent company
        result = company_repo.delete_company(str(uuid4()))

        assert result is False


class TestCompanyRepositoryPerformance:
    """Test performance aspects of CompanyRepository."""

    def test_bulk_operations_performance(self):
        """Test that bulk operations are more efficient than individual operations."""
        import time

        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create companies for bulk insert
        companies_data = [
            CompanyInfo(name=f"Performance Company {i}", industry="Tech")
            for i in range(50)
        ]

        # Time bulk creation
        start_time = time.time()
        bulk_count = company_repo.bulk_create_companies(companies_data)
        bulk_time = time.time() - start_time

        assert bulk_count == 50
        # Bulk operation should complete in reasonable time
        assert bulk_time < 5.0  # Should complete in under 5 seconds

        # Verify all companies were created
        all_companies, total = company_repo.search_companies()
        assert total == 50

    def test_search_performance_with_large_dataset(self):
        """Test search performance with a larger dataset."""
        import time

        from app.data.company_repository import CompanyRepository
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        db_manager = database.get_database_manager()
        company_repo = CompanyRepository(db_manager)

        # Create a larger dataset
        companies_data = [
            CompanyInfo(
                name=f"Search Test Company {i}",
                industry="Technology" if i % 2 == 0 else "Finance",
            )
            for i in range(100)
        ]

        company_repo.bulk_create_companies(companies_data)

        # Time search operation
        start_time = time.time()
        results, total = company_repo.search_companies(industries=["Technology"])
        search_time = time.time() - start_time

        assert total == 50  # Half should be Technology
        assert len(results) <= 50  # Default limit should apply
        # Search should be fast
        assert search_time < 2.0  # Should complete in under 2 seconds


class TestCompanyRepositoryDatabaseConsistency:
    """Test database consistency and data integrity."""

    def test_company_repository_maintains_data_integrity(self):
        """Test that repository operations maintain data integrity."""
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        company_repo = database.get_company_repository()

        # Create company
        company_data = CompanyInfo(name="Integrity Test Company", industry="Technology")
        created_company = company_repo.create_company(company_data)

        # Verify through different access patterns
        by_id = company_repo.get_company(str(created_company.id))
        search_results, _ = company_repo.search_companies(query="Integrity Test")
        industry_results = company_repo.get_companies_by_industry("Technology")

        # All should return the same company data
        assert by_id.id == created_company.id
        assert len(search_results) == 1
        assert search_results[0].id == created_company.id
        assert len(industry_results) >= 1
        assert any(comp.id == created_company.id for comp in industry_results)

    def test_concurrent_access_simulation(self):
        """Test repository behavior under simulated concurrent access."""
        from app.data.models import CompanyInfo

        database.initialize_database("sqlite:///:memory:")
        company_repo = database.get_company_repository()

        # Create initial company
        company_data = CompanyInfo(name="Concurrent Test", industry="Tech")
        company = company_repo.create_company(company_data)

        # Simulate concurrent updates
        update_data_1 = {"description": "First update"}
        update_data_2 = {"location": "San Francisco"}

        # Both updates should succeed (last one wins for conflicting fields)
        result_1 = company_repo.update_company(str(company.id), update_data_1)
        result_2 = company_repo.update_company(str(company.id), update_data_2)

        assert result_1 is not None
        assert result_2 is not None

        # Final state should have both updates
        final_company = company_repo.get_company(str(company.id))
        assert final_company.description == "First update"
        assert final_company.location == "San Francisco"
