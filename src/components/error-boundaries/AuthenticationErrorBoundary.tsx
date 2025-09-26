/**
 * AuthenticationErrorBoundary
 *
 * Specialized error boundary for handling authentication-related errors.
 * Addresses infinite loading states and provides user-friendly error recovery.
 * Part of Fix 3: Infinite Loading State Resolution.
 */

import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, LogIn, Shield, Wifi, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from '@/components/ui/sonner';
import { AuthOnboardingErrorType } from '@/lib/types/auth-onboarding';

// =================================================================
// INTERFACES AND TYPES
// =================================================================

export interface AuthenticationError extends Error {
  code?: string;
  type?: AuthOnboardingErrorType;
  recoverable?: boolean;
  requiresReauth?: boolean;
  details?: Record<string, any>;
}

export interface AuthErrorBoundaryProps {
  children: ReactNode;
  onAuthError?: (error: AuthenticationError) => void;
  onRetrySuccess?: () => void;
  fallbackComponent?: React.ComponentType<AuthErrorFallbackProps>;
  maxRetries?: number;
  enableLogging?: boolean;
  showNetworkStatus?: boolean;
}

export interface AuthErrorFallbackProps {
  error: AuthenticationError | null;
  errorInfo: React.ErrorInfo | null;
  retryCount: number;
  onRetry: () => void;
  onSignOut: () => void;
  onRefresh: () => void;
  isNetworkError: boolean;
  isRecoverable: boolean;
}

interface AuthErrorBoundaryState {
  hasError: boolean;
  error: AuthenticationError | null;
  errorInfo: React.ErrorInfo | null;
  retryCount: number;
  lastErrorTime: number;
  isRetrying: boolean;
  isOnline: boolean;
}

// =================================================================
// ERROR CLASSIFICATION HELPERS
// =================================================================

/**
 * Classify error type based on error properties
 */
function classifyAuthError(error: Error): AuthOnboardingErrorType {
  const message = error.message.toLowerCase();
  const errorCode = (error as any).code?.toLowerCase() || '';

  // Firebase Authentication Errors
  if (errorCode.includes('auth/')) {
    if (errorCode.includes('network') || errorCode.includes('timeout')) {
      return AuthOnboardingErrorType.NETWORK_ERROR;
    }
    if (errorCode.includes('expired') || errorCode.includes('invalid-user-token')) {
      return AuthOnboardingErrorType.SESSION_EXPIRED;
    }
    return AuthOnboardingErrorType.FIREBASE_INIT_ERROR;
  }

  // API Connection Errors
  if (message.includes('fetch') || message.includes('api') || errorCode.includes('failed')) {
    return AuthOnboardingErrorType.API_CONNECTION_ERROR;
  }

  // Network Errors
  if (message.includes('network') || message.includes('timeout') || message.includes('connection')) {
    return AuthOnboardingErrorType.NETWORK_ERROR;
  }

  // Session Errors
  if (message.includes('session') || message.includes('expired') || message.includes('token')) {
    return AuthOnboardingErrorType.SESSION_EXPIRED;
  }

  return AuthOnboardingErrorType.UNKNOWN_ERROR;
}

/**
 * Determine if error is recoverable
 */
function isRecoverableError(error: AuthenticationError): boolean {
  const errorType = error.type || classifyAuthError(error);

  switch (errorType) {
    case AuthOnboardingErrorType.NETWORK_ERROR:
    case AuthOnboardingErrorType.API_CONNECTION_ERROR:
    case AuthOnboardingErrorType.SESSION_EXPIRED:
      return true;
    case AuthOnboardingErrorType.FIREBASE_INIT_ERROR:
    case AuthOnboardingErrorType.ONBOARDING_CHECK_ERROR:
      return true;
    case AuthOnboardingErrorType.INVALID_USER_STATE:
      return false;
    default:
      return true; // Default to recoverable for unknown errors
  }
}

/**
 * Check if error requires reauthentication
 */
function requiresReauth(error: AuthenticationError): boolean {
  const errorType = error.type || classifyAuthError(error);
  const errorCode = (error as any).code?.toLowerCase() || '';

  return (
    errorType === AuthOnboardingErrorType.SESSION_EXPIRED ||
    errorCode.includes('auth/requires-recent-login') ||
    errorCode.includes('auth/user-token-expired') ||
    errorCode.includes('auth/invalid-user-token')
  );
}

/**
 * Check if error is network-related
 */
function isNetworkError(error: AuthenticationError): boolean {
  const errorType = error.type || classifyAuthError(error);
  return (
    errorType === AuthOnboardingErrorType.NETWORK_ERROR ||
    errorType === AuthOnboardingErrorType.API_CONNECTION_ERROR
  );
}

