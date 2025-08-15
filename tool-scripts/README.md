# Tool Scripts

This directory contains one-time utility scripts and legacy testing tools that were used during development but are not part of the main application workflow.

## Directory Structure

### `database/`
Database migration and setup utilities:
- `create_timeline_tables.py` - Creates timeline event tables (one-time migration)
- `migrate_database.py` - Migrates database schema to Phase 2 format

### `demos/`
Demo data generation scripts:
- `generate_demo_jobs.py` - Generates realistic demo jobs using the job scraper
- `simple_demo_jobs.py` - Creates simple demo jobs directly in database
- `jobpilot_demo.db` - Demo database file (if present)

### `legacy-tests/`
Legacy testing scripts (replaced by modern test suite in `tests/`):
- `setup_etl_test.py` - ETL system setup and testing
- `test_etl_system.py` - ETL system validation tests
- `test_etl_progress.py` - ETL progress and component tests
- `test_jsearch_api.py` - JSearch API connectivity test

## Usage Notes

- These scripts are preserved for reference and potential future use
- Most functionality has been integrated into the main application or proper test suite
- Run scripts from the project root directory to ensure proper Python path resolution
- Some scripts may require environment variables or API keys to function

## Migration to Modern Testing

The legacy tests in this directory have been superseded by:
- `tests/` - Comprehensive pytest-based test suite
- `run_tests.py` - Main test orchestrator in project root
- Playwright E2E tests with proper page object models
- CI/CD integration with GitHub Actions

For current testing, use `python run_tests.py --help` to see available options.
