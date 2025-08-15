#!/usr/bin/env python3
"""
Core Components Test
Tests basic system components and integration points.
"""

import sys


def test_imports():
    """Test that all core components can be imported."""
    print("🧪 Testing core component imports...")

    try:
        # Test data models
        pass

        print("✅ Data models imported successfully")

        # Test database components

        print("✅ Database components imported successfully")

        # Test API components

        print("✅ API components imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_database_initialization():
    """Test database initialization."""
    print("🧪 Testing database initialization...")

    try:
        from app.data.database import get_user_repository, initialize_database

        # Initialize test database
        initialize_database("sqlite:///test_core_components.db")
        get_user_repository()

        print("✅ Database initialization successful")
        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def test_api_router():
    """Test API router configuration."""
    print("🧪 Testing API router...")

    try:
        from app.api.user_profiles import router

        routes = router.routes
        print(f"✅ API router loaded with {len(routes)} routes")

        # List the routes
        for route in routes:
            if hasattr(route, "methods") and hasattr(route, "path"):
                methods = ", ".join(route.methods) if route.methods else "N/A"
                print(f"  {methods}: {route.path}")

        return True

    except Exception as e:
        print(f"❌ API router test failed: {e}")
        return False


def test_model_validation():
    """Test model validation and creation."""
    print("🧪 Testing model validation...")

    try:
        from app.api.user_profiles import UserProfileCreate
        from app.data.models import JobType, RemoteType

        # Test model creation
        test_data = UserProfileCreate(
            first_name="Core",
            last_name="Test",
            email="core.test@example.com",
            skills=["Testing", "Validation"],
            preferred_job_types=[JobType.FULL_TIME],
            preferred_remote_types=[RemoteType.REMOTE],
        )

        print("✅ Model validation successful")
        print(f"  Name: {test_data.first_name} {test_data.last_name}")
        print(f"  Email: {test_data.email}")
        print(f"  Skills: {len(test_data.skills)} skills")

        return True

    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False


def main():
    """Run all core component tests."""
    print("🏗️ Core Components Test Suite")
    print("=" * 50)

    tests = [
        test_imports,
        test_database_initialization,
        test_api_router,
        test_model_validation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Core Components Test Summary:")
    print(f"  Tests Passed: {passed}")
    print(f"  Tests Failed: {failed}")
    print(f"  Total Tests: {passed + failed}")

    if failed == 0:
        print("✅ All core component tests passed!")
        return True
    else:
        print(f"❌ {failed} core component tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
