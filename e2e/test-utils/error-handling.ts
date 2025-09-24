/**
 * Error Handling and Retry Strategies for Test Reliability
 * Provides robust error handling, retry mechanisms, and failure recovery
 */

import { Page, Locator, expect, TestInfo } from '@playwright/test';
import { WaitStrategies } from './wait-strategies';

export interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  exponentialBackoff: boolean;
  retryCondition?: (error: Error) => boolean;
}

export interface ErrorContext {
  testName: string;
  step: string;
  timestamp: string;
  errorMessage: string;
  stackTrace?: string;
  pageUrl?: string;
  screenshotPath?: string;
  consoleLogs?: string[];
  networkErrors?: string[];
}

/**
 * Error Handling and Retry Utilities
 */
export class ErrorHandlingStrategies {
  private waitStrategies: WaitStrategies;

  constructor(private page: Page, private testInfo?: TestInfo) {
    this.waitStrategies = new WaitStrategies(page);
  }

  /**
   * Execute action with retry logic
   */
  async executeWithRetry<T>(
    action: () => Promise<T>,
    config: Partial<RetryConfig> = {},
    context?: string
  ): Promise<T> {
    const {
      maxRetries = 3,
      retryDelay = 1000,
      exponentialBackoff = true,
      retryCondition
    } = config;

    let lastError: Error;
    let attempt = 0;

    while (attempt <= maxRetries) {
      try {
        return await action();
      } catch (error) {
        lastError = error as Error;
        attempt++;

        // Check if this error should trigger a retry
        if (retryCondition && !retryCondition(lastError)) {
          throw lastError;
        }

        if (attempt <= maxRetries) {
          const delay = exponentialBackoff ? retryDelay * Math.pow(2, attempt - 1) : retryDelay;

          console.log(`Attempt ${attempt} failed${context ? ` (${context})` : ''}: ${lastError.message}`);
          console.log(`Retrying in ${delay}ms...`);

          await this.page.waitForTimeout(delay);
        }
      }
    }

    throw new Error(
      `Action failed after ${maxRetries} retries${context ? ` (${context})` : ''}. Last error: ${lastError!.message}`
    );
  }

  /**
   * Handle common test failures with specific recovery strategies
   */
  async handleCommonFailures<T>(action: () => Promise<T>, context?: string): Promise<T> {
    return this.executeWithRetry(
      action,
      {
        maxRetries: 3,
        retryDelay: 1000,
        exponentialBackoff: true,
        retryCondition: (error) => this.isRetryableError(error)
      },
      context
    );
  }

  /**
   * Determine if an error is retryable
   */
  private isRetryableError(error: Error): boolean {
    const retryablePatterns = [
      /timeout/i,
      /network.*failed/i,
      /connection.*refused/i,
      /element.*not.*found/i,
      /element.*not.*visible/i,
      /element.*not.*attached/i,
      /navigation.*timeout/i,
      /waiting.*for.*locator/i,
      /page.*closed/i,
      /execution.*context.*destroyed/i
    ];

    return retryablePatterns.some(pattern => pattern.test(error.message));
  }

  /**
   * Safe element interaction with error handling
   */
  async safeClick(
    locator: Locator,
    options: {
      timeout?: number;
      retries?: number;
      scrollIntoView?: boolean;
      waitForEnabled?: boolean;
    } = {}
  ): Promise<void> {
    const {
      timeout = 10000,
      retries = 3,
      scrollIntoView = true,
      waitForEnabled = true
    } = options;

    await this.executeWithRetry(async () => {
      // Wait for element to be visible
      await this.waitStrategies.waitForElement(locator, 'visible', timeout);

      // Scroll into view if needed
      if (scrollIntoView) {
        await locator.scrollIntoViewIfNeeded({ timeout: timeout / 2 });
      }

      // Wait for element to be enabled if requested
      if (waitForEnabled) {
        await this.waitStrategies.waitForEnabled(locator, timeout / 2);
      }

      // Perform the click
      await locator.click({ timeout });
    }, {
      maxRetries: retries,
      retryDelay: 500,
      exponentialBackoff: false
    }, `clicking element`);
  }

