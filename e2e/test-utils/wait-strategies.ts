/**
 * Wait Strategies for Reliable Test Execution
 * Provides robust waiting utilities to prevent flaky tests
 */

import { Page, Locator, expect } from '@playwright/test';

export type WaitCondition = 'visible' | 'hidden' | 'stable' | 'attached' | 'detached';

export interface WaitOptions {
  timeout?: number;
  interval?: number;
  throwOnTimeout?: boolean;
}

/**
 * Advanced wait strategies for reliable test execution
 */
export class WaitStrategies {
  constructor(private page: Page) {}

  /**
   * Wait for an element to meet a specific condition
   */
  async waitForElement(
    locator: Locator,
    condition: WaitCondition = 'visible',
    timeout: number = 10000
  ): Promise<void> {
    const options = { timeout, state: condition as any };

    switch (condition) {
      case 'visible':
        await locator.waitFor({ ...options, state: 'visible' });
        break;
      case 'hidden':
        await locator.waitFor({ ...options, state: 'hidden' });
        break;
      case 'stable':
        // Wait for element to be visible and stable (not moving)
        await locator.waitFor({ timeout, state: 'visible' });
        await this.page.waitForTimeout(100); // Small delay for stability
        break;
      case 'attached':
        await locator.waitFor({ ...options, state: 'attached' });
        break;
      case 'detached':
        await locator.waitFor({ ...options, state: 'detached' });
        break;
    }
  }

  /**
   * Wait for element to be enabled and clickable
   */
  async waitForEnabled(locator: Locator, timeout: number = 10000): Promise<void> {
    await this.waitForElement(locator, 'visible', timeout);

    await this.page.waitForFunction(
      (element) => {
        if (!element) return false;
        return !element.disabled && !element.hasAttribute('aria-disabled');
      },
      locator.first(),
      { timeout }
    );
  }

  /**
   * Wait for element to contain specific text
   */
  async waitForText(
    locator: Locator,
    text: string | RegExp,
    timeout: number = 10000
  ): Promise<void> {
    await this.waitForElement(locator, 'visible', timeout);

    if (typeof text === 'string') {
      await expect(locator).toContainText(text, { timeout });
    } else {
      await expect(locator).toContainText(text, { timeout });
    }
  }

  /**
   * Wait for element attribute to have specific value
   */
  async waitForAttribute(
    locator: Locator,
    attributeName: string,
    expectedValue: string | RegExp,
    timeout: number = 10000
  ): Promise<void> {
    await this.waitForElement(locator, 'visible', timeout);

    await this.page.waitForFunction(
      ({ element, attr, value, isRegex }) => {
        if (!element) return false;
        const actualValue = element.getAttribute(attr);
        if (!actualValue) return false;

        if (isRegex) {
          const regex = new RegExp(value);
          return regex.test(actualValue);
        } else {
          return actualValue === value;
        }
      },
      {
        element: locator.first(),
        attr: attributeName,
        value: expectedValue instanceof RegExp ? expectedValue.source : expectedValue,
        isRegex: expectedValue instanceof RegExp
      },
      { timeout }
    );
  }

