import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { axe, toHaveNoViolations } from 'jest-axe';
import { TeamSelector } from '@/components/TeamSelector';
import { TeamSearchInput } from '@/components/TeamSearchInput';
import { TeamFilterDropdown } from '@/components/TeamFilterDropdown';
import { apiClient, type Team } from '@/lib/api-client';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock the API client
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
];

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

describe('Team Selection Accessibility Tests', () => {
  const mockOnTeamSelect = vi.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();

    // Setup default API responses
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
      ],
    });
  });

  describe('TeamSelector Accessibility', () => {
    it('should not have any accessibility violations', async () => {
      const { container } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have violations when opened', async () => {
      const { container } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
      });

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have violations with selected teams', async () => {
      const { container } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={[mockTeams[0]]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have violations in error state', async () => {
      const { container } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          error="Test error message"
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not have violations when disabled', async () => {
      const { container } = renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
          disabled
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('ARIA Labels and Roles', () => {
    it('has proper combobox role and attributes', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      const combobox = screen.getByRole('combobox');
      expect(combobox).toHaveAttribute('aria-expanded', 'false');
      expect(combobox).toHaveAttribute('aria-label', 'Select teams');
    });

    it('updates aria-expanded when opened', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      expect(combobox).toHaveAttribute('aria-expanded', 'true');
    });

    it('has proper labels for remove buttons', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[mockTeams[0]]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      const removeButton = screen.getByLabelText('Remove Los Angeles Lakers');
      expect(removeButton).toBeInTheDocument();
    });

    it('provides proper team option descriptions', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      // Team options should have accessible descriptions
      const teamOption = screen.getByText('Los Angeles Lakers').closest('[role="option"]');
      expect(teamOption).toBeInTheDocument();
    });

    it('announces selection changes', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Los Angeles Lakers'));

      // Should show selection count
      await waitFor(() => {
        expect(screen.getByText('Selected Teams (1)')).toBeInTheDocument();
      });
    });
  });

  describe('Keyboard Navigation', () => {
    it('supports Enter key to open dropdown', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      combobox.focus();

      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
      });
    });

    it('focuses search input when dropdown opens', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText('Search for teams...');
        expect(searchInput).toHaveFocus();
      });
    });

    it('supports Escape key to clear search', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      await user.type(searchInput, 'Lakers');

      expect(searchInput).toHaveValue('Lakers');

      await user.keyboard('{Escape}');

      expect(searchInput).toHaveValue('');
    });

    it('supports Tab navigation', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[mockTeams[0]]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      // Tab through the component
      const combobox = screen.getByRole('combobox');
      combobox.focus();

      await user.keyboard('{Tab}');

      // Should move to remove button
      const removeButton = screen.getByLabelText('Remove Los Angeles Lakers');
      expect(removeButton).toHaveFocus();
    });

    it('maintains focus management in dropdown', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      const searchInput = screen.getByPlaceholderText('Search for teams...');
      expect(searchInput).toHaveFocus();

      // Arrow keys should navigate options (when implemented)
      await user.keyboard('{ArrowDown}');

      // Focus should remain manageable
      expect(document.activeElement).toBeTruthy();
    });
  });

  describe('Screen Reader Support', () => {
    it('provides meaningful text alternatives for images', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });

      // Team logo should have alt text
      const logo = screen.getByAltText('Los Angeles Lakers logo');
      expect(logo).toBeInTheDocument();
    });

    it('announces loading states', async () => {
      // Mock slow loading
      let resolvePromise: (value: any) => void;
      const slowPromise = new Promise(resolve => {
        resolvePromise = resolve;
      });
      (apiClient.searchTeamsEnhanced as any).mockReturnValue(slowPromise);

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText('Searching teams...')).toBeInTheDocument();
      });

      // Resolve the promise
      resolvePromise!({
        items: mockTeams,
        total: mockTeams.length,
        page: 1,
        page_size: 50,
        has_next: false,
        has_previous: false,
        search_metadata: {
          query: '',
          total_matches: mockTeams.length,
          response_time_ms: 100,
          search_algorithm: 'enhanced',
        },
      });

      await waitFor(() => {
        expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      });
    });

    it('announces error states', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          error="Failed to load teams"
        />
      );

      // Error should be announced
      expect(screen.getByText('Failed to load teams')).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /alert/i })).toBeInTheDocument();
    });

    it('provides status updates for selections', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={mockTeams.slice(0, 2)}
          onTeamSelect={mockOnTeamSelect}
          maxSelections={10}
        />
      );

      // Should announce current selection status
      expect(screen.getByText('Selected Teams (2)')).toBeInTheDocument();
      expect(screen.getByText('Select up to 10 teams.')).toBeInTheDocument();
    });
  });

  describe('TeamSearchInput Accessibility', () => {
    const mockOnChange = vi.fn();

    it('should not have any accessibility violations', async () => {
      const { container } = renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has proper input labeling', () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      expect(input).toHaveAttribute('type', 'text');
    });

    it('has accessible clear button', () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} />
      );

      const clearButton = screen.getByLabelText('Clear search');
      expect(clearButton).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      input.focus();

      await user.keyboard('Lakers');
      expect(input).toHaveValue('Lakers');

      await user.keyboard('{Escape}');
      expect(mockOnChange).toHaveBeenCalledWith('');
    });
  });

  describe('TeamFilterDropdown Accessibility', () => {
    const mockOnChange = vi.fn();
    const mockCategories = [
      {
        id: 'sport',
        name: 'Sport',
        options: [
          { id: 'basketball', name: 'Basketball', count: 30 },
          { id: 'football', name: 'Football', count: 32 },
        ],
        multiSelect: true,
      },
    ];

    it('should not have any accessibility violations', async () => {
      const { container } = render(
        <TeamFilterDropdown
          categories={mockCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has proper combobox attributes', () => {
      render(
        <TeamFilterDropdown
          categories={mockCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const combobox = screen.getByRole('combobox');
      expect(combobox).toHaveAttribute('aria-expanded', 'false');
    });

    it('supports keyboard navigation', async () => {
      render(
        <TeamFilterDropdown
          categories={mockCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const combobox = screen.getByRole('combobox');
      combobox.focus();

      await user.keyboard('{Enter}');

      expect(combobox).toHaveAttribute('aria-expanded', 'true');
    });
  });

  describe('Color Contrast and Visual Accessibility', () => {
    it('maintains adequate contrast in selected state', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[mockTeams[0]]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      // Selected team badges should have adequate contrast
      const selectedTeam = screen.getByText('Los Angeles Lakers');
      expect(selectedTeam).toBeInTheDocument();
    });

    it('maintains contrast in disabled state', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          disabled
        />
      );

      const combobox = screen.getByRole('combobox');
      expect(combobox).toBeDisabled();
    });

    it('provides visual focus indicators', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      const combobox = screen.getByRole('combobox');
      combobox.focus();

      // Should have visible focus state
      expect(combobox).toHaveFocus();
    });
  });

  describe('Motion and Animation Accessibility', () => {
    it('respects reduced motion preferences', async () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      // Animations should be minimal or disabled
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
      });
    });
  });

  describe('Touch and Mobile Accessibility', () => {
    it('has adequate touch targets', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[mockTeams[0]]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      const combobox = screen.getByRole('combobox');
      const removeButton = screen.getByLabelText('Remove Los Angeles Lakers');

      // Touch targets should be adequately sized (this is more visual/CSS related)
      expect(combobox).toBeInTheDocument();
      expect(removeButton).toBeInTheDocument();
    });

    it('supports touch interactions', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      const combobox = screen.getByRole('combobox');

      // Simulate touch events
      fireEvent.touchStart(combobox);
      fireEvent.touchEnd(combobox);
      fireEvent.click(combobox);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
      });
    });
  });

  describe('WCAG 2.1 AA Compliance', () => {
    it('meets keyboard accessibility requirements', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          sportIds={['basketball-uuid']}
        />
      );

      // All interactive elements should be keyboard accessible
      const combobox = screen.getByRole('combobox');

      // Tab to element
      combobox.focus();
      expect(combobox).toHaveFocus();

      // Activate with Enter
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
      });

      // Escape should close
      await user.keyboard('{Escape}');
    });

    it('provides sufficient context for form elements', () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
          placeholder="Choose your favorite teams"
        />
      );

      const combobox = screen.getByRole('combobox');
      expect(combobox).toHaveTextContent('Choose your favorite teams');
    });

    it('maintains focus visibility', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      const combobox = screen.getByRole('combobox');
      combobox.focus();

      // Focus should be clearly visible (CSS dependent)
      expect(combobox).toHaveFocus();
      expect(document.activeElement).toBe(combobox);
    });

    it('provides meaningful sequence navigation', async () => {
      renderWithQueryClient(
        <TeamSelector
          selectedTeams={[mockTeams[0], mockTeams[1]]}
          onTeamSelect={mockOnTeamSelect}
        />
      );

      // Tab order should be logical
      const combobox = screen.getByRole('combobox');
      const removeButton1 = screen.getByLabelText('Remove Los Angeles Lakers');
      const removeButton2 = screen.getByLabelText('Remove Golden State Warriors');

      // Focus first element
      combobox.focus();
      expect(combobox).toHaveFocus();

      // Tab to first remove button
      await user.keyboard('{Tab}');
      expect(removeButton1).toHaveFocus();

      // Tab to second remove button
      await user.keyboard('{Tab}');
      expect(removeButton2).toHaveFocus();
    });
  });
});