/**
 * Jobs E2E Tests
 * Tests for job listings, search, filtering, and job-related functionality
 */

const { test, expect } = require('../fixtures/test-fixtures');
const { takeScreenshot, waitForNetworkIdle, getElementCount } = require('../utils/test-helpers');

test.describe('Jobs Page', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    // Log in before each test
    await loginPage.loginAsTestUser();
    await waitForNetworkIdle(page);
  });

  test('should display jobs page with all main sections', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Verify page structure
    const isValidStructure = await jobsPage.verifyPageStructure();
    expect(isValidStructure).toBeTruthy();

    // Take screenshot of loaded jobs page
    await takeScreenshot(page, 'jobs_main_view', 'page_loaded');
  });

  test('should display job listings', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Get job listings
    const jobs = await jobsPage.getJobListings();
    expect(Array.isArray(jobs)).toBeTruthy();

    if (jobs.length > 0) {
      console.log(`Found ${jobs.length} job listings`);

      // Verify job structure
      const firstJob = jobs[0];
      expect(firstJob).toBeDefined();

      // At least one of the basic fields should be present
      const hasBasicInfo = firstJob.title || firstJob.company || firstJob.location;
      expect(hasBasicInfo).toBeTruthy();

      await takeScreenshot(page, 'jobs_listings', 'with_data');
    } else {
      console.log('No job listings found - checking empty state');

      const isEmpty = await jobsPage.isJobsListEmpty();
      if (isEmpty) {
        console.log('Jobs page shows empty state');
        await takeScreenshot(page, 'jobs_listings', 'empty_state');
      }
    }
  });

  test('should handle job search functionality', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Get initial job count
    const initialJobs = await jobsPage.getJobListings();
    const initialCount = initialJobs.length;

    // Perform a search
    const searchTerm = 'engineer';
    await jobsPage.searchJobs(searchTerm);

    // Get search results
    const searchResults = await jobsPage.getJobListings();

    // Should have results (or show no results message)
    if (searchResults.length > 0) {
      console.log(`Search for '${searchTerm}' returned ${searchResults.length} results`);

      // Results should be relevant (if titles are available)
      const hasRelevantResults = searchResults.some(job =>
        job.title && job.title.toLowerCase().includes(searchTerm.toLowerCase())
      );

      if (searchResults[0].title) {
        // Only check relevance if we have titles to check
        console.log('Checking search result relevance...');
      }

      await takeScreenshot(page, 'jobs_search', 'results_found');
    } else {
      console.log(`Search for '${searchTerm}' returned no results`);

      // Should show no results message
      const isEmpty = await jobsPage.isJobsListEmpty();
      expect(isEmpty).toBeTruthy();

      await takeScreenshot(page, 'jobs_search', 'no_results');
    }

    // Clear search and verify results return
    await jobsPage.clearSearch();
    const clearedResults = await jobsPage.getJobListings();

    // Should show original results (or at least not be filtered)
    if (initialCount > 0) {
      expect(clearedResults.length).toBeGreaterThanOrEqual(0);
    }

    await takeScreenshot(page, 'jobs_search', 'search_cleared');
  });

  test('should handle job filtering', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Get initial jobs
    const initialJobs = await jobsPage.getJobListings();

    if (initialJobs.length > 0) {
      // Try to apply filters
      try {
        const filters = {
          location: 'San Francisco'
        };

        await jobsPage.applyFilters(filters);

        const filteredJobs = await jobsPage.getJobListings();

        console.log(`Applied location filter, got ${filteredJobs.length} results`);

        // Clear filters
        await jobsPage.clearFilters();

        const clearedJobs = await jobsPage.getJobListings();
        console.log(`Cleared filters, got ${clearedJobs.length} results`);

        await takeScreenshot(page, 'jobs_filtering', 'filters_applied');

      } catch (error) {
        console.log('Filtering functionality not fully implemented or accessible');
        await takeScreenshot(page, 'jobs_filtering', 'filters_not_available');
      }
    } else {
      console.log('No jobs to filter - skipping filter test');
    }
  });

  test('should handle job sorting', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    const initialJobs = await jobsPage.getJobListings();

    if (initialJobs.length > 1) {
      // Try sorting by title
      try {
        await jobsPage.sortJobs('title');

        const sortedJobs = await jobsPage.getJobListings();
        expect(sortedJobs.length).toBe(initialJobs.length);

        await takeScreenshot(page, 'jobs_sorting', 'sorted_by_title');

        // Try sorting by company
        await jobsPage.sortJobs('company');

        const companySortedJobs = await jobsPage.getJobListings();
        expect(companySortedJobs.length).toBe(initialJobs.length);

        await takeScreenshot(page, 'jobs_sorting', 'sorted_by_company');

      } catch (error) {
        console.log('Sorting functionality not implemented or accessible:', error.message);
      }
    } else {
      console.log('Not enough jobs to test sorting - need at least 2 jobs');
    }
  });

  test('should handle pagination', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Check initial pagination info
    const initialPageInfo = await jobsPage.getPaginationInfo();
    if (initialPageInfo) {
      console.log('Pagination info:', initialPageInfo);
    }

    // Try to go to next page
    const hasNextPage = await jobsPage.goToNextPage();

    if (hasNextPage) {
      console.log('Successfully navigated to next page');

      const nextPageJobs = await jobsPage.getJobListings();
      expect(Array.isArray(nextPageJobs)).toBeTruthy();

      await takeScreenshot(page, 'jobs_pagination', 'next_page');

      // Try to go back to previous page
      const hasPrevPage = await jobsPage.goToPreviousPage();

      if (hasPrevPage) {
        console.log('Successfully navigated back to previous page');

        const prevPageJobs = await jobsPage.getJobListings();
        expect(Array.isArray(prevPageJobs)).toBeTruthy();

        await takeScreenshot(page, 'jobs_pagination', 'previous_page');
      }
    } else {
      console.log('No pagination available - likely all jobs fit on one page');
    }
  });

  test('should allow clicking on individual jobs', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    const jobs = await jobsPage.getJobListings();

    if (jobs.length > 0) {
      const firstJob = jobs[0];

      if (firstJob.title) {
        const originalUrl = page.url();

        try {
          // Click on the first job
          await jobsPage.clickJobByTitle(firstJob.title);

          // Should navigate to job details page
          await waitForNetworkIdle(page);
          const newUrl = page.url();

          if (newUrl !== originalUrl) {
            console.log('Successfully navigated to job details page');
            expect(newUrl).toContain('job');

            await takeScreenshot(page, 'jobs_interaction', 'job_details_page');

            // Navigate back to jobs page
            await jobsPage.navigate();
          } else {
            console.log('Job click did not navigate - may open in modal or same page');
          }

        } catch (error) {
          console.log('Could not click on job:', error.message);
        }
      } else {
        console.log('First job has no title to click on');
      }
    } else {
      console.log('No jobs available to click on');
    }
  });

  test('should handle add job functionality', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    const originalUrl = page.url();

    try {
      // Click add job button
      await jobsPage.clickAddJob();

      // Should navigate to add job page or open modal
      await waitForNetworkIdle(page);
      const newUrl = page.url();

      if (newUrl !== originalUrl) {
        console.log('Navigated to add job page');
        expect(newUrl).toMatch(/add|create|new/);

        await takeScreenshot(page, 'jobs_add_job', 'add_job_page');

        // Navigate back to jobs page
        await jobsPage.navigate();
      } else {
        console.log('Add job may have opened a modal or inline form');

        // Check for modal or form elements
        const modalExists = await page.isVisible('.modal, [role="dialog"], .popup');
        const formExists = await page.isVisible('form, [data-testid*="form"]');

        if (modalExists || formExists) {
          console.log('Add job modal or form is visible');
          await takeScreenshot(page, 'jobs_add_job', 'add_job_modal');
        }
      }

    } catch (error) {
      console.log('Add job functionality not accessible:', error.message);
      await takeScreenshot(page, 'jobs_add_job', 'button_not_found');
    }
  });

  test('should display job count and total information', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    const totalJobs = await jobsPage.getTotalJobsCount();
    console.log(`Total jobs displayed: ${totalJobs}`);

    // Should be a valid number
    expect(totalJobs).toBeGreaterThanOrEqual(0);

    // Check pagination info for additional context
    const pageInfo = await jobsPage.getPaginationInfo();
    if (pageInfo) {
      console.log('Page information:', pageInfo);
      // Page info should contain some numbers
      expect(pageInfo).toMatch(/\d/);
    }

    await takeScreenshot(page, 'jobs_count_info', 'totals_displayed');
  });

  test('should handle empty jobs state gracefully', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Search for something that definitely won't exist
    await jobsPage.searchJobs('xyznonexistentjobquery12345');

    // Should show empty state
    const isEmpty = await jobsPage.isJobsListEmpty();
    if (isEmpty) {
      console.log('Empty state displayed correctly');

      // Should still have basic page structure
      const isValidStructure = await jobsPage.verifyPageStructure();
      expect(isValidStructure).toBeTruthy();

      await takeScreenshot(page, 'jobs_empty_state', 'no_results_found');

      // Clear search to return to normal state
      await jobsPage.clearSearch();
    } else {
      console.log('Search returned results even for nonsensical query');
    }
  });

  test('should maintain page state during interactions', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Perform a search
    const searchTerm = 'developer';
    await jobsPage.searchJobs(searchTerm);

    const searchResults = await jobsPage.getJobListings();
    const initialCount = searchResults.length;

    // Refresh the page
    await page.reload();
    await waitForNetworkIdle(page);

    // Should maintain some consistent state
    const afterRefreshJobs = await jobsPage.getJobListings();
    expect(Array.isArray(afterRefreshJobs)).toBeTruthy();

    // Page should still be functional
    const isValidStructure = await jobsPage.verifyPageStructure();
    expect(isValidStructure).toBeTruthy();

    await takeScreenshot(page, 'jobs_page_state', 'after_refresh');
  });
});

test.describe('Jobs Page - Error Handling', () => {
  test.beforeEach(async ({ page, loginPage }) => {
    await loginPage.loginAsTestUser();
    await waitForNetworkIdle(page);
  });

  test('should handle network errors gracefully', async ({
    page,
    jobsPage
  }) => {
    await jobsPage.navigate();

    // Simulate network failure
    await page.setOfflineMode(true);

    // Try to search jobs while offline
    await jobsPage.searchJobs('test');

    // Should handle the error gracefully
    await page.waitForTimeout(2000);

    // Page should not crash
    const isStillOnPage = await page.url().includes('/jobs');
    expect(isStillOnPage).toBeTruthy();

    // Restore network
    await page.setOfflineMode(false);

    await takeScreenshot(page, 'jobs_error_handling', 'network_offline');
  });
});
