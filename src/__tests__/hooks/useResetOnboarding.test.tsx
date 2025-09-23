/**
 * useResetOnboarding Hook Test
 *
 * Unit test for the useResetOnboarding hook functionality including
 * API integration, error handling, and navigation logic.
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { useResetOnboarding } from '@/hooks/useResetOnboarding';
import { apiClient } from '@/lib/api-client';
import { toast } from '@/components/ui/use-toast';

// Mock dependencies
vi.mock('@/lib/api-client');
vi.mock('@/components/ui/use-toast');

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock Firebase auth
vi.mock('@/contexts/FirebaseAuthContext', () => ({
  useFirebaseAuth: () => ({
    isAuthenticated: true,
    user: { uid: 'test-user' },
  }),
}));

// Test wrapper
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

describe('useResetOnboarding', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.clearAllTimers();
  });

  it('should provide reset function and initial state', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useResetOnboarding(), { wrapper });

    expect(result.current.resetOnboarding).toBeDefined();
    expect(typeof result.current.resetOnboarding).toBe('function');
    expect(result.current.isResetting).toBe(false);
    expect(result.current.error).toBe(null);
    expect(result.current.reset).toBeDefined();
  });

  it('should call API and show success on reset', async () => {
    vi.useFakeTimers();
    vi.mocked(apiClient.resetOnboarding).mockResolvedValue();

    const wrapper = createWrapper();
    const { result } = renderHook(() => useResetOnboarding(), { wrapper });

    // Trigger reset
    await result.current.resetOnboarding();

    // Check API was called
    expect(apiClient.resetOnboarding).toHaveBeenCalledOnce();

    // Check success toast
    expect(toast).toHaveBeenCalledWith({
      title: 'Onboarding Reset',
      description: 'Your preferences have been reset. Redirecting to onboarding...',
    });

    // Fast-forward timers to trigger navigation
    vi.advanceTimersByTime(1500);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding', { replace: true });
    });
  });

  it('should handle API errors', async () => {
    const mockError = new Error('Reset failed');
    vi.mocked(apiClient.resetOnboarding).mockRejectedValue(mockError);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useResetOnboarding(), { wrapper });

    await result.current.resetOnboarding();

    expect(toast).toHaveBeenCalledWith({
      title: 'Reset Failed',
      description: 'Failed to reset onboarding. Please try again or contact support.',
      variant: 'destructive',
    });

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('should show loading state during reset', async () => {
    let resolveReset: () => void;
    const resetPromise = new Promise<void>((resolve) => {
      resolveReset = resolve;
    });
    vi.mocked(apiClient.resetOnboarding).mockReturnValue(resetPromise);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useResetOnboarding(), { wrapper });

    // Start reset
    const resetCall = result.current.resetOnboarding();

    // Check loading state
    await waitFor(() => {
      expect(result.current.isResetting).toBe(true);
    });

    // Resolve the API call
    resolveReset!();
    await resetCall;

    // Check loading state is cleared
    await waitFor(() => {
      expect(result.current.isResetting).toBe(false);
    });
  });

  it('should clear errors when reset function is called', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useResetOnboarding(), { wrapper });

    // Reset function should be available
    expect(result.current.reset).toBeDefined();
    expect(typeof result.current.reset).toBe('function');

    // Should not throw when called
    expect(() => result.current.reset()).not.toThrow();
  });

  it('should invalidate queries on successful reset', async () => {
    vi.useFakeTimers();
    vi.mocked(apiClient.resetOnboarding).mockResolvedValue();

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries');
    const removeQueriesSpy = vi.spyOn(queryClient, 'removeQueries');

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    );

    const { result } = renderHook(() => useResetOnboarding(), { wrapper });

    await result.current.resetOnboarding();

    expect(invalidateQueriesSpy).toHaveBeenCalledWith({ queryKey: ['user'] });
    expect(invalidateQueriesSpy).toHaveBeenCalledWith({ queryKey: ['auth'] });
    expect(invalidateQueriesSpy).toHaveBeenCalledWith({ queryKey: ['home'] });
    expect(removeQueriesSpy).toHaveBeenCalledWith({ queryKey: ['user', 'profile'] });
    expect(removeQueriesSpy).toHaveBeenCalledWith({ queryKey: ['auth', 'onboarding-status'] });
  });
});