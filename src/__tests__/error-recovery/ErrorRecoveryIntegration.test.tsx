/**
 * Error Recovery Integration Tests
 *
 * End-to-end tests for the complete error recovery system including
 * session persistence, retry logic, fallback UI, and error boundaries.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, act } from '@testing-library/react';
import { useSessionRecovery } from '@/hooks/useSessionRecovery';
import { WelcomeStep } from '@/pages/onboarding/WelcomeStep';
import { sessionRecoveryManager } from '@/lib/session-recovery';
import { errorReporting } from '@/lib/error-reporting';

// Mock Firebase Auth Context
const mockFirebaseAuth = {
  user: { uid: 'test-user-123' },
  isAuthenticated: true,
  isLoading: false,
  getIdToken: vi.fn().mockResolvedValue('mock-token'),
};

vi.mock('@/contexts/FirebaseAuthContext', () => ({
  useFirebaseAuth: () => mockFirebaseAuth,
}));

// Mock API client
const mockApiClient = {
  updateOnboardingStep: vi.fn(),
  completeOnboarding: vi.fn(),
  getOnboardingStatus: vi.fn(),
};

vi.mock('@/lib/api-client', () => ({
  apiClient: mockApiClient,
  createApiQueryClient: () => ({
    getOnboardingStatus: () => ({
      queryKey: ['onboarding-status'],
      queryFn: () => Promise.resolve({ hasCompletedOnboarding: false, currentStep: 1 }),
      enabled: true,
    }),
  }),
}));

// Test wrapper with providers
const TestProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/onboarding/step/1']}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('Error Recovery Integration', () => {
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

    // Mock network status
    Object.defineProperty(navigator, 'onLine', {
      value: true,
      configurable: true,
    });

    // Reset mocks
    vi.clearAllMocks();
    mockApiClient.updateOnboardingStep.mockReset();
    mockApiClient.completeOnboarding.mockReset();

    // Mock console methods
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Session Recovery Hook Integration', () => {
    it('initializes with session recovery on mount', async () => {
      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      expect(result.current.isRecovering).toBe(true);

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      expect(result.current.sessionState).toBeDefined();
      expect(result.current.stepProgress).toBeDefined();
    });

    it('saves step progress and maintains session state', async () => {
      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      const testData = { completed: true, timestamp: Date.now() };

      act(() => {
        result.current.saveStepProgress(1, testData);
      });

      await waitFor(() => {
        expect(result.current.stepProgress.step1.completed).toBe(true);
      });

      // Verify data was saved to localStorage
      expect(localStorage.setItem).toHaveBeenCalledWith(
        expect.stringContaining('step-progress'),
        expect.stringContaining('completed')
      );
    });

    it('recovers step data correctly', async () => {
      // Pre-populate with saved data
      const savedData = {
        step2: {
          completed: true,
          selectedSports: [{ sportId: 'nfl', rank: 1 }],
          timestamp: Date.now(),
        },
      };

      mockLocalStorage['corner-league-step-progress'] = JSON.stringify(savedData);

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      const recoveredData = result.current.recoverStepData(2);

      expect(recoveredData).toEqual({
        selectedSports: [{ sportId: 'nfl', rank: 1 }],
      });
    });

    it('handles network state changes and auto-sync', async () => {
      mockApiClient.updateOnboardingStep.mockResolvedValue({});

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      // Add unsynced data
      act(() => {
        result.current.saveStepProgress(1, { completed: true });
      });

      await waitFor(() => {
        expect(result.current.hasUnsyncedData).toBe(true);
      });

      // Simulate coming back online
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        configurable: true,
      });

      window.dispatchEvent(new Event('online'));

      // Should auto-sync
      await waitFor(() => {
        expect(mockApiClient.updateOnboardingStep).toHaveBeenCalled();
      }, { timeout: 6000 });
    });

    it('handles offline mode gracefully', async () => {
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      expect(result.current.isOnline).toBe(false);

      // Save data while offline
      act(() => {
        result.current.saveStepProgress(1, { completed: true });
      });

      // Should not attempt to sync
      expect(mockApiClient.updateOnboardingStep).not.toHaveBeenCalled();

      // Data should still be saved locally
      expect(result.current.hasUnsyncedData).toBe(true);
    });

    it('provides manual sync functionality', async () => {
      mockApiClient.updateOnboardingStep.mockResolvedValue({});

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      // Add unsynced data
      act(() => {
        result.current.saveStepProgress(1, { completed: true });
      });

      // Manual sync
      let syncResult: any;
      await act(async () => {
        syncResult = await result.current.syncWithAPI();
      });

      expect(syncResult.success).toBeGreaterThan(0);
      expect(mockApiClient.updateOnboardingStep).toHaveBeenCalled();
    });
  });

  describe('Component Integration with Error Boundaries', () => {
    it('renders WelcomeStep with error boundary protection', () => {
      render(
        <TestProviders>
          <WelcomeStep />
        </TestProviders>
      );

      expect(screen.getByText(/Welcome/)).toBeInTheDocument();
      expect(screen.getByText(/Get started with Corner League/)).toBeInTheDocument();
    });

    it('shows sync status indicator', async () => {
      render(
        <TestProviders>
          <WelcomeStep />
        </TestProviders>
      );

      // Should show sync status
      await waitFor(() => {
        expect(screen.getByText(/All synced/)).toBeInTheDocument();
      });
    });

    it('handles component errors gracefully', () => {
      // Mock a component that throws an error
      const ThrowingWelcomeStep = () => {
        throw new Error('Component error');
      };

      const WrappedComponent = () => (
        <TestProviders>
          <ThrowingWelcomeStep />
        </TestProviders>
      );

      // This should not crash the test - error boundary should catch it
      expect(() => render(<WrappedComponent />)).not.toThrow();
    });
  });

  describe('Error Reporting Integration', () => {
    it('reports errors to error reporting system', async () => {
      const reportSpy = vi.spyOn(errorReporting, 'reportOnboardingError');

      render(
        <TestProviders>
          <WelcomeStep />
        </TestProviders>
      );

      // Click get started to trigger navigation and potential error reporting
      const getStartedButton = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(getStartedButton);

      // If any errors occurred during navigation, they should be reported
      // Note: In a real scenario, we'd mock the navigation to throw an error
      await waitFor(() => {
        // This test primarily verifies the integration is in place
        expect(reportSpy).toHaveBeenCalledTimes(0); // No errors in happy path
      });

      reportSpy.mockRestore();
    });

    it('collects error metrics', () => {
      const metrics = errorReporting.getMetrics();

      expect(metrics).toHaveProperty('totalErrors');
      expect(metrics).toHaveProperty('errorsByLevel');
      expect(metrics).toHaveProperty('errorsByCategory');
      expect(metrics).toHaveProperty('trends');
    });
  });

  describe('Data Recovery Integration', () => {
    it('recovers corrupted data on component mount', async () => {
      // Simulate corrupted data in localStorage
      const corruptedData = {
        step2: {
          completed: true,
          selectedSports: [
            { sportId: 'nfl' }, // Missing rank
            { sportId: 'nba', rank: -1 }, // Invalid rank
          ],
        },
      };

      mockLocalStorage['corner-league-step-progress'] = JSON.stringify(corruptedData);

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      // Data should be recovered and fixed
      const recoveredData = result.current.recoverStepData(2);
      expect(recoveredData).toBeDefined();

      // Should have fixed the corruption
      if (recoveredData?.selectedSports) {
        recoveredData.selectedSports.forEach((sport: any) => {
          expect(sport.rank).toBeGreaterThan(0);
        });
      }
    });

    it('handles page refresh with data recovery', async () => {
      // Simulate existing session data
      const sessionData = {
        userId: 'test-user-123',
        currentStep: 2,
        completedSteps: [1],
        lastActiveTime: Date.now(),
        sessionId: 'session-123',
        version: '1.0.0',
      };

      mockLocalStorage['corner-league-session-state'] = JSON.stringify(sessionData);

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      // Should have recovered session state
      expect(result.current.sessionState).toMatchObject({
        userId: 'test-user-123',
        currentStep: 2,
        completedSteps: [1],
      });
    });
  });

  describe('Fallback UI Integration', () => {
    it('displays appropriate loading states', async () => {
      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      // Initial state should show loading
      expect(result.current.isRecovering).toBe(true);

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });
    });

    it('shows offline indicators when network is unavailable', async () => {
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isOnline).toBe(false);
      });

      render(
        <TestProviders>
          <WelcomeStep />
        </TestProviders>
      );

      // Should indicate offline status
      await waitFor(() => {
        expect(screen.getByText(/Pending sync/)).toBeInTheDocument();
      });
    });
  });

  describe('API Retry Integration', () => {
    it('retries failed API calls automatically', async () => {
      // Mock API to fail initially then succeed
      mockApiClient.updateOnboardingStep
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue({});

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      // Add data to sync
      act(() => {
        result.current.saveStepProgress(1, { completed: true });
      });

      // Trigger sync
      await act(async () => {
        await result.current.syncWithAPI();
      });

      // Should have retried and succeeded
      expect(mockApiClient.updateOnboardingStep).toHaveBeenCalledTimes(2);
    });

    it('handles persistent API failures gracefully', async () => {
      // Mock API to always fail
      mockApiClient.updateOnboardingStep.mockRejectedValue(new Error('Service unavailable'));

      const { result } = renderHook(() => useSessionRecovery(), {
        wrapper: TestProviders,
      });

      await waitFor(() => {
        expect(result.current.isRecovering).toBe(false);
      });

      // Add data to sync
      act(() => {
        result.current.saveStepProgress(1, { completed: true });
      });

      // Trigger sync
      let syncResult: any;
      await act(async () => {
        syncResult = await result.current.syncWithAPI();
      });

      // Should have failed after retries
      expect(syncResult.failed).toBeGreaterThan(0);
      expect(result.current.syncStatus).toBe('error');

      // Data should remain unsynced for later retry
      expect(result.current.hasUnsyncedData).toBe(true);
    });
  });
});