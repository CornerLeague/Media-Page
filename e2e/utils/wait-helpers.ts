/**
 * Enhanced Playwright Wait Helper Utilities
 *
 * Provides robust wait utilities with configurable timeouts for different scenarios
 * in Playwright e2e tests. Designed to handle slow loading elements and async operations.
 */

import { Page, Locator, expect } from '@playwright/test';

// Import shared timeout configurations
const TIMEOUTS = {
  // Quick operations
  INSTANT: 100,
  FAST_RENDER: 1000,
  STANDARD_RENDER: 3000,
  SLOW_RENDER: 8000,

  // Animations
  FAST_ANIMATION: 500,
  STANDARD_ANIMATION: 1500,
  SLOW_ANIMATION: 4000,

  // User interactions
  USER_ACTION: 1500,
  USER_ACTION_SLOW: 4000,

  // API and data loading
  API_CALL: 5000,
  API_CALL_SLOW: 10000,
  DATA_LOADING: 8000,

  // Component specific
  MODAL_OPEN: 2000,
  DROPDOWN_OPEN: 1500,
  FORM_SUBMISSION: 6000,

  // Network and page loading
  PAGE_LOAD: 15000,
  NETWORK_IDLE: 10000,

  // Accessibility audits
  A11Y_AUDIT: 8000,
  A11Y_AUDIT_COMPLEX: 15000,

  // Polling intervals
  POLL_INTERVAL: 100,
  POLL_INTERVAL_SLOW: 250,
} as const;

// Environment adjustments
const isCI = process.env.CI === 'true';
const isDebug = process.env.DEBUG === 'true';

function adjustTimeout(baseTimeout: number): number {
  let multiplier = 1;
  if (isDebug) multiplier = 3;
  else if (isCI) multiplier = 2;
  return Math.round(baseTimeout * multiplier);
}

export interface WaitOptions {
  timeout?: number;
  interval?: number;
  errorMessage?: string;
  stable?: boolean;
  visible?: boolean;
}

export interface LoadingOptions extends WaitOptions {
  loadingSelectors?: string[];
  errorSelectors?: string[];
  successSelectors?: string[];
}

/**
 * Wait for an element to become visible with configurable timeout
 */
export async function waitForElementVisible(
  page: Page,
  selector: string,
  options: WaitOptions = {}
): Promise<Locator> {
  const {
    timeout = adjustTimeout(TIMEOUTS.STANDARD_RENDER),
    errorMessage = `Element "${selector}" did not become visible`
  } = options;

  const element = page.locator(selector);
  await expect(element).toBeVisible({ timeout });
  return element;
}

/**
 * Wait for an element to become hidden with configurable timeout
 */
export async function waitForElementHidden(
  page: Page,
  selector: string,
  options: WaitOptions = {}
): Promise<void> {
  const {
    timeout = adjustTimeout(TIMEOUTS.STANDARD_RENDER),
    errorMessage = `Element "${selector}" did not become hidden`
  } = options;

  const element = page.locator(selector);
  await expect(element).toBeHidden({ timeout });
}

/**
 * Wait for multiple elements to become visible
 */
export async function waitForElementsVisible(
  page: Page,
  selectors: string[],
  options: WaitOptions = {}
): Promise<Locator[]> {
  const {
    timeout = adjustTimeout(TIMEOUTS.SLOW_RENDER),
  } = options;

  const elements = selectors.map(selector => page.locator(selector));

  await Promise.all(
    elements.map(element =>
      expect(element).toBeVisible({ timeout })
    )
  );

  return elements;
}

/**
 * Wait for a condition to be true with configurable polling
 */
export async function waitForCondition(
  page: Page,
  condition: () => Promise<boolean> | boolean,
  options: WaitOptions = {}
): Promise<void> {
  const {
    timeout = adjustTimeout(TIMEOUTS.STANDARD_RENDER),
    interval = TIMEOUTS.POLL_INTERVAL,
    errorMessage = 'Condition was not met within timeout'
  } = options;

  await page.waitForFunction(condition, undefined, { timeout, polling: interval });
}

/**
 * Wait for loading states to complete
 */
export async function waitForLoadingComplete(
  page: Page,
  options: LoadingOptions = {}
): Promise<void> {
  const {
    timeout = adjustTimeout(TIMEOUTS.DATA_LOADING),
    interval = TIMEOUTS.POLL_INTERVAL,
    loadingSelectors = [
      '[data-testid*="loading"]',
      '.loading',
      '.animate-spin',
      '.animate-pulse',
      '[aria-busy="true"]',
      '.spinner'
    ]
  } = options;

  // Wait for all loading indicators to disappear
  for (const selector of loadingSelectors) {
    try {
      const loadingElement = page.locator(selector);
      await expect(loadingElement).toBeHidden({
        timeout: Math.min(timeout / loadingSelectors.length, 2000)
      });
    } catch (error) {
      // Continue if specific loading indicator not found
      continue;
    }
  }

  // Additional wait for any async operations to settle
  await page.waitForLoadState('networkidle', {
    timeout: Math.min(timeout, adjustTimeout(TIMEOUTS.NETWORK_IDLE))
  });
}

