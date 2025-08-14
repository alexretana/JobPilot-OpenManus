/**
 * E2E Test Helper Utilities
 * Common helper functions for Playwright E2E tests
 */

const { expect } = require('@playwright/test');

/**
 * Wait for element with custom timeout and error handling
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 * @param {Object} options - Options object
 */
async function waitForElementSafe(page, selector, options = {}) {
  const { timeout = 10000, state = 'visible', throwOnTimeout = false } = options;
  
  try {
    return await page.waitForSelector(selector, { state, timeout });
  } catch (error) {
    if (throwOnTimeout) {
      throw new Error(`Element '${selector}' not found within ${timeout}ms`);
    }
    console.warn(`Element '${selector}' not found, continuing...`);
    return null;
  }
}

/**
 * Safely click an element with retries
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 * @param {Object} options - Options object
 */
async function clickSafe(page, selector, options = {}) {
  const { maxRetries = 3, delay = 1000, waitForSelector = true } = options;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      if (waitForSelector) {
        await waitForElementSafe(page, selector, { throwOnTimeout: true });
      }
      
      await page.click(selector);
      return;
    } catch (error) {
      if (i === maxRetries - 1) {
        throw new Error(`Failed to click '${selector}' after ${maxRetries} attempts: ${error.message}`);
      }
      
      console.warn(`Click attempt ${i + 1} failed for '${selector}', retrying...`);
      await page.waitForTimeout(delay);
    }
  }
}

/**
 * Safely fill an input field with retries
 * @param {Page} page - Playwright page object
 * @param {string} selector - Input selector
 * @param {string} value - Value to fill
 * @param {Object} options - Options object
 */
async function fillSafe(page, selector, value, options = {}) {
  const { maxRetries = 3, delay = 1000, clear = true } = options;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      await waitForElementSafe(page, selector, { throwOnTimeout: true });
      
      if (clear) {
        await page.fill(selector, '');
      }
      
      await page.fill(selector, value);
      return;
    } catch (error) {
      if (i === maxRetries - 1) {
        throw new Error(`Failed to fill '${selector}' after ${maxRetries} attempts: ${error.message}`);
      }
      
      console.warn(`Fill attempt ${i + 1} failed for '${selector}', retrying...`);
      await page.waitForTimeout(delay);
    }
  }
}

/**
 * Take screenshot with automatic naming
 * @param {Page} page - Playwright page object
 * @param {string} testName - Test name for screenshot
 * @param {string} step - Current step description
 */
