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

describe('TeamSelector Performance Tests', () => {
  const mockOnTeamSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.searchTeams as any).mockResolvedValue({
      items: mockTeams,
      total: 1,
      page: 1,
      page_size: 50,
      has_next: false,
      has_previous: false,
    });
  });

  it('should debounce search queries under 300ms', async () => {
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

    const searchInput = screen.getByPlaceholderText('Search for teams...');

    const startTime = performance.now();

    // Simulate rapid typing (should be debounced)
    fireEvent.change(searchInput, { target: { value: 'L' } });
    fireEvent.change(searchInput, { target: { value: 'La' } });
    fireEvent.change(searchInput, { target: { value: 'Lak' } });
    fireEvent.change(searchInput, { target: { value: 'Lake' } });
    fireEvent.change(searchInput, { target: { value: 'Laker' } });
    fireEvent.change(searchInput, { target: { value: 'Lakers' } });

    // Wait for the final debounced call
    await waitFor(() => {
      expect(apiClient.searchTeams).toHaveBeenCalledWith({
        query: 'Lakers',
        sport_id: 'basketball-uuid',
        page_size: 50,
        is_active: true,
      });
    }, { timeout: 500 });

    const endTime = performance.now();
    const searchDuration = endTime - startTime;

    // Should call API only once after debounce period
    expect(apiClient.searchTeams).toHaveBeenCalledTimes(1);

    // Debounce should complete within 300ms tolerance
    expect(searchDuration).toBeLessThan(600); // 300ms debounce + 300ms tolerance
  });

  it('should not make multiple API calls for rapid typing', async () => {
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

    const searchInput = screen.getByPlaceholderText('Search for teams...');

    // Simulate very rapid typing
    const queries = ['L', 'La', 'Lak', 'Lake', 'Laker', 'Lakers'];

    queries.forEach((query, index) => {
      setTimeout(() => {
        fireEvent.change(searchInput, { target: { value: query } });
      }, index * 50); // 50ms intervals (faster than 300ms debounce)
    });

    // Wait for debounce period plus buffer
    await new Promise(resolve => setTimeout(resolve, 400));

    // Should only call API once with the final query
    await waitFor(() => {
      expect(apiClient.searchTeams).toHaveBeenCalledTimes(1);
    });

    expect(apiClient.searchTeams).toHaveBeenCalledWith({
      query: 'Lakers',
      sport_id: 'basketball-uuid',
      page_size: 50,
      is_active: true,
    });
  });

  it('should handle search performance under load', async () => {
    // Mock a slower API response to simulate network conditions
    (apiClient.searchTeams as any).mockImplementation(() =>
      new Promise(resolve =>
        setTimeout(() => resolve({
          items: mockTeams,
          total: 1,
          page: 1,
          page_size: 50,
          has_next: false,
          has_previous: false,
        }), 100) // 100ms simulated network delay
      )
    );

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

    const searchInput = screen.getByPlaceholderText('Search for teams...');

    const startTime = performance.now();

    // Type search query
    fireEvent.change(searchInput, { target: { value: 'Lakers' } });

    // Wait for search results
    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    }, { timeout: 1000 });

    const endTime = performance.now();
    const totalDuration = endTime - startTime;

    // Total search response time should be reasonable (debounce + network + render)
    expect(totalDuration).toBeLessThan(800); // 300ms debounce + 100ms network + 400ms buffer
  });

  it('should maintain UI responsiveness during search', async () => {
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

    const searchInput = screen.getByPlaceholderText('Search for teams...');

    // Type in search input
    fireEvent.change(searchInput, { target: { value: 'Lakers' } });

    // UI should show the loading state immediately
    expect(searchInput).toHaveValue('Lakers');

    // Should show searching state
    await waitFor(() => {
      expect(screen.getByText('Searching teams...')).toBeInTheDocument();
    }, { timeout: 100 });

    // Results should appear after debounce
    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    }, { timeout: 600 });
  });
});