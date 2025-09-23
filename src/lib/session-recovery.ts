/**
 * Session Recovery Utilities
 *
 * Enhanced session persistence and recovery for onboarding flow.
 * Handles automatic data recovery on refresh, network failures, and error scenarios.
 */

import { OnboardingStatus, OnboardingSport, OnboardingTeam } from './api-client';

// Storage keys for session persistence
const RECOVERY_STORAGE_KEYS = {
  SESSION_STATE: 'corner-league-session-state',
  STEP_PROGRESS: 'corner-league-step-progress',
  RECOVERY_METADATA: 'corner-league-recovery-metadata',
  ERROR_LOG: 'corner-league-error-log',
  SYNC_QUEUE: 'corner-league-sync-queue',
} as const;

// Session state interface
export interface SessionState {
  userId: string | null;
  currentStep: number;
  completedSteps: number[];
  lastActiveTime: number;
  sessionId: string;
  version: string; // For migration handling
}

// Step progress data
export interface StepProgress {
  step1: {
    completed: boolean;
    timestamp?: number;
  };
  step2: {
    completed: boolean;
    selectedSports: OnboardingSport[];
    timestamp?: number;
  };
  step3: {
    completed: boolean;
    selectedTeams: OnboardingTeam[];
    timestamp?: number;
  };
  step4: {
    completed: boolean;
    preferences: any;
    timestamp?: number;
  };
  step5: {
    completed: boolean;
    timestamp?: number;
  };
}

// Recovery metadata
export interface RecoveryMetadata {
  lastSyncTime: number;
  pendingSyncItems: string[];
  recoveryCount: number;
  lastRecoveryTime: number;
  apiAvailable: boolean;
  networkStatus: 'online' | 'offline' | 'unknown';
}

// Sync queue item
export interface SyncQueueItem {
  id: string;
  type: 'step-update' | 'completion' | 'preference-update';
  data: any;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
}

/**
 * Session Recovery Manager
 */
export class SessionRecoveryManager {
  private sessionId: string;
  private version = '1.0.0';
  private maxRetries = 3;
  private syncRetryDelay = 1000;
  private sessionTimeout = 24 * 60 * 60 * 1000; // 24 hours

