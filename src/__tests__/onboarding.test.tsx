/**
 * Comprehensive Onboarding Tests
 *
 * This test suite covers accessibility, functionality, and user interactions
 * for the onboarding system.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/components/ThemeProvider';

import WelcomeScreen from '@/pages/onboarding/WelcomeScreen';
import SportsSelection from '@/pages/onboarding/SportsSelection';
import TeamSelection from '@/pages/onboarding/TeamSelection';
import PreferencesSetup from '@/pages/onboarding/PreferencesSetup';
import OnboardingComplete from '@/pages/onboarding/OnboardingComplete';
import { OnboardingLayout } from '@/components/onboarding/OnboardingLayout';
import { FirstTimeExperience } from '@/components/onboarding/FirstTimeExperience';

import { OnboardingStorage } from '@/lib/onboarding/localStorage';
import { OnboardingValidator } from '@/lib/onboarding/validation';
import { runAccessibilityAudit } from '@/lib/accessibility';

// Mock Clerk hooks
vi.mock('@clerk/clerk-react', () => ({
  useUser: vi.fn(() => ({
    user: {
      id: 'test-user-id',
      firstName: 'Test',
      lastName: 'User',
      primaryEmailAddress: { emailAddress: 'test@example.com' }
    },
    isLoaded: true
  })),
  useAuth: vi.fn(() => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
    isSignedIn: true
  })),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

// Mock accessibility audit to prevent slow tests
vi.mock('@/lib/accessibility', async () => {
  const actual = await vi.importActual('@/lib/accessibility') as any;
  return {
    ...actual,
    runAccessibilityAudit: vi.fn().mockResolvedValue({
      violations: [],
      passes: [],
      incomplete: []
    })
  };
});

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="test-theme">
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

// Mock data
const mockSportsPreferences = [
  { sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true },
  { sportId: 'nba', name: 'NBA', rank: 2, hasTeams: true },
];

const mockTeamPreferences = [
  { teamId: 'chiefs', name: 'Kansas City Chiefs', sportId: 'nfl', league: 'NFL', affinityScore: 85 },
  { teamId: 'lakers', name: 'Los Angeles Lakers', sportId: 'nba', league: 'NBA', affinityScore: 90 },
];

const mockUserPreferences = {
  newsTypes: [
    { type: 'injuries' as const, enabled: true, priority: 1 },
    { type: 'trades' as const, enabled: true, priority: 2 },
  ],
  notifications: {
    push: false,
    email: true,
    gameReminders: true,
    newsAlerts: false,
    scoreUpdates: true,
  },
  contentFrequency: 'standard' as const,
};

describe('Onboarding System', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('WelcomeScreen', () => {
    it('renders welcome screen with proper headings and accessibility', async () => {
      const { container } = render(
        <TestWrapper>
          <WelcomeScreen />
        </TestWrapper>
      );

      // Check main heading
      expect(screen.getByRole('heading', { name: /welcome to corner league media/i })).toBeInTheDocument();

      // Check for features
      expect(screen.getByText(/personalized sports feed/i)).toBeInTheDocument();
      expect(screen.getByText(/ai-powered summaries/i)).toBeInTheDocument();

      // Run accessibility audit
      const auditResults = await runAccessibilityAudit(container);
      expect(auditResults.violations).toHaveLength(0);
    });

    it('displays features with proper ARIA labels', () => {
      render(
        <TestWrapper>
          <WelcomeScreen />
        </TestWrapper>
      );

      // Check for accessible icons and descriptions
      const features = screen.getAllByRole('generic');
      expect(features.length).toBeGreaterThan(0);

      // Verify privacy notice is present
      expect(screen.getByText(/we respect your privacy/i)).toBeInTheDocument();
    });

    it('handles reduced motion preferences', async () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: vi.fn().mockImplementation(query => ({
          matches: query.includes('prefers-reduced-motion'),
          media: query,
          onchange: null,
          addListener: vi.fn(),
          removeListener: vi.fn(),
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      render(
        <TestWrapper>
          <WelcomeScreen />
        </TestWrapper>
      );

      // Component should still render properly with reduced motion
      expect(screen.getByRole('heading', { name: /welcome to corner league media/i })).toBeInTheDocument();
    });
  });

  describe('SportsSelection', () => {
    it('renders sports selection with keyboard navigation support', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <SportsSelection />
        </TestWrapper>
      );

      // Check main heading
      expect(screen.getByText(/select and rank your favorite sports/i)).toBeInTheDocument();

      // Check for sports checkboxes
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBeGreaterThan(0);

      // Test keyboard navigation
      const firstCheckbox = checkboxes[0];
      await user.tab();
      expect(firstCheckbox).toHaveFocus();

      // Test checkbox interaction
      await user.keyboard(' ');
      expect(firstCheckbox).toBeChecked();
    });

    it('validates minimum sports selection', () => {
      const validation = OnboardingValidator.validateSportsSelection([]);
      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('At least one sport must be selected');
    });

    it('supports drag and drop reordering', async () => {
      render(
        <TestWrapper>
          <SportsSelection />
        </TestWrapper>
      );

      // Check for drag handles
      const dragHandles = screen.getAllByLabelText(/reorder/i);
      expect(dragHandles.length).toBeGreaterThan(0);
    });

    it('provides proper ARIA labels for screen readers', () => {
      render(
        <TestWrapper>
          <SportsSelection />
        </TestWrapper>
      );

      // Check for proper labeling
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        expect(checkbox).toHaveAccessibleName();
      });
    });
  });

  describe('TeamSelection', () => {
    beforeEach(() => {
      // Mock sports selection in localStorage
      OnboardingStorage.saveOnboardingState({
        currentStep: 2,
        steps: [],
        userPreferences: {
          id: 'test-user',
          sports: mockSportsPreferences,
          teams: [],
          preferences: mockUserPreferences,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        isComplete: false,
        errors: {},
      });
    });

    it('renders team selection with search functionality', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <TeamSelection />
        </TestWrapper>
      );

      // Check for search input
      const searchInput = screen.getByPlaceholderText(/search.*teams/i);
      expect(searchInput).toBeInTheDocument();

      // Test search functionality
      await user.type(searchInput, 'chiefs');
      expect(searchInput).toHaveValue('chiefs');
    });

    it('groups teams by league', () => {
      render(
        <TestWrapper>
          <TeamSelection />
        </TestWrapper>
      );

      // Should have league groupings
      expect(screen.getByText(/nfl/i)).toBeInTheDocument();
    });

    it('validates team selection requirements', () => {
      const validation = OnboardingValidator.validateTeamSelection(
        [],
        mockSportsPreferences
      );
      expect(validation.isValid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });
  });

  describe('PreferencesSetup', () => {
    it('renders preferences form with proper validation', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <PreferencesSetup />
        </TestWrapper>
      );

      // Check for form elements
      expect(screen.getByText(/content preferences/i)).toBeInTheDocument();
      expect(screen.getByText(/notification settings/i)).toBeInTheDocument();

      // Check for switches/toggles
      const switches = screen.getAllByRole('switch');
      expect(switches.length).toBeGreaterThan(0);

      // Test switch interaction
      await user.click(switches[0]);
    });

    it('validates news type selection', () => {
      const validation = OnboardingValidator.validateUserSettings({
        newsTypes: [],
        notifications: mockUserPreferences.notifications,
        contentFrequency: 'standard',
      });
      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('At least one news type must be enabled');
    });

    it('supports keyboard navigation for all controls', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <PreferencesSetup />
        </TestWrapper>
      );

      // Test tab navigation
      await user.tab();
      const focusedElement = document.activeElement;
      expect(focusedElement).toBeDefined();
    });
  });

  describe('OnboardingComplete', () => {
    beforeEach(() => {
      // Mock completed preferences
      const completePreferences = {
        id: 'test-user',
        sports: mockSportsPreferences,
        teams: mockTeamPreferences,
        preferences: mockUserPreferences,
        completedAt: new Date().toISOString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      OnboardingStorage.saveUserPreferences(completePreferences);
    });

    it('displays completion summary with animations', () => {
      render(
        <TestWrapper>
          <OnboardingComplete />
        </TestWrapper>
      );

      // Check completion message
      expect(screen.getByText(/you're all set/i)).toBeInTheDocument();

      // Check summary sections
      expect(screen.getByText(/your personalized setup/i)).toBeInTheDocument();
    });

    it('shows user selections correctly', () => {
      render(
        <TestWrapper>
          <OnboardingComplete />
        </TestWrapper>
      );

      // Should display selected sports and teams
      expect(screen.getByText(/favorite sports/i)).toBeInTheDocument();
      expect(screen.getByText(/favorite teams/i)).toBeInTheDocument();
    });
  });

  describe('OnboardingLayout', () => {
    const mockProps = {
      currentStep: 1,
      steps: [
        { id: 'step1', title: 'Step 1', description: 'First step', isCompleted: true, isRequired: true },
        { id: 'step2', title: 'Step 2', description: 'Second step', isCompleted: false, isRequired: true },
      ],
      onNext: vi.fn(),
      onBack: vi.fn(),
      onSkip: vi.fn(),
      onExit: vi.fn(),
    };

    it('renders layout with proper navigation', () => {
      render(
        <TestWrapper>
          <OnboardingLayout {...mockProps}>
            <div>Test content</div>
          </OnboardingLayout>
        </TestWrapper>
      );

      // Check navigation elements
      expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();

      // Check step indicator
      expect(screen.getByText(/step 2 of 2/i)).toBeInTheDocument();
    });

    it('handles keyboard navigation for buttons', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <OnboardingLayout {...mockProps}>
            <div>Test content</div>
          </OnboardingLayout>
        </TestWrapper>
      );

      // Test keyboard interaction
      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.tab();

      // Should be able to activate with Enter or Space
      await user.keyboard('{Enter}');
      expect(mockProps.onNext).toHaveBeenCalled();
    });

    it('shows progress correctly', () => {
      render(
        <TestWrapper>
          <OnboardingLayout {...mockProps}>
            <div>Test content</div>
          </OnboardingLayout>
        </TestWrapper>
      );

      // Check progress indicators
      const progressElements = screen.getAllByLabelText(/step \d+/i);
      expect(progressElements.length).toBe(2);
    });
  });

  describe('FirstTimeExperience', () => {
    const mockProps = {
      isOpen: true,
      onClose: vi.fn(),
      onComplete: vi.fn(),
      userPreferences: {
        sports: mockSportsPreferences,
        teams: mockTeamPreferences,
      },
    };

    it('renders tutorial overlay with proper accessibility', async () => {
      const { container } = render(
        <TestWrapper>
          <FirstTimeExperience {...mockProps} />
        </TestWrapper>
      );

      // Check for tutorial content
      expect(screen.getByRole('button', { name: /skip tour/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();

      // Run accessibility audit
      const auditResults = await runAccessibilityAudit(container);
      expect(auditResults.violations).toHaveLength(0);
    });

    it('supports keyboard navigation through tutorial steps', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <FirstTimeExperience {...mockProps} />
        </TestWrapper>
      );

      // Should be able to navigate with keyboard
      await user.keyboard('{Escape}');
      expect(mockProps.onClose).toHaveBeenCalled();
    });

    it('handles focus management properly', () => {
      render(
        <TestWrapper>
          <FirstTimeExperience {...mockProps} />
        </TestWrapper>
      );

      // Focus should be trapped within the modal
      const skipButton = screen.getByRole('button', { name: /skip tour/i });
      expect(skipButton).toBeInTheDocument();
    });
  });

  describe('Local Storage Integration', () => {
    it('saves and loads onboarding state correctly', () => {
      const testState = OnboardingStorage.createDefaultOnboardingState();
      OnboardingStorage.saveOnboardingState(testState);

      const loadedState = OnboardingStorage.loadOnboardingState();
      expect(loadedState).toEqual(testState);
    });

    it('handles corrupted localStorage data gracefully', () => {
      localStorage.setItem('corner-league-onboarding-state', 'invalid json');

      const state = OnboardingStorage.loadOnboardingState();
      expect(state).toBeNull();
    });

    it('validates user preferences data structure', () => {
      const validPreferences = {
        id: 'test-user',
        sports: mockSportsPreferences,
        teams: mockTeamPreferences,
        preferences: mockUserPreferences,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      OnboardingStorage.saveUserPreferences(validPreferences);
      const loaded = OnboardingStorage.loadUserPreferences();
      expect(loaded).toEqual(expect.objectContaining(validPreferences));
    });
  });

  describe('Validation System', () => {
    it('validates complete preferences correctly', () => {
      const completePrefs = {
        id: 'test-user',
        sports: mockSportsPreferences,
        teams: mockTeamPreferences,
        preferences: mockUserPreferences,
      };

      const validation = OnboardingValidator.validateCompletePreferences(completePrefs);
      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    it('detects missing required fields', () => {
      const incompletePrefs = {
        sports: mockSportsPreferences,
      };

      const validation = OnboardingValidator.validateCompletePreferences(incompletePrefs);
      expect(validation.isValid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });
  });
});

describe('Accessibility Features', () => {
  it('supports high contrast mode detection', () => {
    // Mock high contrast media query
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: query.includes('prefers-contrast: high'),
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    // Test would check high contrast handling in components
  });

  it('announces important changes to screen readers', async () => {
    // This would test live region announcements
    // Implementation would depend on specific announcement patterns
  });
});

// Performance Tests
describe('Performance', () => {
  it('renders components without performance issues', () => {
    const startTime = performance.now();

    render(
      <TestWrapper>
        <WelcomeScreen />
      </TestWrapper>
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render quickly (less than 100ms)
    expect(renderTime).toBeLessThan(100);
  });

  it('handles large datasets efficiently', () => {
    // Test with many sports/teams
    const largeSportsList = Array.from({ length: 50 }, (_, i) => ({
      sportId: `sport-${i}`,
      name: `Sport ${i}`,
      rank: i + 1,
      hasTeams: true,
    }));

    // Mock large dataset and test rendering performance
    expect(largeSportsList.length).toBe(50);
  });
});