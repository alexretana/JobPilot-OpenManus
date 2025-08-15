/**
 * Global setup for Playwright E2E tests
 * Handles database setup, user authentication, and test data preparation
 */

const { chromium } = require('@playwright/test');
const path = require('path');
const { spawn, execSync } = require('child_process');

async function globalSetup(config) {
  console.log('🚀 Starting E2E test global setup...');

  const baseURL = process.env.BASE_URL || 'http://localhost:3000';
  const backendURL = process.env.BACKEND_URL || 'http://localhost:8000';

  // Wait for backend to be ready
  console.log('⏳ Waiting for backend server...');
  let backendReady = false;
  let attempts = 0;
  const maxAttempts = 60; // 60 seconds max wait

  while (!backendReady && attempts < maxAttempts) {
    try {
      const response = await fetch(`${backendURL}/health`);
      if (response.ok) {
        backendReady = true;
        console.log('✅ Backend server is ready');
      }
    } catch (error) {
      // Server not ready yet
    }

    if (!backendReady) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }
  }

  if (!backendReady) {
    throw new Error('❌ Backend server failed to start within 60 seconds');
  }

  // Wait for frontend to be ready
  console.log('⏳ Waiting for frontend server...');
  let frontendReady = false;
  attempts = 0;

  while (!frontendReady && attempts < maxAttempts) {
    try {
      const response = await fetch(baseURL);
      if (response.ok || response.status === 404) { // 404 is ok for SPA routes
        frontendReady = true;
        console.log('✅ Frontend server is ready');
      }
    } catch (error) {
      // Server not ready yet
    }

    if (!frontendReady) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }
  }

  if (!frontendReady) {
    throw new Error('❌ Frontend server failed to start within 60 seconds');
  }

  // Setup test database state
  console.log('🗄️ Setting up test database...');
  try {
    // Reset database to clean state
    const response = await fetch(`${backendURL}/test/reset-db`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (response.ok) {
      console.log('✅ Test database reset successful');
    } else {
      console.warn('⚠️ Could not reset test database, continuing with current state');
    }
  } catch (error) {
    console.warn('⚠️ Database reset failed:', error.message);
  }

  // Create test users and seed data
  console.log('👤 Creating test users...');
  try {
    const seedResponse = await fetch(`${backendURL}/test/seed-data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        create_users: true,
        create_jobs: true,
        create_applications: true
      })
    });

    if (seedResponse.ok) {
      console.log('✅ Test data seeded successfully');
    } else {
      console.warn('⚠️ Could not seed test data, tests may fail');
    }
  } catch (error) {
    console.warn('⚠️ Data seeding failed:', error.message);
  }

  // Authenticate a test user and store auth state
  console.log('🔐 Setting up authentication state...');
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Go to login page
    await page.goto(`${baseURL}/login`);

    // Fill in test user credentials
    await page.fill('[data-testid="email"]', 'testuser@example.com');
    await page.fill('[data-testid="password"]', 'testpassword');
    await page.click('[data-testid="login-button"]');

    // Wait for successful login (redirect to dashboard)
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Save authenticated state
    await context.storageState({ path: 'tests/e2e/fixtures/auth-state.json' });
    console.log('✅ Authentication state saved');
  } catch (error) {
    console.warn('⚠️ Could not setup authentication state:', error.message);
    console.warn('Some tests requiring authentication may fail');
  } finally {
    await browser.close();
  }

  console.log('🎉 Global setup completed successfully!');
}

module.exports = globalSetup;
