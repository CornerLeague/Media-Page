/**
 * ErrorBoundaryProvider
 *
 * Global error boundary provider that catches and handles all React errors
 * throughout the application. Provides centralized error reporting, recovery
 * mechanisms, and user-friendly error displays.
 */

import React, { Component, createContext, useContext, ReactNode } from 'react';
import { RefreshCw, Home, ArrowLeft, AlertTriangle, Bug } from 'lucide-react';
import { FullScreenError, ErrorAlert, RecoveryAction } from './ErrorRecoveryComponents';
import { toast } from '@/components/ui/use-toast';
import useOnlineStatus from '@/hooks/useOnlineStatus';

// Error context for sharing error state
interface ErrorContextType {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  clearError: () => void;
  reportError: (error: Error, errorInfo?: React.ErrorInfo) => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

// Props for the provider
interface ErrorBoundaryProviderProps {
  children: ReactNode;
  fallbackComponent?: React.ComponentType<ErrorFallbackProps>;
  enableErrorReporting?: boolean;
  maxErrorReports?: number;
  enableAutoRecovery?: boolean;
  autoRecoveryDelay?: number;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  onRecovery?: () => void;
}

// Props for custom fallback components
export interface ErrorFallbackProps {
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  clearError: () => void;
  retryCount: number;
  isOnline: boolean;
  canRetry: boolean;
}

// Internal state
interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  retryCount: number;
  errorId: string;
  lastErrorTime: number;
}

/**
 * Generate unique error ID
 */
