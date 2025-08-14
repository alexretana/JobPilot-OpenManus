/**
 * Jobs page object model
 * Handles job listings, search, and job-related functionality
 */

const BasePage = require('./base-page');

class JobsPage extends BasePage {
  constructor(page) {
    super(page);
    
    // Selectors
    this.selectors = {
      // Header and controls
      pageTitle: '[data-testid="jobs-page-title"]',
      searchInput: '[data-testid="job-search-input"]',
      searchButton: '[data-testid="job-search-button"]',
      addJobButton: '[data-testid="add-job-button"]',
      filterButton: '[data-testid="filter-button"]',
      sortDropdown: '[data-testid="sort-dropdown"]',
      
      // Job list
      jobsList: '[data-testid="jobs-list"]',
      jobItem: '[data-testid="job-item"]',
      jobTitle: '[data-testid="job-title"]',
      jobCompany: '[data-testid="job-company"]',
      jobLocation: '[data-testid="job-location"]',
      jobSalary: '[data-testid="job-salary"]',
      jobStatus: '[data-testid="job-status"]',
      jobActions: '[data-testid="job-actions"]',
      
      // Job item actions
      viewJobButton: '[data-testid="view-job-button"]',
      editJobButton: '[data-testid="edit-job-button"]',
      deleteJobButton: '[data-testid="delete-job-button"]',
      applyButton: '[data-testid="apply-button"]',
      
      // Filters
      filtersPanel: '[data-testid="filters-panel"]',
      locationFilter: '[data-testid="location-filter"]',
      salaryFilter: '[data-testid="salary-filter"]',
      companyFilter: '[data-testid="company-filter"]',
      statusFilter: '[data-testid="status-filter"]',
      clearFiltersButton: '[data-testid="clear-filters-button"]',
      applyFiltersButton: '[data-testid="apply-filters-button"]',
      
      // Pagination
      pagination: '[data-testid="pagination"]',
      prevPageButton: '[data-testid="prev-page-button"]',
      nextPageButton: '[data-testid="next-page-button"]',
      pageInfo: '[data-testid="page-info"]',
      
      // Empty state
      emptyState: '[data-testid="empty-jobs-state"]',
      noResultsMessage: '[data-testid="no-results-message"]',
      
      // Loading state
      loadingSpinner: '[data-testid="loading-jobs"]'
    };
  }

  /**
   * Navigate to the jobs page
   */
  async navigate() {
    await this.goto('/jobs');
    await this.waitForLoad();
    await this.waitForLoadingToComplete();
  }

  /**
   * Search for jobs
   * @param {string} searchTerm - The search term
   */
  async searchJobs(searchTerm) {
    await this.fill(this.selectors.searchInput, searchTerm);
    await this.click(this.selectors.searchButton);
    await this.waitForLoadingToComplete();
  }

  /**
   * Clear search
   */
  async clearSearch() {
    await this.fill(this.selectors.searchInput, '');
    await this.click(this.selectors.searchButton);
    await this.waitForLoadingToComplete();
  }

  /**
   * Get all job listings
   */
  async getJobListings() {
    await this.waitForLoadingToComplete();
    
    if (await this.isVisible(this.selectors.emptyState)) {
      return [];
    }
    
    const jobElements = await this.page.$$(`${this.selectors.jobsList} ${this.selectors.jobItem}`);
    const jobs = [];
    
    for (const jobElement of jobElements) {
      try {
        const job = {};
        
        // Get job title
        const titleElement = await jobElement.$('[data-testid="job-title"]');
        if (titleElement) {
          job.title = await titleElement.textContent();
        }
        
        // Get company
        const companyElement = await jobElement.$('[data-testid="job-company"]');
        if (companyElement) {
          job.company = await companyElement.textContent();
        }
        
        // Get location
        const locationElement = await jobElement.$('[data-testid="job-location"]');
        if (locationElement) {
          job.location = await locationElement.textContent();
        }
        
        // Get salary
        const salaryElement = await jobElement.$('[data-testid="job-salary"]');
        if (salaryElement) {
          job.salary = await salaryElement.textContent();
        }
        
        // Get status
        const statusElement = await jobElement.$('[data-testid="job-status"]');
        if (statusElement) {
          job.status = await statusElement.textContent();
        }
        
        jobs.push(job);
      } catch (error) {
        console.warn('Could not parse job element:', error.message);
      }
    }
    
    return jobs;
  }

  /**
   * Click on a specific job by title
   * @param {string} jobTitle - The job title to click
   */
  async clickJobByTitle(jobTitle) {
    const jobElements = await this.page.$$(`${this.selectors.jobsList} ${this.selectors.jobItem}`);
    
    for (const jobElement of jobElements) {
      try {
        const titleElement = await jobElement.$('[data-testid="job-title"]');
        if (titleElement) {
          const title = await titleElement.textContent();
          if (title && title.includes(jobTitle)) {
            await titleElement.click();
            await this.waitForNavigation();
            return;
          }
        }
      } catch (error) {
        console.warn('Error clicking job:', error.message);
      }
    }
    
    throw new Error(`Job with title "${jobTitle}" not found`);
  }

