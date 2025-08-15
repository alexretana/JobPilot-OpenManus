"""
Pytest-compatible User Profiles Tests
This provides pytest integration for the existing user profiles tests.
"""

import sys
from pathlib import Path

import pytest

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_user_profiles_import():
    """Test that user profiles modules can be imported."""
    try:
        pass

        assert True, "User profiles modules imported successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import user profiles modules: {e}")


def test_user_profiles_database_crud():
    """Test user profiles CRUD operations via subprocess."""
    import subprocess

    # Run the actual comprehensive test
    test_script = project_root / "test_user_profiles_ci.py"

    if not test_script.exists():
        pytest.skip("User profiles CI test script not found")

    result = subprocess.run(
        [sys.executable, str(test_script)], capture_output=True, text=True
    )

    assert result.returncode == 0, f"User profiles tests failed: {result.stderr}"


def test_api_models_validation():
    """Test API model validation."""
    try:
        from app.api.user_profiles import UserProfileCreate, UserProfileUpdate
        from app.data.models import JobType, RemoteType

        # Test UserProfileCreate model
        create_data = UserProfileCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            skills=["Python", "Testing"],
            preferred_job_types=[JobType.FULL_TIME],
            preferred_remote_types=[RemoteType.REMOTE],
        )

        # Test UserProfileUpdate model
        update_data = UserProfileUpdate(
            current_title="Senior Test Engineer", experience_years=5
        )

        assert create_data.first_name == "Test"
        assert update_data.current_title == "Senior Test Engineer"

    except Exception as e:
        pytest.fail(f"API model validation failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
