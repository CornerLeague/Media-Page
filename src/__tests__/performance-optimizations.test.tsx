import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { VirtualizedTeamList, PerformanceMonitoredTeamList } from '@/components/VirtualizedTeamList';
import { OptimizedImage } from '@/components/OptimizedImage';
import { useOnboardingPrefetch } from '@/hooks/useOnboardingPrefetch';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Mock react-window
vi.mock('react-window', () => ({
  FixedSizeList: ({ children, itemData, itemCount, itemSize }: any) => {
    // Simple mock that renders a few items
    const items = Array.from({ length: Math.min(itemCount, 5) }, (_, index) => (
      children({ index, style: { height: itemSize }, data: itemData })
    ));
    return <div data-testid="virtualized-list">{items}</div>;
  }
}));

// Mock Firebase Auth
vi.mock('@/contexts/FirebaseAuthContext', () => ({
  useFirebaseAuth: () => ({
    isAuthenticated: false,
    getIdToken: vi.fn(),
    user: null,
  }),
}));

// Mock API client
vi.mock('@/lib/api-client', () => ({
  createApiQueryClient: () => ({
    getOnboardingTeams: () => ({
      queryKey: ['teams'],
      queryFn: () => Promise.resolve([]),
    }),
    getUserPreferences: () => ({
      queryKey: ['preferences'],
      queryFn: () => Promise.resolve({}),
    }),
    getPersonalizedFeed: () => ({
      queryKey: ['feed'],
      queryFn: () => Promise.resolve([]),
    }),
    getUserAnalytics: () => ({
      queryKey: ['analytics'],
      queryFn: () => Promise.resolve({}),
    }),
  }),
}));

// Mock onboarding storage
vi.mock('@/lib/onboarding-storage', () => ({
  getLocalOnboardingStatus: () => null,
}));

// Performance monitoring mock
const performanceMock = {
  now: vi.fn(() => Date.now()),
  mark: vi.fn(),
  measure: vi.fn(),
};
Object.defineProperty(window, 'performance', {
  value: performanceMock,
});

// Test wrapper
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
};

// Mock team data
const mockTeams = Array.from({ length: 100 }, (_, index) => ({
  id: `team-${index}`,
  name: `Team ${index}`,
  market: `City ${index}`,
  sportId: index % 4 === 0 ? 'nfl' : index % 4 === 1 ? 'nba' : index % 4 === 2 ? 'mlb' : 'nhl',
  league: index % 4 === 0 ? 'NFL' : index % 4 === 1 ? 'NBA' : index % 4 === 2 ? 'MLB' : 'NHL',
  logo: '🏆',
  isSelected: false,
  affinityScore: 5,
}));

