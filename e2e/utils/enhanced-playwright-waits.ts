/**
 * Enhanced Playwright Wait Strategies
 *
 * Advanced waiting utilities specifically designed for Playwright e2e tests.
 * Builds upon the existing wait-helpers.ts with more sophisticated strategies
 * for handling dynamic content, complex interactions, and flaky scenarios.
 */

import { Page, Locator, expect, ElementHandle } from '@playwright/test';
import { TEST_TIMEOUTS } from '../../src/utils/test-timeouts';

export interface PlaywrightWaitOptions {
  timeout?: number;
  interval?: number;
  retries?: number;
  retryDelay?: number;
  errorMessage?: string;
  onRetry?: (attempt: number, error: Error) => void;
  stable?: boolean;
  visible?: boolean;
}

export interface ContentLoadingOptions extends PlaywrightWaitOptions {
  loadingSelectors?: string[];
  contentSelectors?: string[];
  errorSelectors?: string[];
  successSelectors?: string[];
  minContentElements?: number;
  waitForImages?: boolean;
  waitForFonts?: boolean;
  networkIdleTimeout?: number;
}

export interface InteractionOptions extends PlaywrightWaitOptions {
  ensureVisible?: boolean;
  ensureEnabled?: boolean;
  ensureStable?: boolean;
  forceClick?: boolean;
  scrollIntoView?: boolean;
}

/**
 * Enhanced content loading waiter for Playwright
 */
export class PlaywrightContentWaiter {
  private static readonly DEFAULT_LOADING_SELECTORS = [
    '[data-testid*="loading"]',
    '.loading',
    '.spinner',
    '.skeleton',
    '.animate-pulse',
    '.animate-spin',
    '[aria-busy="true"]',
    '.placeholder-glow',
    '.loading-state',
    '.shimmer'
  ];

  private static readonly DEFAULT_ERROR_SELECTORS = [
    '[role="alert"]',
    '.error',
    '.alert-destructive',
    '[data-testid*="error"]',
    '.error-message',
    '.failure-state',
    '.toast-error'
  ];

  private static readonly DEFAULT_SUCCESS_SELECTORS = [
    '[data-testid*="success"]',
    '.success',
    '.alert-success',
    '.toast-success',
    '[role="status"]'
  ];