// =================================================================
// ERROR LOGGING AND REPORTING
// =================================================================

/**
 * Enhanced error logging for authentication issues
 */
function logAuthError(error: AuthenticationError, errorInfo: React.ErrorInfo, context: any = {}) {
  try {
    const errorData = {
      // Error details
      name: error.name,
      message: error.message,
      stack: error.stack,
      code: (error as any).code,
      type: error.type || classifyAuthError(error),

      // Component context
      componentStack: errorInfo.componentStack,

      // Environment context
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      isOnline: navigator.onLine,

      // Additional context
      ...context,
    };

    // Console logging for development
    console.error('Authentication Error Boundary:', errorData);

    // Store in localStorage for debugging (keep last 10 errors)
    const storageKey = 'corner-league-auth-errors';
    const existingErrors = JSON.parse(localStorage.getItem(storageKey) || '[]');
    existingErrors.push(errorData);

    if (existingErrors.length > 10) {
      existingErrors.splice(0, existingErrors.length - 10);
    }

    localStorage.setItem(storageKey, JSON.stringify(existingErrors));

    // TODO: In production, send to error reporting service
    // Example: Sentry, LogRocket, etc.
    if (process.env.NODE_ENV === 'production') {
      // errorReportingService.captureException(error, { extra: errorData });
    }
  } catch (loggingError) {
    console.warn('Failed to log authentication error:', loggingError);
  }
}

// =================================================================
// AUTHENTICATION ERROR BOUNDARY COMPONENT
// =================================================================

export class AuthenticationErrorBoundary extends Component<AuthErrorBoundaryProps, AuthErrorBoundaryState> {
  private retryTimeout: NodeJS.Timeout | null = null;
  private maxRetries: number;
  private retryDelay = 1000; // Start with 1 second

