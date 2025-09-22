/**
 * Tests for CompletionStep component
 * Tests onboarding completion, summary display, navigation to dashboard
 */

import { screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { renderWithProviders } from '@/test-setup';
import { CompletionStep } from '@/pages/onboarding/CompletionStep';

// Mock the navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ step: '5' }),
  };
});

// Mock API client
const mockCompleteOnboarding = vi.fn();

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    completeOnboarding: mockCompleteOnboarding,
  },
}));

// Mock React Query
const mockUseMutation = vi.fn();
const mockUseQuery = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useMutation: mockUseMutation,
    useQuery: mockUseQuery,
  };
});

// Mock confetti for celebration effect
vi.mock('canvas-confetti', () => ({
  default: vi.fn(),
}));

const mockOnboardingData = {
  selectedSports: [
    { sportId: 'sport-1', name: 'Football', rank: 1 },
    { sportId: 'sport-2', name: 'Basketball', rank: 2 },
  ],
  selectedTeams: [
    { teamId: 'team-1', name: 'Patriots', market: 'New England', affinityScore: 9 },
    { teamId: 'team-2', name: 'Lakers', market: 'Los Angeles', affinityScore: 8 },
  ],
  preferences: {
    newsTypes: [
      { type: 'injuries', enabled: true, priority: 5 },
      { type: 'trades', enabled: true, priority: 4 },
    ],
    notifications: {
      push: true,
      email: true,
      gameReminders: true,
      newsAlerts: false,
      scoreUpdates: true,
    },
    contentFrequency: 'standard',
  },
};

