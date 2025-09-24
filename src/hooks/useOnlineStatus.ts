/**
 * useOnlineStatus Hook
 *
 * Custom hook for detecting and monitoring online/offline status.
 * Provides comprehensive network connectivity monitoring with recovery features.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from '@/components/ui/use-toast';

export interface NetworkInfo {
  isOnline: boolean;
  connectionType: 'wifi' | 'cellular' | 'ethernet' | 'unknown';
  effectiveType: '2g' | '3g' | '4g' | 'slow-2g' | 'unknown';
  downlink: number; // Mbps
  rtt: number; // ms round trip time
  saveData: boolean;
}

export interface OnlineStatusHookResult {
  isOnline: boolean;
  networkInfo: NetworkInfo;
  isSlowConnection: boolean;
  wasOffline: boolean;
  connectionQuality: 'poor' | 'fair' | 'good' | 'excellent';
  lastOnlineTime: number | null;
  lastOfflineTime: number | null;
  offlineDuration: number; // milliseconds
  onlineHandlers: {
    onConnectionRestored: () => void;
    onConnectionLost: () => void;
  };
}

/**
 * Get network connection information
 */
function getNetworkInfo(): NetworkInfo {
  const navigator = window.navigator as any;

  // Default fallback values
  const defaultInfo: NetworkInfo = {
    isOnline: navigator.onLine,
    connectionType: 'unknown',
    effectiveType: 'unknown',
    downlink: 0,
    rtt: 0,
    saveData: false,
  };

  // Check for Network Information API support
  const connection = navigator.connection ||
                    navigator.mozConnection ||
                    navigator.webkitConnection;

  if (!connection) {
    return defaultInfo;
  }

  return {
    isOnline: navigator.onLine,
    connectionType: connection.type || 'unknown',
    effectiveType: connection.effectiveType || 'unknown',
    downlink: connection.downlink || 0,
    rtt: connection.rtt || 0,
    saveData: connection.saveData || false,
  };
}

/**
 * Determine connection quality based on network metrics
 */
function getConnectionQuality(networkInfo: NetworkInfo): 'poor' | 'fair' | 'good' | 'excellent' {
  if (!networkInfo.isOnline) {
    return 'poor';
  }

  // If we have downlink data, use it
  if (networkInfo.downlink > 0) {
    if (networkInfo.downlink >= 10) return 'excellent';
    if (networkInfo.downlink >= 2) return 'good';
    if (networkInfo.downlink >= 0.5) return 'fair';
    return 'poor';
  }

  // Fallback to effective type
  switch (networkInfo.effectiveType) {
    case '4g':
      return 'excellent';
    case '3g':
      return 'good';
    case '2g':
      return 'fair';
    case 'slow-2g':
    default:
      return 'poor';
  }
}