  constructor(props: AuthErrorBoundaryProps) {
    super(props);
    this.maxRetries = props.maxRetries || 3;

    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      lastErrorTime: 0,
      isRetrying: false,
      isOnline: navigator.onLine,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<AuthErrorBoundaryState> {
    // Enhance the error with authentication-specific properties
    const authError: AuthenticationError = Object.assign(error, {
      type: classifyAuthError(error),
      recoverable: isRecoverableError(error as AuthenticationError),
      requiresReauth: requiresReauth(error as AuthenticationError),
    });

    return {
      hasError: true,
      error: authError,
      lastErrorTime: Date.now(),
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const authError = this.state.error || (error as AuthenticationError);

    // Log the error
    if (this.props.enableLogging !== false) {
      logAuthError(authError, errorInfo, {
        retryCount: this.state.retryCount,
        component: 'AuthenticationErrorBoundary',
      });
    }

    // Update state with error info
    this.setState({ errorInfo });

    // Call external error handler
    if (this.props.onAuthError) {
      this.props.onAuthError(authError);
    }

    // Auto-retry for certain recoverable errors
    if (authError.recoverable && this.shouldAutoRetry(authError)) {
      this.scheduleAutoRetry();
    }

    // Show toast notification for user awareness
    this.showErrorToast(authError);
  }

  componentDidMount() {
    // Listen for network status changes
    window.addEventListener('online', this.handleOnline);
    window.addEventListener('offline', this.handleOffline);
  }

  componentWillUnmount() {
    // Cleanup
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
    window.removeEventListener('online', this.handleOnline);
    window.removeEventListener('offline', this.handleOffline);
  }

  private handleOnline = () => {
    this.setState({ isOnline: true });

    // Auto-retry if we have a network error and we're back online
    if (this.state.hasError && isNetworkError(this.state.error!)) {
      toast.success('Connection restored. Retrying...', {
        duration: 2000,
      });
      this.handleRetry();
    }
  };

  private handleOffline = () => {
    this.setState({ isOnline: false });
  };

  private shouldAutoRetry = (error: AuthenticationError): boolean => {
    // Only auto-retry network errors and specific authentication errors
    return (
      this.state.retryCount < this.maxRetries &&
      (isNetworkError(error) || error.type === AuthOnboardingErrorType.FIREBASE_INIT_ERROR)
    );
  };

  private scheduleAutoRetry = () => {
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }

    const delay = this.retryDelay * Math.pow(2, this.state.retryCount); // Exponential backoff

    this.retryTimeout = setTimeout(() => {
      this.handleRetry(true);
    }, delay);
  };

  private showErrorToast = (error: AuthenticationError) => {
    const errorType = error.type || classifyAuthError(error);

    let toastMessage = 'Authentication error occurred';

    switch (errorType) {
      case AuthOnboardingErrorType.NETWORK_ERROR:
        toastMessage = 'Network connection issue. Please check your internet.';
        break;
      case AuthOnboardingErrorType.SESSION_EXPIRED:
        toastMessage = 'Your session has expired. Please sign in again.';
        break;
      case AuthOnboardingErrorType.API_CONNECTION_ERROR:
        toastMessage = 'Unable to connect to our servers. Please try again.';
        break;
      case AuthOnboardingErrorType.FIREBASE_INIT_ERROR:
        toastMessage = 'Authentication service is temporarily unavailable.';
        break;
      default:
        toastMessage = 'An unexpected error occurred. Please try again.';
    }

    toast.error(toastMessage, {
      duration: 5000,
      action: {
        label: 'Retry',
        onClick: () => this.handleRetry(),
      },
    });
  };

  private handleRetry = (isAutoRetry = false) => {
    const now = Date.now();
    const timeSinceLastError = now - this.state.lastErrorTime;

    // Prevent rapid retries (except auto-retries)
    if (timeSinceLastError < 500 && !isAutoRetry) {
      return;
    }

    this.setState({ isRetrying: true });

    // Small delay to show loading state
    setTimeout(() => {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prevState.retryCount + 1,
        isRetrying: false,
      }));

      // Call success callback
      if (this.props.onRetrySuccess) {
        this.props.onRetrySuccess();
      }

      toast.success('Retrying...', { duration: 2000 });
    }, 300);
  };

  private handleSignOut = () => {
    // Force a sign out to clear any corrupted auth state
    try {
      // Import auth service dynamically to avoid circular dependencies
      import('@/lib/firebase').then(({ authService }) => {
        authService.signOut().then(() => {
          toast.info('Signed out successfully. Please sign in again.', { duration: 3000 });
          window.location.href = '/auth/sign-in';
        });
      });
    } catch (error) {
      console.error('Failed to sign out:', error);
      // Fallback: force navigation
      window.location.href = '/auth/sign-in';
    }
  };

  private handleRefresh = () => {
    // Force a page refresh as last resort
    window.location.reload();
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback component if provided
      if (this.props.fallbackComponent) {
        const FallbackComponent = this.props.fallbackComponent;
        return (
          <FallbackComponent
            error={this.state.error}
            errorInfo={this.state.errorInfo}
            retryCount={this.state.retryCount}
            onRetry={() => this.handleRetry()}
            onSignOut={this.handleSignOut}
            onRefresh={this.handleRefresh}
            isNetworkError={isNetworkError(this.state.error)}
            isRecoverable={this.state.error.recoverable || false}
          />
        );
      }

      // Default error UI
      return (
        <DefaultAuthErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          retryCount={this.state.retryCount}
          maxRetries={this.maxRetries}
          isRetrying={this.state.isRetrying}
          isOnline={this.state.isOnline}
          showNetworkStatus={this.props.showNetworkStatus !== false}
          onRetry={() => this.handleRetry()}
          onSignOut={this.handleSignOut}
          onRefresh={this.handleRefresh}
        />
      );
    }

    return this.props.children;
  }
}

// =================================================================
// DEFAULT ERROR FALLBACK COMPONENT
// =================================================================

interface DefaultAuthErrorFallbackProps {
  error: AuthenticationError;
  errorInfo: React.ErrorInfo | null;
  retryCount: number;
  maxRetries: number;
  isRetrying: boolean;
  isOnline: boolean;
  showNetworkStatus: boolean;
  onRetry: () => void;
  onSignOut: () => void;
  onRefresh: () => void;
}

