"""
Test-Driven Development for Phase 6: Repository Layer Updates
Task 6.1: Update JobRepository Methods

This test file validates that the JobRepository works correctly with the new
company relationship structure instead of the old string-based company field.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.data.database import DatabaseManager, JobRepository
from app.data.models import (
    CompanyInfoDB,
    CompanySizeCategory,
    ExperienceLevel,
    JobListing,
    JobListingDB,
    JobStatus,
    JobType,
    RemoteType,
)


@pytest.fixture
def db_manager():
    """Create an in-memory test database."""
    db_manager = DatabaseManager("sqlite:///:memory:")
    return db_manager


@pytest.fixture
def job_repo(db_manager):
    """Create a JobRepository instance."""
    return JobRepository(db_manager)


@pytest.fixture
def sample_companies(db_manager):
    """Create sample companies for testing."""
    companies_data = [
        {
            "id": str(uuid4()),
            "name": "TechFlow Solutions",
            "normalized_name": "techflow solutions",
            "domain": "techflowsolutions.com",
            "industry": "Software Development",
            "size": "201-500 employees",
            "size_category": CompanySizeCategory.MEDIUM,
            "location": "San Francisco, CA",
            "website": "https://techflowsolutions.com",
            "founded_year": 2015,
            "description": "Leading provider of enterprise software solutions",
        },
        {
            "id": str(uuid4()),
            "name": "DataCore Analytics",
            "normalized_name": "datacore analytics",
            "domain": "datacore.io",
            "industry": "Data Analytics",
            "size": "51-200 employees",
            "size_category": CompanySizeCategory.SMALL,
            "location": "Seattle, WA",
            "website": "https://datacore.io",
            "founded_year": 2018,
            "description": "Advanced data analytics and machine learning platform",
        },
        {
            "id": str(uuid4()),
            "name": "CloudFirst Technologies",
            "normalized_name": "cloudfirst technologies",
            "domain": "cloudfirst.tech",
            "industry": "Cloud Computing",
            "size": "1001-5000 employees",
            "size_category": CompanySizeCategory.LARGE,
            "location": "Austin, TX",
            "website": "https://cloudfirst.tech",
            "founded_year": 2012,
            "description": "Enterprise cloud infrastructure solutions",
        },
    ]

    with db_manager.get_session() as session:
        companies = []
        for company_data in companies_data:
            company = CompanyInfoDB(**company_data)
            session.add(company)
            companies.append(company)
        session.flush()

        # Return list of company data for easy reference in tests
        return [(c.id, c.name, c.domain) for c in companies]


@pytest.fixture
def sample_jobs(db_manager, sample_companies):
    """Create sample jobs linked to companies."""
    company_ids = [c[0] for c in sample_companies]  # Extract company IDs

    jobs_data = [
        {
            "id": str(uuid4()),
            "title": "Senior Software Engineer",
            "company_id": company_ids[0],  # TechFlow Solutions
            "location": "San Francisco, CA",
            "description": "Build scalable web applications",
            "requirements": "5+ years experience in Python",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.HYBRID,
            "experience_level": ExperienceLevel.SENIOR_LEVEL,
            "salary_min": 120000,
            "salary_max": 180000,
            "status": JobStatus.ACTIVE,
            "posted_date": datetime.utcnow() - timedelta(days=5),
        },
        {
            "id": str(uuid4()),
            "title": "Data Scientist",
            "company_id": company_ids[1],  # DataCore Analytics
            "location": "Seattle, WA",
            "description": "Analyze complex datasets and build ML models",
            "requirements": "PhD in Statistics or related field",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.REMOTE,
            "experience_level": ExperienceLevel.SENIOR_LEVEL,
            "salary_min": 130000,
            "salary_max": 200000,
            "status": JobStatus.ACTIVE,
            "posted_date": datetime.utcnow() - timedelta(days=3),
        },
        {
            "id": str(uuid4()),
            "title": "DevOps Engineer",
            "company_id": company_ids[2],  # CloudFirst Technologies
            "location": "Austin, TX",
            "description": "Manage cloud infrastructure and CI/CD pipelines",
            "requirements": "Experience with AWS, Kubernetes, Docker",
            "job_type": JobType.CONTRACT,
            "remote_type": RemoteType.ON_SITE,
            "experience_level": ExperienceLevel.MID_LEVEL,
            "salary_min": 90000,
            "salary_max": 130000,
            "status": JobStatus.ACTIVE,
            "posted_date": datetime.utcnow() - timedelta(days=1),
        },
        {
            "id": str(uuid4()),
            "title": "Frontend Developer",
            "company_id": company_ids[0],  # TechFlow Solutions (second job)
            "location": "San Francisco, CA",
            "description": "Build beautiful user interfaces with React",
            "requirements": "3+ years React experience",
            "job_type": JobType.FULL_TIME,
            "remote_type": RemoteType.REMOTE,
            "experience_level": ExperienceLevel.MID_LEVEL,
            "salary_min": 100000,
            "salary_max": 140000,
            "status": JobStatus.ACTIVE,
            "posted_date": datetime.utcnow() - timedelta(days=7),
        },
    ]

    with db_manager.get_session() as session:
        jobs = []
        for job_data in jobs_data:
            job = JobListingDB(**job_data)
            session.add(job)
            jobs.append(job)
        session.flush()

        return [(j.id, j.title, j.company_id) for j in jobs]


class TestJobRepositoryCompanyIntegration:
    """Test JobRepository methods with company relationship integration."""

    def test_search_jobs_with_company_join_basic(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test that search_jobs can join with CompanyInfoDB and return results."""
        jobs, total_count = job_repo.search_jobs(limit=10)

        # Should return all active jobs
        assert len(jobs) == 4
        assert total_count == 4

        # Each job should have company information populated
        for job in jobs:
            assert job.company_id is not None
            assert job.company_name is not None  # Should be populated from relationship
            assert isinstance(job, JobListing)

    def test_search_jobs_filter_by_company_name(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test filtering jobs by company name using the new relationship."""
        # Search for jobs at "TechFlow Solutions"
        jobs, total_count = job_repo.search_jobs(
            companies=["TechFlow Solutions"], limit=10
        )

        # Should return 2 jobs (Senior Software Engineer + Frontend Developer)
        assert len(jobs) == 2
        assert total_count == 2

        # All jobs should be from TechFlow Solutions
        for job in jobs:
            assert job.company_name == "TechFlow Solutions"

    def test_search_jobs_filter_by_multiple_companies(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test filtering by multiple company names."""
        jobs, total_count = job_repo.search_jobs(
            companies=["TechFlow Solutions", "DataCore Analytics"], limit=10
        )

        # Should return 3 jobs (2 from TechFlow + 1 from DataCore)
        assert len(jobs) == 3
        assert total_count == 3

        # Verify company names
        company_names = {job.company_name for job in jobs}
        expected_names = {"TechFlow Solutions", "DataCore Analytics"}
        assert company_names == expected_names

    def test_search_jobs_text_search_includes_company_name(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test that text search can find jobs by company name."""
        jobs, total_count = job_repo.search_jobs(query="TechFlow", limit=10)

        # Should find jobs at TechFlow Solutions
        assert len(jobs) == 2
        assert total_count == 2

        for job in jobs:
            assert "TechFlow" in job.company_name

    def test_search_jobs_with_company_and_other_filters(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test combining company filter with other search filters."""
        jobs, total_count = job_repo.search_jobs(
            companies=["TechFlow Solutions"],
            job_types=[JobType.FULL_TIME],
            remote_types=[RemoteType.REMOTE],
            limit=10,
        )

        # Should return 1 job (Frontend Developer - full-time, remote, at TechFlow)
        assert len(jobs) == 1
        assert total_count == 1

        job = jobs[0]
        assert job.title == "Frontend Developer"
        assert job.company_name == "TechFlow Solutions"
        assert job.job_type == JobType.FULL_TIME
        assert job.remote_type == RemoteType.REMOTE

    def test_get_jobs_by_company_exact_match(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test getting jobs by exact company name match."""
        jobs = job_repo.get_jobs_by_company("TechFlow Solutions", limit=10)

        # Should return 2 jobs from TechFlow Solutions
        assert len(jobs) == 2

        # Verify all jobs are from the correct company
        for job in jobs:
            assert job.company_name == "TechFlow Solutions"

        # Should be ordered by creation date (newest first)
        assert jobs[0].created_at >= jobs[1].created_at

    def test_get_jobs_by_company_partial_match(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test getting jobs by partial company name match (case insensitive)."""
        jobs = job_repo.get_jobs_by_company("techflow", limit=10)

        # Should find TechFlow Solutions jobs (case insensitive)
        assert len(jobs) == 2

        for job in jobs:
            assert "TechFlow" in job.company_name

    def test_get_jobs_by_company_no_match(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test getting jobs by company name that doesn't exist."""
        jobs = job_repo.get_jobs_by_company("NonExistent Company", limit=10)

        # Should return empty list
        assert len(jobs) == 0

    def test_get_jobs_by_company_with_limit(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test that get_jobs_by_company respects the limit parameter."""
        jobs = job_repo.get_jobs_by_company("TechFlow Solutions", limit=1)

        # Should return only 1 job despite having 2 available
        assert len(jobs) == 1
        assert jobs[0].company_name == "TechFlow Solutions"

    def test_get_or_create_company_new_company(self, job_repo):
        """Test creating a new company when it doesn't exist."""
        company = job_repo.get_or_create_company(
            name="New Startup Inc", domain="newstartup.com"
        )

        assert company is not None
        assert company.name == "New Startup Inc"
        assert company.domain == "newstartup.com"
        assert (
            company.normalized_name == "new startup"
        )  # Should be normalized (inc removed)
        assert company.id is not None

    def test_get_or_create_company_existing_company(self, job_repo, sample_companies):
        """Test getting an existing company by name and domain."""
        # Try to create a company that already exists
        company = job_repo.get_or_create_company(
            name="TechFlow Solutions", domain="techflowsolutions.com"
        )

        # Should return the existing company, not create a duplicate
        assert company is not None
        assert company.name == "TechFlow Solutions"
        assert company.domain == "techflowsolutions.com"

        # Verify only one company with this name exists
        with job_repo.db_manager.get_session() as session:
            count = (
                session.query(CompanyInfoDB)
                .filter(CompanyInfoDB.name == "TechFlow Solutions")
                .count()
            )
            assert count == 1

    def test_get_or_create_company_fuzzy_matching(self, job_repo, sample_companies):
        """Test fuzzy matching for similar company names."""
        # Try variations of existing company name
        company = job_repo.get_or_create_company(
            name="TechFlow Solutions Inc",  # Slightly different name
            domain="techflowsolutions.com",  # Same domain
        )

        # Should match existing company based on domain
        assert company is not None
        assert company.name == "TechFlow Solutions"  # Should return original name
        assert company.domain == "techflowsolutions.com"

    def test_get_or_create_company_with_additional_fields(self, job_repo):
        """Test creating company with additional optional fields."""
        company = job_repo.get_or_create_company(
            name="Advanced Tech Corp",
            domain="advancedtech.com",
            industry="Artificial Intelligence",
            size_category=CompanySizeCategory.MEDIUM,
            founded_year=2020,
            description="AI-powered solutions company",
        )

        assert company.name == "Advanced Tech Corp"
        assert company.industry == "Artificial Intelligence"
        assert company.size_category == CompanySizeCategory.MEDIUM
        assert company.founded_year == 2020
        assert company.description == "AI-powered solutions company"


class TestJobRepositoryDataIntegrity:
    """Test data integrity and edge cases with company relationships."""

    def test_search_jobs_handles_missing_company_gracefully(
        self, job_repo, sample_companies
    ):
        """Test that search works correctly when jobs have invalid company_ids."""
        # This test ensures robustness - in practice this shouldn't happen due to foreign key constraints
        # But if it does, we expect the search to filter out invalid records (INNER JOIN behavior)
        with job_repo.db_manager.get_session() as session:
            # Create a job with a non-existent company_id
            invalid_job = JobListingDB(
                id=str(uuid4()),
                title="Test Job",
                company_id="non-existent-id",
                location="Test Location",
                description="Test Description",
                status=JobStatus.ACTIVE,
            )
            session.add(invalid_job)
            session.commit()

        # Search should still work and exclude jobs with invalid company references
        jobs, total_count = job_repo.search_jobs(limit=10)

        # Should NOT include the invalid job due to INNER JOIN with CompanyInfoDB
        # This is the expected behavior for data integrity
        assert (
            total_count == 0
        )  # No valid jobs with company relationships exist in this isolated test
        assert len(jobs) == 0

    def test_company_name_normalization_consistency(self, job_repo):
        """Test that company name normalization is consistent."""
        test_cases = [
            ("Microsoft Corp.", "microsoft"),  # Corp removed
            ("Google LLC", "google"),  # LLC removed
            ("Amazon.com Inc", "amazon com"),  # Inc removed and period removed
            ("Apple Inc.", "apple"),  # Inc removed
        ]

        for original_name, expected_normalized in test_cases:
            company = job_repo.get_or_create_company(
                name=original_name,
                domain=f"{expected_normalized.replace(' ', '').replace('.', '')}.com",
            )

            assert company.normalized_name == expected_normalized

    def test_search_performance_with_company_joins(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test that search performance is acceptable with company joins."""
        import time

        start_time = time.time()
        jobs, total_count = job_repo.search_jobs(
            query="software",
            companies=["TechFlow Solutions"],
            job_types=[JobType.FULL_TIME],
            limit=50,
        )
        end_time = time.time()

        # Search should complete in reasonable time (< 1 second for small dataset)
        assert (end_time - start_time) < 1.0

        # Results should be correct
        assert isinstance(jobs, list)
        assert isinstance(total_count, int)


class TestJobRepositoryErrorHandling:
    """Test error handling and edge cases."""

    def test_search_jobs_with_empty_company_list(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test search with empty company list."""
        jobs, total_count = job_repo.search_jobs(companies=[], limit=10)

        # Should return all jobs (empty list means no filter)
        assert len(jobs) == 4
        assert total_count == 4

    def test_search_jobs_with_none_company_filter(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test search with None company filter."""
        jobs, total_count = job_repo.search_jobs(companies=None, limit=10)

        # Should return all jobs (None means no filter)
        assert len(jobs) == 4
        assert total_count == 4

    def test_get_jobs_by_company_empty_string(
        self, job_repo, sample_companies, sample_jobs
    ):
        """Test get_jobs_by_company with empty string."""
        jobs = job_repo.get_jobs_by_company("", limit=10)

        # Should return empty list or handle gracefully
        assert isinstance(jobs, list)

    def test_get_or_create_company_invalid_input(self, job_repo):
        """Test get_or_create_company with invalid input."""
        with pytest.raises((ValueError, Exception)):
            # Should raise error for empty name
            job_repo.get_or_create_company(name="", domain="test.com")

    def test_get_or_create_company_without_domain(self, job_repo):
        """Test creating company without domain."""
        company = job_repo.get_or_create_company(name="Domain-less Company")

        assert company is not None
        assert company.name == "Domain-less Company"
        assert company.domain is None


# Test data setup validation
def test_sample_data_setup(sample_companies, sample_jobs):
    """Verify that test data is set up correctly."""
    assert len(sample_companies) == 3
    assert len(sample_jobs) == 4

    # Verify company data structure
    for company_id, company_name, domain in sample_companies:
        assert company_id is not None
        assert company_name is not None
        assert domain is not None

    # Verify job data structure
    for job_id, job_title, company_id in sample_jobs:
        assert job_id is not None
        assert job_title is not None
        assert company_id is not None
