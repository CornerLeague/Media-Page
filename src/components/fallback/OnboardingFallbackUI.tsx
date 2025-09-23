/**
 * OnboardingFallbackUI Components
 *
 * Fallback UI components for graceful degradation during onboarding errors.
 * Provides offline modes, skeleton loaders, and error states.
 */

import React from 'react';
import { AlertTriangle, Wifi, WifiOff, RefreshCw, Clock, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

export interface FallbackUIProps {
  type: 'loading' | 'error' | 'offline' | 'empty' | 'timeout';
  title?: string;
  message?: string;
  onRetry?: () => void;
  onSkip?: () => void;
  showProgress?: boolean;
  progress?: number;
  retryCount?: number;
  maxRetries?: number;
  className?: string;
}

/**
 * Loading Skeleton for Sports Selection
 */
export function SportsSelectionSkeleton() {
  return (
    <div className="space-y-4" data-testid="sports-skeleton">
      <div className="text-center space-y-4">
        <Skeleton className="h-6 w-64 mx-auto" />
        <div className="flex justify-center gap-3">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-20" />
        </div>
      </div>

      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <Skeleton className="h-5 w-5" />
                <Skeleton className="h-8 w-8 rounded" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-4 w-24" />
                </div>
                <Skeleton className="h-5 w-5 rounded" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

/**
 * Loading Skeleton for Team Selection
 */
export function TeamSelectionSkeleton() {
  return (
    <div className="space-y-6" data-testid="teams-skeleton">
      <div className="text-center space-y-4">
        <Skeleton className="h-6 w-48 mx-auto" />
        <Skeleton className="h-10 w-64 mx-auto" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 9 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="space-y-3">
                <Skeleton className="h-16 w-16 rounded-full mx-auto" />
                <div className="text-center space-y-2">
                  <Skeleton className="h-5 w-24 mx-auto" />
                  <Skeleton className="h-4 w-16 mx-auto" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

/**
 * Generic Fallback UI
 */
export function OnboardingFallbackUI({
  type,
  title,
  message,
  onRetry,
  onSkip,
  showProgress = false,
  progress = 0,
  retryCount = 0,
  maxRetries = 3,
  className,
}: FallbackUIProps) {
  const getIcon = () => {
    switch (type) {
      case 'loading':
        return <RefreshCw className="h-8 w-8 animate-spin text-primary" />;
      case 'error':
        return <AlertTriangle className="h-8 w-8 text-red-500" />;
      case 'offline':
        return <WifiOff className="h-8 w-8 text-orange-500" />;
      case 'timeout':
        return <Clock className="h-8 w-8 text-yellow-500" />;
      case 'empty':
        return <AlertTriangle className="h-8 w-8 text-muted-foreground" />;
      default:
        return <AlertTriangle className="h-8 w-8 text-muted-foreground" />;
    }
  };

  const getTitle = () => {
    if (title) return title;

    switch (type) {
      case 'loading':
        return 'Loading...';
      case 'error':
        return 'Something went wrong';
      case 'offline':
        return 'You\'re offline';
      case 'timeout':
        return 'Request timed out';
      case 'empty':
        return 'No data available';
      default:
        return 'Something went wrong';
    }
  };

  const getMessage = () => {
    if (message) return message;

    switch (type) {
      case 'loading':
        return 'Please wait while we load your data...';
      case 'error':
        return 'An unexpected error occurred. Please try again.';
      case 'offline':
        return 'Check your internet connection and try again.';
      case 'timeout':
        return 'The request is taking longer than expected. Please try again.';
      case 'empty':
        return 'No data is available at this time.';
      default:
        return 'Please try again or contact support if the problem persists.';
    }
  };

  const getVariant = () => {
    switch (type) {
      case 'error':
        return 'destructive';
      case 'offline':
        return 'warning';
      case 'timeout':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <div className={cn('flex flex-col items-center justify-center py-12 px-4', className)}>
      <Card className="w-full max-w-md">
        <CardContent className="pt-8 pb-6">
          <div className="text-center space-y-6">
            {/* Icon */}
            <div className="flex justify-center">
              {getIcon()}
            </div>

            {/* Title and Message */}
            <div className="space-y-2">
              <h3 className="font-display font-semibold text-lg">
                {getTitle()}
              </h3>
              <p className="text-muted-foreground text-sm">
                {getMessage()}
              </p>
            </div>

            {/* Progress Bar */}
            {showProgress && (
              <div className="space-y-2">
                <Progress value={progress} className="h-2" />
                <p className="text-xs text-muted-foreground">
                  {Math.round(progress)}% complete
                </p>
              </div>
            )}

            {/* Retry Count */}
            {retryCount > 0 && (
              <div className="flex justify-center">
                <Badge variant="outline">
                  Attempt {retryCount} of {maxRetries}
                </Badge>
              </div>
            )}

            {/* Action Buttons */}
            {(onRetry || onSkip) && (
              <div className="space-y-3">
                {onRetry && retryCount < maxRetries && (
                  <Button onClick={onRetry} className="w-full">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Try Again
                  </Button>
                )}

                {onSkip && (
                  <Button onClick={onSkip} variant="outline" className="w-full">
                    Skip for Now
                  </Button>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Offline Mode Banner
 */
export function OfflineModeBanner({
  isVisible = true,
  hasUnsyncedData = false,
  onSync,
  className,
}: {
  isVisible?: boolean;
  hasUnsyncedData?: boolean;
  onSync?: () => void;
  className?: string;
}) {
  if (!isVisible) return null;

  return (
    <Alert className={cn('border-orange-200 bg-orange-50 dark:bg-orange-950/30', className)}>
      <WifiOff className="h-4 w-4 text-orange-600" />
      <AlertDescription className="flex items-center justify-between">
        <div className="space-y-1">
          <p className="font-medium text-orange-800 dark:text-orange-200">
            Working Offline
          </p>
          <p className="text-sm text-orange-700 dark:text-orange-300">
            {hasUnsyncedData
              ? 'Your progress is saved locally and will sync when connection is restored.'
              : 'Your data is being saved locally.'
            }
          </p>
        </div>

        {onSync && hasUnsyncedData && (
          <Button onClick={onSync} size="sm" variant="outline" className="ml-4">
            <Wifi className="h-4 w-4 mr-2" />
            Sync Now
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}

/**
 * Sync Status Indicator
 */
export function SyncStatusIndicator({
  status,
  lastSyncTime,
  hasUnsyncedData,
  onSync,
  className,
}: {
  status: 'idle' | 'syncing' | 'success' | 'error';
  lastSyncTime?: number | null;
  hasUnsyncedData?: boolean;
  onSync?: () => void;
  className?: string;
}) {
  const getIcon = () => {
    switch (status) {
      case 'syncing':
        return <RefreshCw className="h-4 w-4 animate-spin" />;
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return hasUnsyncedData ? (
          <WifiOff className="h-4 w-4 text-orange-500" />
        ) : (
          <Wifi className="h-4 w-4 text-green-500" />
        );
    }
  };

  const getMessage = () => {
    switch (status) {
      case 'syncing':
        return 'Syncing...';
      case 'success':
        return lastSyncTime ? `Synced ${new Date(lastSyncTime).toLocaleTimeString()}` : 'Synced';
      case 'error':
        return 'Sync failed';
      default:
        return hasUnsyncedData ? 'Pending sync' : 'All synced';
    }
  };

  return (
    <div className={cn('flex items-center gap-2 text-sm text-muted-foreground', className)}>
      {getIcon()}
      <span>{getMessage()}</span>

      {onSync && hasUnsyncedData && status !== 'syncing' && (
        <Button onClick={onSync} size="sm" variant="ghost" className="h-6 px-2 text-xs">
          Sync
        </Button>
      )}
    </div>
  );
}

/**
 * Error Boundary Fallback for specific onboarding steps
 */
export function StepErrorFallback({
  step,
  stepName,
  error,
  onRetry,
  onSkip,
  onGoBack,
}: {
  step: number;
  stepName: string;
  error?: Error;
  onRetry?: () => void;
  onSkip?: () => void;
  onGoBack?: () => void;
}) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <AlertTriangle className="h-12 w-12 text-red-500" />
          </div>
          <CardTitle className="text-xl">
            Error on Step {step}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center space-y-2">
            <p className="text-muted-foreground">
              We encountered an error during the {stepName} step.
            </p>
            <p className="text-sm text-muted-foreground">
              Your progress has been saved automatically.
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription className="text-sm">
                <strong>Error:</strong> {error.message}
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-3">
            {onRetry && (
              <Button onClick={onRetry} className="w-full">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            )}

            <div className="flex gap-2">
              {onGoBack && (
                <Button onClick={onGoBack} variant="outline" className="flex-1">
                  Go Back
                </Button>
              )}

              {onSkip && (
                <Button onClick={onSkip} variant="outline" className="flex-1">
                  Skip Step
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default {
  OnboardingFallbackUI,
  SportsSelectionSkeleton,
  TeamSelectionSkeleton,
  OfflineModeBanner,
  SyncStatusIndicator,
  StepErrorFallback,
};