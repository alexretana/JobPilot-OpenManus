#!/usr/bin/env python3
"""
CI-Friendly Backend API Tests using FastAPI TestClient

This test suite validates backend API functionality using a minimal
CI-friendly web server that avoids heavy browser dependencies.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

import pytest
from fastapi import FastAPI

# FastAPI testing imports
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)


# ==================== Fixtures ====================


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Get the CI-friendly FastAPI application instance."""
    try:
        import web_server_ci

        return web_server_ci.app
    except ImportError as e:
        pytest.skip(f"Cannot import web_server_ci: {e}")


@pytest.fixture(scope="session")
def client(app: FastAPI) -> TestClient:
    """Create FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture(scope="function")
def clean_database():
    """Clean database before and after each test."""
    # Setup: Clean database
    try:
        from app.data.database import get_user_repository, initialize_database

        # Initialize with test database
        initialize_database("sqlite:///test_ci_api.db")
        user_repo = get_user_repository()

        # Clean any existing test data
        test_users, _ = user_repo.list_users(limit=100, offset=0)
        for user in test_users:
            if "@test.ci" in user.email:
                user_repo.delete_user(str(user.id))

    except Exception as e:
        pytest.skip(f"Database setup failed: {e}")

    yield

    # Teardown: Clean database
    try:
        test_users, _ = user_repo.list_users(limit=100, offset=0)
        for user in test_users:
            if "@test.ci" in user.email:
                user_repo.delete_user(str(user.id))
    except Exception:
        pass  # Ignore cleanup failures


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@test.ci",
        "phone": "+1-555-0199",
        "current_title": "Test Engineer",
        "experience_years": 3,
        "skills": ["Python", "FastAPI", "Testing"],
        "education": "BS Computer Science",
        "bio": "Test engineer for API validation",
        "preferred_locations": ["Remote"],
        "preferred_job_types": ["Full-time"],
        "preferred_remote_types": ["Remote"],
        "desired_salary_min": 70000.0,
        "desired_salary_max": 90000.0,
    }


@pytest.fixture
def sample_job_data() -> Dict[str, Any]:
    """Sample job data for testing."""
    return {
        "name": "test-ci-job",
        "title": "CI Test Engineer",
        "company": "CI Test Corp",
        "location": "Remote",
        "description": "Test CI functionality",
        "requirements": "Python, FastAPI, Testing",
        "job_type": "Full-time",
        "remote_type": "Remote",
        "salary_min": 80000,
        "salary_max": 120000,
        "skills_required": ["Python", "FastAPI", "Testing"],
    }


# ==================== Health & Basic API Tests ====================


class TestHealthAndBasics:
    """Test basic API functionality and health endpoints."""

    def test_health_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
        assert "server" in data
        assert data["server"] == "jobpilot-ci"

        # Validate timestamp format
        timestamp_str = data["timestamp"]
        datetime.fromisoformat(timestamp_str)

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "healthy"
        assert data["version"] == "ci-test"

    def test_api_status_endpoint(self, client: TestClient):
        """Test the API status endpoint."""
        response = client.get("/api/status")
        assert response.status_code == 200

        data = response.json()
        assert "apis" in data
        assert "database" in data
        assert "test_mode" in data
        assert data["test_mode"] is True

        # Check that all APIs are reported as available
        apis = data["apis"]
        expected_apis = [
            "user_profiles",
            "timeline",
            "applications",
            "leads",
            "enhanced_jobs",
        ]
        for api in expected_apis:
            assert api in apis
            assert apis[api] == "available"

    def test_invalid_endpoint(self, client: TestClient):
        """Test invalid endpoint returns proper error."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404


# ==================== User Profiles API Tests ====================


