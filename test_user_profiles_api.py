#!/usr/bin/env python3
"""
Test script for User Profiles API HTTP endpoints
Tests the actual FastAPI endpoints using HTTP requests.
"""

import requests


# Test data
test_user_data = {
    "first_name": "API",
    "last_name": "Test",
    "email": "api.test@example.com",
    "phone": "+1-555-9999",
    "current_title": "API Test Engineer",
    "experience_years": 5,
    "skills": ["Python", "FastAPI", "Testing", "HTTP"],
    "education": "BS Computer Science",
    "bio": "API testing specialist with experience in automated testing",
    "preferred_locations": ["Remote", "Silicon Valley"],
    "preferred_job_types": ["Full-time"],
    "preferred_remote_types": ["Remote"],
    "desired_salary_min": 100000.0,
    "desired_salary_max": 150000.0,
}


def test_user_profiles_api():
    """Test User Profiles API endpoints via HTTP."""
    print("🌐 Testing User Profiles API HTTP endpoints")
    print("=" * 50)

    base_url = "http://localhost:8080/api/users"
    created_user_id = None

    print("📱 Starting test server check...")
    try:
        # Test health endpoint first
        health_response = requests.get("http://localhost:8080/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print(f"⚠️ Server health check failed: {health_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print(
            "💡 Please start the server with: python web_server.py --host 0.0.0.0 --port 8080"
        )
        return False

    # Test 1: Create user profile
    print(f"\n📝 Test 1: Creating user profile via POST {base_url}")
    try:
        response = requests.post(base_url, json=test_user_data, timeout=10)
        if response.status_code == 201:
            user_data = response.json()
            created_user_id = user_data["id"]
            print(f"✅ User created successfully")
            print(f"   ID: {created_user_id[:8]}...")
            print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
            print(f"   Email: {user_data['email']}")
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    # Test 2: Get user by ID
    print(f"\n🔍 Test 2: Getting user by ID via GET {base_url}/{created_user_id[:8]}...")
    try:
        response = requests.get(f"{base_url}/{created_user_id}", timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User retrieved successfully")
            print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
            print(f"   Title: {user_data['current_title']}")
            print(f"   Skills: {len(user_data['skills'])} skills")
        else:
            print(f"❌ Failed to get user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    # Test 3: List users
    print(f"\n📋 Test 3: Listing users via GET {base_url}")
    try:
        response = requests.get(base_url, params={"limit": 10}, timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Users listed successfully")
            print(f"   Retrieved {len(users)} users")
            for i, user in enumerate(users[:3], 1):  # Show first 3
                print(
                    f"   {i}. {user['first_name']} {user['last_name']} - {user.get('current_title', 'No title')}"
                )
        else:
            print(f"❌ Failed to list users: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    # Test 4: Update user profile
    print(
        f"\n✏️ Test 4: Updating user profile via PUT {base_url}/{created_user_id[:8]}..."
    )
    update_data = {
        "current_title": "Senior API Test Engineer",
        "experience_years": 6,
        "skills": ["Python", "FastAPI", "Testing", "HTTP", "pytest", "Automation"],
    }
    try:
        response = requests.put(
            f"{base_url}/{created_user_id}", json=update_data, timeout=10
        )
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User updated successfully")
            print(f"   New title: {user_data['current_title']}")
            print(f"   New experience: {user_data['experience_years']} years")
            print(f"   New skills count: {len(user_data['skills'])}")
        else:
            print(f"❌ Failed to update user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    # Test 5: Search user by email
    print(f"\n📧 Test 5: Searching user by email via GET {base_url}/search/by-email")
    try:
        response = requests.get(
            f"{base_url}/search/by-email",
            params={"email": test_user_data["email"]},
            timeout=10,
        )
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User found by email successfully")
            print(f"   ID: {user_data['id'][:8]}...")
            print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
        else:
            print(f"❌ Failed to find user by email: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    # Test 6: Delete user profile
    print(
        f"\n🗑️ Test 6: Deleting user profile via DELETE {base_url}/{created_user_id[:8]}..."
    )
    try:
        response = requests.delete(f"{base_url}/{created_user_id}", timeout=10)
        if response.status_code == 204:
            print(f"✅ User deleted successfully")

            # Verify deletion
            verify_response = requests.get(f"{base_url}/{created_user_id}", timeout=10)
            if verify_response.status_code == 404:
                print(f"✅ Deletion confirmed - user not found")
            else:
                print(f"❌ User still exists after deletion")
                return False
        else:
            print(f"❌ Failed to delete user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    print("\n🎉 All API tests passed successfully!")
    print("=" * 50)
    print("✅ User Profiles API HTTP endpoints are working correctly!")
    return True


if __name__ == "__main__":
    success = test_user_profiles_api()
    if success:
        print("\n🚀 User Profiles API HTTP endpoints are fully functional!")
        exit(0)
    else:
        print("\n❌ Some API tests failed. Please check the errors above.")
        exit(1)