describe('CompletionStep', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockNavigate.mockClear();
    mockCompleteOnboarding.mockClear();
    vi.clearAllMocks();

    // Mock successful query for onboarding data
    mockUseQuery.mockReturnValue({
      data: mockOnboardingData,
      isLoading: false,
      error: null,
      isError: false,
    });

    // Mock successful completion mutation
    mockUseMutation.mockReturnValue({
      mutate: mockCompleteOnboarding,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: false,
    });
  });

  it('renders completion interface', () => {
    renderWithProviders(<CompletionStep />);

    expect(screen.getByText('Step 5 of 5')).toBeInTheDocument();
    expect(screen.getByText(/complete/i)).toBeInTheDocument();
    expect(screen.getByText(/congratulations/i)).toBeInTheDocument();
  });

  it('displays onboarding summary', () => {
    renderWithProviders(<CompletionStep />);

    expect(screen.getByText(/summary/i)).toBeInTheDocument();

    // Check sports summary
    expect(screen.getByText('Football')).toBeInTheDocument();
    expect(screen.getByText('Basketball')).toBeInTheDocument();

    // Check teams summary
    expect(screen.getByText('New England Patriots')).toBeInTheDocument();
    expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();

    // Check preferences summary
    expect(screen.getByText(/injuries.*enabled/i)).toBeInTheDocument();
    expect(screen.getByText(/trades.*enabled/i)).toBeInTheDocument();
    expect(screen.getByText(/standard.*frequency/i)).toBeInTheDocument();
  });

  it('shows progress bar at 100%', () => {
    renderWithProviders(<CompletionStep />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '100');
    expect(screen.getByText('100% complete')).toBeInTheDocument();
  });

  it('displays complete onboarding button', () => {
    renderWithProviders(<CompletionStep />);

    const completeButton = screen.getByRole('button', { name: /complete.*onboarding/i });
    expect(completeButton).toBeInTheDocument();
    expect(completeButton).not.toBeDisabled();
  });

  it('shows back button for final review', () => {
    renderWithProviders(<CompletionStep />);

    const backButton = screen.getByRole('button', { name: /back/i });
    expect(backButton).toBeInTheDocument();

    // Should have different label indicating review
    expect(screen.getByText(/review.*preferences/i)).toBeInTheDocument();
  });

  it('completes onboarding and navigates to dashboard', async () => {
    mockCompleteOnboarding.mockResolvedValue({
      success: true,
      userId: 'user-123',
      onboardingCompletedAt: new Date().toISOString(),
    });

    renderWithProviders(<CompletionStep />);

    const completeButton = screen.getByRole('button', { name: /complete.*onboarding/i });
    await user.click(completeButton);

    await waitFor(() => {
      expect(mockCompleteOnboarding).toHaveBeenCalledWith({
        sports: mockOnboardingData.selectedSports,
        teams: mockOnboardingData.selectedTeams,
        preferences: mockOnboardingData.preferences,
      });
    });

    // Should show success message and then navigate
    await waitFor(() => {
      expect(screen.getByText(/onboarding.*complete/i)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    }, { timeout: 3000 });
  });

  it('handles completion API error', async () => {
    mockCompleteOnboarding.mockRejectedValue(new Error('Completion failed'));

    mockUseMutation.mockReturnValue({
      mutate: mockCompleteOnboarding,
      isLoading: false,
      error: new Error('Completion failed'),
      isError: true,
      isSuccess: false,
    });

    renderWithProviders(<CompletionStep />);

    const completeButton = screen.getByRole('button', { name: /complete.*onboarding/i });
    await user.click(completeButton);

    await waitFor(() => {
      expect(screen.getByText(/error.*completing.*onboarding/i)).toBeInTheDocument();
    });

    // Should show retry button
    expect(screen.getByRole('button', { name: /try.*again/i })).toBeInTheDocument();
  });

  it('shows loading state during completion', () => {
    mockUseMutation.mockReturnValue({
      mutate: mockCompleteOnboarding,
      isLoading: true,
      error: null,
      isError: false,
      isSuccess: false,
    });

    renderWithProviders(<CompletionStep />);

    const completeButton = screen.getByRole('button', { name: /complete.*onboarding/i });
    expect(completeButton).toBeDisabled();
    expect(screen.getByText(/completing/i)).toBeInTheDocument();
  });

  it('displays success animation after completion', async () => {
    mockCompleteOnboarding.mockResolvedValue({ success: true });

    mockUseMutation.mockReturnValue({
      mutate: mockCompleteOnboarding,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
    });

    renderWithProviders(<CompletionStep />);

    // Should show success animation/confetti
    expect(screen.getByTestId('success-animation')).toBeInTheDocument();
  });

  it('allows editing selections via back navigation', async () => {
    renderWithProviders(<CompletionStep />);

    const backButton = screen.getByRole('button', { name: /back/i });
    await user.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/4');
  });

  it('shows detailed sport preferences in summary', () => {
    renderWithProviders(<CompletionStep />);

    const sportsSection = screen.getByTestId('sports-summary');

    // Should show sports in rank order
    const sportItems = within(sportsSection).getAllByTestId(/sport-item-/);
    expect(sportItems).toHaveLength(2);

    expect(within(sportItems[0]).getByText('1st')).toBeInTheDocument();
    expect(within(sportItems[0]).getByText('Football')).toBeInTheDocument();

    expect(within(sportItems[1]).getByText('2nd')).toBeInTheDocument();
    expect(within(sportItems[1]).getByText('Basketball')).toBeInTheDocument();
  });

  it('shows detailed team preferences with affinity scores', () => {
    renderWithProviders(<CompletionStep />);

    const teamsSection = screen.getByTestId('teams-summary');

    // Should show teams with affinity scores
    expect(within(teamsSection).getByText(/patriots.*9\/10/i)).toBeInTheDocument();
    expect(within(teamsSection).getByText(/lakers.*8\/10/i)).toBeInTheDocument();
  });

  it('shows notification preferences summary', () => {
    renderWithProviders(<CompletionStep />);

    const notificationsSection = screen.getByTestId('notifications-summary');

    // Should show enabled notifications
    expect(within(notificationsSection).getByText(/push.*enabled/i)).toBeInTheDocument();
    expect(within(notificationsSection).getByText(/email.*enabled/i)).toBeInTheDocument();
    expect(within(notificationsSection).getByText(/game.*reminders.*enabled/i)).toBeInTheDocument();
    expect(within(notificationsSection).getByText(/score.*updates.*enabled/i)).toBeInTheDocument();

    // Should show disabled notifications
    expect(within(notificationsSection).getByText(/news.*alerts.*disabled/i)).toBeInTheDocument();
  });

  it('provides edit links for each section', () => {
    renderWithProviders(<CompletionStep />);

    expect(screen.getByRole('link', { name: /edit.*sports/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /edit.*teams/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /edit.*preferences/i })).toBeInTheDocument();
  });

  it('handles edit link navigation', async () => {
    renderWithProviders(<CompletionStep />);

    const editSportsLink = screen.getByRole('link', { name: /edit.*sports/i });
    await user.click(editSportsLink);

    expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/2');
  });

  it('displays estimated completion time', () => {
    renderWithProviders(<CompletionStep />);

    expect(screen.getByText(/completed.*in.*\d+.*minutes?/i)).toBeInTheDocument();
  });

  it('shows personalized welcome message', () => {
    renderWithProviders(<CompletionStep />);

    // Should include user's top sport/team in welcome message
    expect(screen.getByText(/ready.*football/i)).toBeInTheDocument();
    expect(screen.getByText(/patriots.*fan/i)).toBeInTheDocument();
  });

  it('has proper accessibility structure', () => {
    renderWithProviders(<CompletionStep />);

    // Check main heading
    const mainHeading = screen.getByRole('heading', { level: 1 });
    expect(mainHeading).toHaveTextContent(/congratulations/i);

    // Check section headings
    expect(screen.getByRole('heading', { name: /summary/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /sports/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /teams/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /preferences/i })).toBeInTheDocument();

    // Check progress bar accessibility
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-label', expect.stringContaining('completion'));
  });

  it('supports keyboard navigation', async () => {
    renderWithProviders(<CompletionStep />);

    const completeButton = screen.getByRole('button', { name: /complete.*onboarding/i });
    const backButton = screen.getByRole('button', { name: /back/i });

    // Tab navigation
    backButton.focus();
    expect(backButton).toHaveFocus();

    await user.keyboard('{Tab}');
    expect(completeButton).toHaveFocus();

    // Enter to activate
    mockCompleteOnboarding.mockResolvedValue({ success: true });
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(mockCompleteOnboarding).toHaveBeenCalled();
    });
  });

  it('prevents multiple completion attempts', async () => {
    mockCompleteOnboarding.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
    );

    renderWithProviders(<CompletionStep />);

    const completeButton = screen.getByRole('button', { name: /complete.*onboarding/i });

    // Click multiple times rapidly
    await user.click(completeButton);
    await user.click(completeButton);
    await user.click(completeButton);

    // Should only call API once
    await waitFor(() => {
      expect(mockCompleteOnboarding).toHaveBeenCalledTimes(1);
    });
  });

  it('handles loading state for onboarding data', () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      isError: false,
    });

    renderWithProviders(<CompletionStep />);

    expect(screen.getByTestId('loading-summary')).toBeInTheDocument();
  });

  it('handles error state for onboarding data', () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to load data'),
      isError: true,
    });

    renderWithProviders(<CompletionStep />);

    expect(screen.getByText(/error.*loading.*summary/i)).toBeInTheDocument();
  });

  it('shows skip option for quick completion', async () => {
    renderWithProviders(<CompletionStep />);

    const skipButton = screen.getByRole('button', { name: /skip.*dashboard/i });
    expect(skipButton).toBeInTheDocument();

    await user.click(skipButton);

    // Should force complete and navigate immediately
    await waitFor(() => {
      expect(mockCompleteOnboarding).toHaveBeenCalledWith(
        expect.objectContaining({ force_complete: true })
      );
    });
  });

  it('validates required data before completion', async () => {
    // Mock incomplete data
    mockUseQuery.mockReturnValue({
      data: {
        selectedSports: [],
        selectedTeams: [],
        preferences: null,
      },
      isLoading: false,
      error: null,
      isError: false,
    });

    renderWithProviders(<CompletionStep />);

    const completeButton = screen.getByRole('button', { name: /complete.*onboarding/i });
    await user.click(completeButton);

    // Should show validation error
    expect(screen.getByText(/complete.*required.*steps/i)).toBeInTheDocument();
    expect(mockCompleteOnboarding).not.toHaveBeenCalled();
  });

  it('shows celebration message after successful completion', async () => {
    mockCompleteOnboarding.mockResolvedValue({ success: true });

    mockUseMutation.mockReturnValue({
      mutate: mockCompleteOnboarding,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
    });

    renderWithProviders(<CompletionStep />);

    expect(screen.getByText(/welcome.*corner.*league/i)).toBeInTheDocument();
    expect(screen.getByText(/redirecting.*dashboard/i)).toBeInTheDocument();
  });
});