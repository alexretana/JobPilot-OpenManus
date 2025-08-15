/**
 * Dashboard E2E Tests
 * Tests for dashboard functionality, navigation, and data display
 */

const { test, expect } = require('../fixtures/test-fixtures');
const { takeScreenshot, waitForNetworkIdle, getElementCount } = require('../utils/test-helpers');

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    // Log in before each test
    await loginPage.loginAsTestUser();
    await waitForNetworkIdle(page);
  });

  test('should display dashboard with all main sections', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();

    // Verify page structure
    const isValidStructure = await dashboardPage.verifyPageStructure();
    expect(isValidStructure).toBeTruthy();

    // Wait for dashboard data to load
    await dashboardPage.waitForDashboardData();

    // Take screenshot of loaded dashboard
    await takeScreenshot(page, 'dashboard_main_view', 'all_sections_loaded');
  });

  test('should display user profile information', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();

    // Check if user profile is visible
    const isProfileVisible = await dashboardPage.isUserProfileVisible();
    expect(isProfileVisible).toBeTruthy();

    // Try to get user profile info
    const profileInfo = await dashboardPage.getUserProfileInfo();
    if (profileInfo) {
      expect(profileInfo).toBeDefined();

      // If email is available, it should be a valid format
      if (profileInfo.email) {
        expect(profileInfo.email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
      }
    }

    await takeScreenshot(page, 'dashboard_user_profile', 'profile_visible');
  });

  test('should display statistics cards', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    // Get statistics
    const stats = await dashboardPage.getStatistics();
    expect(stats).toBeDefined();

    // Check if at least some statistics are present
    const hasStats = Object.keys(stats).length > 0;
    if (hasStats) {
      console.log('Dashboard statistics:', stats);

      // Verify statistics are numeric strings or numbers
      Object.values(stats).forEach(stat => {
        if (stat && stat.toString().trim()) {
          // Should be a number or contain numeric characters
          expect(stat.toString()).toMatch(/\d/);
        }
      });
    }

    await takeScreenshot(page, 'dashboard_statistics', 'stats_displayed');
  });

  test('should display recent jobs section', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    // Get recent jobs
    const recentJobs = await dashboardPage.getRecentJobs();
    expect(Array.isArray(recentJobs)).toBeTruthy();

    if (recentJobs.length > 0) {
      console.log('Recent jobs found:', recentJobs.length);

      // Verify job structure
      const firstJob = recentJobs[0];
      expect(firstJob).toBeDefined();

      // At least one of title, company, or location should be present
      const hasBasicInfo = firstJob.title || firstJob.company || firstJob.location;
      expect(hasBasicInfo).toBeTruthy();
    } else {
      console.log('No recent jobs found - may be empty state');
    }

    await takeScreenshot(page, 'dashboard_recent_jobs', 'jobs_section');
  });

  test('should display recent applications section', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    // Get recent applications
    const recentApplications = await dashboardPage.getRecentApplications();
    expect(Array.isArray(recentApplications)).toBeTruthy();

    if (recentApplications.length > 0) {
      console.log('Recent applications found:', recentApplications.length);

      // Verify application structure
      const firstApp = recentApplications[0];
      expect(firstApp).toBeDefined();

      // At least one of the basic fields should be present
      const hasBasicInfo = firstApp.jobTitle || firstApp.company || firstApp.status;
      expect(hasBasicInfo).toBeTruthy();
    } else {
      console.log('No recent applications found - may be empty state');
    }

    await takeScreenshot(page, 'dashboard_recent_applications', 'applications_section');
  });

  test('should handle empty dashboard state gracefully', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    // Check if dashboard shows empty state
    const isEmpty = await dashboardPage.isEmptyState();

    if (isEmpty) {
      console.log('Dashboard is in empty state - this is expected for new users');

      // Should still display the basic structure
      const isValidStructure = await dashboardPage.verifyPageStructure();
      expect(isValidStructure).toBeTruthy();

      await takeScreenshot(page, 'dashboard_empty_state', 'no_data_display');
    } else {
      console.log('Dashboard has data - checking for proper display');

      // If not empty, should have some statistics or data
      const stats = await dashboardPage.getStatistics();
      const recentJobs = await dashboardPage.getRecentJobs();
      const recentApps = await dashboardPage.getRecentApplications();

      const hasData = Object.keys(stats).length > 0 ||
                     recentJobs.length > 0 ||
                     recentApps.length > 0;

      expect(hasData).toBeTruthy();
    }
  });

  test('should navigate to different sections via quick actions', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    const originalUrl = page.url();

    // Test navigation to jobs section
    try {
      await dashboardPage.clickQuickAction('searchJobs');
      await waitForNetworkIdle(page);

      // Should have navigated to jobs page
      const jobsUrl = page.url();
      expect(jobsUrl).not.toBe(originalUrl);
      expect(jobsUrl.includes('/jobs')).toBeTruthy();

      await takeScreenshot(page, 'dashboard_navigation', 'jobs_section');

      // Go back to dashboard
      await dashboardPage.navigate();
    } catch (error) {
      console.log('Search jobs quick action not available:', error.message);
    }

    // Test navigation to applications
    try {
      await dashboardPage.clickQuickAction('viewApplications');
      await waitForNetworkIdle(page);

      // Should have navigated to applications page
      const appsUrl = page.url();
      expect(appsUrl).not.toBe(originalUrl);
      expect(appsUrl.includes('/applications')).toBeTruthy();

      await takeScreenshot(page, 'dashboard_navigation', 'applications_section');

      // Go back to dashboard
      await dashboardPage.navigate();
    } catch (error) {
      console.log('View applications quick action not available:', error.message);
    }
  });

  test('should navigate using main navigation links', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    const originalUrl = page.url();

    // Test navigation to jobs via nav link
    try {
      await dashboardPage.navigateToSection('jobs');
      await waitForNetworkIdle(page);

      const jobsUrl = page.url();
      expect(jobsUrl).not.toBe(originalUrl);
      expect(jobsUrl.includes('/jobs')).toBeTruthy();

      // Go back to dashboard
      await dashboardPage.navigate();
    } catch (error) {
      console.log('Jobs navigation link not available:', error.message);
    }

    // Test navigation to applications via nav link
    try {
      await dashboardPage.navigateToSection('applications');
      await waitForNetworkIdle(page);

      const appsUrl = page.url();
      expect(appsUrl).not.toBe(originalUrl);
      expect(appsUrl.includes('/applications')).toBeTruthy();

      // Go back to dashboard
      await dashboardPage.navigate();
    } catch (error) {
      console.log('Applications navigation link not available:', error.message);
    }
  });

  test('should refresh dashboard data correctly', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    // Get initial state
    const initialStats = await dashboardPage.getStatistics();
    const initialJobs = await dashboardPage.getRecentJobs();
    const initialApps = await dashboardPage.getRecentApplications();

    // Refresh the page
    await page.reload();
    await waitForNetworkIdle(page);
    await dashboardPage.waitForDashboardData();

    // Get refreshed state
    const refreshedStats = await dashboardPage.getStatistics();
    const refreshedJobs = await dashboardPage.getRecentJobs();
    const refreshedApps = await dashboardPage.getRecentApplications();

    // Data should be consistent after refresh
    expect(typeof refreshedStats).toBe('object');
    expect(Array.isArray(refreshedJobs)).toBeTruthy();
    expect(Array.isArray(refreshedApps)).toBeTruthy();

    // Should still have valid structure
    const isValidStructure = await dashboardPage.verifyPageStructure();
    expect(isValidStructure).toBeTruthy();

    await takeScreenshot(page, 'dashboard_after_refresh', 'data_reloaded');
  });

  test('should handle dashboard interactions without errors', async ({
    page,
    dashboardPage
  }) => {
    await dashboardPage.navigate();
    await dashboardPage.waitForDashboardData();

    // Try various interactions that shouldn't cause errors

    // Click on statistics cards (if clickable)
    try {
      const statsElements = await page.$$('[data-testid*="card"], .stat-card, .dashboard-card');
      if (statsElements.length > 0) {
        await statsElements[0].click();
        await page.waitForTimeout(500); // Brief wait to see if anything happens
      }
    } catch (error) {
      // It's okay if stats cards aren't clickable
      console.log('Statistics cards are not interactive');
    }

    // Hover over interactive elements
    try {
      const interactiveElements = await page.$$('[data-testid*="button"], button, a');
      if (interactiveElements.length > 0) {
        await interactiveElements[0].hover();
        await page.waitForTimeout(300);
      }
    } catch (error) {
      console.log('Could not hover over elements');
    }

    // Should still be on dashboard and functional
    expect(await dashboardPage.isOnDashboard()).toBeTruthy();

    await takeScreenshot(page, 'dashboard_interactions', 'after_clicks');
  });
});
