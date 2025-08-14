/**
 * E2E Test Fixtures
 * Provides reusable test data and fixtures for Playwright E2E tests
 */

const { test: base, expect } = require('@playwright/test');
const LoginPage = require('../pages/login-page');
const DashboardPage = require('../pages/dashboard-page');
const JobsPage = require('../pages/jobs-page');

/**
 * Test users for authentication testing
 */
const TEST_USERS = {
  standard: {
    email: 'testuser@example.com',
    password: 'testpassword',
    name: 'Test User',
    role: 'user'
  },
  admin: {
    email: 'admin@example.com',
    password: 'adminpassword',
    name: 'Admin User',
    role: 'admin'
  },
  premium: {
    email: 'premium@example.com',
    password: 'premiumpassword',
    name: 'Premium User',
    role: 'premium'
  }
};

/**
 * Test data for jobs
 */
const TEST_JOBS = {
  softwareEngineer: {
    title: 'Senior Software Engineer',
    company: 'Tech Corp',
    location: 'San Francisco, CA',
    salary: '$120,000 - $150,000',
    description: 'We are looking for an experienced software engineer...',
    requirements: ['5+ years of experience', 'JavaScript', 'React', 'Node.js'],
    type: 'Full-time',
    remote: true
  },
  dataScientist: {
    title: 'Data Scientist',
    company: 'Data Analytics Inc',
    location: 'New York, NY',
    salary: '$100,000 - $130,000',
    description: 'Join our data science team to work on exciting projects...',
    requirements: ['Python', 'Machine Learning', 'SQL', 'Statistics'],
    type: 'Full-time',
    remote: false
  },
  productManager: {
    title: 'Product Manager',
    company: 'Startup XYZ',
    location: 'Austin, TX',
    salary: '$90,000 - $110,000',
    description: 'Lead product development and strategy...',
    requirements: ['3+ years PM experience', 'Agile', 'Analytics'],
    type: 'Full-time',
    remote: true
  }
};

/**
 * Test applications data
 */
const TEST_APPLICATIONS = {
  pending: {
    status: 'pending',
    appliedDate: '2024-01-15',
    coverLetter: 'I am very interested in this position...',
    notes: 'Applied through company website'
  },
  interviewed: {
    status: 'interviewed',
    appliedDate: '2024-01-10',
    interviewDate: '2024-01-20',
    coverLetter: 'My experience aligns perfectly...',
    notes: 'Had a great conversation with the hiring manager'
  },
  rejected: {
    status: 'rejected',
    appliedDate: '2024-01-05',
    rejectedDate: '2024-01-18',
    coverLetter: 'I would love to contribute to your team...',
    notes: 'Not selected for this round'
  }
};

/**
 * Extended test with page objects and authentication
 */
const test = base.extend({
  // Page objects
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  
  jobsPage: async ({ page }, use) => {
    await use(new JobsPage(page));
  },

  // Authenticated contexts
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'tests/e2e/fixtures/auth-state.json'
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },

  // Test data
  testUsers: async ({}, use) => {
    await use(TEST_USERS);
  },

  testJobs: async ({}, use) => {
    await use(TEST_JOBS);
  },

  testApplications: async ({}, use) => {
    await use(TEST_APPLICATIONS);
  }
});

/**
 * Helper function to create a fresh authenticated context
 */
async function createAuthenticatedContext(browser, userType = 'standard') {
  const user = TEST_USERS[userType];
  if (!user) {
    throw new Error(`Unknown user type: ${userType}`);
  }

  const context = await browser.newContext();
  const page = await context.newPage();
  const loginPage = new LoginPage(page);
  
  try {
    await loginPage.login(user.email, user.password);
    return { context, page };
  } catch (error) {
    await context.close();
    throw error;
  }
}

/**
 * Helper function to seed test data
 */
async function seedTestData(page, options = {}) {
  const { 
    createJobs = true, 
    createApplications = true, 
    jobCount = 5, 
    applicationCount = 3 
  } = options;

  const backendURL = process.env.BACKEND_URL || 'http://localhost:8000';
  
  try {
    const seedResponse = await page.evaluate(async ({ backendURL, createJobs, createApplications, jobCount, applicationCount }) => {
      const response = await fetch(`${backendURL}/test/seed-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          create_jobs: createJobs,
          create_applications: createApplications,
          job_count: jobCount,
          application_count: applicationCount
        })
      });
      return response.ok;
    }, { backendURL, createJobs, createApplications, jobCount, applicationCount });
    
    return seedResponse;
  } catch (error) {
    console.warn('Failed to seed test data:', error.message);
    return false;
  }
}

/**
 * Helper function to clean test data
 */
async function cleanTestData(page) {
  const backendURL = process.env.BACKEND_URL || 'http://localhost:8000';
  
  try {
    const cleanResponse = await page.evaluate(async ({ backendURL }) => {
      const response = await fetch(`${backendURL}/test/cleanup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      return response.ok;
    }, { backendURL });
    
    return cleanResponse;
  } catch (error) {
    console.warn('Failed to clean test data:', error.message);
    return false;
  }
}

/**
 * Helper function to wait for API responses
 */
async function waitForApiResponse(page, urlPattern, timeout = 10000) {
  return page.waitForResponse(
    response => response.url().includes(urlPattern) && response.ok(),
    { timeout }
  );
}

/**
 * Helper function to mock API responses
 */
async function mockApiResponse(page, urlPattern, mockData) {
  await page.route(`**${urlPattern}**`, route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData)
    });
  });
}

module.exports = {
  test,
  expect,
  TEST_USERS,
  TEST_JOBS,
  TEST_APPLICATIONS,
  createAuthenticatedContext,
  seedTestData,
  cleanTestData,
  waitForApiResponse,
  mockApiResponse
};
