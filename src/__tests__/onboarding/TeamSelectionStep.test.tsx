/**
 * Tests for TeamSelectionStep component
 * Tests team selection based on previously selected sports, search/filter functionality
 */

import { screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { renderWithProviders } from '@/test-setup';
import { TeamSelectionStep } from '@/pages/onboarding/TeamSelectionStep';

// Mock the navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ step: '3' }),
  };
});

// Mock API client
const mockUpdateOnboardingStep = vi.fn();
const mockGetOnboardingTeams = vi.fn();

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    updateOnboardingStep: mockUpdateOnboardingStep,
    getOnboardingTeams: mockGetOnboardingTeams,
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

const mockTeamsData = [
  {
    id: 'team-1',
    name: 'Patriots',
    market: 'New England',
    slug: 'patriots',
    sportId: 'sport-1',
    league: 'NFL',
    logo: 'https://example.com/patriots.png',
    colors: { primary: '#002244', secondary: '#C60C30' },
  },
  {
    id: 'team-2',
    name: 'Chiefs',
    market: 'Kansas City',
    slug: 'chiefs',
    sportId: 'sport-1',
    league: 'NFL',
    logo: 'https://example.com/chiefs.png',
    colors: { primary: '#E31837', secondary: '#FFB81C' },
  },
  {
    id: 'team-3',
    name: 'Lakers',
    market: 'Los Angeles',
    slug: 'lakers',
    sportId: 'sport-2',
    league: 'NBA',
    logo: 'https://example.com/lakers.png',
    colors: { primary: '#552583', secondary: '#FDB927' },
  },
  {
    id: 'team-4',
    name: 'Celtics',
    market: 'Boston',
    slug: 'celtics',
    sportId: 'sport-2',
    league: 'NBA',
    logo: 'https://example.com/celtics.png',
    colors: { primary: '#007A33', secondary: '#BA9653' },
  },
];

const mockSelectedSports = [
  { sportId: 'sport-1', name: 'Football', rank: 1 },
  { sportId: 'sport-2', name: 'Basketball', rank: 2 },
];