async function takeScreenshot(page, testName, step = 'default') {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${testName}_${step}_${timestamp}.png`;
  
  await page.screenshot({
    path: `test-reports/screenshots/${filename}`,
    fullPage: true
  });
  
  return filename;
}

/**
 * Wait for network to be idle
 * @param {Page} page - Playwright page object
 * @param {Object} options - Options object
 */
async function waitForNetworkIdle(page, options = {}) {
  const { timeout = 10000, idleTime = 500 } = options;
  
  await page.waitForLoadState('networkidle', { timeout });
  await page.waitForTimeout(idleTime); // Additional buffer
}

/**
 * Check if element exists without throwing
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 */
async function elementExists(page, selector) {
  try {
    const element = await page.$(selector);
    return element !== null;
  } catch (error) {
    return false;
  }
}

/**
 * Get text content safely
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 * @param {Object} options - Options object
 */
async function getTextSafe(page, selector, options = {}) {
  const { defaultValue = '', trim = true } = options;
  
  try {
    await waitForElementSafe(page, selector, { throwOnTimeout: true });
    const text = await page.textContent(selector);
    return trim && text ? text.trim() : text || defaultValue;
  } catch (error) {
    console.warn(`Could not get text from '${selector}': ${error.message}`);
    return defaultValue;
  }
}

/**
 * Wait for URL to match pattern
 * @param {Page} page - Playwright page object
 * @param {string|RegExp} pattern - URL pattern to match
 * @param {Object} options - Options object
 */
async function waitForUrlPattern(page, pattern, options = {}) {
  const { timeout = 10000 } = options;
  
  if (typeof pattern === 'string') {
    await page.waitForURL(`**${pattern}**`, { timeout });
  } else {
    await page.waitForFunction(
      (regex) => regex.test(window.location.href),
      pattern,
      { timeout }
    );
  }
}

/**
 * Scroll element into view
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 */
async function scrollIntoView(page, selector) {
  await page.$eval(selector, element => {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  
  // Wait for scroll to complete
  await page.waitForTimeout(500);
}

/**
 * Clear browser storage
 * @param {Page} page - Playwright page object
 * @param {Object} options - Options object
 */
async function clearBrowserStorage(page, options = {}) {
  const { localStorage = true, sessionStorage = true, cookies = true } = options;
  
  if (localStorage) {
    await page.evaluate(() => window.localStorage.clear());
  }
  
  if (sessionStorage) {
    await page.evaluate(() => window.sessionStorage.clear());
  }
  
  if (cookies) {
    await page.context().clearCookies();
  }
}

/**
 * Simulate keyboard shortcuts
 * @param {Page} page - Playwright page object
 * @param {string} shortcut - Keyboard shortcut (e.g., 'Ctrl+A', 'Meta+C')
 */
async function pressShortcut(page, shortcut) {
  await page.keyboard.press(shortcut);
}

/**
 * Upload file to input
 * @param {Page} page - Playwright page object
 * @param {string} selector - File input selector
 * @param {string} filePath - Path to file to upload
 */
async function uploadFile(page, selector, filePath) {
  await waitForElementSafe(page, selector, { throwOnTimeout: true });
  await page.setInputFiles(selector, filePath);
}

/**
 * Hover over element
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 */
async function hoverElement(page, selector) {
  await waitForElementSafe(page, selector, { throwOnTimeout: true });
  await page.hover(selector);
}

/**
 * Double click element
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 */
async function doubleClickElement(page, selector) {
  await waitForElementSafe(page, selector, { throwOnTimeout: true });
  await page.dblclick(selector);
}

/**
 * Drag and drop elements
 * @param {Page} page - Playwright page object
 * @param {string} sourceSelector - Source element selector
 * @param {string} targetSelector - Target element selector
 */
async function dragAndDrop(page, sourceSelector, targetSelector) {
  await waitForElementSafe(page, sourceSelector, { throwOnTimeout: true });
  await waitForElementSafe(page, targetSelector, { throwOnTimeout: true });
  
  await page.dragAndDrop(sourceSelector, targetSelector);
}

/**
 * Assert element visibility with custom message
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 * @param {boolean} shouldBeVisible - Expected visibility state
 * @param {string} message - Custom assertion message
 */
async function assertElementVisibility(page, selector, shouldBeVisible = true, message) {
  const isVisible = await elementExists(page, selector) && await page.isVisible(selector);
  const defaultMessage = `Element '${selector}' should ${shouldBeVisible ? 'be visible' : 'not be visible'}`;
  
  if (shouldBeVisible) {
    expect(isVisible, message || defaultMessage).toBeTruthy();
  } else {
    expect(isVisible, message || defaultMessage).toBeFalsy();
  }
}

/**
 * Wait for element to contain text
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 * @param {string} text - Text to wait for
 * @param {Object} options - Options object
 */
async function waitForText(page, selector, text, options = {}) {
  const { timeout = 10000, exact = false } = options;
  
  await page.waitForFunction(
    ({ selector, text, exact }) => {
      const element = document.querySelector(selector);
      if (!element) return false;
      
      const elementText = element.textContent || '';
      return exact ? elementText === text : elementText.includes(text);
    },
    { selector, text, exact },
    { timeout }
  );
}

/**
 * Get all elements matching selector
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 */
async function getAllElements(page, selector) {
  return await page.$$(selector);
}

/**
 * Get element count
 * @param {Page} page - Playwright page object
 * @param {string} selector - Element selector
 */
async function getElementCount(page, selector) {
  const elements = await getAllElements(page, selector);
  return elements.length;
}

module.exports = {
  waitForElementSafe,
  clickSafe,
  fillSafe,
  takeScreenshot,
  waitForNetworkIdle,
  elementExists,
  getTextSafe,
  waitForUrlPattern,
  scrollIntoView,
  clearBrowserStorage,
  pressShortcut,
  uploadFile,
  hoverElement,
  doubleClickElement,
  dragAndDrop,
  assertElementVisibility,
  waitForText,
  getAllElements,
  getElementCount
};
