/**
 * useAuthOnboarding Hook
 *
 * Custom hook that integrates Firebase authentication with backend onboarding status
 * for Phase 1.1 Authentication Flow Integration. Provides auto-redirect logic,
 * session persistence, and comprehensive error handling.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { User } from 'firebase/auth';
import { useQuery } from '@tanstack/react-query';

import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { apiClient, createApiQueryClient, type OnboardingStatusResponse } from '@/lib/api-client';
import {
  type EnhancedAuthState,
  type UserOnboardingStatus,
  type UseAuthOnboardingResult,
  type AuthFlowState,
  type AuthOnboardingError,
  type AuthOnboardingErrorType,
  type PersistedSessionData,
  AUTH_ONBOARDING_DEFAULTS,
  AUTH_STORAGE_KEYS,
} from '@/lib/types/auth-onboarding';

/**
 * Session persistence utilities
 */
const SessionStorage = {
  get: (key: string): PersistedSessionData | null => {
    try {
      const data = localStorage.getItem(key);
      if (!data) return null;

      const parsed = JSON.parse(data);
      if (parsed.expiresAt && Date.now() > parsed.expiresAt) {
        localStorage.removeItem(key);
        return null;
      }

      return parsed;
    } catch {
      return null;
    }
  },

  set: (key: string, data: PersistedSessionData): void => {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.warn('Failed to persist session data:', error);
    }
  },

  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn('Failed to remove session data:', error);
    }
  },
};

/**
 * Convert backend response to internal format
 */
const convertOnboardingStatus = (response: OnboardingStatusResponse): UserOnboardingStatus => {
  return {
    hasCompletedOnboarding: response.hasCompletedOnboarding,
    currentStep: response.currentStep,
  };
};

/**
 * Determine if user is new based on Firebase metadata
 */
const isNewUser = (user: User | null): boolean => {
  if (!user?.metadata) return false;

  const creationTime = user.metadata.creationTime;
  const lastSignInTime = user.metadata.lastSignInTime;

  // Consider user new if creation and last sign-in are very close (within 30 seconds)
  if (creationTime && lastSignInTime) {
    const creationMs = new Date(creationTime).getTime();
    const lastSignInMs = new Date(lastSignInTime).getTime();
    return Math.abs(lastSignInMs - creationMs) < 30000;
  }

  return false;
};

/**
 * Create structured auth error
 */
const createAuthError = (
  type: AuthOnboardingErrorType,
  message: string,
  details?: Record<string, any>
): AuthOnboardingError => ({
  type,
  message,
  details,
  timestamp: new Date(),
  recoverable: type !== AuthOnboardingErrorType.FIREBASE_INIT_ERROR,
});

/**
 * useAuthOnboarding Hook Implementation
 */
