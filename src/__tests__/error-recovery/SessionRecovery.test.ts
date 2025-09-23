/**
 * Session Recovery Tests
 *
 * Tests for session persistence and recovery functionality.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { SessionRecoveryManager } from '@/lib/session-recovery';
import { onboardingDataRecovery } from '@/lib/onboarding-recovery';

describe('SessionRecoveryManager', () => {
  let sessionManager: SessionRecoveryManager;
  let mockLocalStorage: any;

  beforeEach(() => {
    // Mock localStorage
    mockLocalStorage = {};
    global.localStorage = {
      getItem: vi.fn((key) => mockLocalStorage[key] || null),
      setItem: vi.fn((key, value) => {
        mockLocalStorage[key] = value;
      }),
      removeItem: vi.fn((key) => {
        delete mockLocalStorage[key];
      }),
      clear: vi.fn(() => {
        mockLocalStorage = {};
      }),
    } as any;

    // Mock window events
    global.window = {
      ...global.window,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    } as any;

    global.document = {
      ...global.document,
      addEventListener: vi.fn(),
      visibilityState: 'visible',
    } as any;

    global.navigator = {
      ...global.navigator,
      onLine: true,
    } as any;

    sessionManager = new SessionRecoveryManager();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Session State Management', () => {
    it('saves and restores session state', () => {
      const userId = 'user123';
      const currentStep = 3;
      const completedSteps = [1, 2];

      sessionManager.saveSessionState(userId, currentStep, completedSteps);

      const restored = sessionManager.restoreSessionState();

      expect(restored).toMatchObject({
        userId,
        currentStep,
        completedSteps,
      });
      expect(restored?.sessionId).toBeDefined();
      expect(restored?.version).toBe('1.0.0');
    });

    it('returns null for expired session', () => {
      const userId = 'user123';
      const currentStep = 2;
      const completedSteps = [1];

      // Save session state
      sessionManager.saveSessionState(userId, currentStep, completedSteps);

      // Mock expired session (25 hours ago)
      const expiredTime = Date.now() - (25 * 60 * 60 * 1000);
      const sessionData = JSON.parse(mockLocalStorage['corner-league-session-state']);
      sessionData.lastActiveTime = expiredTime;
      mockLocalStorage['corner-league-session-state'] = JSON.stringify(sessionData);

      const restored = sessionManager.restoreSessionState();

      expect(restored).toBeNull();
    });

    it('handles corrupted session data gracefully', () => {
      mockLocalStorage['corner-league-session-state'] = 'invalid-json';

      const restored = sessionManager.restoreSessionState();

      expect(restored).toBeNull();
    });
  });

  describe('Step Progress Management', () => {
    it('saves and retrieves step progress', () => {
      const stepData = {
        selectedSports: [
          { sportId: 'nfl', rank: 1 },
          { sportId: 'nba', rank: 2 },
        ],
      };

      sessionManager.saveStepProgress(2, stepData);

      const progress = sessionManager.getStepProgress();

      expect(progress.step2).toMatchObject({
        completed: true,
        selectedSports: stepData.selectedSports,
      });
      expect(progress.step2.timestamp).toBeDefined();
    });

    it('recovers step data correctly', () => {
      const sportsData = {
        selectedSports: [{ sportId: 'nfl', rank: 1 }],
      };

      const teamsData = {
        selectedTeams: [
          { teamId: 'cowboys', sportId: 'nfl', affinityScore: 0.9 },
        ],
      };

      sessionManager.saveStepProgress(2, sportsData);
      sessionManager.saveStepProgress(3, teamsData);

      const recoveredSports = sessionManager.recoverStepData(2);
      const recoveredTeams = sessionManager.recoverStepData(3);

      expect(recoveredSports).toEqual(sportsData);
      expect(recoveredTeams).toEqual(teamsData);
    });

    it('returns null for non-existent step data', () => {
      const recovered = sessionManager.recoverStepData(5);
      expect(recovered).toBeNull();
    });
  });

  describe('Sync Queue Management', () => {
    it('adds items to sync queue', () => {
      const stepData = { selectedSports: [{ sportId: 'nfl', rank: 1 }] };

      sessionManager.saveStepProgress(2, stepData);

      const queue = sessionManager.getSyncQueue();

      expect(queue).toHaveLength(1);
      expect(queue[0]).toMatchObject({
        type: 'step-update',
        data: { step: 2, ...stepData },
        retryCount: 0,
        maxRetries: 3,
      });
      expect(queue[0].id).toBeDefined();
      expect(queue[0].timestamp).toBeDefined();
    });

    it('processes sync queue successfully', async () => {
      const mockApiClient = {
        updateOnboardingStep: vi.fn().mockResolvedValue({}),
        completeOnboarding: vi.fn().mockResolvedValue({}),
      };

      // Add items to queue
      sessionManager.saveStepProgress(2, { selectedSports: [] });
      sessionManager.saveStepProgress(3, { selectedTeams: [] });

      const result = await sessionManager.processSyncQueue(mockApiClient);

      expect(result.success).toBe(2);
      expect(result.failed).toBe(0);
      expect(mockApiClient.updateOnboardingStep).toHaveBeenCalledTimes(2);

      // Queue should be empty after successful sync
      const queue = sessionManager.getSyncQueue();
      expect(queue).toHaveLength(0);
    });

    it('handles sync failures with retry logic', async () => {
      const mockApiClient = {
        updateOnboardingStep: vi.fn()
          .mockRejectedValueOnce(new Error('Network error'))
          .mockResolvedValue({}),
      };

      sessionManager.saveStepProgress(2, { selectedSports: [] });

      // First attempt should fail
      let result = await sessionManager.processSyncQueue(mockApiClient);
      expect(result.success).toBe(0);
      expect(result.failed).toBe(0); // Not failed yet, will retry

      let queue = sessionManager.getSyncQueue();
      expect(queue[0].retryCount).toBe(1);

      // Second attempt should succeed
      result = await sessionManager.processSyncQueue(mockApiClient);
      expect(result.success).toBe(1);
      expect(result.failed).toBe(0);

      queue = sessionManager.getSyncQueue();
      expect(queue).toHaveLength(0);
    });

    it('removes items after max retries', async () => {
      const mockApiClient = {
        updateOnboardingStep: vi.fn().mockRejectedValue(new Error('Persistent error')),
      };

      sessionManager.saveStepProgress(2, { selectedSports: [] });

      // Process queue multiple times to exceed max retries
      for (let i = 0; i < 4; i++) {
        await sessionManager.processSyncQueue(mockApiClient);
      }

      const result = await sessionManager.processSyncQueue(mockApiClient);
      expect(result.failed).toBe(1);

      // Item should be removed from queue
      const queue = sessionManager.getSyncQueue();
      expect(queue).toHaveLength(0);
    });
  });

  describe('Recovery Metadata', () => {
    it('tracks recovery metadata', () => {
      const metadata = sessionManager.getRecoveryMetadata();

      expect(metadata).toMatchObject({
        lastSyncTime: 0,
        pendingSyncItems: [],
        recoveryCount: 0,
        lastRecoveryTime: 0,
        apiAvailable: true,
        networkStatus: 'online',
      });
    });

    it('updates network status', () => {
      // Simulate offline
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      const newManager = new SessionRecoveryManager();
      const metadata = newManager.getRecoveryMetadata();

      expect(metadata.networkStatus).toBe('offline');
    });
  });

  describe('Data Export and Cleanup', () => {
    it('exports session data for debugging', () => {
      sessionManager.saveSessionState('user123', 2, [1]);
      sessionManager.saveStepProgress(2, { selectedSports: [] });

      const exported = sessionManager.exportSessionData();

      expect(exported).toHaveProperty('sessionState');
      expect(exported).toHaveProperty('stepProgress');
      expect(exported).toHaveProperty('syncQueue');
      expect(exported).toHaveProperty('recoveryMetadata');
    });

    it('clears all session data', () => {
      sessionManager.saveSessionState('user123', 2, [1]);
      sessionManager.saveStepProgress(2, { selectedSports: [] });

      sessionManager.clearSessionData();

      expect(sessionManager.restoreSessionState()).toBeNull();
      expect(sessionManager.getSyncQueue()).toHaveLength(0);
    });
  });

  describe('Error Handling', () => {
    it('handles localStorage errors gracefully', () => {
      // Mock localStorage to throw errors
      global.localStorage.setItem = vi.fn().mockImplementation(() => {
        throw new Error('Quota exceeded');
      });

      // Should not throw
      expect(() => {
        sessionManager.saveSessionState('user123', 2, [1]);
      }).not.toThrow();
    });

    it('handles malformed data gracefully', () => {
      mockLocalStorage['corner-league-step-progress'] = '{invalid-json}';

      const progress = sessionManager.getStepProgress();

      // Should return default progress structure
      expect(progress).toMatchObject({
        step1: { completed: false },
        step2: { completed: false, selectedSports: [] },
        step3: { completed: false, selectedTeams: [] },
        step4: { completed: false, preferences: null },
        step5: { completed: false },
      });
    });
  });
});

describe('OnboardingDataRecovery', () => {
  beforeEach(() => {
    // Mock localStorage for recovery tests
    global.localStorage = {
      getItem: vi.fn().mockReturnValue(null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    } as any;
  });

  describe('Data Recovery', () => {
    it('recovers valid sports data', async () => {
      const validSportsData = {
        selectedSports: [
          { sportId: 'nfl', rank: 1 },
          { sportId: 'nba', rank: 2 },
        ],
      };

      // Mock session manager to return data
      vi.spyOn(sessionManager, 'recoverStepData').mockReturnValue(validSportsData);

      const result = await onboardingDataRecovery.recoverStepData(2);

      expect(result.success).toBe(true);
      expect(result.recoveredData).toEqual(validSportsData);
      expect(result.validationResult.isValid).toBe(true);
    });

    it('validates and fixes corrupted data', async () => {
      const corruptedData = {
        selectedSports: [
          { sportId: 'nfl' }, // Missing rank
          { sportId: 'nba', rank: 0 }, // Invalid rank
          { sportId: 'nfl', rank: 2 }, // Duplicate sport
        ],
      };

      vi.spyOn(sessionManager, 'recoverStepData').mockReturnValue(corruptedData);

      const result = await onboardingDataRecovery.recoverStepData(2);

      expect(result.success).toBe(true);
      expect(result.validationResult.warnings.length).toBeGreaterThan(0);
      expect(result.recoveredData.selectedSports).toHaveLength(1); // Duplicates removed
      expect(result.recoveredData.selectedSports[0].rank).toBe(1); // Rank fixed
    });

    it('provides default data when no sources available', async () => {
      vi.spyOn(sessionManager, 'recoverStepData').mockReturnValue(null);

      const result = await onboardingDataRecovery.recoverStepData(2);

      expect(result.success).toBe(false);
      expect(result.source).toBe('default');
      expect(result.recoveredData).toEqual({ selectedSports: [] });
    });
  });

  describe('Data Validation', () => {
    it('validates sports data correctly', async () => {
      const validData = {
        selectedSports: [
          { sportId: 'nfl', rank: 1 },
          { sportId: 'nba', rank: 2 },
        ],
      };

      vi.spyOn(sessionManager, 'recoverStepData').mockReturnValue(validData);

      const result = await onboardingDataRecovery.recoverStepData(2);

      expect(result.validationResult.isValid).toBe(true);
      expect(result.validationResult.errors).toHaveLength(0);
    });

    it('detects validation errors', async () => {
      const invalidData = {
        selectedSports: 'not-an-array', // Should be array
      };

      vi.spyOn(sessionManager, 'recoverStepData').mockReturnValue(invalidData);

      const result = await onboardingDataRecovery.recoverStepData(2);

      expect(result.validationResult.isValid).toBe(false);
      expect(result.validationResult.errors.length).toBeGreaterThan(0);
    });

    it('validates teams data', async () => {
      const validTeamsData = {
        selectedTeams: [
          {
            teamId: 'cowboys',
            sportId: 'nfl',
            affinityScore: 0.8,
          },
        ],
      };

      vi.spyOn(sessionManager, 'recoverStepData').mockReturnValue(validTeamsData);

      const result = await onboardingDataRecovery.recoverStepData(3);

      expect(result.validationResult.isValid).toBe(true);
    });

    it('validates preferences data', async () => {
      const validPreferencesData = {
        preferences: {
          newsTypes: [
            { type: 'injuries', enabled: true, priority: 1 },
          ],
          notifications: {
            push: true,
            email: false,
            gameReminders: true,
            newsAlerts: false,
            scoreUpdates: true,
          },
          contentFrequency: 'standard',
        },
      };

      vi.spyOn(sessionManager, 'recoverStepData').mockReturnValue(validPreferencesData);

      const result = await onboardingDataRecovery.recoverStepData(4);

      expect(result.validationResult.isValid).toBe(true);
    });
  });

  describe('Data Backup and Recovery', () => {
    it('creates and retrieves backups', () => {
      const testData = { selectedSports: [{ sportId: 'nfl', rank: 1 }] };

      onboardingDataRecovery.createBackup(2, testData);

      // Mock localStorage to return the backup
      const backups = [{
        id: 'backup-2-123',
        timestamp: Date.now(),
        step: 2,
        data: testData,
        version: '1.0.0',
        checksum: 'abc123',
      }];

      global.localStorage.getItem = vi.fn().mockReturnValue(JSON.stringify(backups));

      // The recovery should find the backup
      expect(global.localStorage.setItem).toHaveBeenCalled();
    });

    it('limits backup count', () => {
      // Create many backups
      for (let i = 0; i < 15; i++) {
        onboardingDataRecovery.createBackup(2, { test: i });
      }

      // Should only keep max backups (10)
      const lastCall = (global.localStorage.setItem as any).mock.calls.slice(-1)[0];
      const backups = JSON.parse(lastCall[1]);
      expect(backups.length).toBeLessThanOrEqual(10);
    });
  });

  describe('Conflict Resolution', () => {
    it('resolves conflicts based on timestamps', () => {
      const localData = { timestamp: Date.now() - 1000 };
      const remoteData = { timestamp: Date.now() };

      const resolution = onboardingDataRecovery.resolveConflict(localData, remoteData, 2);

      expect(resolution.strategy).toBe('remote');
      expect(resolution.reason).toContain('more recent');
    });

    it('merges data when timestamps are equal', () => {
      const timestamp = Date.now();
      const localData = { timestamp, local: true };
      const remoteData = { timestamp, remote: true };

      const resolution = onboardingDataRecovery.resolveConflict(localData, remoteData, 2);

      expect(resolution.strategy).toBe('merge');
      expect(resolution.mergedData).toBeDefined();
    });
  });
});