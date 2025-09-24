/**
 * useOnboardingApiWithRetry Hook
 *
 * A custom hook that provides API methods specifically for onboarding with
 * built-in retry logic, error recovery, and offline handling.
 */

import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/components/ui/use-toast';
import { apiClient, ApiClientError } from '@/lib/api-client';
import { RetryConfig } from '@/lib/api-retry';
import useOnlineStatus from '@/hooks/useOnlineStatus';
import useSessionRecovery from '@/hooks/useSessionRecovery';

interface ApiError {
  code: string;
  message: string;
  statusCode?: number;
  isRetryable?: boolean;
  isOfflineError?: boolean;
}

interface ApiState {
  isLoading: boolean;
  isRetrying: boolean;
  error: ApiError | null;
  retryCount: number;
  lastAttemptTime: number | null;
}

export interface UseOnboardingApiResult {
  // State
  apiState: ApiState;
  isOnline: boolean;
  canRetry: boolean;

  // Sports API
  getSports: () => Promise<any[]>;
  getTeams: (sportIds: string[]) => Promise<any[]>;

  // Onboarding API
  getOnboardingStatus: () => Promise<any>;
  updateOnboardingStep: (stepData: any) => Promise<any>;
  completeOnboarding: (data: any) => Promise<any>;

  // Error recovery
  clearError: () => void;
  retryLastRequest: () => Promise<void>;
  forceSync: () => Promise<void>;
}

const defaultRetryConfig: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  backoffFactor: 2,
  jitter: true,
};

