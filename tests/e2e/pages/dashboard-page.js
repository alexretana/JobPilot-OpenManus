/**
 * Dashboard page object model
 * Handles main dashboard functionality and navigation
 */

const BasePage = require('./base-page');

class DashboardPage extends BasePage {
  constructor(page) {
    super(page);

    // Selectors
    this.selectors = {
      // Header and navigation
      header: '[data-testid="dashboard-header"]',
      userProfile: '[data-testid="user-profile"]',
      navMenu: '[data-testid="nav-menu"]',
      logoutButton: '[data-testid="logout-button"]',

      // Dashboard sections
      statsSection: '[data-testid="stats-section"]',
      recentJobs: '[data-testid="recent-jobs"]',
      recentApplications: '[data-testid="recent-applications"]',
      quickActions: '[data-testid="quick-actions"]',

      // Statistics cards
      totalJobsCard: '[data-testid="total-jobs-card"]',
      totalApplicationsCard: '[data-testid="total-applications-card"]',
      pendingApplicationsCard: '[data-testid="pending-applications-card"]',
      interviewsCard: '[data-testid="interviews-card"]',

      // Quick action buttons
      addJobButton: '[data-testid="add-job-button"]',
      searchJobsButton: '[data-testid="search-jobs-button"]',
      viewApplicationsButton: '[data-testid="view-applications-button"]',
      viewTimelineButton: '[data-testid="view-timeline-button"]',

      // Navigation links
      jobsLink: '[data-testid="jobs-link"]',
      applicationsLink: '[data-testid="applications-link"]',
      timelineLink: '[data-testid="timeline-link"]',
      profileLink: '[data-testid="profile-link"]',

      // Alternative selectors
      altHeader: '.dashboard-header, header',
      altStatsCards: '.stat-card, .dashboard-card',
      altQuickActions: '.quick-actions, .action-buttons'
    };
  }

  /**
   * Navigate to the dashboard
   */
  async navigate() {
    await this.goto('/dashboard');
    await this.waitForLoad();
    await this.waitForLoadingToComplete();
  }

  /**
   * Verify user is on dashboard page
   */
  async isOnDashboard() {
    return await this.isOnPage('/dashboard');
  }

  /**
   * Verify dashboard page structure
   */
  async verifyPageStructure() {
    const requiredElements = [
      this.selectors.header,
      this.selectors.statsSection,
      this.selectors.quickActions
    ];

    for (const selector of requiredElements) {
      try {
        await this.waitForElement(selector, { timeout: 5000 });
      } catch (error) {
        console.warn(`Dashboard element not found: ${selector}`);
        // Try alternative selectors
        if (selector === this.selectors.header) {
          try {
            await this.waitForElement(this.selectors.altHeader, { timeout: 5000 });
          } catch (altError) {
            return false;
          }
        }
      }
    }

    return true;
  }

  /**
   * Get statistics from dashboard cards
   */
  async getStatistics() {
    await this.waitForLoadingToComplete();

    const stats = {};

    try {
      if (await this.isVisible(this.selectors.totalJobsCard)) {
        stats.totalJobs = await this.getTextContent(`${this.selectors.totalJobsCard} .stat-number`);
      }

      if (await this.isVisible(this.selectors.totalApplicationsCard)) {
        stats.totalApplications = await this.getTextContent(`${this.selectors.totalApplicationsCard} .stat-number`);
      }

      if (await this.isVisible(this.selectors.pendingApplicationsCard)) {
        stats.pendingApplications = await this.getTextContent(`${this.selectors.pendingApplicationsCard} .stat-number`);
      }

      if (await this.isVisible(this.selectors.interviewsCard)) {
        stats.interviews = await this.getTextContent(`${this.selectors.interviewsCard} .stat-number`);
      }
    } catch (error) {
      console.warn('Could not retrieve all statistics:', error.message);
    }

    return stats;
  }

  /**
   * Get recent jobs list
   */
  async getRecentJobs() {
    if (!(await this.isVisible(this.selectors.recentJobs))) {
      return [];
    }

    const jobElements = await this.page.$$(`${this.selectors.recentJobs} .job-item`);
    const jobs = [];

    for (const jobElement of jobElements) {
      try {
        const title = await jobElement.textContent('.job-title');
        const company = await jobElement.textContent('.job-company');
        const location = await jobElement.textContent('.job-location');

        jobs.push({ title, company, location });
      } catch (error) {
        console.warn('Could not parse job element:', error.message);
      }
    }

    return jobs;
  }

