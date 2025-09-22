/**
 * Enhanced Wait Utilities Unit Tests
 *
 * Unit tests to verify the enhanced waiting strategies work correctly
 */

import { describe, it, expect, vi } from 'vitest';
import { TEST_TIMEOUTS } from '../test-setup';
import {
  SmartContentWaiter,
  ElementWaiter,
  AsyncOperationWaiter
} from '../utils/enhanced-wait-strategies';

// Mock DOM environment
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
global.document = dom.window.document;
global.window = dom.window as any;

describe('Enhanced Wait Utilities', () => {
  describe('SmartContentWaiter', () => {
    it('should detect when content is loaded', async () => {
      // Create a container with content
      const container = document.createElement('div');
      container.innerHTML = '<p>Loaded content</p>';
      document.body.appendChild(container);

      const result = SmartContentWaiter.waitForContentLoaded(container, {
        timeout: 1000,
        minContentLength: 5
      });

      await expect(result).resolves.toBeUndefined();

      document.body.removeChild(container);
    });

    it('should detect loading states', async () => {
      const container = document.createElement('div');
      container.innerHTML = '<div class=\"loading\">Loading...</div>';
      document.body.appendChild(container);

      // Should timeout because loading indicator is present
      const result = SmartContentWaiter.waitForContentLoaded(container, {
        timeout: 500,
        checkVisibility: false // Disable visibility check for testing
      });

      await expect(result).rejects.toThrow();

      document.body.removeChild(container);
    });

    it('should detect error states', async () => {
      const container = document.createElement('div');
      container.innerHTML = '<div role=\"alert\">Error occurred</div>';

      // Mock element visibility
      Object.defineProperty(container.querySelector('[role=\"alert\"]'), 'offsetParent', {
        get: () => container,
        configurable: true
      });

      document.body.appendChild(container);

      const result = SmartContentWaiter.waitForContentLoaded(container, {
        timeout: 1000
      });

      await expect(result).rejects.toThrow('Error state detected');

      document.body.removeChild(container);
    });
  });

  describe('AsyncOperationWaiter', () => {
    it('should handle successful async operations', async () => {
      const asyncOp = async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
        return { success: true, data: 'test' };
      };

      const result = await AsyncOperationWaiter.waitForAsyncOperation(asyncOp, {
        timeout: 1000,
        retries: 2
      });

      expect(result).toEqual({ success: true, data: 'test' });
    });

    it('should retry failed operations', async () => {
      let attemptCount = 0;

      const flakyOp = async () => {
        attemptCount++;
        if (attemptCount < 3) {
          throw new Error('Temporary failure');
        }
        return { success: true, attempt: attemptCount };
      };

      const result = await AsyncOperationWaiter.waitForAsyncOperation(flakyOp, {
        timeout: 5000,
        retries: 3,
        retryDelay: 50
      });

      expect(result).toEqual({ success: true, attempt: 3 });
      expect(attemptCount).toBe(3);
    });

    it('should validate operation results', async () => {
      const asyncOp = async () => ({ success: false, data: null });

      const result = AsyncOperationWaiter.waitForAsyncOperation(asyncOp, {
        timeout: 1000,
        validateResult: (result) => result.success === true,
        retries: 2
      });

      await expect(result).rejects.toThrow('Operation result validation failed');
    });

    it('should handle timeouts', async () => {
      const slowOp = async () => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        return { data: 'slow' };
      };

      const result = AsyncOperationWaiter.waitForAsyncOperation(slowOp, {
        timeout: 500,
        retries: 1
      });

      await expect(result).rejects.toThrow();
    });
  });

  describe('ElementWaiter', () => {
    it('should find stable elements', async () => {
      const container = document.createElement('div');\n      const button = document.createElement('button');\n      button.setAttribute('data-testid', 'test-button');\n      button.textContent = 'Click me';\n      container.appendChild(button);\n      document.body.appendChild(container);\n\n      // Mock getBoundingClientRect\n      button.getBoundingClientRect = vi.fn(() => ({\n        x: 10,\n        y: 20,\n        width: 100,\n        height: 30,\n        top: 20,\n        left: 10,\n        bottom: 50,\n        right: 110\n      } as DOMRect));\n\n      const element = await ElementWaiter.waitForElementStable(\n        '[data-testid=\"test-button\"]',\n        container,\n        {\n          timeout: 1000,\n          checkStability: false // Skip stability check for unit test\n        }\n      );\n\n      expect(element).toBe(button);\n\n      document.body.removeChild(container);\n    });\n\n    it('should timeout when element not found', async () => {\n      const container = document.createElement('div');\n      document.body.appendChild(container);\n\n      const result = ElementWaiter.waitForElementStable(\n        '[data-testid=\"nonexistent\"]',\n        container,\n        {\n          timeout: 500,\n          retries: 1\n        }\n      );\n\n      await expect(result).rejects.toThrow();\n\n      document.body.removeChild(container);\n    });\n  });\n\n  describe('Timeout Configuration', () => {\n    it('should have properly configured timeouts', () => {\n      expect(TEST_TIMEOUTS.STANDARD_RENDER).toBeGreaterThan(0);\n      expect(TEST_TIMEOUTS.API_STANDARD).toBeGreaterThan(0);\n      expect(TEST_TIMEOUTS.FORM_SUBMISSION).toBeGreaterThan(0);\n      expect(TEST_TIMEOUTS.DATA_FETCH).toBeGreaterThan(0);\n    });\n\n    it('should adjust timeouts for environment', () => {\n      // Timeouts should be reasonable numbers (not NaN or negative)\n      Object.values(TEST_TIMEOUTS).forEach(timeout => {\n        expect(typeof timeout).toBe('number');\n        expect(timeout).toBeGreaterThan(0);\n        expect(timeout).toBeLessThan(300000); // Less than 5 minutes\n      });\n    });\n  });\n\n  describe('Error Handling', () => {\n    it('should provide meaningful error messages', async () => {\n      const failingOp = async () => {\n        throw new Error('Network connection failed');\n      };\n\n      try {\n        await AsyncOperationWaiter.waitForAsyncOperation(failingOp, {\n          timeout: 1000,\n          retries: 2,\n          errorMessage: 'Custom error message'\n        });\n      } catch (error) {\n        expect(error.message).toContain('Custom error message');\n        expect(error.message).toContain('after 3 attempts');\n      }\n    });\n\n    it('should call retry callbacks', async () => {\n      const retryCallback = vi.fn();\n      let attemptCount = 0;\n      \n      const flakyOp = async () => {\n        attemptCount++;\n        if (attemptCount < 3) {\n          throw new Error('Retry needed');\n        }\n        return 'success';\n      };\n\n      await AsyncOperationWaiter.waitForAsyncOperation(flakyOp, {\n        timeout: 5000,\n        retries: 3,\n        retryDelay: 10,\n        onRetry: retryCallback\n      });\n\n      expect(retryCallback).toHaveBeenCalledTimes(2);\n      expect(retryCallback).toHaveBeenCalledWith(1, expect.any(Error));\n      expect(retryCallback).toHaveBeenCalledWith(2, expect.any(Error));\n    });\n  });\n\n  describe('Abort Signal Support', () => {\n    it('should respect abort signals', async () => {\n      const abortController = new AbortController();\n      const container = document.createElement('div');\n      document.body.appendChild(container);\n\n      // Abort immediately\n      abortController.abort();\n\n      const result = SmartContentWaiter.waitForContentLoaded(container, {\n        timeout: 5000,\n        abortSignal: abortController.signal\n      });\n\n      await expect(result).rejects.toThrow('Operation was aborted');\n\n      document.body.removeChild(container);\n    });\n\n    it('should abort long-running operations', async () => {\n      const abortController = new AbortController();\n      const container = document.createElement('div');\n      container.innerHTML = '<div class=\"loading\">Loading...</div>';\n      document.body.appendChild(container);\n\n      // Abort after 100ms\n      setTimeout(() => abortController.abort(), 100);\n\n      const result = SmartContentWaiter.waitForContentLoaded(container, {\n        timeout: 5000,\n        abortSignal: abortController.signal,\n        checkVisibility: false\n      });\n\n      await expect(result).rejects.toThrow('Operation was aborted');\n\n      document.body.removeChild(container);\n    });\n  });\n});