/**
 * Enhanced Wait Strategies for Dynamic Content
 *
 * Comprehensive waiting utilities designed to handle dynamic content loading,
 * async operations, animations, and state changes with improved reliability.
 * 
 * Features:
 * - Smart content detection
 * - Adaptive timeout handling
 * - Retry mechanisms with exponential backoff
 * - Element stability checking
 * - Performance-aware waiting
 * - Accessibility-ready waiting
 */

import { waitFor } from '@testing-library/react';
import { TEST_TIMEOUTS } from './test-timeouts';

export interface WaitOptions {
  timeout?: number;
  interval?: number;
  retries?: number;
  retryDelay?: number;
  errorMessage?: string;
  onRetry?: (attempt: number, error: Error) => void;
  abortSignal?: AbortSignal;
}

export interface ContentWaitOptions extends WaitOptions {
  loadingSelectors?: string[];
  contentSelectors?: string[];
  errorSelectors?: string[];
  minContentLength?: number;
  checkVisibility?: boolean;
  checkInteractivity?: boolean;
}

export interface ElementWaitOptions extends WaitOptions {
  checkStability?: boolean;
  stabilityThreshold?: number;
  checkBounds?: boolean;
  minSize?: { width: number; height: number };
}

/**
 * Smart content loading detector that adapts to different loading patterns
 */
export class SmartContentWaiter {
  private static readonly DEFAULT_LOADING_SELECTORS = [
    '[data-testid*="loading"]',
    '.loading',
    '.spinner',
    '.skeleton',
    '.animate-pulse',
    '.animate-spin',
    '[aria-busy="true"]',
    '.placeholder-glow',
    '.loading-state'
  ];

  private static readonly DEFAULT_ERROR_SELECTORS = [
    '[role="alert"]',
    '.error',
    '.alert-destructive',
    '[data-testid*="error"]',
    '.error-message',
    '.failure-state'
  ];

  private static readonly DEFAULT_SUCCESS_SELECTORS = [
    '[data-testid*="content"]',
    '[data-testid*="loaded"]',
    '.content-loaded',
    '.data-loaded',
    'main[data-loaded="true"]'
  ];