/**
 * Wait for form submission and response
 */
export async function waitForFormSubmission(
  page: Page,
  submitAction: () => Promise<void>,
  options: LoadingOptions = {}
): Promise<{ success: boolean; message?: string }> {
  const {
    timeout = adjustTimeout(TIMEOUTS.FORM_SUBMISSION),
    successSelectors = [
      '[data-testid*="success"]',
      '.success',
      '[role="status"]',
      '.alert:not(.alert-destructive)'
    ],
    errorSelectors = [
      '[role="alert"]',
      '.error',
      '.alert-destructive',
      '[data-testid*="error"]'
    ]
  } = options;

  // Execute the submit action
  await submitAction();

  // Wait for either success or error response
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    // Check for success indicators
    for (const selector of successSelectors) {
      const successElement = page.locator(selector);
      if (await successElement.isVisible()) {
        const message = await successElement.textContent();
        return { success: true, message: message || 'Success' };
      }
    }

    // Check for error indicators
    for (const selector of errorSelectors) {
      const errorElement = page.locator(selector);
      if (await errorElement.isVisible()) {
        const message = await errorElement.textContent();
        return { success: false, message: message || 'Error occurred' };
      }
    }

    await page.waitForTimeout(TIMEOUTS.POLL_INTERVAL);
  }

  throw new Error(`Form submission timeout after ${timeout}ms`);
}

/**
 * Wait for API calls to complete
 */
export async function waitForApiCalls(
  page: Page,
  expectedCalls: string[] = [],
  options: WaitOptions = {}
): Promise<void> {
  const {
    timeout = adjustTimeout(TIMEOUTS.API_CALL),
  } = options;

  if (expectedCalls.length === 0) {
    // Wait for network to be idle
    await page.waitForLoadState('networkidle', { timeout });
    return;
  }

  // Wait for specific API calls
  const apiPromises = expectedCalls.map(apiPath =>
    page.waitForResponse(response =>
      response.url().includes(apiPath) && response.status() < 400,
      { timeout }
    )
  );

  await Promise.all(apiPromises);
}

/**
 * Wait for modal or dialog to open and be ready for interaction
 */
export async function waitForModalOpen(
  page: Page,
  modalSelector: string = '[role="dialog"]',
  options: WaitOptions = {}
): Promise<Locator> {
  const {
    timeout = adjustTimeout(TIMEOUTS.MODAL_OPEN),
  } = options;

  const modal = page.locator(modalSelector);

  // Wait for modal to be visible
  await expect(modal).toBeVisible({ timeout });

  // Wait for modal to be stable (animations complete)
  await modal.waitFor({ state: 'attached', timeout });

  // Ensure modal is ready for interaction
  await page.waitForTimeout(adjustTimeout(TIMEOUTS.FAST_ANIMATION));

  return modal;
}

/**
 * Wait for dropdown or popover to open
 */
export async function waitForDropdownOpen(
  page: Page,
  dropdownSelector: string,
  options: WaitOptions = {}
): Promise<Locator> {
  const {
    timeout = adjustTimeout(TIMEOUTS.DROPDOWN_OPEN),
  } = options;

  const dropdown = page.locator(dropdownSelector);
  await expect(dropdown).toBeVisible({ timeout });

  // Wait for animations to complete
  await page.waitForTimeout(adjustTimeout(TIMEOUTS.FAST_ANIMATION));

  return dropdown;
}

/**
 * Wait for page navigation to complete
 */
export async function waitForNavigation(
  page: Page,
  navigationAction: () => Promise<void>,
  expectedUrl?: string | RegExp,
  options: WaitOptions = {}
): Promise<void> {
  const {
    timeout = adjustTimeout(TIMEOUTS.PAGE_LOAD),
  } = options;

  const navigationPromise = page.waitForURL(
    expectedUrl || '*',
    { timeout, waitUntil: 'networkidle' }
  );

  await navigationAction();
  await navigationPromise;
}

/**
 * Wait for animations to complete
 */
export async function waitForAnimationsComplete(
  page: Page,
  animationType: 'fast' | 'standard' | 'slow' = 'standard'
): Promise<void> {
  const timeouts = {
    fast: adjustTimeout(TIMEOUTS.FAST_ANIMATION),
    standard: adjustTimeout(TIMEOUTS.STANDARD_ANIMATION),
    slow: adjustTimeout(TIMEOUTS.SLOW_ANIMATION)
  };

  await page.waitForTimeout(timeouts[animationType]);

  // Wait for CSS animations to complete
  await page.waitForFunction(() => {
    const elements = document.querySelectorAll('*');
    for (const element of elements) {
      const computedStyle = getComputedStyle(element);
      if (computedStyle.animationName !== 'none' ||
          computedStyle.transitionProperty !== 'none') {
        return false;
      }
    }
    return true;
  }, undefined, { timeout: timeouts[animationType] });
}

