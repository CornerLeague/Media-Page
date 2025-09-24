/**
 * Error Recovery Integration Test
 *
 * Test suite to verify error recovery features work correctly in the onboarding flow.
 * This includes offline detection, retry logic, and error boundaries.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { toast } from '@/components/ui/use-toast';

// Import components to test
import ErrorBoundaryProvider from '@/components/error-boundaries/ErrorBoundaryProvider';
import OnboardingWithErrorRecovery from '@/components/onboarding/OnboardingWithErrorRecovery';
import OfflineIndicator from '@/components/ui/OfflineIndicator';
import useOnlineStatus from '@/hooks/useOnlineStatus';
import useOnboardingApiWithRetry from '@/hooks/useOnboardingApiWithRetry';

// Mock toast
vi.mock('@/components/ui/use-toast', () => ({
  toast: vi.fn(),
}));

// Mock API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    getOnboardingSports: vi.fn(),
    getOnboardingTeams: vi.fn(),
    updateOnboardingStep: vi.fn(),
    completeOnboarding: vi.fn(),
    requestWithRetry: vi.fn(),
  },
  ApiClientError: class MockApiClientError extends Error {
    constructor(
      public apiError: { code: string; message: string },
      public statusCode: number
    ) {
      super(apiError.message);
      this.name = 'ApiClientError';
    }

    get code() {
      return this.apiError.code;
    }
  },
}));

// Mock session recovery
vi.mock('@/hooks/useSessionRecovery', () => ({
  default: () => ({
    sessionState: null,
    stepProgress: {},
    isRecovering: false,
    hasUnsyncedData: false,
    saveStepProgress: vi.fn(),
    recoverStepData: vi.fn(),
    syncWithAPI: vi.fn().mockResolvedValue({ success: 1, failed: 0 }),
    syncStatus: 'idle',
  }),
}));

// Mock online status hook
const mockOnlineStatus = {
  isOnline: true,
  networkInfo: {
    connectionType: 'wifi',
    effectiveType: '4g',
    downlink: 10,
    rtt: 50,
    saveData: false,
  },
  connectionQuality: 'excellent',
  wasOffline: false,
  lastOnlineTime: Date.now(),
  offlineDuration: 0,
  onlineHandlers: {
    onConnectionRestored: vi.fn(),
    onConnectionLost: vi.fn(),
  },
};

vi.mock('@/hooks/useOnlineStatus', () => ({
  default: vi.fn(() => mockOnlineStatus),
}));

// Test wrapper component
function TestWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/onboarding/step/1']}>
        <ErrorBoundaryProvider enableErrorReporting={false}>
          {children}
        </ErrorBoundaryProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

// Mock step component
function MockStepComponent({
  onStepComplete,
  onStepError,
  triggerError,
  triggerComplete,
}: {
  onStepComplete?: (data: any) => void;
  onStepError?: (error: Error) => void;
  triggerError?: boolean;
  triggerComplete?: boolean;
}) {
  React.useEffect(() => {
    if (triggerError && onStepError) {
      onStepError(new Error('Mock step error'));
    }
    if (triggerComplete && onStepComplete) {
      onStepComplete({ step: 1, data: 'mock data' });
    }
  }, [triggerError, triggerComplete, onStepError, onStepComplete]);

  return (
    <div data-testid="mock-step">
      <h2>Mock Onboarding Step</h2>
      <button onClick={() => onStepError?.(new Error('Manual error'))}>
        Trigger Error
      </button>
      <button onClick={() => onStepComplete?.({ step: 1, data: 'completed' })}>
        Complete Step
      </button>
    </div>
  );
}

describe('Error Recovery Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset online status to default
    Object.assign(mockOnlineStatus, {
      isOnline: true,
      connectionQuality: 'excellent',
      wasOffline: false,
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Offline Indicator', () => {
    it('shows online status correctly', () => {
      render(
        <TestWrapper>
          <OfflineIndicator variant="badge" showConnectionQuality />
        </TestWrapper>
      );

      expect(screen.getByText(/excellent/i)).toBeInTheDocument();
    });

    it('shows offline status correctly', () => {
      // Mock offline state
      vi.mocked(useOnlineStatus).mockReturnValue({
        ...mockOnlineStatus,
        isOnline: false,
        connectionQuality: 'poor',
      });

      render(
        <TestWrapper>
          <OfflineIndicator variant="alert" />
        </TestWrapper>
      );

      expect(screen.getByText(/offline/i)).toBeInTheDocument();
      expect(screen.getByText(/progress is being saved locally/i)).toBeInTheDocument();
    });

    it('shows connection quality warnings', () => {
      // Mock slow connection
      vi.mocked(useOnlineStatus).mockReturnValue({
        ...mockOnlineStatus,
        connectionQuality: 'poor',
      });

      render(
        <TestWrapper>
          <OfflineIndicator variant="alert" showConnectionQuality />
        </TestWrapper>
      );

      expect(screen.getByText(/connection is poor/i)).toBeInTheDocument();
    });
  });

  describe('OnboardingWithErrorRecovery', () => {
    it('renders step content correctly', () => {
      render(
        <TestWrapper>
          <OnboardingWithErrorRecovery step={1} stepName="Test Step">
            <MockStepComponent />
          </OnboardingWithErrorRecovery>
        </TestWrapper>
      );

      expect(screen.getByTestId('mock-step')).toBeInTheDocument();
      expect(screen.getByText('Mock Onboarding Step')).toBeInTheDocument();
    });

    it('shows offline warning when offline', () => {
      // Mock offline state
      vi.mocked(useOnlineStatus).mockReturnValue({
        ...mockOnlineStatus,
        isOnline: false,
      });

      render(
        <TestWrapper>
          <OnboardingWithErrorRecovery step={1} stepName="Test Step">
            <MockStepComponent />
          </OnboardingWithErrorRecovery>
        </TestWrapper>
      );

      expect(screen.getByText(/offline/i)).toBeInTheDocument();
      expect(screen.getByText(/progress will be saved locally/i)).toBeInTheDocument();
    });

    it('shows slow connection warning', () => {
      // Mock slow connection
      vi.mocked(useOnlineStatus).mockReturnValue({
        ...mockOnlineStatus,
        connectionQuality: 'poor',
      });

      render(
        <TestWrapper>
          <OnboardingWithErrorRecovery step={1} stepName="Test Step">
            <MockStepComponent />
          </OnboardingWithErrorRecovery>
        </TestWrapper>
      );

      expect(screen.getByText(/connection is slow/i)).toBeInTheDocument();
    });

    it('handles step errors correctly', async () => {
      render(
        <TestWrapper>
          <OnboardingWithErrorRecovery step={1} stepName="Test Step">
            <MockStepComponent />
          </OnboardingWithErrorRecovery>
        </TestWrapper>
      );

      // Trigger error
      fireEvent.click(screen.getByText('Trigger Error'));

      await waitFor(() => {
        expect(screen.getByText(/step error/i)).toBeInTheDocument();
        expect(screen.getByText(/manual error/i)).toBeInTheDocument();
      });

      // Check retry button exists
      expect(screen.getByText(/try again/i)).toBeInTheDocument();
    });

    it('handles step completion correctly', async () => {
      const onStepComplete = vi.fn();

      render(
        <TestWrapper>
          <OnboardingWithErrorRecovery
            step={1}
            stepName="Test Step"
            onStepComplete={onStepComplete}
          >
            <MockStepComponent />
          </OnboardingWithErrorRecovery>
        </TestWrapper>
      );

      // Complete step
      fireEvent.click(screen.getByText('Complete Step'));

      await waitFor(() => {
        expect(onStepComplete).toHaveBeenCalledWith({ step: 1, data: 'completed' });
        expect(toast).toHaveBeenCalledWith({
          title: 'Progress Saved',
          description: 'Step 1 completed successfully.',
          variant: 'default',
        });
      });
    });
  });

  describe('Error Boundary Provider', () => {
    it('catches and displays errors correctly', () => {
      const ErrorComponent = () => {
        throw new Error('Test error boundary');
      };

      render(
        <TestWrapper>
          <ErrorComponent />
        </TestWrapper>
      );

      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('provides retry functionality', async () => {
      let shouldThrow = true;
      const ErrorComponent = () => {
        if (shouldThrow) {
          throw new Error('Recoverable error');
        }
        return <div>Component recovered</div>;
      };

      render(
        <TestWrapper>
          <ErrorComponent />
        </TestWrapper>
      );

      // Error should be displayed
      expect(screen.getByText(/application error/i)).toBeInTheDocument();

      // Simulate fixing the issue
      shouldThrow = false;

      // Find and click retry button
      const retryButton = screen.getByText(/try again/i);
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText('Component recovered')).toBeInTheDocument();
      });
    });
  });

  describe('useOnboardingApiWithRetry Hook', () => {
    it('handles successful API calls', async () => {
      const { result } = renderHook(() => useOnboardingApiWithRetry(), {
        wrapper: ({ children }) => <TestWrapper>{children}</TestWrapper>,
      });

      // Mock successful API response
      const mockApiClient = await import('@/lib/api-client');
      vi.mocked(mockApiClient.apiClient.getOnboardingSports).mockResolvedValue([
        { id: '1', name: 'Football' },
      ]);

      const sports = await result.current.getSports();

      expect(sports).toEqual([{ id: '1', name: 'Football' }]);
      expect(result.current.apiState.error).toBeNull();
    });

    it('handles API errors with retry', async () => {
      const { result } = renderHook(() => useOnboardingApiWithRetry(), {
        wrapper: ({ children }) => <TestWrapper>{children}</TestWrapper>,
      });

      // Mock API error
      const mockApiClient = await import('@/lib/api-client');
      const error = new mockApiClient.ApiClientError(
        { code: 'NETWORK_ERROR', message: 'Network failure' },
        0
      );
      vi.mocked(mockApiClient.apiClient.getOnboardingSports).mockRejectedValue(error);

      try {
        await result.current.getSports();
      } catch (e) {
        // Expected to throw
      }

      expect(result.current.apiState.error).toBeTruthy();
      expect(result.current.apiState.error?.code).toBe('NETWORK_ERROR');
      expect(result.current.canRetry).toBe(true);
    });

    it('handles offline scenarios', async () => {
      // Mock offline state
      vi.mocked(useOnlineStatus).mockReturnValue({
        ...mockOnlineStatus,
        isOnline: false,
      });

      const { result } = renderHook(() => useOnboardingApiWithRetry(), {
        wrapper: ({ children }) => <TestWrapper>{children}</TestWrapper>,
      });

      expect(result.current.isOnline).toBe(false);
    });
  });
});

// Helper to render hooks
function renderHook<T>(
  hook: () => T,
  options?: { wrapper?: React.ComponentType<{ children: React.ReactNode }> }
) {
  const result: { current: T } = { current: undefined as any };

  function HookWrapper() {
    result.current = hook();
    return null;
  }

  const Wrapper = options?.wrapper || React.Fragment;
  render(<Wrapper><HookWrapper /></Wrapper>);

  return { result };
}