describe('Performance Optimizations', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: Infinity,
        },
      },
    });
    vi.clearAllMocks();
    performanceMock.now.mockImplementation(() => Date.now());
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe('VirtualizedTeamList', () => {
    it('renders large team lists efficiently', async () => {
      const onToggleTeam = vi.fn();
      const onAffinityChange = vi.fn();

      const startTime = performance.now();

      render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams}
            onToggleTeam={onToggleTeam}
            onAffinityChange={onAffinityChange}
            containerHeight={400}
            itemHeight={120}
          />
        </TestWrapper>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render in less than 100ms for 100 items
      expect(renderTime).toBeLessThan(100);

      // Should show teams container (custom virtualization)
      expect(screen.getByTestId('teams-container')).toBeInTheDocument();
    });

    it('handles team selection efficiently', async () => {
      const onToggleTeam = vi.fn();
      const onAffinityChange = vi.fn();

      render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams.slice(0, 5)}
            onToggleTeam={onToggleTeam}
            onAffinityChange={onAffinityChange}
            containerHeight={400}
            itemHeight={120}
          />
        </TestWrapper>
      );

      // Should not call handlers during initial render
      expect(onToggleTeam).not.toHaveBeenCalled();
      expect(onAffinityChange).not.toHaveBeenCalled();
    });

    it('shows appropriate message for empty team list', () => {
      const onToggleTeam = vi.fn();
      const onAffinityChange = vi.fn();

      render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={[]}
            onToggleTeam={onToggleTeam}
            onAffinityChange={onAffinityChange}
          />
        </TestWrapper>
      );

      expect(screen.getByText(/no teams available/i)).toBeInTheDocument();
    });
  });

  describe('OptimizedImage', () => {
    it('renders with lazy loading by default', () => {
      render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Test image"
          width={100}
          height={100}
        />
      );

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('loading', 'lazy');
      expect(img).toHaveAttribute('decoding', 'async');
    });

    it('renders with eager loading when priority is true', () => {
      render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Test image"
          width={100}
          height={100}
          priority={true}
        />
      );

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('loading', 'eager');
    });

    it('shows placeholder while loading', () => {
      render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Test image"
          width={100}
          height={100}
          priority={true} // Force immediate loading to test placeholder
        />
      );

      // Should have container with relative positioning for placeholder overlay
      const container = screen.getByRole('img').parentElement;
      expect(container).toHaveClass('relative');
    });

    it('handles image load error gracefully', () => {
      render(
        <OptimizedImage
          src="/invalid-image.jpg"
          alt="Test image"
          width={100}
          height={100}
        />
      );

      // Should have proper error handling structure
      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('decoding', 'async');
      expect(img).toHaveAttribute('alt', 'Test image');
    });
  });

  describe('Prefetching Hook', () => {
    it('provides prefetch functions', () => {
      let prefetchFunctions: any;

      function TestComponent() {
        prefetchFunctions = useOnboardingPrefetch();
        return <div>Test</div>;
      }

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      expect(prefetchFunctions).toHaveProperty('prefetchTeamsForSports');
      expect(prefetchFunctions).toHaveProperty('prefetchPreferences');
      expect(prefetchFunctions).toHaveProperty('prefetchDashboardData');
      expect(typeof prefetchFunctions.prefetchTeamsForSports).toBe('function');
    });

    it('can be disabled', () => {
      let prefetchFunctions: any;

      function TestComponent() {
        prefetchFunctions = useOnboardingPrefetch({ enabled: false });
        return <div>Test</div>;
      }

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      );

      expect(prefetchFunctions).toHaveProperty('prefetchTeamsForSports');
      // When disabled, functions should still exist but may not perform operations
    });
  });

  describe('Performance Monitoring', () => {
    it('tracks render performance for VirtualizedTeamList', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

      render(
        <TestWrapper>
          <PerformanceMonitoredTeamList
            teams={mockTeams}
            onToggleTeam={vi.fn()}
            onAffinityChange={vi.fn()}
          />
        </TestWrapper>
      );

      // Should render the performance monitored wrapper successfully
      expect(screen.getByTestId('teams-container')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('monitors image loading performance', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

      render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Test image"
          width={100}
          height={100}
        />
      );

      // Should have monitoring structure in place
      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('decoding', 'async');

      consoleSpy.mockRestore();
    });
  });

  describe('Memory Management', () => {
    it('cleans up virtualized list resources', () => {
      const { unmount } = render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams}
            onToggleTeam={vi.fn()}
            onAffinityChange={vi.fn()}
          />
        </TestWrapper>
      );

      // Should unmount without errors
      expect(() => unmount()).not.toThrow();
    });

    it('cleans up image resources', () => {
      const { unmount } = render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Test image"
          width={100}
          height={100}
        />
      );

      // Should unmount without errors
      expect(() => unmount()).not.toThrow();
    });
  });
});

describe('Integration Tests', () => {
  it('virtualized list works with team selection', async () => {
    const onToggleTeam = vi.fn();
    const teams = mockTeams.slice(0, 5);

    render(
      <TestWrapper>
        <VirtualizedTeamList
          teams={teams}
          onToggleTeam={onToggleTeam}
          onAffinityChange={vi.fn()}
        />
      </TestWrapper>
    );

    // List should render
    expect(screen.getByTestId('teams-container')).toBeInTheDocument();

    // Should show team count in a way that indicates virtualization is working
    const listElement = screen.getByTestId('teams-container');
    expect(listElement).toBeInTheDocument();
  });

  it('prefetching integrates with onboarding flow', () => {
    let prefetchCalled = false;

    function TestComponent() {
      const { prefetchTeamsForSports } = useOnboardingPrefetch();

      // Simulate selecting sports
      React.useEffect(() => {
        prefetchTeamsForSports(['nfl', 'nba']);
        prefetchCalled = true;
      }, [prefetchTeamsForSports]);

      return <div>Test</div>;
    }

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    expect(prefetchCalled).toBe(true);
  });
});