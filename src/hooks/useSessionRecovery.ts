/**
 * useSessionRecovery Hook
 *
 * Custom hook for managing session persistence and automatic recovery
 * during the onboarding flow.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { sessionRecoveryManager, SessionState, StepProgress } from '@/lib/session-recovery';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { apiClient } from '@/lib/api-client';
import { toast } from '@/components/ui/use-toast';

export interface UseSessionRecoveryResult {
  // Session state
  sessionState: SessionState | null;
  stepProgress: StepProgress;
  isRecovering: boolean;
  hasUnsyncedData: boolean;

  // Recovery actions
  saveStepProgress: (step: number, data: any) => void;
  recoverStepData: (step: number) => any;
  syncWithAPI: () => Promise<{ success: number; failed: number }>;
  clearSession: () => void;

  // Navigation helpers
  recoverNavigationState: () => void;
  determineStartingStep: () => number;

  // Status indicators
  isOnline: boolean;
  lastSyncTime: number | null;
  syncStatus: 'idle' | 'syncing' | 'success' | 'error';
}

export function useSessionRecovery(): UseSessionRecoveryResult {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated } = useFirebaseAuth();

  // State
  const [sessionState, setSessionState] = useState<SessionState | null>(null);
  const [stepProgress, setStepProgress] = useState<StepProgress>(
    sessionRecoveryManager.getStepProgress()
  );
  const [isRecovering, setIsRecovering] = useState(true);
  const [hasUnsyncedData, setHasUnsyncedData] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastSyncTime, setLastSyncTime] = useState<number | null>(null);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');

  // Refs to prevent stale closures
  const syncTimeoutRef = useRef<NodeJS.Timeout>();
  const recoveryCompleteRef = useRef(false);

  /**
   * Initialize session recovery on mount
   */
  useEffect(() => {
    const initializeRecovery = async () => {
      try {
        setIsRecovering(true);

        // Restore session state
        const restored = sessionRecoveryManager.restoreSessionState();
        setSessionState(restored);

        // Update progress from storage
        const progress = sessionRecoveryManager.getStepProgress();
        setStepProgress(progress);

        // Check for unsynced data
        const syncQueue = sessionRecoveryManager.getSyncQueue();
        setHasUnsyncedData(syncQueue.length > 0);

        // Get last sync time
        const metadata = sessionRecoveryManager.getRecoveryMetadata();
        setLastSyncTime(metadata.lastSyncTime || null);

        // Auto-recover navigation state if needed
        if (restored && !recoveryCompleteRef.current) {
          recoverNavigationState();
        }

        recoveryCompleteRef.current = true;
      } catch (error) {
        console.error('Failed to initialize session recovery:', error);
        toast({
          title: 'Recovery Error',
          description: 'Failed to restore your previous session. Starting fresh.',
          variant: 'destructive',
        });
      } finally {
        setIsRecovering(false);
      }
    };

    initializeRecovery();
  }, []);

  /**
   * Update session state when user changes
   */
  useEffect(() => {
    if (user?.uid && sessionState) {
      sessionRecoveryManager.saveSessionState(
        user.uid,
        sessionState.currentStep,
        sessionState.completedSteps
      );
    }
  }, [user?.uid, sessionState]);

  /**
   * Monitor network status
   */
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Auto-sync when coming back online
      if (hasUnsyncedData && isAuthenticated) {
        setTimeout(() => {
          syncWithAPI();
        }, 1000); // Delay to ensure connection is stable
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      setSyncStatus('idle');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [hasUnsyncedData, isAuthenticated]);

  /**
   * Auto-sync periodically when online
   */
  useEffect(() => {
    if (isOnline && isAuthenticated && hasUnsyncedData) {
      // Clear existing timeout
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current);
      }

      // Schedule sync after delay
      syncTimeoutRef.current = setTimeout(() => {
        syncWithAPI();
      }, 5000); // 5 second delay
    }

    return () => {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current);
      }
    };
  }, [isOnline, isAuthenticated, hasUnsyncedData]);

  /**
   * Save step progress
   */
  const saveStepProgress = useCallback((step: number, data: any) => {
    try {
      sessionRecoveryManager.saveStepProgress(step, data);

      // Update local state
      const updated = sessionRecoveryManager.getStepProgress();
      setStepProgress(updated);

      // Update session state
      setSessionState(prev => {
        if (!prev) return prev;

        const updatedCompletedSteps = [...prev.completedSteps];
        if (!updatedCompletedSteps.includes(step)) {
          updatedCompletedSteps.push(step);
        }

        const newState = {
          ...prev,
          currentStep: Math.max(step + 1, prev.currentStep),
          completedSteps: updatedCompletedSteps,
        };

        // Persist to storage
        if (user?.uid) {
          sessionRecoveryManager.saveSessionState(
            user.uid,
            newState.currentStep,
            newState.completedSteps
          );
        }

        return newState;
      });

      // Mark as having unsynced data
      setHasUnsyncedData(true);

      toast({
        title: 'Progress Saved',
        description: `Step ${step} completed and saved locally.`,
        variant: 'default',
      });
    } catch (error) {
      console.error('Failed to save step progress:', error);
      toast({
        title: 'Save Error',
        description: 'Failed to save progress. Please try again.',
        variant: 'destructive',
      });
    }
  }, [user?.uid]);

  /**
   * Recover step data
   */
  const recoverStepData = useCallback((step: number): any => {
    return sessionRecoveryManager.recoverStepData(step);
  }, []);

  /**
   * Sync with API
   */
  const syncWithAPI = useCallback(async (): Promise<{ success: number; failed: number }> => {
    if (!isAuthenticated || !isOnline) {
      return { success: 0, failed: 0 };
    }

    try {
      setSyncStatus('syncing');

      const result = await sessionRecoveryManager.processSyncQueue(apiClient);

      if (result.success > 0) {
        setLastSyncTime(Date.now());
        toast({
          title: 'Sync Complete',
          description: `Successfully synced ${result.success} items.`,
          variant: 'default',
        });
      }

      if (result.failed > 0) {
        console.warn(`Failed to sync ${result.failed} items`);
      }

      // Update unsynced data status
      const remainingQueue = sessionRecoveryManager.getSyncQueue();
      setHasUnsyncedData(remainingQueue.length > 0);

      setSyncStatus(result.failed > 0 ? 'error' : 'success');

      return result;
    } catch (error) {
      console.error('Sync failed:', error);
      setSyncStatus('error');

      toast({
        title: 'Sync Failed',
        description: 'Failed to sync with server. Will retry automatically.',
        variant: 'destructive',
      });

      return { success: 0, failed: 1 };
    }
  }, [isAuthenticated, isOnline]);

  /**
   * Clear session
   */
  const clearSession = useCallback(() => {
    sessionRecoveryManager.clearSessionData();
    setSessionState(null);
    setStepProgress(sessionRecoveryManager.getStepProgress());
    setHasUnsyncedData(false);
    setLastSyncTime(null);
    setSyncStatus('idle');

    toast({
      title: 'Session Cleared',
      description: 'All onboarding data has been cleared.',
      variant: 'default',
    });
  }, []);

  /**
   * Recover navigation state
   */
  const recoverNavigationState = useCallback(() => {
    if (!sessionState) return;

    const currentPath = location.pathname;
    const currentStepMatch = currentPath.match(/\/onboarding\/step\/(\d+)/);
    const currentStepFromUrl = currentStepMatch ? parseInt(currentStepMatch[1], 10) : null;

    // If we're not on an onboarding step or the step doesn't match session state
    if (!currentStepFromUrl || currentStepFromUrl !== sessionState.currentStep) {
      const targetStep = sessionState.currentStep;
      const targetPath = `/onboarding/step/${targetStep}`;

      if (currentPath !== targetPath) {
        navigate(targetPath, { replace: true });

        toast({
          title: 'Session Restored',
          description: `Continuing from step ${targetStep} where you left off.`,
          variant: 'default',
        });
      }
    }
  }, [sessionState, location.pathname, navigate]);

  /**
   * Determine starting step based on progress
   */
  const determineStartingStep = useCallback((): number => {
    if (sessionState) {
      return sessionState.currentStep;
    }

    // Find the last completed step
    const progress = stepProgress;
    for (let step = 5; step >= 1; step--) {
      const stepKey = `step${step}` as keyof StepProgress;
      if (progress[stepKey]?.completed) {
        return Math.min(step + 1, 5); // Next step or final step
      }
    }

    return 1; // Start from beginning
  }, [sessionState, stepProgress]);

  return {
    // Session state
    sessionState,
    stepProgress,
    isRecovering,
    hasUnsyncedData,

    // Recovery actions
    saveStepProgress,
    recoverStepData,
    syncWithAPI,
    clearSession,

    // Navigation helpers
    recoverNavigationState,
    determineStartingStep,

    // Status indicators
    isOnline,
    lastSyncTime,
    syncStatus,
  };
}

export default useSessionRecovery;