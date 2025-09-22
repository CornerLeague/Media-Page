/**
 * Enhanced Waiting Strategies Examples
 *
 * This test file demonstrates how to use the new enhanced waiting strategies
 * for better handling of dynamic content, async operations, and flaky scenarios.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  renderWithProviders,
  SmartContentWaiter,
  ElementWaiter,
  AsyncOperationWaiter,
  waitStrategies,
  testUtils,
  TEST_TIMEOUTS
} from '../../test-setup';

import React from 'react';

// Mock component that simulates dynamic loading behavior
const DynamicContentComponent = ({
  loadingDelay = 1000,
  hasError = false,
  asyncData = false
}: {
  loadingDelay?: number;
  hasError?: boolean;
  asyncData?: boolean;
}) => {
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(false);
  const [data, setData] = React.useState<string | null>(null);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (hasError) {
        setError(true);
        setLoading(false);
      } else if (asyncData) {
        // Simulate API call
        fetch('/api/mock-data')
          .then(() => {
            setData('Loaded content from API');
            setLoading(false);
          })
          .catch(() => {
            setError(true);
            setLoading(false);
          });
      } else {
        setLoading(false);
      }
    }, loadingDelay);

    return () => clearTimeout(timer);
  }, [loadingDelay, hasError, asyncData]);

  if (loading) {
    return (
      <div>
        <div data-testid="loading-spinner" className="animate-pulse">
          Loading...
        </div>
        <div aria-busy="true">Content is loading</div>
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" data-testid="error-message">
        Failed to load content
      </div>
    );
  }

  return (
    <div data-testid="content-loaded">
      <h1>Dynamic Content</h1>
      <p>This content loaded after {loadingDelay}ms</p>
      {data && <p data-testid="api-data">{data}</p>}
      <button data-testid="interactive-button">
        Click me
      </button>
    </div>
  );
};

// Mock form component for testing form interactions
const FormComponent = () => {
  const [submitting, setSubmitting] = React.useState(false);
  const [submitted, setSubmitted] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Randomly succeed or fail for testing
    if (Math.random() > 0.7) {
      setError('Submission failed');
    } else {
      setSubmitted(true);
    }
    setSubmitting(false);
  };

  return (
    <form onSubmit={handleSubmit} data-testid="test-form">
      <input
        type="text"
        placeholder="Enter text"
        data-testid="form-input"
      />
      <button
        type="submit"
        disabled={submitting}
        data-testid="submit-button"
      >
        {submitting ? 'Submitting...' : 'Submit'}
      </button>

      {submitting && (
        <div data-testid="submitting-indicator" aria-busy="true">
          Submitting form...
        </div>
      )}

      {submitted && (
        <div data-testid="success-message" className="success">
          Form submitted successfully!
        </div>
      )}

      {error && (
        <div role="alert" data-testid="error-message">
          {error}
        </div>
      )}
    </form>
  );
};

// Mock modal component
const ModalComponent = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div
        role="dialog"
        aria-modal="true"
        data-testid="test-modal"
        className="modal"
      >
        <h2>Modal Title</h2>
        <p>Modal content that takes time to render</p>
        <button onClick={onClose} data-testid="close-modal">
          Close
        </button>
      </div>
    </div>
  );
};

// Mock API for testing
global.fetch = vi.fn();

describe('Enhanced Waiting Strategies Examples', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ data: 'mock data' })
    });
  });

  describe('SmartContentWaiter Examples', () => {
    it('should wait for dynamic content to load', async () => {
      const { container } = renderWithProviders(
        <DynamicContentComponent loadingDelay={500} />
      );

      // Use smart content waiter to wait for loading to complete
      await SmartContentWaiter.waitForContentLoaded(container, {
        timeout: TEST_TIMEOUTS.DATA_FETCH,
        checkVisibility: true,
        minContentLength: 10
      });

      // Content should be loaded and visible
      expect(screen.getByTestId('content-loaded')).toBeVisible();
      expect(screen.getByText('Dynamic Content')).toBeInTheDocument();
    });

    it('should detect and handle error states', async () => {
      const { container } = renderWithProviders(
        <DynamicContentComponent hasError={true} loadingDelay={300} />
      );

      // Smart waiter should detect error state and throw
      await expect(
        SmartContentWaiter.waitForContentLoaded(container, {
          timeout: TEST_TIMEOUTS.DATA_FETCH
        })
      ).rejects.toThrow('Error state detected');
    });

    it('should wait for API-driven content', async () => {
      const { container } = renderWithProviders(
        <DynamicContentComponent asyncData={true} loadingDelay={200} />
      );

      await SmartContentWaiter.waitForContentLoaded(container, {
        timeout: TEST_TIMEOUTS.API_STANDARD,
        checkVisibility: true,
        retries: 3
      });

      expect(screen.getByTestId('api-data')).toBeVisible();
      expect(screen.getByText('Loaded content from API')).toBeInTheDocument();
    });
  });

  describe('ElementWaiter Examples', () => {
    it('should wait for element to be stable', async () => {
      const { container } = renderWithProviders(
        <DynamicContentComponent loadingDelay={300} />
      );

      // Wait for button to be stable and ready for interaction
      const button = await ElementWaiter.waitForElementStable(
        '[data-testid="interactive-button"]',
        container,
        {
          timeout: TEST_TIMEOUTS.USER_ACTION,
          checkStability: true,
          stabilityThreshold: 200
        }
      );

      expect(button).toBeVisible();
      expect(button).toBeEnabled();
    });

    it('should handle elements that move during animation', async () => {
      // Component that moves elements around
      const AnimatedComponent = () => {
        const [position, setPosition] = React.useState(0);

        React.useEffect(() => {
          const interval = setInterval(() => {
            setPosition(p => p < 100 ? p + 10 : 100);
          }, 50);

          return () => clearInterval(interval);
        }, []);

        return (
          <div
            data-testid="moving-element"
            style={{ transform: `translateX(${position}px)` }}
          >
            Moving Element
          </div>
        );
      };

      const { container } = renderWithProviders(<AnimatedComponent />);

      // Wait for element to stabilize
      const element = await ElementWaiter.waitForElementStable(
        '[data-testid="moving-element"]',
        container,
        {
          timeout: TEST_TIMEOUTS.SLOW_ANIMATION,
          stabilityThreshold: 300 // Wait 300ms for stability
        }
      );

      expect(element).toBeVisible();
    });
  });

  describe('AsyncOperationWaiter Examples', () => {
    it('should handle API calls with retry logic', async () => {
      let callCount = 0;
      const flakyApiCall = async () => {
        callCount++;
        if (callCount < 3) {
          throw new Error('Network timeout');
        }
        return { data: 'success', attempt: callCount };
      };

      const result = await AsyncOperationWaiter.waitForAsyncOperation(
        flakyApiCall,
        {
          timeout: TEST_TIMEOUTS.API_STANDARD,
          retries: 3,
          retryDelay: 100,
          onRetry: (attempt, error) => {
            console.log(`Retry attempt ${attempt}: ${error.message}`);
          }
        }
      );

      expect(result.data).toBe('success');
      expect(result.attempt).toBe(3);
    });

    it('should validate API responses', async () => {
      const apiCall = async () => ({ status: 'invalid', data: null });

      await expect(
        AsyncOperationWaiter.waitForAsyncOperation(apiCall, {
          validateResult: (result) => result.status === 'success',
          retries: 2
        })
      ).rejects.toThrow('Operation result validation failed');
    });
  });

  describe('Convenience Functions Examples', () => {
    it('should use testUtils for quick operations', async () => {
      const { container } = renderWithProviders(
        <DynamicContentComponent loadingDelay={400} />
      );

      // Use convenience function
      await testUtils.waitForContent(container);

      expect(screen.getByTestId('content-loaded')).toBeVisible();
    });

    it('should handle form interactions with smart waiting', async () => {
      const user = userEvent.setup();
      renderWithProviders(<FormComponent />);

      // Wait for form to be ready
      const form = await testUtils.waitForFormReady('[data-testid="test-form"]');
      expect(form).toBeVisible();

      // Fill and submit form
      await user.type(screen.getByTestId('form-input'), 'test data');

      // Mock successful submission
      vi.spyOn(Math, 'random').mockReturnValue(0.5); // Ensure success

      await user.click(screen.getByTestId('submit-button'));

      // Wait for form submission to complete
      await testUtils.apiCall(
        async () => {
          // Wait for success message
          const successMessage = screen.queryByTestId('success-message');
          if (!successMessage) {
            throw new Error('Form not submitted yet');
          }
          return successMessage;
        },
        {
          timeout: TEST_TIMEOUTS.FORM_SUBMISSION,
          retries: 5
        }
      );

      expect(screen.getByTestId('success-message')).toBeVisible();
    });

    it('should handle modal interactions', async () => {
      const user = userEvent.setup();
      const MockApp = () => {
        const [isModalOpen, setIsModalOpen] = React.useState(false);

        return (
          <div>
            <button
              onClick={() => setIsModalOpen(true)}
              data-testid="open-modal"
            >
              Open Modal
            </button>
            <ModalComponent
              isOpen={isModalOpen}
              onClose={() => setIsModalOpen(false)}
            />
          </div>
        );
      };

      renderWithProviders(<MockApp />);

      // Open modal
      await user.click(screen.getByTestId('open-modal'));

      // Wait for modal to be ready for interaction
      const modal = await testUtils.waitForModalReady('[data-testid="test-modal"]');
      expect(modal).toBeVisible();

      // Interact with modal
      await user.click(screen.getByTestId('close-modal'));
    });
  });

  describe('waitStrategies Examples', () => {
    it('should use page ready strategy', async () => {
      const { container } = renderWithProviders(
        <DynamicContentComponent loadingDelay={600} />
      );

      // Wait for entire "page" to be ready
      await waitStrategies.forPageReady({
        timeout: TEST_TIMEOUTS.PAGE_LOAD,
        checkVisibility: true,
        checkInteractivity: true
      });

      expect(screen.getByTestId('content-loaded')).toBeVisible();
      expect(screen.getByTestId('interactive-button')).toBeEnabled();
    });

    it('should handle API response waiting', async () => {
      let responseData: any = null;

      const apiOperation = async () => {
        const response = await fetch('/api/test');
        responseData = await response.json();
        return responseData;
      };

      const result = await waitStrategies.forApiResponse(apiOperation, {
        timeout: TEST_TIMEOUTS.API_STANDARD,
        validateResponse: (data) => data && data.data === 'mock data'
      });

      expect(result.data).toBe('mock data');
    });
  });

  describe('Performance and Reliability', () => {
    it('should handle very slow loading content', async () => {
      const { container } = renderWithProviders(
        <DynamicContentComponent loadingDelay={3000} />
      );

      const startTime = Date.now();

      await SmartContentWaiter.waitForContentLoaded(container, {
        timeout: TEST_TIMEOUTS.SLOW_RENDER,
        retries: 2,
        onRetry: (attempt, error) => {
          console.log(`Retry ${attempt} due to: ${error.message}`);
        }
      });

      const endTime = Date.now();

      expect(screen.getByTestId('content-loaded')).toBeVisible();
      expect(endTime - startTime).toBeGreaterThan(2900); // Should take at least 3 seconds
    });

    it('should abort operations when requested', async () => {
      const abortController = new AbortController();

      // Abort after 1 second
      setTimeout(() => abortController.abort(), 1000);

      await expect(
        SmartContentWaiter.waitForContentLoaded(document.body, {
          timeout: TEST_TIMEOUTS.SLOW_RENDER,
          abortSignal: abortController.signal
        })
      ).rejects.toThrow('Operation was aborted');
    });
  });

  describe('Integration with renderWithProviders', () => {
    it('should use enhanced render options', async () => {
      const renderResult = renderWithProviders(
        <DynamicContentComponent loadingDelay={500} />,
        {
          smartWaiting: true,
          waitForContent: true,
          waitOptions: {
            checkVisibility: true,
            checkInteractivity: true
          }
        }
      );

      // Wait for render to complete
      await renderResult.ready;

      expect(screen.getByTestId('content-loaded')).toBeVisible();
    });

    it('should use enhanced waiting methods', async () => {
      const renderResult = renderWithProviders(
        <DynamicContentComponent loadingDelay={300} />
      );

      // Use enhanced waiting methods
      await renderResult.waitForSmartContent({
        checkVisibility: true,
        timeout: TEST_TIMEOUTS.DATA_FETCH
      });

      const button = await renderResult.waitForStableElement(
        '[data-testid="interactive-button"]'
      );

      expect(button).toBeVisible();
      expect(button).toBeEnabled();
    });
  });
});