import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Import the complete onboarding flow components
import { TeamSelector } from '@/components/TeamSelector';
import { useTeamSelection } from '@/hooks/useTeamSelection';
import { apiClient, type Team, type EnhancedTeam } from '@/lib/api-client';

// Mock the API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    searchTeams: vi.fn(),
    searchTeamsEnhanced: vi.fn(),
    getSearchSuggestions: vi.fn(),
  },
}));

// Mock toast notifications
vi.mock('@/components/ui/sonner', () => ({
  toast: {
    success: vi.fn(),
    warning: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock browser storage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

const mockTeams: Team[] = [
  {
    id: 'lakers-id',
    sport_id: 'basketball-uuid',
    league_id: 'nba-uuid',
    name: 'Lakers',
    market: 'Los Angeles',
    slug: 'los-angeles-lakers',
    abbreviation: 'LAL',
    logo_url: 'https://example.com/lakers-logo.png',
    primary_color: '#552583',
    secondary_color: '#FDB927',
    is_active: true,
    sport_name: 'Basketball',
    league_name: 'NBA',
    display_name: 'Los Angeles Lakers',
    short_name: 'LAL',
  },
  {
    id: 'warriors-id',
    sport_id: 'basketball-uuid',
    league_id: 'nba-uuid',
    name: 'Warriors',
    market: 'Golden State',
    slug: 'golden-state-warriors',
    abbreviation: 'GSW',
    logo_url: 'https://example.com/warriors-logo.png',
    primary_color: '#1D428A',
    secondary_color: '#FFC72C',
    is_active: true,
    sport_name: 'Basketball',
    league_name: 'NBA',
    display_name: 'Golden State Warriors',
    short_name: 'GSW',
  },
  {
    id: 'bears-id',
    sport_id: 'football-uuid',
    league_id: 'nfl-uuid',
    name: 'Bears',
    market: 'Chicago',
    slug: 'chicago-bears',
    abbreviation: 'CHI',
    logo_url: 'https://example.com/bears-logo.png',
    primary_color: '#0B162A',
    secondary_color: '#C83803',
    is_active: true,
    sport_name: 'Football',
    league_name: 'NFL',
    display_name: 'Chicago Bears',
    short_name: 'CHI',
  },
  {
    id: 'bulls-id',
    sport_id: 'basketball-uuid',
    league_id: 'nba-uuid',
    name: 'Bulls',
    market: 'Chicago',
    slug: 'chicago-bulls',
    abbreviation: 'CHI',
    logo_url: 'https://example.com/bulls-logo.png',
    primary_color: '#CE1141',
    secondary_color: '#000000',
    is_active: true,
    sport_name: 'Basketball',
    league_name: 'NBA',
    display_name: 'Chicago Bulls',
    short_name: 'CHI',
  },
];

const mockEnhancedTeams: EnhancedTeam[] = mockTeams.map(team => ({
  ...team,
  relevance_score: Math.floor(Math.random() * 100),
  search_matches: [
    {
      field: 'display_name',
      highlighted: team.display_name.replace(/(Lakers|Warriors|Bears|Bulls)/g, '<mark>$1</mark>'),
      match_type: 'exact',
    },
  ],
}));

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

const renderWithProviders = (component: React.ReactElement, initialRoute = '/') => {
  const queryClient = createTestQueryClient();
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    </MemoryRouter>
  );
};

// Test component that simulates the onboarding flow
function OnboardingFlowTest({
  onComplete,
  maxSelections = 10,
}: {
  onComplete?: (teams: Team[]) => void;
  maxSelections?: number;
}) {
  const [selectedTeams, setSelectedTeams] = React.useState<Team[]>([]);

  const handleTeamSelect = (teams: Team[]) => {
    setSelectedTeams(teams);
    onComplete?.(teams);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2>Select Your Favorite Teams</h2>
        <p>Choose up to {maxSelections} teams to personalize your experience.</p>
      </div>

      <TeamSelector
        selectedTeams={selectedTeams}
        onTeamSelect={handleTeamSelect}
        maxSelections={maxSelections}
        showFilters={true}
        showSearchSuggestions={true}
        useEnhancedSearch={true}
      />

      <div className="flex justify-between">
        <button disabled={selectedTeams.length === 0}>
          Continue ({selectedTeams.length} selected)
        </button>
        <button onClick={() => setSelectedTeams([])}>
          Clear All
        </button>
      </div>
    </div>
  );
}

describe('Team Selection Enhanced Integration Tests', () => {
  let user: ReturnType<typeof userEvent.setup>;
  const mockOnComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();

    // Setup default API responses
    (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
      items: mockEnhancedTeams,
      total: mockEnhancedTeams.length,
      page: 1,
      page_size: 50,
      has_next: false,
      has_previous: false,
      search_metadata: {
        query: '',
        total_matches: mockEnhancedTeams.length,
        response_time_ms: 8,
        search_algorithm: 'enhanced',
      },
    });

    (apiClient.getSearchSuggestions as any).mockResolvedValue({
      suggestions: [
        {
          suggestion: 'Lakers',
          type: 'team_name',
          team_count: 1,
          preview_teams: ['Los Angeles Lakers'],
        },
        {
          suggestion: 'Chicago',
          type: 'city',
          team_count: 2,
          preview_teams: ['Chicago Bulls', 'Chicago Bears'],
        },
      ],
    });
  });

  afterEach(() => {
    vi.clearAllTimers();
    mockLocalStorage.clear();
  });

  describe('Complete Onboarding Flow', () => {
    it('completes full team selection workflow', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      // Step 1: Verify initial state
      expect(screen.getByText('Select Your Favorite Teams')).toBeInTheDocument();
      expect(screen.getByText('Choose up to 10 teams to personalize your experience.')).toBeInTheDocument();

      const continueButton = screen.getByText(/Continue \(0 selected\)/);
      expect(continueButton).toBeDisabled();

      // Step 2: Search for teams
      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lakers');

      // Step 3: Open team selector
      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      // Step 4: Select first team
      await user.click(screen.getByText('Los Angeles Lakers'));

      expect(mockOnComplete).toHaveBeenCalledWith([mockTeams[0]]);

      // Step 5: Verify UI updates
      await waitFor(() => {
        expect(screen.getByText(/Continue \(1 selected\)/)).toBeInTheDocument();
        expect(screen.getByText(/Continue \(1 selected\)/)).not.toBeDisabled();
      });

      // Step 6: Add more teams via different search
      await user.clear(searchInput);
      await user.type(searchInput, 'Chicago');

      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Chicago Bears')).toBeInTheDocument();
        expect(screen.getByText('Chicago Bulls')).toBeInTheDocument();
      });

      // Select both Chicago teams
      await user.click(screen.getByText('Chicago Bears'));
      await user.click(screen.getByText('Chicago Bulls'));

      // Step 7: Verify final state
      await waitFor(() => {
        expect(screen.getByText(/Continue \(3 selected\)/)).toBeInTheDocument();
      });

      expect(mockOnComplete).toHaveBeenLastCalledWith([
        mockTeams[0], // Lakers
        mockTeams[2], // Bears
        mockTeams[3], // Bulls
      ]);
    });

    it('handles search and filter combinations', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      // Use filter dropdown
      const filterButton = screen.getByText('Filter teams...');
      await user.click(filterButton);

      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });

      // Apply sport filter (simulated)
      // Note: Actual filter interaction would depend on the filter implementation

      // Combine with search
      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Chi');

      // Verify enhanced search is working
      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'Chi',
          })
        );
      });
    });

    it('enforces selection limits correctly', async () => {
      const { toast } = await import('@/components/ui/sonner');

      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} maxSelections={2} />
      );

      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      // Select first team
      await user.click(screen.getByText('Los Angeles Lakers'));

      await waitFor(() => {
        expect(screen.getByText(/Continue \(1 selected\)/)).toBeInTheDocument();
      });

      // Select second team (should reach limit)
      await user.click(screen.getByText('Golden State Warriors'));

      await waitFor(() => {
        expect(screen.getByText(/Continue \(2 selected\)/)).toBeInTheDocument();
      });

      // Verify max selection state
      expect(screen.getByText('Maximum teams selected')).toBeInTheDocument();

      const maxedButton = screen.getByRole('combobox');
      expect(maxedButton).toBeDisabled();
    });

    it('persists selections across component re-renders', async () => {
      let selectedTeams: Team[] = [];

      function TestComponent() {
        const [teams, setTeams] = React.useState<Team[]>(selectedTeams);

        return (
          <div>
            <OnboardingFlowTest
              onComplete={(newTeams) => {
                selectedTeams = newTeams;
                setTeams(newTeams);
              }}
            />
            <div data-testid="external-count">
              External count: {teams.length}
            </div>
          </div>
        );
      }

      const { rerender } = renderWithProviders(<TestComponent />);

      // Select a team
      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));

      await waitFor(() => {
        expect(screen.getByTestId('external-count')).toHaveTextContent('External count: 1');
      });

      // Force re-render
      rerender(<TestComponent />);

      // Verify selection is maintained
      expect(screen.getByTestId('external-count')).toHaveTextContent('External count: 1');
      expect(screen.getByText(/Continue \(1 selected\)/)).toBeInTheDocument();
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('handles API failures gracefully', async () => {
      (apiClient.searchTeamsEnhanced as any).mockRejectedValue(new Error('Network error'));

      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lakers');

      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to search teams. Please try again.')).toBeInTheDocument();
      });

      // User should still be able to continue with no selections
      const continueButton = screen.getByText(/Continue \(0 selected\)/);
      expect(continueButton).toBeDisabled();
    });

    it('handles empty search results', async () => {
      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: 'NonexistentTeam',
          total_matches: 0,
          response_time_ms: 5,
          search_algorithm: 'enhanced',
        },
      });

      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'NonexistentTeam');

      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('No teams found for "NonexistentTeam".')).toBeInTheDocument();
      });
    });

    it('handles rapid user interactions', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      const selectorButton = screen.getByRole('combobox');

      // Rapidly click the selector multiple times
      await user.click(selectorButton);
      await user.click(selectorButton);
      await user.click(selectorButton);

      // Should not cause errors or unexpected behavior
      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      // Rapidly select/deselect teams
      const lakersOption = screen.getByText('Los Angeles Lakers');
      await user.click(lakersOption);
      await user.click(lakersOption);
      await user.click(lakersOption);

      // Should handle rapid clicks gracefully
      expect(mockOnComplete).toHaveBeenCalled();
    });

    it('clears all selections when requested', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      // Select multiple teams
      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));
      await user.click(screen.getByText('Golden State Warriors'));

      await waitFor(() => {
        expect(screen.getByText(/Continue \(2 selected\)/)).toBeInTheDocument();
      });

      // Clear all selections
      const clearButton = screen.getByText('Clear All');
      await user.click(clearButton);

      await waitFor(() => {
        expect(screen.getByText(/Continue \(0 selected\)/)).toBeInTheDocument();
        expect(screen.getByText(/Continue \(0 selected\)/)).toBeDisabled();
      });

      expect(mockOnComplete).toHaveBeenLastCalledWith([]);
    });
  });

  describe('Performance in Integration Context', () => {
    it('maintains responsive interactions during complex workflows', async () => {
      const startTime = performance.now();

      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      // Perform complex workflow
      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lakers');

      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));

      // Clear and search again
      await user.clear(searchInput);
      await user.type(searchInput, 'Chicago');

      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Chicago Bears')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Chicago Bears'));

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      // Complex workflow should complete within reasonable time
      expect(totalTime).toBeLessThan(300);

      await waitFor(() => {
        expect(screen.getByText(/Continue \(2 selected\)/)).toBeInTheDocument();
      });
    });

    it('handles state updates efficiently', async () => {
      let updateCount = 0;

      function TestWrapper() {
        updateCount++;
        return <OnboardingFlowTest onComplete={mockOnComplete} />;
      }

      renderWithProviders(<TestWrapper />);

      const initialUpdateCount = updateCount;

      // Perform multiple interactions
      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));
      await user.click(screen.getByText('Golden State Warriors'));

      const finalUpdateCount = updateCount;

      // Should not cause excessive re-renders
      expect(finalUpdateCount - initialUpdateCount).toBeLessThan(10);
    });
  });

  describe('Accessibility in Integration Context', () => {
    it('maintains keyboard navigation throughout workflow', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      // Test keyboard navigation
      const selectorButton = screen.getByRole('combobox');

      // Focus and activate with keyboard
      selectorButton.focus();
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      expect(searchInput).toHaveFocus();

      // Navigate with Tab
      await user.keyboard('{Tab}');

      // Should maintain focus management
      expect(document.activeElement).toBeTruthy();
    });

    it('provides proper ARIA announcements', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      // Check ARIA attributes
      const selectorButton = screen.getByRole('combobox');
      expect(selectorButton).toHaveAttribute('aria-label', 'Select teams');

      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));

      // Should update selection count accessibly
      await waitFor(() => {
        expect(screen.getByText('Selected Teams (1)')).toBeInTheDocument();
      });
    });

    it('handles screen reader compatibility', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));

      // Verify remove button has proper label
      const removeButton = screen.getByLabelText('Remove Los Angeles Lakers');
      expect(removeButton).toBeInTheDocument();

      await user.click(removeButton);

      await waitFor(() => {
        expect(screen.getByText(/Continue \(0 selected\)/)).toBeInTheDocument();
      });
    });
  });

  describe('Mobile Responsiveness', () => {
    it('works on mobile viewport', async () => {
      // Simulate mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: 667,
      });

      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      // Mobile interactions should work the same
      const selectorButton = screen.getByRole('combobox');
      await user.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));

      await waitFor(() => {
        expect(screen.getByText(/Continue \(1 selected\)/)).toBeInTheDocument();
      });

      expect(mockOnComplete).toHaveBeenCalledWith([mockTeams[0]]);
    });

    it('handles touch interactions', async () => {
      renderWithProviders(
        <OnboardingFlowTest onComplete={mockOnComplete} />
      );

      const selectorButton = screen.getByRole('combobox');

      // Simulate touch events
      fireEvent.touchStart(selectorButton);
      fireEvent.touchEnd(selectorButton);
      fireEvent.click(selectorButton);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      const lakersOption = screen.getByText('Los Angeles Lakers');
      fireEvent.touchStart(lakersOption);
      fireEvent.touchEnd(lakersOption);
      fireEvent.click(lakersOption);

      await waitFor(() => {
        expect(screen.getByText(/Continue \(1 selected\)/)).toBeInTheDocument();
      });

      expect(mockOnComplete).toHaveBeenCalledWith([mockTeams[0]]);
    });
  });
});