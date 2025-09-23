/**
 * OnboardingStepErrorBoundary
 *
 * Error boundary component specifically designed for onboarding steps.
 * Provides graceful error handling with user-friendly messages and recovery options.
 */

import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface Props {
  children: ReactNode;
  step: number;
  stepName: string;
  onRetry?: () => void;
  onGoBack?: () => void;
  onGoHome?: () => void;
  fallbackComponent?: React.ComponentType<OnboardingErrorFallbackProps>;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  retryCount: number;
  lastErrorTime: number;
}

export interface OnboardingErrorFallbackProps {
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  retryCount: number;
  step: number;
  stepName: string;
  onRetry: () => void;
  onGoBack?: () => void;
  onGoHome?: () => void;
}

export class OnboardingStepErrorBoundary extends Component<Props, State> {
  private retryTimeout: NodeJS.Timeout | null = null;
  private maxRetries = 3;
  private retryDelay = 1000; // Start with 1 second

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      lastErrorTime: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      lastErrorTime: Date.now(),
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error for debugging
    console.error(`Onboarding Step ${this.props.step} Error:`, error, errorInfo);

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Report error to error tracking service (if available)
    this.reportError(error, errorInfo);

    // Auto-retry for certain types of errors
    if (this.shouldAutoRetry(error)) {
      this.scheduleAutoRetry();
    }
  }

  componentWillUnmount() {
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
  }

  private shouldAutoRetry = (error: Error): boolean => {
    // Auto-retry for network errors, but not for component errors
    const networkErrorPatterns = [
      'fetch',
      'network',
      'timeout',
      'connection',
      'NetworkError',
      'Failed to fetch',
    ];

    const errorMessage = error.message.toLowerCase();
    return networkErrorPatterns.some(pattern =>
      errorMessage.includes(pattern.toLowerCase())
    );
  };

  private scheduleAutoRetry = () => {
    if (this.state.retryCount >= this.maxRetries) {
      return;
    }

    const delay = this.retryDelay * Math.pow(2, this.state.retryCount); // Exponential backoff

    this.retryTimeout = setTimeout(() => {
      this.handleRetry(true);
    }, delay);
  };

  private reportError = (error: Error, errorInfo: React.ErrorInfo) => {
    try {
      // Store error details for debugging
      const errorData = {
        step: this.props.step,
        stepName: this.props.stepName,
        error: {
          name: error.name,
          message: error.message,
          stack: error.stack,
        },
        errorInfo: {
          componentStack: errorInfo.componentStack,
        },
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      // Store in localStorage for debugging
      const existingErrors = JSON.parse(
        localStorage.getItem('corner-league-onboarding-errors') || '[]'
      );
      existingErrors.push(errorData);

      // Keep only last 10 errors
      if (existingErrors.length > 10) {
        existingErrors.splice(0, existingErrors.length - 10);
      }

      localStorage.setItem(
        'corner-league-onboarding-errors',
        JSON.stringify(existingErrors)
      );
    } catch (reportingError) {
      console.warn('Failed to report error:', reportingError);
    }
  };

  private handleRetry = (isAutoRetry = false) => {
    const now = Date.now();
    const timeSinceLastError = now - this.state.lastErrorTime;

    // Prevent rapid retries
    if (timeSinceLastError < 500 && !isAutoRetry) {
      return;
    }

    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1,
    }));

    // Call parent retry handler if provided
    if (this.props.onRetry) {
      try {
        this.props.onRetry();
      } catch (error) {
        console.error('Error in onRetry callback:', error);
      }
    }
  };

  private handleGoBack = () => {
    if (this.props.onGoBack) {
      this.props.onGoBack();
    } else {
      // Default: go to previous step
      window.history.back();
    }
  };

  private handleGoHome = () => {
    if (this.props.onGoHome) {
      this.props.onGoHome();
    } else {
      // Default: navigate to home
      window.location.href = '/';
    }
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback component if provided
      if (this.props.fallbackComponent) {
        const FallbackComponent = this.props.fallbackComponent;
        return (
          <FallbackComponent
            error={this.state.error}
            errorInfo={this.state.errorInfo}
            retryCount={this.state.retryCount}
            step={this.props.step}
            stepName={this.props.stepName}
            onRetry={() => this.handleRetry()}
            onGoBack={this.props.onGoBack ? this.handleGoBack : undefined}
            onGoHome={this.handleGoHome}
          />
        );
      }

      // Default error fallback UI
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <Card className="w-full max-w-lg">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <AlertTriangle className="h-12 w-12 text-red-500" />
              </div>
              <CardTitle className="text-xl">
                Oops! Something went wrong
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center space-y-2">
                <p className="text-muted-foreground">
                  We encountered an error on step {this.props.step} ({this.props.stepName}).
                </p>
                <p className="text-sm text-muted-foreground">
                  Don't worry - your progress has been saved.
                </p>
              </div>

              {this.state.error && (
                <Alert>
                  <AlertDescription className="text-sm">
                    <strong>Error details:</strong> {this.state.error.message}
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-3">
                {this.state.retryCount < this.maxRetries && (
                  <Button
                    onClick={() => this.handleRetry()}
                    className="w-full"
                    variant="default"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Try Again {this.state.retryCount > 0 && `(${this.state.retryCount}/${this.maxRetries})`}
                  </Button>
                )}

                <div className="flex gap-2">
                  {this.props.onGoBack && (
                    <Button
                      onClick={this.handleGoBack}
                      variant="outline"
                      className="flex-1"
                    >
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Go Back
                    </Button>
                  )}

                  <Button
                    onClick={this.handleGoHome}
                    variant="outline"
                    className="flex-1"
                  >
                    <Home className="h-4 w-4 mr-2" />
                    Go Home
                  </Button>
                </div>
              </div>

              {this.state.retryCount >= this.maxRetries && (
                <Alert>
                  <AlertDescription className="text-sm">
                    We've tried several times but the error persists.
                    Please try refreshing the page or contact support if the problem continues.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default OnboardingStepErrorBoundary;