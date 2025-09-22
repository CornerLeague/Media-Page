/**
 * Integration tests for Onboarding API client and React Query integration
 * Tests end-to-end API communication, error handling, caching, and state management
 */

import { screen, waitFor, renderHook } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query';
import { renderWithProviders } from '@/test-setup';
import { apiClient, ApiClientError } from '@/lib/api-client';

// Mock fetch for API calls
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock Firebase auth
const mockFirebaseAuth = {
  getIdToken: vi.fn().mockResolvedValue('mock-firebase-token'),
  isAuthenticated: true,
  userId: 'test-user-123',
};

beforeAll(() => {
  apiClient.setFirebaseAuth(mockFirebaseAuth);
});

describe('Onboarding API Integration', () => {
  const user = userEvent.setup();
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: 0,
          cacheTime: 0,
        },
        mutations: {
          retry: false,
        },
      },
    });

    mockFetch.mockClear();
    mockFirebaseAuth.getIdToken.mockClear();
    vi.clearAllMocks();
  });

  describe('Sports API Integration', () => {
    it('fetches sports data successfully', async () => {
      const mockSportsResponse = {
        sports: [
          {
            id: '1',
            name: 'Football',
            slug: 'football',
            icon: '🏈',
            icon_url: 'https://example.com/football.png',
            description: 'American Football',
            popularity_rank: 1,
            is_active: true,
          },
          {
            id: '2',
            name: 'Basketball',
            slug: 'basketball',
            icon: '🏀',
            icon_url: 'https://example.com/basketball.png',
            description: 'Basketball',
            popularity_rank: 2,
            is_active: true,
          },
        ],
        total: 2,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockSportsResponse }),
      });

      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'sports'],
          queryFn: () => apiClient.getOnboardingSports(),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockSportsResponse.sports);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/sports'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('handles sports API error gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({
          code: 'INTERNAL_ERROR',
          message: 'Failed to retrieve sports data',
          timestamp: new Date().toISOString(),
        }),
      });

      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'sports'],
          queryFn: () => apiClient.getOnboardingSports(),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeInstanceOf(ApiClientError);
      expect(result.current.error?.message).toContain('Failed to retrieve sports data');
    });

    it('caches sports data correctly', async () => {
      const mockSportsResponse = {
        sports: [{ id: '1', name: 'Football' }],
        total: 1,
      };

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ data: mockSportsResponse }),
      });

      // First request
      const { result: result1 } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'sports'],
          queryFn: () => apiClient.getOnboardingSports(),
          staleTime: 5 * 60 * 1000, // 5 minutes
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result1.current.isSuccess).toBe(true);
      });

      // Second request with same query key
      const { result: result2 } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'sports'],
          queryFn: () => apiClient.getOnboardingSports(),
          staleTime: 5 * 60 * 1000,
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      // Should get cached data immediately
      expect(result2.current.data).toEqual(mockSportsResponse.sports);
      expect(mockFetch).toHaveBeenCalledTimes(1); // Only called once due to caching
    });
  });

  describe('Teams API Integration', () => {
    it('fetches teams data with sport IDs', async () => {
      const mockTeamsResponse = {
        teams: [
          {
            id: 'team-1',
            name: 'Patriots',
            market: 'New England',
            slug: 'patriots',
            sportId: 'sport-1',
            league: 'NFL',
            logo: 'https://example.com/patriots.png',
            colors: { primary: '#002244', secondary: '#C60C30' },
          },
        ],
        total: 1,
        sport_ids: ['sport-1'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockTeamsResponse }),
      });

      const sportIds = ['sport-1'];
      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'teams', sportIds],
          queryFn: () => apiClient.getOnboardingTeams(sportIds),
          enabled: sportIds.length > 0,
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockTeamsResponse.teams);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/teams?sport_ids=sport-1'),
        expect.any(Object)
      );
    });

    it('handles multiple sport IDs in query', async () => {
      const mockTeamsResponse = {
        teams: [
          { id: 'team-1', name: 'Patriots', sportId: 'sport-1' },
          { id: 'team-2', name: 'Lakers', sportId: 'sport-2' },
        ],
        total: 2,
        sport_ids: ['sport-1', 'sport-2'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockTeamsResponse }),
      });

      const sportIds = ['sport-1', 'sport-2'];
      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'teams', sportIds],
          queryFn: () => apiClient.getOnboardingTeams(sportIds),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('sport_ids=sport-1%2Csport-2'),
        expect.any(Object)
      );
    });

    it('disables teams query when no sports selected', () => {
      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'teams', []],
          queryFn: () => apiClient.getOnboardingTeams([]),
          enabled: false,
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      expect(result.current.isIdle).toBe(true);
      expect(mockFetch).not.toHaveBeenCalled();
    });
  });

  describe('Onboarding Status API Integration', () => {
    it('fetches onboarding status with authentication', async () => {
      const mockStatusResponse = {
        is_onboarded: false,
        current_step: 2,
        onboarding_completed_at: null,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockStatusResponse }),
      });

      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'status'],
          queryFn: () => apiClient.getOnboardingStatus(),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockStatusResponse);
      expect(mockFirebaseAuth.getIdToken).toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/status'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-firebase-token',
          }),
        })
      );
    });

    it('handles authentication failure', async () => {
      mockFirebaseAuth.getIdToken.mockRejectedValueOnce(new Error('Auth token expired'));

      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'status'],
          queryFn: () => apiClient.getOnboardingStatus(),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error?.message).toContain('Authentication failed');
    });
  });

  describe('Step Update Mutation Integration', () => {
    it('updates onboarding step successfully', async () => {
      const mockUpdateResponse = {
        is_onboarded: false,
        current_step: 3,
        onboarding_completed_at: null,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockUpdateResponse }),
      });

      const { result } = renderHook(
        () => useMutation({
          mutationFn: (data: { step: number; data?: any }) =>
            apiClient.updateOnboardingStep(data),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      const updateData = {
        step: 3,
        data: {
          sports: [{ sportId: 'sport-1', rank: 1 }],
        },
      };

      result.current.mutate(updateData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockUpdateResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/step'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updateData),
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-firebase-token',
          }),
        })
      );
    });

    it('handles step update validation errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          code: 'VALIDATION_ERROR',
          message: 'Step must be between 1 and 5',
          timestamp: new Date().toISOString(),
        }),
      });

      const { result } = renderHook(
        () => useMutation({
          mutationFn: (data: { step: number }) =>
            apiClient.updateOnboardingStep(data),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      result.current.mutate({ step: 6 });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      const error = result.current.error as ApiClientError;
      expect(error.statusCode).toBe(400);
      expect(error.message).toContain('Step must be between 1 and 5');
    });
  });

  describe('Completion Mutation Integration', () => {
    it('completes onboarding successfully', async () => {
      const mockCompletionResponse = {
        success: true,
        user_id: 'user-123',
        onboarding_completed_at: '2024-01-01T00:00:00Z',
        message: 'Onboarding completed successfully',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockCompletionResponse }),
      });

      const { result } = renderHook(
        () => useMutation({
          mutationFn: (data: any) => apiClient.completeOnboarding(data),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      const completionData = {
        sports: [{ sportId: 'sport-1', name: 'Football', rank: 1 }],
        teams: [{ teamId: 'team-1', name: 'Patriots', affinityScore: 9 }],
        preferences: {
          newsTypes: [{ type: 'injuries', enabled: true, priority: 5 }],
          notifications: { push: true, email: false },
          contentFrequency: 'standard',
        },
      };

      result.current.mutate(completionData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockCompletionResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/complete'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(completionData),
        })
      );
    });

    it('handles completion requirements validation', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          code: 'VALIDATION_ERROR',
          message: 'User must have at least one sport preference to complete onboarding',
          timestamp: new Date().toISOString(),
        }),
      });

      const { result } = renderHook(
        () => useMutation({
          mutationFn: (data: any) => apiClient.completeOnboarding(data),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      const incompleteData = {
        sports: [],
        teams: [],
        preferences: {},
      };

      result.current.mutate(incompleteData);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      const error = result.current.error as ApiClientError;
      expect(error.message).toContain('sport preference');
    });
  });

  describe('Error Handling and Retry Logic', () => {
    it('handles network timeouts', async () => {
      mockFetch.mockImplementation(
        () => new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Network timeout')), 50)
        )
      );

      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'sports'],
          queryFn: () => apiClient.getOnboardingSports(),
          retry: 1,
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      }, { timeout: 5000 });

      expect(result.current.error?.message).toContain('Network timeout');
    });

    it('handles rate limiting with retry', async () => {
      // First call fails with rate limit
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 429,
          json: async () => ({
            code: 'RATE_LIMITED',
            message: 'Too many requests',
            timestamp: new Date().toISOString(),
          }),
        })
        // Second call succeeds
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            data: { sports: [], total: 0 },
          }),
        });

      const { result } = renderHook(
        () => useQuery({
          queryKey: ['onboarding', 'sports'],
          queryFn: () => apiClient.getOnboardingSports(),
          retry: 1,
          retryDelay: 100,
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      }, { timeout: 5000 });

      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('Optimistic Updates', () => {
    it('provides optimistic updates for step changes', async () => {
      const { result } = renderHook(
        () => {
          const statusQuery = useQuery({
            queryKey: ['onboarding', 'status'],
            queryFn: () => apiClient.getOnboardingStatus(),
            initialData: { is_onboarded: false, current_step: 1 },
          });

          const updateMutation = useMutation({
            mutationFn: (data: { step: number }) =>
              apiClient.updateOnboardingStep(data),
            onMutate: async (newData) => {
              // Optimistically update the cache
              queryClient.setQueryData(['onboarding', 'status'], (old: any) => ({
                ...old,
                current_step: newData.step,
              }));
            },
          });

          return { statusQuery, updateMutation };
        },
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      // Initial state
      expect(result.current.statusQuery.data.current_step).toBe(1);

      // Mock successful update
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: { is_onboarded: false, current_step: 2 },
        }),
      });

      // Trigger optimistic update
      result.current.updateMutation.mutate({ step: 2 });

      // Should immediately see optimistic update
      expect(result.current.statusQuery.data.current_step).toBe(2);

      await waitFor(() => {
        expect(result.current.updateMutation.isSuccess).toBe(true);
      });
    });
  });

  describe('Cache Invalidation', () => {
    it('invalidates related queries after successful mutations', async () => {
      const queryClient = new QueryClient({
        defaultOptions: {
          queries: { retry: false, staleTime: 0, cacheTime: 0 },
        },
      });

      // Pre-populate cache
      queryClient.setQueryData(['onboarding', 'status'], {
        is_onboarded: false,
        current_step: 1,
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: { is_onboarded: false, current_step: 2 },
        }),
      });

      const { result } = renderHook(
        () => useMutation({
          mutationFn: (data: { step: number }) =>
            apiClient.updateOnboardingStep(data),
          onSuccess: () => {
            // Invalidate status query to refetch
            queryClient.invalidateQueries(['onboarding', 'status']);
          },
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      result.current.mutate({ step: 2 });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Should trigger refetch of status query
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/onboarding/step'),
        expect.any(Object)
      );
    });
  });

  describe('Concurrent Request Handling', () => {
    it('handles concurrent mutations gracefully', async () => {
      const { result } = renderHook(
        () => ({
          mutation1: useMutation({
            mutationFn: (data: { step: number }) =>
              apiClient.updateOnboardingStep(data),
          }),
          mutation2: useMutation({
            mutationFn: (data: { step: number }) =>
              apiClient.updateOnboardingStep(data),
          }),
        }),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );

      // Mock responses for concurrent requests
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ data: { current_step: 2 } }),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ data: { current_step: 3 } }),
        });

      // Trigger concurrent mutations
      result.current.mutation1.mutate({ step: 2 });
      result.current.mutation2.mutate({ step: 3 });

      await waitFor(() => {
        expect(result.current.mutation1.isSuccess).toBe(true);
        expect(result.current.mutation2.isSuccess).toBe(true);
      });

      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });
});