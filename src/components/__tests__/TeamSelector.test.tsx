import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TeamSelector } from '../TeamSelector';
import { apiClient, type Team } from '@/lib/api-client';

// Mock the API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    searchTeams: vi.fn(),
  },
  type: {
    Team: {},
    TeamSearchParams: {},
    TeamSearchResponse: {},
  },
}));

const mockTeams: Team[] = [
  {
    id: '1',
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
    id: '2',
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

describe('TeamSelector', () => {
  const mockOnTeamSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.searchTeams as any).mockResolvedValue({
      items: mockTeams,
      total: 2,
      page: 1,
      page_size: 50,
      has_next: false,
      has_previous: false,
    });
  });

  it('renders the team selector with placeholder text', () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[]}
        onTeamSelect={mockOnTeamSelect}
        placeholder="Select teams..."
      />
    );

    expect(screen.getByText('Select teams...')).toBeInTheDocument();
  });

  it('opens dropdown when clicked', async () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[]}
        onTeamSelect={mockOnTeamSelect}
        sportIds={['basketball-uuid']}
      />
    );

    const button = screen.getByRole('combobox');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
    });
  });

  it('searches teams with debouncing', async () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[]}
        onTeamSelect={mockOnTeamSelect}
        sportIds={['basketball-uuid']}
      />
    );

    // Open dropdown
    const button = screen.getByRole('combobox');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
    });

    // Type in search
    const searchInput = screen.getByPlaceholderText('Search for teams...');
    fireEvent.change(searchInput, { target: { value: 'Lakers' } });

    // Should search after debounce delay
    await waitFor(() => {
      expect(apiClient.searchTeams).toHaveBeenCalledWith({
        query: 'Lakers',
        sport_id: 'basketball-uuid',
        page_size: 50,
        is_active: true,
      });
    }, { timeout: 500 }); // Give more time for debouncing
  });

  it('displays team options correctly', async () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[]}
        onTeamSelect={mockOnTeamSelect}
        sportIds={['basketball-uuid']}
      />
    );

    // Open dropdown
    const button = screen.getByRole('combobox');
    fireEvent.click(button);

    // Wait for teams to load
    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
      expect(screen.getByText('Golden State Warriors')).toBeInTheDocument();
    });

    // Check team details are displayed
    expect(screen.getByText('NBA')).toBeInTheDocument();
    expect(screen.getByText('Basketball')).toBeInTheDocument();
  });

  it('selects teams correctly', async () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[]}
        onTeamSelect={mockOnTeamSelect}
        sportIds={['basketball-uuid']}
      />
    );

    // Open dropdown
    const button = screen.getByRole('combobox');
    fireEvent.click(button);

    // Wait for teams to load and click on Lakers
    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Los Angeles Lakers'));

    // Check that onTeamSelect was called with the selected team
    expect(mockOnTeamSelect).toHaveBeenCalledWith([mockTeams[0]]);
  });

  it('displays selected teams as chips', () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[mockTeams[0]]}
        onTeamSelect={mockOnTeamSelect}
      />
    );

    expect(screen.getByText('Selected Teams (1)')).toBeInTheDocument();
    expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
  });

  it('removes selected teams when X is clicked', () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[mockTeams[0]]}
        onTeamSelect={mockOnTeamSelect}
      />
    );

    const removeButton = screen.getByLabelText('Remove Los Angeles Lakers');
    fireEvent.click(removeButton);

    expect(mockOnTeamSelect).toHaveBeenCalledWith([]);
  });

  it('respects maximum selections limit', () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[mockTeams[0]]}
        onTeamSelect={mockOnTeamSelect}
        maxSelections={1}
      />
    );

    const button = screen.getByRole('combobox');
    expect(button).toHaveTextContent('Maximum teams selected');
    expect(button).toBeDisabled();
  });

  it('shows error state when API fails', async () => {
    (apiClient.searchTeams as any).mockRejectedValue(new Error('API Error'));

    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[]}
        onTeamSelect={mockOnTeamSelect}
        sportIds={['basketball-uuid']}
        error="Failed to load teams"
      />
    );

    expect(screen.getByText('Failed to load teams')).toBeInTheDocument();
  });

  it('handles single select mode', async () => {
    renderWithQueryClient(
      <TeamSelector
        selectedTeams={[]}
        onTeamSelect={mockOnTeamSelect}
        sportIds={['basketball-uuid']}
        multiSelect={false}
      />
    );

    // Open dropdown
    const button = screen.getByRole('combobox');
    fireEvent.click(button);

    // Wait for teams and select one
    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Los Angeles Lakers'));

    // Should call with single team array
    expect(mockOnTeamSelect).toHaveBeenCalledWith([mockTeams[0]]);
  });
});