  /**
   * Get recent applications list
   */
  async getRecentApplications() {
    if (!(await this.isVisible(this.selectors.recentApplications))) {
      return [];
    }

    const appElements = await this.page.$$(`${this.selectors.recentApplications} .application-item`);
    const applications = [];

    for (const appElement of appElements) {
      try {
        const jobTitle = await appElement.textContent('.job-title');
        const company = await appElement.textContent('.company-name');
        const status = await appElement.textContent('.application-status');
        const appliedDate = await appElement.textContent('.applied-date');

        applications.push({ jobTitle, company, status, appliedDate });
      } catch (error) {
        console.warn('Could not parse application element:', error.message);
      }
    }

    return applications;
  }

  /**
   * Click on a quick action button
   * @param {string} action - The action to perform ('addJob', 'searchJobs', 'viewApplications', 'viewTimeline')
   */
  async clickQuickAction(action) {
    const buttonMap = {
      addJob: this.selectors.addJobButton,
      searchJobs: this.selectors.searchJobsButton,
      viewApplications: this.selectors.viewApplicationsButton,
      viewTimeline: this.selectors.viewTimelineButton
    };

    const selector = buttonMap[action];
    if (!selector) {
      throw new Error(`Unknown quick action: ${action}`);
    }

    await this.click(selector);
    await this.waitForNavigation();
  }

  /**
   * Navigate to a specific section via navigation links
   * @param {string} section - The section to navigate to ('jobs', 'applications', 'timeline', 'profile')
   */
  async navigateToSection(section) {
    const linkMap = {
      jobs: this.selectors.jobsLink,
      applications: this.selectors.applicationsLink,
      timeline: this.selectors.timelineLink,
      profile: this.selectors.profileLink
    };

    const selector = linkMap[section];
    if (!selector) {
      throw new Error(`Unknown section: ${section}`);
    }

    await this.click(selector);
    await this.waitForNavigation();
  }

  /**
   * Perform logout
   */
  async logout() {
    await this.click(this.selectors.userProfile);
    await this.click(this.selectors.logoutButton);
    await this.waitForNavigation();
  }

  /**
   * Check if user profile information is visible
   */
  async isUserProfileVisible() {
    return await this.isVisible(this.selectors.userProfile);
  }

  /**
   * Get user profile information
   */
  async getUserProfileInfo() {
    if (!(await this.isVisible(this.selectors.userProfile))) {
      return null;
    }

    try {
      const profileInfo = {};

      // Try to get user name
      const nameSelector = `${this.selectors.userProfile} .user-name`;
      if (await this.isVisible(nameSelector)) {
        profileInfo.name = await this.getTextContent(nameSelector);
      }

      // Try to get user email
      const emailSelector = `${this.selectors.userProfile} .user-email`;
      if (await this.isVisible(emailSelector)) {
        profileInfo.email = await this.getTextContent(emailSelector);
      }

      return profileInfo;
    } catch (error) {
      console.warn('Could not retrieve user profile info:', error.message);
      return null;
    }
  }

  /**
   * Wait for dashboard data to load
   */
  async waitForDashboardData() {
    await this.waitForLoadingToComplete();

    // Wait for at least one of the main sections to be visible
    await Promise.race([
      this.waitForElement(this.selectors.statsSection),
      this.waitForElement(this.selectors.recentJobs),
      this.waitForElement(this.selectors.recentApplications)
    ]);
  }

  /**
   * Check if dashboard shows empty state
   */
  async isEmptyState() {
    const emptyStateSelectors = [
      '[data-testid="empty-state"]',
      '.empty-state',
      '.no-data'
    ];

    for (const selector of emptyStateSelectors) {
      if (await this.isVisible(selector)) {
        return true;
      }
    }

    // Check if statistics show zero values
    const stats = await this.getStatistics();
    const hasData = Object.values(stats).some(value => {
      const num = parseInt(value || '0');
      return num > 0;
    });

    return !hasData;
  }
}

module.exports = DashboardPage;
