/**
 * Authentication and Onboarding Integration Types
 *
 * Enhanced TypeScript interfaces that integrate Firebase authentication
 * with the backend onboarding API for Phase 1.1 Authentication Flow Integration.
 */

import { User } from 'firebase/auth';
import { AuthState } from './firebase-types';

// =================================================================
// ENHANCED AUTHENTICATION STATE
// =================================================================

/**
 * Enhanced authentication state that includes onboarding status
 */
export interface EnhancedAuthState extends AuthState {
  // Onboarding-specific state
  onboarding: {
    isChecking: boolean;
    status: UserOnboardingStatus | null;
    error: string | null;
    lastChecked: Date | null;
  };

  // Session persistence
  sessionPersistent: boolean;

  // User metadata tracking
  userMetadata: {
    isNewUser: boolean;
    creationTime: string | null;
    lastSignInTime: string | null;
  } | null;
}

/**
 * User onboarding status that matches backend API schema
 */
export interface UserOnboardingStatus {
  hasCompletedOnboarding: boolean;
  currentStep: number | null;
}

/**
 * Onboarding status response from backend API
 */
export interface OnboardingStatusResponse {
  hasCompletedOnboarding: boolean;
  currentStep?: number | null;
}

// =================================================================
// AUTHENTICATION FLOW STATES
// =================================================================

/**
 * Authentication flow states for routing logic
 */
export type AuthFlowState =
  | 'initializing'     // Firebase auth is initializing
  | 'unauthenticated' // User is not signed in
  | 'checking'        // Checking onboarding status
  | 'onboarding'      // User needs to complete onboarding
  | 'authenticated'   // User is fully authenticated and onboarded
  | 'error';          // Error occurred in auth flow

/**
 * Auth check result for routing decisions
 */
export interface AuthCheckResult {
  state: AuthFlowState;
  user: User | null;
  onboardingStatus: UserOnboardingStatus | null;
  redirectTo: string | null;
  error: string | null;
}

// =================================================================
// AUTHENTICATION HOOKS INTERFACES
// =================================================================

/**
 * useAuthOnboarding hook interface
 */
export interface UseAuthOnboardingResult {
  // Current state
  authState: EnhancedAuthState;
  flowState: AuthFlowState;

  // User and onboarding data
  user: User | null;
  onboardingStatus: UserOnboardingStatus | null;

  // Status flags
  isLoading: boolean;
  isAuthenticated: boolean;
  isOnboarded: boolean;
  isNewUser: boolean;

  // Error handling
  error: string | null;
  onboardingError: string | null;

  // Actions
  checkOnboardingStatus: () => Promise<UserOnboardingStatus | null>;
  refreshAuth: () => Promise<void>;
  clearErrors: () => void;

  // Routing helpers
  getRedirectPath: () => string | null;
  shouldRedirectToOnboarding: () => boolean;
  shouldRedirectToAuth: () => boolean;
}

// =================================================================
// ROUTE PROTECTION INTERFACES
// =================================================================

/**
 * Enhanced protected route props
 */
export interface EnhancedProtectedRouteProps {
  children: React.ReactNode;

  // Route configuration
  requireAuth?: boolean;
  requireOnboarding?: boolean;
  redirectTo?: string;
  onboardingRedirectTo?: string;

  // Custom loading component
  loadingComponent?: React.ComponentType;

  // Custom error handling
  onAuthError?: (error: string) => void;
  onOnboardingError?: (error: string) => void;

  // Test mode support
  allowTestMode?: boolean;
}

/**
 * Route guard result
 */
export interface RouteGuardResult {
  canAccess: boolean;
  redirectTo: string | null;
  isLoading: boolean;
  error: string | null;
}

// =================================================================
// SESSION PERSISTENCE
// =================================================================

/**
 * Session persistence configuration
 */
export interface SessionPersistenceConfig {
  // Storage type
  storage: 'localStorage' | 'sessionStorage' | 'memory';

  // Key prefix for storage
  keyPrefix: string;

  // Session timeout (in milliseconds)
  timeoutMs: number;

  // Auto-refresh configuration
  autoRefresh: {
    enabled: boolean;
    intervalMs: number;
    beforeExpiryMs: number;
  };
}

/**
 * Persisted session data
 */
export interface PersistedSessionData {
  userId: string;
  lastCheckTime: number;
  onboardingStatus: UserOnboardingStatus;
  expiresAt: number;
}

// =================================================================
// ERROR HANDLING
// =================================================================

/**
 * Auth onboarding error types
 */
