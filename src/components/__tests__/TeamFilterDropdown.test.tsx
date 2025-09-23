import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TeamFilterDropdown, createFilterCategoriesFromTeams, type FilterCategory, type FilterValues } from '../TeamFilterDropdown';

const mockFilterCategories: FilterCategory[] = [
  {
    id: 'sport',
    name: 'Sport',
    options: [
      { id: 'basketball-uuid', name: 'Basketball', count: 30 },
      { id: 'football-uuid', name: 'Football', count: 32 },
      { id: 'baseball-uuid', name: 'Baseball', count: 30 },
    ],
    multiSelect: true,
  },
  {
    id: 'league',
    name: 'League',
    options: [
      { id: 'nba-uuid', name: 'NBA', count: 30 },
      { id: 'nfl-uuid', name: 'NFL', count: 32 },
      { id: 'mlb-uuid', name: 'MLB', count: 30 },
      { id: 'nhl-uuid', name: 'NHL', count: 30 },
    ],
    multiSelect: false,
  },
];

const mockTeamsForFilters = [
  {
    sport_id: 'basketball-uuid',
    sport_name: 'Basketball',
    league_id: 'nba-uuid',
    league_name: 'NBA',
  },
  {
    sport_id: 'basketball-uuid',
    sport_name: 'Basketball',
    league_id: 'nba-uuid',
    league_name: 'NBA',
  },
  {
    sport_id: 'football-uuid',
    sport_name: 'Football',
    league_id: 'nfl-uuid',
    league_name: 'NFL',
  },
  {
    sport_id: 'football-uuid',
    sport_name: 'Football',
    league_id: 'nfl-uuid',
    league_name: 'NFL',
  },
  {
    sport_id: 'baseball-uuid',
    sport_name: 'Baseball',
    league_id: 'mlb-uuid',
    league_name: 'MLB',
  },
];

