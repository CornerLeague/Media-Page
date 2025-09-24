/**
 * OfflineIndicator Component
 *
 * A flexible offline indicator component that shows connection status,
 * network quality, and provides user-friendly messages about offline functionality.
 */

import React, { useState } from 'react';
import { WifiOff, Wifi, Signal, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import useOnlineStatus from '@/hooks/useOnlineStatus';
import { cn } from '@/lib/utils';

interface OfflineIndicatorProps {
  variant?: 'badge' | 'alert' | 'card' | 'minimal';
  showConnectionQuality?: boolean;
  showRetryButton?: boolean;
  onRetry?: () => void;
  className?: string;
  hideWhenOnline?: boolean;
  customOfflineMessage?: string;
  customOnlineMessage?: string;
}

/**
 * Get connection quality icon and color
 */
function getConnectionIcon(quality: string, isOnline: boolean) {
  if (!isOnline) {
    return { icon: WifiOff, color: 'text-red-500', bgColor: 'bg-red-100 dark:bg-red-900/30' };
  }

  switch (quality) {
    case 'excellent':
      return { icon: Wifi, color: 'text-green-500', bgColor: 'bg-green-100 dark:bg-green-900/30' };
    case 'good':
      return { icon: Signal, color: 'text-blue-500', bgColor: 'bg-blue-100 dark:bg-blue-900/30' };
    case 'fair':
      return { icon: Signal, color: 'text-yellow-500', bgColor: 'bg-yellow-100 dark:bg-yellow-900/30' };
    case 'poor':
      return { icon: Signal, color: 'text-orange-500', bgColor: 'bg-orange-100 dark:bg-orange-900/30' };
    default:
      return { icon: Wifi, color: 'text-gray-500', bgColor: 'bg-gray-100 dark:bg-gray-900/30' };
  }
}

/**
 * Get connection quality label
 */
function getConnectionLabel(quality: string, isOnline: boolean): string {
  if (!isOnline) return 'Offline';

  switch (quality) {
    case 'excellent':
      return 'Excellent';
    case 'good':
      return 'Good';
    case 'fair':
      return 'Fair';
    case 'poor':
      return 'Poor';
    default:
      return 'Unknown';
  }
}

/**
 * Badge variant of offline indicator
 */
function OfflineBadge({
  isOnline,
  connectionQuality,
  showConnectionQuality,
  className,
}: {
  isOnline: boolean;
  connectionQuality: string;
  showConnectionQuality: boolean;
  className?: string;
}) {
  const { icon: Icon, color } = getConnectionIcon(connectionQuality, isOnline);
  const label = getConnectionLabel(connectionQuality, isOnline);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <Badge
            variant={isOnline ? 'secondary' : 'destructive'}
            className={cn('flex items-center gap-1', className)}
          >
            <Icon className={cn('h-3 w-3', color)} />
            {showConnectionQuality ? label : isOnline ? 'Online' : 'Offline'}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>
            Connection: {label}
            {!isOnline && (
              <span className="block text-xs text-muted-foreground">
                Your progress is saved locally
              </span>
            )}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Alert variant of offline indicator
 */
function OfflineAlert({
  isOnline,
  connectionQuality,
  showRetryButton,
  onRetry,
  customOfflineMessage,
  customOnlineMessage,
  className,
}: {
  isOnline: boolean;
  connectionQuality: string;
  showRetryButton: boolean;
  onRetry?: () => void;
  customOfflineMessage?: string;
  customOnlineMessage?: string;
  className?: string;
}) {
  const { icon: Icon, color, bgColor } = getConnectionIcon(connectionQuality, isOnline);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    if (!onRetry) return;

    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setTimeout(() => setIsRetrying(false), 1000);
    }
  };

  if (isOnline) {
    const message = customOnlineMessage ||
      (connectionQuality === 'poor' || connectionQuality === 'fair'
        ? `You're online but your connection is ${connectionQuality.toLowerCase()}. Some features may load slowly.`
        : 'You\'re online with a good connection.');

    return (
      <Alert className={cn(bgColor, 'border-green-200', className)}>
        <Icon className={cn('h-4 w-4', color)} />
        <AlertDescription className="text-green-800 dark:text-green-200">
          {message}
        </AlertDescription>
      </Alert>
    );
  }

  const offlineMessage = customOfflineMessage ||
    'You\'re currently offline. Don\'t worry - your progress is being saved locally and will sync when you reconnect.';

  return (
    <Alert className={cn('border-red-200', bgColor, className)}>
      <Icon className={cn('h-4 w-4', color)} />
      <AlertDescription className="text-red-800 dark:text-red-200">
        <div className="flex items-center justify-between">
          <span>{offlineMessage}</span>
          {showRetryButton && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleRetry}
              disabled={isRetrying}
              className="ml-4 bg-white/50 hover:bg-white/80"
            >
              {isRetrying ? (
                <RefreshCw className="h-3 w-3 animate-spin" />
              ) : (
                <>
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Retry
                </>
              )}
            </Button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
}

/**
 * Card variant of offline indicator
 */
function OfflineCard({
  isOnline,
  connectionQuality,
  networkInfo,
  showRetryButton,
  onRetry,
  className,
}: {
  isOnline: boolean;
  connectionQuality: string;
  networkInfo: any;
  showRetryButton: boolean;
  onRetry?: () => void;
  className?: string;
}) {
  const { icon: Icon, color } = getConnectionIcon(connectionQuality, isOnline);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    if (!onRetry) return;

    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setTimeout(() => setIsRetrying(false), 1000);
    }
  };

  return (
    <Card className={cn('w-full max-w-md', className)}>
      <CardContent className="pt-6">
        <div className="flex items-center space-x-3">
          <div className={cn('p-2 rounded-full',
            isOnline ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30'
          )}>
            <Icon className={cn('h-5 w-5', color)} />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold">
              {isOnline ? 'Connected' : 'Offline'}
            </h4>
            <p className="text-sm text-muted-foreground">
              {isOnline
                ? `Connection quality: ${getConnectionLabel(connectionQuality, isOnline)}`
                : 'Your progress is saved locally'
              }
            </p>
            {isOnline && networkInfo && (
              <div className="mt-2 space-y-1 text-xs text-muted-foreground">
                {networkInfo.connectionType !== 'unknown' && (
                  <div>Type: {networkInfo.connectionType}</div>
                )}
                {networkInfo.downlink > 0 && (
                  <div>Speed: ~{networkInfo.downlink} Mbps</div>
                )}
                {networkInfo.rtt > 0 && (
                  <div>Latency: {networkInfo.rtt}ms</div>
                )}
              </div>
            )}
          </div>
          {showRetryButton && !isOnline && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleRetry}
              disabled={isRetrying}
            >
              {isRetrying ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Minimal variant of offline indicator
 */
function OfflineMinimal({
  isOnline,
  connectionQuality,
  className,
}: {
  isOnline: boolean;
  connectionQuality: string;
  className?: string;
}) {
  const { icon: Icon, color } = getConnectionIcon(connectionQuality, isOnline);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <div className={cn('flex items-center gap-1', className)}>
            <Icon className={cn('h-4 w-4', color)} />
            <div className={cn('h-2 w-2 rounded-full',
              isOnline ? 'bg-green-500' : 'bg-red-500'
            )} />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>
            {isOnline ? 'Online' : 'Offline'}
            {isOnline && connectionQuality !== 'excellent' && (
              <span className="block text-xs">
                Connection: {getConnectionLabel(connectionQuality, isOnline)}
              </span>
            )}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Main OfflineIndicator component
 */
export function OfflineIndicator({
  variant = 'badge',
  showConnectionQuality = false,
  showRetryButton = false,
  onRetry,
  className,
  hideWhenOnline = false,
  customOfflineMessage,
  customOnlineMessage,
}: OfflineIndicatorProps) {
  const { isOnline, connectionQuality, networkInfo } = useOnlineStatus({
    showToasts: false,
  });

  // Hide when online if requested
  if (hideWhenOnline && isOnline) {
    return null;
  }

  switch (variant) {
    case 'badge':
      return (
        <OfflineBadge
          isOnline={isOnline}
          connectionQuality={connectionQuality}
          showConnectionQuality={showConnectionQuality}
          className={className}
        />
      );

    case 'alert':
      return (
        <OfflineAlert
          isOnline={isOnline}
          connectionQuality={connectionQuality}
          showRetryButton={showRetryButton}
          onRetry={onRetry}
          customOfflineMessage={customOfflineMessage}
          customOnlineMessage={customOnlineMessage}
          className={className}
        />
      );

    case 'card':
      return (
        <OfflineCard
          isOnline={isOnline}
          connectionQuality={connectionQuality}
          networkInfo={networkInfo}
          showRetryButton={showRetryButton}
          onRetry={onRetry}
          className={className}
        />
      );

    case 'minimal':
      return (
        <OfflineMinimal
          isOnline={isOnline}
          connectionQuality={connectionQuality}
          className={className}
        />
      );

    default:
      return null;
  }
}

export default OfflineIndicator;