export function useOnboardingApiWithRetry(): UseOnboardingApiResult {
  const queryClient = useQueryClient();
  const { isOnline, connectionQuality } = useOnlineStatus({ showToasts: false });
  const { saveStepProgress, syncWithAPI } = useSessionRecovery();

  // Local state
  const [apiState, setApiState] = useState<ApiState>({
    isLoading: false,
    isRetrying: false,
    error: null,
    retryCount: 0,
    lastAttemptTime: null,
  });

  const [lastFailedRequest, setLastFailedRequest] = useState<(() => Promise<any>) | null>(null);

  /**
   * Enhanced error handler
   */
  const handleApiError = useCallback((error: any, requestFn?: () => Promise<any>) => {
    const now = Date.now();
    let apiError: ApiError;

    if (error instanceof ApiClientError) {
      apiError = {
        code: error.code,
        message: error.message,
        statusCode: error.statusCode,
        isRetryable: error.statusCode >= 500 || error.statusCode === 429,
        isOfflineError: error.code === 'NETWORK_ERROR',
      };
    } else {
      // Network or unknown error
      apiError = {
        code: 'UNKNOWN_ERROR',
        message: error.message || 'An unexpected error occurred',
        isRetryable: true,
        isOfflineError: !isOnline,
      };
    }

    setApiState(prev => ({
      isLoading: false,
      isRetrying: false,
      error: apiError,
      retryCount: prev.retryCount + 1,
      lastAttemptTime: now,
    }));

    // Store the failed request for retry
    if (requestFn) {
      setLastFailedRequest(() => requestFn);
    }

    // Show user-friendly error message
    const friendlyMessage = getFriendlyErrorMessage(apiError, isOnline, connectionQuality);

    toast({
      title: 'Request Failed',
      description: friendlyMessage,
      variant: 'destructive',
    });

    console.error('API Error:', apiError);
  }, [isOnline, connectionQuality]);

  /**
   * Execute API request with error handling and retry logic
   */
  const executeWithRetry = useCallback(async <T>(
    requestFn: () => Promise<T>,
    customRetryConfig?: Partial<RetryConfig>,
    saveLocally?: (data: T) => void
  ): Promise<T> => {
    setApiState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // If offline and we have local data, use it
      if (!isOnline && saveLocally) {
        // Try to get cached data
        const cachedData = queryClient.getQueryData(['cached-request']);
        if (cachedData) {
          setApiState(prev => ({ ...prev, isLoading: false }));
          return cachedData as T;
        }
      }

      // Execute request with retry logic
      const result = await apiClient.requestWithRetry('/endpoint', {}, {
        ...defaultRetryConfig,
        ...customRetryConfig,
        onRetry: (attempt, error) => {
          setApiState(prev => ({
            ...prev,
            isRetrying: true,
            retryCount: attempt,
          }));

          toast({
            title: 'Retrying...',
            description: `Attempt ${attempt} of ${customRetryConfig?.maxRetries || defaultRetryConfig.maxRetries}`,
            variant: 'default',
          });
        },
      });

      // Success - clear error state and save locally if needed
      setApiState(prev => ({
        ...prev,
        isLoading: false,
        isRetrying: false,
        error: null,
        retryCount: 0,
      }));

      if (saveLocally) {
        saveLocally(result);
      }

      setLastFailedRequest(null);
      return result;

    } catch (error) {
      handleApiError(error, requestFn);
      throw error;
    }
  }, [isOnline, queryClient, handleApiError]);

  /**
   * Get onboarding sports
   */
  const getSports = useCallback(async () => {
    return executeWithRetry(
      () => apiClient.getOnboardingSports(),
      { maxRetries: 2 }, // Fewer retries for static data
      (data) => {
        // Cache sports data locally
        queryClient.setQueryData(['onboarding', 'sports'], data);
      }
    );
  }, [executeWithRetry, queryClient]);

  /**
   * Get onboarding teams
   */
  const getTeams = useCallback(async (sportIds: string[]) => {
    return executeWithRetry(
      () => apiClient.getOnboardingTeams(sportIds),
      { maxRetries: 2 },
      (data) => {
        // Cache teams data locally
        queryClient.setQueryData(['onboarding', 'teams', sportIds], data);
      }
    );
  }, [executeWithRetry, queryClient]);

  /**
   * Get onboarding status
   */
  const getOnboardingStatus = useCallback(async () => {
    return executeWithRetry(
      () => apiClient.getOnboardingStatus(),
      { maxRetries: 3 },
      (data) => {
        queryClient.setQueryData(['auth', 'onboarding-status'], data);
      }
    );
  }, [executeWithRetry, queryClient]);

  /**
   * Update onboarding step
   */
  const updateOnboardingStep = useCallback(async (stepData: any) => {
    return executeWithRetry(
      () => apiClient.updateOnboardingStep(stepData),
      {
        maxRetries: 3,
        retryCondition: (error) => {
          // Only retry server errors, not validation errors
          return error.statusCode >= 500;
        },
      },
      (data) => {
        // Save step progress locally
        saveStepProgress(stepData.step, stepData.data);
        queryClient.setQueryData(['onboarding', 'step', stepData.step], data);
      }
    );
  }, [executeWithRetry, saveStepProgress, queryClient]);

  /**
   * Complete onboarding
   */
  const completeOnboarding = useCallback(async (data: any) => {
    return executeWithRetry(
      () => apiClient.completeOnboarding(data),
      {
        maxRetries: 5, // More retries for critical operation
        maxDelay: 30000, // Longer delay for completion
      },
      (result) => {
        // Clear onboarding cache
        queryClient.removeQueries({ queryKey: ['onboarding'] });
        queryClient.setQueryData(['user', 'current'], result);
      }
    );
  }, [executeWithRetry, queryClient]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setApiState(prev => ({
      ...prev,
      error: null,
      retryCount: 0,
    }));
    setLastFailedRequest(null);
  }, []);

  /**
   * Retry the last failed request
   */
  const retryLastRequest = useCallback(async () => {
    if (!lastFailedRequest) {
      throw new Error('No request to retry');
    }

    setApiState(prev => ({ ...prev, isRetrying: true }));

    try {
      await lastFailedRequest();
      setApiState(prev => ({
        ...prev,
        isRetrying: false,
        error: null,
        retryCount: 0,
      }));
      setLastFailedRequest(null);

      toast({
        title: 'Request Successful',
        description: 'The retry was successful.',
        variant: 'default',
      });
    } catch (error) {
      setApiState(prev => ({ ...prev, isRetrying: false }));
      handleApiError(error);
      throw error;
    }
  }, [lastFailedRequest, handleApiError]);

  /**
   * Force sync with server
   */
  const forceSync = useCallback(async () => {
    if (!isOnline) {
      throw new Error('Cannot sync while offline');
    }

    try {
      const result = await syncWithAPI();

      toast({
        title: 'Sync Complete',
        description: `Synced ${result.success} items successfully.`,
        variant: 'default',
      });

      return result;
    } catch (error) {
      toast({
        title: 'Sync Failed',
        description: 'Failed to sync with server. Will retry automatically.',
        variant: 'destructive',
      });
      throw error;
    }
  }, [isOnline, syncWithAPI]);

  const canRetry = apiState.error?.isRetryable === true && lastFailedRequest !== null;

  return {
    apiState,
    isOnline,
    canRetry,
    getSports,
    getTeams,
    getOnboardingStatus,
    updateOnboardingStep,
    completeOnboarding,
    clearError,
    retryLastRequest,
    forceSync,
  };
}

/**
 * Get user-friendly error message
 */
function getFriendlyErrorMessage(
  error: ApiError,
  isOnline: boolean,
  connectionQuality: string
): string {
  if (!isOnline || error.isOfflineError) {
    return 'You\'re currently offline. Your progress has been saved locally and will sync when you reconnect.';
  }

  if (error.statusCode === 401) {
    return 'Your session has expired. Please sign in again.';
  }

  if (error.statusCode === 403) {
    return 'You don\'t have permission to perform this action.';
  }

  if (error.statusCode === 429) {
    return 'Too many requests. Please wait a moment before trying again.';
  }

  if (error.statusCode && error.statusCode >= 500) {
    return 'Our servers are experiencing issues. Please try again in a few moments.';
  }

  if (connectionQuality === 'poor' || connectionQuality === 'fair') {
    return 'Your connection is slow, which may be causing issues. Please check your internet connection.';
  }

  return error.message || 'An unexpected error occurred. Please try again.';
}

export default useOnboardingApiWithRetry;