/**
 * Comprehensive Error Handling Tests for Onboarding System
 *
 * Tests all error scenarios and recovery mechanisms to ensure
 * robust error handling throughout the onboarding flow.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Test utilities
import { createMockApiClient } from '../utils/mockApiClient';
import { createMockFirebaseAuth } from '../utils/mockFirebaseAuth';

// Components under test
import { ValidatedSportsSelectionStep } from '@/components/onboarding/ValidatedSportsSelectionStep';
import { ValidatedTeamSelectionStep } from '@/components/onboarding/ValidatedTeamSelectionStep';
import { ValidatedPreferencesStep } from '@/components/onboarding/ValidatedPreferencesStep';
import { OnboardingStepErrorBoundary } from '@/components/error-boundaries/OnboardingStepErrorBoundary';

// Validation imports
import {
  validateSportsSelection,
  validateTeamSelection,
  validateContentPreferences,
} from '@/lib/validation/onboarding-schemas';

// Error reporting
import { errorReporting } from '@/lib/error-reporting';

// Test wrapper component
function TestWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

// Mock implementations
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock API client
const mockApiClient = createMockApiClient();
vi.mock('@/lib/api-client', () => ({
  createApiQueryClient: () => mockApiClient.queryConfigs,
  apiClient: mockApiClient.client,
}));

// Mock Firebase auth
const mockAuth = createMockFirebaseAuth();
vi.mock('@/contexts/FirebaseAuthContext', () => ({
  useFirebaseAuth: () => mockAuth,
}));

// Mock toast
const mockToast = vi.fn();
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast }),
}));

describe('Onboarding Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    errorReporting.clearReports();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Validation Schema Tests', () => {
    describe('Sports Selection Validation', () => {
      it('should reject empty sports selection', () => {
        const result = validateSportsSelection({ selectedSports: [] });

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['selectedSports']).toContain('Please select at least');
        }
      });

      it('should reject too many sports', () => {
        const tooManySports = Array.from({ length: 6 }, (_, i) => ({
          sportId: `sport-${i}`,
          rank: i + 1,
        }));

        const result = validateSportsSelection({ selectedSports: tooManySports });

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['selectedSports']).toContain('no more than 5');
        }
      });

      it('should reject duplicate ranks', () => {
        const duplicateRanks = [
          { sportId: 'sport-1', rank: 1 },
          { sportId: 'sport-2', rank: 1 },
        ];

        const result = validateSportsSelection({ selectedSports: duplicateRanks });

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['selectedSports']).toContain('unique rank');
        }
      });

      it('should reject non-consecutive ranks', () => {
        const nonConsecutiveRanks = [
          { sportId: 'sport-1', rank: 1 },
          { sportId: 'sport-2', rank: 3 }, // Missing rank 2
        ];

        const result = validateSportsSelection({ selectedSports: nonConsecutiveRanks });

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['selectedSports']).toContain('consecutive');
        }
      });

      it('should accept valid sports selection', () => {
        const validSports = [
          { sportId: 'nfl', rank: 1 },
          { sportId: 'nba', rank: 2 },
          { sportId: 'mlb', rank: 3 },
        ];

        const result = validateSportsSelection({ selectedSports: validSports });

        expect(result.success).toBe(true);
      });
    });

    describe('Team Selection Validation', () => {
      it('should reject empty team selection', () => {
        const result = validateTeamSelection({ selectedTeams: [] });

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['selectedTeams']).toContain('Please select at least');
        }
      });

      it('should reject too many teams', () => {
        const tooManyTeams = Array.from({ length: 11 }, (_, i) => ({
          teamId: `team-${i}`,
          sportId: 'nfl',
          rank: i + 1,
        }));

        const result = validateTeamSelection({ selectedTeams: tooManyTeams });

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['selectedTeams']).toContain('no more than 10');
        }
      });

      it('should accept valid team selection', () => {
        const validTeams = [
          { teamId: 'chiefs', sportId: 'nfl', rank: 1 },
          { teamId: 'lakers', sportId: 'nba', rank: 2 },
        ];

        const result = validateTeamSelection({ selectedTeams: validTeams });

        expect(result.success).toBe(true);
      });
    });

    describe('Content Preferences Validation', () => {
      it('should require email address when email notifications enabled', () => {
        const invalidPreferences = {
          contentFrequency: 'medium' as const,
          emailNotifications: true,
          emailAddress: '',
          pushNotifications: false,
          newsTypes: ['breaking'],
          timeZone: 'America/New_York',
        };

        const result = validateContentPreferences(invalidPreferences);

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['emailAddress']).toContain('required');
        }
      });

      it('should require at least one news type', () => {
        const invalidPreferences = {
          contentFrequency: 'medium' as const,
          emailNotifications: false,
          pushNotifications: false,
          newsTypes: [],
          timeZone: 'America/New_York',
        };

        const result = validateContentPreferences(invalidPreferences);

        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.fieldErrors['newsTypes']).toContain('at least one');
        }
      });

      it('should accept valid preferences', () => {
        const validPreferences = {
          contentFrequency: 'medium' as const,
          emailNotifications: false,
          pushNotifications: true,
          newsTypes: ['breaking', 'scores'],
          timeZone: 'America/New_York',
        };

        const result = validateContentPreferences(validPreferences);

        expect(result.success).toBe(true);
      });
    });
  });

  describe('Component Error Handling', () => {
    describe('Sports Selection Component', () => {
      it('should handle API failures gracefully', async () => {
        // Mock API failure
        mockApiClient.queryConfigs.getOnboardingSports.mockReturnValue({
          queryKey: ['sports'],
          queryFn: () => Promise.reject(new Error('API Error')),
        });

        render(
          <TestWrapper>
            <ValidatedSportsSelectionStep />
          </TestWrapper>
        );

        // Should show working offline message
        await waitFor(() => {
          expect(screen.getByText(/working offline/i)).toBeInTheDocument();
        });

        // Should still show fallback sports
        expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
      });

      it('should prevent selection of more than 5 sports', async () => {
        const user = userEvent.setup();

        render(
          <TestWrapper>
            <ValidatedSportsSelectionStep />
          </TestWrapper>
        );

        // Wait for component to load
        await waitFor(() => {
          expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
        });

        // Try to select 6 sports (should fail)
        const sportCards = screen.getAllByTestId(/sport-card-/);

        // Select first 5 sports
        for (let i = 0; i < 5; i++) {
          await user.click(sportCards[i]);
        }

        // Try to select 6th sport
        if (sportCards[5]) {
          await user.click(sportCards[5]);

          // Should show error message
          await waitFor(() => {
            expect(mockToast).toHaveBeenCalledWith(
              expect.objectContaining({
                title: 'Maximum 5 Sports',
                variant: 'destructive',
              })
            );
          });
        }
      });

      it('should show validation errors on submit', async () => {
        const user = userEvent.setup();

        render(
          <TestWrapper>
            <ValidatedSportsSelectionStep />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
        });

        // Try to continue without selecting any sports
        const continueButton = screen.getByRole('button', { name: /continue/i });
        expect(continueButton).toBeDisabled();
      });
    });

    describe('Team Selection Component', () => {
      beforeEach(() => {
        // Mock selected sports in localStorage
        localStorage.setItem('corner-league-onboarding-status', JSON.stringify({
          selectedSports: [
            { sportId: 'nfl', rank: 1 },
            { sportId: 'nba', rank: 2 },
          ]
        }));
      });

      it('should handle missing sports selection', () => {
        // Clear localStorage to simulate no sports selected
        localStorage.clear();

        render(
          <TestWrapper>
            <ValidatedTeamSelectionStep />
          </TestWrapper>
        );

        // Should show error message about no sports selected
        expect(screen.getByText(/no sports selected/i)).toBeInTheDocument();
        expect(screen.getByText(/go back to sports selection/i)).toBeInTheDocument();
      });

      it('should handle team API failures', async () => {
        // Mock API failure
        mockApiClient.queryConfigs.getOnboardingTeams.mockReturnValue({
          queryKey: ['teams'],
          queryFn: () => Promise.reject(new Error('Teams API Error')),
        });

        render(
          <TestWrapper>
            <ValidatedTeamSelectionStep />
          </TestWrapper>
        );

        // Should show working offline message
        await waitFor(() => {
          expect(screen.getByText(/working offline/i)).toBeInTheDocument();
        });

        // Should still show fallback teams
        expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
      });

      it('should prevent selection of more than 10 teams', async () => {
        const user = userEvent.setup();

        render(
          <TestWrapper>
            <ValidatedTeamSelectionStep />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText(/select your teams/i)).toBeInTheDocument();
        });

        // Get all team checkboxes
        const teamCheckboxes = screen.getAllByRole('checkbox');

        // Select first 10 teams
        for (let i = 0; i < Math.min(10, teamCheckboxes.length); i++) {
          await user.click(teamCheckboxes[i]);
        }

        // Try to select 11th team if available
        if (teamCheckboxes[10]) {
          await user.click(teamCheckboxes[10]);

          // Should show error message
          await waitFor(() => {
            expect(mockToast).toHaveBeenCalledWith(
              expect.objectContaining({
                title: 'Maximum 10 Teams',
                variant: 'destructive',
              })
            );
          });
        }
      });
    });

    describe('Preferences Component', () => {
      it('should validate email requirement', async () => {
        const user = userEvent.setup();

        render(
          <TestWrapper>
            <ValidatedPreferencesStep />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText(/set your preferences/i)).toBeInTheDocument();
        });

        // Enable email notifications
        const emailSwitch = screen.getByLabelText(/email notifications/i);
        await user.click(emailSwitch);

        // Try to continue without entering email
        const continueButton = screen.getByRole('button', { name: /continue/i });
        await user.click(continueButton);

        // Should show email validation error
        await waitFor(() => {
          expect(screen.getByText(/email address is required/i)).toBeInTheDocument();
        });
      });

      it('should validate news types requirement', async () => {
        const user = userEvent.setup();

        render(
          <TestWrapper>
            <ValidatedPreferencesStep />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByText(/set your preferences/i)).toBeInTheDocument();
        });

        // Uncheck all news types
        const newsTypeCheckboxes = screen.getAllByRole('checkbox');
        for (const checkbox of newsTypeCheckboxes) {
          if (checkbox instanceof HTMLInputElement && checkbox.checked) {
            await user.click(checkbox);
          }
        }

        // Try to continue
        const continueButton = screen.getByRole('button', { name: /continue/i });
        await user.click(continueButton);

        // Should show validation error
        await waitFor(() => {
          expect(screen.getByText(/at least one news type/i)).toBeInTheDocument();
        });
      });
    });
  });

  describe('Error Boundary Testing', () => {
    // Mock component that throws an error
    function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
      if (shouldThrow) {
        throw new Error('Test error');
      }
      return <div>Normal component</div>;
    }

    it('should catch and display errors', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <TestWrapper>
          <OnboardingStepErrorBoundary
            step={2}
            stepName="Test Step"
            onRetry={() => {}}
            onGoBack={() => {}}
            onGoHome={() => {}}
          >
            <ThrowingComponent shouldThrow={true} />
          </OnboardingStepErrorBoundary>
        </TestWrapper>
      );

      // Should show error UI
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      expect(screen.getByText(/test step/i)).toBeInTheDocument();

      // Should show retry button
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('should provide retry functionality', async () => {
      const user = userEvent.setup();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const RetryableComponent = () => {
        const [shouldThrow, setShouldThrow] = React.useState(true);

        const handleRetry = () => {
          setShouldThrow(false);
        };

        return (
          <OnboardingStepErrorBoundary
            step={2}
            stepName="Test Step"
            onRetry={handleRetry}
            onGoBack={() => {}}
            onGoHome={() => {}}
          >
            <ThrowingComponent shouldThrow={shouldThrow} />
          </OnboardingStepErrorBoundary>
        );
      };

      render(
        <TestWrapper>
          <RetryableComponent />
        </TestWrapper>
      );

      // Should show error UI initially
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

      // Click retry button
      const retryButton = screen.getByRole('button', { name: /try again/i });
      await user.click(retryButton);

      // Should show normal component after retry
      await waitFor(() => {
        expect(screen.getByText('Normal component')).toBeInTheDocument();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Recovery Mechanisms', () => {
    it('should provide clear recovery steps for API failures', async () => {
      // Mock API failure
      mockApiClient.queryConfigs.getOnboardingSports.mockReturnValue({
        queryKey: ['sports'],
        queryFn: () => Promise.reject(new Error('Network Error')),
      });

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      // Should show offline indicator with recovery guidance
      await waitFor(() => {
        expect(screen.getByText(/working offline/i)).toBeInTheDocument();
      });

      // Should still allow user to continue with fallback data
      expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
    });

    it('should save progress locally during API failures', async () => {
      const user = userEvent.setup();

      // Mock API failure for saving
      mockApiClient.client.updateOnboardingStep.mockRejectedValue(new Error('Save failed'));

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/choose your sports/i)).toBeInTheDocument();
      });

      // Select a sport
      const sportCards = screen.getAllByTestId(/sport-card-/);
      if (sportCards[0]) {
        await user.click(sportCards[0]);
      }

      // Should save to localStorage despite API failure
      const savedStatus = localStorage.getItem('corner-league-onboarding-status');
      expect(savedStatus).toBeTruthy();
    });
  });

  describe('Error Reporting', () => {
    it('should report errors to error tracking', async () => {
      // Trigger an error
      const error = new Error('Test error');

      const errorId = errorReporting.reportOnboardingError(
        2,
        'Test error message',
        error,
        { test: 'context' }
      );

      expect(errorId).toBeTruthy();

      // Verify error was recorded
      const reports = errorReporting.getReports();
      expect(reports).toHaveLength(1);
      expect(reports[0].message).toBe('Test error message');
      expect(reports[0].context.step).toBe(2);
    });

    it('should track error metrics', () => {
      // Report multiple errors
      errorReporting.reportOnboardingError(2, 'Error 1', new Error('Error 1'));
      errorReporting.reportOnboardingError(3, 'Error 2', new Error('Error 2'));
      errorReporting.reportOnboardingError(2, 'Error 1', new Error('Error 1')); // Duplicate

      const metrics = errorReporting.getMetrics();
      expect(metrics.totalErrors).toBe(3);
      expect(metrics.commonErrors).toHaveLength(2);
      expect(metrics.commonErrors[0].count).toBe(2); // Duplicate error
    });
  });

  describe('Accessibility in Error States', () => {
    it('should maintain accessibility during errors', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <TestWrapper>
          <OnboardingStepErrorBoundary
            step={2}
            stepName="Test Step"
            onRetry={() => {}}
            onGoBack={() => {}}
            onGoHome={() => {}}
          >
            <ThrowingComponent shouldThrow={true} />
          </OnboardingStepErrorBoundary>
        </TestWrapper>
      );

      // Error UI should have proper roles and labels
      const alertElement = screen.getByRole('alert', { name: /something went wrong/i });
      expect(alertElement).toBeInTheDocument();

      // Buttons should be accessible
      const retryButton = screen.getByRole('button', { name: /try again/i });
      expect(retryButton).toBeInTheDocument();
      expect(retryButton).not.toHaveAttribute('aria-disabled', 'true');

      consoleSpy.mockRestore();
    });

    it('should provide screen reader friendly error messages', () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <ValidatedSportsSelectionStep />
        </TestWrapper>
      );

      // Error messages should have proper ARIA labels
      const sportCards = screen.getAllByTestId(/sport-card-/);
      if (sportCards[0]) {
        expect(sportCards[0]).toHaveAttribute('aria-selected');
        expect(sportCards[0]).toHaveAttribute('role', 'button');
      }
    });
  });
});

// Export test utilities for use in other test files
export {
  TestWrapper,
  mockApiClient,
  mockAuth,
  createMockApiClient,
  createMockFirebaseAuth,
};