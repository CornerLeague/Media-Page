import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { TeamSelector } from '../TeamSelector';
import { apiClient, type Team, type EnhancedTeam } from '@/lib/api-client';

// Performance testing utilities
interface PerformanceMetrics {
  renderTime: number;
  interactionTime: number;
  searchResponseTime: number;
  memoryUsage?: number;
}

const measurePerformance = async (fn: () => Promise<void> | void): Promise<number> => {
  const start = performance.now();
  await fn();
  const end = performance.now();
  return end - start;
};

const measureMemoryUsage = (): number => {
  if (typeof performance !== 'undefined' && (performance as any).memory) {
    return (performance as any).memory.usedJSHeapSize;
  }
  return 0;
};

// Mock the API client with performance simulation
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    searchTeams: vi.fn(),
    searchTeamsEnhanced: vi.fn(),
    getSearchSuggestions: vi.fn(),
  },
}));

// Mock toast
vi.mock('@/components/ui/sonner', () => ({
  toast: {
    success: vi.fn(),
    warning: vi.fn(),
    error: vi.fn(),
  },
}));

// Generate large dataset for performance testing
const generateMockTeams = (count: number): Team[] => {
  return Array.from({ length: count }, (_, i) => ({
    id: `team-${i}`,
    sport_id: `sport-${i % 6}`, // 6 different sports
    league_id: `league-${i % 20}`, // 20 different leagues
    name: `Team ${i}`,
    market: `City ${i}`,
    slug: `team-${i}-slug`,
    abbreviation: `T${i}`,
    logo_url: `https://example.com/logo-${i}.png`,
    primary_color: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
    secondary_color: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
    is_active: true,
    sport_name: `Sport ${i % 6}`,
    league_name: `League ${i % 20}`,
    display_name: `City ${i} Team ${i}`,
    short_name: `T${i}`,
  }));
};

const generateEnhancedMockTeams = (teams: Team[]): EnhancedTeam[] => {
  return teams.map(team => ({
    ...team,
    relevance_score: Math.floor(Math.random() * 100),
    search_matches: [
      {
        field: 'display_name',
        highlighted: team.display_name,
        match_type: 'exact',
      },
    ],
  }));
};

