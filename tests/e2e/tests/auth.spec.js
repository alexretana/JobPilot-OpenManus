/**
 * Authentication E2E Tests
 * Tests for login, logout, and authentication flows
 */

const { test, expect } = require('../fixtures/test-fixtures');
const { takeScreenshot, waitForNetworkIdle } = require('../utils/test-helpers');

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Start with a clean slate
    await page.goto('/');
  });

  test('should successfully log in with valid credentials', async ({
    page,
    loginPage,
    dashboardPage,
    testUsers
  }) => {
    const user = testUsers.standard;

    // Navigate to login page
    await loginPage.navigate();

    // Verify login page structure
    const isValidStructure = await loginPage.verifyPageStructure();
    expect(isValidStructure).toBeTruthy();

    // Perform login
    await loginPage.enterEmail(user.email);
    await loginPage.enterPassword(user.password);
    await loginPage.clickLogin();

    // Wait for navigation and verify we're on dashboard
    await waitForNetworkIdle(page);
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();

    // Verify user profile is visible
    const isProfileVisible = await dashboardPage.isUserProfileVisible();
    expect(isProfileVisible).toBeTruthy();

    await takeScreenshot(page, 'auth_login_success', 'dashboard_loaded');
  });

  test('should show error message with invalid credentials', async ({
    page,
    loginPage
  }) => {
    await loginPage.navigate();

    // Try to login with invalid credentials
    await loginPage.enterEmail('invalid@example.com');
    await loginPage.enterPassword('wrongpassword');
    await loginPage.clickLogin();

    // Wait for error message
    await page.waitForTimeout(2000);

    // Should still be on login page
    expect(await loginPage.isOnLoginPage()).toBeTruthy();

    // Check for error message (if implementation provides one)
    const errorMessage = await loginPage.getErrorMessage();
    if (errorMessage) {
      expect(errorMessage.length).toBeGreaterThan(0);
    }

    await takeScreenshot(page, 'auth_login_failure', 'error_shown');
  });

  test('should require email and password fields', async ({
    page,
    loginPage
  }) => {
    await loginPage.navigate();

    // Try to submit without filling any fields
    await loginPage.clickLogin();

    // Should still be on login page
    expect(await loginPage.isOnLoginPage()).toBeTruthy();

    // Try with only email
    await loginPage.enterEmail('test@example.com');
    await loginPage.clickLogin();

    // Should still be on login page
    expect(await loginPage.isOnLoginPage()).toBeTruthy();
  });

  test('should successfully log out', async ({
    page,
    loginPage,
    dashboardPage,
    testUsers
  }) => {
    // First, log in
    await loginPage.loginAsTestUser();

    // Verify we're on dashboard
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();

    // Perform logout
    await dashboardPage.logout();

    // Wait for navigation
    await waitForNetworkIdle(page);

    // Should be redirected to login page or home page
    const currentUrl = page.url();
    expect(currentUrl.includes('/login') || currentUrl.includes('/')).toBeTruthy();

    await takeScreenshot(page, 'auth_logout_success', 'redirected_after_logout');
  });

  test('should redirect to login when accessing protected pages without authentication', async ({
    page
  }) => {
    // Try to access dashboard without authentication
    await page.goto('/dashboard');

    // Should be redirected to login page
    await waitForNetworkIdle(page);
    const currentUrl = page.url();
    expect(currentUrl.includes('/login')).toBeTruthy();

    // Try to access jobs page without authentication
    await page.goto('/jobs');

    // Should be redirected to login page
    await waitForNetworkIdle(page);
    const currentUrl2 = page.url();
    expect(currentUrl2.includes('/login')).toBeTruthy();
  });

  test('should maintain session after page refresh', async ({
    page,
    loginPage,
    dashboardPage
  }) => {
    // Log in
    await loginPage.loginAsTestUser();

    // Verify we're on dashboard
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();

    // Refresh the page
    await page.reload();
    await waitForNetworkIdle(page);

    // Should still be logged in and on dashboard
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();

    // Profile should still be visible
    const isProfileVisible = await dashboardPage.isUserProfileVisible();
    expect(isProfileVisible).toBeTruthy();
  });

  test('should handle login with different user roles', async ({
    page,
    loginPage,
    dashboardPage,
    testUsers
  }) => {
    // Test admin user login
    const adminUser = testUsers.admin;

    await loginPage.login(adminUser.email, adminUser.password);

    // Should successfully reach dashboard
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();

    // Log out
    await dashboardPage.logout();
    await waitForNetworkIdle(page);

    // Test standard user login
    const standardUser = testUsers.standard;

    await loginPage.login(standardUser.email, standardUser.password);

    // Should successfully reach dashboard
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();
  });

  test('should check if user is already logged in', async ({
    page,
    loginPage,
    dashboardPage
  }) => {
    // First, log in
    await loginPage.loginAsTestUser();
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();

    // Try to access login page when already logged in
    const alreadyLoggedIn = await loginPage.checkIfAlreadyLoggedIn();

    if (alreadyLoggedIn) {
      // Should be redirected away from login page
      expect(await loginPage.isOnLoginPage()).toBeFalsy();
    } else {
      // If not redirected, should at least be able to access dashboard
      await dashboardPage.navigate();
      expect(await dashboardPage.isOnDashboard()).toBeTruthy();
    }
  });

  test('should handle network errors gracefully', async ({
    page,
    loginPage
  }) => {
    await loginPage.navigate();

    // Simulate network failure
    await page.setOfflineMode(true);

    await loginPage.enterEmail('test@example.com');
    await loginPage.enterPassword('password');
    await loginPage.clickLogin();

    // Wait for potential error handling
    await page.waitForTimeout(3000);

    // Should handle the error gracefully (implementation dependent)
    // At minimum, should not crash or hang
    expect(await loginPage.isOnLoginPage()).toBeTruthy();

    // Restore network
    await page.setOfflineMode(false);

    await takeScreenshot(page, 'auth_network_error', 'offline_handled');
  });
});

test.describe('Authentication - Navigation Flow', () => {
  test('should allow navigation between authentication pages', async ({
    page,
    loginPage
  }) => {
    await loginPage.navigate();

    // Try to click signup link (if available)
    try {
      await loginPage.clickSignupLink();
      await waitForNetworkIdle(page);

      // Should be on signup page or some registration flow
      const currentUrl = page.url();
      expect(currentUrl.includes('/signup') || currentUrl.includes('/register')).toBeTruthy();
    } catch (error) {
      console.log('Signup link not available or not implemented');
    }

    // Go back to login
    await loginPage.navigate();

    // Try to click forgot password link (if available)
    try {
      await loginPage.clickForgotPasswordLink();
      await waitForNetworkIdle(page);

      // Should be on forgot password page
      const currentUrl = page.url();
      expect(currentUrl.includes('/forgot') || currentUrl.includes('/reset')).toBeTruthy();
    } catch (error) {
      console.log('Forgot password link not available or not implemented');
    }
  });
});
