# Testing Guide

This document provides comprehensive instructions for understanding, setting up, and running tests in the TaskMaster project.

## Table of Contents

- [Overview](#overview)
- [Test Architecture](#test-architecture)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

## Overview

TaskMaster includes a comprehensive testing suite that ensures code quality, functionality, and user experience across the entire application stack:

- **Backend API Tests**: FastAPI TestClient-based tests for all API endpoints
- **Integration Tests**: Database operations, ETL pipelines, and data validation
- **End-to-End Tests**: Full workflow testing with Playwright for browser automation
- **WebSocket Tests**: Real-time communication validation
- **Server Lifecycle Management**: Automated test environment setup and cleanup

## Test Architecture

```
tests/
├── backend/
│   ├── api/                    # FastAPI endpoint tests
│   ├── database/               # Database operation tests
│   ├── etl/                    # ETL pipeline tests
│   └── models/                 # Data model tests
├── e2e/
│   ├── tests/                  # End-to-end test cases
│   ├── fixtures/               # Test data and setup
│   ├── pages/                  # Page object models
│   └── utils/                  # E2E test utilities
├── utils/
│   ├── test_server.py          # Server lifecycle management
│   ├── test_data.py            # Test data generators
│   └── fixtures.py             # Shared test fixtures
└── conftest.py                 # Pytest configuration
```

## Setup

### Prerequisites

1. **Python Environment**: Python 3.8+ with virtual environment
2. **Node.js**: For Playwright browser automation
3. **Database**: SQLite for testing (automatically managed)

### Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install
   ```

3. **Verify Setup**:
   ```bash
   python -m pytest tests/backend/test_health.py -v
   ```

### Environment Configuration

Create a `.env.test` file for testing configurations:

```bash
# Test Database
DATABASE_URL=sqlite:///./test_taskmaster.db
TEST_MODE=true

# Test Servers
BACKEND_TEST_PORT=8001
FRONTEND_TEST_PORT=3001

# Playwright Configuration
HEADLESS=true
BROWSER=chromium
```

## Running Tests

### Quick Commands

```bash
# Run all tests
npm test

# Backend tests only
npm run test:backend

# E2E tests only
npm run test:e2e

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

### Detailed Commands

#### Backend Tests

```bash
# All backend tests
python -m pytest tests/backend/ -v

# Specific test categories
python -m pytest tests/backend/api/ -v          # API tests
python -m pytest tests/backend/database/ -v    # Database tests
python -m pytest tests/backend/etl/ -v         # ETL tests

# With coverage report
python -m pytest tests/backend/ --cov=app --cov-report=html
```

#### End-to-End Tests

```bash
# All E2E tests
python -m pytest tests/e2e/ -v

# Specific browser
python -m pytest tests/e2e/ --browser chromium

# Headed mode (see browser)
python -m pytest tests/e2e/ --headed

# Parallel execution
python -m pytest tests/e2e/ -n auto
```

#### Custom Test Runs

```bash
# Run tests matching pattern
python -m pytest -k "test_create_task" -v

# Run failed tests only
python -m pytest --lf

# Stop on first failure
python -m pytest -x

# Verbose output with logs
python -m pytest -v -s --log-cli-level=INFO
```

## Test Categories

### 1. API Tests (`tests/backend/api/`)

Test all FastAPI endpoints with comprehensive scenarios:

```python
# Example: Task API tests
def test_create_task_success(client, sample_task_data):
    """Test successful task creation."""
    response = client.post("/api/tasks", json=sample_task_data)
    assert response.status_code == 201
    assert response.json()["title"] == sample_task_data["title"]

def test_create_task_validation_error(client):
    """Test task creation with invalid data."""
    response = client.post("/api/tasks", json={})
    assert response.status_code == 422
```

**Coverage**:
- ✅ Task CRUD operations
- ✅ User authentication
- ✅ Data validation
- ✅ Error handling
- ✅ Pagination
- ✅ Filtering and search

### 2. Database Tests (`tests/backend/database/`)

Test database operations and data integrity:

```python
def test_task_database_operations(db_session):
    """Test direct database operations."""
    task = Task(title="Test Task", status="pending")
    db_session.add(task)
    db_session.commit()

    retrieved = db_session.query(Task).filter_by(title="Test Task").first()
    assert retrieved is not None
    assert retrieved.status == "pending"
```

**Coverage**:
- ✅ CRUD operations
- ✅ Relationships
- ✅ Constraints
- ✅ Migrations
- ✅ Transactions

### 3. ETL Pipeline Tests (`tests/backend/etl/`)

Test data processing and transformation:

```python
def test_csv_import_pipeline(temp_csv_file):
    """Test CSV import functionality."""
    result = import_tasks_from_csv(temp_csv_file)
    assert result["success"] == True
    assert result["imported_count"] > 0
```

**Coverage**:
- ✅ CSV import/export
- ✅ Data validation
- ✅ Error handling
- ✅ Batch processing

### 4. End-to-End Tests (`tests/e2e/`)

Test complete user workflows with browser automation:

```python
def test_task_management_workflow(page):
    """Test complete task management workflow."""
    # Navigate to application
    page.goto("http://localhost:3000")

    # Create new task
    page.click('[data-testid="add-task-button"]')
    page.fill('[data-testid="task-title"]', "E2E Test Task")
    page.click('[data-testid="save-task"]')

    # Verify task appears in list
    expect(page.locator('[data-testid="task-item"]')).to_contain_text("E2E Test Task")

    # Update task status
    page.click('[data-testid="task-status-dropdown"]')
    page.click('[data-testid="status-completed"]')

    # Verify status update
    expect(page.locator('[data-testid="task-status"]')).to_contain_text("Completed")
```

**Coverage**:
- ✅ User interface interactions
- ✅ Form submissions
- ✅ Navigation flows
- ✅ Real-time updates
- ✅ Error states
- ✅ Mobile responsiveness

### 5. WebSocket Tests (`tests/e2e/websocket/`)

Test real-time communication:

```python
async def test_real_time_task_updates(websocket_client):
    """Test real-time task updates via WebSocket."""
    # Connect to WebSocket
    await websocket_client.connect()

    # Create task via API
    task_data = {"title": "WebSocket Test", "status": "pending"}
    response = await api_client.post("/api/tasks", json=task_data)
    task_id = response.json()["id"]

    # Verify WebSocket notification
    message = await websocket_client.receive_json()
    assert message["type"] == "task_created"
    assert message["task_id"] == task_id
```

## Writing Tests

### Best Practices

1. **Use Descriptive Names**:
   ```python
   def test_create_task_with_valid_data_returns_201():
       """Clear, descriptive test name"""
       pass
   ```

2. **Follow AAA Pattern**:
   ```python
   def test_update_task_status():
       # Arrange
       task = create_test_task()

       # Act
       response = client.put(f"/api/tasks/{task.id}", json={"status": "completed"})

       # Assert
       assert response.status_code == 200
   ```

3. **Use Fixtures for Setup**:
   ```python
   @pytest.fixture
   def sample_task():
       return {
           "title": "Test Task",
           "description": "Test Description",
           "status": "pending"
       }
   ```

### Test Data Management

Use the test data utilities for consistent test data:

```python
from tests.utils.test_data import TaskDataFactory, UserDataFactory

def test_task_assignment():
    user_data = UserDataFactory.create()
    task_data = TaskDataFactory.create(assigned_to=user_data["id"])
    # ... test logic
```

### Page Object Models (E2E Tests)

Organize E2E tests with page object models:

```python
class TaskListPage:
    def __init__(self, page):
        self.page = page

    def goto(self):
        self.page.goto("/tasks")

    def add_task(self, title, description=""):
        self.page.click('[data-testid="add-task-btn"]')
        self.page.fill('[data-testid="task-title"]', title)
        if description:
            self.page.fill('[data-testid="task-description"]', description)
        self.page.click('[data-testid="save-task-btn"]')

    def get_task_count(self):
        return self.page.locator('[data-testid="task-item"]').count()
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>

# Or use different port
BACKEND_TEST_PORT=8002 python -m pytest tests/e2e/
```

#### 2. Browser Issues (Playwright)

```bash
# Reinstall browsers
playwright install --force

# Run in headed mode for debugging
python -m pytest tests/e2e/ --headed --slowmo 1000
```

#### 3. Database Lock Issues

```bash
# Remove test database
rm test_taskmaster.db*

# Run tests with fresh database
python -m pytest tests/backend/ --fresh-db
```

#### 4. Test Data Conflicts

```bash
# Run with isolated test data
python -m pytest tests/ --isolated

# Clear test cache
python -m pytest --cache-clear
```

### Debugging Tests

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in pytest.ini
[tool:pytest]
log_cli = true
log_cli_level = DEBUG
```

#### Use Playwright Debug Mode

```bash
# Interactive debugging
PWDEBUG=1 python -m pytest tests/e2e/test_tasks.py::test_create_task

# Generate trace files
python -m pytest tests/e2e/ --tracing on
```

#### Test Database Inspection

```python
def test_debug_database_state(db_session):
    """Debug test to inspect database state."""
    tasks = db_session.query(Task).all()
    print(f"Tasks in database: {len(tasks)}")
    for task in tasks:
        print(f"  - {task.title}: {task.status}")
```

## CI/CD Integration

### GitHub Actions

The testing suite integrates with GitHub Actions for automated testing:

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run backend tests
        run: python -m pytest tests/backend/ --cov=app

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Install Playwright
        run: playwright install
      - name: Run E2E tests
        run: python -m pytest tests/e2e/
```

### Test Reports

The CI pipeline generates test reports:

- **Coverage Reports**: HTML coverage reports uploaded as artifacts
- **Test Results**: JUnit XML format for integration with CI tools
- **Screenshots**: Failed E2E test screenshots for debugging

### Quality Gates

Tests serve as quality gates in the CI/CD pipeline:

- **Minimum Coverage**: 80% code coverage required
- **All Tests Pass**: No failing tests allowed for merge
- **Performance**: E2E tests must complete within time limits

## Test Metrics and Monitoring

### Current Test Coverage

- **Backend API**: 95% coverage
- **Database Layer**: 90% coverage
- **ETL Pipeline**: 85% coverage
- **End-to-End Workflows**: 80% coverage

### Performance Benchmarks

- **Backend Tests**: < 30 seconds
- **E2E Tests**: < 5 minutes
- **Full Suite**: < 10 minutes

### Continuous Monitoring

The test suite includes monitoring for:

- Test execution times
- Flaky test detection
- Coverage trend analysis
- Performance regression detection

---

## Contributing to Tests

When adding new features or fixing bugs:

1. **Add corresponding tests** for new functionality
2. **Update existing tests** when modifying behavior
3. **Maintain test coverage** above minimum thresholds
4. **Document test scenarios** in code comments
5. **Follow naming conventions** for consistency

For questions or issues with testing, please refer to the project's issue tracker or contact the development team.