  /**
   * Wait for dynamic content to load with comprehensive checking
   */
  static async waitForDynamicContent(
    page: Page,
    options: ContentLoadingOptions = {}
  ): Promise<void> {
    const {
      timeout = TEST_TIMEOUTS.DATA_FETCH,
      retries = 3,
      retryDelay = TEST_TIMEOUTS.RETRY_DELAY,
      loadingSelectors = this.DEFAULT_LOADING_SELECTORS,
      errorSelectors = this.DEFAULT_ERROR_SELECTORS,
      minContentElements = 1,
      waitForImages = false,
      waitForFonts = false,
      networkIdleTimeout = TEST_TIMEOUTS.NETWORK_IDLE,
      errorMessage = 'Dynamic content failed to load',
      onRetry
    } = options;

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        // Step 1: Wait for network activity to settle
        await page.waitForLoadState('networkidle', { 
          timeout: Math.min(networkIdleTimeout, timeout / 2) 
        });

        // Step 2: Wait for loading indicators to disappear
        await this.waitForLoadingIndicatorsHidden(page, loadingSelectors, {
          timeout: timeout / 3,
          checkMultiple: true
        });

        // Step 3: Check for error states
        await this.checkForErrorStates(page, errorSelectors);

        // Step 4: Verify content is present
        await this.verifyContentPresence(page, minContentElements, timeout / 3);

        // Step 5: Wait for images if requested
        if (waitForImages) {
          await this.waitForImagesLoaded(page, timeout / 4);
        }

        // Step 6: Wait for fonts if requested
        if (waitForFonts) {
          await this.waitForFontsLoaded(page, timeout / 4);
        }

        return; // Success!
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt < retries) {
          onRetry?.(attempt + 1, lastError);
          await page.waitForTimeout(retryDelay * Math.pow(1.5, attempt));
          
          // Refresh page state on retry
          await page.reload({ waitUntil: 'domcontentloaded' });
        }
      }
    }

    throw new Error(`${errorMessage} after ${retries + 1} attempts. Last error: ${lastError?.message}`);
  }

  /**
   * Wait for loading indicators to disappear
   */
  private static async waitForLoadingIndicatorsHidden(
    page: Page, 
    selectors: string[], 
    options: { timeout: number; checkMultiple?: boolean }
  ): Promise<void> {
    const { timeout, checkMultiple = false } = options;
    
    if (checkMultiple) {
      // Check all selectors in parallel
      const promises = selectors.map(async selector => {
        try {
          const elements = page.locator(selector);
          await expect(elements).toBeHidden({ timeout: timeout / selectors.length });
        } catch (error) {
          // Individual selector might not exist, continue
        }
      });
      
      await Promise.allSettled(promises);
    } else {
      // Check if any loading indicator is visible
      for (const selector of selectors) {
        try {
          const element = page.locator(selector).first();
          if (await element.isVisible()) {
            await expect(element).toBeHidden({ timeout });
          }
        } catch (error) {
          // Continue to next selector
        }
      }
    }
  }

  /**
   * Check for error states and throw if found
   */
  private static async checkForErrorStates(page: Page, errorSelectors: string[]): Promise<void> {
    for (const selector of errorSelectors) {
      const errorElement = page.locator(selector).first();
      if (await errorElement.isVisible()) {
        const errorText = await errorElement.textContent();
        throw new Error(`Error state detected: ${errorText || 'Unknown error'}`);
      }
    }
  }

  /**
   * Verify minimum content is present
   */
  private static async verifyContentPresence(page: Page, minElements: number, timeout: number): Promise<void> {
    const contentSelectors = [
      '[data-testid*="content"]',
      'main',
      '.content',
      'article',
      'section[data-loaded="true"]'
    ];

    for (const selector of contentSelectors) {
      try {
        const elements = page.locator(selector);
        const count = await elements.count();
        if (count >= minElements) {
          return; // Found sufficient content
        }
      } catch (error) {
        // Continue to next selector
      }
    }

    // If no content selectors worked, check for any meaningful content
    await page.waitForFunction(
      (minCount) => {
        const textContent = document.body.textContent?.trim() || '';
        const meaningfulElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, span');
        return textContent.length > 50 && meaningfulElements.length >= minCount;
      },
      minElements,
      { timeout }
    );
  }

  /**
   * Wait for images to load
   */
  private static async waitForImagesLoaded(page: Page, timeout: number): Promise<void> {
    await page.waitForFunction(
      () => {
        const images = Array.from(document.querySelectorAll('img'));
        return images.every(img => img.complete && img.naturalHeight !== 0);
      },
      undefined,
      { timeout }
    );
  }

  /**
   * Wait for fonts to load
   */
  private static async waitForFontsLoaded(page: Page, timeout: number): Promise<void> {
    try {
      await page.waitForFunction(
        () => (document as any).fonts?.ready || Promise.resolve(),
        undefined,
        { timeout }
      );
    } catch (error) {
      // Font API might not be available, continue
    }
  }
}

/**
 * Enhanced element interaction waiter
 */
