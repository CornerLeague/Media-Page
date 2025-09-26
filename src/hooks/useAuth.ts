/**
 * useAuth Hook
 *
 * Provides enhanced authentication state with user preferences from onboarding.
 * This hook combines Firebase authentication with user preference data for
 * dashboard personalization as required by section 1.2.
 *
 * Enhanced with intelligent retry logic, timeout handling, and comprehensive
 * error state management for Fix 3: Infinite Loading State Resolution.
 */

import { useMemo, useCallback, useRef, useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { useAuthOnboarding } from '@/hooks/useAuthOnboarding';
import { apiClient, createApiQueryClient, type UserProfile } from '@/lib/api-client';
import { getLocalOnboardingStatus } from '@/lib/onboarding-storage';
import { AuthOnboardingErrorType, type AuthOnboardingError } from '@/lib/types/auth-onboarding';

// =================================================================
// ENHANCED AUTHENTICATION TYPES
// =================================================================

/**
 * Retry configuration for authentication operations
 */
export interface AuthRetryConfig {
  maxRetries: number;
  baseDelay: number; // Base delay in milliseconds
  maxDelay: number; // Maximum delay in milliseconds
  backoffMultiplier: number; // Exponential backoff multiplier
  jitter: boolean; // Add random jitter to prevent thundering herd
}

/**
 * Timeout configuration for authentication operations
 */
export interface AuthTimeoutConfig {
  firebaseTimeout: number; // Firebase auth operations timeout
  apiTimeout: number; // API calls timeout
  totalTimeout: number; // Total authentication flow timeout (30 seconds)
}

/**
 * Enhanced error state for authentication
 */
export interface AuthErrorState {
  hasError: boolean;
  error: AuthOnboardingError | null;
  retryCount: number;
  lastRetryTime: number;
  isRetrying: boolean;
  canRetry: boolean;
}

/**
 * Authentication operation result
 */
export interface AuthOperationResult<T = unknown> {
  success: boolean;
  data: T | null;
  error: AuthOnboardingError | null;
  retryCount: number;
  totalTime: number;
}

/**
 * Loading state with timeout awareness
 */
export interface AuthLoadingState {
  isLoading: boolean;
  loadingStage: 'firebase' | 'api' | 'onboarding' | null;
  loadingStartTime: number;
  hasTimedOut: boolean;
  timeoutIn: number; // Milliseconds until timeout
}

// Default configuration values
const DEFAULT_RETRY_CONFIG: AuthRetryConfig = {
  maxRetries: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 10000, // 10 seconds
  backoffMultiplier: 2,
  jitter: true,
};

const DEFAULT_TIMEOUT_CONFIG: AuthTimeoutConfig = {
  firebaseTimeout: 10000, // 10 seconds
  apiTimeout: 15000, // 15 seconds
  totalTimeout: 30000, // 30 seconds
};

// Extended user preferences interface for dashboard
export interface UserPreferences {
  // Selected sports from onboarding
  sports: Array<{
    sportId: string;
    name: string;
    rank: number;
    hasTeams: boolean;
  }>;

  // Selected teams from onboarding
  teams: Array<{
    teamId: string;
    name: string;
    sportId: string;
    league: string;
    affinityScore: number;
  }>;

  // Content preferences from onboarding
  preferences: {
    newsTypes: Array<{
      type: string;
      enabled: boolean;
      priority: number;
    }>;
    notifications: {
      push: boolean;
      email: boolean;
      gameReminders: boolean;
      newsAlerts: boolean;
      scoreUpdates: boolean;
    };
    contentFrequency: 'minimal' | 'standard' | 'comprehensive';
  };
}

// Default preferences for fallback
const DEFAULT_PREFERENCES: UserPreferences = {
  sports: [],
  teams: [],
  preferences: {
    newsTypes: [
      { type: 'injuries', enabled: true, priority: 1 },
      { type: 'trades', enabled: true, priority: 2 },
      { type: 'roster', enabled: true, priority: 3 },
      { type: 'scores', enabled: true, priority: 4 },
      { type: 'analysis', enabled: false, priority: 5 },
    ],
    notifications: {
      push: true,
      email: false,
      gameReminders: true,
      newsAlerts: false,
      scoreUpdates: true,
    },
    contentFrequency: 'standard',
  },
};

export interface UseAuthResult {
  // User authentication state
  user: unknown;
  isLoading: boolean;
  isAuthenticated: boolean;
  isOnboarded: boolean;

  // User preferences for dashboard personalization
  userPreferences: UserPreferences;

  // Firebase auth methods
  signOut: () => Promise<void>;
  getIdToken: (forceRefresh?: boolean) => Promise<string | null>;

  // Status flags
  hasSelectedSports: boolean;
  hasSelectedTeams: boolean;
  shouldShowTeams: boolean;

  // Enhanced loading state with timeout awareness
  loadingState: AuthLoadingState;

  // Enhanced error state management
  errorState: AuthErrorState;

  // Actions
  refreshUserData: () => void;
  retryAuthentication: () => Promise<void>;
  clearAuthError: () => void;

  // Configuration
  retryConfig: AuthRetryConfig;
  timeoutConfig: AuthTimeoutConfig;
}

// =================================================================
// UTILITY FUNCTIONS FOR RETRY AND TIMEOUT LOGIC
// =================================================================

/**
 * Calculate exponential backoff delay with jitter
 */
function calculateBackoffDelay(
  retryCount: number,
  config: AuthRetryConfig
): number {
  const baseDelay = config.baseDelay * Math.pow(config.backoffMultiplier, retryCount);
  const delay = Math.min(baseDelay, config.maxDelay);

  if (config.jitter) {
    // Add ±25% jitter to prevent thundering herd
    const jitterRange = delay * 0.25;
    const jitter = (Math.random() - 0.5) * 2 * jitterRange;
    return Math.max(0, delay + jitter);
  }

  return delay;
}

/**
 * Create an authentication error with proper typing
 */
function createAuthError(
  type: AuthOnboardingErrorType,
  message: string,
  originalError?: Error,
  details?: Record<string, unknown>
): AuthOnboardingError {
  return {
    type,
    message,
    details: {
      ...details,
      originalError: originalError?.message,
      stack: originalError?.stack,
    },
    timestamp: new Date(),
    recoverable: type !== AuthOnboardingErrorType.INVALID_USER_STATE,
  };
}

/**
 * Check if an error is retryable
 */
function isRetryableError(error: unknown): boolean {
  if (!error) return false;

  const errorCode = (error as { code?: string }).code?.toLowerCase() || '';
  const errorMessage = (error as { message?: string }).message?.toLowerCase() || '';

  // Network errors are retryable
  if (errorMessage.includes('network') || errorMessage.includes('timeout') || errorMessage.includes('fetch')) {
    return true;
  }

  // Firebase auth errors that are retryable
  if (errorCode.includes('auth/network-request-failed') ||
      errorCode.includes('auth/timeout') ||
      errorCode.includes('auth/unavailable')) {
    return true;
  }

  // API connection errors are retryable
  if (errorMessage.includes('api') || errorMessage.includes('connection')) {
    return true;
  }

  return false;
}

/**
 * Wrap a promise with timeout functionality
 */
function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  timeoutMessage: string = 'Operation timed out'
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(createAuthError(
          AuthOnboardingErrorType.NETWORK_ERROR,
          timeoutMessage,
          new Error('Timeout'),
          { timeoutMs }
        ));
      }, timeoutMs);
    })
  ]);
}

