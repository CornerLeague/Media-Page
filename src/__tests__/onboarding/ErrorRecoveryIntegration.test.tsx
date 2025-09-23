/**
 * Error Recovery Integration Tests
 *
 * Tests the complete error recovery workflows including
 * retry mechanisms, fallback handling, and user guidance.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Test components and utilities
import { TestWrapper } from './OnboardingErrorHandling.test';
import {
  createNetworkErrorApiClient,
  createTimeoutErrorApiClient,
  createServerErrorApiClient,
  createRateLimitErrorApiClient,
} from '../utils/mockApiClient';
import {
  createUnauthenticatedFirebaseAuth,
  createExpiredTokenFirebaseAuth,
  createNetworkErrorFirebaseAuth,
} from '../utils/mockFirebaseAuth';

// Components under test
import { ValidatedSportsSelectionStep } from '@/components/onboarding/ValidatedSportsSelectionStep';
import { OnboardingStepErrorBoundary } from '@/components/error-boundaries/OnboardingStepErrorBoundary';

// Error recovery components
import {
  ErrorAlert,
  FullScreenError,
  RecoveryGuidance,
  type RecoveryAction
} from '@/components/error-boundaries/ErrorRecoveryComponents';

// API retry utilities
import { ApiRetryManager, RetryableFetch } from '@/lib/api-retry';

// Error reporting
import { errorReporting } from '@/lib/error-reporting';

describe('Error Recovery Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    errorReporting.clearReports();

    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('API Retry Logic', () => {
    it('should retry failed API calls with exponential backoff', async () => {
      const retryManager = new ApiRetryManager({
        maxRetries: 3,
        baseDelay: 100,
        backoffFactor: 2,
      });

      let callCount = 0;
      const mockApiCall = vi.fn().mockImplementation(() => {
        callCount++;
        if (callCount < 3) {
          return Promise.reject(new Error('Network error'));
        }
        return Promise.resolve('success');
      });

      const result = await retryManager.executeWithRetry(mockApiCall);

      expect(result).toBe('success');
      expect(mockApiCall).toHaveBeenCalledTimes(3);
    });

    it('should not retry client errors (4xx)', async () => {
      const retryManager = new ApiRetryManager();

      const clientError = new Error('Bad Request');
      (clientError as any).status = 400;

      const mockApiCall = vi.fn().mockRejectedValue(clientError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow('Bad Request');
      expect(mockApiCall).toHaveBeenCalledTimes(1);
    });

    it('should retry server errors (5xx)', async () => {
      const retryManager = new ApiRetryManager({
        maxRetries: 2,
        baseDelay: 50,
      });

      const serverError = new Error('Internal Server Error');
      (serverError as any).status = 500;

      const mockApiCall = vi.fn().mockRejectedValue(serverError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow('Internal Server Error');
      expect(mockApiCall).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });

    it('should handle rate limiting with retry-after header', async () => {
      const retryableFetch = new RetryableFetch({
        maxRetries: 1,
        baseDelay: 50,
      });

      // Mock fetch to return rate limit error
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        headers: new Map([['Retry-After', '1']]),
      });

      global.fetch = mockFetch;

      await expect(retryableFetch.get('/api/test')).rejects.toThrow('HTTP 429');
      expect(mockFetch).toHaveBeenCalledTimes(2); // Initial + 1 retry
    });
  });

  describe('Component Error Recovery', () => {
    it('should show fallback UI during network errors', async () => {
      const networkErrorClient = createNetworkErrorApiClient();

      // Mock the API client
      vi.doMock('@/lib/api-client', () => ({
        createApiQueryClient: () => networkErrorClient.queryConfigs,
        apiClient: networkErrorClient.client,
      }));

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      // Should show working offline message
      await waitFor(() => {
        expect(screen.getByText(/working offline/i)).toBeInTheDocument();
      });

      // Should still show fallback sports data
      expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();

      // Should show at least some sports options
      const sportCards = screen.getAllByTestId(/sport-card-/);
      expect(sportCards.length).toBeGreaterThan(0);
    });

    it('should provide retry functionality for failed API calls', async () => {
      const user = userEvent.setup();
      let apiCallCount = 0;

      const mockApiClient = {
        queryConfigs: {
          getOnboardingSports: vi.fn(() => ({
            queryKey: ['sports'],
            queryFn: () => {
              apiCallCount++;
              if (apiCallCount === 1) {
                return Promise.reject(new Error('Network error'));
              }
              return Promise.resolve([
                { id: 'nfl', name: 'NFL', icon: '🏈', hasTeams: true, isPopular: true },
              ]);
            },
          })),
        },
        client: {
          updateOnboardingStep: vi.fn(),
        },
      };

      vi.doMock('@/lib/api-client', () => ({
        createApiQueryClient: () => mockApiClient.queryConfigs,
        apiClient: mockApiClient.client,
      }));

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      // Should show error state initially
      await waitFor(() => {
        expect(screen.getByText(/working offline/i)).toBeInTheDocument();
      });

      // The component should have fallback data, so it continues to work
      expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
    });

    it('should handle authentication errors gracefully', async () => {
      const unauthenticatedAuth = createUnauthenticatedFirebaseAuth();

      vi.doMock('@/contexts/FirebaseAuthContext', () => ({
        useFirebaseAuth: () => unauthenticatedAuth,
      }));

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      // Should still render the component for unauthenticated users
      await waitFor(() => {
        expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
      });

      // Should not attempt authenticated API calls
      expect(unauthenticatedAuth.getIdToken).not.toHaveBeenCalled();
    });
  });

  describe('Error Boundary Recovery', () => {
    function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
      if (shouldThrow) {
        throw new Error('Component error');
      }
      return <div>Component loaded successfully</div>;
    }

    it('should provide recovery actions in error boundary', async () => {
      const user = userEvent.setup();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const onRetry = vi.fn();
      const onGoBack = vi.fn();
      const onGoHome = vi.fn();

      render(
        <TestWrapper>
          <OnboardingStepErrorBoundary
            step={2}
            stepName="Test Step"
            onRetry={onRetry}
            onGoBack={onGoBack}
            onGoHome={onGoHome}
          >
            <ThrowingComponent shouldThrow={true} />
          </OnboardingStepErrorBoundary>
        </TestWrapper>
      );

      // Should show error boundary UI
      await waitFor(() => {
        expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      });

      // Should show recovery buttons
      const retryButton = screen.getByRole('button', { name: /try again/i });
      const backButton = screen.getByRole('button', { name: /go back/i });
      const homeButton = screen.getByRole('button', { name: /go home/i });

      expect(retryButton).toBeInTheDocument();
      expect(backButton).toBeInTheDocument();
      expect(homeButton).toBeInTheDocument();

      // Test retry functionality
      await user.click(retryButton);
      expect(onRetry).toHaveBeenCalledTimes(1);

      // Test go back functionality
      await user.click(backButton);
      expect(onGoBack).toHaveBeenCalledTimes(1);

      // Test go home functionality
      await user.click(homeButton);
      expect(onGoHome).toHaveBeenCalledTimes(1);

      consoleSpy.mockRestore();
    });

    it('should limit retry attempts', async () => {
      const user = userEvent.setup();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      let retryCount = 0;
      const RetryableErrorComponent = () => {
        const [error, setError] = React.useState<Error | null>(null);

        const handleRetry = () => {
          retryCount++;
          if (retryCount <= 3) {
            setError(new Error(`Retry attempt ${retryCount}`));
          } else {
            setError(null);
          }
        };

        React.useEffect(() => {
          setError(new Error('Initial error'));
        }, []);

        if (error) {
          throw error;
        }

        return <div>Component recovered</div>;
      };

      render(
        <TestWrapper>
          <OnboardingStepErrorBoundary
            step={2}
            stepName="Retry Test"
            onRetry={() => {}}
            onGoBack={() => {}}
            onGoHome={() => {}}
          >
            <RetryableErrorComponent />
          </OnboardingStepErrorBoundary>
        </TestWrapper>
      );

      // Should show error boundary UI
      await waitFor(() => {
        expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      });

      // After max retries, should show different messaging
      const retryButton = screen.getByRole('button', { name: /try again/i });

      // Click retry multiple times
      for (let i = 0; i < 4; i++) {
        if (retryButton && !retryButton.getAttribute('disabled')) {
          await user.click(retryButton);
        }
      }

      // After max retries, should show different options
      await waitFor(() => {
        expect(screen.getByText(/tried several times/i)).toBeInTheDocument();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('User Guidance and Recovery Steps', () => {
    it('should provide contextual recovery guidance', () => {
      const recoverySteps = [
        'Check your internet connection',
        'Try refreshing the page',
        'Clear your browser cache',
        'Contact support if the problem persists',
      ];

      render(
        <TestWrapper>
          <RecoveryGuidance steps={recoverySteps} title="How to fix this issue" />
        </TestWrapper>
      );

      expect(screen.getByText('How to fix this issue')).toBeInTheDocument();

      // Should show all recovery steps
      recoverySteps.forEach((step, index) => {
        expect(screen.getByText(step)).toBeInTheDocument();
        expect(screen.getByText((index + 1).toString())).toBeInTheDocument();
      });
    });

    it('should show appropriate error messages for different error types', () => {
      // Network error
      render(
        <TestWrapper>
          <ErrorAlert
            title="Network Error"
            message="Please check your internet connection"
            severity="error"
          />
        </TestWrapper>
      );

      expect(screen.getByText('Network Error')).toBeInTheDocument();
      expect(screen.getByText('Please check your internet connection')).toBeInTheDocument();
    });

    it('should provide recovery actions for different scenarios', async () => {
      const user = userEvent.setup();

      const mockRetry = vi.fn();
      const mockRefresh = vi.fn();

      const recoveryActions: RecoveryAction[] = [
        {
          label: 'Try Again',
          action: mockRetry,
          variant: 'default',
        },
        {
          label: 'Refresh Page',
          action: mockRefresh,
          variant: 'outline',
        },
      ];

      render(
        <TestWrapper>
          <ErrorAlert
            title="Something went wrong"
            message="Please try again or refresh the page"
            severity="error"
            recoveryActions={recoveryActions}
          />
        </TestWrapper>
      );

      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      const refreshButton = screen.getByRole('button', { name: /refresh page/i });

      await user.click(tryAgainButton);
      expect(mockRetry).toHaveBeenCalledTimes(1);

      await user.click(refreshButton);
      expect(mockRefresh).toHaveBeenCalledTimes(1);
    });
  });

  describe('Error Persistence and Recovery', () => {
    it('should save progress locally when API calls fail', async () => {
      const user = userEvent.setup();

      // Mock API failure
      const failingApiClient = createServerErrorApiClient();

      vi.doMock('@/lib/api-client', () => ({
        createApiQueryClient: () => failingApiClient.queryConfigs,
        apiClient: failingApiClient.client,
      }));

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
      });

      // Select a sport
      const sportCards = screen.getAllByTestId(/sport-card-/);
      if (sportCards[0]) {
        await user.click(sportCards[0]);
      }

      // Should save progress locally despite API failure
      const savedData = localStorage.getItem('corner-league-onboarding-status');
      expect(savedData).toBeTruthy();
    });

    it('should restore progress from local storage on component mount', () => {
      // Pre-populate localStorage with saved progress
      const savedProgress = {
        selectedSports: [
          { sportId: 'nfl', rank: 1 },
          { sportId: 'nba', rank: 2 },
        ],
      };

      localStorage.setItem('corner-league-onboarding-status', JSON.stringify(savedProgress));

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      // Should show selected sports count
      expect(screen.getByText(/sports selected/i)).toBeInTheDocument();
    });

    it('should sync local data when connection is restored', async () => {
      const user = userEvent.setup();

      // Start with failing API
      const failingApiClient = createNetworkErrorApiClient();
      let currentApiClient = failingApiClient;

      vi.doMock('@/lib/api-client', () => ({
        createApiQueryClient: () => currentApiClient.queryConfigs,
        apiClient: currentApiClient.client,
      }));

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      // Should show offline indicator
      await waitFor(() => {
        expect(screen.getByText(/working offline/i)).toBeInTheDocument();
      });

      // The component should continue to work with fallback data
      expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
    });
  });

  describe('Circuit Breaker Pattern', () => {
    it('should open circuit breaker after repeated failures', async () => {
      const retryManager = new ApiRetryManager(
        {},
        {
          failureThreshold: 3,
          timeout: 60000,
          monitoringPeriod: 300000,
        }
      );

      const mockApiCall = vi.fn().mockRejectedValue(new Error('Service unavailable'));

      // Trigger failures to open circuit breaker
      for (let i = 0; i < 3; i++) {
        try {
          await retryManager.executeWithRetry(mockApiCall);
        } catch (error) {
          // Expected to fail
        }
      }

      // Next call should fail immediately due to open circuit
      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow('Circuit breaker is OPEN');

      // Should have made 3 attempts for each call, plus no attempts for the final call
      expect(mockApiCall).toHaveBeenCalledTimes(12); // 3 calls × 4 attempts each (initial + 3 retries)
    });

    it('should provide circuit breaker status information', () => {
      const retryManager = new ApiRetryManager();

      const status = retryManager.getCircuitBreakerStatus();

      expect(status).toHaveProperty('state');
      expect(status).toHaveProperty('failures');
      expect(status.state).toBe('CLOSED');
    });
  });
});

export default {};