export function useAuthOnboarding(): UseAuthOnboardingResult {
  const navigate = useNavigate();
  const { user, isLoading: firebaseLoading, isAuthenticated, getIdToken } = useFirebaseAuth();

  // State management
  const [authState, setAuthState] = useState<EnhancedAuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
    onboarding: {
      isChecking: false,
      status: null,
      error: null,
      lastChecked: null,
    },
    sessionPersistent: false,
    userMetadata: null,
  });

  const [flowState, setFlowState] = useState<AuthFlowState>('initializing');
  const [errors, setErrors] = useState<{
    auth: string | null;
    onboarding: string | null;
  }>({
    auth: null,
    onboarding: null,
  });

  // Refs to prevent stale closures
  const latestUser = useRef<User | null>(null);
  const redirectPending = useRef(false);

  // Set up API client with Firebase auth
  useEffect(() => {
    if (isAuthenticated && getIdToken) {
      apiClient.setFirebaseAuth({
        getIdToken,
        isAuthenticated: true,
        userId: user?.uid,
      });
    }
  }, [isAuthenticated, getIdToken, user?.uid]);

  // Get query configurations
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Query onboarding status
  const {
    data: onboardingResponse,
    isLoading: onboardingLoading,
    error: onboardingQueryError,
    refetch: refetchOnboarding,
  } = useQuery({
    ...queryConfigs.getOnboardingStatus(),
    enabled: isAuthenticated && !firebaseLoading,
    retry: 2,
    retryDelay: 1000,
  });

  // Update auth state when Firebase auth changes
  useEffect(() => {
    latestUser.current = user;

    const userMetadata = user?.metadata ? {
      isNewUser: isNewUser(user),
      creationTime: user.metadata.creationTime || null,
      lastSignInTime: user.metadata.lastSignInTime || null,
    } : null;

    setAuthState(prev => ({
      ...prev,
      user,
      isLoading: firebaseLoading,
      isAuthenticated,
      userMetadata,
    }));

    // Update flow state based on auth status
    if (firebaseLoading) {
      setFlowState('initializing');
    } else if (!isAuthenticated) {
      setFlowState('unauthenticated');
      // Clear session data when user signs out
      SessionStorage.remove(AUTH_STORAGE_KEYS.sessionData);
    } else if (onboardingLoading) {
      setFlowState('checking');
    }
  }, [user, firebaseLoading, isAuthenticated, onboardingLoading]);

  // Handle onboarding status updates
  useEffect(() => {
    if (onboardingResponse) {
      const onboardingStatus = convertOnboardingStatus(onboardingResponse);
      const now = new Date();

      setAuthState(prev => ({
        ...prev,
        onboarding: {
          ...prev.onboarding,
          status: onboardingStatus,
          error: null,
          lastChecked: now,
          isChecking: false,
        },
      }));

      // Persist session data
      if (user?.uid) {
        const sessionData: PersistedSessionData = {
          userId: user.uid,
          lastCheckTime: now.getTime(),
          onboardingStatus,
          expiresAt: now.getTime() + AUTH_ONBOARDING_DEFAULTS.sessionTimeout,
        };
        SessionStorage.set(AUTH_STORAGE_KEYS.sessionData, sessionData);
      }

      // Update flow state
      if (onboardingStatus.hasCompletedOnboarding) {
        setFlowState('authenticated');
      } else {
        setFlowState('onboarding');
      }

      // Clear errors
      setErrors(prev => ({ ...prev, onboarding: null }));
    }
  }, [onboardingResponse, user?.uid]);

  // Handle onboarding errors
  useEffect(() => {
    if (onboardingQueryError) {
      const errorMessage = onboardingQueryError instanceof Error
        ? onboardingQueryError.message
        : 'Failed to check onboarding status';

      setAuthState(prev => ({
        ...prev,
        onboarding: {
          ...prev.onboarding,
          error: errorMessage,
          isChecking: false,
        },
      }));

      setErrors(prev => ({ ...prev, onboarding: errorMessage }));
      setFlowState('error');
    }
  }, [onboardingQueryError]);

  // Load persisted session data
  useEffect(() => {
    if (isAuthenticated && user?.uid) {
      const sessionData = SessionStorage.get(AUTH_STORAGE_KEYS.sessionData);

      if (sessionData && sessionData.userId === user.uid) {
        setAuthState(prev => ({
          ...prev,
          onboarding: {
            ...prev.onboarding,
            status: sessionData.onboardingStatus,
            lastChecked: new Date(sessionData.lastCheckTime),
          },
          sessionPersistent: true,
        }));

        // Update flow state based on persisted data
        if (sessionData.onboardingStatus.hasCompletedOnboarding) {
          setFlowState('authenticated');
        } else {
          setFlowState('onboarding');
        }
      }
    }
  }, [isAuthenticated, user?.uid]);

  // Auto-redirect logic
  useEffect(() => {
    if (redirectPending.current || firebaseLoading) return;

    const shouldRedirect = () => {
      // Don't redirect during loading states
      if (flowState === 'initializing' || flowState === 'checking') {
        return null;
      }

      // Don't redirect unauthenticated users - let onboarding routes handle them
      if (flowState === 'unauthenticated') {
        return null;
      }

      // Don't redirect if user is on auth page or onboarding pages - let route guards handle them
      const currentPath = window.location.pathname;
      if (currentPath === '/auth/sign-in' || currentPath.startsWith('/onboarding/')) {
        return null;
      }

      // Redirect authenticated users who need onboarding only if they're not already there
      if (flowState === 'onboarding' && authState.onboarding.status) {
        const currentStep = authState.onboarding.status.currentStep || 1;
        const targetPath = `/onboarding/step/${currentStep}`;
        return currentPath !== targetPath ? targetPath : null;
      }

      return null;
    };

    const redirectPath = shouldRedirect();
    if (redirectPath && window.location.pathname !== redirectPath) {
      redirectPending.current = true;
      navigate(redirectPath, { replace: true });

      // Reset redirect flag after navigation
      setTimeout(() => {
        redirectPending.current = false;
      }, 100);
    }
  }, [flowState, authState.onboarding.status, firebaseLoading, navigate]);

  // Action methods
  const checkOnboardingStatus = useCallback(async (): Promise<UserOnboardingStatus | null> => {
    if (!isAuthenticated) return null;

    try {
      setAuthState(prev => ({
        ...prev,
        onboarding: { ...prev.onboarding, isChecking: true, error: null },
      }));

      const response = await refetchOnboarding();
      return response.data ? convertOnboardingStatus(response.data) : null;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to check onboarding status';

      setAuthState(prev => ({
        ...prev,
        onboarding: { ...prev.onboarding, isChecking: false, error: errorMessage },
      }));

      return null;
    }
  }, [isAuthenticated, refetchOnboarding]);

  const refreshAuth = useCallback(async (): Promise<void> => {
    if (!isAuthenticated) return;

    try {
      // Force refresh Firebase token
      await getIdToken(true);

      // Refresh onboarding status
      await refetchOnboarding();
    } catch (error) {
      console.error('Failed to refresh auth:', error);
    }
  }, [isAuthenticated, getIdToken, refetchOnboarding]);

  const clearErrors = useCallback((): void => {
    setErrors({ auth: null, onboarding: null });
    setAuthState(prev => ({
      ...prev,
      error: null,
      onboarding: { ...prev.onboarding, error: null },
    }));
  }, []);

  // Helper methods
  const getRedirectPath = useCallback((): string | null => {
    if (flowState === 'unauthenticated') {
      return '/auth/sign-in';
    }

    if (flowState === 'onboarding' && authState.onboarding.status) {
      const currentStep = authState.onboarding.status.currentStep || 1;
      return `/onboarding/step/${currentStep}`;
    }

    return null;
  }, [flowState, authState.onboarding.status]);

  const shouldRedirectToOnboarding = useCallback((): boolean => {
    return flowState === 'onboarding';
  }, [flowState]);

  const shouldRedirectToAuth = useCallback((): boolean => {
    return flowState === 'unauthenticated';
  }, [flowState]);

  // Computed values
  const isLoading = firebaseLoading || onboardingLoading || flowState === 'initializing' || flowState === 'checking';
  const isOnboarded = authState.onboarding.status?.hasCompletedOnboarding ?? false;
  const userIsNew = authState.userMetadata?.isNewUser ?? false;

  return {
    // Current state
    authState,
    flowState,

    // User and onboarding data
    user,
    onboardingStatus: authState.onboarding.status,

    // Status flags
    isLoading,
    isAuthenticated,
    isOnboarded,
    isNewUser: userIsNew,

    // Error handling
    error: errors.auth,
    onboardingError: errors.onboarding,

    // Actions
    checkOnboardingStatus,
    refreshAuth,
    clearErrors,

    // Routing helpers
    getRedirectPath,
    shouldRedirectToOnboarding,
    shouldRedirectToAuth,
  };
}

export default useAuthOnboarding;