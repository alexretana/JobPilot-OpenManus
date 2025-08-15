"""
Shared pytest configuration and fixtures for JobPilot-OpenManus testing.

This module configures custom markers and provides shared fixtures
that can be used across all test modules.
"""

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    # Register custom markers to avoid warnings
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
    config.addinivalue_line("markers", "database: marks tests as database tests")
    config.addinivalue_line("markers", "etl: marks tests as ETL pipeline tests")
    config.addinivalue_line("markers", "browser: marks tests as browser/UI tests")
    config.addinivalue_line("markers", "websocket: marks tests as WebSocket tests")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment before running any tests."""
    import os
    import sys

    # Ensure project root is in Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Set test mode environment variable
    os.environ["TEST_MODE"] = "true"

    yield

    # Cleanup after all tests
    if "TEST_MODE" in os.environ:
        del os.environ["TEST_MODE"]


@pytest.fixture
def temp_test_data():
    """Provide temporary test data that gets cleaned up."""
    test_data = {}

    yield test_data

    # Cleanup test data if needed
    test_data.clear()
