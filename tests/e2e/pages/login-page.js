/**
 * Login page object model
 * Handles authentication and login-related actions
 */

const BasePage = require('./base-page');

class LoginPage extends BasePage {
  constructor(page) {
    super(page);

    // Selectors
    this.selectors = {
      emailInput: '[data-testid="email"]',
      passwordInput: '[data-testid="password"]',
      loginButton: '[data-testid="login-button"]',
      signupLink: '[data-testid="signup-link"]',
      forgotPasswordLink: '[data-testid="forgot-password-link"]',
      errorMessage: '[data-testid="error-message"]',
      successMessage: '[data-testid="success-message"]',
      loadingSpinner: '[data-testid="loading"]',

      // Alternative selectors if data-testids are not available
      altEmailInput: 'input[type="email"]',
      altPasswordInput: 'input[type="password"]',
      altLoginButton: 'button[type="submit"], .login-button, #login-btn'
    };
  }

  /**
   * Navigate to the login page
   */
  async navigate() {
    await this.goto('/login');
    await this.waitForLoad();
  }

  /**
   * Enter email address
   * @param {string} email - The email address
   */
  async enterEmail(email) {
    try {
      await this.fill(this.selectors.emailInput, email);
    } catch (error) {
      // Fallback to alternative selector
      await this.fill(this.selectors.altEmailInput, email);
    }
  }

  /**
   * Enter password
   * @param {string} password - The password
   */
  async enterPassword(password) {
    try {
      await this.fill(this.selectors.passwordInput, password);
    } catch (error) {
      // Fallback to alternative selector
      await this.fill(this.selectors.altPasswordInput, password);
    }
  }

  /**
   * Click the login button
   */
  async clickLogin() {
    try {
      await this.click(this.selectors.loginButton);
    } catch (error) {
      // Fallback to alternative selector
      await this.click(this.selectors.altLoginButton);
    }
  }

  /**
   * Perform complete login flow
   * @param {string} email - The email address
   * @param {string} password - The password
   * @param {Object} options - Additional options
   */
  async login(email, password, options = {}) {
    const { waitForRedirect = true, expectedRedirect = '/dashboard' } = options;

    await this.navigate();
    await this.enterEmail(email);
    await this.enterPassword(password);
    await this.clickLogin();

    if (waitForRedirect) {
      await this.waitForNavigation();

      // Check if we're redirected to the expected page
      if (expectedRedirect && !(await this.isOnPage(expectedRedirect))) {
        // Check for error messages if not redirected
        const errorMessage = await this.getErrorMessage();
        if (errorMessage) {
          throw new Error(`Login failed: ${errorMessage}`);
        }
      }
    }

    await this.waitForLoadingToComplete();
  }

  /**
   * Login with test user credentials
   * @param {Object} options - Additional options
   */
  async loginAsTestUser(options = {}) {
    return await this.login('testuser@example.com', 'testpassword', options);
  }

  /**
   * Login with admin credentials
   * @param {Object} options - Additional options
   */
  async loginAsAdmin(options = {}) {
    return await this.login('admin@example.com', 'adminpassword', options);
  }

  /**
   * Click the signup link
   */
  async clickSignupLink() {
    await this.click(this.selectors.signupLink);
    await this.waitForNavigation();
  }

  /**
   * Click the forgot password link
   */
  async clickForgotPasswordLink() {
    await this.click(this.selectors.forgotPasswordLink);
    await this.waitForNavigation();
  }

  /**
   * Get error message if present
   */
  async getErrorMessage() {
    if (await this.isVisible(this.selectors.errorMessage)) {
      return await this.getTextContent(this.selectors.errorMessage);
    }
    return null;
  }

  /**
   * Get success message if present
   */
  async getSuccessMessage() {
    if (await this.isVisible(this.selectors.successMessage)) {
      return await this.getTextContent(this.selectors.successMessage);
    }
    return null;
  }

  /**
   * Check if currently on login page
   */
  async isOnLoginPage() {
    return await this.isOnPage('/login');
  }

  /**
   * Verify login page structure
   */
  async verifyPageStructure() {
    const requiredElements = [
      this.selectors.emailInput,
      this.selectors.passwordInput,
      this.selectors.loginButton
    ];

    for (const selector of requiredElements) {
      try {
        await this.waitForElement(selector);
      } catch (error) {
        console.warn(`Required element not found: ${selector}`);
        return false;
      }
    }

    return true;
  }

  /**
   * Check if user is already logged in (redirected from login page)
   */
  async checkIfAlreadyLoggedIn() {
    await this.navigate();

    // If we're redirected away from login page, user is already logged in
    await this.page.waitForTimeout(2000); // Give time for potential redirect

    return !(await this.isOnLoginPage());
  }

  /**
   * Wait for login to complete (either success or error)
   */
  async waitForLoginResult() {
    await Promise.race([
      // Wait for redirect (success)
      this.page.waitForURL('**/dashboard', { timeout: 10000 }),
      // Wait for error message (failure)
      this.waitForElement(this.selectors.errorMessage, { timeout: 10000 })
    ]);
  }
}

module.exports = LoginPage;