export class PlaywrightInteractionWaiter {
  /**
   * Wait for element to be ready for interaction with comprehensive checks
   */
  static async waitForInteractionReady(
    page: Page,
    selector: string,
    options: InteractionOptions = {}
  ): Promise<Locator> {
    const {
      timeout = TEST_TIMEOUTS.USER_ACTION,
      retries = 3,
      retryDelay = TEST_TIMEOUTS.RETRY_DELAY,
      ensureVisible = true,
      ensureEnabled = true,
      ensureStable = true,
      scrollIntoView = true,
      errorMessage = `Element "${selector}" not ready for interaction`,
      onRetry
    } = options;

    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const element = page.locator(selector);
        
        // Step 1: Wait for element to exist
        await expect(element).toBeAttached({ timeout: timeout / 4 });
        
        // Step 2: Scroll into view if requested
        if (scrollIntoView) {
          await element.scrollIntoViewIfNeeded({ timeout: timeout / 8 });
        }
        
        // Step 3: Wait for visibility
        if (ensureVisible) {
          await expect(element).toBeVisible({ timeout: timeout / 4 });
        }
        
        // Step 4: Wait for enabled state
        if (ensureEnabled) {
          await expect(element).toBeEnabled({ timeout: timeout / 4 });
        }
        
        // Step 5: Wait for stability
        if (ensureStable) {
          await this.waitForElementStability(element, timeout / 4);
        }
        
        // Step 6: Final interaction readiness check
        await this.verifyInteractionReadiness(element);
        
        return element;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt < retries) {
          onRetry?.(attempt + 1, lastError);
          await page.waitForTimeout(retryDelay * Math.pow(1.5, attempt));
        }
      }
    }
    
    throw new Error(`${errorMessage} after ${retries + 1} attempts. Last error: ${lastError?.message}`);
  }

  /**
   * Wait for element to be stable (no movement/resizing)
   */
  private static async waitForElementStability(element: Locator, timeout: number): Promise<void> {
    let previousBox = await element.boundingBox();
    const startTime = Date.now();
    const stabilityPeriod = 200; // ms to consider stable
    let stableStart = Date.now();
    
    while (Date.now() - startTime < timeout) {
      await element.page().waitForTimeout(50);
      
      const currentBox = await element.boundingBox();
      
      if (!previousBox || !currentBox) {
        stableStart = Date.now();
        previousBox = currentBox;
        continue;
      }
      
      const isStable = 
        Math.abs(previousBox.x - currentBox.x) < 1 &&
        Math.abs(previousBox.y - currentBox.y) < 1 &&
        Math.abs(previousBox.width - currentBox.width) < 1 &&
        Math.abs(previousBox.height - currentBox.height) < 1;
      
      if (!isStable) {
        stableStart = Date.now();
        previousBox = currentBox;
        continue;
      }
      
      if (Date.now() - stableStart >= stabilityPeriod) {
        return; // Element is stable
      }
    }
    
    throw new Error('Element did not stabilize within timeout');
  }

  /**
   * Verify element is ready for interaction
   */
  private static async verifyInteractionReadiness(element: Locator): Promise<void> {
    // Check if element is not obscured by other elements
    const isVisible = await element.isVisible();
    if (!isVisible) {
      throw new Error('Element is not visible');
    }
    
    // Check if element has minimum size for interaction
    const box = await element.boundingBox();
    if (!box || box.width < 1 || box.height < 1) {
      throw new Error('Element has insufficient size for interaction');
    }
    
    // Check for common blocking overlays
    const page = element.page();
    const overlays = await page.locator('.modal, .overlay, .backdrop, [data-testid*="overlay"]').count();
    if (overlays > 0) {
      const visibleOverlays = await page.locator('.modal:visible, .overlay:visible, .backdrop:visible').count();
      if (visibleOverlays > 0) {
        throw new Error('Element is obscured by modal or overlay');
      }
    }
  }

  /**
   * Safe click with retry and stability checking
   */
  static async safeClick(
    page: Page,
    selector: string,
    options: InteractionOptions = {}
  ): Promise<void> {
    const {
      forceClick = false,
      timeout = TEST_TIMEOUTS.USER_ACTION,
      retries = 3,
      retryDelay = TEST_TIMEOUTS.RETRY_DELAY,
      onRetry
    } = options;

    const element = await this.waitForInteractionReady(page, selector, options);
    
    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        if (forceClick) {
          await element.click({ force: true, timeout });
        } else {
          await element.click({ timeout });
        }
        
        // Verify click was successful by waiting for state change
        await page.waitForTimeout(100);
        return;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (attempt < retries) {
          onRetry?.(attempt + 1, lastError);
          await page.waitForTimeout(retryDelay);
          
          // Re-verify element is still ready
          await this.waitForInteractionReady(page, selector, { ...options, retries: 1 });
        }
      }
    }
    
    throw new Error(`Safe click failed after ${retries + 1} attempts. Last error: ${lastError?.message}`);
  }

  /**
   * Safe fill with validation
   */
  static async safeFill(
    page: Page,
    selector: string,
    value: string,
    options: InteractionOptions & { clearFirst?: boolean; validateInput?: boolean } = {}
  ): Promise<void> {
    const {
      clearFirst = true,
      validateInput = true,
      timeout = TEST_TIMEOUTS.USER_ACTION,
      retries = 3
    } = options;

    const element = await this.waitForInteractionReady(page, selector, options);
    
    // Clear existing value if requested
    if (clearFirst) {
      await element.clear({ timeout });
    }
    
    // Fill the value
    await element.fill(value, { timeout });
    
    // Validate input if requested
    if (validateInput) {
      await expect(element).toHaveValue(value, { timeout });
    }
  }
}

