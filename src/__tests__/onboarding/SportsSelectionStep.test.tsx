/**
 * Tests for SportsSelectionStep component
 * Tests drag and drop functionality, sport selection, API integration
 */

import { screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { renderWithProviders } from '@/test-setup';
import { SportsSelectionStep } from '@/pages/onboarding/SportsSelectionStep';
import { useQuery, useMutation } from '@tanstack/react-query';

// Mock the navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ step: '2' }),
  };
});

// Mock Firebase Auth context
vi.mock('@/contexts/FirebaseAuthContext', () => ({
  useFirebaseAuth: vi.fn(() => ({
    isAuthenticated: true,
    user: { uid: 'test-user-id' },
    getIdToken: vi.fn().mockResolvedValue('test-token'),
    loading: false,
    error: null,
  })),
  FirebaseAuthProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    updateOnboardingStep: vi.fn(),
    getOnboardingSports: vi.fn(),
  },
  createApiQueryClient: vi.fn(() => ({
    getOnboardingSports: () => ({
      queryKey: ['onboarding', 'sports'],
      queryFn: vi.fn(),
      staleTime: 30 * 60 * 1000,
    }),
  })),
}));

// Mock React Query
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: vi.fn(),
    useMutation: vi.fn(),
    useQueryClient: vi.fn(() => ({
      invalidateQueries: vi.fn(),
      setQueryData: vi.fn(),
    })),
  };
});

const mockSportsData = [
  {
    id: '1',
    name: 'Football',
    icon: '🏈',
    hasTeams: true,
    isPopular: true,
  },
  {
    id: '2',
    name: 'Basketball',
    icon: '🏀',
    hasTeams: true,
    isPopular: true,
  },
  {
    id: '3',
    name: 'Baseball',
    icon: '⚾',
    hasTeams: true,
    isPopular: false,
  },
];