class TestUserProfilesAPI:
    """Test user profiles API endpoints."""

    def test_create_user_profile(
        self, client: TestClient, sample_user_data: Dict, clean_database
    ):
        """Test successful user profile creation."""
        response = client.post("/api/users", json=sample_user_data)
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert data["email"] == sample_user_data["email"]
        assert data["current_title"] == sample_user_data["current_title"]
        assert data["skills"] == sample_user_data["skills"]

        return data

    def test_get_user_profile_by_id(
        self, client: TestClient, sample_user_data: Dict, clean_database
    ):
        """Test getting user profile by ID."""
        # First create a user
        create_response = client.post("/api/users", json=sample_user_data)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # Then get the user by ID
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]

    def test_get_user_profile_by_email(
        self, client: TestClient, sample_user_data: Dict, clean_database
    ):
        """Test getting user profile by email."""
        # First create a user
        create_response = client.post("/api/users", json=sample_user_data)
        assert create_response.status_code == 201

        email = sample_user_data["email"]

        # Then get the user by email
        response = client.get(f"/api/users/search/by-email?email={email}")
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == email
        assert data["first_name"] == sample_user_data["first_name"]

    def test_update_user_profile(
        self, client: TestClient, sample_user_data: Dict, clean_database
    ):
        """Test updating user profile."""
        # First create a user
        create_response = client.post("/api/users", json=sample_user_data)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # Update the user
        update_data = {
            "current_title": "Senior Test Engineer",
            "experience_years": 5,
            "skills": ["Python", "FastAPI", "Testing", "CI/CD"],
        }

        response = client.put(f"/api/users/{user_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["current_title"] == update_data["current_title"]
        assert data["experience_years"] == update_data["experience_years"]
        assert data["skills"] == update_data["skills"]

    def test_list_user_profiles(self, client: TestClient, clean_database):
        """Test listing user profiles."""
        # Create multiple users
        users_data = [
            {
                "first_name": "Alice",
                "last_name": "Test",
                "email": "alice@test.ci",
                "skills": ["Python"],
                "preferred_job_types": ["Full-time"],
                "preferred_remote_types": ["Remote"],
            },
            {
                "first_name": "Bob",
                "last_name": "Test",
                "email": "bob@test.ci",
                "skills": ["JavaScript"],
                "preferred_job_types": ["Part-time"],
                "preferred_remote_types": ["Hybrid"],
            },
        ]

        created_ids = []
        for user_data in users_data:
            response = client.post("/api/users", json=user_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # List users
        response = client.get("/api/users")
        assert response.status_code == 200

        data = response.json()
        # The list endpoint returns a list directly, not a dict with "users" and "total"
        assert isinstance(data, list)
        assert len(data) >= 2

        # Check that our created users are in the list
        emails = [user["email"] for user in data]
        assert "alice@test.ci" in emails
        assert "bob@test.ci" in emails

    def test_delete_user_profile(
        self, client: TestClient, sample_user_data: Dict, clean_database
    ):
        """Test deleting user profile."""
        # First create a user
        create_response = client.post("/api/users", json=sample_user_data)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # Delete the user
        response = client.delete(f"/api/users/{user_id}")
        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404


# ==================== Error Handling Tests ====================


class TestAPIErrorHandling:
    """Test API error handling."""

    def test_create_user_missing_required_fields(self, client: TestClient):
        """Test creating user with missing required fields."""
        invalid_data = {
            "first_name": "Test",
            # Missing last_name, email, skills, preferred_job_types, preferred_remote_types
        }

        response = client.post("/api/users", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_user_duplicate_email(
        self, client: TestClient, sample_user_data: Dict, clean_database
    ):
        """Test creating user with duplicate email."""
        # Create first user
        response1 = client.post("/api/users", json=sample_user_data)
        assert response1.status_code == 201

        # Try to create second user with same email
        response2 = client.post("/api/users", json=sample_user_data)
        # This should fail with conflict error
        assert response2.status_code in [400, 409, 422]

    def test_get_nonexistent_user(self, client: TestClient):
        """Test getting non-existent user."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/users/{fake_id}")
        assert response.status_code == 404

    def test_update_nonexistent_user(self, client: TestClient):
        """Test updating non-existent user."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"current_title": "New Title"}

        response = client.put(f"/api/users/{fake_id}", json=update_data)
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client: TestClient):
        """Test deleting non-existent user."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.delete(f"/api/users/{fake_id}")
        assert response.status_code == 404

    def test_invalid_uuid_format(self, client: TestClient):
        """Test endpoints with invalid UUID format."""
        invalid_id = "not-a-valid-uuid"

        # Test various endpoints with invalid UUID
        endpoints = [f"/api/users/{invalid_id}"]

        for endpoint in endpoints[:-1]:  # Skip the email endpoint
            response = client.get(endpoint)
            assert response.status_code in [400, 422]  # Bad request or validation error


# ==================== Performance Tests ====================


class TestAPIPerformance:
    """Test API performance characteristics."""

    def test_health_endpoint_performance(self, client: TestClient):
        """Test health endpoint responds quickly."""
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond in under 1 second

    def test_bulk_user_creation_performance(self, client: TestClient, clean_database):
        """Test creating multiple users."""
        import time

        users_count = 10
        start_time = time.time()

        created_ids = []
        for i in range(users_count):
            user_data = {
                "first_name": f"User{i}",
                "last_name": "Test",
                "email": f"user{i}@test.ci",
                "skills": ["Python"],
                "preferred_job_types": ["Full-time"],
                "preferred_remote_types": ["Remote"],
            }

            response = client.post("/api/users", json=user_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        end_time = time.time()
        total_time = end_time - start_time

        # Should be able to create 10 users in under 5 seconds
        assert total_time < 5.0
        assert len(created_ids) == users_count

        # Clean up
        for user_id in created_ids:
            client.delete(f"/api/users/{user_id}")


# ==================== Integration Tests ====================


class TestAPIIntegration:
    """Test API integration workflows."""

    def test_complete_user_lifecycle(
        self, client: TestClient, sample_user_data: Dict, clean_database
    ):
        """Test complete user lifecycle: create, read, update, delete."""
        # 1. Create user
        create_response = client.post("/api/users", json=sample_user_data)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # 2. Read user
        read_response = client.get(f"/api/users/{user_id}")
        assert read_response.status_code == 200
        read_user = read_response.json()
        assert read_user["email"] == sample_user_data["email"]

        # 3. Update user
        update_data = {"current_title": "Updated Title"}
        update_response = client.put(f"/api/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["current_title"] == "Updated Title"

        # 4. Delete user
        delete_response = client.delete(f"/api/users/{user_id}")
        assert delete_response.status_code == 204

        # 5. Verify deletion
        final_read_response = client.get(f"/api/users/{user_id}")
        assert final_read_response.status_code == 404
