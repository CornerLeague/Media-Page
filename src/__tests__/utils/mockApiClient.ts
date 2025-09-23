/**
 * Mock API Client Utilities
 *
 * Creates mock implementations of the API client for testing
 * error scenarios and recovery mechanisms.
 */

import { vi } from 'vitest';

export function createMockApiClient() {
  const mockClient = {
    updateOnboardingStep: vi.fn(),
    getOnboardingSports: vi.fn(),
    getOnboardingTeams: vi.fn(),
  };

  const mockQueryConfigs = {
    getOnboardingSports: vi.fn(() => ({
      queryKey: ['onboarding', 'sports'],
      queryFn: () => Promise.resolve([
        { id: 'nfl', name: 'NFL', icon: '🏈', hasTeams: true, isPopular: true },
        { id: 'nba', name: 'NBA', icon: '🏀', hasTeams: true, isPopular: true },
        { id: 'mlb', name: 'MLB', icon: '⚾', hasTeams: true, isPopular: true },
        { id: 'nhl', name: 'NHL', icon: '🏒', hasTeams: true, isPopular: true },
        { id: 'soccer', name: 'Soccer', icon: '⚽', hasTeams: true, isPopular: false },
        { id: 'tennis', name: 'Tennis', icon: '🎾', hasTeams: false, isPopular: false },
      ]),
    })),

    getOnboardingTeams: vi.fn((sportIds: string[]) => ({
      queryKey: ['onboarding', 'teams', sportIds],
      queryFn: () => {
        const teams = [];

        if (sportIds.includes('nfl')) {
          teams.push(
            { id: 'chiefs', name: 'Kansas City Chiefs', market: 'Kansas City', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'cowboys', name: 'Dallas Cowboys', market: 'Dallas', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'patriots', name: 'New England Patriots', market: 'New England', sportId: 'nfl', league: 'NFL', logo: '🏈' },
          );
        }

        if (sportIds.includes('nba')) {
          teams.push(
            { id: 'lakers', name: 'Los Angeles Lakers', market: 'Los Angeles', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'warriors', name: 'Golden State Warriors', market: 'Golden State', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'celtics', name: 'Boston Celtics', market: 'Boston', sportId: 'nba', league: 'NBA', logo: '🏀' },
          );
        }

        if (sportIds.includes('mlb')) {
          teams.push(
            { id: 'yankees', name: 'New York Yankees', market: 'New York', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'dodgers', name: 'Los Angeles Dodgers', market: 'Los Angeles', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'red-sox', name: 'Boston Red Sox', market: 'Boston', sportId: 'mlb', league: 'MLB', logo: '⚾' },
          );
        }

        return Promise.resolve(teams);
      },
    })),
  };

  return {
    client: mockClient,
    queryConfigs: mockQueryConfigs,
  };
}

export function createNetworkErrorApiClient() {
  return {
    client: {
      updateOnboardingStep: vi.fn().mockRejectedValue(new Error('Network Error')),
      getOnboardingSports: vi.fn().mockRejectedValue(new Error('Network Error')),
      getOnboardingTeams: vi.fn().mockRejectedValue(new Error('Network Error')),
    },
    queryConfigs: {
      getOnboardingSports: vi.fn(() => ({
        queryKey: ['onboarding', 'sports'],
        queryFn: () => Promise.reject(new Error('Network Error')),
      })),
      getOnboardingTeams: vi.fn(() => ({
        queryKey: ['onboarding', 'teams'],
        queryFn: () => Promise.reject(new Error('Network Error')),
      })),
    },
  };
}

export function createTimeoutErrorApiClient() {
  return {
    client: {
      updateOnboardingStep: vi.fn().mockRejectedValue(new Error('Request timeout')),
      getOnboardingSports: vi.fn().mockRejectedValue(new Error('Request timeout')),
      getOnboardingTeams: vi.fn().mockRejectedValue(new Error('Request timeout')),
    },
    queryConfigs: {
      getOnboardingSports: vi.fn(() => ({
        queryKey: ['onboarding', 'sports'],
        queryFn: () => Promise.reject(new Error('Request timeout')),
      })),
      getOnboardingTeams: vi.fn(() => ({
        queryKey: ['onboarding', 'teams'],
        queryFn: () => Promise.reject(new Error('Request timeout')),
      })),
    },
  };
}

export function createServerErrorApiClient() {
  const serverError = new Error('Internal Server Error');
  (serverError as any).status = 500;

  return {
    client: {
      updateOnboardingStep: vi.fn().mockRejectedValue(serverError),
      getOnboardingSports: vi.fn().mockRejectedValue(serverError),
      getOnboardingTeams: vi.fn().mockRejectedValue(serverError),
    },
    queryConfigs: {
      getOnboardingSports: vi.fn(() => ({
        queryKey: ['onboarding', 'sports'],
        queryFn: () => Promise.reject(serverError),
      })),
      getOnboardingTeams: vi.fn(() => ({
        queryKey: ['onboarding', 'teams'],
        queryFn: () => Promise.reject(serverError),
      })),
    },
  };
}

export function createAuthErrorApiClient() {
  const authError = new Error('Unauthorized');
  (authError as any).status = 401;

  return {
    client: {
      updateOnboardingStep: vi.fn().mockRejectedValue(authError),
      getOnboardingSports: vi.fn().mockRejectedValue(authError),
      getOnboardingTeams: vi.fn().mockRejectedValue(authError),
    },
    queryConfigs: {
      getOnboardingSports: vi.fn(() => ({
        queryKey: ['onboarding', 'sports'],
        queryFn: () => Promise.reject(authError),
      })),
      getOnboardingTeams: vi.fn(() => ({
        queryKey: ['onboarding', 'teams'],
        queryFn: () => Promise.reject(authError),
      })),
    },
  };
}

export function createRateLimitErrorApiClient() {
  const rateLimitError = new Error('Too Many Requests');
  (rateLimitError as any).status = 429;
  (rateLimitError as any).headers = { 'Retry-After': '60' };

  return {
    client: {
      updateOnboardingStep: vi.fn().mockRejectedValue(rateLimitError),
      getOnboardingSports: vi.fn().mockRejectedValue(rateLimitError),
      getOnboardingTeams: vi.fn().mockRejectedValue(rateLimitError),
    },
    queryConfigs: {
      getOnboardingSports: vi.fn(() => ({
        queryKey: ['onboarding', 'sports'],
        queryFn: () => Promise.reject(rateLimitError),
      })),
      getOnboardingTeams: vi.fn(() => ({
        queryKey: ['onboarding', 'teams'],
        queryFn: () => Promise.reject(rateLimitError),
      })),
    },
  };
}

export default {
  createMockApiClient,
  createNetworkErrorApiClient,
  createTimeoutErrorApiClient,
  createServerErrorApiClient,
  createAuthErrorApiClient,
  createRateLimitErrorApiClient,
};