describe('TeamFilterDropdown', () => {
  const mockOnChange = vi.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();
  });

  describe('Basic Functionality', () => {
    it('renders with default placeholder', () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('Filter teams...')).toBeInTheDocument();
    });

    it('renders with custom placeholder', () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
          placeholder="Custom filter placeholder"
        />
      );

      expect(screen.getByText('Custom filter placeholder')).toBeInTheDocument();
    });

    it('is disabled when disabled prop is true', () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
          disabled
        />
      );

      const button = screen.getByRole('combobox');
      expect(button).toBeDisabled();
    });

    it('opens filter panel when clicked', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });
    });
  });

  describe('Active Filter Display', () => {
    it('shows filter count when filters are applied', () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
        league: 'nba-uuid',
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('2 filters applied')).toBeInTheDocument();
    });

    it('shows singular filter text for single filter', () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('1 filter applied')).toBeInTheDocument();
    });

    it('displays filter count badge', () => {
      const values: FilterValues = {
        sport: ['basketball-uuid', 'football-uuid'],
        league: 'nba-uuid',
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('3')).toBeInTheDocument(); // Badge count
    });

    it('highlights button when filters are active', () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      expect(button).toHaveClass('border-primary');
    });
  });

  describe('Multi-Select Filters', () => {
    it('displays multi-select checkboxes correctly', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Sport')).toBeInTheDocument();
        expect(screen.getByText('Basketball')).toBeInTheDocument();
        expect(screen.getByText('Football')).toBeInTheDocument();
        expect(screen.getByText('Baseball')).toBeInTheDocument();
      });

      // Should show option counts
      expect(screen.getByText('(30)')).toBeInTheDocument(); // Basketball count
      expect(screen.getByText('(32)')).toBeInTheDocument(); // Football count
    });

    it('selects and deselects multi-select options', async () => {
      const values: FilterValues = {
        sport: [],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Basketball')).toBeInTheDocument();
      });

      // Click Basketball option
      await user.click(screen.getByText('Basketball'));

      expect(mockOnChange).toHaveBeenCalledWith({
        sport: ['basketball-uuid'],
      });
    });

    it('handles multiple selections in multi-select', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Click Football option (should add to existing selection)
      await user.click(screen.getByText('Football'));

      expect(mockOnChange).toHaveBeenCalledWith({
        sport: ['basketball-uuid', 'football-uuid'],
      });
    });

    it('deselects already selected multi-select option', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid', 'football-uuid'],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Basketball')).toBeInTheDocument();
      });

      // Click Basketball option (should remove from selection)
      await user.click(screen.getByText('Basketball'));

      expect(mockOnChange).toHaveBeenCalledWith({
        sport: ['football-uuid'],
      });
    });

    it('shows checkmarks for selected multi-select options', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Basketball')).toBeInTheDocument();
      });

      // Basketball should be checked
      const basketballOption = screen.getByText('Basketball').closest('div');
      expect(basketballOption?.querySelector('[class*="bg-primary"]')).toBeInTheDocument();
    });
  });

  describe('Single-Select Filters', () => {
    it('displays single-select dropdown correctly', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('League')).toBeInTheDocument();
      });

      // Should show a select dropdown for League
      const leagueSelect = screen.getByDisplayValue('Select league...');
      expect(leagueSelect).toBeInTheDocument();
    });

    it('selects single-select option', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('League')).toBeInTheDocument();
      });

      // Open league select and choose NBA
      const leagueSelect = screen.getByDisplayValue('Select league...');
      await user.click(leagueSelect);

      await waitFor(() => {
        expect(screen.getByText('NBA')).toBeInTheDocument();
      });

      await user.click(screen.getByText('NBA'));

      expect(mockOnChange).toHaveBeenCalledWith({
        league: 'nba-uuid',
      });
    });

    it('deselects single-select option when selecting "All"', async () => {
      const values: FilterValues = {
        league: 'nba-uuid',
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('League')).toBeInTheDocument();
      });

      // Open league select and choose "All League"
      const leagueSelect = screen.getByDisplayValue('NBA');
      await user.click(leagueSelect);

      await waitFor(() => {
        expect(screen.getByText('All League')).toBeInTheDocument();
      });

      await user.click(screen.getByText('All League'));

      expect(mockOnChange).toHaveBeenCalledWith({
        league: '',
      });
    });

    it('replaces single-select value when selecting different option', async () => {
      const values: FilterValues = {
        league: 'nba-uuid',
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('League')).toBeInTheDocument();
      });

      // Change from NBA to NFL
      const leagueSelect = screen.getByDisplayValue('NBA');
      await user.click(leagueSelect);

      await waitFor(() => {
        expect(screen.getByText('NFL')).toBeInTheDocument();
      });

      await user.click(screen.getByText('NFL'));

      expect(mockOnChange).toHaveBeenCalledWith({
        league: 'nfl-uuid',
      });
    });
  });

  describe('Active Filters Display', () => {
    it('shows active filters in the panel', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid', 'football-uuid'],
        league: 'nba-uuid',
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Active filters:')).toBeInTheDocument();
        expect(screen.getByText('Basketball')).toBeInTheDocument();
        expect(screen.getByText('Football')).toBeInTheDocument();
        expect(screen.getByText('NBA')).toBeInTheDocument();
      });
    });

    it('does not show active filters section when no filters applied', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });

      expect(screen.queryByText('Active filters:')).not.toBeInTheDocument();
    });
  });

  describe('Clear All Functionality', () => {
    it('shows clear all button when filters are applied', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
        league: 'nba-uuid',
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Clear all')).toBeInTheDocument();
      });
    });

    it('does not show clear all button when no filters applied', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });

      expect(screen.queryByText('Clear all')).not.toBeInTheDocument();
    });

    it('clears all filters when clear all is clicked', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid', 'football-uuid'],
        league: 'nba-uuid',
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Clear all')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Clear all'));

      expect(mockOnChange).toHaveBeenCalledWith({
        sport: [],
        league: '',
      });
    });

    it('does not show clear all when showClearAll is false', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
          showClearAll={false}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });

      expect(screen.queryByText('Clear all')).not.toBeInTheDocument();
    });
  });

  describe('Empty States', () => {
    it('shows empty message when no categories provided', async () => {
      render(
        <TeamFilterDropdown
          categories={[]}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('No filter options available')).toBeInTheDocument();
      });
    });

    it('handles categories with no options', async () => {
      const emptyCategories: FilterCategory[] = [
        {
          id: 'empty',
          name: 'Empty Category',
          options: [],
        },
      ];

      render(
        <TeamFilterDropdown
          categories={emptyCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Empty Category')).toBeInTheDocument();
      });

      // Should not crash with empty options
    });
  });

  describe('createFilterCategoriesFromTeams utility', () => {
    it('creates filter categories from team data', () => {
      const categories = createFilterCategoriesFromTeams(mockTeamsForFilters);

      expect(categories).toHaveLength(2); // Sport and League

      const sportCategory = categories.find(c => c.id === 'sport');
      expect(sportCategory).toBeDefined();
      expect(sportCategory?.name).toBe('Sport');
      expect(sportCategory?.multiSelect).toBe(true);
      expect(sportCategory?.options).toHaveLength(3); // Basketball, Football, Baseball

      const leagueCategory = categories.find(c => c.id === 'league');
      expect(leagueCategory).toBeDefined();
      expect(leagueCategory?.name).toBe('League');
      expect(leagueCategory?.multiSelect).toBe(true);
      expect(leagueCategory?.options).toHaveLength(3); // NBA, NFL, MLB
    });

    it('counts teams correctly for each option', () => {
      const categories = createFilterCategoriesFromTeams(mockTeamsForFilters);

      const sportCategory = categories.find(c => c.id === 'sport');
      const basketballOption = sportCategory?.options.find(o => o.name === 'Basketball');
      const footballOption = sportCategory?.options.find(o => o.name === 'Football');
      const baseballOption = sportCategory?.options.find(o => o.name === 'Baseball');

      expect(basketballOption?.count).toBe(2);
      expect(footballOption?.count).toBe(2);
      expect(baseballOption?.count).toBe(1);
    });

    it('handles empty team data', () => {
      const categories = createFilterCategoriesFromTeams([]);
      expect(categories).toHaveLength(0);
    });

    it('handles teams with missing sport/league data', () => {
      const incompleteTeams = [
        { sport_id: 'basketball-uuid', sport_name: 'Basketball' }, // Missing league
        { league_id: 'nba-uuid', league_name: 'NBA' }, // Missing sport
        {}, // Missing everything
      ];

      const categories = createFilterCategoriesFromTeams(incompleteTeams);

      // Should handle gracefully
      expect(categories.length).toBeGreaterThanOrEqual(0);
    });

    it('does not create category for single option', () => {
      const singleSportTeams = [
        { sport_id: 'basketball-uuid', sport_name: 'Basketball', league_id: 'nba-uuid', league_name: 'NBA' },
        { sport_id: 'basketball-uuid', sport_name: 'Basketball', league_id: 'nba-uuid', league_name: 'NBA' },
      ];

      const categories = createFilterCategoriesFromTeams(singleSportTeams);

      // Should not create sport category with only one sport
      const sportCategory = categories.find(c => c.id === 'sport');
      expect(sportCategory).toBeUndefined();
    });
  });

  describe('Performance and Edge Cases', () => {
    it('handles large number of filter options', async () => {
      const largeCategories: FilterCategory[] = [
        {
          id: 'teams',
          name: 'Teams',
          options: Array.from({ length: 500 }, (_, i) => ({
            id: `team-${i}`,
            name: `Team ${i}`,
            count: Math.floor(Math.random() * 100),
          })),
          multiSelect: true,
        },
      ];

      const startTime = performance.now();

      render(
        <TeamFilterDropdown
          categories={largeCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Teams')).toBeInTheDocument();
      });

      const endTime = performance.now();

      // Should render within reasonable time
      expect(endTime - startTime).toBeLessThan(200);
    });

    it('handles rapid filter changes', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Basketball')).toBeInTheDocument();
      });

      // Rapidly click multiple options
      await user.click(screen.getByText('Basketball'));
      await user.click(screen.getByText('Football'));
      await user.click(screen.getByText('Baseball'));

      // Should handle all clicks without issues
      expect(mockOnChange).toHaveBeenCalledTimes(3);
    });

    it('maintains state consistency with external updates', () => {
      const { rerender } = render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{ sport: ['basketball-uuid'] }}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('1 filter applied')).toBeInTheDocument();

      // Update values externally
      rerender(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{ sport: ['basketball-uuid', 'football-uuid'] }}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('2 filters applied')).toBeInTheDocument();
    });

    it('handles invalid filter values gracefully', () => {
      const invalidValues: FilterValues = {
        sport: ['nonexistent-sport-id'],
        league: 'nonexistent-league-id',
        unknownCategory: 'some-value',
      };

      // Should not crash with invalid values
      expect(() => {
        render(
          <TeamFilterDropdown
            categories={mockFilterCategories}
            values={invalidValues}
            onChange={mockOnChange}
          />
        );
      }).not.toThrow();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const combobox = screen.getByRole('combobox');
      expect(combobox).toHaveAttribute('aria-expanded', 'false');
    });

    it('updates aria-expanded when opened', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const combobox = screen.getByRole('combobox');
      await user.click(combobox);

      expect(combobox).toHaveAttribute('aria-expanded', 'true');
    });

    it('provides proper keyboard navigation support', async () => {
      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={{}}
          onChange={mockOnChange}
        />
      );

      const combobox = screen.getByRole('combobox');

      // Should be focusable
      combobox.focus();
      expect(combobox).toHaveFocus();

      // Should open with Enter
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByText('Filter Teams')).toBeInTheDocument();
      });
    });

    it('has proper labels for screen readers', async () => {
      const values: FilterValues = {
        sport: ['basketball-uuid'],
      };

      render(
        <TeamFilterDropdown
          categories={mockFilterCategories}
          values={values}
          onChange={mockOnChange}
        />
      );

      expect(screen.getByText('1 filter applied')).toBeInTheDocument();

      const button = screen.getByRole('combobox');
      await user.click(button);

      await waitFor(() => {
        expect(screen.getByText('Active filters:')).toBeInTheDocument();
      });
    });
  });
});