  /**
   * Wait for dynamic content to finish loading with intelligent detection
   */
  static async waitForContentLoaded(
    container: HTMLElement | Document = document,
    options: ContentWaitOptions = {}
  ): Promise<void> {
    const {
      timeout = TEST_TIMEOUTS.DATA_FETCH,
      interval = TEST_TIMEOUTS.POLL_INTERVAL_STANDARD,
      retries = 3,
      retryDelay = TEST_TIMEOUTS.RETRY_DELAY,
      loadingSelectors = this.DEFAULT_LOADING_SELECTORS,
      errorSelectors = this.DEFAULT_ERROR_SELECTORS,
      minContentLength = 0,
      checkVisibility = true,
      checkInteractivity = false,
      errorMessage = 'Content failed to load within timeout',
      onRetry,
      abortSignal
    } = options;

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        await this.waitForConditionWithTimeout(
          () => this.isContentReady(container, {
            loadingSelectors,
            errorSelectors,
            minContentLength,
            checkVisibility,
            checkInteractivity
          }),
          { timeout, interval, abortSignal }
        );
        return; // Success!
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (abortSignal?.aborted) {
          throw new Error('Operation was aborted');
        }

        if (attempt < retries) {
          onRetry?.(attempt + 1, lastError);
          await this.delay(retryDelay * Math.pow(1.5, attempt)); // Exponential backoff
        }
      }
    }

    throw new Error(`${errorMessage} after ${retries + 1} attempts. Last error: ${lastError?.message}`);
  }

  /**
   * Check if content is ready based on multiple criteria
   */
  private static isContentReady(
    container: HTMLElement | Document,
    options: {
      loadingSelectors: string[];
      errorSelectors: string[];
      minContentLength: number;
      checkVisibility: boolean;
      checkInteractivity: boolean;
    }
  ): boolean {
    const { loadingSelectors, errorSelectors, minContentLength, checkVisibility, checkInteractivity } = options;

    // Check for error states first
    const errorElements = errorSelectors
      .flatMap(selector => Array.from(container.querySelectorAll(selector)))
      .filter(el => el instanceof HTMLElement);
    
    if (errorElements.some(el => this.isElementVisible(el))) {
      throw new Error(`Error state detected: ${errorElements.map(el => el.textContent).join(', ')}`);
    }

    // Check for active loading indicators
    const loadingElements = loadingSelectors
      .flatMap(selector => Array.from(container.querySelectorAll(selector)))
      .filter(el => el instanceof HTMLElement);
    
    if (loadingElements.some(el => this.isElementVisible(el))) {
      return false; // Still loading
    }

    // Check content length if specified
    if (minContentLength > 0) {
      const textContent = container.textContent || '';
      if (textContent.trim().length < minContentLength) {
        return false;
      }
    }

    // Check visibility of main content if requested
    if (checkVisibility) {
      const contentElements = Array.from(container.querySelectorAll('[data-testid*="content"], main, .content'))
        .filter(el => el instanceof HTMLElement);
      
      if (contentElements.length > 0 && !contentElements.some(el => this.isElementVisible(el))) {
        return false;
      }
    }

    // Check interactivity if requested
    if (checkInteractivity) {
      const interactiveElements = Array.from(container.querySelectorAll('button, input, select, textarea, [role="button"]'))
        .filter(el => el instanceof HTMLElement);
      
      if (interactiveElements.length > 0 && !interactiveElements.some(el => this.isElementInteractive(el))) {
        return false;
      }
    }

    return true;
  }

  /**
   * Enhanced element visibility check
   */
  private static isElementVisible(element: HTMLElement): boolean {
    if (!element.isConnected) return false;
    
    const rect = element.getBoundingClientRect();
    if (rect.width === 0 && rect.height === 0) return false;
    
    const style = getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
      return false;
    }
    
    return true;
  }

  /**
   * Check if element is interactive (not disabled or aria-disabled)
   */
  private static isElementInteractive(element: HTMLElement): boolean {
    if (!this.isElementVisible(element)) return false;
    
    if (element instanceof HTMLButtonElement && element.disabled) return false;
    if (element instanceof HTMLInputElement && element.disabled) return false;
    if (element instanceof HTMLSelectElement && element.disabled) return false;
    if (element instanceof HTMLTextAreaElement && element.disabled) return false;
    
    const ariaDisabled = element.getAttribute('aria-disabled');
    if (ariaDisabled === 'true') return false;
    
    return true;
  }

  /**
   * Wait for a condition with timeout and abort signal support
   */
  private static async waitForConditionWithTimeout(
    condition: () => boolean | Promise<boolean>,
    options: { timeout: number; interval: number; abortSignal?: AbortSignal }
  ): Promise<void> {
    const { timeout, interval, abortSignal } = options;
    const startTime = Date.now();

    while (true) {
      if (abortSignal?.aborted) {
        throw new Error('Operation was aborted');
      }

      try {
        const result = await condition();
        if (result) return;
      } catch (error) {
        // Re-throw non-timeout errors immediately
        if (error instanceof Error && !error.message.includes('timeout')) {
          throw error;
        }
      }

      if (Date.now() - startTime >= timeout) {
        throw new Error(`Condition not met within ${timeout}ms`);
      }

      await this.delay(interval);
    }
  }

  /**
   * Promise-based delay utility
   */
  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Enhanced element waiter with stability checks
 */
export class ElementWaiter {
  /**
   * Wait for element to be stable (position, size, visibility)
   */
  static async waitForElementStable(
    selector: string,
    container: HTMLElement | Document = document,
    options: ElementWaitOptions = {}
  ): Promise<HTMLElement> {
    const {
      timeout = TEST_TIMEOUTS.ELEMENT_STABLE,
      interval = TEST_TIMEOUTS.POLL_INTERVAL_STANDARD,
      stabilityThreshold = 100, // ms to wait for stability
      checkBounds = true,
      minSize = { width: 1, height: 1 },
      retries = 3,
      retryDelay = TEST_TIMEOUTS.RETRY_DELAY,
      errorMessage = `Element "${selector}" did not become stable`,
      onRetry,
      abortSignal
    } = options;

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const element = await this.waitForElementPresent(selector, container, { timeout: timeout / (retries + 1) });
        
        if (checkBounds) {
          await this.waitForElementBoundsStable(element, { stabilityThreshold, minSize, abortSignal });
        }
        
        return element;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (abortSignal?.aborted) {
          throw new Error('Operation was aborted');
        }

        if (attempt < retries) {
          onRetry?.(attempt + 1, lastError);
          await SmartContentWaiter['delay'](retryDelay * Math.pow(1.5, attempt));
        }
      }
    }

    throw new Error(`${errorMessage} after ${retries + 1} attempts. Last error: ${lastError?.message}`);
  }

  /**
   * Wait for element to be present in DOM
   */
  private static async waitForElementPresent(
    selector: string,
    container: HTMLElement | Document,
    options: { timeout: number }
  ): Promise<HTMLElement> {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      
      const check = () => {
        const element = container.querySelector(selector);
        if (element instanceof HTMLElement) {
          resolve(element);
          return;
        }
        
        if (Date.now() - startTime >= options.timeout) {
          reject(new Error(`Element "${selector}" not found within ${options.timeout}ms`));
          return;
        }
        
        setTimeout(check, TEST_TIMEOUTS.POLL_INTERVAL);
      };
      
      check();
    });
  }

  /**
   * Wait for element bounds to be stable
   */
  private static async waitForElementBoundsStable(
    element: HTMLElement,
    options: {
      stabilityThreshold: number;
      minSize: { width: number; height: number };
      abortSignal?: AbortSignal;
    }
  ): Promise<void> {
    const { stabilityThreshold, minSize, abortSignal } = options;
    
    let lastRect = element.getBoundingClientRect();
    let stableStart = Date.now();
    
    while (true) {
      if (abortSignal?.aborted) {
        throw new Error('Operation was aborted');
      }
      
      await SmartContentWaiter['delay'](TEST_TIMEOUTS.POLL_INTERVAL);
      
      const currentRect = element.getBoundingClientRect();
      
      // Check if element meets minimum size requirements
      if (currentRect.width < minSize.width || currentRect.height < minSize.height) {
        stableStart = Date.now();
        lastRect = currentRect;
        continue;
      }
      
      // Check if position/size has changed
      const hasChanged = 
        Math.abs(lastRect.x - currentRect.x) > 1 ||
        Math.abs(lastRect.y - currentRect.y) > 1 ||
        Math.abs(lastRect.width - currentRect.width) > 1 ||
        Math.abs(lastRect.height - currentRect.height) > 1;
      
      if (hasChanged) {
        stableStart = Date.now();
        lastRect = currentRect;
        continue;
      }
      
      // Check if we've been stable long enough
      if (Date.now() - stableStart >= stabilityThreshold) {
        return;
      }
    }
  }
}

