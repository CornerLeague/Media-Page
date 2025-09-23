/**
 * Enhanced Loading States for Authentication Flow
 *
 * Provides comprehensive loading indicators and error handling
 * for different stages of the authentication and onboarding process.
 */

import React from 'react';
import { AlertCircle, Wifi, WifiOff } from 'lucide-react';
import { type AuthFlowState, type CurrentLoadingState } from '@/lib/types/auth-onboarding';

// =================================================================
// LOADING INDICATOR COMPONENTS
// =================================================================

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div
      className={`animate-spin rounded-full border-b-2 border-primary ${sizeClasses[size]} ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}

function PulsingDots() {
  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="h-2 w-2 bg-primary rounded-full animate-pulse"
          style={{
            animationDelay: `${i * 0.2}s`,
            animationDuration: '1s',
          }}
        />
      ))}
    </div>
  );
}

// =================================================================
// LOADING STATE SCREENS
// =================================================================

interface LoadingScreenProps {
  stage: AuthFlowState;
  message?: string;
  showSpinner?: boolean;
  timeout?: number;
  onTimeout?: () => void;
}

export function AuthLoadingScreen({
  stage,
  message,
  showSpinner = true,
  timeout,
  onTimeout,
}: LoadingScreenProps) {
  // Auto-timeout handling
  React.useEffect(() => {
    if (timeout && onTimeout) {
      const timer = setTimeout(onTimeout, timeout);
      return () => clearTimeout(timer);
    }
  }, [timeout, onTimeout]);

  const getStageConfig = (stage: AuthFlowState) => {
    switch (stage) {
      case 'initializing':
        return {
          title: 'Welcome to Corner League Media',
          message: message || 'Initializing your sports experience...',
          icon: showSpinner ? <Spinner size="lg" /> : <PulsingDots />,
          className: 'text-primary',
        };

      case 'checking':
        return {
          title: 'Setting Up Your Profile',
          message: message || 'Checking your preferences and settings...',
          icon: showSpinner ? <Spinner size="lg" /> : <PulsingDots />,
          className: 'text-blue-600',
        };

      case 'unauthenticated':
        return {
          title: 'Authentication Required',
          message: message || 'Redirecting to sign in...',
          icon: <Spinner size="lg" />,
          className: 'text-orange-600',
        };

      case 'onboarding':
        return {
          title: 'Welcome!',
          message: message || 'Setting up your personalized experience...',
          icon: <Spinner size="lg" />,
          className: 'text-green-600',
        };

      case 'error':
        return {
          title: 'Connection Issue',
          message: message || 'Having trouble connecting...',
          icon: <AlertCircle className="h-12 w-12 text-red-600" />,
          className: 'text-red-600',
        };

      default:
        return {
          title: 'Loading',
          message: message || 'Please wait...',
          icon: <Spinner size="lg" />,
          className: 'text-primary',
        };
    }
  };

  const config = getStageConfig(stage);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md mx-auto px-4">
        {/* Icon */}
        <div className="flex justify-center">
          {config.icon}
        </div>

        {/* Title */}
        <div className="space-y-2">
          <h1 className={`font-display font-bold text-2xl ${config.className}`}>
            {config.title}
          </h1>
          <p className="text-muted-foreground font-body">
            {config.message}
          </p>
        </div>

        {/* Progress indicator for non-error states */}
        {stage !== 'error' && (
          <div className="w-full bg-secondary rounded-full h-1">
            <div
              className="bg-primary h-1 rounded-full transition-all duration-300 ease-out"
              style={{
                width: stage === 'initializing' ? '25%' :
                       stage === 'checking' ? '75%' :
                       stage === 'authenticated' ? '100%' : '50%'
              }}
            />
          </div>
        )}

        {/* Additional context for specific stages */}
        {stage === 'checking' && (
          <div className="text-xs text-muted-foreground">
            This may take a few moments...
          </div>
        )}
      </div>
    </div>
  );
}

// =================================================================
// ERROR STATE COMPONENTS
// =================================================================

interface AuthErrorScreenProps {
  error: string;
  type?: 'network' | 'auth' | 'api' | 'unknown';
  onRetry?: () => void;
  onSignOut?: () => void;
  showNetworkStatus?: boolean;
}

export function AuthErrorScreen({
  error,
  type = 'unknown',
  onRetry,
  onSignOut,
  showNetworkStatus = true,
}: AuthErrorScreenProps) {
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);

  React.useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const getErrorConfig = (type: string) => {
    switch (type) {
      case 'network':
        return {
          title: 'Network Connection Issue',
          icon: isOnline ? <Wifi className="h-12 w-12 text-orange-600" /> : <WifiOff className="h-12 w-12 text-red-600" />,
          suggestions: [
            'Check your internet connection',
            'Try refreshing the page',
            'Contact support if the issue persists',
          ],
        };

      case 'auth':
        return {
          title: 'Authentication Error',
          icon: <AlertCircle className="h-12 w-12 text-red-600" />,
          suggestions: [
            'Try signing in again',
            'Clear your browser cache',
            'Disable browser extensions',
          ],
        };

      case 'api':
        return {
          title: 'Service Temporarily Unavailable',
          icon: <AlertCircle className="h-12 w-12 text-orange-600" />,
          suggestions: [
            'Our servers are experiencing high traffic',
            'Please try again in a few moments',
            'Check our status page for updates',
          ],
        };

      default:
        return {
          title: 'Something Went Wrong',
          icon: <AlertCircle className="h-12 w-12 text-red-600" />,
          suggestions: [
            'Try refreshing the page',
            'Clear your browser cache',
            'Contact support if the issue persists',
          ],
        };
    }
  };

  const config = getErrorConfig(type);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-lg mx-auto px-4">
        {/* Error Icon */}
        <div className="flex justify-center">
          {config.icon}
        </div>

        {/* Error Title and Message */}
        <div className="space-y-3">
          <h1 className="font-display font-bold text-2xl text-foreground">
            {config.title}
          </h1>
          <p className="text-muted-foreground font-body">
            {error}
          </p>
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

        {/* Suggestions */}
        <div className="text-left bg-secondary/50 rounded-lg p-4">
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
        <div className="flex gap-3 justify-center">
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Try Again
            </button>
          )}

          {onSignOut && (
            <button
              onClick={onSignOut}
              className="px-6 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
            >
              Sign Out
            </button>
          )}
        </div>

        {/* Contact Support Link */}
        <div className="text-xs text-muted-foreground">
          Need help?{' '}
          <button
            onClick={() => window.open('mailto:support@cornerleague.com', '_blank')}
            className="text-primary hover:underline"
          >
            Contact Support
          </button>
        </div>
      </div>
    </div>
  );
}

// =================================================================
// INLINE LOADING COMPONENTS
// =================================================================

interface InlineLoadingProps {
  message?: string;
  size?: 'sm' | 'md';
  showMessage?: boolean;
}

export function InlineAuthLoading({
  message = 'Loading...',
  size = 'sm',
  showMessage = true,
}: InlineLoadingProps) {
  return (
    <div className="flex items-center justify-center space-x-2 py-4">
      <Spinner size={size} />
      {showMessage && (
        <span className="text-muted-foreground text-sm">{message}</span>
      )}
    </div>
  );
}

// =================================================================
// TIMEOUT WRAPPER
// =================================================================

interface TimeoutWrapperProps {
  children: React.ReactNode;
  timeout: number;
  onTimeout: () => void;
  fallback?: React.ReactNode;
}

export function AuthTimeoutWrapper({
  children,
  timeout,
  onTimeout,
  fallback,
}: TimeoutWrapperProps) {
  const [hasTimedOut, setHasTimedOut] = React.useState(false);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setHasTimedOut(true);
      onTimeout();
    }, timeout);

    return () => clearTimeout(timer);
  }, [timeout, onTimeout]);

  if (hasTimedOut && fallback) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

// =================================================================
// PROGRESSIVE LOADING
// =================================================================

interface ProgressiveLoadingProps {
  stages: Array<{
    message: string;
    duration: number;
  }>;
  onComplete?: () => void;
}

export function ProgressiveAuthLoading({
  stages,
  onComplete,
}: ProgressiveLoadingProps) {
  const [currentStage, setCurrentStage] = React.useState(0);

  React.useEffect(() => {
    if (currentStage >= stages.length) {
      onComplete?.();
      return;
    }

    const timer = setTimeout(() => {
      setCurrentStage(prev => prev + 1);
    }, stages[currentStage].duration);

    return () => clearTimeout(timer);
  }, [currentStage, stages, onComplete]);

  const stage = stages[currentStage];
  const progress = Math.min(((currentStage + 1) / stages.length) * 100, 100);

  return (
    <div className="text-center space-y-4">
      <Spinner size="lg" />
      <div className="space-y-2">
        <p className="text-muted-foreground font-body">
          {stage?.message || 'Loading...'}
        </p>
        <div className="w-64 bg-secondary rounded-full h-2 mx-auto">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}

export default {
  AuthLoadingScreen,
  AuthErrorScreen,
  InlineAuthLoading,
  AuthTimeoutWrapper,
  ProgressiveAuthLoading,
};