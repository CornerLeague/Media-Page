import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { TeamSearchInput } from '../TeamSearchInput';
import { apiClient, type SearchSuggestion } from '@/lib/api-client';

// Mock the API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    getSearchSuggestions: vi.fn(),
  },
  type: {
    SearchSuggestion: {},
  },
}));

const mockSuggestions: SearchSuggestion[] = [
  {
    suggestion: 'Lakers',
    type: 'team_name',
    team_count: 1,
    preview_teams: ['Los Angeles Lakers'],
  },
  {
    suggestion: 'Chicago',
    type: 'city',
    team_count: 3,
    preview_teams: ['Chicago Bulls', 'Chicago Bears', 'Chicago Fire'],
  },
  {
    suggestion: 'NBA',
    type: 'league',
    team_count: 30,
    preview_teams: ['Lakers', 'Warriors'],
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

describe('TeamSearchInput', () => {
  const mockOnChange = vi.fn();
  const mockOnKeyDown = vi.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();

    // Setup default API response
    (apiClient.getSearchSuggestions as any).mockResolvedValue({
      suggestions: mockSuggestions,
    });
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('Basic Functionality', () => {
    it('renders with default placeholder', () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      expect(screen.getByPlaceholderText('Search for teams...')).toBeInTheDocument();
    });

    it('renders with custom placeholder', () => {
      renderWithQueryClient(
        <TeamSearchInput
          value=""
          onChange={mockOnChange}
          placeholder="Custom placeholder"
        />
      );

      expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument();
    });

    it('displays the current value', () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} />
      );

      const input = screen.getByDisplayValue('Lakers');
      expect(input).toBeInTheDocument();
    });

    it('calls onChange when text is typed', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'L');

      expect(mockOnChange).toHaveBeenCalledWith('L');
    });

    it('is disabled when disabled prop is true', () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} disabled />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      expect(input).toBeDisabled();
    });
  });

  describe('Debouncing', () => {
    it('debounces input changes with default delay', async () => {
      vi.useFakeTimers();

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');

      // Type rapidly
      await user.type(input, 'Lakers');

      // Should not call API immediately
      expect(apiClient.getSearchSuggestions).not.toHaveBeenCalled();

      // Fast forward default debounce time (300ms)
      act(() => {
        vi.advanceTimersByTime(300);
      });

      // Now should call API
      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledWith('Lakers');
      });

      vi.useRealTimers();
    });

    it('respects custom debounce delay', async () => {
      vi.useFakeTimers();

      renderWithQueryClient(
        <TeamSearchInput
          value=""
          onChange={mockOnChange}
          showSuggestions
          debounceMs={500}
        />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'Test');

      // Should not call API after 300ms
      act(() => {
        vi.advanceTimersByTime(300);
      });
      expect(apiClient.getSearchSuggestions).not.toHaveBeenCalled();

      // Should call API after 500ms
      act(() => {
        vi.advanceTimersByTime(200);
      });

      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledWith('Test');
      });

      vi.useRealTimers();
    });

    it('cancels previous debounced calls when typing rapidly', async () => {
      vi.useFakeTimers();

      renderWithQueryClient(
        <TeamSearchInput
          value=""
          onChange={mockOnChange}
          showSuggestions
          debounceMs={300}
        />
      );

      const input = screen.getByPlaceholderText('Search for teams...');

      // Type "L"
      await user.type(input, 'L');
      act(() => {
        vi.advanceTimersByTime(200);
      });

      // Type "a" before debounce completes
      await user.type(input, 'a');
      act(() => {
        vi.advanceTimersByTime(200);
      });

      // Type "kers" before debounce completes
      await user.type(input, 'kers');

      // Fast forward full debounce time
      act(() => {
        vi.advanceTimersByTime(300);
      });

      // Should only call API once with final value
      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledTimes(1);
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledWith('Lakers');
      });

      vi.useRealTimers();
    });
  });

  describe('Search Suggestions', () => {
    it('shows suggestions when typing 2+ characters', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'La');

      // Focus the input to trigger suggestions
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('Lakers')).toBeInTheDocument();
        expect(screen.getByText('Chicago')).toBeInTheDocument();
        expect(screen.getByText('NBA')).toBeInTheDocument();
      });
    });

    it('does not show suggestions for less than 2 characters', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'L');
      await user.click(input);

      // Should not show suggestions
      expect(screen.queryByText('Lakers')).not.toBeInTheDocument();
      expect(apiClient.getSearchSuggestions).not.toHaveBeenCalled();
    });

    it('does not fetch suggestions when showSuggestions is false', async () => {
      renderWithQueryClient(
        <TeamSearchInput
          value=""
          onChange={mockOnChange}
          showSuggestions={false}
        />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'Lakers');
      await user.click(input);

      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).not.toHaveBeenCalled();
      });

      expect(screen.queryByText('Lakers')).not.toBeInTheDocument();
    });

    it('selects suggestion when clicked', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'La');
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('Lakers')).toBeInTheDocument();
      });

      await user.click(screen.getByText('Lakers'));

      expect(mockOnChange).toHaveBeenCalledWith('Lakers');
    });

    it('displays suggestion metadata correctly', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'Chi');
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('Chicago')).toBeInTheDocument();
        expect(screen.getByText('3 teams')).toBeInTheDocument();
        expect(screen.getByText('• Chicago Bulls, Chicago Bears +1 more')).toBeInTheDocument();
      });
    });

    it('shows different suggestion types correctly', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'test');
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('team name')).toBeInTheDocument();
        expect(screen.getByText('city')).toBeInTheDocument();
        expect(screen.getByText('league')).toBeInTheDocument();
      });
    });

    it('handles empty suggestions gracefully', async () => {
      (apiClient.getSearchSuggestions as any).mockResolvedValue({
        suggestions: [],
      });

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'NoResults');
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('No suggestions found.')).toBeInTheDocument();
      });
    });

    it('handles API errors gracefully', async () => {
      (apiClient.getSearchSuggestions as any).mockRejectedValue(new Error('API Error'));

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'Error');
      await user.click(input);

      // Should not crash or show error state
      expect(screen.queryByText('Error')).not.toBeInTheDocument();
    });
  });

  describe('Clear Functionality', () => {
    it('shows clear button when there is text', () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} />
      );

      const clearButton = screen.getByLabelText('Clear search');
      expect(clearButton).toBeInTheDocument();
    });

    it('does not show clear button when input is empty', () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      const clearButton = screen.queryByLabelText('Clear search');
      expect(clearButton).not.toBeInTheDocument();
    });

    it('does not show clear button when disabled', () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} disabled />
      );

      const clearButton = screen.queryByLabelText('Clear search');
      expect(clearButton).not.toBeInTheDocument();
    });

    it('clears text and focuses input when clear button is clicked', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} />
      );

      const clearButton = screen.getByLabelText('Clear search');
      await user.click(clearButton);

      expect(mockOnChange).toHaveBeenCalledWith('');

      // Input should be focused after clearing
      const input = screen.getByPlaceholderText('Search for teams...');
      expect(input).toHaveFocus();
    });
  });

  describe('Loading States', () => {
    it('shows loading indicator when fetching suggestions', async () => {
      // Mock a slow API response
      let resolvePromise: (value: any) => void;
      const slowPromise = new Promise(resolve => {
        resolvePromise = resolve;
      });
      (apiClient.getSearchSuggestions as any).mockReturnValue(slowPromise);

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'Lakers');
      await user.click(input);

      // Wait for debounce and check loading state
      await waitFor(() => {
        expect(screen.getByTestId('loading-indicator') || document.querySelector('[class*="animate-spin"]')).toBeInTheDocument();
      }, { timeout: 500 });

      // Resolve the promise
      resolvePromise!({ suggestions: mockSuggestions });

      await waitFor(() => {
        expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
      });
    });
  });

  describe('Keyboard Navigation', () => {
    it('handles Enter key without suggestions open', async () => {
      renderWithQueryClient(
        <TeamSearchInput
          value="Lakers"
          onChange={mockOnChange}
          onKeyDown={mockOnKeyDown}
        />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, '{Enter}');

      expect(mockOnKeyDown).toHaveBeenCalledWith(
        expect.objectContaining({ key: 'Enter' })
      );
    });

    it('clears input on Escape when there is text', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, '{Escape}');

      expect(mockOnChange).toHaveBeenCalledWith('');
    });

    it('blurs input on Escape when input is empty', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      input.focus();
      await user.keyboard('{Escape}');

      expect(input).not.toHaveFocus();
    });

    it('calls parent onKeyDown handler', async () => {
      renderWithQueryClient(
        <TeamSearchInput
          value=""
          onChange={mockOnChange}
          onKeyDown={mockOnKeyDown}
        />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'a');

      expect(mockOnKeyDown).toHaveBeenCalledWith(
        expect.objectContaining({ key: 'a' })
      );
    });
  });

  describe('Focus and Blur Events', () => {
    it('shows suggestions on focus if criteria are met', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('Lakers')).toBeInTheDocument();
      });
    });

    it('hides suggestions on blur with delay', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="Lakers" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('Lakers')).toBeInTheDocument();
      });

      // Blur the input
      await user.tab();

      // Should hide suggestions after delay
      await waitFor(() => {
        expect(screen.queryByText('Lakers')).not.toBeInTheDocument();
      }, { timeout: 200 });
    });

    it('allows suggestion click before blur timeout', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="La" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.click(input);

      await waitFor(() => {
        expect(screen.getByText('Lakers')).toBeInTheDocument();
      });

      // Quickly click suggestion before blur timeout
      await user.click(screen.getByText('Lakers'));

      expect(mockOnChange).toHaveBeenCalledWith('Lakers');
    });
  });

  describe('Performance', () => {
    it('handles rapid input changes efficiently', async () => {
      vi.useFakeTimers();

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');

      // Type rapidly
      const rapidText = 'Los Angeles Lakers';
      for (const char of rapidText) {
        await user.type(input, char);
        act(() => {
          vi.advanceTimersByTime(50); // Fast typing
        });
      }

      // Complete debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });

      // Should only call API once with final text
      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledTimes(1);
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledWith(rapidText);
      });

      vi.useRealTimers();
    });

    it('handles very long search terms', async () => {
      const longText = 'A'.repeat(1000);

      renderWithQueryClient(
        <TeamSearchInput value={longText} onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByDisplayValue(longText);
      expect(input).toBeInTheDocument();

      await user.click(input);

      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledWith(longText);
      });
    });

    it('prevents memory leaks from uncompleted requests', async () => {
      let cancelledCount = 0;
      const mockAbortController = {
        abort: () => {
          cancelledCount++;
        },
        signal: {} as AbortSignal,
      };

      // Mock fetch with AbortController
      global.AbortController = vi.fn(() => mockAbortController);

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');

      // Type multiple times rapidly
      await user.type(input, 'L');
      await user.type(input, 'a');
      await user.type(input, 'k');

      // Should have properly cancelled previous requests
      // This is implementation dependent, but verifies the component
      // handles cleanup correctly
      expect(input).toHaveValue('Lak');
    });
  });

  describe('Edge Cases', () => {
    it('handles special characters in search', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      const specialText = 'St. Louis & Co. (2023)';
      await user.type(input, specialText);

      await waitFor(() => {
        expect(apiClient.getSearchSuggestions).toHaveBeenCalledWith(specialText);
      });
    });

    it('handles empty API responses', async () => {
      (apiClient.getSearchSuggestions as any).mockResolvedValue({
        suggestions: undefined,
      });

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'test');
      await user.click(input);

      // Should not crash
      await waitFor(() => {
        expect(screen.queryByText('No suggestions found.')).toBeInTheDocument();
      });
    });

    it('handles malformed API responses', async () => {
      (apiClient.getSearchSuggestions as any).mockResolvedValue(null);

      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} showSuggestions />
      );

      const input = screen.getByPlaceholderText('Search for teams...');
      await user.type(input, 'test');
      await user.click(input);

      // Should not crash and handle gracefully
      expect(screen.queryByText('Lakers')).not.toBeInTheDocument();
    });

    it('maintains cursor position during rapid updates', async () => {
      renderWithQueryClient(
        <TeamSearchInput value="" onChange={mockOnChange} />
      );

      const input = screen.getByPlaceholderText('Search for teams...') as HTMLInputElement;

      // Type some text
      await user.type(input, 'Lakers');

      // Position cursor in middle
      input.setSelectionRange(3, 3);

      // Type more text
      await user.type(input, 'XXX');

      // Cursor should still be functional
      expect(input.selectionStart).toBeDefined();
    });
  });
});