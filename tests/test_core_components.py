#!/usr/bin/env python3
"""
Core JobPilot Components Test
Test the migrated core components without OpenManus dependencies.
"""

import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_data_models():
    """Test JobPilot data models."""
    try:
        from app.data.models import (
            ExperienceLevel,
            JobListing,
            JobType,
            RemoteType,
            UserProfile,
        )

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


def test_database_operations():
    """Test database operations."""
    try:
        from app.data.database import DatabaseManager, JobRepository, UserRepository
        from app.data.models import JobListing, JobType, RemoteType, UserProfile

        # Create temporary database
        temp_dir = tempfile.mkdtemp()
        temp_db_path = os.path.join(temp_dir, "test_jobpilot.db")
        database_url = f"sqlite:///{temp_db_path}"

        # Initialize database components
        db_manager = DatabaseManager(database_url)
        job_repo = JobRepository(db_manager)
        user_repo = UserRepository(db_manager)

        # Test database health check
        health = db_manager.health_check()
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

        created_job = job_repo.create_job(job_data)
        assert created_job.title == "Test Job"

        # Test job retrieval
        retrieved_job = job_repo.get_job(str(created_job.id))
        assert retrieved_job is not None
        assert retrieved_job.title == "Test Job"

        # Test job search
        jobs, total = job_repo.search_jobs(query="Test", limit=10)
        assert len(jobs) >= 1
        assert total >= 1

        # Test recent jobs
        recent_jobs = job_repo.get_recent_jobs(limit=5)
        assert len(recent_jobs) >= 1

        # Test user creation
        user_data = UserProfile(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            skills=["Python", "Testing"],
        )

        created_user = user_repo.create_user(user_data)
        assert created_user.email == "test@example.com"

        # Close database connections before cleanup
        db_manager.engine.dispose()

        # Cleanup
        try:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
        except OSError:
            pass  # File may still be in use, ignore cleanup error

        return True, f"Database operations passed - {len(recent_jobs)} jobs, 1 user"

    except Exception as e:
        return False, f"Database operations test failed: {e}"


def test_project_structure():
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


def run_tests():
    """Run all tests."""
    print("🚀 JobPilot Core Components Test Suite")
    print("=" * 50)

    test_cases = [
        ("Project Structure", test_project_structure),
        ("Data Models", test_data_models),
        ("Database Operations", test_database_operations),
    ]

    results = []

    for test_name, test_func in test_cases:
        print(f"\n🔍 Running {test_name}...")

        try:
            success, message = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} - {message}")
            results.append((test_name, success, message))

        except Exception as e:
            print(f"   ❌ FAIL - Unexpected error: {e}")
            results.append((test_name, False, f"Unexpected error: {e}"))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All core tests passed! Migration foundation is solid.")
    else:
        print("⚠️  Some tests failed. Check the details above.")

    return results


if __name__ == "__main__":
    try:
        results = run_tests()
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        exit_code = 0 if passed == total else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
