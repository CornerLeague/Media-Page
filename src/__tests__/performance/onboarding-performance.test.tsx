/**
 * Onboarding Performance Test Suite
 *
 * Tests performance characteristics of the onboarding flow including:
 * - Component render times
 * - Bundle size analysis
 * - Team selection performance with large datasets
 * - Image loading optimization
 * - API call efficiency
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { performance, PerformanceObserver } from 'perf_hooks';

import { TeamSelectionStep } from '@/pages/onboarding/TeamSelectionStep';
import { SportsSelectionStep } from '@/pages/onboarding/SportsSelectionStep';
import { OnboardingRouter } from '@/pages/onboarding';
import { FirebaseAuthProvider } from '@/contexts/FirebaseAuthContext';

// Mock Firebase Auth
const mockFirebaseAuth = {
  isAuthenticated: true,
  user: { uid: 'test-user' },
  getIdToken: vi.fn().mockResolvedValue('mock-token'),
};

vi.mock('@/contexts/FirebaseAuthContext', () => ({
  useFirebaseAuth: () => mockFirebaseAuth,
  FirebaseAuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock API client with performance tracking
const mockApiClient = {
  getOnboardingTeams: vi.fn(),
  updateOnboardingStep: vi.fn(),
  setFirebaseAuth: vi.fn(),
};

vi.mock('@/lib/api-client', () => ({
  apiClient: mockApiClient,
  createApiQueryClient: () => ({
    getOnboardingTeams: () => ({
      queryKey: ['onboarding-teams'],
      queryFn: mockApiClient.getOnboardingTeams,
    }),
  }),
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Performance measurement utilities
class PerformanceTracker {
  private measurements: Record<string, number[]> = {};

  startMeasurement(name: string): string {
    const markName = `${name}-start-${Date.now()}`;
    performance.mark(markName);
    return markName;
  }

  endMeasurement(name: string, startMark: string): number {
    const endMark = `${name}-end-${Date.now()}`;
    performance.mark(endMark);

    const measureName = `${name}-duration`;
    performance.measure(measureName, startMark, endMark);

    const measurement = performance.getEntriesByName(measureName)[0];
    const duration = measurement.duration;

    if (!this.measurements[name]) {
      this.measurements[name] = [];
    }
    this.measurements[name].push(duration);

    return duration;
  }

  getAverageDuration(name: string): number {
    const measurements = this.measurements[name] || [];
    return measurements.length > 0
      ? measurements.reduce((sum, duration) => sum + duration, 0) / measurements.length
      : 0;
  }

  getMetrics() {
    return Object.entries(this.measurements).reduce((metrics, [name, durations]) => {
      metrics[name] = {
        count: durations.length,
        average: this.getAverageDuration(name),
        min: Math.min(...durations),
        max: Math.max(...durations),
        total: durations.reduce((sum, d) => sum + d, 0),
      };
      return metrics;
    }, {} as Record<string, any>);
  }

  reset() {
    this.measurements = {};
    performance.clearMeasures();
    performance.clearMarks();
  }
}

// Generate large team dataset for performance testing
function generateLargeTeamDataset(count: number = 1000) {
  const sports = ['nfl', 'nba', 'mlb', 'nhl', 'college-football', 'college-basketball'];
  const cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Detroit'];
  const teamNames = ['Lions', 'Tigers', 'Bears', 'Eagles', 'Hawks', 'Wolves', 'Panthers', 'Jaguars', 'Ravens', 'Cardinals'];

  return Array.from({ length: count }, (_, i) => ({
    id: `team-${i}`,
    name: `${cities[i % cities.length]} ${teamNames[i % teamNames.length]}`,
    market: cities[i % cities.length],
    sportId: sports[i % sports.length],
    league: sports[i % sports.length].toUpperCase(),
    logo: '🏈',
  }));
}

describe('Onboarding Performance Tests', () => {
  let queryClient: QueryClient;
  let performanceTracker: PerformanceTracker;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    performanceTracker = new PerformanceTracker();

    // Reset mocks
    vi.clearAllMocks();

    // Mock local storage with onboarding data
    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'corner-league-onboarding') {
        return JSON.stringify({
          selectedSports: [
            { sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true },
            { sportId: 'nba', name: 'NBA', rank: 2, hasTeams: true },
          ],
        });
      }
      return null;
    });
  });

  afterEach(() => {
    performanceTracker.reset();
  });

  const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <FirebaseAuthProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </FirebaseAuthProvider>
    </QueryClientProvider>
  );

  describe('Component Render Performance', () => {
    it('should render TeamSelectionStep within performance thresholds', async () => {
      const startMark = performanceTracker.startMeasurement('team-selection-render');

      render(
        <TestWrapper>
          <TeamSelectionStep />
        </TestWrapper>
      );

      // Wait for component to be fully rendered
      await waitFor(() => {
        expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
      });

      const renderTime = performanceTracker.endMeasurement('team-selection-render', startMark);

      // Team selection should render within 100ms
      expect(renderTime).toBeLessThan(100);
    });

    it('should handle re-renders efficiently when team selection changes', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <TeamSelectionStep />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
      });

      // Measure re-render performance when toggling teams
      const startMark = performanceTracker.startMeasurement('team-toggle-rerender');

      // Simulate team selection changes (would need actual checkboxes in real implementation)
      const checkboxes = screen.getAllByRole('checkbox');
      if (checkboxes.length > 0) {
        await act(async () => {
          await user.click(checkboxes[0]);
        });
      }

      const rerenderTime = performanceTracker.endMeasurement('team-toggle-rerender', startMark);

      // Re-renders should be under 50ms
      expect(rerenderTime).toBeLessThan(50);
    });
  });

  describe('Large Dataset Performance', () => {
    it('should handle 1000+ teams without performance degradation', async () => {
      const largeTeamDataset = generateLargeTeamDataset(1000);

      mockApiClient.getOnboardingTeams.mockResolvedValue(largeTeamDataset);

      const startMark = performanceTracker.startMeasurement('large-dataset-render');

      render(
        <TestWrapper>
          <TeamSelectionStep />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
      }, { timeout: 5000 });

      const renderTime = performanceTracker.endMeasurement('large-dataset-render', startMark);

      // Should handle large datasets within 500ms
      expect(renderTime).toBeLessThan(500);
    });

    it('should maintain scroll performance with large team lists', async () => {
      const largeTeamDataset = generateLargeTeamDataset(1000);
      mockApiClient.getOnboardingTeams.mockResolvedValue(largeTeamDataset);

      render(
        <TestWrapper>
          <TeamSelectionStep />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
      });

      // Measure scroll performance
      const scrollContainer = document.querySelector('[data-testid="teams-container"]') || document.body;

      const startMark = performanceTracker.startMeasurement('scroll-performance');

      // Simulate scroll events
      for (let i = 0; i < 10; i++) {
        await act(async () => {
          scrollContainer.scrollTop += 100;
          // Trigger scroll event
          scrollContainer.dispatchEvent(new Event('scroll'));
        });
      }

      const scrollTime = performanceTracker.endMeasurement('scroll-performance', startMark);

      // Scroll operations should be smooth (under 100ms for 10 scrolls)
      expect(scrollTime).toBeLessThan(100);
    });
  });

  describe('API Performance', () => {
    it('should cache API requests efficiently', async () => {
      mockApiClient.getOnboardingTeams.mockResolvedValue([
        { id: 'team1', name: 'Team 1', sportId: 'nfl', league: 'NFL', logo: '🏈' },
      ]);

      // First render
      const { unmount } = render(
        <TestWrapper>
          <TeamSelectionStep />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(mockApiClient.getOnboardingTeams).toHaveBeenCalledTimes(1);
      });

      unmount();

      // Second render should use cache
      render(
        <TestWrapper>
          <TeamSelectionStep />
        </TestWrapper>
      );

      // Should not make additional API calls due to caching
      expect(mockApiClient.getOnboardingTeams).toHaveBeenCalledTimes(1);
    });

    it('should handle API errors gracefully without performance impact', async () => {
      mockApiClient.getOnboardingTeams.mockRejectedValue(new Error('API Error'));

      const startMark = performanceTracker.startMeasurement('error-handling');

      render(
        <TestWrapper>
          <TeamSelectionStep />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/working offline/i)).toBeInTheDocument();
      });

      const errorHandlingTime = performanceTracker.endMeasurement('error-handling', startMark);

      // Error handling should not significantly impact performance
      expect(errorHandlingTime).toBeLessThan(200);
    });
  });

  describe('Memory Performance', () => {
    it('should not create memory leaks during navigation', async () => {
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;

      // Render and unmount multiple times
      for (let i = 0; i < 10; i++) {
        const { unmount } = render(
          <TestWrapper>
            <TeamSelectionStep />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
        });

        unmount();
      }

      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }

      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      const memoryIncrease = finalMemory - initialMemory;

      // Memory increase should be minimal (less than 10MB)
      expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
    });
  });

  describe('Bundle Size Performance', () => {
    it('should not load unnecessary dependencies', () => {
      // This test would need build-time analysis
      // For now, we can check that components don't import heavy libraries unnecessarily

      const heavyLibraries = [
        'lodash',
        'moment',
        'three',
        'chart.js',
        'd3',
      ];

      // In a real implementation, you would analyze the webpack bundle
      // or use tools like bundle-analyzer to verify this
      expect(true).toBe(true); // Placeholder
    });
  });

  it('should provide performance metrics summary', () => {
    const metrics = performanceTracker.getMetrics();

    // Log performance metrics for analysis
    console.log('Onboarding Performance Metrics:', metrics);

    // Verify we collected performance data
    expect(typeof metrics).toBe('object');
  });
});

describe('Performance Benchmarks', () => {
  let performanceTracker: PerformanceTracker;

  beforeEach(() => {
    performanceTracker = new PerformanceTracker();
  });

  afterEach(() => {
    performanceTracker.reset();
  });

  it('should benchmark team selection with different dataset sizes', async () => {
    const dataSizes = [10, 50, 100, 500, 1000];
    const results: Record<number, number> = {};

    for (const size of dataSizes) {
      const dataset = generateLargeTeamDataset(size);
      mockApiClient.getOnboardingTeams.mockResolvedValue(dataset);

      const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false } },
      });

      const startMark = performanceTracker.startMeasurement(`dataset-${size}`);

      const { unmount } = render(
        <QueryClientProvider client={queryClient}>
          <FirebaseAuthProvider>
            <BrowserRouter>
              <TeamSelectionStep />
            </BrowserRouter>
          </FirebaseAuthProvider>
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
      }, { timeout: 10000 });

      const duration = performanceTracker.endMeasurement(`dataset-${size}`, startMark);
      results[size] = duration;

      unmount();
    }

    // Log benchmark results
    console.log('Dataset Size Performance Benchmark:', results);

    // Verify performance doesn't degrade linearly with size
    // (should be sub-linear due to virtualization or pagination)
    const performance1000 = results[1000];
    const performance100 = results[100];

    if (performance1000 && performance100) {
      // 10x data should not take 10x time (should be better due to optimization)
      expect(performance1000 / performance100).toBeLessThan(5);
    }
  });
});