  /**
   * Safe text input with error handling
   */
  async safeType(
    locator: Locator,
    text: string,
    options: {
      timeout?: number;
      retries?: number;
      clearFirst?: boolean;
    } = {}
  ): Promise<void> {
    const { timeout = 10000, retries = 3, clearFirst = true } = options;

    await this.executeWithRetry(async () => {
      await this.waitStrategies.waitForElement(locator, 'visible', timeout);

      if (clearFirst) {
        await locator.clear({ timeout });
      }

      await locator.type(text, { timeout });
    }, {
      maxRetries: retries,
      retryDelay: 500
    }, `typing text: ${text}`);
  }

  /**
   * Safe navigation with error handling
   */
  async safeNavigate(
    url: string,
    options: {
      timeout?: number;
      retries?: number;
      waitForLoad?: boolean;
    } = {}
  ): Promise<void> {
    const { timeout = 30000, retries = 3, waitForLoad = true } = options;

    await this.executeWithRetry(async () => {
      await this.page.goto(url, {
        timeout,
        waitUntil: waitForLoad ? 'networkidle' : 'domcontentloaded'
      });

      if (waitForLoad) {
        await this.waitStrategies.waitForPageReady(timeout / 2);
      }
    }, {
      maxRetries: retries,
      retryDelay: 2000,
      exponentialBackoff: true
    }, `navigating to ${url}`);
  }

  /**
   * Safe element wait with fallback strategies
   */
  async safeWaitForElement(
    locator: Locator,
    condition: 'visible' | 'hidden' | 'attached' = 'visible',
    timeout: number = 10000
  ): Promise<boolean> {
    try {
      await this.waitStrategies.waitForElement(locator, condition, timeout);
      return true;
    } catch (error) {
      // Try alternative strategies
      if (condition === 'visible') {
        // Try waiting for attachment first, then visibility
        try {
          await this.waitStrategies.waitForElement(locator, 'attached', timeout / 2);
          await this.page.waitForTimeout(500);
          await this.waitStrategies.waitForElement(locator, 'visible', timeout / 2);
          return true;
        } catch {
          return false;
        }
      }
      return false;
    }
  }

  /**
   * Capture error context for debugging
   */
  async captureErrorContext(error: Error, step: string): Promise<ErrorContext> {
    const timestamp = new Date().toISOString();
    const testName = this.testInfo?.title || 'unknown-test';

    const context: ErrorContext = {
      testName,
      step,
      timestamp,
      errorMessage: error.message,
      stackTrace: error.stack,
      pageUrl: this.page.url()
    };

    try {
      // Capture screenshot
      if (this.testInfo) {
        const screenshotPath = `${this.testInfo.outputDir}/error-${Date.now()}.png`;
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
        context.screenshotPath = screenshotPath;
      }

      // Capture console logs
      context.consoleLogs = await this.page.evaluate(() => {
        // @ts-ignore - accessing console logs if available
        return window.__testConsole || [];
      }).catch(() => []);

      // Capture network errors
      context.networkErrors = await this.page.evaluate(() => {
        // @ts-ignore - accessing network errors if available
        return window.__testNetworkErrors || [];
      }).catch(() => []);

    } catch (captureError) {
      console.warn('Failed to capture error context:', captureError);
    }

    return context;
  }

  /**
   * Log detailed error information
   */
  logError(context: ErrorContext): void {
    console.error('\n=== TEST ERROR DETAILS ===');
    console.error(`Test: ${context.testName}`);
    console.error(`Step: ${context.step}`);
    console.error(`Time: ${context.timestamp}`);
    console.error(`URL: ${context.pageUrl}`);
    console.error(`Error: ${context.errorMessage}`);

    if (context.stackTrace) {
      console.error(`Stack: ${context.stackTrace}`);
    }

    if (context.screenshotPath) {
      console.error(`Screenshot: ${context.screenshotPath}`);
    }

    if (context.consoleLogs && context.consoleLogs.length > 0) {
      console.error(`Console logs: ${JSON.stringify(context.consoleLogs, null, 2)}`);
    }

    if (context.networkErrors && context.networkErrors.length > 0) {
      console.error(`Network errors: ${JSON.stringify(context.networkErrors, null, 2)}`);
    }

    console.error('=========================\n');
  }

