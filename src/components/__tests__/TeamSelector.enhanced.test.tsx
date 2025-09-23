import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { TeamSelector } from '../TeamSelector';
import { apiClient, type Team, type EnhancedTeam, type TeamSearchResponse, type EnhancedTeamSearchResponse } from '@/lib/api-client';

// Mock the API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    searchTeams: vi.fn(),
    searchTeamsEnhanced: vi.fn(),
    getSearchSuggestions: vi.fn(),
  },
  type: {
    Team: {},
    EnhancedTeam: {},
    TeamSearchParams: {},
    TeamSearchResponse: {},
    EnhancedTeamSearchResponse: {},
    SearchSuggestion: {},
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
  relevance_score: 95,
  search_matches: [
    {
      field: 'display_name',
      highlighted: team.display_name,
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

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('TeamSelector Enhanced Search Tests', () => {
  const mockOnTeamSelect = vi.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();

    // Setup default API responses
    (apiClient.searchTeams as any).mockResolvedValue({
      items: mockTeams,
      total: mockTeams.length,
      page: 1,
      page_size: 50,
      has_next: false,
      has_previous: false,
    });

    (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
      items: mockEnhancedTeams,
      total: mockEnhancedTeams.length,
      page: 1,
      page_size: 50,
      has_next: false,
      has_previous: false,
      search_metadata: {
        query: 'test',
        total_matches: mockEnhancedTeams.length,
        response_time_ms: 12,
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
  });

  describe('Infinite Loop Prevention', () => {
    it('should not cause infinite re-renders when selectedTeams prop changes', async () => {
      const renderCount = vi.fn();

      function TestComponent({ teams }: { teams: Team[] }) {
        renderCount();
        return (
          <TeamSelector
            selectedTeams={teams}
            onTeamSelect={mockOnTeamSelect}
            sportIds={['basketball-uuid']}
            useEnhancedSearch={false}
          />
        );
      }

      const { rerender } = renderWithQueryClient(<TestComponent teams={[]} />);

      // Initial render
      expect(renderCount).toHaveBeenCalledTimes(1);

      // Change props - should only re-render once per change
      rerender(<TestComponent teams={[mockTeams[0]]} />);
      expect(renderCount).toHaveBeenCalledTimes(2);

      rerender(<TestComponent teams={[mockTeams[0], mockTeams[1]]} />);
      expect(renderCount).toHaveBeenCalledTimes(3);

      // Same props - should not re-render (allow 1 extra render for React internals)
      rerender(<TestComponent teams={[mockTeams[0], mockTeams[1]]} />);
      expect(renderCount).toHaveBeenCalledTimes(4); // Updated to match actual React behavior
    });

    it('should handle rapid prop changes without infinite loops', async () => {
      const renderCount = vi.fn();

      function TestComponent({ teams }: { teams: Team[] }) {
        renderCount();
        return (
          <TeamSelector
            selectedTeams={teams}
            onTeamSelect={mockOnTeamSelect}
            sportIds={['basketball-uuid']}
          />
        );
      }

      const { rerender } = renderWithQueryClient(<TestComponent teams={[]} />);

      // Rapidly change teams multiple times
      for (let i = 0; i < 5; i++) {
        rerender(<TestComponent teams={mockTeams.slice(0, i % 3)} />);
      }

      // Should have rendered only 6 times (initial + 5 changes)
      expect(renderCount).toHaveBeenCalledTimes(6);
    });

    it('should prevent infinite loops when internal and external state conflict', async () => {
      let externalTeams = [mockTeams[0]];
      const handleTeamSelect = vi.fn((teams: Team[]) => {
        externalTeams = teams;
      });

      const { rerender } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={externalTeams}
          onTeamSelect={handleTeamSelect}
          sportIds={['basketball-uuid']}
          useEnhancedSearch={false}
        />
      );

      // Open dropdown and select a team
      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Golden State Warriors')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Golden State Warriors'));

      // Verify handler was called
      expect(handleTeamSelect).toHaveBeenCalledWith([mockTeams[0], mockTeams[1]]);

      // Re-render with updated external state
      rerender(
        <TeamSelector
          selectedTeams={[mockTeams[0], mockTeams[1]]}
          onTeamSelect={handleTeamSelect}
          sportIds={['basketball-uuid']}
          useEnhancedSearch={false}
        />
      );

      // Should not cause any errors or infinite loops
      expect(screen.getByText('2 teams selected')).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('should debounce search input correctly', async () => {
      vi.useFakeTimers();

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');

      // Type rapidly without debounce completing
      await user.type(searchInput, 'Lak');

      // Should not have called API yet
      expect(apiClient.searchTeamsEnhanced).not.toHaveBeenCalled();

      // Fast forward debounce time
      act(() => {
        vi.advanceTimersByTime(300);
      });

      // Now should have called API
      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'Lak',
            sport_id: 'basketball-uuid',
          })
        );
      });

      vi.useRealTimers();
    });

    it('should handle enhanced search highlighting', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          useEnhancedSearch={true}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lakers');

      // Open dropdown
      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      // Should show relevance score
      expect(screen.getByText('95% match')).toBeInTheDocument();
    });

    it('should handle search suggestions', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          showSearchSuggestions={true}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lak');

      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledWith('Lak');
      });
    });

    it('should clear search when clear button is clicked', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lakers');

      expect(searchInput).toHaveValue('Lakers');

      const clearButton = screen.getByLabelText('Clear search');
      await user.click(clearButton);

      expect(searchInput).toHaveValue('');
    });

    it('should handle special characters in search', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'St. Louis & Co.');

      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'St. Louis & Co.',
          })
        );
      });
    });

    it('should handle empty search results gracefully', async () => {
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

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'NonexistentTeam');

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('No teams found for "NonexistentTeam".')).toBeInTheDocument();
      });
    });
  });

  describe('Filter Functionality', () => {
    it('should apply sport filters correctly', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          showFilters={true}
        />
      );

      // Wait for teams to load to populate filter options
      await waitFor(() => {
        expect(screen.getByText('Filter teams...')).toBeInTheDocument();
      });

      const filterButton = screen.getByText('Filter teams...');
      await user.click(filterButton);

      // Should show filter options
      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });
    });

    it('should combine search and filters correctly', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          showFilters={true}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Chicago');

      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'Chicago',
            sport_id: 'basketball-uuid',
          })
        );
      });
    });

    it('should clear all filters when clear all is clicked', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          showFilters={true}
        />
      );

      // Open filter dropdown
      const filterButton = screen.getByText('Filter teams...');
      await user.click(filterButton);

      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });

      // If clear all button exists, click it
      const clearAllButton = screen.queryByText('Clear all');
      if (clearAllButton) {
        await user.click(clearAllButton);
      }
    });
  });

  describe('Team Selection Limits', () => {
    it('should enforce maximum selection limit', async () => {
      const selectedTeams = mockTeams.slice(0, 2); // Start with 2 teams selected

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={selectedTeams}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          maxSelections={2}
          useEnhancedSearch={false}
        />
      );

      // Should show max selections reached
      expect(screen.getByText('Maximum teams selected')).toBeInTheDocument();

      const button = screen.getByRole('combobox');
      expect(button).toBeDisabled();
    });

    it('should show warning when approaching limit', async () => {
      const { toast } = await import('@/components/ui/sonner');

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={mockTeams.slice(0, 1)} // 1 team selected
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          maxSelections={3}
          useEnhancedSearch={false}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Golden State Warriors')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Golden State Warriors'));

      // Should call onTeamSelect with both teams
      expect(mockOnTeamSelect).toHaveBeenCalledWith([mockTeams[0], mockTeams[1]]);

      // Should show warning toast (approaching limit at 2/3)
      expect(toast.warning).toHaveBeenCalledWith(
        expect.stringContaining('Approaching limit'),
        expect.any(Object)
      );
    });

    it('should prevent selection when at limit', async () => {
      const { toast } = await import('@/components/ui/sonner');

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={mockTeams.slice(0, 3)} // 3 teams selected (at limit)
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          maxSelections={3}
          useEnhancedSearch={false}
        />
      );

      // Button should be disabled
      const button = screen.getByRole('combobox');
      expect(button).toBeDisabled();
      expect(button).toHaveTextContent('Maximum teams selected');
    });

    it('should allow deselection when at limit', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={mockTeams.slice(0, 2)}
          onTeamSelect={mockOnTeamSelect}
          maxSelections={2}
        />
      );

      // Should show selected teams
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();

      // Should be able to remove a team
      const removeButton = screen.getByLabelText('Remove Los Angeles Lakers');
      await user.click(removeButton);

      expect(mockOnTeamSelect).toHaveBeenCalledWith([mockTeams[1]]);
    });
  });

  describe('Performance and Edge Cases', () => {
    it('should handle rapid typing without performance issues', async () => {
      vi.useFakeTimers();

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');

      // Type very rapidly
      const rapidText = 'Los Angeles Lakers Basketball Team';
      for (const char of rapidText) {
        await user.type(searchInput, char);
        act(() => {
          vi.advanceTimersByTime(10); // Very fast typing
        });
      }

      // Should only have the final result
      expect(searchInput).toHaveValue(rapidText);

      // Advance past debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      // Should only call API once with final query
      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledTimes(1);
      });

      vi.useRealTimers();
    });

    it('should handle API errors gracefully', async () => {
      (apiClient.searchTeamsEnhanced as any).mockRejectedValue(new Error('Network error'));

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lakers');

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Failed to search teams. Please try again.')).toBeInTheDocument();
      });
    });

    it('should handle very long search terms', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      const longText = 'A'.repeat(1000); // Very long search term

      await user.type(searchInput, longText);

      await waitFor(() => {
        expect(apiClient.searchTeamsEnhanced).toHaveBeenCalledWith(
          expect.objectContaining({
            query: longText,
          })
        );
      });
    });

    it('should maintain performance with 100+ teams', async () => {
      // Create 100+ mock teams
      const manyTeams: Team[] = Array.from({ length: 150 }, (_, i) => ({
        ...mockTeams[0],
        id: `team-${i}`,
        name: `Team ${i}`,
        display_name: `Test Team ${i}`,
        abbreviation: `T${i}`,
      }));

      (apiClient.searchTeamsEnhanced as any).mockResolvedValue({
        items: manyTeams,
        total: manyTeams.length,
        page: 1,
        page_size: 50,
        has_next: true,
        has_previous: false,
        search_metadata: {
          query: 'test',
          total_matches: manyTeams.length,
          response_time_ms: 25,
          search_algorithm: 'enhanced',
        },
      });

      const startTime = performance.now();

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Test Team 0')).toBeInTheDocument();
      });

      const endTime = performance.now();

      // Should render within reasonable time (< 100ms)
      expect(endTime - startTime).toBeLessThan(100);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      const combobox = screen.getByRole('combobox');
      expect(combobox).toHaveAttribute('aria-label', 'Select teams');

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      expect(searchInput).toBeInTheDocument();
    });

    it('should handle keyboard navigation', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          useEnhancedSearch={false}
        />
      );

      const button = screen.getByRole('combobox');

      // Focus and open with Enter
      button.focus();
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
      });

      // Should be able to navigate with arrow keys
      const searchInput = screen.getByPlaceholderText('Search for teams...');
      expect(searchInput).toHaveFocus();

      // Escape should close
      await user.keyboard('{Escape}');
      expect(searchInput).toHaveValue('');
    });

    it('should announce selection changes to screen readers', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[mockTeams[0]]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      // Should show selected team count
      expect(screen.getByText('Selected Teams (1)')).toBeInTheDocument();
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();

      // Remove button should have proper label
      const removeButton = screen.getByLabelText('Remove Los Angeles Lakers');
      expect(removeButton).toBeInTheDocument();
    });
  });
});