/**
 * Wait for accessibility audit to complete
 */
export async function waitForAccessibilityReady(
  page: Page,
  options: WaitOptions = {}
): Promise<void> {
  const {
    timeout = adjustTimeout(TIMEOUTS.A11Y_AUDIT),
  } = options;

  // Wait for page to be stable
  await page.waitForLoadState('networkidle', { timeout });

  // Wait for any pending DOM mutations
  await page.waitForFunction(() => {
    return !document.querySelector('[aria-busy="true"]') &&
           !document.querySelector('.loading') &&
           !document.querySelector('[data-testid*="loading"]');
  }, undefined, { timeout });

  // Additional wait for screen readers and assistive technology
  await page.waitForTimeout(adjustTimeout(500));
}

/**
 * Wait for element to be stable (not moving/changing)
 */
export async function waitForElementStable(
  page: Page,
  selector: string,
  options: WaitOptions = {}
): Promise<Locator> {
  const {
    timeout = adjustTimeout(TIMEOUTS.STANDARD_RENDER),
  } = options;

  const element = page.locator(selector);

  // Wait for element to be visible
  await expect(element).toBeVisible({ timeout });

  // Wait for element to be stable
  await element.waitFor({ state: 'attached', timeout });

  // Check that element position is stable
  let previousBox = await element.boundingBox();
  await page.waitForTimeout(100);
  const currentBox = await element.boundingBox();

  if (!previousBox || !currentBox) {
    throw new Error('Element bounding box not available');
  }

  const isStable =
    Math.abs(previousBox.x - currentBox.x) < 1 &&
    Math.abs(previousBox.y - currentBox.y) < 1 &&
    Math.abs(previousBox.width - currentBox.width) < 1 &&
    Math.abs(previousBox.height - currentBox.height) < 1;

  if (!isStable) {
    // Element is still moving, wait a bit more
    await page.waitForTimeout(adjustTimeout(TIMEOUTS.FAST_ANIMATION));
  }

  return element;
}

/**
 * Wait with retry logic for flaky operations
 */
export async function waitWithRetry<T>(
  operation: () => Promise<T>,
  options: {
    retries?: number;
    retryDelay?: number;
    timeout?: number;
    errorMessage?: string;
  } = {}
): Promise<T> {
  const {
    retries = 3,
    retryDelay = 1000,
    timeout = adjustTimeout(TIMEOUTS.API_CALL),
    errorMessage = 'Operation failed after retries'
  } = options;

  let lastError: Error;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error(`${errorMessage} - timeout`)), timeout)
      );

      return await Promise.race([operation(), timeoutPromise]);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }

  throw lastError!;
}

/**
 * Smart wait that detects the type of operation and applies appropriate timeout
 */
export async function smartWait(
  page: Page,
  action: 'render' | 'animation' | 'api' | 'navigation' | 'form' | 'modal',
  complexity: 'fast' | 'standard' | 'slow' = 'standard'
): Promise<void> {
  const timeoutMatrix = {
    render: {
      fast: TIMEOUTS.FAST_RENDER,
      standard: TIMEOUTS.STANDARD_RENDER,
      slow: TIMEOUTS.SLOW_RENDER
    },
    animation: {
      fast: TIMEOUTS.FAST_ANIMATION,
      standard: TIMEOUTS.STANDARD_ANIMATION,
      slow: TIMEOUTS.SLOW_ANIMATION
    },
    api: {
      fast: TIMEOUTS.API_CALL,
      standard: TIMEOUTS.API_CALL,
      slow: TIMEOUTS.API_CALL_SLOW
    },
    navigation: {
      fast: TIMEOUTS.PAGE_LOAD,
      standard: TIMEOUTS.PAGE_LOAD,
      slow: TIMEOUTS.PAGE_LOAD
    },
    form: {
      fast: TIMEOUTS.FORM_SUBMISSION,
      standard: TIMEOUTS.FORM_SUBMISSION,
      slow: TIMEOUTS.FORM_SUBMISSION
    },
    modal: {
      fast: TIMEOUTS.MODAL_OPEN,
      standard: TIMEOUTS.MODAL_OPEN,
      slow: TIMEOUTS.MODAL_OPEN
    }
  };

  const timeout = adjustTimeout(timeoutMatrix[action][complexity]);
  await page.waitForTimeout(timeout);
}

// Export timeout constants for direct use
export { TIMEOUTS };