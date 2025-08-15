# End-to-End (E2E) Testing with Playwright

This directory contains comprehensive end-to-end tests for the JobPilot-OpenManus application using [Playwright](https://playwright.dev/).

## 📁 Directory Structure

```
tests/e2e/
├── README.md                   # This file
├── fixtures/
│   ├── test-fixtures.js       # Reusable test data and fixtures
│   └── auth-state.json        # Saved authentication state (generated)
├── pages/
│   ├── base-page.js           # Base page object with common functionality
│   ├── login-page.js          # Login page object model
│   ├── dashboard-page.js      # Dashboard page object model
│   └── jobs-page.js           # Jobs page object model
├── tests/
│   ├── auth.spec.js           # Authentication flow tests
│   ├── dashboard.spec.js      # Dashboard functionality tests
│   └── jobs.spec.js           # Jobs page functionality tests
└── utils/
    ├── global-setup.js        # Global test setup (authentication, data seeding)
    ├── global-teardown.js     # Global test cleanup
    └── test-helpers.js        # Common utility functions
```

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (v18+) and **npm** installed
2. **Python** (3.12+) with backend dependencies
3. **Frontend and backend servers** running or configured for auto-start

### Installation

1. Install npm dependencies:
   ```bash
   npm install
   ```

2. Install Playwright browsers:
   ```bash
   npx playwright install
   ```

### Running Tests

#### Using npm scripts (recommended):

```bash
# Run all E2E tests
npm run test:e2e

# Run with visible browser (headed mode)
npm run test:e2e:headed

# Run in debug mode (step through tests)
npm run test:e2e:debug

# Run both backend and E2E tests
npm run test:ci
```

#### Using the Python test runner:

```bash
# Run E2E tests via Python runner
python run_tests.py --e2e

# Run with visible browser
python run_tests.py --e2e --headed

# Run specific browser project
python run_tests.py --e2e --project chromium

# Run with debug mode
python run_tests.py --e2e --debug
```

#### Using Playwright directly:

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test auth.spec.js

# Run with UI mode
npx playwright test --ui

# Run specific project
npx playwright test --project chromium
```

## 🎭 Test Configuration

### Browser Support

Tests run on multiple browsers by default:
- **Chromium** (Chrome/Edge)
- **Firefox**
- **WebKit** (Safari)
- **Mobile Chrome** (Pixel 5 simulation)
- **Mobile Safari** (iPhone 12 simulation)

### Environment Variables

Set these environment variables for customization:

```bash
# Base URLs
BASE_URL=http://localhost:3000          # Frontend URL
BACKEND_URL=http://localhost:8000       # Backend API URL

# Test configuration
CI=true                                 # CI mode (affects retries, workers)
RAPIDAPI_KEY=your_key_here             # For API testing (optional)
INCLUDE_FRONTEND=true                   # Include frontend server startup
```

### Configuration File

The `playwright.config.js` file in the root directory contains:
- Test directory configuration
- Browser and device settings
- Reporting options
- Global setup/teardown
- Server startup configuration

## 📝 Writing Tests

### Page Object Model

We use the Page Object Model pattern for maintainable tests:

```javascript
// Example test using page objects
const { test, expect } = require('../fixtures/test-fixtures');

test('should login successfully', async ({ loginPage, dashboardPage }) => {
  await loginPage.navigate();
  await loginPage.loginAsTestUser();

  expect(await dashboardPage.isOnDashboard()).toBeTruthy();
});
```

### Test Fixtures

Use the extended test fixtures for common functionality:

```javascript
const { test, expect } = require('../fixtures/test-fixtures');

test('dashboard test', async ({
  page,           // Standard Playwright page
  loginPage,      // Login page object
  dashboardPage,  // Dashboard page object
  jobsPage,       // Jobs page object
  testUsers,      // Test user data
  testJobs        // Test job data
}) => {
  // Your test code here
});
```

### Helper Functions

Use test helpers for common operations:

```javascript
const { takeScreenshot, waitForNetworkIdle } = require('../utils/test-helpers');

test('example test', async ({ page }) => {
  await waitForNetworkIdle(page);
  await takeScreenshot(page, 'test-name', 'step-description');
});
```

## 📊 Test Reports

### HTML Reports

After running tests, view the HTML report:

```bash
npx playwright show-report
```

Reports include:
- Test results and timing
- Screenshots on failure
- Video recordings (on failure)
- Trace files for debugging

### Trace Viewer

For failed tests, view detailed traces:

```bash
npx playwright show-trace test-results/path-to-trace.zip
```

## 🐛 Debugging

### Debug Mode

Run tests in debug mode to step through:

```bash
npx playwright test --debug
```

### Visual Debugging

Use headed mode to see browser actions:

```bash
npx playwright test --headed
```

### Screenshots

Screenshots are automatically taken:
- On test failures
- At specific test steps (when using `takeScreenshot`)

### Video Recording

Videos are recorded for failed tests and stored in `test-reports/`.

## 🔧 Test Architecture

### Global Setup

The `global-setup.js` file handles:
- Server health checks
- Database setup and seeding
- Authentication state preparation
- Test data initialization

### Global Teardown

The `global-teardown.js` file handles:
- Test data cleanup
- Authentication state cleanup
- Resource cleanup

### Page Objects

Each page object extends `BasePage` and includes:
- Element selectors (with fallbacks)
- Page-specific actions
- Validation methods
- Error handling

### Test Data

Test data is managed through:
- **fixtures/test-fixtures.js**: Static test data
- **Global setup**: Dynamic data seeding
- **Environment variables**: Configuration

## 📈 Best Practices

### Test Organization

- Group related tests using `test.describe()`
- Use descriptive test names
- Keep tests focused and independent
- Use `beforeEach` for common setup

### Selectors

- Prefer `data-testid` attributes
- Include fallback selectors for flexibility
- Avoid brittle CSS selectors
- Use semantic selectors when possible

### Assertions

- Use Playwright's built-in assertions
- Include meaningful assertion messages
- Test both positive and negative cases
- Verify page state changes

### Error Handling

- Handle expected errors gracefully
- Include fallback behavior for optional elements
- Use try-catch for experimental features
- Log warnings for missing functionality

## 🚨 Troubleshooting

### Common Issues

**Tests fail with "Server not ready":**
- Ensure backend server is running on port 8000
- Check frontend server is running on port 3000
- Verify server health endpoints

**Playwright installation issues:**
- Run `npx playwright install` to install browsers
- For system dependencies: `npx playwright install-deps`

**Authentication failures:**
- Check test user credentials in fixtures
- Verify backend authentication endpoints
- Clear authentication state and re-run setup

**Element not found errors:**
- Verify data-testid attributes exist
- Check selector fallbacks
- Ensure page is fully loaded before interactions

### Environment-Specific Issues

**CI/CD:**
- Set `CI=true` environment variable
- Use headless mode
- Ensure adequate timeouts
- Configure proper server startup

**Local Development:**
- Use headed mode for debugging
- Check console output for server errors
- Verify port availability

## 🔄 Integration with CI/CD

### GitHub Actions

The tests are configured to run in GitHub Actions:

```yaml
- name: Run E2E Tests
  run: npm run test:ci
```

### Coverage Integration

E2E tests work with the overall coverage reporting:

```bash
python run_tests.py --all --cov
```

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Page Object Model](https://playwright.dev/docs/pom)
- [Debugging Tests](https://playwright.dev/docs/debugging)