  /**
   * Graceful error handling wrapper
   */
  async withErrorHandling<T>(
    action: () => Promise<T>,
    stepName: string,
    options: {
      retries?: number;
      screenshot?: boolean;
      continueOnError?: boolean;
    } = {}
  ): Promise<T | null> {
    const { retries = 1, screenshot = true, continueOnError = false } = options;

    try {
      return await this.executeWithRetry(action, { maxRetries: retries }, stepName);
    } catch (error) {
      const context = await this.captureErrorContext(error as Error, stepName);
      this.logError(context);

      if (continueOnError) {
        console.warn(`Continuing despite error in step: ${stepName}`);
        return null;
      } else {
        throw error;
      }
    }
  }

  /**
   * Network error simulation and recovery
   */
  async simulateNetworkIssues(
    type: 'timeout' | 'failure' | 'slow' | 'intermittent',
    duration: number = 5000
  ): Promise<void> {
    switch (type) {
      case 'timeout':
        await this.page.route('**/*', async route => {
          await new Promise(resolve => setTimeout(resolve, duration));
          await route.abort('timedout');
        });
        break;

      case 'failure':
        await this.page.route('**/*', async route => {
          await route.abort('failed');
        });
        break;

      case 'slow':
        await this.page.route('**/*', async route => {
          await new Promise(resolve => setTimeout(resolve, duration));
          await route.continue();
        });
        break;

      case 'intermittent':
        let requestCount = 0;
        await this.page.route('**/*', async route => {
          requestCount++;
          if (requestCount % 3 === 0) {
            await route.abort('failed');
          } else {
            await route.continue();
          }
        });
        break;
    }
  }

  /**
   * Recovery strategies for specific failures
   */
  async recoverFromFailure(failureType: 'navigation' | 'element' | 'api' | 'timeout'): Promise<void> {
    switch (failureType) {
      case 'navigation':
        // Try refreshing the page
        await this.page.reload({ waitUntil: 'networkidle', timeout: 15000 });
        break;

      case 'element':
        // Wait a bit longer and try scrolling
        await this.page.waitForTimeout(1000);
        await this.page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
        await this.page.waitForTimeout(500);
        break;

      case 'api':
        // Clear storage and restart
        await this.page.evaluate(() => {
          localStorage.clear();
          sessionStorage.clear();
        });
        await this.page.waitForTimeout(1000);
        break;

      case 'timeout':
        // Wait for network to settle
        await this.waitStrategies.waitForNetworkIdle(10000);
        break;
    }
  }

  /**
   * Test stability helpers
   */
  async ensureStableState(timeout: number = 3000): Promise<void> {
    // Wait for animations to complete
    await this.waitStrategies.waitForAnimations(timeout);

    // Wait for network to be idle
    await this.waitStrategies.waitForNetworkIdle(timeout);

    // Additional stability wait
    await this.page.waitForTimeout(200);
  }

  /**
   * Conditional retry based on error patterns
   */
  createRetryCondition(patterns: RegExp[]): (error: Error) => boolean {
    return (error: Error) => {
      return patterns.some(pattern => pattern.test(error.message));
    };
  }

  /**
   * Smart recovery that attempts multiple strategies
   */
  async smartRecovery(error: Error): Promise<void> {
    console.log(`Attempting smart recovery for error: ${error.message}`);

    // Try different recovery strategies based on error type
    if (/navigation|timeout|network/i.test(error.message)) {
      await this.recoverFromFailure('navigation');
    } else if (/element.*not.*found|not.*visible|not.*attached/i.test(error.message)) {
      await this.recoverFromFailure('element');
    } else if (/api|server|request/i.test(error.message)) {
      await this.recoverFromFailure('api');
    } else {
      await this.recoverFromFailure('timeout');
    }

    // Ensure stable state after recovery
    await this.ensureStableState();
  }
}