/**
 * Flaky test retry wrapper with sophisticated retry logic
 */
export class FlakeResistantRunner {
  /**
   * Run a test operation with intelligent retry logic
   */
  static async runWithRetry<T>(
    operation: () => Promise<T>,
    options: {
      maxRetries?: number;
      baseDelay?: number;
      maxDelay?: number;
      backoffFactor?: number;
      retryCondition?: (error: Error, attempt: number) => boolean;
      onRetry?: (attempt: number, error: Error) => void;
      timeout?: number;
    } = {}
  ): Promise<T> {
    const {
      maxRetries = 3,
      baseDelay = TEST_TIMEOUTS.RETRY_DELAY,
      maxDelay = 10000,
      backoffFactor = 2,
      retryCondition = () => true,
      onRetry,
      timeout = TEST_TIMEOUTS.API_COMPLEX
    } = options;

    let lastError: Error | null = null;
    const startTime = Date.now();

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      if (Date.now() - startTime >= timeout) {
        throw new Error(`Operation timeout after ${timeout}ms`);
      }

      try {
        return await operation();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        // Check if we should retry this error
        if (attempt >= maxRetries || !retryCondition(lastError, attempt)) {
          throw lastError;
        }
        
        onRetry?.(attempt + 1, lastError);
        
        // Calculate delay with exponential backoff
        const delay = Math.min(
          baseDelay * Math.pow(backoffFactor, attempt),
          maxDelay
        );
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }

  /**
   * Predefined retry conditions for common flaky scenarios
   */
  static retryConditions = {
    networkErrors: (error: Error) => {
      const networkKeywords = ['timeout', 'network', 'connection', 'refused', 'reset'];
      return networkKeywords.some(keyword => 
        error.message.toLowerCase().includes(keyword)
      );
    },
    
    elementNotFound: (error: Error) => {
      const elementKeywords = ['not attached', 'not visible', 'not found', 'detached'];
      return elementKeywords.some(keyword => 
        error.message.toLowerCase().includes(keyword)
      );
    },
    
    loadingErrors: (error: Error) => {
      const loadingKeywords = ['loading', 'pending', 'busy', 'wait'];
      return loadingKeywords.some(keyword => 
        error.message.toLowerCase().includes(keyword)
      );
    },
    
    allCommonFlakes: (error: Error) => {
      return FlakeResistantRunner.retryConditions.networkErrors(error) ||
             FlakeResistantRunner.retryConditions.elementNotFound(error) ||
             FlakeResistantRunner.retryConditions.loadingErrors(error);
    }
  };
}

/**
 * Convenience wrapper functions for common scenarios
 */
export const playwrightWaitStrategies = {
  /**
   * Wait for page to be fully ready for testing
   */
  async forPageReady(
    page: Page, 
    options: ContentLoadingOptions = {}
  ): Promise<void> {
    await PlaywrightContentWaiter.waitForDynamicContent(page, {
      timeout: TEST_TIMEOUTS.PAGE_LOAD,
      waitForImages: false,
      waitForFonts: false,
      ...options
    });
  },

  /**
   * Wait for SPA route change to complete
   */
  async forRouteChange(
    page: Page,
    expectedUrl?: string | RegExp,
    options: ContentLoadingOptions = {}
  ): Promise<void> {
    if (expectedUrl) {
      await page.waitForURL(expectedUrl, { 
        timeout: TEST_TIMEOUTS.ROUTE_CHANGE,
        waitUntil: 'networkidle'
      });
    }
    
    await this.forPageReady(page, {
      timeout: TEST_TIMEOUTS.ROUTE_CHANGE,
      ...options
    });
  },

  /**
   * Wait for form submission to complete
   */
  async forFormSubmission(
    page: Page,
    submitAction: () => Promise<void>,
    options: ContentLoadingOptions = {}
  ): Promise<{ success: boolean; message?: string }> {
    await submitAction();
    
    try {
      // Wait for success indicators
      const successElement = page.locator(
        '[data-testid*="success"], .success, .alert-success, [role="status"]'
      ).first();
      
      await expect(successElement).toBeVisible({ 
        timeout: options.timeout || TEST_TIMEOUTS.FORM_SUBMISSION 
      });
      
      const message = await successElement.textContent();
      return { success: true, message: message || 'Success' };
    } catch (error) {
      // Check for error indicators
      const errorElement = page.locator(
        '[role="alert"], .error, .alert-destructive, [data-testid*="error"]'
      ).first();
      
      if (await errorElement.isVisible()) {
        const message = await errorElement.textContent();
        return { success: false, message: message || 'Error occurred' };
      }
      
      throw error;
    }
  },

  /**
   * Wait for modal/dialog to be ready for interaction
   */
  async forModalReady(
    page: Page,
    modalSelector: string = '[role="dialog"]',
    options: InteractionOptions = {}
  ): Promise<Locator> {
    return PlaywrightInteractionWaiter.waitForInteractionReady(page, modalSelector, {
      timeout: TEST_TIMEOUTS.MODAL_OPEN,
      ensureStable: true,
      ...options
    });
  },

  /**
   * Wait for API operation to complete
   */
  async forApiOperation(
    page: Page,
    operation: () => Promise<void>,
    options: { expectedResponses?: string[]; timeout?: number } = {}
  ): Promise<void> {
    const { expectedResponses = [], timeout = TEST_TIMEOUTS.API_STANDARD } = options;
    
    if (expectedResponses.length > 0) {
      const responsePromises = expectedResponses.map(url => 
        page.waitForResponse(response => 
          response.url().includes(url) && response.status() < 400,
          { timeout }
        )
      );
      
      await Promise.all([operation(), ...responsePromises]);
    } else {
      await Promise.all([
        operation(),
        page.waitForLoadState('networkidle', { timeout })
      ]);
    }
  }
};

// Export all classes and utilities
export {
  PlaywrightContentWaiter,
  PlaywrightInteractionWaiter,
  FlakeResistantRunner
};

// Legacy compatibility exports
export const waitForDynamicContent = PlaywrightContentWaiter.waitForDynamicContent;
export const waitForInteractionReady = PlaywrightInteractionWaiter.waitForInteractionReady;
export const safeClick = PlaywrightInteractionWaiter.safeClick;
export const safeFill = PlaywrightInteractionWaiter.safeFill;
export const runWithRetry = FlakeResistantRunner.runWithRetry;