  /**
   * Apply to a job by title
   * @param {string} jobTitle - The job title to apply to
   */
  async applyToJobByTitle(jobTitle) {
    const jobElements = await this.page.$$(`${this.selectors.jobsList} ${this.selectors.jobItem}`);
    
    for (const jobElement of jobElements) {
      try {
        const titleElement = await jobElement.$('[data-testid="job-title"]');
        if (titleElement) {
          const title = await titleElement.textContent();
          if (title && title.includes(jobTitle)) {
            const applyButton = await jobElement.$('[data-testid="apply-button"]');
            if (applyButton) {
              await applyButton.click();
              await this.waitForNavigation();
              return;
            }
          }
        }
      } catch (error) {
        console.warn('Error applying to job:', error.message);
      }
    }
    
    throw new Error(`Job with title "${jobTitle}" not found or apply button not available`);
  }

  /**
   * Open filters panel
   */
  async openFilters() {
    if (!(await this.isVisible(this.selectors.filtersPanel))) {
      await this.click(this.selectors.filterButton);
    }
  }

  /**
   * Apply filters
   * @param {Object} filters - Filter options
   * @param {string} filters.location - Location filter
   * @param {string} filters.salary - Salary filter
   * @param {string} filters.company - Company filter
   * @param {string} filters.status - Status filter
   */
  async applyFilters(filters) {
    await this.openFilters();
    
    if (filters.location) {
      await this.fill(this.selectors.locationFilter, filters.location);
    }
    
    if (filters.salary) {
      await this.page.selectOption(this.selectors.salaryFilter, filters.salary);
    }
    
    if (filters.company) {
      await this.fill(this.selectors.companyFilter, filters.company);
    }
    
    if (filters.status) {
      await this.page.selectOption(this.selectors.statusFilter, filters.status);
    }
    
    await this.click(this.selectors.applyFiltersButton);
    await this.waitForLoadingToComplete();
  }

  /**
   * Clear all filters
   */
  async clearFilters() {
    await this.openFilters();
    await this.click(this.selectors.clearFiltersButton);
    await this.waitForLoadingToComplete();
  }

  /**
   * Sort jobs
   * @param {string} sortOption - Sort option (e.g., 'title', 'company', 'date', 'salary')
   */
  async sortJobs(sortOption) {
    await this.page.selectOption(this.selectors.sortDropdown, sortOption);
    await this.waitForLoadingToComplete();
  }

  /**
   * Navigate to next page
   */
  async goToNextPage() {
    if (await this.isVisible(this.selectors.nextPageButton)) {
      const isDisabled = await this.page.isDisabled(this.selectors.nextPageButton);
      if (!isDisabled) {
        await this.click(this.selectors.nextPageButton);
        await this.waitForLoadingToComplete();
        return true;
      }
    }
    return false;
  }

  /**
   * Navigate to previous page
   */
  async goToPreviousPage() {
    if (await this.isVisible(this.selectors.prevPageButton)) {
      const isDisabled = await this.page.isDisabled(this.selectors.prevPageButton);
      if (!isDisabled) {
        await this.click(this.selectors.prevPageButton);
        await this.waitForLoadingToComplete();
        return true;
      }
    }
    return false;
  }

  /**
   * Get pagination information
   */
  async getPaginationInfo() {
    if (await this.isVisible(this.selectors.pageInfo)) {
      const pageInfoText = await this.getTextContent(this.selectors.pageInfo);
      return pageInfoText;
    }
    return null;
  }

  /**
   * Get total number of jobs
   */
  async getTotalJobsCount() {
    const jobElements = await this.page.$$(`${this.selectors.jobsList} ${this.selectors.jobItem}`);
    return jobElements.length;
  }

  /**
   * Check if jobs list is empty
   */
  async isJobsListEmpty() {
    return await this.isVisible(this.selectors.emptyState) || 
           await this.isVisible(this.selectors.noResultsMessage);
  }

  /**
   * Click add job button
   */
  async clickAddJob() {
    await this.click(this.selectors.addJobButton);
    await this.waitForNavigation();
  }

  /**
   * Verify jobs page structure
   */
  async verifyPageStructure() {
    const requiredElements = [
      this.selectors.searchInput,
      this.selectors.addJobButton
    ];

    for (const selector of requiredElements) {
      try {
        await this.waitForElement(selector, { timeout: 5000 });
      } catch (error) {
        console.warn(`Jobs page element not found: ${selector}`);
        return false;
      }
    }
    
    return true;
  }

  /**
   * Get job details by index
   * @param {number} index - The job index (0-based)
   */
  async getJobByIndex(index) {
    const jobElements = await this.page.$$(`${this.selectors.jobsList} ${this.selectors.jobItem}`);
    
    if (index >= jobElements.length) {
      throw new Error(`Job index ${index} is out of range (${jobElements.length} jobs found)`);
    }
    
    const jobElement = jobElements[index];
    const job = {};
    
    try {
      const titleElement = await jobElement.$('[data-testid="job-title"]');
      if (titleElement) job.title = await titleElement.textContent();
      
      const companyElement = await jobElement.$('[data-testid="job-company"]');
      if (companyElement) job.company = await companyElement.textContent();
      
      const locationElement = await jobElement.$('[data-testid="job-location"]');
      if (locationElement) job.location = await locationElement.textContent();
      
      const salaryElement = await jobElement.$('[data-testid="job-salary"]');
      if (salaryElement) job.salary = await salaryElement.textContent();
      
      const statusElement = await jobElement.$('[data-testid="job-status"]');
      if (statusElement) job.status = await statusElement.textContent();
    } catch (error) {
      console.warn('Could not parse job element:', error.message);
    }
    
    return job;
  }
}

module.exports = JobsPage;