/**
 * Execute an operation with retry logic and timeout
 */
async function executeWithRetry<T>(
  operation: () => Promise<T>,
  config: AuthRetryConfig,
  timeoutMs: number,
  operationName: string = 'Authentication operation'
): Promise<AuthOperationResult<T>> {
  let lastError: AuthOnboardingError | null = null;
  let retryCount = 0;
  const startTime = Date.now();

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      const result = await withTimeout(
        operation(),
        timeoutMs,
        `${operationName} timed out after ${timeoutMs}ms`
      );

      return {
        success: true,
        data: result,
        error: null,
        retryCount,
        totalTime: Date.now() - startTime,
      };
    } catch (error: unknown) {
      retryCount = attempt;

      // Create structured error
      const authError = createAuthError(
        AuthOnboardingErrorType.API_CONNECTION_ERROR,
        `${operationName} failed: ${(error as Error).message || 'Unknown error'}`,
        error as Error,
        { attempt, retryCount }
      );

      lastError = authError;

      // Don't retry if it's not retryable or we've reached max retries
      if (!isRetryableError(error) || attempt >= config.maxRetries) {
        break;
      }

      // Wait before retrying
      const delay = calculateBackoffDelay(attempt, config);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  return {
    success: false,
    data: null,
    error: lastError,
    retryCount,
    totalTime: Date.now() - startTime,
  };
}