/**
 * API and async operation waiter with intelligent retry logic
 */
export class AsyncOperationWaiter {
  /**
   * Wait for async operation with exponential backoff retry
   */
  static async waitForAsyncOperation<T>(
    operation: () => Promise<T>,
    options: WaitOptions & {
      validateResult?: (result: T) => boolean;
      transformError?: (error: Error, attempt: number) => Error;
    } = {}
  ): Promise<T> {
    const {
      timeout = TEST_TIMEOUTS.API_STANDARD,
      retries = 3,
      retryDelay = TEST_TIMEOUTS.RETRY_DELAY,
      errorMessage = 'Async operation failed',
      validateResult,
      transformError,
      onRetry,
      abortSignal
    } = options;

    let lastError: Error | null = null;
    const startTime = Date.now();

    for (let attempt = 0; attempt <= retries; attempt++) {
      if (abortSignal?.aborted) {
        throw new Error('Operation was aborted');
      }

      if (Date.now() - startTime >= timeout) {
        throw new Error(`${errorMessage} - global timeout of ${timeout}ms exceeded`);
      }

      try {
        const timeoutPromise = new Promise<never>((_, reject) => {
          const remaining = timeout - (Date.now() - startTime);
          setTimeout(() => reject(new Error('Operation timeout')), Math.max(remaining, 1000));
        });

        const result = await Promise.race([operation(), timeoutPromise]);
        
        if (validateResult && !validateResult(result)) {
          throw new Error('Operation result validation failed');
        }
        
        return result;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        
        if (transformError) {
          lastError = transformError(lastError, attempt);
        }
        
        if (attempt < retries) {
          onRetry?.(attempt + 1, lastError);
          const delay = retryDelay * Math.pow(2, attempt); // Exponential backoff
          await SmartContentWaiter['delay'](Math.min(delay, 5000)); // Cap at 5 seconds
        }
      }
    }

    throw new Error(`${errorMessage} after ${retries + 1} attempts. Last error: ${lastError?.message}`);
  }

  /**
   * Wait for multiple async operations with different strategies
   */
  static async waitForMultipleOperations<T>(
    operations: Array<() => Promise<T>>,
    strategy: 'all' | 'race' | 'allSettled' = 'all',
    options: WaitOptions = {}
  ): Promise<T[]> {
    const {
      timeout = TEST_TIMEOUTS.API_COMPLEX,
      retries = 2,
      errorMessage = 'Multiple operations failed',
      abortSignal
    } = options;

    const operationPromises = operations.map((op, index) => 
      this.waitForAsyncOperation(op, {
        ...options,
        errorMessage: `${errorMessage} - operation ${index}`,
        timeout: timeout / operations.length,
        retries
      })
    );

    switch (strategy) {
      case 'all':
        return await Promise.all(operationPromises);
      
      case 'race':
        const result = await Promise.race(operationPromises);
        return [result];
      
      case 'allSettled':
        const results = await Promise.allSettled(operationPromises);
        const fulfilled = results
          .filter((result): result is PromiseFulfilledResult<T> => result.status === 'fulfilled')
          .map(result => result.value);
        
        if (fulfilled.length === 0) {
          const errors = results
            .filter((result): result is PromiseRejectedResult => result.status === 'rejected')
            .map(result => result.reason);
          throw new Error(`All operations failed: ${errors.join(', ')}`);
        }
        
        return fulfilled;
      
      default:
        throw new Error(`Unknown strategy: ${strategy}`);
    }
  }
}

