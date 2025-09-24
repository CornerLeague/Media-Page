/**
 * OnboardingWithErrorRecovery
 *
 * Enhanced onboarding wrapper that provides error recovery, offline detection,
 * and retry functionality for onboarding steps. This component integrates with
 * the existing onboarding flow to provide a robust user experience.
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { WifiOff, AlertCircle, RefreshCw, ArrowLeft, Save, Zap } from 'lucide-react';
import { OnboardingStepErrorBoundary } from '@/components/error-boundaries/OnboardingStepErrorBoundary';
import { ErrorAlert, SuccessMessage, RecoveryAction } from '@/components/error-boundaries/ErrorRecoveryComponents';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/components/ui/use-toast';
import useOnlineStatus from '@/hooks/useOnlineStatus';
import useSessionRecovery from '@/hooks/useSessionRecovery';
import { cn } from '@/lib/utils';

interface OnboardingWithErrorRecoveryProps {
  children: React.ReactNode;
  step: number;
  stepName: string;
  onStepComplete?: (stepData: any) => void;
  onStepError?: (error: Error, step: number) => void;
  allowOfflineMode?: boolean;
  requiresConnection?: boolean;
  autoSaveEnabled?: boolean;
  className?: string;
}

interface StepErrorState {
  hasError: boolean;
  error: Error | null;
  errorCount: number;
  lastErrorTime: number;
  isRetrying: boolean;
}

export function OnboardingWithErrorRecovery({
  children,
  step,
  stepName,
  onStepComplete,
  onStepError,
  allowOfflineMode = true,
  requiresConnection = false,
  autoSaveEnabled = true,
  className,
}: OnboardingWithErrorRecoveryProps) {
  const navigate = useNavigate();
  const location = useLocation();

  // Hooks
  const {
    isOnline,
    networkInfo,
    connectionQuality,
    wasOffline,
    lastOnlineTime,
    offlineDuration
  } = useOnlineStatus({
    showToasts: false,
    enableNetworkAPI: true,
  });

  const {
    sessionState,
    stepProgress,
    isRecovering,
    hasUnsyncedData,
    saveStepProgress,
    recoverStepData,
    syncWithAPI,
    syncStatus,
  } = useSessionRecovery();

  // Local state
  const [stepError, setStepError] = useState<StepErrorState>({
    hasError: false,
    error: null,
    errorCount: 0,
    lastErrorTime: 0,
    isRetrying: false,
  });
  const [showOfflineWarning, setShowOfflineWarning] = useState(false);
  const [showSlowConnectionWarning, setShowSlowConnectionWarning] = useState(false);
  const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  /**
   * Handle step error
   */
  const handleStepError = useCallback((error: Error) => {
    const now = Date.now();

    setStepError(prev => ({
      hasError: true,
      error,
      errorCount: prev.errorCount + 1,
      lastErrorTime: now,
      isRetrying: false,
    }));

    // Call parent error handler
    onStepError?.(error, step);

    // Show error toast
    toast({
      title: 'Step Error',
      description: `An error occurred in ${stepName}. You can retry or continue offline.`,
      variant: 'destructive',
    });
  }, [step, stepName, onStepError]);

  /**
   * Handle step completion
   */
  const handleStepComplete = useCallback(async (stepData: any) => {
    try {
      // Save progress locally first
      if (autoSaveEnabled) {
        setAutoSaveStatus('saving');
        saveStepProgress(step, stepData);
        setAutoSaveStatus('saved');
      }

      // Call parent completion handler
      onStepComplete?.(stepData);

      // Clear any previous errors
      setStepError({
        hasError: false,
        error: null,
        errorCount: 0,
        lastErrorTime: 0,
        isRetrying: false,
      });

      toast({
        title: 'Progress Saved',
        description: `Step ${step} completed successfully.`,
        variant: 'default',
      });

      // Auto-save timeout
      setTimeout(() => {
        setAutoSaveStatus('idle');
      }, 3000);

    } catch (error) {
      console.error('Failed to complete step:', error);
      setAutoSaveStatus('error');

      toast({
        title: 'Save Error',
        description: 'Failed to save progress. Your data is preserved locally.',
        variant: 'destructive',
      });
    }
  }, [step, stepName, autoSaveEnabled, saveStepProgress, onStepComplete]);

  /**
   * Retry current step
   */
  const handleRetryStep = useCallback(async () => {
    setStepError(prev => ({ ...prev, isRetrying: true }));

    try {
      // Wait a bit before retry
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Reset error state
      setStepError({
        hasError: false,
        error: null,
        errorCount: 0,
        lastErrorTime: 0,
        isRetrying: false,
      });

      toast({
        title: 'Retrying',
        description: 'Attempting to recover from the error...',
        variant: 'default',
      });

    } catch (retryError) {
      setStepError(prev => ({
        ...prev,
        isRetrying: false,
        error: retryError as Error,
      }));

      toast({
        title: 'Retry Failed',
        description: 'The retry attempt was unsuccessful.',
        variant: 'destructive',
      });
    }
  }, []);

  /**
   * Go back to previous step
   */
  const handleGoBack = useCallback(() => {
    if (step > 1) {
      navigate(`/onboarding/step/${step - 1}`);
    }
  }, [step, navigate]);

  /**
   * Sync data when connection is restored
   */
  const handleSyncData = useCallback(async () => {
    if (!isOnline || !hasUnsyncedData) return;

    try {
      const result = await syncWithAPI();

      if (result.success > 0) {
        toast({
          title: 'Data Synced',
          description: `Successfully synced ${result.success} items with the server.`,
          variant: 'default',
        });
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }, [isOnline, hasUnsyncedData, syncWithAPI]);

  /**
   * Monitor offline status changes
   */
  useEffect(() => {
    if (!isOnline && requiresConnection) {
      setShowOfflineWarning(true);
    } else {
      setShowOfflineWarning(false);
    }
  }, [isOnline, requiresConnection]);

  /**
   * Monitor connection quality
   */
  useEffect(() => {
    if (isOnline && (connectionQuality === 'poor' || connectionQuality === 'fair')) {
      setShowSlowConnectionWarning(true);
    } else {
      setShowSlowConnectionWarning(false);
    }
  }, [isOnline, connectionQuality]);

  /**
   * Auto-sync when coming online
   */
  useEffect(() => {
    if (wasOffline && isOnline && hasUnsyncedData) {
      // Delay sync to ensure connection is stable
      const syncTimeout = setTimeout(() => {
        handleSyncData();
      }, 2000);

      return () => clearTimeout(syncTimeout);
    }
  }, [wasOffline, isOnline, hasUnsyncedData, handleSyncData]);

  // Recovery actions for step errors
  const stepRecoveryActions: RecoveryAction[] = [
    {
      label: stepError.isRetrying ? 'Retrying...' : 'Try Again',
      action: handleRetryStep,
      disabled: stepError.isRetrying,
      loading: stepError.isRetrying,
      icon: RefreshCw,
      variant: 'default',
    },
    ...(step > 1 ? [{
      label: 'Go Back',
      action: handleGoBack,
      icon: ArrowLeft,
      variant: 'outline' as const,
    }] : []),
    ...(allowOfflineMode ? [{
      label: 'Continue Offline',
      action: () => setStepError(prev => ({ ...prev, hasError: false })),
      icon: WifiOff,
      variant: 'secondary' as const,
    }] : []),
  ];

  return (
    <div className={cn('relative', className)}>
      {/* Connection Status Indicators */}
      <div className="space-y-2 mb-4">
        {/* Offline Warning */}
        {showOfflineWarning && (
          <Alert className="border-amber-200 bg-amber-50 dark:bg-amber-950/30">
            <WifiOff className="h-4 w-4 text-amber-600" />
            <AlertDescription className="text-amber-800 dark:text-amber-200">
              <div className="flex items-center justify-between">
                <span>
                  You're offline. {allowOfflineMode ? 'You can continue, and your progress will be saved locally.' : 'Please reconnect to continue.'}
                </span>
                {hasUnsyncedData && (
                  <Badge variant="outline" className="ml-2">
                    {Object.keys(stepProgress).length} items to sync
                  </Badge>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Slow Connection Warning */}
        {showSlowConnectionWarning && (
          <Alert className="border-orange-200 bg-orange-50 dark:bg-orange-950/30">
            <Zap className="h-4 w-4 text-orange-600" />
            <AlertDescription className="text-orange-800 dark:text-orange-200">
              Your connection is slow ({connectionQuality}). Some features may take longer to load.
            </AlertDescription>
          </Alert>
        )}

        {/* Sync Status */}
        {hasUnsyncedData && isOnline && syncStatus === 'idle' && (
          <Alert className="border-blue-200 bg-blue-50 dark:bg-blue-950/30">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800 dark:text-blue-200">
              <div className="flex items-center justify-between">
                <span>You have unsaved changes that need to be synced.</span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleSyncData}
                  disabled={syncStatus === 'syncing'}
                >
                  {syncStatus === 'syncing' ? (
                    <>
                      <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                      Syncing...
                    </>
                  ) : (
                    'Sync Now'
                  )}
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Connection Restored */}
        {wasOffline && isOnline && (
          <SuccessMessage
            title="Connection Restored"
            message={`You were offline for ${Math.round(offlineDuration / 1000)} seconds. Your data is being synced.`}
            onDismiss={() => {/* handled by useOnlineStatus */}}
          />
        )}

        {/* Auto-save Status */}
        {autoSaveEnabled && autoSaveStatus !== 'idle' && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            {autoSaveStatus === 'saving' && (
              <>
                <RefreshCw className="h-3 w-3 animate-spin" />
                Saving progress...
              </>
            )}
            {autoSaveStatus === 'saved' && (
              <>
                <Save className="h-3 w-3 text-green-600" />
                Progress saved
              </>
            )}
            {autoSaveStatus === 'error' && (
              <>
                <AlertCircle className="h-3 w-3 text-red-600" />
                Save failed
              </>
            )}
          </div>
        )}
      </div>

      {/* Step Error Display */}
      {stepError.hasError && (
        <div className="mb-4">
          <ErrorAlert
            title="Step Error"
            message={stepError.error?.message || 'An error occurred in this step.'}
            severity="error"
            context={{
              step,
              stepName,
              timestamp: new Date(stepError.lastErrorTime),
            }}
            recoveryActions={stepRecoveryActions}
            canRetry={stepError.errorCount < 3}
            retryCount={stepError.errorCount}
            maxRetries={3}
            helpText={
              !isOnline
                ? 'This error might be related to your internet connection. You can continue offline or wait until you\'re back online.'
                : stepError.errorCount > 1
                ? 'Multiple errors have occurred. Consider going back to the previous step or continuing offline.'
                : undefined
            }
          />
        </div>
      )}

      {/* Error Boundary for Step Content */}
      <OnboardingStepErrorBoundary
        step={step}
        stepName={stepName}
        onRetry={handleRetryStep}
        onGoBack={handleGoBack}
        fallbackComponent={({ error, retryCount, onRetry, onGoBack }) => (
          <div className="text-center py-8">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Step Error</h3>
            <p className="text-muted-foreground mb-4">
              {error?.message || `An error occurred in ${stepName}.`}
            </p>
            <div className="flex justify-center gap-2">
              <Button onClick={onRetry} disabled={retryCount >= 3}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
              {onGoBack && (
                <Button variant="outline" onClick={onGoBack}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Go Back
                </Button>
              )}
            </div>
          </div>
        )}
      >
        {/* Render step content */}
        {React.cloneElement(children as React.ReactElement, {
          onStepComplete: handleStepComplete,
          onStepError: handleStepError,
          isOnline,
          connectionQuality,
          stepProgress: stepProgress[`step${step}` as keyof typeof stepProgress],
          recoverStepData: () => recoverStepData(step),
        })}
      </OnboardingStepErrorBoundary>
    </div>
  );
}

export default OnboardingWithErrorRecovery;