  constructor() {
    this.sessionId = this.generateSessionId();
    this.initializeSession();
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Initialize session recovery system
   */
  private initializeSession(): void {
    // Clean up expired sessions
    this.cleanupExpiredData();

    // Set up network status monitoring
    this.setupNetworkMonitoring();

    // Set up visibility change monitoring for session management
    this.setupVisibilityMonitoring();
  }

  /**
   * Save current session state
   */
  saveSessionState(userId: string | null, currentStep: number, completedSteps: number[]): void {
    try {
      const sessionState: SessionState = {
        userId,
        currentStep,
        completedSteps,
        lastActiveTime: Date.now(),
        sessionId: this.sessionId,
        version: this.version,
      };

      localStorage.setItem(RECOVERY_STORAGE_KEYS.SESSION_STATE, JSON.stringify(sessionState));
    } catch (error) {
      console.warn('Failed to save session state:', error);
    }
  }

  /**
   * Restore session state
   */
  restoreSessionState(): SessionState | null {
    try {
      const stored = localStorage.getItem(RECOVERY_STORAGE_KEYS.SESSION_STATE);
      if (!stored) return null;

      const sessionState: SessionState = JSON.parse(stored);

      // Check if session is expired
      const now = Date.now();
      if (now - sessionState.lastActiveTime > this.sessionTimeout) {
        this.clearSessionData();
        return null;
      }

      // Handle version migration if needed
      if (sessionState.version !== this.version) {
        return this.migrateSessionState(sessionState);
      }

      return sessionState;
    } catch (error) {
      console.warn('Failed to restore session state:', error);
      return null;
    }
  }

  /**
   * Save step progress
   */
  saveStepProgress(step: number, data: any): void {
    try {
      const existing = this.getStepProgress();
      const timestamp = Date.now();

      const updated: StepProgress = {
        ...existing,
        [`step${step}`]: {
          completed: true,
          timestamp,
          ...data,
        },
      };

      localStorage.setItem(RECOVERY_STORAGE_KEYS.STEP_PROGRESS, JSON.stringify(updated));

      // Add to sync queue for later API sync
      this.addToSyncQueue({
        id: `step-${step}-${timestamp}`,
        type: 'step-update',
        data: { step, ...data },
        timestamp,
        retryCount: 0,
        maxRetries: this.maxRetries,
      });
    } catch (error) {
      console.warn('Failed to save step progress:', error);
    }
  }

  /**
   * Get step progress
   */
  getStepProgress(): StepProgress {
    try {
      const stored = localStorage.getItem(RECOVERY_STORAGE_KEYS.STEP_PROGRESS);
      if (!stored) {
        return this.getDefaultStepProgress();
      }

      return JSON.parse(stored);
    } catch (error) {
      console.warn('Failed to get step progress:', error);
      return this.getDefaultStepProgress();
    }
  }

  /**
   * Get default step progress structure
   */
  private getDefaultStepProgress(): StepProgress {
    return {
      step1: { completed: false },
      step2: { completed: false, selectedSports: [] },
      step3: { completed: false, selectedTeams: [] },
      step4: { completed: false, preferences: null },
      step5: { completed: false },
    };
  }

  /**
   * Recover step data for specific step
   */
  recoverStepData(step: number): any {
    const progress = this.getStepProgress();
    const stepKey = `step${step}` as keyof StepProgress;
    const stepData = progress[stepKey];

    if (!stepData || !stepData.completed) {
      return null;
    }

    // Return step-specific data
    switch (step) {
      case 2:
        return { selectedSports: (stepData as any).selectedSports || [] };
      case 3:
        return { selectedTeams: (stepData as any).selectedTeams || [] };
      case 4:
        return { preferences: (stepData as any).preferences };
      default:
        return {};
    }
  }

  /**
   * Clear all session data
   */
  clearSessionData(): void {
    try {
      Object.values(RECOVERY_STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
      });
    } catch (error) {
      console.warn('Failed to clear session data:', error);
    }
  }

  /**
   * Add item to sync queue
   */
  private addToSyncQueue(item: SyncQueueItem): void {
    try {
      const existing = this.getSyncQueue();
      const updated = [...existing, item];

      // Keep only last 50 items
      if (updated.length > 50) {
        updated.splice(0, updated.length - 50);
      }

      localStorage.setItem(RECOVERY_STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to add to sync queue:', error);
    }
  }

  /**
   * Get sync queue
   */
  getSyncQueue(): SyncQueueItem[] {
    try {
      const stored = localStorage.getItem(RECOVERY_STORAGE_KEYS.SYNC_QUEUE);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.warn('Failed to get sync queue:', error);
      return [];
    }
  }

  /**
   * Process sync queue
   */
  async processSyncQueue(apiClient: any): Promise<{ success: number; failed: number }> {
    const queue = this.getSyncQueue();
    let success = 0;
    let failed = 0;

    for (const item of queue) {
      try {
        await this.syncItem(apiClient, item);
        success++;

        // Remove successful item from queue
        this.removeSyncQueueItem(item.id);
      } catch (error) {
        console.warn(`Failed to sync item ${item.id}:`, error);

        // Increment retry count
        item.retryCount++;

        if (item.retryCount >= item.maxRetries) {
          // Remove failed item after max retries
          this.removeSyncQueueItem(item.id);
          failed++;
        } else {
          // Update retry count in storage
          this.updateSyncQueueItem(item);
        }
      }
    }

    return { success, failed };
  }

  /**
   * Sync individual item
   */
  private async syncItem(apiClient: any, item: SyncQueueItem): Promise<void> {
    switch (item.type) {
      case 'step-update':
        await apiClient.updateOnboardingStep({
          step: item.data.step,
          data: item.data,
        });
        break;
      case 'completion':
        await apiClient.completeOnboarding(item.data);
        break;
      case 'preference-update':
        await apiClient.updatePreferences(item.data);
        break;
      default:
        throw new Error(`Unknown sync item type: ${item.type}`);
    }
  }

  /**
   * Remove item from sync queue
   */
  private removeSyncQueueItem(itemId: string): void {
    try {
      const queue = this.getSyncQueue();
      const updated = queue.filter(item => item.id !== itemId);
      localStorage.setItem(RECOVERY_STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to remove sync queue item:', error);
    }
  }

  /**
   * Update item in sync queue
   */
  private updateSyncQueueItem(updatedItem: SyncQueueItem): void {
    try {
      const queue = this.getSyncQueue();
      const index = queue.findIndex(item => item.id === updatedItem.id);

      if (index !== -1) {
        queue[index] = updatedItem;
        localStorage.setItem(RECOVERY_STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(queue));
      }
    } catch (error) {
      console.warn('Failed to update sync queue item:', error);
    }
  }

  /**
   * Setup network monitoring
   */
  private setupNetworkMonitoring(): void {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => {
        this.updateRecoveryMetadata({ networkStatus: 'online' });
      });

      window.addEventListener('offline', () => {
        this.updateRecoveryMetadata({ networkStatus: 'offline' });
      });
    }
  }

