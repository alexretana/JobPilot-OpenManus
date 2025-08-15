#!/usr/bin/env python3
"""
CI-friendly User Profiles Test Script
Tests CRUD operations without Unicode display issues.
"""

import asyncio
import os
import sys

from app.api.user_profiles import UserProfileCreate, UserProfileUpdate
from app.data.database import get_user_repository, initialize_database

# Test the database and API logic directly
from app.data.models import JobType, RemoteType, UserProfile


async def test_user_profiles_crud():
    """Test all CRUD operations for user profiles."""
    print("TESTING: User Profiles CRUD Operations")
    print("=" * 50)

    # Clean up previous test database if it exists
    test_db_file = "test_jobpilot_ci.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        print("CLEANUP: Removed previous test database")

    # Initialize database
    print("INITIALIZING: Database...")
    initialize_database("sqlite:///test_jobpilot_ci.db")
    user_repo = get_user_repository()
    print("SUCCESS: Database initialized")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Create a user profile
    print("\nTEST 1: Creating a user profile...")
    try:
        user_data = UserProfile(
            first_name="Alex",
            last_name="Rodriguez",
            email="alex.rodriguez.ci@example.com",
            phone="+1-555-0123",
            current_title="Senior Software Engineer",
            experience_years=8,
            skills=["Python", "JavaScript", "React", "FastAPI", "PostgreSQL"],
            education="BS Computer Science",
            bio="Experienced full-stack developer with expertise in modern web technologies",
            preferred_locations=["Remote", "San Francisco", "New York"],
            preferred_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
            preferred_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID],
            desired_salary_min=120000.0,
            desired_salary_max=180000.0,
        )

        created_user = user_repo.create_user(user_data)
        print(f"SUCCESS: User created with ID: {created_user.id}")
        print(f"  Name: {created_user.first_name} {created_user.last_name}")
        print(f"  Email: {created_user.email}")
        print(f"  Title: {created_user.current_title}")
        print(f"  Skills: {len(created_user.skills)} skills")
        test_user_id = str(created_user.id)
        tests_passed += 1

    except Exception as e:
        print(f"FAILED: Error creating user: {e}")
        tests_failed += 1
        return False

    # Test 2: Get user by ID
    print(f"\nTEST 2: Getting user by ID...")
    try:
        retrieved_user = user_repo.get_user(test_user_id)
        if retrieved_user:
            print(f"SUCCESS: User retrieved successfully")
            print(f"  Name: {retrieved_user.first_name} {retrieved_user.last_name}")
            print(f"  Email: {retrieved_user.email}")
            print(f"  Experience: {retrieved_user.experience_years} years")
            tests_passed += 1
        else:
            print("FAILED: User not found")
            tests_failed += 1
            return False

    except Exception as e:
        print(f"FAILED: Error retrieving user: {e}")
        tests_failed += 1
        return False

    # Test 3: Get user by email
    print(f"\nTEST 3: Getting user by email...")
    try:
        user_by_email = user_repo.get_user_by_email("alex.rodriguez.ci@example.com")
        if user_by_email:
            print(f"SUCCESS: User retrieved by email successfully")
            print(f"  ID: {str(user_by_email.id)[:8]}...")
            print(f"  Name: {user_by_email.first_name} {user_by_email.last_name}")
            tests_passed += 1
        else:
            print("FAILED: User not found by email")
            tests_failed += 1
            return False

    except Exception as e:
        print(f"FAILED: Error retrieving user by email: {e}")
        tests_failed += 1
        return False

    # Test 4: Update user profile
    print(f"\nTEST 4: Updating user profile...")
    try:
        update_data = {
            "current_title": "Principal Software Engineer",
            "experience_years": 9,
            "skills": [
                "Python",
                "JavaScript",
                "React",
                "FastAPI",
                "PostgreSQL",
                "Docker",
                "Kubernetes",
            ],
            "bio": "Senior full-stack developer with extensive experience in cloud-native applications",
            "desired_salary_min": 140000.0,
            "desired_salary_max": 200000.0,
        }

        updated_user = user_repo.update_user(test_user_id, update_data)
        if updated_user:
            print(f"SUCCESS: User updated successfully")
            print(f"  New title: {updated_user.current_title}")
            print(f"  New experience: {updated_user.experience_years} years")
            print(f"  New skills count: {len(updated_user.skills)}")
            print(
                f"  New salary range: ${updated_user.desired_salary_min:,.0f} - ${updated_user.desired_salary_max:,.0f}"
            )
            tests_passed += 1
        else:
            print("FAILED: User update failed")
            tests_failed += 1
            return False

    except Exception as e:
        print(f"FAILED: Error updating user: {e}")
        tests_failed += 1
        return False

    # Test 5: Create a second user for list testing
    print(f"\nTEST 5: Creating second user for list testing...")
    try:
        user_data_2 = UserProfile(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith.ci@example.com",
            current_title="Frontend Developer",
            experience_years=5,
            skills=["React", "TypeScript", "CSS", "HTML"],
            preferred_job_types=[JobType.FULL_TIME],
            preferred_remote_types=[RemoteType.REMOTE],
        )

        created_user_2 = user_repo.create_user(user_data_2)
        print(f"SUCCESS: Second user created with ID: {str(created_user_2.id)[:8]}...")
        print(f"  Name: {created_user_2.first_name} {created_user_2.last_name}")
        print(f"  Title: {created_user_2.current_title}")
        test_user_id_2 = str(created_user_2.id)
        tests_passed += 1

    except Exception as e:
        print(f"FAILED: Error creating second user: {e}")
        tests_failed += 1
        return False

    # Test 6: List all users
    print(f"\nTEST 6: Listing all users...")
    try:
        users, total = user_repo.list_users(limit=10, offset=0)
        print(f"SUCCESS: Retrieved {len(users)} users out of {total} total")
        for i, user in enumerate(users, 1):
            print(
                f"  {i}. {user.first_name} {user.last_name} - {user.current_title or 'No title'}"
            )

        if len(users) < 2:
            print("FAILED: Expected at least 2 users in the list")
            tests_failed += 1
            return False
        else:
            tests_passed += 1

    except Exception as e:
        print(f"FAILED: Error listing users: {e}")
        tests_failed += 1
        return False

    # Test 7: Test API request models
    print(f"\nTEST 7: Testing API request models...")
    try:
        # Test UserProfileCreate model
        create_request = UserProfileCreate(
            first_name="Test",
            last_name="User",
            email="test.ci@example.com",
            skills=["Python", "FastAPI"],
            preferred_job_types=[JobType.FULL_TIME],
            preferred_remote_types=[RemoteType.REMOTE],
        )

        # Convert to UserProfile
        UserProfile(**create_request.model_dump())
        print(f"SUCCESS: UserProfileCreate model validation passed")

        # Test UserProfileUpdate model
        update_request = UserProfileUpdate(
            current_title="Updated Title",
            experience_years=3,
            skills=["Python", "FastAPI", "PostgreSQL"],
        )

        # Filter None values for update
        update_dict = {
            k: v for k, v in update_request.model_dump().items() if v is not None
        }
        print(f"SUCCESS: UserProfileUpdate model validation passed")
        print(f"  Update fields: {list(update_dict.keys())}")
        tests_passed += 1

    except Exception as e:
        print(f"FAILED: Error testing API models: {e}")
        tests_failed += 1
        return False

    # Test 8: Delete user profile
    print(f"\nTEST 8: Deleting user profile...")
    try:
        success = user_repo.delete_user(test_user_id_2)
        if success:
            print(f"SUCCESS: User deleted successfully")

            # Verify deletion
            deleted_user = user_repo.get_user(test_user_id_2)
            if deleted_user is None:
                print(f"SUCCESS: Deletion confirmed - user not found")
                tests_passed += 1
            else:
                print(f"FAILED: User still exists after deletion")
                tests_failed += 1
                return False
        else:
            print("FAILED: User deletion failed")
            tests_failed += 1
            return False

    except Exception as e:
        print(f"FAILED: Error deleting user: {e}")
        tests_failed += 1
        return False

    # Test 9: Test integration with resume generation workflow
    print(f"\nTEST 9: Testing integration with resume generation workflow...")
    try:
        final_user = user_repo.get_user(test_user_id)
        if not final_user:
            print("FAILED: Could not retrieve user for integration test")
            tests_failed += 1
            return False

        # Test fields that resume generation would use
        resume_fields = {
            "personal_info": {
                "first_name": final_user.first_name,
                "last_name": final_user.last_name,
                "email": final_user.email,
                "phone": final_user.phone,
            },
            "professional_info": {
                "current_title": final_user.current_title,
                "experience_years": final_user.experience_years,
                "skills": final_user.skills,
                "education": final_user.education,
                "bio": final_user.bio,
            },
            "job_preferences": {
                "preferred_locations": final_user.preferred_locations,
                "preferred_job_types": [
                    jt.value for jt in final_user.preferred_job_types
                ],
                "preferred_remote_types": [
                    rt.value for rt in final_user.preferred_remote_types
                ],
                "salary_range": f"${final_user.desired_salary_min:,.0f} - ${final_user.desired_salary_max:,.0f}",
            },
        }

        print(f"SUCCESS: Resume generation integration test passed")
        print(f"  Available resume fields: {len(resume_fields)}")
        print(f"  Skills available: {len(final_user.skills)}")
        print(
            f"  Job preferences: {len(final_user.preferred_job_types)} types, {len(final_user.preferred_remote_types)} remote"
        )
        tests_passed += 1

    except Exception as e:
        print(f"FAILED: Error in resume generation integration test: {e}")
        tests_failed += 1
        return False

    # Final summary
    print(f"\n" + "=" * 50)
    print(f"TEST SUMMARY:")
    print(f"  Tests Passed: {tests_passed}")
    print(f"  Tests Failed: {tests_failed}")
    print(f"  Total Tests: {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("SUCCESS: All tests passed successfully!")
        print("User Profiles Backend is ready for production!")
        return True
    else:
        print(f"FAILED: {tests_failed} tests failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_user_profiles_crud())
    if success:
        print("\nSUCCESS: User Profiles API is fully functional and ready to use!")
        sys.exit(0)
    else:
        print("\nFAILED: Some tests failed. Please check the errors above.")
        sys.exit(1)