/**
 * Animation and transition waiter
 */
export class AnimationWaiter {
  /**
   * Wait for CSS animations and transitions to complete
   */
  static async waitForAnimationsComplete(
    element: HTMLElement,
    options: WaitOptions = {}
  ): Promise<void> {
    const {
      timeout = TEST_TIMEOUTS.STANDARD_ANIMATION,
      interval = TEST_TIMEOUTS.POLL_INTERVAL,
      abortSignal
    } = options;

    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      if (abortSignal?.aborted) {
        throw new Error('Operation was aborted');
      }

      const style = getComputedStyle(element);
      const hasAnimations = style.animationName !== 'none' && style.animationName !== '';
      const hasTransitions = style.transitionProperty !== 'none' && style.transitionProperty !== '';
      
      if (!hasAnimations && !hasTransitions) {
        return;
      }
      
      await SmartContentWaiter['delay'](interval);
    }

    // Final check with event listeners for more precision
    return new Promise((resolve, reject) => {
      const cleanup = () => {
        element.removeEventListener('animationend', onAnimationEnd);
        element.removeEventListener('transitionend', onTransitionEnd);
        clearTimeout(timeoutId);
      };

      const onAnimationEnd = () => {
        cleanup();
        resolve();
      };

      const onTransitionEnd = () => {
        cleanup();
        resolve();
      };

      const timeoutId = setTimeout(() => {
        cleanup();
        resolve(); // Don't reject, just resolve after timeout
      }, TEST_TIMEOUTS.FAST_ANIMATION);

      element.addEventListener('animationend', onAnimationEnd, { once: true });
      element.addEventListener('transitionend', onTransitionEnd, { once: true });
    });
  }
}

/**
 * Convenience functions that combine multiple waiting strategies
 */
export const waitStrategies = {
  /**
   * Wait for page to be fully loaded with content
   */
  async forPageReady(options: ContentWaitOptions = {}): Promise<void> {
    await SmartContentWaiter.waitForContentLoaded(document, {
      timeout: TEST_TIMEOUTS.PAGE_LOAD,
      checkVisibility: true,
      checkInteractivity: false,
      ...options
    });
  },

  /**
   * Wait for form to be ready for interaction
   */
  async forFormReady(formSelector: string, options: ElementWaitOptions = {}): Promise<HTMLElement> {
    const form = await ElementWaiter.waitForElementStable(formSelector, document, {
      timeout: TEST_TIMEOUTS.FORM_INTERACTION,
      checkBounds: true,
      ...options
    });
    
    // Wait for form inputs to be interactive
    await SmartContentWaiter.waitForContentLoaded(form, {
      checkInteractivity: true,
      timeout: TEST_TIMEOUTS.USER_ACTION
    });
    
    return form;
  },

  /**
   * Wait for modal/dialog to be ready
   */
  async forModalReady(modalSelector: string = '[role="dialog"]', options: ElementWaitOptions = {}): Promise<HTMLElement> {
    const modal = await ElementWaiter.waitForElementStable(modalSelector, document, {
      timeout: TEST_TIMEOUTS.MODAL_OPEN,
      stabilityThreshold: 200,
      ...options
    });
    
    // Wait for animations to complete
    await AnimationWaiter.waitForAnimationsComplete(modal);
    
    return modal;
  },

  /**
   * Wait for API response and content update
   */
  async forApiResponse<T>(
    apiCall: () => Promise<T>,
    options: WaitOptions & { validateResponse?: (response: T) => boolean } = {}
  ): Promise<T> {
    const { validateResponse, ...waitOptions } = options;
    
    return AsyncOperationWaiter.waitForAsyncOperation(apiCall, {
      timeout: TEST_TIMEOUTS.API_STANDARD,
      retries: 3,
      validateResult: validateResponse,
      ...waitOptions
    });
  }
};

// Export everything for convenience
export {
  SmartContentWaiter,
  ElementWaiter,
  AsyncOperationWaiter,
  AnimationWaiter
};

// Legacy compatibility
export const enhancedWaitFor = waitFor;
export const smartWaitFor = SmartContentWaiter.waitForContentLoaded;
export const waitForStableElement = ElementWaiter.waitForElementStable;
export const waitForAsyncOp = AsyncOperationWaiter.waitForAsyncOperation;