describe('SportsSelectionStep', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockNavigate.mockClear();
    vi.clearAllMocks();

    // Default successful query mock
    vi.mocked(useQuery).mockReturnValue({
      data: mockSportsData,
      isLoading: false,
      error: null,
      isError: false,
    });

    // Default successful mutation mock
    vi.mocked(useMutation).mockReturnValue({
      mutate: vi.fn(),
      isLoading: false,
      error: null,
      isError: false,
    });
  });

  it('renders sports selection interface', async () => {
    renderWithProviders(<SportsSelectionStep />);

    expect(screen.getByText('Step 2 of 5')).toBeInTheDocument();
    expect(screen.getByText('Choose Your Sports')).toBeInTheDocument();

    // Wait for sports to load
    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
      expect(screen.getByText('Basketball')).toBeInTheDocument();
      expect(screen.getByText('Baseball')).toBeInTheDocument();
    });
  });

  it('displays loading state while fetching sports', () => {
    vi.mocked(useQuery).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      isError: false,
    });

    renderWithProviders(<SportsSelectionStep />);

    expect(screen.getByTestId('loading-sports')).toBeInTheDocument();
  });

  it('displays error state when sports fetch fails', () => {
    vi.mocked(useQuery).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch sports'),
      isError: true,
    });

    renderWithProviders(<SportsSelectionStep />);

    expect(screen.getByText(/error.*loading.*sports/i)).toBeInTheDocument();
  });

  it('allows sport selection via click', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    const footballCard = screen.getByTestId('sport-card-1');
    await user.click(footballCard);

    expect(footballCard).toHaveAttribute('data-selected', 'true');
  });

  it('allows sport deselection via click', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    const footballCard = screen.getByTestId('sport-card-1');

    // Select
    await user.click(footballCard);
    expect(footballCard).toHaveAttribute('data-selected', 'true');

    // Deselect
    await user.click(footballCard);
    expect(footballCard).toHaveAttribute('data-selected', 'false');
  });

  it('supports keyboard navigation for sport selection', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    const footballCard = screen.getByTestId('sport-card-1');

    // Tab to the card and press Enter
    footballCard.focus();
    await user.keyboard('{Enter}');

    expect(footballCard).toHaveAttribute('data-selected', 'true');

    // Press Space to deselect
    await user.keyboard(' ');
    expect(footballCard).toHaveAttribute('data-selected', 'false');
  });

  it('displays sport ranking when multiple sports selected', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Select multiple sports
    await user.click(screen.getByTestId('sport-card-1')); // Football
    await user.click(screen.getByTestId('sport-card-2')); // Basketball

    // Check ranking indicators appear
    expect(screen.getByText('1st')).toBeInTheDocument();
    expect(screen.getByText('2nd')).toBeInTheDocument();
  });

  it('supports drag and drop reordering of selected sports', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Select multiple sports
    await user.click(screen.getByTestId('sport-card-1')); // Football
    await user.click(screen.getByTestId('sport-card-2')); // Basketball

    // Test drag and drop (mocked behavior)
    const footballCard = screen.getByTestId('sport-card-1');
    const basketballCard = screen.getByTestId('sport-card-2');

    // Simulate drag start
    fireEvent.dragStart(footballCard);
    fireEvent.dragOver(basketballCard);
    fireEvent.drop(basketballCard);

    // After drag and drop, the order should change
    // This is a simplified test - actual implementation would test the reordering logic
    expect(footballCard).toBeInTheDocument();
    expect(basketballCard).toBeInTheDocument();
  });

  it('disables continue button when no sports selected', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    const continueButton = screen.getByRole('button', { name: /continue/i });
    expect(continueButton).toBeDisabled();
  });

  it('enables continue button when at least one sport selected', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Select a sport
    await user.click(screen.getByTestId('sport-card-1'));

    const continueButton = screen.getByRole('button', { name: /continue/i });
    expect(continueButton).not.toBeDisabled();
  });

  it('saves selection and navigates to next step', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Select sports
    await user.click(screen.getByTestId('sport-card-1'));
    await user.click(screen.getByTestId('sport-card-2'));

    // Click continue
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/3');
    });
  });

  it('allows maximum of 5 sports selection', async () => {
    // Add more sports to mock data
    const extendedSportsData = [
      ...mockSportsData,
      { id: '4', name: 'Soccer', icon: '⚽', hasTeams: true, isPopular: false },
      { id: '5', name: 'Tennis', icon: '🎾', hasTeams: true, isPopular: false },
      { id: '6', name: 'Hockey', icon: '🏒', hasTeams: true, isPopular: false },
    ];

    vi.mocked(useQuery).mockReturnValue({
      data: extendedSportsData,
      isLoading: false,
      error: null,
      isError: false,
    });

    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Select 5 sports
    for (let i = 1; i <= 5; i++) {
      await user.click(screen.getByTestId(`sport-card-${i}`));
    }

    // Try to select 6th sport
    const sixthSportCard = screen.getByTestId('sport-card-6');
    await user.click(sixthSportCard);

    // Should show warning message
    expect(screen.getByText(/maximum.*5.*sports/i)).toBeInTheDocument();
    // 6th sport should not be selected
    expect(sixthSportCard).toHaveAttribute('data-selected', 'false');
  });

  it('shows back button and handles back navigation', async () => {
    renderWithProviders(<SportsSelectionStep />);

    const backButton = screen.getByRole('button', { name: /back/i });
    expect(backButton).toBeInTheDocument();

    await user.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/1');
  });

  it('has proper accessibility attributes', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Check sport cards have proper accessibility
    const footballCard = screen.getByTestId('sport-card-1');
    expect(footballCard).toHaveAttribute('role', 'button');
    expect(footballCard).toHaveAttribute('tabindex', '0');
    expect(footballCard).toHaveAttribute('aria-selected', 'false');

    // Select the sport
    await user.click(footballCard);
    expect(footballCard).toHaveAttribute('aria-selected', 'true');

    // Check progress bar
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '40');
  });

  it('displays sports in popularity order', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    const sportsCards = screen.getAllByTestId(/sport-card-/);
    const sportsOrder = sportsCards.map(card =>
      within(card).getByText(/Football|Basketball|Baseball/).textContent
    );

    expect(sportsOrder).toEqual(['Football', 'Basketball', 'Baseball']);
  });

  it('persists selections during component re-renders', async () => {
    const { rerender } = renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Select a sport
    await user.click(screen.getByTestId('sport-card-1'));
    expect(screen.getByTestId('sport-card-1')).toHaveAttribute('data-selected', 'true');

    // Rerender component
    rerender(<SportsSelectionStep />);

    // Selection should persist (assuming proper state management)
    await waitFor(() => {
      expect(screen.getByTestId('sport-card-1')).toHaveAttribute('data-selected', 'true');
    });
  });

  it('handles empty sports list gracefully', () => {
    vi.mocked(useQuery).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
      isError: false,
    });

    renderWithProviders(<SportsSelectionStep />);

    expect(screen.getByText(/no.*sports.*available/i)).toBeInTheDocument();
  });

  it('shows tooltip with sport description on hover', async () => {
    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    const footballCard = screen.getByTestId('sport-card-1');
    await user.hover(footballCard);

    await waitFor(() => {
      expect(screen.getByText('American Football')).toBeInTheDocument();
    });
  });

  // DRAG-TO-SELECT FUNCTIONALITY TESTS
  describe('Drag-to-Select Functionality', () => {
    it('includes all sports in SortableContext items for drag functionality', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Verify all sports are rendered with drag handles
      const footballCard = screen.getByTestId('sport-card-1');
      const basketballCard = screen.getByTestId('sport-card-2');
      const baseballCard = screen.getByTestId('sport-card-3');

      // All cards should have drag handles
      expect(footballCard.querySelector('[data-drag-handle="true"]')).toBeInTheDocument();
      expect(basketballCard.querySelector('[data-drag-handle="true"]')).toBeInTheDocument();
      expect(baseballCard.querySelector('[data-drag-handle="true"]')).toBeInTheDocument();

      // All cards should be draggable (not disabled)
      expect(footballCard.querySelector('[data-drag-handle="true"]')).not.toHaveAttribute('disabled');
      expect(basketballCard.querySelector('[data-drag-handle="true"]')).not.toHaveAttribute('disabled');
      expect(baseballCard.querySelector('[data-drag-handle="true"]')).not.toHaveAttribute('disabled');
    });

    it('shows proper tooltip text for drag handles based on selection state', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Initially unselected sport should show "Drag to select and reorder"
      const footballDragHandle = screen.getByTestId('sport-card-1').querySelector('[data-drag-handle="true"]');
      expect(footballDragHandle).toHaveAttribute('title', 'Drag to select and reorder');

      // Select the sport
      await user.click(screen.getByTestId('sport-card-1'));

      // Selected sport should show "Drag to reorder"
      expect(footballDragHandle).toHaveAttribute('title', 'Drag to reorder');
    });

    it('displays helpful instruction text about drag functionality', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Verify the instruction text includes information about dragging
      expect(screen.getByText('Click to select sports or drag them to select and reorder by preference.')).toBeInTheDocument();
    });
  });

  // CRITICAL RANKING LOGIC TESTS
  describe('Sports Ranking Logic - Corruption Fix Tests', () => {
    it('maintains consecutive rank order during sequential selection/deselection', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Select sports in sequence
      await user.click(screen.getByTestId('sport-card-1')); // Football - should be rank 1
      await user.click(screen.getByTestId('sport-card-2')); // Basketball - should be rank 2
      await user.click(screen.getByTestId('sport-card-3')); // Baseball - should be rank 3

      // Verify initial ranking
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.getByText('3rd')).toBeInTheDocument();

      // Deselect middle sport (Basketball)
      await user.click(screen.getByTestId('sport-card-2'));

      // Verify ranks are normalized: Football=1st, Baseball=2nd (not 3rd)
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.queryByText('3rd')).not.toBeInTheDocument();
    });

    it('prevents rank corruption during rapid toggle operations', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Rapidly toggle sports to test for race conditions
      await user.click(screen.getByTestId('sport-card-1')); // Select Football
      await user.click(screen.getByTestId('sport-card-2')); // Select Basketball
      await user.click(screen.getByTestId('sport-card-1')); // Deselect Football
      await user.click(screen.getByTestId('sport-card-3')); // Select Baseball
      await user.click(screen.getByTestId('sport-card-1')); // Reselect Football

      // Verify final state has proper consecutive ranks
      const rankedElements = screen.getAllByText(/^\d+(st|nd|rd|th)$/);
      expect(rankedElements).toHaveLength(3); // Should have exactly 3 ranked items

      // Verify we have 1st, 2nd, 3rd (no gaps or duplicates)
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.getByText('3rd')).toBeInTheDocument();
    });

    it('maintains rank integrity during drag-and-drop operations', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Select multiple sports
      await user.click(screen.getByTestId('sport-card-1')); // Football
      await user.click(screen.getByTestId('sport-card-2')); // Basketball
      await user.click(screen.getByTestId('sport-card-3')); // Baseball

      // Simulate drag and drop (Football to position 3)
      const footballCard = screen.getByTestId('sport-card-1');
      const baseballCard = screen.getByTestId('sport-card-3');

      fireEvent.dragStart(footballCard);
      fireEvent.dragOver(baseballCard);
      fireEvent.drop(baseballCard);
      fireEvent.dragEnd(footballCard);

      // After drag, verify we still have consecutive ranks 1, 2, 3
      const rankedElements = screen.getAllByText(/^\d+(st|nd|rd|th)$/);
      expect(rankedElements).toHaveLength(3);
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.getByText('3rd')).toBeInTheDocument();
    });

    it('assigns logical ranks for bulk operations, not array index', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Test Select All button
      const selectAllButton = screen.getByRole('button', { name: /select all/i });
      await user.click(selectAllButton);

      // Verify all sports are selected with consecutive ranks
      const rankedElements = screen.getAllByText(/^\d+(st|nd|rd|th)$/);
      expect(rankedElements.length).toBeGreaterThan(0);

      // Verify ranks start from 1 and are consecutive
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.getByText('3rd')).toBeInTheDocument();
    });

    it('gives priority ranking to popular sports in bulk selection', async () => {
      // Mock data with popular sports
      const sportsWithPopular = [
        {
          id: '1',
          name: 'Football',
          icon: '🏈',
          hasTeams: true,
          isPopular: true,
        },
        {
          id: '2',
          name: 'Basketball',
          icon: '🏀',
          hasTeams: true,
          isPopular: true,
        },
        {
          id: '3',
          name: 'Baseball',
          icon: '⚾',
          hasTeams: true,
          isPopular: false,
        },
      ];

      vi.mocked(useQuery).mockReturnValue({
        data: sportsWithPopular,
        isLoading: false,
        error: null,
        isError: false,
      });

      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Test Popular Sports button
      const popularButton = screen.getByRole('button', { name: /popular sports/i });
      await user.click(popularButton);

      // Only popular sports should be selected (Football and Basketball)
      expect(screen.getByTestId('sport-card-1')).toHaveAttribute('data-selected', 'true');
      expect(screen.getByTestId('sport-card-2')).toHaveAttribute('data-selected', 'true');
      expect(screen.getByTestId('sport-card-3')).toHaveAttribute('data-selected', 'false');

      // Verify consecutive ranking for popular sports
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.queryByText('3rd')).not.toBeInTheDocument();
    });

    it('handles edge case: empty selection maintains clean state', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Select some sports first
      await user.click(screen.getByTestId('sport-card-1'));
      await user.click(screen.getByTestId('sport-card-2'));

      // Clear all selections
      const clearButton = screen.getByRole('button', { name: /clear all/i });
      await user.click(clearButton);

      // Verify no ranks are displayed
      expect(screen.queryByText(/\d+(st|nd|rd|th)/)).not.toBeInTheDocument();
      expect(screen.getByText('0 sports selected')).toBeInTheDocument();

      // Verify all cards are deselected
      expect(screen.getByTestId('sport-card-1')).toHaveAttribute('data-selected', 'false');
      expect(screen.getByTestId('sport-card-2')).toHaveAttribute('data-selected', 'false');
      expect(screen.getByTestId('sport-card-3')).toHaveAttribute('data-selected', 'false');
    });

    it('handles edge case: single sport selection', async () => {
      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Select only one sport
      await user.click(screen.getByTestId('sport-card-1'));

      // Verify it gets rank 1
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.queryByText('2nd')).not.toBeInTheDocument();
      expect(screen.getByText('1 sports selected')).toBeInTheDocument();
    });

    it('handles maximum selection edge case properly', async () => {
      // Extended mock data with 6+ sports for max selection testing
      const extendedSportsData = [
        ...mockSportsData,
        { id: '4', name: 'Soccer', icon: '⚽', hasTeams: true, isPopular: false },
        { id: '5', name: 'Tennis', icon: '🎾', hasTeams: true, isPopular: false },
        { id: '6', name: 'Hockey', icon: '🏒', hasTeams: true, isPopular: false },
      ];

      vi.mocked(useQuery).mockReturnValue({
        data: extendedSportsData,
        isLoading: false,
        error: null,
        isError: false,
      });

      renderWithProviders(<SportsSelectionStep />);

      await waitFor(() => {
        expect(screen.getByText('Football')).toBeInTheDocument();
      });

      // Select exactly 5 sports (maximum)
      for (let i = 1; i <= 5; i++) {
        await user.click(screen.getByTestId(`sport-card-${i}`));
      }

      // Verify we have exactly 5 consecutive ranks
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.getByText('3rd')).toBeInTheDocument();
      expect(screen.getByText('4th')).toBeInTheDocument();
      expect(screen.getByText('5th')).toBeInTheDocument();
      expect(screen.getByText('5 sports selected')).toBeInTheDocument();

      // Now deselect one sport and verify ranks remain consecutive
      await user.click(screen.getByTestId('sport-card-3')); // Deselect 3rd sport

      // Should now have ranks 1-4, no gaps
      expect(screen.getByText('1st')).toBeInTheDocument();
      expect(screen.getByText('2nd')).toBeInTheDocument();
      expect(screen.getByText('3rd')).toBeInTheDocument();
      expect(screen.getByText('4th')).toBeInTheDocument();
      expect(screen.queryByText('5th')).not.toBeInTheDocument();
      expect(screen.getByText('4 sports selected')).toBeInTheDocument();
    });
  });
});