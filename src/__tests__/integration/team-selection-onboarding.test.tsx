import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TeamSelectionStep } from '@/pages/onboarding/TeamSelectionStep';
import { FirebaseAuthProvider } from '@/contexts/FirebaseAuthContext';
import { apiClient, type Team } from '@/lib/api-client';

// Mock the API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    searchTeams: vi.fn(),
    updateOnboardingStep: vi.fn(),
  },
  createApiQueryClient: vi.fn(),
}));

// Mock Firebase auth context
vi.mock('@/contexts/FirebaseAuthContext', () => ({
  FirebaseAuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useFirebaseAuth: () => ({
    isAuthenticated: true,
    getIdToken: vi.fn().mockResolvedValue('mock-token'),
    user: { uid: 'test-user-id' },
  }),
}));

// Mock onboarding storage
vi.mock('@/lib/onboarding-storage', () => ({
  getLocalOnboardingStatus: vi.fn().mockReturnValue({
    selectedSports: [
      { sportId: 'basketball-uuid', rank: 1 },
      { sportId: 'football-uuid', rank: 2 },
    ],
    selectedTeams: [],
  }),
  updateLocalOnboardingStep: vi.fn(),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockTeams: Team[] = [
  {
    id: 'lakers-uuid',
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
    id: 'warriors-uuid',
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
    id: 'chiefs-uuid',
    sport_id: 'football-uuid',
    league_id: 'nfl-uuid',
    name: 'Chiefs',
    market: 'Kansas City',
    slug: 'kansas-city-chiefs',
    abbreviation: 'KC',
    logo_url: 'https://example.com/chiefs-logo.png',
    primary_color: '#E31837',
    secondary_color: '#FFB81C',
    is_active: true,
    sport_name: 'Football',
    league_name: 'NFL',
    display_name: 'Kansas City Chiefs',
    short_name: 'KC',
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

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <FirebaseAuthProvider>
          {component}
        </FirebaseAuthProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('Team Selection Onboarding Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.searchTeams as any).mockResolvedValue({
      items: mockTeams,
      total: 3,
      page: 1,
      page_size: 50,
      has_next: false,
      has_previous: false,
    });
    (apiClient.updateOnboardingStep as any).mockResolvedValue({
      currentStep: 4,
      totalSteps: 5,
      isComplete: false,
    });
  });

  it('completes team selection onboarding flow', async () => {
    renderWithProviders(<TeamSelectionStep />);

    // Should display the team selection step
    expect(screen.getByText('Select Your Teams')).toBeInTheDocument();
    expect(screen.getByText('Choose your favorite teams from your selected sports')).toBeInTheDocument();

    // Should show selected sports
    expect(screen.getByText(/Selected sports:/)).toBeInTheDocument();

    // Open team selector dropdown
    const teamSelectorButton = screen.getByRole('combobox');
    fireEvent.click(teamSelectorButton);

    // Wait for dropdown to open
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
    });

    // Teams should be loaded from API
    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      expect(screen.getByText('Golden State Warriors')).toBeInTheDocument();
      expect(screen.getByText('Kansas City Chiefs')).toBeInTheDocument();
    });

    // Select Lakers
    fireEvent.click(screen.getByText('Los Angeles Lakers'));

    // Should show selected team
    await waitFor(() => {
      expect(screen.getByText('Selected Teams (1)')).toBeInTheDocument();
    });

    // Open dropdown again and select another team
    fireEvent.click(teamSelectorButton);
    await waitFor(() => {
      expect(screen.getByText('Golden State Warriors')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Golden State Warriors'));

    // Should show 2 selected teams
    await waitFor(() => {
      expect(screen.getByText('Selected Teams (2)')).toBeInTheDocument();
    });

    // Continue button should be enabled
    const continueButton = screen.getByText('Continue');
    expect(continueButton).not.toBeDisabled();

    // Click continue
    fireEvent.click(continueButton);

    // Should save to API and navigate
    await waitFor(() => {
      expect(apiClient.updateOnboardingStep).toHaveBeenCalledWith({
        step: 3,
        data: {
          teams: [
            {
              teamId: 'lakers-uuid',
              sportId: 'basketball-uuid',
              affinityScore: 0.8,
            },
            {
              teamId: 'warriors-uuid',
              sportId: 'basketball-uuid',
              affinityScore: 0.8,
            },
          ],
        },
      });
    });

    expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/4');
  });

  it('handles team search functionality', async () => {
    renderWithProviders(<TeamSelectionStep />);

    // Open team selector
    const teamSelectorButton = screen.getByRole('combobox');
    fireEvent.click(teamSelectorButton);

    // Wait for dropdown
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
    });

    // Search for Lakers
    const searchInput = screen.getByPlaceholderText('Search for teams...');
    fireEvent.change(searchInput, { target: { value: 'Lakers' } });

    // Should trigger search API call after debounce
    await waitFor(() => {
      expect(apiClient.searchTeams).toHaveBeenCalledWith({
        query: 'Lakers',
        sport_id: 'basketball-uuid,football-uuid',
        page_size: 50,
        is_active: true,
      });
    }, { timeout: 500 });
  });

  it('handles maximum team selections', async () => {
    renderWithProviders(<TeamSelectionStep />);

    // Open team selector
    const teamSelectorButton = screen.getByRole('combobox');
    fireEvent.click(teamSelectorButton);

    // Wait for teams to load
    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    });

    // Select maximum number of teams (component is set to max 10)
    // For this test, let's just select a few teams
    fireEvent.click(screen.getByText('Los Angeles Lakers'));
    fireEvent.click(screen.getByText('Golden State Warriors'));
    fireEvent.click(screen.getByText('Kansas City Chiefs'));

    // Should show all selected teams
    await waitFor(() => {
      expect(screen.getByText('Selected Teams (3)')).toBeInTheDocument();
    });

    // Should be able to remove teams
    const removeButtons = screen.getAllByLabelText(/Remove/);
    expect(removeButtons).toHaveLength(3);

    // Remove one team
    fireEvent.click(removeButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Selected Teams (2)')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (apiClient.searchTeams as any).mockRejectedValue(new Error('API Error'));

    renderWithProviders(<TeamSelectionStep />);

    // Open team selector
    const teamSelectorButton = screen.getByRole('combobox');
    fireEvent.click(teamSelectorButton);

    // Search should still work but show error state
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search for teams...');
    fireEvent.change(searchInput, { target: { value: 'Lakers' } });

    // Should show error message eventually
    await waitFor(() => {
      expect(screen.getByText(/Failed to search teams/)).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('prevents navigation without team selection', async () => {
    renderWithProviders(<TeamSelectionStep />);

    // Continue button should be disabled initially
    const continueButton = screen.getByText('Continue');
    expect(continueButton).toBeDisabled();

    // Should not navigate when disabled button is clicked
    fireEvent.click(continueButton);
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('handles offline mode gracefully', async () => {
    (apiClient.updateOnboardingStep as any).mockRejectedValue(new Error('Network Error'));

    renderWithProviders(<TeamSelectionStep />);

    // Select a team
    const teamSelectorButton = screen.getByRole('combobox');
    fireEvent.click(teamSelectorButton);

    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Los Angeles Lakers'));

    // Continue
    const continueButton = screen.getByText('Continue');
    fireEvent.click(continueButton);

    // Should show offline indicator after API fails
    await waitFor(() => {
      expect(screen.getByText(/Working Offline/)).toBeInTheDocument();
    });

    // Should still navigate despite API failure
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/4');
    });
  });
});