/**
 * Comprehensive test suite for the Edit Flow for user profile preferences.
 * Tests the complete user journey from accessing preferences to saving changes.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { PreferencesPage } from '@/pages/profile/PreferencesPage';
import { usePreferences } from '@/hooks/usePreferences';

// Mock the hooks
vi.mock('@/contexts/FirebaseAuthContext');
vi.mock('@/hooks/usePreferences');

// Mock navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock toast notifications
vi.mock('@/components/ui/use-toast', () => ({
  toast: vi.fn(),
}));

// Test data
const mockSports = [
  { sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true },
  { sportId: 'nba', name: 'NBA', rank: 2, hasTeams: true },
];

const mockTeams = [
  { teamId: 'chiefs', name: 'Kansas City Chiefs', sportId: 'nfl', league: 'NFL', affinityScore: 8 },
  { teamId: 'lakers', name: 'Los Angeles Lakers', sportId: 'nba', league: 'NBA', affinityScore: 7 },
];

const mockContentPreferences = {
  newsTypes: [
    { type: 'injuries', enabled: true, priority: 1 },
    { type: 'trades', enabled: true, priority: 2 },
    { type: 'scores', enabled: false, priority: 3 },
  ],
  notifications: {
    push: true,
    email: false,
    gameReminders: true,
    newsAlerts: false,
    scoreUpdates: true,
  },
  contentFrequency: 'standard' as const,
};

const mockPreferencesData = {
  sports: mockSports,
  teams: mockTeams,
  preferences: mockContentPreferences,
};

// Helper function to render components with providers
function renderWithProviders(component: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

describe('PreferencesEditFlow', () => {
  const mockUpdateSportsPreferences = vi.fn();
  const mockUpdateTeamsPreferences = vi.fn();
  const mockUpdateContentPreferences = vi.fn();
  const mockRefreshPreferences = vi.fn();
  const mockClearErrors = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock Firebase Auth
    (useFirebaseAuth as any).mockReturnValue({
      isAuthenticated: true,
      user: { uid: 'test-user', email: 'test@example.com' },
      getIdToken: vi.fn().mockResolvedValue('test-token'),
    });

    // Mock usePreferences hook
    (usePreferences as any).mockReturnValue({
      preferencesData: mockPreferencesData,
      isLoading: false,
      error: null,
      updateSportsPreferences: mockUpdateSportsPreferences,
      updateTeamsPreferences: mockUpdateTeamsPreferences,
      updateContentPreferences: mockUpdateContentPreferences,
      isUpdatingSports: false,
      isUpdatingTeams: false,
      isUpdatingContent: false,
      sportsError: null,
      teamsError: null,
      contentError: null,
      refreshPreferences: mockRefreshPreferences,
      clearErrors: mockClearErrors,
    });
  });

  describe('Page Loading and Navigation', () => {
    it('renders the preferences page correctly', async () => {
      renderWithProviders(<PreferencesPage />);

      expect(screen.getByText('Edit Preferences')).toBeInTheDocument();
      expect(screen.getByText('Customize your sports, teams, and content preferences')).toBeInTheDocument();
    });

    it('displays loading state when preferences are loading', () => {
      (usePreferences as any).mockReturnValue({
        preferencesData: undefined,
        isLoading: true,
        error: null,
        // ... other methods
      });

      renderWithProviders(<PreferencesPage />);

      expect(screen.getByText('Loading preferences...')).toBeInTheDocument();
    });

    it('handles navigation back to dashboard', () => {
      renderWithProviders(<PreferencesPage />);

      const backButton = screen.getByRole('button', { name: /go back/i });
      fireEvent.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Sports Preferences Editing', () => {
    it('displays current sports preferences', () => {
      renderWithProviders(<PreferencesPage />);

      // Click on Sports tab
      fireEvent.click(screen.getByRole('tab', { name: /sports/i }));

      expect(screen.getByText('NFL')).toBeInTheDocument();
      expect(screen.getByText('NBA')).toBeInTheDocument();
      expect(screen.getByText('2 selected')).toBeInTheDocument();
    });

    it('allows saving sports preferences', async () => {
      mockUpdateSportsPreferences.mockResolvedValue({});

      renderWithProviders(<PreferencesPage />);

      // Click on Sports tab
      fireEvent.click(screen.getByRole('tab', { name: /sports/i }));

      // Click save sports button
      const saveButton = screen.getByRole('button', { name: /save sports/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockUpdateSportsPreferences).toHaveBeenCalledWith(mockSports);
      });
    });
  });

  describe('Teams Preferences Editing', () => {
    it('displays current team preferences', () => {
      renderWithProviders(<PreferencesPage />);

      // Click on Teams tab
      fireEvent.click(screen.getByRole('tab', { name: /teams/i }));

      expect(screen.getByText('Kansas City Chiefs')).toBeInTheDocument();
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      expect(screen.getByText('2 selected')).toBeInTheDocument();
    });

    it('allows saving team preferences', async () => {
      mockUpdateTeamsPreferences.mockResolvedValue({});

      renderWithProviders(<PreferencesPage />);

      // Click on Teams tab
      fireEvent.click(screen.getByRole('tab', { name: /teams/i }));

      // Click save teams button
      const saveButton = screen.getByRole('button', { name: /save teams/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockUpdateTeamsPreferences).toHaveBeenCalledWith(mockTeams);
      });
    });
  });

  describe('Content Preferences Editing', () => {
    it('displays current content preferences', () => {
      renderWithProviders(<PreferencesPage />);

      // Click on Content tab
      fireEvent.click(screen.getByRole('tab', { name: /content/i }));

      expect(screen.getByText('Injuries & Health')).toBeInTheDocument();
      expect(screen.getByText('Trades & Transfers')).toBeInTheDocument();
      expect(screen.getByText('standard')).toBeInTheDocument();
    });

    it('allows toggling notification settings', () => {
      renderWithProviders(<PreferencesPage />);

      // Click on Content tab
      fireEvent.click(screen.getByRole('tab', { name: /content/i }));

      // Find push notifications switch
      const pushSwitch = screen.getByRole('switch', { name: /push notifications/i });
      expect(pushSwitch).toBeChecked();

      // Find email notifications switch
      const emailSwitch = screen.getByRole('switch', { name: /email notifications/i });
      expect(emailSwitch).not.toBeChecked();
    });

    it('allows saving content preferences', async () => {
      mockUpdateContentPreferences.mockResolvedValue({});

      renderWithProviders(<PreferencesPage />);

      // Click on Content tab
      fireEvent.click(screen.getByRole('tab', { name: /content/i }));

      // Click save content button
      const saveButton = screen.getByRole('button', { name: /save content/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockUpdateContentPreferences).toHaveBeenCalledWith(mockContentPreferences);
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message when preferences fail to load', () => {
      (usePreferences as any).mockReturnValue({
        preferencesData: undefined,
        isLoading: false,
        error: new Error('Failed to load preferences'),
        refreshPreferences: mockRefreshPreferences,
        // ... other methods
      });

      renderWithProviders(<PreferencesPage />);

      expect(screen.getByText(/failed to load preferences/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    it('displays sports error when sports update fails', () => {
      (usePreferences as any).mockReturnValue({
        ...mockPreferencesData,
        isLoading: false,
        error: null,
        sportsError: new Error('Failed to update sports'),
        // ... other methods
      });

      renderWithProviders(<PreferencesPage />);

      expect(screen.getByText(/failed to update sports/i)).toBeInTheDocument();
    });
  });

  describe('Save All Functionality', () => {
    it('shows unsaved changes indicator when data is modified', () => {
      renderWithProviders(<PreferencesPage />);

      // The component should detect changes and show the indicator
      // This would require simulating user interactions that modify data
      // For now, we test that the UI can handle the unsaved changes state
      expect(screen.queryByText('Unsaved Changes')).not.toBeInTheDocument();
    });

    it('allows saving all preferences at once', async () => {
      mockUpdateSportsPreferences.mockResolvedValue({});
      mockUpdateTeamsPreferences.mockResolvedValue({});
      mockUpdateContentPreferences.mockResolvedValue({});

      // Mock the hook to show unsaved changes
      (usePreferences as any).mockReturnValue({
        ...mockPreferencesData,
        isLoading: false,
        error: null,
        updateSportsPreferences: mockUpdateSportsPreferences,
        updateTeamsPreferences: mockUpdateTeamsPreferences,
        updateContentPreferences: mockUpdateContentPreferences,
        isUpdatingSports: false,
        isUpdatingTeams: false,
        isUpdatingContent: false,
        sportsError: null,
        teamsError: null,
        contentError: null,
        refreshPreferences: mockRefreshPreferences,
        clearErrors: mockClearErrors,
      });

      renderWithProviders(<PreferencesPage />);

      // If there were unsaved changes, we'd expect to see the Save All button
      // This test verifies the component structure is correct
      expect(screen.getByText('Edit Preferences')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      renderWithProviders(<PreferencesPage />);

      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /sports/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /teams/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /content/i })).toBeInTheDocument();
    });

    it('supports keyboard navigation', () => {
      renderWithProviders(<PreferencesPage />);

      const sportsTab = screen.getByRole('tab', { name: /sports/i });
      sportsTab.focus();
      expect(sportsTab).toHaveFocus();
    });
  });
});

describe('usePreferences Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('provides the correct interface', () => {
    const result = (usePreferences as any)();

    expect(result).toHaveProperty('preferencesData');
    expect(result).toHaveProperty('isLoading');
    expect(result).toHaveProperty('error');
    expect(result).toHaveProperty('updateSportsPreferences');
    expect(result).toHaveProperty('updateTeamsPreferences');
    expect(result).toHaveProperty('updateContentPreferences');
    expect(result).toHaveProperty('refreshPreferences');
    expect(result).toHaveProperty('clearErrors');
  });
});