/**
 * useAuth Hook
 *
 * Enhanced authentication hook with intelligent retry logic, timeout handling,
 * and comprehensive error state management.
 */
export function useAuth(
  customRetryConfig?: Partial<AuthRetryConfig>,
  customTimeoutConfig?: Partial<AuthTimeoutConfig>
): UseAuthResult {
  // Configuration
  const retryConfig = useMemo(() => ({
    ...DEFAULT_RETRY_CONFIG,
    ...customRetryConfig,
  }), [customRetryConfig]);

  const timeoutConfig = useMemo(() => ({
    ...DEFAULT_TIMEOUT_CONFIG,
    ...customTimeoutConfig,
  }), [customTimeoutConfig]);

  // Core auth dependencies
  const { user, isLoading: firebaseLoading, isAuthenticated, signOut, getIdToken } = useFirebaseAuth();
  const { isOnboarded, flowState } = useAuthOnboarding();

  // Enhanced state management
  const [errorState, setErrorState] = useState<AuthErrorState>({
    hasError: false,
    error: null,
    retryCount: 0,
    lastRetryTime: 0,
    isRetrying: false,
    canRetry: true,
  });

  const [loadingState, setLoadingState] = useState<AuthLoadingState>({
    isLoading: false,
    loadingStage: null,
    loadingStartTime: 0,
    hasTimedOut: false,
    timeoutIn: 0,
  });

  // Refs for cleanup
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const loadingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Clear timeouts on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (loadingTimeoutRef.current) clearTimeout(loadingTimeoutRef.current);
    };
  }, []);

  // Update loading state based on Firebase loading
  useEffect(() => {
    if (firebaseLoading && !loadingState.isLoading) {
      const startTime = Date.now();
      setLoadingState({
        isLoading: true,
        loadingStage: 'firebase',
        loadingStartTime: startTime,
        hasTimedOut: false,
        timeoutIn: timeoutConfig.totalTimeout,
      });

      // Set up timeout monitoring
      loadingTimeoutRef.current = setTimeout(() => {
        setLoadingState(prev => ({
          ...prev,
          hasTimedOut: true,
        }));

        setErrorState(prev => ({
          ...prev,
          hasError: true,
          error: createAuthError(
            AuthOnboardingErrorType.NETWORK_ERROR,
            'Authentication timed out after 30 seconds',
            new Error('Timeout'),
            { stage: 'firebase' }
          ),
          canRetry: true,
        }));
      }, timeoutConfig.totalTimeout);
    } else if (!firebaseLoading && loadingState.isLoading && loadingState.loadingStage === 'firebase') {
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current);
        loadingTimeoutRef.current = null;
      }

      setLoadingState({
        isLoading: false,
        loadingStage: null,
        loadingStartTime: 0,
        hasTimedOut: false,
        timeoutIn: 0,
      });
    }
  }, [firebaseLoading, timeoutConfig.totalTimeout, loadingState.isLoading, loadingState.loadingStage]);

  // Get query configurations with Firebase auth
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Enhanced API query with retry logic
  const {
    data: userProfile,
    isLoading: profileLoading,
    error: profileError,
    refetch: refetchProfile,
  } = useQuery({
    ...queryConfigs.getCurrentUser(),
    enabled: isAuthenticated && isOnboarded && flowState === 'authenticated' && !errorState.hasError,
    retry: (failureCount, error) => {
      // Use our custom retry logic instead of TanStack Query's default
      return failureCount < retryConfig.maxRetries && isRetryableError(error);
    },
    retryDelay: (attemptIndex) => calculateBackoffDelay(attemptIndex, retryConfig),
    onError: (error: unknown) => {
      setErrorState(prev => ({
        ...prev,
        hasError: true,
        error: createAuthError(
          AuthOnboardingErrorType.API_CONNECTION_ERROR,
          'Failed to fetch user profile',
          error as Error
        ),
        canRetry: isRetryableError(error),
      }));
    },
  });

  // Update loading state for API calls
  useEffect(() => {
    if (profileLoading && !loadingState.isLoading) {
      setLoadingState(prev => ({
        ...prev,
        isLoading: true,
        loadingStage: 'api',
        loadingStartTime: Date.now(),
      }));
    } else if (!profileLoading && loadingState.loadingStage === 'api') {
      setLoadingState(prev => ({
        ...prev,
        isLoading: false,
        loadingStage: null,
      }));
    }
  }, [profileLoading, loadingState.isLoading, loadingState.loadingStage]);

  // Get local onboarding data as fallback
  const localOnboardingData = useMemo(() => {
    if (!isAuthenticated) return null;
    return getLocalOnboardingStatus();
  }, [isAuthenticated]);

  // Determine user preferences from API or local storage
  const userPreferences = useMemo((): UserPreferences => {
    // Try to use backend API data first
    if (userProfile && (userProfile as UserProfile).preferences) {
      return {
        sports: [], // Will be populated when backend provides sports data
        teams: [], // Will be populated when backend provides teams data
        preferences: (userProfile as UserProfile).preferences,
      };
    }

    // Fallback to local onboarding data
    if (localOnboardingData && (localOnboardingData.selectedSports.length > 0 || localOnboardingData.selectedTeams.length > 0)) {
      return {
        sports: localOnboardingData.selectedSports.map(s => ({
          sportId: s.sportId,
          name: s.sportId, // Will be enriched later
          rank: s.rank,
          hasTeams: true,
        })),
        teams: localOnboardingData.selectedTeams.map(t => ({
          teamId: t.teamId,
          name: t.teamId, // Will be enriched later
          sportId: t.sportId,
          league: 'Unknown',
          affinityScore: t.affinityScore,
        })),
        preferences: localOnboardingData.preferences,
      };
    }

    // Final fallback to defaults
    return DEFAULT_PREFERENCES;
  }, [userProfile, localOnboardingData]);

  // Computed flags
  const hasSelectedSports = userPreferences.sports.length > 0;
  const hasSelectedTeams = userPreferences.teams.length > 0;
  const shouldShowTeams = hasSelectedTeams && isOnboarded;

  // Enhanced action methods
  const refreshUserData = useCallback(() => {
    if (isAuthenticated && isOnboarded && !errorState.isRetrying) {
      setErrorState(prev => ({ ...prev, hasError: false, error: null }));
      refetchProfile();
    }
  }, [isAuthenticated, isOnboarded, errorState.isRetrying, refetchProfile]);

  const retryAuthentication = useCallback(async () => {
    if (errorState.isRetrying || !errorState.canRetry) return;

    setErrorState(prev => ({
      ...prev,
      isRetrying: true,
      retryCount: prev.retryCount + 1,
      lastRetryTime: Date.now(),
    }));

    try {
      // Clear any existing errors
      setErrorState(prev => ({ ...prev, hasError: false, error: null }));

      // Retry the operation based on the current state
      if (isAuthenticated && isOnboarded) {
        await refetchProfile();
      }

      setErrorState(prev => ({
        ...prev,
        isRetrying: false,
        hasError: false,
        error: null,
      }));
    } catch (error: unknown) {
      setErrorState(prev => ({
        ...prev,
        isRetrying: false,
        hasError: true,
        error: createAuthError(
          AuthOnboardingErrorType.API_CONNECTION_ERROR,
          'Retry failed',
          error as Error
        ),
        canRetry: prev.retryCount < retryConfig.maxRetries && isRetryableError(error),
      }));
    }
  }, [errorState.isRetrying, errorState.canRetry, errorState.retryCount, isAuthenticated, isOnboarded, refetchProfile, retryConfig.maxRetries]);

  const clearAuthError = useCallback(() => {
    setErrorState({
      hasError: false,
      error: null,
      retryCount: 0,
      lastRetryTime: 0,
      isRetrying: false,
      canRetry: true,
    });
  }, []);

  // Calculate overall loading state
  const isLoading = firebaseLoading || profileLoading || loadingState.isLoading || errorState.isRetrying;

  return {
    // User authentication state
    user,
    isLoading,
    isAuthenticated,
    isOnboarded,

    // User preferences for dashboard personalization
    userPreferences,

    // Firebase auth methods
    signOut,
    getIdToken,

    // Status flags
    hasSelectedSports,
    hasSelectedTeams,
    shouldShowTeams,

    // Enhanced state management
    loadingState,
    errorState,

    // Actions
    refreshUserData,
    retryAuthentication,
    clearAuthError,

    // Configuration
    retryConfig,
    timeoutConfig,
  };
}

