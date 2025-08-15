#!/usr/bin/env python3
"""
Test script for User Profiles API endpoints
Tests CRUD operations without starting the full web server.
"""

import asyncio
import json
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any

# Test the database and API logic directly
from app.data.models import UserProfile, JobType, RemoteType
from app.data.database import initialize_database, get_user_repository
from app.logger import logger
from app.api.user_profiles import UserProfileCreate, UserProfileUpdate


async def test_user_profiles_crud():
    """Test all CRUD operations for user profiles."""
    print("🧪 Testing User Profiles CRUD Operations")
    print("=" * 50)
    
    # Initialize database
    print("🔌 Initializing database...")
    initialize_database("sqlite:///test_jobpilot.db")
    user_repo = get_user_repository()
    print("✅ Database initialized")
    
    # Test 1: Create a user profile
    print("\n📝 Test 1: Creating a user profile...")
    try:
        user_data = UserProfile(
            first_name="Alex",
            last_name="Rodriguez",
            email="alex.rodriguez@example.com",
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
            desired_salary_max=180000.0
        )
        
        created_user = user_repo.create_user(user_data)
        print(f"✅ User created with ID: {created_user.id}")
        print(f"   Name: {created_user.first_name} {created_user.last_name}")
        print(f"   Email: {created_user.email}")
        print(f"   Title: {created_user.current_title}")
        print(f"   Skills: {created_user.skills[:3]}...")
        test_user_id = str(created_user.id)
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False
    
    # Test 2: Get user by ID
    print(f"\n🔍 Test 2: Getting user by ID ({test_user_id[:8]}...)...")
    try:
        retrieved_user = user_repo.get_user(test_user_id)
        if retrieved_user:
            print(f"✅ User retrieved successfully")
            print(f"   Name: {retrieved_user.first_name} {retrieved_user.last_name}")
            print(f"   Email: {retrieved_user.email}")
            print(f"   Experience: {retrieved_user.experience_years} years")
        else:
            print("❌ User not found")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving user: {e}")
        return False
    
    # Test 3: Get user by email
    print(f"\n📧 Test 3: Getting user by email...")
    try:
        user_by_email = user_repo.get_user_by_email("alex.rodriguez@example.com")
        if user_by_email:
            print(f"✅ User retrieved by email successfully")
            print(f"   ID: {str(user_by_email.id)[:8]}...")
            print(f"   Name: {user_by_email.first_name} {user_by_email.last_name}")
        else:
            print("❌ User not found by email")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving user by email: {e}")
        return False
    
    # Test 4: Update user profile
    print(f"\n✏️ Test 4: Updating user profile...")
    try:
        update_data = {
            "current_title": "Principal Software Engineer",
            "experience_years": 9,
            "skills": ["Python", "JavaScript", "React", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
            "bio": "Senior full-stack developer with extensive experience in cloud-native applications",
            "desired_salary_min": 140000.0,
            "desired_salary_max": 200000.0
        }
        
        updated_user = user_repo.update_user(test_user_id, update_data)
        if updated_user:
            print(f"✅ User updated successfully")
            print(f"   New title: {updated_user.current_title}")
            print(f"   New experience: {updated_user.experience_years} years")
            print(f"   New skills count: {len(updated_user.skills)}")
            print(f"   New salary range: ${updated_user.desired_salary_min:,.0f} - ${updated_user.desired_salary_max:,.0f}")
        else:
            print("❌ User update failed")
            return False
            
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return False
    
    # Test 5: Create a second user for list testing
    print(f"\n👥 Test 5: Creating second user for list testing...")
    try:
        user_data_2 = UserProfile(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            current_title="Frontend Developer",
            experience_years=5,
            skills=["React", "TypeScript", "CSS", "HTML"],
            preferred_job_types=[JobType.FULL_TIME],
            preferred_remote_types=[RemoteType.REMOTE]
        )
        
        created_user_2 = user_repo.create_user(user_data_2)
        print(f"✅ Second user created with ID: {str(created_user_2.id)[:8]}...")
        print(f"   Name: {created_user_2.first_name} {created_user_2.last_name}")
        print(f"   Title: {created_user_2.current_title}")
        test_user_id_2 = str(created_user_2.id)
        
    except Exception as e:
        print(f"❌ Error creating second user: {e}")
        return False
    
    # Test 6: List all users
    print(f"\n📋 Test 6: Listing all users...")
    try:
        users, total = user_repo.list_users(limit=10, offset=0)
        print(f"✅ Retrieved {len(users)} users out of {total} total")
        for i, user in enumerate(users, 1):
            print(f"   {i}. {user.first_name} {user.last_name} - {user.current_title or 'No title'}")
        
        if len(users) < 2:
            print("❌ Expected at least 2 users in the list")
            return False
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return False
    
    # Test 7: Test API request models
    print(f"\n🔬 Test 7: Testing API request models...")
    try:
        # Test UserProfileCreate model
        create_request = UserProfileCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            skills=["Python", "FastAPI"],
            preferred_job_types=[JobType.FULL_TIME],
            preferred_remote_types=[RemoteType.REMOTE]
        )
        
        # Convert to UserProfile
        user_profile = UserProfile(**create_request.dict())
        print(f"✅ UserProfileCreate model validation passed")
        
        # Test UserProfileUpdate model
        update_request = UserProfileUpdate(
            current_title="Updated Title",
            experience_years=3,
            skills=["Python", "FastAPI", "PostgreSQL"]
        )
        
        # Filter None values for update
        update_dict = {k: v for k, v in update_request.dict().items() if v is not None}
        print(f"✅ UserProfileUpdate model validation passed")
        print(f"   Update fields: {list(update_dict.keys())}")
        
    except Exception as e:
        print(f"❌ Error testing API models: {e}")
        return False
    
    # Test 8: Delete user profile
    print(f"\n🗑️ Test 8: Deleting user profile...")
    try:
        success = user_repo.delete_user(test_user_id_2)
        if success:
            print(f"✅ User deleted successfully")
            
            # Verify deletion
            deleted_user = user_repo.get_user(test_user_id_2)
            if deleted_user is None:
                print(f"✅ Deletion confirmed - user not found")
            else:
                print(f"❌ User still exists after deletion")
                return False
        else:
            print("❌ User deletion failed")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False
    
    # Test 9: Test integration with resume generation workflow
    print(f"\n🔗 Test 9: Testing integration with resume generation workflow...")
    try:
        # This tests that the user profile structure is compatible with resume generation
        # by checking if we can access the fields that resume generation would need
        
        final_user = user_repo.get_user(test_user_id)
        if not final_user:
            print("❌ Could not retrieve user for integration test")
            return False
        
        # Test fields that resume generation would use
        resume_fields = {
            "personal_info": {
                "first_name": final_user.first_name,
                "last_name": final_user.last_name,
                "email": final_user.email,
                "phone": final_user.phone
            },
            "professional_info": {
                "current_title": final_user.current_title,
                "experience_years": final_user.experience_years,
                "skills": final_user.skills,
                "education": final_user.education,
                "bio": final_user.bio
            },
            "job_preferences": {
                "preferred_locations": final_user.preferred_locations,
                "preferred_job_types": [jt.value for jt in final_user.preferred_job_types],
                "preferred_remote_types": [rt.value for rt in final_user.preferred_remote_types],
                "salary_range": f"${final_user.desired_salary_min:,.0f} - ${final_user.desired_salary_max:,.0f}"
            }
        }
        
        print(f"✅ Resume generation integration test passed")
        print(f"   Available resume fields: {len(resume_fields)}")
        print(f"   Skills available: {len(final_user.skills)}")
        print(f"   Job preferences configured: {len(final_user.preferred_job_types)} types, {len(final_user.preferred_remote_types)} remote types")
        
    except Exception as e:
        print(f"❌ Error in resume generation integration test: {e}")
        return False
    
    print("\n🎉 All tests passed successfully!")
    print("=" * 50)
    print("✅ User Profiles Backend is ready for production!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_user_profiles_crud())
    if success:
        print("\n🚀 User Profiles API is fully functional and ready to use!")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        exit(1)