  /**
   * Wait for network requests to settle
   */
  async waitForNetworkIdle(timeout: number = 10000): Promise<void> {
    await this.page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Wait for API response with specific pattern
   */
  async waitForApiResponse(
    urlPattern: string | RegExp,
    timeout: number = 15000
  ): Promise<void> {
    await this.page.waitForResponse(
      response => {
        const url = response.url();
        if (typeof urlPattern === 'string') {
          return url.includes(urlPattern);
        } else {
          return urlPattern.test(url);
        }
      },
      { timeout }
    );
  }

  /**
   * Wait for multiple conditions to be met
   */
  async waitForAll(
    conditions: Array<() => Promise<void>>,
    timeout: number = 10000
  ): Promise<void> {
    const startTime = Date.now();

    await Promise.all(
      conditions.map(async (condition) => {
        const remainingTime = Math.max(0, timeout - (Date.now() - startTime));
        if (remainingTime <= 0) {
          throw new Error('Timeout exceeded while waiting for multiple conditions');
        }
        return condition();
      })
    );
  }

  /**
   * Wait for any one of multiple conditions to be met
   */
  async waitForAny(
    conditions: Array<() => Promise<void>>,
    timeout: number = 10000
  ): Promise<number> {
    const promises = conditions.map(async (condition, index) => {
      try {
        await condition();
        return index;
      } catch (error) {
        throw { index, error };
      }
    });

    try {
      return await Promise.race(promises);
    } catch (error) {
      throw new Error(`None of the conditions were met within ${timeout}ms`);
    }
  }

  /**
   * Wait with exponential backoff retry
   */
  async waitWithRetry<T>(
    action: () => Promise<T>,
    options: WaitOptions & { maxRetries?: number } = {}
  ): Promise<T> {
    const {
      timeout = 10000,
      interval = 500,
      maxRetries = 5,
      throwOnTimeout = true
    } = options;

    const startTime = Date.now();
    let lastError: Error | null = null;
    let retryCount = 0;

    while (retryCount < maxRetries && (Date.now() - startTime) < timeout) {
      try {
        return await action();
      } catch (error) {
        lastError = error as Error;
        retryCount++;

        if (retryCount < maxRetries && (Date.now() - startTime) < timeout) {
          // Exponential backoff: interval * 2^retryCount
          const delay = Math.min(interval * Math.pow(2, retryCount - 1), 2000);
          await this.page.waitForTimeout(delay);
        }
      }
    }

    if (throwOnTimeout) {
      throw new Error(
        `Action failed after ${retryCount} retries and ${Date.now() - startTime}ms. Last error: ${lastError?.message}`
      );
    }

    return null as T;
  }

  /**
   * Wait for element count to match expected value
   */
  async waitForCount(
    locator: Locator,
    expectedCount: number,
    timeout: number = 10000
  ): Promise<void> {
    await this.page.waitForFunction(
      ({ selector, count }) => {
        const elements = document.querySelectorAll(selector);
        return elements.length === count;
      },
      { selector: locator, count: expectedCount },
      { timeout }
    );
  }

  /**
   * Wait for page to be fully loaded and interactive
   */
  async waitForPageReady(timeout: number = 15000): Promise<void> {
    // Wait for DOM content loaded
    await this.page.waitForLoadState('domcontentloaded', { timeout });

    // Wait for all resources to load
    await this.page.waitForLoadState('load', { timeout });

    // Wait for network to be idle
    await this.page.waitForLoadState('networkidle', { timeout: timeout / 2 });

    // Additional wait for any animations or dynamic content
    await this.page.waitForTimeout(200);
  }

  /**
   * Wait for element to be in viewport
   */
  async waitForInViewport(locator: Locator, timeout: number = 10000): Promise<void> {
    await this.waitForElement(locator, 'visible', timeout);

    await this.page.waitForFunction(
      (element) => {
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const windowWidth = window.innerWidth;

        return (
          rect.top >= 0 &&
          rect.left >= 0 &&
          rect.bottom <= windowHeight &&
          rect.right <= windowWidth
        );
      },
      locator.first(),
      { timeout }
    );
  }

  /**
   * Smart wait that combines multiple strategies
   */
  async smartWait(locator: Locator, options: {
    condition?: WaitCondition;
    text?: string | RegExp;
    attribute?: { name: string; value: string | RegExp };
    timeout?: number;
    stable?: boolean;
  } = {}): Promise<void> {
    const {
      condition = 'visible',
      text,
      attribute,
      timeout = 10000,
      stable = false
    } = options;

    // Start with basic element condition
    await this.waitForElement(locator, condition, timeout);

    // Wait for text if specified
    if (text) {
      await this.waitForText(locator, text, timeout);
    }

    // Wait for attribute if specified
    if (attribute) {
      await this.waitForAttribute(locator, attribute.name, attribute.value, timeout);
    }

    // Wait for stability if requested
    if (stable) {
      await this.waitForStability(locator, 200);
    }
  }

  /**
   * Wait for element to stop moving/changing
   */
  async waitForStability(locator: Locator, stableTime: number = 500): Promise<void> {
    let lastPosition: { x: number; y: number; width: number; height: number } | null = null;
    const checkInterval = 50;
    let stableCount = 0;
    const requiredStableChecks = Math.ceil(stableTime / checkInterval);

    while (stableCount < requiredStableChecks) {
      const currentPosition = await locator.boundingBox();

      if (!currentPosition) {
        await this.page.waitForTimeout(checkInterval);
        continue;
      }

      if (lastPosition &&
          lastPosition.x === currentPosition.x &&
          lastPosition.y === currentPosition.y &&
          lastPosition.width === currentPosition.width &&
          lastPosition.height === currentPosition.height) {
        stableCount++;
      } else {
        stableCount = 0;
      }

      lastPosition = currentPosition;
      await this.page.waitForTimeout(checkInterval);
    }
  }

  /**
   * Wait for animations to complete
   */
  async waitForAnimations(timeout: number = 5000): Promise<void> {
    await this.page.waitForFunction(
      () => {
        const animatedElements = document.querySelectorAll('*');
        for (const element of animatedElements) {
          const computedStyle = window.getComputedStyle(element);
          if (computedStyle.animationName !== 'none' || computedStyle.transitionProperty !== 'none') {
            return false;
          }
        }
        return true;
      },
      {},
      { timeout }
    );
  }
}