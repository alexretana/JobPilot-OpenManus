/**
 * Global teardown for Playwright E2E tests
 * Cleans up test data and resources after all tests complete
 */

async function globalTeardown(config) {
  console.log('🧹 Starting E2E test global teardown...');
  
  const backendURL = process.env.BACKEND_URL || 'http://localhost:8000';

  // Clean up test data
  console.log('🗄️ Cleaning up test database...');
  try {
    const response = await fetch(`${backendURL}/test/cleanup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      console.log('✅ Test database cleanup successful');
    } else {
      console.warn('⚠️ Could not clean up test database');
    }
  } catch (error) {
    console.warn('⚠️ Database cleanup failed:', error.message);
  }

  // Clean up authentication files
  console.log('🔐 Cleaning up authentication state...');
  try {
    const fs = require('fs');
    const authStatePath = 'tests/e2e/fixtures/auth-state.json';
    
    if (fs.existsSync(authStatePath)) {
      fs.unlinkSync(authStatePath);
      console.log('✅ Authentication state file cleaned up');
    }
  } catch (error) {
    console.warn('⚠️ Could not clean up auth state file:', error.message);
  }

  console.log('🎉 Global teardown completed successfully!');
}

module.exports = globalTeardown;