export function useOnlineStatus({
  showToasts = true,
  enableNetworkAPI = true,
  connectionTestUrl,
}: {
  showToasts?: boolean;
  enableNetworkAPI?: boolean;
  connectionTestUrl?: string;
} = {}): OnlineStatusHookResult {

  // State
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [networkInfo, setNetworkInfo] = useState<NetworkInfo>(getNetworkInfo);
  const [wasOffline, setWasOffline] = useState(false);
  const [lastOnlineTime, setLastOnlineTime] = useState<number | null>(null);
  const [lastOfflineTime, setLastOfflineTime] = useState<number | null>(null);
  const [offlineDuration, setOfflineDuration] = useState(0);

  // Refs to track state changes
  const previousOnlineRef = useRef(navigator.onLine);
  const offlineStartTimeRef = useRef<number | null>(null);

  // Derived state
  const connectionQuality = getConnectionQuality(networkInfo);
  const isSlowConnection = connectionQuality === 'poor' || connectionQuality === 'fair';

  /**
   * Handle online status change
   */
  const handleOnline = useCallback(async () => {
    const now = Date.now();

    // Test actual connectivity if URL provided
    if (connectionTestUrl) {
      try {
        await fetch(connectionTestUrl, {
          method: 'HEAD',
          mode: 'no-cors',
          cache: 'no-cache',
        });
      } catch {
        // If test fails, we might not actually be online
        return;
      }
    }

    setIsOnline(true);
    setLastOnlineTime(now);

    // Calculate offline duration if we were offline
    if (offlineStartTimeRef.current) {
      const duration = now - offlineStartTimeRef.current;
      setOfflineDuration(duration);
      offlineStartTimeRef.current = null;
    }

    // Update network info
    if (enableNetworkAPI) {
      setNetworkInfo(getNetworkInfo());
    }

    // Show reconnection toast
    if (showToasts && wasOffline) {
      const duration = offlineDuration > 0 ?
        Math.round(offlineDuration / 1000) : 0;

      toast({
        title: 'Connection Restored',
        description: duration > 0 ?
          `You were offline for ${duration} seconds.` :
          'Your internet connection has been restored.',
        variant: 'default',
      });
    }

    setWasOffline(false);
    previousOnlineRef.current = true;
  }, [connectionTestUrl, enableNetworkAPI, showToasts, wasOffline, offlineDuration]);

  /**
   * Handle offline status change
   */
  const handleOffline = useCallback(() => {
    const now = Date.now();

    setIsOnline(false);
    setWasOffline(true);
    setLastOfflineTime(now);
    offlineStartTimeRef.current = now;

    // Update network info
    if (enableNetworkAPI) {
      setNetworkInfo(getNetworkInfo());
    }

    // Show offline toast
    if (showToasts && previousOnlineRef.current) {
      toast({
        title: 'Connection Lost',
        description: 'You are currently offline. Your progress will be saved locally.',
        variant: 'destructive',
      });
    }

    previousOnlineRef.current = false;
  }, [enableNetworkAPI, showToasts]);

  /**
   * Handle connection change (for Network Information API)
   */
  const handleConnectionChange = useCallback(() => {
    if (!enableNetworkAPI) return;

    setNetworkInfo(getNetworkInfo());

    // Check if connection quality changed significantly
    const newQuality = getConnectionQuality(getNetworkInfo());
    if (newQuality !== connectionQuality && showToasts) {
      const qualityMessages = {
        poor: 'Connection is slow. Some features may be limited.',
        fair: 'Connection quality is fair.',
        good: 'Connection quality is good.',
        excellent: 'Connection quality is excellent.',
      };

      if (newQuality === 'poor' || newQuality === 'fair') {
        toast({
          title: 'Slow Connection',
          description: qualityMessages[newQuality],
          variant: 'destructive',
        });
      }
    }
  }, [enableNetworkAPI, connectionQuality, showToasts]);

  /**
   * Test connectivity with a ping-like request
   */
  const testConnectivity = useCallback(async (): Promise<boolean> => {
    if (!navigator.onLine) {
      return false;
    }

    try {
      // Use a fast, reliable endpoint
      const testUrl = connectionTestUrl || 'https://www.google.com/favicon.ico';

      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000); // 5 second timeout

      await fetch(testUrl, {
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-cache',
        signal: controller.signal,
      });

      clearTimeout(timeout);
      return true;
    } catch {
      return false;
    }
  }, [connectionTestUrl]);

  /**
   * Initialize and set up event listeners
   */
  useEffect(() => {
    const navigator = window.navigator as any;

    // Initial state
    const initialNetworkInfo = getNetworkInfo();
    setNetworkInfo(initialNetworkInfo);
    setIsOnline(initialNetworkInfo.isOnline);

    if (initialNetworkInfo.isOnline) {
      setLastOnlineTime(Date.now());
    } else {
      setLastOfflineTime(Date.now());
      setWasOffline(true);
      offlineStartTimeRef.current = Date.now();
    }

    // Add online/offline listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Add connection change listener if supported
    const connection = navigator.connection ||
                      navigator.mozConnection ||
                      navigator.webkitConnection;

    if (connection && enableNetworkAPI) {
      connection.addEventListener('change', handleConnectionChange);
    }

    // Periodic connectivity check (every 30 seconds when online)
    const connectivityInterval = setInterval(async () => {
      if (navigator.onLine) {
        const actuallyOnline = await testConnectivity();
        if (!actuallyOnline && isOnline) {
          handleOffline();
        } else if (actuallyOnline && !isOnline) {
          handleOnline();
        }
      }
    }, 30000);

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);

      if (connection && enableNetworkAPI) {
        connection.removeEventListener('change', handleConnectionChange);
      }

      clearInterval(connectivityInterval);
    };
  }, [handleOnline, handleOffline, handleConnectionChange, enableNetworkAPI, testConnectivity, isOnline]);

  /**
   * Update offline duration periodically while offline
   */
  useEffect(() => {
    if (!isOnline && offlineStartTimeRef.current) {
      const updateDuration = () => {
        setOfflineDuration(Date.now() - offlineStartTimeRef.current!);
      };

      const interval = setInterval(updateDuration, 1000);
      return () => clearInterval(interval);
    }
  }, [isOnline]);

  return {
    isOnline,
    networkInfo,
    isSlowConnection,
    wasOffline,
    connectionQuality,
    lastOnlineTime,
    lastOfflineTime,
    offlineDuration,
    onlineHandlers: {
      onConnectionRestored: handleOnline,
      onConnectionLost: handleOffline,
    },
  };
}

export default useOnlineStatus;