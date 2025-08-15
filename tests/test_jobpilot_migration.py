#!/usr/bin/env python3
"""
JobPilot-OpenManus Migration Test Suite
Comprehensive testing of migrated components and new integrations.
"""

import asyncio
import os
import sys
import tempfile


# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.agent.job_discovery import JobDiscoveryAgent
from app.data.database import DatabaseManager, JobRepository, UserRepository
from app.data.models import (
    ExperienceLevel,
    JobListing,
    JobType,
    RemoteType,
    UserProfile,
)
from app.tool.job_scraper.job_scraper_tool import JobScraperTool
from app.tool.semantic_search.semantic_search_tool import SemanticSearchTool


class JobPilotMigrationTester:
    """Comprehensive test suite for JobPilot migration."""

    def __init__(self):
        """Initialize tester."""
        self.test_results = []
        self.temp_db_path = None
        self.db_manager = None
        self.job_repo = None
        self.user_repo = None

    def setup_test_database(self):
        """Set up temporary test database."""
        try:
            # Create temporary database
            temp_dir = tempfile.mkdtemp()
            self.temp_db_path = os.path.join(temp_dir, "test_jobpilot.db")
            database_url = f"sqlite:///{self.temp_db_path}"

            # Initialize database components
            self.db_manager = DatabaseManager(database_url)
            self.job_repo = JobRepository(self.db_manager)
            self.user_repo = UserRepository(self.db_manager)

            return True, "Test database initialized successfully"
        except Exception as e:
            return False, f"Database setup failed: {e}"

    def cleanup_test_database(self):
        """Clean up temporary test database."""
        try:
            if self.temp_db_path and os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
            return True, "Test database cleaned up"
        except Exception as e:
            return False, f"Database cleanup failed: {e}"

    def test_data_models(self) -> tuple[bool, str]:
        """Test JobPilot data models."""
        try:
            # Test JobListing model
            job_data = {
                "title": "Senior Python Developer",
                "company": "Test Company",
                "location": "San Francisco",
                "description": "Exciting Python development role",
                "requirements": "5+ years Python experience",
                "job_type": JobType.FULL_TIME,
                "remote_type": RemoteType.HYBRID,
                "experience_level": ExperienceLevel.SENIOR_LEVEL,
                "salary_min": 120000.0,
                "salary_max": 180000.0,
                "skills_required": ["Python", "Django", "PostgreSQL"],
                "skills_preferred": ["React", "AWS"],
                "benefits": ["Health Insurance", "401k", "Remote Work"],
            }

            job = JobListing(**job_data)
            assert job.title == "Senior Python Developer"
            assert job.job_type == JobType.FULL_TIME
            assert len(job.skills_required) == 3

            # Test UserProfile model
            user_data = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "current_title": "Software Developer",
                "experience_years": 5,
                "skills": ["Python", "JavaScript", "SQL"],
                "preferred_locations": ["San Francisco", "Remote"],
                "desired_salary_min": 100000.0,
                "desired_salary_max": 150000.0,
            }

            user = UserProfile(**user_data)
            assert user.email == "john.doe@example.com"
            assert len(user.skills) == 3

            return True, "Data models validation passed"

        except Exception as e:
            return False, f"Data models test failed: {e}"

    def test_database_operations(self) -> tuple[bool, str]:
        """Test database operations."""
        try:
            # Test database health check
            health = self.db_manager.health_check()
            if not health:
                return False, "Database health check failed"

            # Test job creation
            job_data = JobListing(
                title="Test Job",
                company="Test Company",
                location="Remote",
                job_type=JobType.FULL_TIME,
                remote_type=RemoteType.REMOTE,
                salary_min=80000.0,
                salary_max=120000.0,
                skills_required=["Python", "FastAPI"],
            )

            created_job = self.job_repo.create_job(job_data)
            assert created_job.title == "Test Job"

            # Test job retrieval
            retrieved_job = self.job_repo.get_job(str(created_job.id))
            assert retrieved_job is not None
            assert retrieved_job.title == "Test Job"

            # Test job search
            jobs, total = self.job_repo.search_jobs(query="Test", limit=10)
            assert len(jobs) >= 1
            assert total >= 1

            # Test recent jobs
            recent_jobs = self.job_repo.get_recent_jobs(limit=5)
            assert len(recent_jobs) >= 1

            # Test user creation
            user_data = UserProfile(
                email="test@example.com",
                first_name="Test",
                last_name="User",
                skills=["Python", "Testing"],
            )

            created_user = self.user_repo.create_user(user_data)
            assert created_user.email == "test@example.com"

            return True, f"Database operations passed - {len(recent_jobs)} jobs, 1 user"

        except Exception as e:
            return False, f"Database operations test failed: {e}"

    async def test_job_scraper_tool(self) -> tuple[bool, str]:
        """Test job scraper tool."""
        try:
            # Initialize job scraper with test database
            scraper = JobScraperTool()
            scraper.job_repo = self.job_repo

            # Test scraping
            result = await scraper._run(
                query="python developer",
                location="Remote",
                job_type="Full-time",
                max_results=5,
            )

            assert isinstance(result, str)
            assert "Successfully scraped" in result or "jobs" in result.lower()

            # Verify jobs were stored
            jobs = self.job_repo.get_recent_jobs(limit=10)
            assert len(jobs) > 0

            # Test scraper methods
            sources = scraper.get_available_sources()
            assert len(sources) > 0
            assert "demo_scraper" in sources

            locations = scraper.get_supported_locations()
            assert len(locations) > 0
            assert "Remote" in locations

            job_types = scraper.get_supported_job_types()
            assert len(job_types) > 0
            assert "Full-time" in job_types

            return True, f"Job scraper test passed - {result[:100]}..."

        except Exception as e:
            return False, f"Job scraper test failed: {e}"

    async def test_semantic_search_tool(self) -> tuple[bool, str]:
        """Test semantic search tool."""
        try:
            # Initialize semantic search with test database
            search_tool = SemanticSearchTool()
            search_tool.job_repo = self.job_repo

            # First, ensure we have some test jobs
            await self.test_job_scraper_tool()

            # Test semantic search
            result = await search_tool._run(
                query="python developer machine learning", max_results=5
            )

            assert isinstance(result, str)
            assert len(result) > 0

            # Test with filters
            filtered_result = await search_tool._run(
                query="software engineer",
                job_types="Full-time",
                remote_types="Remote",
                min_salary=50000,
                max_results=3,
            )

            assert isinstance(filtered_result, str)

            # Test model info
            model_info = search_tool.get_model_info()
            assert "model_name" in model_info
            assert "status" in model_info

            return (
                True,
                f"Semantic search test passed - Found results with both queries",
            )

        except Exception as e:
            return False, f"Semantic search test failed: {e}"

    async def test_job_discovery_agent(self) -> tuple[bool, str]:
        """Test job discovery agent."""
        try:
            # Initialize agent
            agent = JobDiscoveryAgent()
            agent.job_repo = self.job_repo

            # Test job discovery
            discovery_result = await agent.discover_jobs(
                query="data scientist", location="San Francisco", max_results=3
            )

            assert isinstance(discovery_result, dict)
            assert "query" in discovery_result
            assert discovery_result["query"] == "data scientist"

            # Test market analysis
            market_analysis = await agent.analyze_job_market()
            assert isinstance(market_analysis, dict)

            if "error" not in market_analysis:
                assert "total_jobs" in market_analysis
                assert "locations" in market_analysis
                assert "job_types" in market_analysis

            # Test company search
            company_jobs = await agent.search_company_jobs("Google")
            assert isinstance(company_jobs, list)

            return True, "Job discovery agent test passed"

        except Exception as e:
            return False, f"Job discovery agent test failed: {e}"

    def test_project_structure(self) -> tuple[bool, str]:
        """Test project structure and imports."""
        try:
            # Test critical imports
            pass

            # Check critical directories exist
            required_dirs = [
                "app/data",
                "app/tool/job_scraper",
                "app/tool/semantic_search",
                "app/agent",
                "tests",
            ]

            for dir_path in required_dirs:
                full_path = os.path.join(project_root, dir_path)
                if not os.path.exists(full_path):
                    return False, f"Required directory missing: {dir_path}"

            # Check critical files exist
            required_files = [
                "app/data/models.py",
                "app/data/database.py",
                "app/tool/job_scraper/job_scraper_tool.py",
                "app/tool/semantic_search/semantic_search_tool.py",
                "app/agent/job_discovery.py",
            ]

            for file_path in required_files:
                full_path = os.path.join(project_root, file_path)
                if not os.path.exists(full_path):
                    return False, f"Required file missing: {file_path}"

            return (
                True,
                f"Project structure validated - {len(required_dirs)} dirs, {len(required_files)} files",
            )

        except ImportError as e:
            return False, f"Import error in project structure: {e}"
        except Exception as e:
            return False, f"Project structure test failed: {e}"

    async def run_all_tests(self):
        """Run all tests and return results."""
        print("🚀 JobPilot-OpenManus Migration Test Suite")
        print("=" * 60)

        # Setup
        setup_success, setup_msg = self.setup_test_database()
        if not setup_success:
            print(f"❌ SETUP FAILED: {setup_msg}")
            return

        # Test cases
        test_cases = [
            ("Project Structure", self.test_project_structure),
            ("Data Models", self.test_data_models),
            ("Database Operations", self.test_database_operations),
            ("Job Scraper Tool", self.test_job_scraper_tool),
            ("Semantic Search Tool", self.test_semantic_search_tool),
            ("Job Discovery Agent", self.test_job_discovery_agent),
        ]

        results = []

        for test_name, test_func in test_cases:
            print(f"\n🔍 Running {test_name}...")

            try:
                if asyncio.iscoroutinefunction(test_func):
                    success, message = await test_func()
                else:
                    success, message = test_func()

                status = "✅ PASS" if success else "❌ FAIL"
                print(f"   {status} - {message}")
                results.append((test_name, success, message))

            except Exception as e:
                print(f"   ❌ FAIL - Unexpected error: {e}")
                results.append((test_name, False, f"Unexpected error: {e}"))

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY:")

        passed = sum(1 for _, success, _ in results if success)
        total = len(results)

        for test_name, success, message in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} - {test_name}")

        print(f"\n🎯 Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Migration is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")

        # Cleanup
        cleanup_success, cleanup_msg = self.cleanup_test_database()
        if not cleanup_success:
            print(f"⚠️  Cleanup warning: {cleanup_msg}")

        return results


async def main():
    """Run the test suite."""
    tester = JobPilotMigrationTester()
    results = await tester.run_all_tests()

    # Return exit code based on results
    if results:
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        return 0 if passed == total else 1
    return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
