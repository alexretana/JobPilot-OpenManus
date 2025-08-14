/**
 * Base page object class providing common functionality for all page objects
 */

class BasePage {
  constructor(page) {
    this.page = page;
    this.baseURL = process.env.BASE_URL || 'http://localhost:3000';
  }

  /**
   * Navigate to a specific path
   * @param {string} path - The path to navigate to
   */
  async goto(path = '') {
    const url = path.startsWith('http') ? path : `${this.baseURL}${path}`;
    await this.page.goto(url);
  }

  /**
   * Wait for the page to be loaded
   */
  async waitForLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for an element to be visible
   * @param {string} selector - The selector to wait for
   * @param {Object} options - Additional options
   */
  async waitForElement(selector, options = {}) {
    return await this.page.waitForSelector(selector, { 
      state: 'visible', 
      timeout: 10000,
      ...options 
    });
  }

  /**
   * Click an element safely
   * @param {string} selector - The selector to click
   * @param {Object} options - Additional options
   */
  async click(selector, options = {}) {
    await this.waitForElement(selector);
    await this.page.click(selector, options);
  }

  /**
   * Fill an input field
   * @param {string} selector - The input selector
   * @param {string} value - The value to fill
   * @param {Object} options - Additional options
   */
  async fill(selector, value, options = {}) {
    await this.waitForElement(selector);
    await this.page.fill(selector, value, options);
  }

  /**
   * Get text content of an element
   * @param {string} selector - The selector to get text from
   */
  async getTextContent(selector) {
    await this.waitForElement(selector);
    return await this.page.textContent(selector);
  }

  /**
   * Check if an element is visible
   * @param {string} selector - The selector to check
   */
  async isVisible(selector) {
    try {
      return await this.page.isVisible(selector);
    } catch (error) {
      return false;
    }
  }

  /**
   * Wait for navigation to complete
   * @param {Object} options - Additional options
   */
  async waitForNavigation(options = {}) {
    await this.page.waitForLoadState('networkidle', { timeout: 10000, ...options });
  }

  /**
   * Take a screenshot
   * @param {string} name - The screenshot name
   * @param {Object} options - Additional options
   */
  async screenshot(name, options = {}) {
    return await this.page.screenshot({ 
      path: `test-reports/screenshots/${name}.png`,
      fullPage: true,
      ...options 
    });
  }

  /**
   * Get current URL
   */
  url() {
    return this.page.url();
  }

  /**
   * Get page title
   */
  async title() {
    return await this.page.title();
  }

  /**
   * Check if current page matches expected path
   * @param {string} expectedPath - The expected path or pattern
   */
  async isOnPage(expectedPath) {
    const currentURL = this.url();
    if (expectedPath.includes('*')) {
      const regex = new RegExp(expectedPath.replace(/\*/g, '.*'));
      return regex.test(currentURL);
    }
    return currentURL.includes(expectedPath);
  }

  /**
   * Verify common page elements are present
   */
  async verifyPageStructure() {
    // Override in child classes to verify specific page structure
    return true;
  }

  /**
   * Handle common error states
   */
  async handleErrors() {
    const errorSelectors = [
      '[data-testid="error-message"]',
      '.error',
      '.alert-error',
      '[role="alert"]'
    ];

    for (const selector of errorSelectors) {
      if (await this.isVisible(selector)) {
        const errorText = await this.getTextContent(selector);
        console.warn(`Found error on page: ${errorText}`);
        return errorText;
      }
    }
    return null;
  }

  /**
   * Wait for loading spinners to disappear
   */
  async waitForLoadingToComplete() {
    const loadingSelectors = [
      '[data-testid="loading"]',
      '.loading',
      '.spinner',
      '[role="progressbar"]'
    ];

    for (const selector of loadingSelectors) {
      try {
        await this.page.waitForSelector(selector, { state: 'hidden', timeout: 5000 });
      } catch (error) {
        // Continue if loading indicator is not found or doesn't disappear
      }
    }
  }
}

module.exports = BasePage;