export enum AuthOnboardingErrorType {
  FIREBASE_INIT_ERROR = 'firebase_init_error',
  API_CONNECTION_ERROR = 'api_connection_error',
  ONBOARDING_CHECK_ERROR = 'onboarding_check_error',
  SESSION_EXPIRED = 'session_expired',
  INVALID_USER_STATE = 'invalid_user_state',
  NETWORK_ERROR = 'network_error',
  UNKNOWN_ERROR = 'unknown_error',
}

/**
 * Structured error for auth onboarding flow
 */
export interface AuthOnboardingError {
  type: AuthOnboardingErrorType;
  message: string;
  details?: Record<string, any>;
  timestamp: Date;
  recoverable: boolean;
}

// =================================================================
// LOADING STATES
// =================================================================

/**
 * Loading state configuration for different stages
 */
export interface LoadingStatesConfig {
  firebase: {
    message: string;
    showSpinner: boolean;
    timeout?: number;
  };
  onboarding: {
    message: string;
    showSpinner: boolean;
    timeout?: number;
  };
  redirect: {
    message: string;
    showSpinner: boolean;
    timeout?: number;
  };
}

/**
 * Current loading state
 */
export interface CurrentLoadingState {
  stage: 'firebase' | 'onboarding' | 'redirect' | null;
  message: string;
  showSpinner: boolean;
  startTime: Date;
  timeout?: number;
}

// =================================================================
// NAVIGATION HELPERS
// =================================================================

/**
 * Navigation decision based on auth state
 */
export interface NavigationDecision {
  action: 'stay' | 'redirect' | 'replace';
  path: string | null;
  reason: string;
  immediate: boolean;
}

/**
 * Auth-aware routing configuration
 */
export interface AuthRoutingConfig {
  // Default paths
  authPath: string;
  onboardingBasePath: string;
  homePath: string;

  // Onboarding steps
  onboardingSteps: {
    [stepNumber: number]: string;
  };

  // Fallback configuration
  fallback: {
    onApiError: string;
    onUnknownError: string;
    onTimeout: string;
  };
}

// =================================================================
// INTEGRATION WITH EXISTING TYPES
// =================================================================

/**
 * Extended Firebase user with onboarding data
 */
export interface OnboardingAwareUser extends User {
  onboardingCompleted?: boolean;
  currentOnboardingStep?: number | null;
  lastOnboardingCheck?: Date;
}

/**
 * API client configuration for auth onboarding
 */
export interface AuthOnboardingApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  retryDelay: number;

  // Authentication headers
  getAuthHeaders: () => Promise<Record<string, string>>;

  // Error handling
  onApiError: (error: any) => void;
  onNetworkError: (error: any) => void;
}

// =================================================================
// UTILITY TYPES
// =================================================================

/**
 * Make onboarding fields optional for partial updates
 */
export type PartialOnboardingStatus = Partial<UserOnboardingStatus>;

/**
 * Onboarding status with loading state
 */
export type OnboardingStatusWithLoading = {
  data: UserOnboardingStatus | null;
  isLoading: boolean;
  error: string | null;
};

/**
 * Auth state change callback
 */
export type AuthStateChangeCallback = (state: EnhancedAuthState) => void;

/**
 * Onboarding status change callback
 */
export type OnboardingStatusChangeCallback = (status: UserOnboardingStatus | null) => void;

// =================================================================
// CONSTANTS
// =================================================================

/**
 * Default configuration values
 */
export const AUTH_ONBOARDING_DEFAULTS = {
  sessionTimeout: 24 * 60 * 60 * 1000, // 24 hours
  onboardingCheckInterval: 5 * 60 * 1000, // 5 minutes
  apiTimeout: 10000, // 10 seconds
  maxRetries: 3,
  retryDelay: 1000, // 1 second

  // Default messages
  loadingMessages: {
    firebase: 'Initializing authentication...',
    onboarding: 'Checking your profile...',
    redirect: 'Setting up your experience...',
  },

  // Default paths
  defaultPaths: {
    auth: '/auth/sign-in',
    onboardingBase: '/onboarding',
    home: '/',
  },
} as const;

/**
 * Storage keys for persistence
 */
export const AUTH_STORAGE_KEYS = {
  sessionData: 'corner-league-auth-session',
  onboardingStatus: 'corner-league-onboarding-status',
  userPreferences: 'corner-league-user-preferences',
  lastCheck: 'corner-league-last-auth-check',
} as const;

export default {
  // Export types for convenience
  type: {} as {
    EnhancedAuthState: EnhancedAuthState;
    UserOnboardingStatus: UserOnboardingStatus;
    UseAuthOnboardingResult: UseAuthOnboardingResult;
    EnhancedProtectedRouteProps: EnhancedProtectedRouteProps;
    AuthOnboardingError: AuthOnboardingError;
  },

  // Export constants
  defaults: AUTH_ONBOARDING_DEFAULTS,
  storageKeys: AUTH_STORAGE_KEYS,
};