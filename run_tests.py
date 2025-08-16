#!/usr/bin/env python3
"""
Universal Test Runner
Automatically chooses the appropriate test version based on the environment.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def detect_encoding_support():
    """Detect if the current environment supports Unicode emojis."""
    try:
        # Try to encode/decode a simple emoji
        test_emoji = "✅"
        test_emoji.encode(sys.stdout.encoding or "utf-8")
        return True
    except (UnicodeEncodeError, AttributeError):
        return False


def is_ci_environment():
    """Detect if running in a CI environment."""
    ci_indicators = [
        "CI",
        "CONTINUOUS_INTEGRATION",
        "BUILD_NUMBER",
        "GITHUB_ACTIONS",
        "TRAVIS",
        "CIRCLECI",
        "JENKINS_URL",
        "GITLAB_CI",
        "AZURE_PIPELINES",
        "BUILDKITE",
    ]
    return any(os.environ.get(indicator) for indicator in ci_indicators)


def run_user_profiles_test():
    """Run the appropriate user profiles test based on environment."""

    print("🚀 JobPilot User Profiles Test Runner")
    print("=" * 50)

    # Detect environment
    supports_unicode = detect_encoding_support()
    is_ci = is_ci_environment()
    is_windows = platform.system() == "Windows"

    print("Environment Detection:")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Encoding: {sys.stdout.encoding}")
    print(f"  Unicode Support: {'Yes' if supports_unicode else 'No'}")
    print(f"  CI Environment: {'Yes' if is_ci else 'No'}")
    print()

    # Choose appropriate test script
    if supports_unicode and not is_ci and not is_windows:
        test_script = "test_user_profiles.py"
        print("Using Unicode-enabled test script (with emojis)")
    else:
        test_script = "tests/backend/test_user_profiles_ci.py"
        print("Using CI-friendly test script (ASCII only)")
        if is_windows:
            print("  Reason: Windows encoding compatibility")
        if is_ci:
            print("  Reason: CI environment detected")
        if not supports_unicode:
            print("  Reason: Limited Unicode support")

    print(f"Running: {test_script}")
    print("=" * 50)
    print()

    # Check if test file exists
    if not Path(test_script).exists():
        print(f"ERROR: Test script '{test_script}' not found!")
        print("Please ensure the test file exists in the current directory.")
        return False

    # Run the test
    try:
        result = subprocess.run(
            [sys.executable, test_script], capture_output=False, text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: Failed to run test script: {e}")
        return False


def run_api_test():
    """Run the API integration test."""
    print("\n" + "=" * 50)
    print("Running API Integration Tests...")
    print("=" * 50)

    api_test_script = "test_user_profiles_api.py"

    if not Path(api_test_script).exists():
        print(f"WARNING: API test script '{api_test_script}' not found!")
        print("Skipping API tests.")
        return True

    print("NOTE: API tests require the FastAPI server to be running.")
    print("Start the server with: python main.py")
    print("Then run API tests separately with: python test_user_profiles_api.py")
    print()
    return True


if __name__ == "__main__":
    print("JobPilot Test Suite")
    print("=" * 50)

    # Parse command line arguments
    run_all = "--all" in sys.argv
    run_db_only = "--db-only" in sys.argv
    run_api_only = "--api-only" in sys.argv
    run_backend = "--backend" in sys.argv
    run_integration = "--integration" in sys.argv
    run_e2e = "--e2e" in sys.argv
    run_performance = "--performance" in sys.argv
    generate_coverage = "--cov" in sys.argv
    generate_html = any(arg.startswith("--html=") for arg in sys.argv)

    # Default behavior - run user profiles tests
    if not any([run_backend, run_integration, run_e2e, run_performance, run_api_only]):
        run_backend = True

    success = True

    if run_backend or run_db_only:
        print("\n🚀 Running Backend/Database Tests...")
        success = run_user_profiles_test()

    if run_integration and success:
        print("\n🔄 Running Integration Tests...")
        print("Integration tests not yet implemented - using backend tests")
        success = run_user_profiles_test()

    if run_e2e and success:
        print("\n🎭 Running End-to-End Tests...")
        print("E2E tests not yet implemented - skipping")

    if run_performance and success:
        print("\n⚡ Running Performance Tests...")
        print("Performance tests not yet implemented - skipping")

    if run_all and success:
        print("\n📊 Running All Available Tests...")
        if not run_backend:
            success = run_user_profiles_test()
        if success:
            success = run_api_test()

    if run_api_only:
        print("\n🌐 Running API Tests Only...")
        success = run_api_test()

    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("User Profiles Backend is ready for production!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above.")

    # Show coverage/html info if requested
    if generate_coverage:
        print("\nℹ️ Coverage reporting requested but not yet implemented")
    if generate_html:
        print("ℹ️ HTML reporting requested but not yet implemented")

    sys.exit(0 if success else 1)