  /**
   * Setup visibility monitoring
   */
  private setupVisibilityMonitoring(): void {
    if (typeof document !== 'undefined') {
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          // Update last active time when page becomes visible
          const sessionState = this.restoreSessionState();
          if (sessionState) {
            this.saveSessionState(
              sessionState.userId,
              sessionState.currentStep,
              sessionState.completedSteps
            );
          }
        }
      });
    }
  }

  /**
   * Update recovery metadata
   */
  private updateRecoveryMetadata(updates: Partial<RecoveryMetadata>): void {
    try {
      const existing = this.getRecoveryMetadata();
      const updated = { ...existing, ...updates };
      localStorage.setItem(RECOVERY_STORAGE_KEYS.RECOVERY_METADATA, JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to update recovery metadata:', error);
    }
  }

  /**
   * Get recovery metadata
   */
  getRecoveryMetadata(): RecoveryMetadata {
    try {
      const stored = localStorage.getItem(RECOVERY_STORAGE_KEYS.RECOVERY_METADATA);
      if (!stored) {
        return {
          lastSyncTime: 0,
          pendingSyncItems: [],
          recoveryCount: 0,
          lastRecoveryTime: 0,
          apiAvailable: true,
          networkStatus: navigator.onLine ? 'online' : 'offline',
        };
      }

      return JSON.parse(stored);
    } catch (error) {
      console.warn('Failed to get recovery metadata:', error);
      return {
        lastSyncTime: 0,
        pendingSyncItems: [],
        recoveryCount: 0,
        lastRecoveryTime: 0,
        apiAvailable: true,
        networkStatus: 'unknown',
      };
    }
  }

  /**
   * Clean up expired data
   */
  private cleanupExpiredData(): void {
    try {
      const sessionState = this.restoreSessionState();
      if (!sessionState) {
        // Clear all data if session is expired
        this.clearSessionData();
      }
    } catch (error) {
      console.warn('Failed to cleanup expired data:', error);
    }
  }

  /**
   * Migrate session state to new version
   */
  private migrateSessionState(oldState: SessionState): SessionState {
    // Handle version migrations here
    return {
      ...oldState,
      version: this.version,
    };
  }

  /**
   * Export session data for debugging
   */
  exportSessionData(): any {
    return {
      sessionState: this.restoreSessionState(),
      stepProgress: this.getStepProgress(),
      syncQueue: this.getSyncQueue(),
      recoveryMetadata: this.getRecoveryMetadata(),
    };
  }
}

// Global session recovery manager instance
export const sessionRecoveryManager = new SessionRecoveryManager();

export default sessionRecoveryManager;