// =================================================================
// BACKWARD COMPATIBILITY HELPERS
// =================================================================

/**
 * Legacy useAuth hook interface for backward compatibility
 * This ensures existing components continue to work without modification
 */
export interface LegacyUseAuthResult {
  // User authentication state
  user: unknown;
  isLoading: boolean;
  isAuthenticated: boolean;
  isOnboarded: boolean;

  // User preferences for dashboard personalization
  userPreferences: UserPreferences;

  // Firebase auth methods
  signOut: () => Promise<void>;
  getIdToken: (forceRefresh?: boolean) => Promise<string | null>;

  // Status flags
  hasSelectedSports: boolean;
  hasSelectedTeams: boolean;
  shouldShowTeams: boolean;

  // Actions
  refreshUserData: () => void;
}

/**
 * Legacy useAuth hook wrapper for backward compatibility
 * This maintains the original API while providing enhanced functionality under the hood
 */
export function useLegacyAuth(): LegacyUseAuthResult {
  const enhancedResult = useAuth();

  return {
    // User authentication state
    user: enhancedResult.user,
    isLoading: enhancedResult.isLoading,
    isAuthenticated: enhancedResult.isAuthenticated,
    isOnboarded: enhancedResult.isOnboarded,

    // User preferences for dashboard personalization
    userPreferences: enhancedResult.userPreferences,

    // Firebase auth methods
    signOut: enhancedResult.signOut,
    getIdToken: enhancedResult.getIdToken,

    // Status flags
    hasSelectedSports: enhancedResult.hasSelectedSports,
    hasSelectedTeams: enhancedResult.hasSelectedTeams,
    shouldShowTeams: enhancedResult.shouldShowTeams,

    // Actions
    refreshUserData: enhancedResult.refreshUserData,
  };
}

