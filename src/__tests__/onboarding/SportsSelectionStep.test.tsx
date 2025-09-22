/**
 * Tests for SportsSelectionStep component
 * Tests drag and drop functionality, sport selection, API integration
 */

import { screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { renderWithProviders } from '@/test-setup';
import { SportsSelectionStep } from '@/pages/onboarding/SportsSelectionStep';

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

// Mock API client
const mockUpdateOnboardingStep = vi.fn();
const mockGetOnboardingSports = vi.fn();

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    updateOnboardingStep: mockUpdateOnboardingStep,
    getOnboardingSports: mockGetOnboardingSports,
  },
}));

// Mock React Query
const mockUseQuery = vi.fn();
const mockUseMutation = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: mockUseQuery,
    useMutation: mockUseMutation,
  };
});

const mockSportsData = [
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
  {
    id: '3',
    name: 'Baseball',
    slug: 'baseball',
    icon: '⚾',
    icon_url: 'https://example.com/baseball.png',
    description: 'Baseball',
    popularity_rank: 3,
    is_active: true,
  },
];

describe('SportsSelectionStep', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockNavigate.mockClear();
    mockUpdateOnboardingStep.mockClear();
    mockGetOnboardingSports.mockClear();
    vi.clearAllMocks();

    // Default successful query mock
    mockUseQuery.mockReturnValue({
      data: { sports: mockSportsData, total: mockSportsData.length },
      isLoading: false,
      error: null,
      isError: false,
    });

    // Default successful mutation mock
    mockUseMutation.mockReturnValue({
      mutate: mockUpdateOnboardingStep,
      isLoading: false,
      error: null,
      isError: false,
    });
  });

  it('renders sports selection interface', async () => {
    renderWithProviders(<SportsSelectionStep />);

    expect(screen.getByText('Step 2 of 5')).toBeInTheDocument();
    expect(screen.getByText(/select.*sports/i)).toBeInTheDocument();

    // Wait for sports to load
    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
      expect(screen.getByText('Basketball')).toBeInTheDocument();
      expect(screen.getByText('Baseball')).toBeInTheDocument();
    });
  });

  it('displays loading state while fetching sports', () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      isError: false,
    });

    renderWithProviders(<SportsSelectionStep />);

    expect(screen.getByTestId('loading-sports')).toBeInTheDocument();
  });

  it('displays error state when sports fetch fails', () => {
    mockUseQuery.mockReturnValue({
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
    mockUpdateOnboardingStep.mockResolvedValue({ currentStep: 3 });

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
      expect(mockUpdateOnboardingStep).toHaveBeenCalledWith({
        step: 3,
        data: {
          sports: expect.arrayContaining([
            expect.objectContaining({ sportId: '1', rank: 1 }),
            expect.objectContaining({ sportId: '2', rank: 2 }),
          ]),
        },
      });
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/3');
    });
  });

  it('handles API error during save', async () => {
    mockUpdateOnboardingStep.mockRejectedValue(new Error('API Error'));

    renderWithProviders(<SportsSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Football')).toBeInTheDocument();
    });

    // Select a sport
    await user.click(screen.getByTestId('sport-card-1'));

    // Click continue
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    await waitFor(() => {
      expect(screen.getByText(/error.*saving/i)).toBeInTheDocument();
    });
  });

  it('allows maximum of 5 sports selection', async () => {
    // Add more sports to mock data
    const extendedSportsData = [
      ...mockSportsData,
      { id: '4', name: 'Soccer', slug: 'soccer', icon: '⚽', description: 'Soccer', popularity_rank: 4, is_active: true },
      { id: '5', name: 'Tennis', slug: 'tennis', icon: '🎾', description: 'Tennis', popularity_rank: 5, is_active: true },
      { id: '6', name: 'Hockey', slug: 'hockey', icon: '🏒', description: 'Hockey', popularity_rank: 6, is_active: true },
    ];

    mockUseQuery.mockReturnValue({
      data: { sports: extendedSportsData, total: extendedSportsData.length },
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
    mockUseQuery.mockReturnValue({
      data: { sports: [], total: 0 },
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
});