describe('TeamSelectionStep', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockNavigate.mockClear();
    mockUpdateOnboardingStep.mockClear();
    mockGetOnboardingTeams.mockClear();
    vi.clearAllMocks();

    // Mock the onboarding state to include selected sports
    vi.mocked(mockUseQuery).mockImplementation((queryKey) => {
      if (queryKey.includes('teams')) {
        return {
          data: { teams: mockTeamsData, total: mockTeamsData.length },
          isLoading: false,
          error: null,
          isError: false,
        };
      }
      // Default return for other queries
      return {
        data: { selectedSports: mockSelectedSports },
        isLoading: false,
        error: null,
        isError: false,
      };
    });

    mockUseMutation.mockReturnValue({
      mutate: mockUpdateOnboardingStep,
      isLoading: false,
      error: null,
      isError: false,
    });
  });

  it('renders team selection interface', async () => {
    renderWithProviders(<TeamSelectionStep />);

    expect(screen.getByText('Step 3 of 5')).toBeInTheDocument();
    expect(screen.getByText(/select.*teams/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
      expect(screen.getByText('Chiefs')).toBeInTheDocument();
      expect(screen.getByText('Lakers')).toBeInTheDocument();
      expect(screen.getByText('Celtics')).toBeInTheDocument();
    });
  });

  it('displays loading state while fetching teams', () => {
    vi.mocked(mockUseQuery).mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      isError: false,
    });

    renderWithProviders(<TeamSelectionStep />);

    expect(screen.getByTestId('loading-teams')).toBeInTheDocument();
  });

  it('displays error state when teams fetch fails', () => {
    vi.mocked(mockUseQuery).mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch teams'),
      isError: true,
    });

    renderWithProviders(<TeamSelectionStep />);

    expect(screen.getByText(/error.*loading.*teams/i)).toBeInTheDocument();
  });

  it('groups teams by sport/league', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('NFL')).toBeInTheDocument();
      expect(screen.getByText('NBA')).toBeInTheDocument();
    });

    // Check teams are under correct league sections
    const nflSection = screen.getByTestId('league-section-NFL');
    within(nflSection).getByText('Patriots');
    within(nflSection).getByText('Chiefs');

    const nbaSection = screen.getByTestId('league-section-NBA');
    within(nbaSection).getByText('Lakers');
    within(nbaSection).getByText('Celtics');
  });

  it('allows team selection via click', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const patriotsCard = screen.getByTestId('team-card-team-1');
    await user.click(patriotsCard);

    expect(patriotsCard).toHaveAttribute('data-selected', 'true');
  });

  it('allows team deselection via click', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const patriotsCard = screen.getByTestId('team-card-team-1');

    // Select
    await user.click(patriotsCard);
    expect(patriotsCard).toHaveAttribute('data-selected', 'true');

    // Deselect
    await user.click(patriotsCard);
    expect(patriotsCard).toHaveAttribute('data-selected', 'false');
  });

  it('supports search functionality', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search.*teams/i);
    await user.type(searchInput, 'Lakers');

    await waitFor(() => {
      expect(screen.getByText('Lakers')).toBeInTheDocument();
      expect(screen.queryByText('Patriots')).not.toBeInTheDocument();
      expect(screen.queryByText('Chiefs')).not.toBeInTheDocument();
      expect(screen.queryByText('Celtics')).not.toBeInTheDocument();
    });
  });

  it('supports filter by sport/league', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const leagueFilter = screen.getByRole('combobox', { name: /filter.*league/i });
    await user.click(leagueFilter);

    const nflOption = screen.getByRole('option', { name: 'NFL' });
    await user.click(nflOption);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
      expect(screen.getByText('Chiefs')).toBeInTheDocument();
      expect(screen.queryByText('Lakers')).not.toBeInTheDocument();
      expect(screen.queryByText('Celtics')).not.toBeInTheDocument();
    });
  });

  it('clears search when clear button is clicked', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search.*teams/i);
    await user.type(searchInput, 'Lakers');

    const clearButton = screen.getByRole('button', { name: /clear.*search/i });
    await user.click(clearButton);

    expect(searchInput).toHaveValue('');
    expect(screen.getByText('Patriots')).toBeInTheDocument();
  });

  it('shows affinity score slider for selected teams', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Select a team
    await user.click(screen.getByTestId('team-card-team-1'));

    // Affinity slider should appear
    const affinitySlider = screen.getByTestId('affinity-slider-team-1');
    expect(affinitySlider).toBeInTheDocument();
    expect(affinitySlider).toHaveAttribute('min', '1');
    expect(affinitySlider).toHaveAttribute('max', '10');
  });

  it('updates affinity score when slider is moved', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Select a team
    await user.click(screen.getByTestId('team-card-team-1'));

    const affinitySlider = screen.getByTestId('affinity-slider-team-1');
    fireEvent.change(affinitySlider, { target: { value: '8' } });

    expect(affinitySlider).toHaveValue('8');
    expect(screen.getByText('8/10')).toBeInTheDocument();
  });

  it('disables continue button when no teams selected', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const continueButton = screen.getByRole('button', { name: /continue/i });
    expect(continueButton).toBeDisabled();
  });

  it('enables continue button when at least one team selected', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Select a team
    await user.click(screen.getByTestId('team-card-team-1'));

    const continueButton = screen.getByRole('button', { name: /continue/i });
    expect(continueButton).not.toBeDisabled();
  });

  it('saves team selections and navigates to next step', async () => {
    mockUpdateOnboardingStep.mockResolvedValue({ currentStep: 4 });

    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Select teams with different affinity scores
    await user.click(screen.getByTestId('team-card-team-1'));
    const slider1 = screen.getByTestId('affinity-slider-team-1');
    fireEvent.change(slider1, { target: { value: '9' } });

    await user.click(screen.getByTestId('team-card-team-3'));
    const slider3 = screen.getByTestId('affinity-slider-team-3');
    fireEvent.change(slider3, { target: { value: '7' } });

    // Click continue
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    await waitFor(() => {
      expect(mockUpdateOnboardingStep).toHaveBeenCalledWith({
        step: 4,
        data: {
          teams: expect.arrayContaining([
            expect.objectContaining({
              teamId: 'team-1',
              sportId: 'sport-1',
              affinityScore: 9,
            }),
            expect.objectContaining({
              teamId: 'team-3',
              sportId: 'sport-2',
              affinityScore: 7,
            }),
          ]),
        },
      });
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/4');
    });
  });

  it('handles API error during save', async () => {
    mockUpdateOnboardingStep.mockRejectedValue(new Error('API Error'));

    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Select a team
    await user.click(screen.getByTestId('team-card-team-1'));

    // Click continue
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    await waitFor(() => {
      expect(screen.getByText(/error.*saving/i)).toBeInTheDocument();
    });
  });

  it('allows selection of multiple teams from same sport', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Select both NFL teams
    await user.click(screen.getByTestId('team-card-team-1'));
    await user.click(screen.getByTestId('team-card-team-2'));

    expect(screen.getByTestId('team-card-team-1')).toHaveAttribute('data-selected', 'true');
    expect(screen.getByTestId('team-card-team-2')).toHaveAttribute('data-selected', 'true');
  });

  it('limits maximum number of teams (e.g., 10)', async () => {
    // Mock more teams
    const manyTeams = Array.from({ length: 15 }, (_, i) => ({
      id: `team-${i + 1}`,
      name: `Team ${i + 1}`,
      market: `City ${i + 1}`,
      slug: `team-${i + 1}`,
      sportId: 'sport-1',
      league: 'NFL',
      logo: `https://example.com/team${i + 1}.png`,
      colors: { primary: '#000000', secondary: '#FFFFFF' },
    }));

    vi.mocked(mockUseQuery).mockReturnValue({
      data: { teams: manyTeams, total: manyTeams.length },
      isLoading: false,
      error: null,
      isError: false,
    });

    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Team 1')).toBeInTheDocument();
    });

    // Select 10 teams
    for (let i = 1; i <= 10; i++) {
      await user.click(screen.getByTestId(`team-card-team-${i}`));
    }

    // Try to select 11th team
    const eleventhTeamCard = screen.getByTestId('team-card-team-11');
    await user.click(eleventhTeamCard);

    // Should show warning message
    expect(screen.getByText(/maximum.*10.*teams/i)).toBeInTheDocument();
    // 11th team should not be selected
    expect(eleventhTeamCard).toHaveAttribute('data-selected', 'false');
  });

  it('displays team logos and colors correctly', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const patriotsCard = screen.getByTestId('team-card-team-1');
    const logoImg = within(patriotsCard).getByRole('img', { name: /patriots.*logo/i });

    expect(logoImg).toHaveAttribute('src', 'https://example.com/patriots.png');
    expect(logoImg).toHaveAttribute('alt', 'New England Patriots logo');
  });

  it('shows back button and handles back navigation', async () => {
    renderWithProviders(<TeamSelectionStep />);

    const backButton = screen.getByRole('button', { name: /back/i });
    expect(backButton).toBeInTheDocument();

    await user.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/2');
  });

  it('has proper accessibility attributes', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Check team cards have proper accessibility
    const patriotsCard = screen.getByTestId('team-card-team-1');
    expect(patriotsCard).toHaveAttribute('role', 'button');
    expect(patriotsCard).toHaveAttribute('tabindex', '0');
    expect(patriotsCard).toHaveAttribute('aria-selected', 'false');

    // Select the team
    await user.click(patriotsCard);
    expect(patriotsCard).toHaveAttribute('aria-selected', 'true');

    // Check affinity slider accessibility
    const affinitySlider = screen.getByTestId('affinity-slider-team-1');
    expect(affinitySlider).toHaveAttribute('aria-label', expect.stringContaining('affinity'));
    expect(affinitySlider).toHaveAttribute('role', 'slider');
  });

  it('supports keyboard navigation', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    const patriotsCard = screen.getByTestId('team-card-team-1');

    // Tab to the card and press Enter
    patriotsCard.focus();
    await user.keyboard('{Enter}');

    expect(patriotsCard).toHaveAttribute('data-selected', 'true');

    // Press Space to deselect
    await user.keyboard(' ');
    expect(patriotsCard).toHaveAttribute('data-selected', 'false');
  });

  it('persists search and filter state during interaction', async () => {
    renderWithProviders(<TeamSelectionStep />);

    await waitFor(() => {
      expect(screen.getByText('Patriots')).toBeInTheDocument();
    });

    // Set search filter
    const searchInput = screen.getByPlaceholderText(/search.*teams/i);
    await user.type(searchInput, 'Lakers');

    // Select the filtered team
    await user.click(screen.getByTestId('team-card-team-3'));

    // Clear search
    await user.clear(searchInput);

    // Lakers should still be selected
    expect(screen.getByTestId('team-card-team-3')).toHaveAttribute('data-selected', 'true');
  });

  it('handles empty teams list when no sports selected', () => {
    vi.mocked(mockUseQuery).mockReturnValue({
      data: { teams: [], total: 0 },
      isLoading: false,
      error: null,
      isError: false,
    });

    renderWithProviders(<TeamSelectionStep />);

    expect(screen.getByText(/no.*teams.*available/i)).toBeInTheDocument();
    expect(screen.getByText(/select.*sports.*first/i)).toBeInTheDocument();
  });
});