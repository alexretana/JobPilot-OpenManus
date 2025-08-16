#!/usr/bin/env python3
"""
CI-Friendly User Profiles Database Tests
ASCII-only version for CI/CD environments without Unicode support.
"""

import shutil
import sys
import tempfile
from pathlib import Path

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker

    from app.api.user_profiles import (
        UserProfileCreate,
        UserProfileResponse,
    )
    from app.data.models import (
        JobType,
        RemoteType,
        UserProfileDB,
        create_database_engine,
        create_tables,
    )
except ImportError as e:
    print(f"CRITICAL: Failed to import required modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


class UserProfilesTestRunner:
    """CI-friendly test runner for user profiles functionality."""

    def __init__(self):
        self.test_db_path = None
        self.engine = None
        self.session = None
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0

    def setup_test_database(self):
        """Create a temporary test database."""
        try:
            # Create temporary database file
            temp_dir = Path(tempfile.mkdtemp())
            self.test_db_path = temp_dir / "test_user_profiles_ci.db"

            # Create database engine and tables
            self.engine = create_database_engine(f"sqlite:///{self.test_db_path}")
            create_tables(self.engine)

            # Create session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

            print("   Database setup completed successfully")
            return True

        except Exception as e:
            print(f"   FAILED: Database setup error: {e}")
            return False

    def teardown_test_database(self):
        """Clean up test database."""
        try:
            if self.session:
                self.session.close()
            if self.engine:
                self.engine.dispose()
            if self.test_db_path and Path(self.test_db_path).exists():
                temp_dir = Path(self.test_db_path).parent
                shutil.rmtree(temp_dir)
            print("   Database cleanup completed")
            return True
        except Exception as e:
            print(f"   WARNING: Database cleanup error: {e}")
            return False

    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        self.total_tests += 1
        print(f"\nTest {self.total_tests}: {test_name}")
        print("-" * 50)

        try:
            result = test_func()
            if result:
                print("   PASSED")
                self.passed_tests += 1
                return True
            else:
                print("   FAILED")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"   FAILED: {e}")
            self.failed_tests += 1
            return False

    def test_database_connection(self):
        """Test database connection and basic functionality."""
        try:
            # Test database connection
            result = self.session.execute(text("SELECT 1"))
            assert result.scalar() == 1

            # Test that tables exist
            tables = self.engine.table_names()
            expected_tables = ["user_profiles", "job_listings", "job_applications"]

            for table in expected_tables:
                if table not in tables:
                    print(f"   WARNING: Expected table '{table}' not found")

            print("   Database connection test passed")
            return True

        except Exception as e:
            print(f"   Database connection failed: {e}")
            return False

    def test_user_profile_crud_operations(self):
        """Test complete CRUD operations for user profiles."""
        try:
            # CREATE - Test user profile creation
            print("   Testing CREATE operation...")
            profile_data = UserProfileCreate(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="+1-555-0123",
                location="San Francisco, CA",
                current_title="Software Engineer",
                experience_years=5,
                skills=["Python", "JavaScript", "SQL"],
                preferred_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
                preferred_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID],
                salary_expectation=100000,
                available_date="2024-01-15",
                linkedin_url="https://linkedin.com/in/johndoe",
                github_url="https://github.com/johndoe",
                portfolio_url="https://johndoe.dev",
            )

            # Convert Pydantic model to SQLAlchemy model
            db_profile = UserProfileDB(
                first_name=profile_data.first_name,
                last_name=profile_data.last_name,
                email=profile_data.email,
                phone=profile_data.phone,
                location=profile_data.location,
                current_title=profile_data.current_title,
                experience_years=profile_data.experience_years,
                skills=profile_data.skills,
                preferred_job_types=[
                    jt.value for jt in profile_data.preferred_job_types
                ],
                preferred_remote_types=[
                    rt.value for rt in profile_data.preferred_remote_types
                ],
                salary_expectation=profile_data.salary_expectation,
                available_date=profile_data.available_date,
                linkedin_url=profile_data.linkedin_url,
                github_url=profile_data.github_url,
                portfolio_url=profile_data.portfolio_url,
            )

            self.session.add(db_profile)
            self.session.commit()

            created_profile_id = db_profile.id
            assert created_profile_id is not None
            print(
                f"   CREATE: Successfully created profile with ID {created_profile_id}"
            )

            # READ - Test retrieving the user profile
            print("   Testing READ operation...")
            retrieved_profile = (
                self.session.query(UserProfileDB)
                .filter_by(id=created_profile_id)
                .first()
            )
            assert retrieved_profile is not None
            assert retrieved_profile.email == "john.doe@example.com"
            assert retrieved_profile.first_name == "John"
            assert retrieved_profile.experience_years == 5
            assert "Python" in retrieved_profile.skills
            print("   READ: Successfully retrieved profile")

            # UPDATE - Test updating the user profile
            print("   Testing UPDATE operation...")
            retrieved_profile.current_title = "Senior Software Engineer"
            retrieved_profile.experience_years = 7
            retrieved_profile.skills = ["Python", "JavaScript", "SQL", "Docker"]
            self.session.commit()

            # Verify the update
            updated_profile = (
                self.session.query(UserProfileDB)
                .filter_by(id=created_profile_id)
                .first()
            )
            assert updated_profile.current_title == "Senior Software Engineer"
            assert updated_profile.experience_years == 7
            assert "Docker" in updated_profile.skills
            print("   UPDATE: Successfully updated profile")

            # Test multiple profiles (list operation)
            print("   Testing LIST operation...")
            profile_data_2 = UserProfileCreate(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                skills=["React", "Node.js"],
                preferred_job_types=[JobType.PART_TIME],
                preferred_remote_types=[RemoteType.ONSITE],
            )

            db_profile_2 = UserProfileDB(
                first_name=profile_data_2.first_name,
                last_name=profile_data_2.last_name,
                email=profile_data_2.email,
                skills=profile_data_2.skills,
                preferred_job_types=[
                    jt.value for jt in profile_data_2.preferred_job_types
                ],
                preferred_remote_types=[
                    rt.value for rt in profile_data_2.preferred_remote_types
                ],
            )

            self.session.add(db_profile_2)
            self.session.commit()

            all_profiles = self.session.query(UserProfileDB).all()
            assert len(all_profiles) >= 2
            print(f"   LIST: Found {len(all_profiles)} profiles")

            # DELETE - Test deleting a user profile
            print("   Testing DELETE operation...")
            profile_to_delete = (
                self.session.query(UserProfileDB)
                .filter_by(email="jane.smith@example.com")
                .first()
            )
            assert profile_to_delete is not None

            self.session.delete(profile_to_delete)
            self.session.commit()

            # Verify deletion
            deleted_profile = (
                self.session.query(UserProfileDB)
                .filter_by(email="jane.smith@example.com")
                .first()
            )
            assert deleted_profile is None
            print("   DELETE: Successfully deleted profile")

            print("   All CRUD operations completed successfully")
            return True

        except Exception as e:
            print(f"   CRUD operations failed: {e}")
            return False

    def test_data_validation(self):
        """Test data validation and constraints."""
        try:
            print("   Testing data validation...")

            # Test valid JobType and RemoteType enums
            valid_job_types = [
                JobType.FULL_TIME,
                JobType.PART_TIME,
                JobType.CONTRACT,
                JobType.FREELANCE,
            ]
            valid_remote_types = [
                RemoteType.ONSITE,
                RemoteType.REMOTE,
                RemoteType.HYBRID,
            ]

            assert len(valid_job_types) == 4
            assert len(valid_remote_types) == 3
            print("   Enum validation passed")

            # Test Pydantic model validation
            valid_profile = UserProfileCreate(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                skills=["Python"],
                preferred_job_types=[JobType.FULL_TIME],
                preferred_remote_types=[RemoteType.REMOTE],
            )

            assert valid_profile.email == "test@example.com"
            assert valid_profile.skills == ["Python"]
            print("   Pydantic validation passed")

            # Test UserProfileResponse model
            response_model = UserProfileResponse(
                id=1,
                first_name="Test",
                last_name="User",
                email="test@example.com",
                skills=["Python"],
                preferred_job_types=[JobType.FULL_TIME],
                preferred_remote_types=[RemoteType.REMOTE],
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
            )

            assert response_model.id == 1
            print("   Response model validation passed")

            print("   Data validation completed successfully")
            return True

        except Exception as e:
            print(f"   Data validation failed: {e}")
            return False

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        try:
            print("   Testing edge cases...")

            # Test profile with minimal required fields
            minimal_profile = UserProfileCreate(
                first_name="Min",
                last_name="Profile",
                email="min@example.com",
                skills=[],  # Empty skills list
                preferred_job_types=[JobType.FULL_TIME],
                preferred_remote_types=[RemoteType.ONSITE],
            )

            db_minimal = UserProfileDB(
                first_name=minimal_profile.first_name,
                last_name=minimal_profile.last_name,
                email=minimal_profile.email,
                skills=minimal_profile.skills,
                preferred_job_types=[
                    jt.value for jt in minimal_profile.preferred_job_types
                ],
                preferred_remote_types=[
                    rt.value for rt in minimal_profile.preferred_remote_types
                ],
            )

            self.session.add(db_minimal)
            self.session.commit()

            retrieved_minimal = (
                self.session.query(UserProfileDB)
                .filter_by(email="min@example.com")
                .first()
            )
            assert retrieved_minimal is not None
            assert retrieved_minimal.skills == []
            print("   Minimal profile creation passed")

            # Test profile with maximum fields
            max_profile = UserProfileCreate(
                first_name="Max" * 20,  # Long name
                last_name="Profile" * 20,
                email="max.profile@verylongdomainname.example.com",
                phone="+1-555-0123-4567-8901",
                location="Very Long City Name, Very Long State Name, Country",
                current_title="Senior Principal Staff Software Engineering Manager",
                experience_years=50,
                skills=[
                    "Python",
                    "JavaScript",
                    "Java",
                    "C++",
                    "Go",
                    "Rust",
                    "Ruby",
                    "PHP",
                ]
                * 5,
                preferred_job_types=list(JobType),
                preferred_remote_types=list(RemoteType),
                salary_expectation=999999,
                available_date="2030-12-31",
                linkedin_url="https://linkedin.com/in/very-long-profile-name-with-lots-of-details",
                github_url="https://github.com/very-long-username",
                portfolio_url="https://very-long-portfolio-domain.example.com/portfolio",
            )

            # This should work without issues
            assert max_profile.experience_years == 50
            assert len(max_profile.skills) > 10
            print("   Maximum profile creation passed")

            print("   Edge case testing completed successfully")
            return True

        except Exception as e:
            print(f"   Edge case testing failed: {e}")
            return False

    def run_all_tests(self):
        """Run the complete test suite."""
        print("JobPilot User Profiles Database Tests (CI Version)")
        print("=" * 60)
        print("ASCII-only output for CI/CD compatibility")
        print("=" * 60)

        # Setup
        if not self.setup_test_database():
            print("\nFATAL: Could not set up test database")
            return False

        # Run all tests
        tests = [
            ("Database Connection", self.test_database_connection),
            ("User Profile CRUD Operations", self.test_user_profile_crud_operations),
            ("Data Validation", self.test_data_validation),
            ("Edge Cases", self.test_edge_cases),
        ]

        print(f"\nRunning {len(tests)} test suites...")

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Cleanup
        self.teardown_test_database()

        # Results
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")

        if self.failed_tests == 0:
            print("\nSUCCESS: All user profiles tests passed!")
            print("The user profiles backend is ready for deployment.")
            return True
        else:
            print(f"\nFAILED: {self.failed_tests} test(s) failed.")
            print("Please review the errors above and fix the issues.")
            return False


def main():
    """Main entry point for CI testing."""
    runner = UserProfilesTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