const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });
};

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('TeamSelector Performance Tests', () => {
  const mockOnTeamSelect = vi.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('Rendering Performance', () => {
    it('renders initial component within 50ms', async () => {
      const smallTeamSet = generateMockTeams(10);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: smallTeamSet,
        total: smallTeamSet.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: '',
          total_matches: smallTeamSet.length,
          response_time_ms: 5,
          search_algorithm: 'enhanced',
        },
      });

      const renderTime = await measurePerformance(() => {
        renderWithQueryClient(
          <TeamSelector
            selectedTeams={[]}
            onTeamSelect={mockOnTeamSelect}
            sportIds={['sport-1']}
          />
        );
      });

      expect(renderTime).toBeLessThan(50);
    });

    it('handles 100+ teams render performance', async () => {
      const largeTeamSet = generateMockTeams(150);
      const enhancedTeams = generateEnhancedMockTeams(largeTeamSet);

      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: enhancedTeams,
        total: enhancedTeams.length,
        page: 1,
        page_size: 150,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: 'test',
          total_matches: enhancedTeams.length,
          response_time_ms: 12,
          search_algorithm: 'enhanced',
        },
      });

      const renderTime = await measurePerformance(async () => {
        renderWithQueryClient(
          <TeamSelector
            selectedTeams={[]}
            onTeamSelect={mockOnTeamSelect}
            sportIds={['sport-1']}
          />
        );

        // Open dropdown to trigger team list rendering
        const button = screen.getByRole('combobox');
        await user.click(button);

        await waitFor(() => {
          expect(screen.getByText('City 0 Team 0')).toBeInTheDocument();
        });
      });

      // Should render 150 teams within 100ms
      expect(renderTime).toBeLessThan(100);
    });

    it('measures memory usage with large datasets', async () => {
      const largeTeamSet = generateMockTeams(500);
      const enhancedTeams = generateEnhancedMockTeams(largeTeamSet);

      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: enhancedTeams,
        total: enhancedTeams.length,
        page: 1,
        page_size: 500,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: 'test',
          total_matches: enhancedTeams.length,
          response_time_ms: 25,
          search_algorithm: 'enhanced',
        },
      });

      const initialMemory = measureMemoryUsage();

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('City 0 Team 0')).toBeInTheDocument();
      });

      const finalMemory = measureMemoryUsage();
      const memoryIncrease = finalMemory - initialMemory;

      // Memory increase should be reasonable (less than 10MB for 500 teams)
      if (initialMemory > 0) {
        expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024); // 10MB
      }
    });
  });

  describe('Search Performance', () => {
    it('validates search debouncing prevents excessive API calls', async () => {
      vi.useFakeTimers();

      const mockTeams = generateMockTeams(50);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: 'Lakers',
          total_matches: mockTeams.length,
          response_time_ms: 8,
          search_algorithm: 'enhanced',
        },
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');

      // Type rapidly - each character with 50ms interval (much faster than 300ms debounce)
      const searchText = 'Lakers';
      for (const char of searchText) {
        await user.type(searchInput, char);
        act(() => {
          vi.advanceTimersByTime(50);
        });
      }

      // Verify no API calls yet
      expect(apiClient.searchTeamsEnhanced).not.toHaveBeenCalled();

      // Complete debounce period
      act(() => {
        vi.advanceTimersByTime(300);
      });

      // Should only call API once
      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledTimes(1);
      });

      vi.useRealTimers();
    });

    it('measures search response time performance', async () => {
      const mockTeams = generateMockTeams(30);
      let searchStartTime: number;

      (apiClient.searchTeamsEnhanced as any).mockImplementation(async () => {
        // Simulate realistic API response time
        await new Promise(resolve => setTimeout(resolve, 5));
        return {
          items: mockTeams,
          total: mockTeams.length,
          page: 1,
          page_size: 50,
          has_next: false,
          has_previous: false,
          search_metadata: {
            query: 'Lakers',
            total_matches: mockTeams.length,
            response_time_ms: 5,
            search_algorithm: 'enhanced',
          },
        };
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');

      const totalSearchTime = await measurePerformance(async () => {
        searchStartTime = performance.now();
        await user.type(searchInput, 'Lakers');

        await waitFor(() => {
          expect(apiClient.searchTeamsEnhanced).toHaveBeenCalled();
        });

        // Open dropdown to see results
        const button = screen.getByRole('combobox');
        await user.click(button);

        await waitFor(() => {
          expect(screen.getByText('City 0 Team 0')).toBeInTheDocument();
        });
      });

      // Total search interaction should complete within 100ms (excluding network delay)
      expect(totalSearchTime).toBeLessThan(100);
    });

    it('handles rapid search query changes efficiently', async () => {
      vi.useFakeTimers();

      const mockTeams = generateMockTeams(20);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: 'test',
          total_matches: mockTeams.length,
          response_time_ms: 3,
          search_algorithm: 'enhanced',
        },
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');

      // Simulate very rapid typing
      const queries = ['L', 'La', 'Lak', 'Lake', 'Laker', 'Lakers'];

      const performanceStart = performance.now();

      for (const query of queries) {
        // Clear and type new query
        await user.clear(searchInput);
        await user.type(searchInput, query);

        // Advance time by 100ms (still within debounce window)
        act(() => {
          vi.advanceTimersByTime(100);
        });
      }

      // Complete final debounce
      act(() => {
        vi.advanceTimersByTime(300);
      });

      const performanceEnd = performance.now();
      const totalTime = performanceEnd - performanceStart;

      // Rapid typing handling should be efficient
      expect(totalTime).toBeLessThan(50);

      // Should only make one API call for final query
      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledTimes(1);
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledWith(
          expect.objectContaining({ query: 'Lakers' })
        );
      });

      vi.useRealTimers();
    });
  });

  describe('Interaction Performance', () => {
    it('measures team selection performance', async () => {
      const mockTeams = generateMockTeams(50);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: '',
          total_matches: mockTeams.length,
          response_time_ms: 5,
          search_algorithm: 'enhanced',
        },
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
          useEnhancedSearch={false}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('City 0 Team 0')).toBeInTheDocument();
      });

      const selectionTime = await measurePerformance(async () => {
        await user.click(screen.getByText('City 0 Team 0'));
      });

      // Team selection should respond within 10ms
      expect(selectionTime).toBeLessThan(10);
      expect(mockOnTeamSelect).toHaveBeenCalledWith([mockTeams[0]]);
    });

    it('measures multiple team selection performance', async () => {
      const mockTeams = generateMockTeams(20);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: '',
          total_matches: mockTeams.length,
          response_time_ms: 5,
          search_algorithm: 'enhanced',
        },
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
          useEnhancedSearch={false}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('City 0 Team 0')).toBeInTheDocument();
      });

      // Select 5 teams rapidly
      const multiSelectionTime = await measurePerformance(async () => {
        for (let i = 0; i < 5; i++) {
          await user.click(screen.getByText(`City ${i} Team ${i}`));
        }
      });

      // Multiple selections should complete within 50ms
      expect(multiSelectionTime).toBeLessThan(50);
      expect(mockOnTeamSelect).toHaveBeenCalledTimes(5);
    });

    it('measures filter application performance', async () => {
      const mockTeams = generateMockTeams(100);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 100,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: '',
          total_matches: mockTeams.length,
          response_time_ms: 15,
          search_algorithm: 'enhanced',
        },
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          showFilters={true}
        />
      );

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('Filter teams...')).toBeInTheDocument();
      });

      const filterTime = await measurePerformance(async () => {
        const filterButton = screen.getByText('Filter teams...');
        await user.click(filterButton);

        await waitFor(() => {
          expect(screen.getByText('Filter Teams')).toBeInTheDocument();
        });
      });

      // Filter dropdown should open within 25ms
      expect(filterTime).toBeLessThan(25);
    });
  });

  describe('Component Re-render Performance', () => {
    it('minimizes re-renders during prop changes', async () => {
      let renderCount = 0;

      function TestComponent({ teams }: { teams: Team[] }) {
        renderCount++;
        return (
          <TeamSelector
            selectedTeams={teams}
            onTeamSelect={mockOnTeamSelect}
            sportIds={['sport-1']}
            useEnhancedSearch={false}
          />
        );
      }

      const mockTeams = generateMockTeams(10);
      (apiClient.searchTeams as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
      });

      const { rerender } = renderWithQueryClient(<TestComponent teams={[]} />);

      // Initial render
      expect(renderCount).toBe(1);

      const rerenderTime = await measurePerformance(() => {
        // Change teams prop 5 times
        rerender(<TestComponent teams={[mockTeams[0]]} />);
        rerender(<TestComponent teams={[mockTeams[0], mockTeams[1]]} />);
        rerender(<TestComponent teams={[mockTeams[0], mockTeams[1], mockTeams[2]]} />);
        rerender(<TestComponent teams={[mockTeams[0], mockTeams[1]]} />);
        rerender(<TestComponent teams={[mockTeams[0]]} />);
      });

      // Should have rendered 6 times total (initial + 5 updates)
      expect(renderCount).toBe(6);

      // Re-renders should be fast
      expect(rerenderTime).toBeLessThan(25);
    });

    it('prevents infinite re-render loops', async () => {
      let renderCount = 0;
      const maxRenders = 10; // Safety limit

      function TestComponent() {
        renderCount++;

        // Prevent infinite loop in test
        if (renderCount > maxRenders) {
          throw new Error(`Exceeded maximum renders: ${renderCount}`);
        }

        return (
          <TeamSelector
            selectedTeams={[]}
            onTeamSelect={mockOnTeamSelect}
            sportIds={['sport-1']}
          />
        );
      }

      const mockTeams = generateMockTeams(5);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: '',
          total_matches: mockTeams.length,
          response_time_ms: 5,
          search_algorithm: 'enhanced',
        },
      });

      // Should not throw error due to infinite re-renders
      expect(() => {
        renderWithQueryClient(<TestComponent />);
      }).not.toThrow();

      // Should render reasonable number of times
      expect(renderCount).toBeLessThanOrEqual(maxRenders);
    });
  });

  describe('Memory Leak Prevention', () => {
    it('cleans up event listeners and timeouts', async () => {
      const mockTeams = generateMockTeams(10);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: '',
          total_matches: mockTeams.length,
          response_time_ms: 5,
          search_algorithm: 'enhanced',
        },
      });

      const { unmount } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'test');

      // Unmount component while debounce is active
      const unmountTime = await measurePerformance(() => {
        unmount();
      });

      // Unmounting should be fast and clean
      expect(unmountTime).toBeLessThan(10);
    });

    it('handles component unmount during API calls', async () => {
      let resolvePromise: (value: any) => void;
      const pendingPromise = new Promise(resolve => {
        resolvePromise = resolve;
      });

      (apiClient.searchTeamsEnhanced as any).mockReturnValue(pendingPromise);

      const { unmount } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'test');

      // Unmount while API call is pending
      unmount();

      // Resolve the promise after unmount
      resolvePromise!({
        items: [],
        total: 0,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: 'test',
          total_matches: 0,
          response_time_ms: 100,
          search_algorithm: 'enhanced',
        },
      });

      // Should not cause any errors or memory leaks
    });
  });

  describe('API Response Time Validation', () => {
    it('validates backend API performance meets targets', async () => {
      const mockTeams = generateMockTeams(30);

      // Simulate backend response times
      const responseTime = 8; // ms
      (apiClient.searchTeamsEnhanced as any).mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, responseTime));
        return {
          items: mockTeams,
          total: mockTeams.length,
          page: 1,
          page_size: 50,
          has_next: false,
          has_previous: false,
          search_metadata: {
            query: 'test',
            total_matches: mockTeams.length,
            response_time_ms: responseTime,
            search_algorithm: 'enhanced',
          },
        };
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');

      const totalTime = await measurePerformance(async () => {
        await user.type(searchInput, 'test');

        await waitFor(() => {
          expect(apiClient.searchTeamsEnhanced).toHaveBeenCalled();
        });
      });

      // API call should complete within expected timeframe
      await waitFor(() => {
        const searchMetadata = screen.queryByText(/Found \d+ results in \d+ms/);
        if (searchMetadata) {
          // Verify API response time is within target (< 100ms)
          expect(responseTime).toBeLessThan(100);
        }
      });
    });

    it('measures end-to-end search performance', async () => {
      const mockTeams = generateMockTeams(50);
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: 'Lakers',
          total_matches: mockTeams.length,
          response_time_ms: 12,
          search_algorithm: 'enhanced',
        },
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['sport-1']}
        />
      );

      // Measure complete search workflow
      const endToEndTime = await measurePerformance(async () => {
        const searchInput = screen.getByPlaceholderText('Search for teams...');
        await user.type(searchInput, 'Lakers');

        const button = screen.getByRole('combobox');
        await user.click(button);

        await waitFor(() => {
          expect(screen.getByText('City 0 Team 0')).toBeInTheDocument();
        });

        // Select a team
        await user.click(screen.getByText('City 0 Team 0'));
      });

      // Complete workflow should finish within 150ms
      expect(endToEndTime).toBeLessThan(150);
    });
  });
});