// =================================================================
// ERROR BOUNDARY INTEGRATION HOOKS
// =================================================================

/**
 * Hook for integrating with AuthenticationErrorBoundary
 * This provides error boundary components with the ability to trigger
 * authentication retries and access enhanced error state
 */
export function useAuthErrorIntegration() {
  const { errorState, retryAuthentication, clearAuthError, loadingState } = useAuth();

  const triggerErrorBoundary = useCallback((error: AuthOnboardingError) => {
    // This can be called by error boundary to manually set error state
    throw error;
  }, []);

  return {
    errorState,
    loadingState,
    retryAuthentication,
    clearAuthError,
    triggerErrorBoundary,
    hasError: errorState.hasError,
    canRetry: errorState.canRetry,
    isRetrying: errorState.isRetrying,
    hasTimedOut: loadingState.hasTimedOut,
  };
}

/**
 * Hook for accessing authentication metrics and debugging info
 */
export function useAuthMetrics() {
  const { errorState, loadingState, retryConfig, timeoutConfig } = useAuth();

  return {
    retryCount: errorState.retryCount,
    lastRetryTime: errorState.lastRetryTime,
    loadingStartTime: loadingState.loadingStartTime,
    hasTimedOut: loadingState.hasTimedOut,
    timeoutIn: loadingState.timeoutIn,
    retryConfig,
    timeoutConfig,

    // Helper methods
    getLoadingDuration: () => {
      if (!loadingState.isLoading || !loadingState.loadingStartTime) return 0;
      return Date.now() - loadingState.loadingStartTime;
    },

    getTimeSinceLastRetry: () => {
      if (!errorState.lastRetryTime) return 0;
      return Date.now() - errorState.lastRetryTime;
    },
  };
}

export default useAuth;