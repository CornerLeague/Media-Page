/**
 * withOnboardingErrorBoundary
 *
 * Higher-order component that wraps onboarding steps with error boundary
 * and provides automatic error recovery capabilities with enhanced error messages.
 */

import React, { ComponentType } from 'react';
import { useNavigate } from 'react-router-dom';
import { OnboardingStepErrorBoundary, OnboardingErrorFallbackProps } from './OnboardingStepErrorBoundary';
import { FullScreenError, RecoveryGuidance, type RecoveryAction } from './ErrorRecoveryComponents';
import { RefreshCw, ArrowLeft, Home, RotateCcw } from 'lucide-react';
import { reportOnboardingError } from '@/lib/error-reporting';

interface OnboardingStepConfig {
  step: number;
  stepName: string;
  canGoBack?: boolean;
  customFallback?: React.ComponentType<OnboardingErrorFallbackProps>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  retryHandler?: () => void;
  recoverySteps?: string[];
  helpText?: string;
  criticalError?: boolean;
}

export function withOnboardingErrorBoundary<P extends Record<string, any>>(
  WrappedComponent: ComponentType<P>,
  config: OnboardingStepConfig
) {
  const WithErrorBoundary = React.forwardRef<any, P>((props, ref) => {
    const navigate = useNavigate();

    const handleRetry = () => {
      if (config.retryHandler) {
        config.retryHandler();
      } else {
        // Default retry: reload the component by navigating to the same route
        const currentPath = window.location.pathname;
        navigate(currentPath, { replace: true });
      }
    };

    const handleGoBack = config.canGoBack !== false ? () => {
      const previousStep = Math.max(1, config.step - 1);
      navigate(`/onboarding/step/${previousStep}`, { replace: true });
    } : undefined;

    const handleGoHome = () => {
      navigate('/', { replace: true });
    };

    const handleResetOnboarding = () => {
      // Clear any stored onboarding data
      try {
        localStorage.removeItem('corner-league-onboarding-status');
        localStorage.removeItem('corner-league-onboarding-sports');
        localStorage.removeItem('corner-league-onboarding-teams');
        localStorage.removeItem('corner-league-onboarding-preferences');
      } catch (error) {
        console.warn('Failed to clear onboarding data:', error);
      }

      // Navigate to step 1
      navigate('/onboarding/step/1', { replace: true });
    };

    // Enhanced fallback component with recovery guidance
    const EnhancedFallback: React.ComponentType<OnboardingErrorFallbackProps> = ({
      error,
      errorInfo,
      retryCount,
      step,
      stepName,
      onRetry,
      onGoBack,
      onGoHome,
    }) => {
      // If custom fallback is provided, use it
      if (config.customFallback) {
        const CustomFallback = config.customFallback;
        return (
          <CustomFallback
            error={error}
            errorInfo={errorInfo}
            retryCount={retryCount}
            step={step}
            stepName={stepName}
            onRetry={onRetry}
            onGoBack={onGoBack}
            onGoHome={onGoHome}
          />
        );
      }

      // Report the error for analytics
      if (error) {
        reportOnboardingError(
          step,
          `Error in ${stepName} step`,
          error,
          {
            retryCount,
            componentStack: errorInfo?.componentStack,
            userAgent: navigator.userAgent,
          }
        );
      }

      // Build recovery actions
      const recoveryActions: RecoveryAction[] = [];

      // Retry action (if not exceeded max retries)
      if (onRetry && retryCount < 3) {
        recoveryActions.push({
          label: 'Try Again',
          action: onRetry,
          variant: 'default',
          icon: RefreshCw,
        });
      }

      // Go back action
      if (onGoBack) {
        recoveryActions.push({
          label: 'Go Back',
          action: onGoBack,
          variant: 'outline',
          icon: ArrowLeft,
        });
      }

      // Reset onboarding action (for critical errors)
      if (config.criticalError || retryCount >= 3) {
        recoveryActions.push({
          label: 'Restart Setup',
          action: handleResetOnboarding,
          variant: 'outline',
          icon: RotateCcw,
        });
      }

      // Default recovery steps
      const defaultRecoverySteps = [
        'Try refreshing the page',
        'Check your internet connection',
        'Make sure you have a stable connection',
        'If the problem persists, try restarting the setup',
      ];

      const recoverySteps = config.recoverySteps || defaultRecoverySteps;

      const errorTitle = config.criticalError ?
        `Critical Error in ${stepName}` :
        `Error in ${stepName}`;

      const errorMessage = error?.message || 'An unexpected error occurred. Please try again.';

      const helpText = config.helpText ||
        `We encountered an issue during the ${stepName.toLowerCase()} step. Don't worry - your progress has been saved and you can continue from where you left off.`;

      return (
        <div className="space-y-6">
          <FullScreenError
            title={errorTitle}
            message={errorMessage}
            severity={config.criticalError ? 'critical' : 'error'}
            context={{
              step,
              stepName,
              timestamp: new Date(),
              url: window.location.href,
            }}
            recoveryActions={recoveryActions}
            canRetry={retryCount < 3}
            retryCount={retryCount}
            maxRetries={3}
            helpText={helpText}
            technicalDetails={error?.stack}
          />

          {recoverySteps.length > 0 && (
            <div className="max-w-lg mx-auto">
              <RecoveryGuidance steps={recoverySteps} />
            </div>
          )}
        </div>
      );
    };

    return (
      <OnboardingStepErrorBoundary
        step={config.step}
        stepName={config.stepName}
        onRetry={handleRetry}
        onGoBack={handleGoBack}
        onGoHome={handleGoHome}
        fallbackComponent={EnhancedFallback}
      >
        <WrappedComponent {...props} ref={ref} />
      </OnboardingStepErrorBoundary>
    );
  });

  WithErrorBoundary.displayName = `withOnboardingErrorBoundary(${
    WrappedComponent.displayName || WrappedComponent.name || 'Component'
  })`;

  return WithErrorBoundary;
}

// Convenience function for common onboarding step patterns
export const createOnboardingStep = <P extends Record<string, any>>(
  component: ComponentType<P>,
  step: number,
  stepName: string,
  options?: Partial<OnboardingStepConfig>
) => {
  return withOnboardingErrorBoundary(component, {
    step,
    stepName,
    canGoBack: step > 1,
    ...options,
  });
};

export default withOnboardingErrorBoundary;