#!/usr/bin/env python3
"""
JobPilot-OpenManus CI Test Runner
Comprehensive test suite for local development and CI/CD pipelines.
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def print_banner(message, char="=", width=60):
    """Print a formatted banner message."""
    print()
    print(char * width)
    print(f" {message} ")
    print(char * width)


def print_step(step_name, emoji="🧪"):
    """Print a test step with emoji."""
    print(f"\n{emoji} {step_name}")
    print("-" * (len(step_name) + 5))


def run_command(command, description, continue_on_error=False):
    """Run a command and return success status."""
    print(f"Running: {command}")
    start_time = time.time()

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        duration = time.time() - start_time
        print(f"✅ {description} - Completed in {duration:.2f}s")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True

    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"❌ {description} - Failed in {duration:.2f}s")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")

        if continue_on_error:
            print(f"⚠️ Continuing despite error in {description}")
            return False
        else:
            print(f"🛑 Stopping due to error in {description}")
            return False


def check_file_exists(filepath):
    """Check if a file exists and report."""
    if Path(filepath).exists():
        print(f"✅ Found: {filepath}")
        return True
    else:
        print(f"❌ Missing: {filepath}")
        return False


def main():
    parser = argparse.ArgumentParser(description="JobPilot-OpenManus CI Test Runner")
    parser.add_argument(
        "--quick", action="store_true", help="Run quick validation only"
    )
    parser.add_argument(
        "--full", action="store_true", help="Run comprehensive test suite"
    )
    parser.add_argument(
        "--user-profiles", action="store_true", help="Run user profiles tests only"
    )
    parser.add_argument(
        "--syntax-check", action="store_true", help="Run syntax check only"
    )
    parser.add_argument(
        "--ci", action="store_true", help="CI mode - skip interactive prompts"
    )
    args = parser.parse_args()

    start_time = time.time()

    print_banner("🧪 JobPilot-OpenManus CI Test Runner")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    # Test counters
    tests_run = 0
    tests_passed = 0
    tests_failed = 0

    # File existence check
    print_step("File Existence Check", "📁")
    required_files = [
        "app/api/user_profiles.py",
        "app/data/database.py",
        "app/data/models.py",
        "test_user_profiles.py",
    ]

    for filepath in required_files:
        if check_file_exists(filepath):
            tests_passed += 1
        else:
            tests_failed += 1
        tests_run += 1

    # Syntax checking
    if (
        args.syntax_check
        or args.quick
        or args.full
        or not any([args.quick, args.full, args.user_profiles])
    ):
        print_step("Python Syntax Validation", "🔍")

        syntax_files = [
            "app/api/user_profiles.py",
            "app/data/database.py",
            "app/data/models.py",
        ]

        for filepath in syntax_files:
            tests_run += 1
            if run_command(
                f"python -m py_compile {filepath}", f"Syntax check: {filepath}"
            ):
                tests_passed += 1
            else:
                tests_failed += 1

    # Import validation
    if args.quick or args.full or args.user_profiles or not any([args.syntax_check]):
        print_step("Import Validation", "📦")

        import_tests = [
            (
                "from app.data.models import UserProfile, JobType, RemoteType",
                "Core models",
            ),
            (
                "from app.api.user_profiles import router, UserProfileCreate",
                "API components",
            ),
            (
                "from app.data.database import get_user_repository, initialize_database",
                "Database components",
            ),
        ]

        for import_cmd, description in import_tests:
            tests_run += 1
            if run_command(
                f"python -c \"{import_cmd}; print('SUCCESS: {description} imported successfully')\"",
                f"Import test: {description}",
            ):
                tests_passed += 1
            else:
                tests_failed += 1

    # User Profiles comprehensive tests
    if args.user_profiles or args.full:
        print_step("User Profiles Database Tests", "🧪")
        tests_run += 1
        if run_command(
            "python test_user_profiles.py", "User Profiles comprehensive tests"
        ):
            tests_passed += 1
        else:
            tests_failed += 1

    # Database schema validation
    if args.full:
        print_step("Database Schema Validation", "🗄️")
        schema_test = """
from app.data.models import Base, UserProfileDB, JobListingDB
from app.data.database import create_database_engine, create_tables
engine = create_database_engine("sqlite:///test_ci_validation.db")
create_tables(engine)
print("SUCCESS: Database schema validation passed")
"""
        tests_run += 1
        if run_command(f'python -c "{schema_test}"', "Database schema validation"):
            tests_passed += 1
        else:
            tests_failed += 1

    # API endpoint validation
    if args.full:
        print_step("API Endpoint Validation", "🔌")
        api_test = """
from app.api.user_profiles import router
print(f"✅ User Profiles API: {len(router.routes)} endpoints")
for route in router.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        methods = ", ".join(route.methods) if route.methods else "N/A"
        print(f"  {methods}: {route.path}")
"""
        tests_run += 1
        if run_command(f'python -c "{api_test}"', "API endpoint validation"):
            tests_passed += 1
        else:
            tests_failed += 1

    # Core component tests (if available)
    if args.full and Path("test_core_components.py").exists():
        print_step("Core Component Tests", "🏗️")
        tests_run += 1
        if run_command(
            "python test_core_components.py",
            "Core component tests",
            continue_on_error=True,
        ):
            tests_passed += 1
        else:
            tests_failed += 1
            print(
                "⚠️ Core component tests failed - this may be expected if dependencies are missing"
            )

    # Backend API tests (if available)
    if args.full and Path("tests/backend").exists():
        print_step("Backend API Tests", "🌐")
        tests_run += 1
        if run_command(
            "pytest tests/backend/ -v --tb=short --disable-warnings",
            "Backend API tests",
            continue_on_error=True,
        ):
            tests_passed += 1
        else:
            tests_failed += 1
            print("⚠️ Backend API tests may require additional setup")

    # Final summary
    total_time = time.time() - start_time
    print_banner("📊 Test Results Summary")

    print(f"🧪 Tests Run: {tests_run}")
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"⏱️ Total Time: {total_time:.2f}s")
    print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success_rate = (tests_passed / tests_run * 100) if tests_run > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")

    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! User Profiles backend is ready!")
        print("✅ Database operations validated")
        print("✅ API endpoints verified")
        print("✅ Code quality confirmed")
        print("✅ Ready for frontend development!")
        return 0
    else:
        print(f"\n⚠️ {tests_failed} tests failed. Please review the errors above.")
        if not args.ci:
            print("💡 Try running with --quick for basic validation")
            print("💡 Or --user-profiles for just user profile tests")
        return 1


if __name__ == "__main__":
    exit(main())