function DefaultAuthErrorFallback({
  error,
  retryCount,
  maxRetries,
  isRetrying,
  isOnline,
  showNetworkStatus,
  onRetry,
  onSignOut,
  onRefresh,
}: DefaultAuthErrorFallbackProps) {
  const errorType = error.type || classifyAuthError(error);
  const isRecoverable = error.recoverable !== false;
  const needsReauth = error.requiresReauth || requiresReauth(error);
  const isNetwork = isNetworkError(error);

  const getErrorConfig = () => {
    switch (errorType) {
      case AuthOnboardingErrorType.SESSION_EXPIRED:
        return {
          title: 'Session Expired',
          icon: <Shield className="h-12 w-12 text-orange-600" />,
          message: 'Your session has expired for security reasons. Please sign in again to continue.',
          suggestions: [
            'Click "Sign In Again" to reauthenticate',
            'Your progress has been saved',
            'Clear browser cache if issues persist',
          ],
        };

      case AuthOnboardingErrorType.NETWORK_ERROR:
        return {
          title: 'Network Connection Issue',
          icon: isOnline ? <Wifi className="h-12 w-12 text-orange-600" /> : <WifiOff className="h-12 w-12 text-red-600" />,
          message: isOnline
            ? 'Having trouble connecting to our servers. Please check your connection.'
            : 'You appear to be offline. Please check your internet connection.',
          suggestions: [
            'Check your internet connection',
            'Try refreshing the page',
            'Disable VPN if enabled',
            'Contact support if issues persist',
          ],
        };

      case AuthOnboardingErrorType.API_CONNECTION_ERROR:
        return {
          title: 'Service Temporarily Unavailable',
          icon: <AlertTriangle className="h-12 w-12 text-orange-600" />,
          message: 'Our authentication service is temporarily unavailable. Please try again in a moment.',
          suggestions: [
            'Our servers may be experiencing high traffic',
            'Please try again in a few moments',
            'Check our status page for updates',
          ],
        };

      case AuthOnboardingErrorType.FIREBASE_INIT_ERROR:
        return {
          title: 'Authentication Service Error',
          icon: <AlertTriangle className="h-12 w-12 text-red-600" />,
          message: 'There was an issue initializing the authentication service.',
          suggestions: [
            'Try refreshing the page',
            'Clear your browser cache',
            'Try signing out and back in',
          ],
        };

      default:
        return {
          title: 'Authentication Error',
          icon: <AlertTriangle className="h-12 w-12 text-red-600" />,
          message: 'An unexpected authentication error occurred.',
          suggestions: [
            'Try refreshing the page',
            'Clear your browser cache',
            'Sign out and back in',
            'Contact support if issues persist',
          ],
        };
    }
  };

  const config = getErrorConfig();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {config.icon}
          </div>
          <CardTitle className="text-xl">{config.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center space-y-2">
            <p className="text-muted-foreground">{config.message}</p>
            {retryCount > 0 && (
              <p className="text-sm text-muted-foreground">
                Retry attempts: {retryCount}/{maxRetries}
              </p>
            )}
          </div>

          {/* Network Status */}
          {showNetworkStatus && (
            <div className={`text-sm px-3 py-2 rounded-md ${
              isOnline
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {isOnline ? '✓ Connected to internet' : '✗ No internet connection'}
            </div>
          )}

          {/* Error Details */}
          <Alert>
            <AlertDescription className="text-sm">
              <strong>Error details:</strong> {error.message}
            </AlertDescription>
          </Alert>

          {/* Suggestions */}
          <div className="bg-secondary/50 rounded-lg p-4">
            <h3 className="font-semibold text-sm mb-2">Try these steps:</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              {config.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-primary mr-2">•</span>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            {/* Primary action based on error type */}
            {needsReauth ? (
              <Button onClick={onSignOut} className="w-full" variant="default">
                <LogIn className="h-4 w-4 mr-2" />
                Sign In Again
              </Button>
            ) : isRecoverable && retryCount < maxRetries ? (
              <Button
                onClick={onRetry}
                className="w-full"
                variant="default"
                disabled={isRetrying}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isRetrying ? 'animate-spin' : ''}`} />
                {isRetrying ? 'Retrying...' : 'Try Again'}
              </Button>
            ) : null}

            {/* Secondary actions */}
            <div className="flex gap-2">
              {!needsReauth && (
                <Button onClick={onSignOut} variant="outline" className="flex-1">
                  <LogIn className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              )}

              <Button onClick={onRefresh} variant="outline" className="flex-1">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Page
              </Button>
            </div>
          </div>

          {/* Help Link */}
          <div className="text-center text-xs text-muted-foreground">
            Need help?{' '}
            <button
              onClick={() => window.open('mailto:support@cornerleague.com', '_blank')}
              className="text-primary hover:underline"
            >
              Contact Support
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// =================================================================
// CONVENIENCE HOOKS
// =================================================================

/**
 * Hook for manually triggering authentication error boundary
 */
export function useAuthErrorBoundary() {
  return {
    captureAuthError: (error: AuthenticationError, context?: any) => {
      // Enhance error with context
      const enhancedError = Object.assign(error, {
        type: error.type || classifyAuthError(error),
        recoverable: error.recoverable ?? isRecoverableError(error),
        requiresReauth: error.requiresReauth ?? requiresReauth(error),
        details: { ...error.details, ...context },
      });

      // Throw the error to be caught by error boundary
      throw enhancedError;
    },
  };
}

export default AuthenticationErrorBoundary;