function generateErrorId(): string {
  return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Determine if error is recoverable
 */
function isRecoverableError(error: Error): boolean {
  const recoverablePatterns = [
    'Network',
    'fetch',
    'timeout',
    'ChunkLoadError',
    'Loading chunk',
    'Loading CSS chunk',
  ];

  return recoverablePatterns.some(pattern =>
    error.message.toLowerCase().includes(pattern.toLowerCase())
  );
}

/**
 * Global error boundary provider class
 */
class ErrorBoundaryProvider extends Component<ErrorBoundaryProviderProps, State> {
  private autoRecoveryTimeout: NodeJS.Timeout | null = null;
  private maxRetries = 3;
  private errorReportCount = 0;

  constructor(props: ErrorBoundaryProviderProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      errorId: '',
      lastErrorTime: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: generateErrorId(),
      lastErrorTime: Date.now(),
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundaryProvider caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({ errorInfo });

    // Report error
    this.reportError(error, errorInfo);

    // Call custom error handler
    this.props.onError?.(error, errorInfo);

    // Setup auto-recovery for recoverable errors
    if (this.props.enableAutoRecovery && isRecoverableError(error)) {
      this.setupAutoRecovery();
    }

    // Show error toast for non-critical errors
    if (!this.isFullScreenError(error)) {
      toast({
        title: 'Something went wrong',
        description: 'An error occurred, but the application is still running.',
        variant: 'destructive',
      });
    }
  }

  componentWillUnmount() {
    if (this.autoRecoveryTimeout) {
      clearTimeout(this.autoRecoveryTimeout);
    }
  }

  /**
   * Setup automatic error recovery
   */
  private setupAutoRecovery = () => {
    const delay = this.props.autoRecoveryDelay || 5000;

    this.autoRecoveryTimeout = setTimeout(() => {
      this.handleRetry();
    }, delay);
  };

  /**
   * Determine if error should show full screen
   */
  private isFullScreenError = (error: Error): boolean => {
    const fullScreenPatterns = [
      'ChunkLoadError',
      'Loading chunk failed',
      'TypeError: Failed to fetch',
      'Script error',
    ];

    return fullScreenPatterns.some(pattern =>
      error.message.includes(pattern)
    );
  };

  /**
   * Report error to monitoring service
   */
  private reportError = (error: Error, errorInfo?: React.ErrorInfo) => {
    if (!this.props.enableErrorReporting) return;

    const maxReports = this.props.maxErrorReports || 10;
    if (this.errorReportCount >= maxReports) return;

    try {
      const errorReport = {
        errorId: this.state.errorId,
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo?.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        retryCount: this.state.retryCount,
      };

      // Store in localStorage for debugging
      const existingReports = JSON.parse(
        localStorage.getItem('corner-league-error-reports') || '[]'
      );
      existingReports.push(errorReport);

      // Keep only last 20 reports
      if (existingReports.length > 20) {
        existingReports.splice(0, existingReports.length - 20);
      }

      localStorage.setItem(
        'corner-league-error-reports',
        JSON.stringify(existingReports)
      );

      this.errorReportCount++;

      // TODO: Send to external monitoring service
      console.log('Error reported:', errorReport);
    } catch (reportingError) {
      console.warn('Failed to report error:', reportingError);
    }
  };

  /**
   * Clear error and retry
   */
  private handleRetry = () => {
    if (this.autoRecoveryTimeout) {
      clearTimeout(this.autoRecoveryTimeout);
      this.autoRecoveryTimeout = null;
    }

    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1,
      errorId: '',
    }));

    this.props.onRecovery?.();

    toast({
      title: 'Recovery Attempted',
      description: 'The application has been reset. Please try again.',
      variant: 'default',
    });
  };

  /**
   * Clear error without retry
   */
  private clearError = () => {
    if (this.autoRecoveryTimeout) {
      clearTimeout(this.autoRecoveryTimeout);
      this.autoRecoveryTimeout = null;
    }

    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    });

    this.props.onRecovery?.();
  };

  /**
   * Navigate home
   */
  private handleGoHome = () => {
    this.clearError();
    window.location.href = '/';
  };

  /**
   * Go back
   */
  private handleGoBack = () => {
    this.clearError();
    window.history.back();
  };

  /**
   * Reload page
   */
  private handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      const { error, errorInfo, retryCount } = this.state;
      const canRetry = retryCount < this.maxRetries;

      // Use custom fallback component if provided
      if (this.props.fallbackComponent) {
        const FallbackComponent = this.props.fallbackComponent;
        return (
          <ErrorBoundaryWithHook>
            {(isOnline) => (
              <FallbackComponent
                error={error}
                errorInfo={errorInfo}
                clearError={this.clearError}
                retryCount={retryCount}
                isOnline={isOnline}
                canRetry={canRetry}
              />
            )}
          </ErrorBoundaryWithHook>
        );
      }

      // Default error UI based on error type
      const isFullScreen = error ? this.isFullScreenError(error) : false;

      if (isFullScreen) {
        const recoveryActions: RecoveryAction[] = [
          ...(canRetry
            ? [{
                label: 'Try Again',
                action: this.handleRetry,
                variant: 'default' as const,
                icon: RefreshCw,
              }]
            : []
          ),
          {
            label: 'Reload Page',
            action: this.handleReload,
            variant: 'outline' as const,
            icon: RefreshCw,
          },
          {
            label: 'Go Back',
            action: this.handleGoBack,
            variant: 'outline' as const,
            icon: ArrowLeft,
          },
          {
            label: 'Go Home',
            action: this.handleGoHome,
            variant: 'outline' as const,
            icon: Home,
          },
        ];

        return (
          <ErrorBoundaryWithHook>
            {(isOnline) => (
              <FullScreenError
                title="Application Error"
                message={
                  isOnline
                    ? "We're sorry, but something went wrong. This might be a temporary issue."
                    : "You're currently offline. Please check your internet connection and try again."
                }
                severity="critical"
                context={{
                  timestamp: new Date(this.state.lastErrorTime),
                  url: window.location.href,
                }}
                recoveryActions={recoveryActions}
                canRetry={canRetry}
                retryCount={retryCount}
                maxRetries={this.maxRetries}
                helpText={
                  error?.message.includes('ChunkLoadError')
                    ? 'This error often occurs when the application has been updated. Reloading the page should fix it.'
                    : 'If this problem persists, please try refreshing the page or contact support.'
                }
                technicalDetails={error ? `${error.name}: ${error.message}` : undefined}
              />
            )}
          </ErrorBoundaryWithHook>
        );
      } else {
        // Show alert-style error for less critical errors
        const recoveryActions: RecoveryAction[] = [
          ...(canRetry
            ? [{
                label: 'Retry',
                action: this.handleRetry,
                variant: 'default' as const,
                icon: RefreshCw,
              }]
            : []
          ),
          {
            label: 'Dismiss',
            action: this.clearError,
            variant: 'outline' as const,
          },
        ];

        return (
          <ErrorBoundaryWithHook>
            {(isOnline) => (
              <div className="p-4">
                <ErrorAlert
                  title="Error Occurred"
                  message={
                    error?.message ||
                    'An unexpected error occurred, but you can continue using the application.'
                  }
                  severity="error"
                  context={{
                    timestamp: new Date(this.state.lastErrorTime),
                  }}
                  recoveryActions={recoveryActions}
                  canRetry={canRetry}
                  retryCount={retryCount}
                  maxRetries={this.maxRetries}
                  helpText={
                    !isOnline
                      ? 'This error might be related to your internet connection.'
                      : undefined
                  }
                  technicalDetails={error ? `${error.name}: ${error.message}` : undefined}
                />
              </div>
            )}
          </ErrorBoundaryWithHook>
        );
      }
    }

    return (
      <ErrorContext.Provider
        value={{
          hasError: this.state.hasError,
          error: this.state.error,
          errorInfo: this.state.errorInfo,
          clearError: this.clearError,
          reportError: this.reportError,
        }}
      >
        {this.props.children}
      </ErrorContext.Provider>
    );
  }
}

/**
 * Hook wrapper to provide online status to error components
 */
function ErrorBoundaryWithHook({
  children,
}: {
  children: (isOnline: boolean) => ReactNode;
}) {
  const { isOnline } = useOnlineStatus({ showToasts: false });
  return <>{children(isOnline)}</>;
}

/**
 * Hook to access error context
 */
export function useErrorBoundary() {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useErrorBoundary must be used within ErrorBoundaryProvider');
  }
  return context;
}

/**
 * Hook to manually trigger error boundary
 */
export function useThrowError() {
  return (error: Error) => {
    throw error;
  };
}

export default ErrorBoundaryProvider;