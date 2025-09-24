/**
 * Test Utilities Index
 * Centralized exports for all onboarding test utilities
 */

// Page Object Models
export {
  BaseOnboardingPage,
  WelcomeStepPage,
  SportsSelectionStepPage,
  TeamSelectionStepPage,
  PreferencesStepPage,
  CompletionStepPage,
  OnboardingFlowPage,
  type OnboardingState
} from './page-objects';

// Wait Strategies
export {
  WaitStrategies,
  type WaitCondition,
  type WaitOptions
} from './wait-strategies';

// Team Selection Helpers
export {
  TeamSelectionTestHelpers,
  type TeamData,
  type TeamSelection
} from './team-selection-helpers';

// Preferences Helpers
export {
  PreferencesTestHelpers,
  type NewsTypePreferences,
  type NotificationPreferences,
  type ContentPreferences,
  type PreferencesData
} from './preferences-helpers';

// Completion Helpers
export {
  CompletionTestHelpers,
  type OnboardingSummary,
  type CompletionMetrics
} from './completion-helpers';

// Error Handling
export {
  ErrorHandlingStrategies,
  type RetryConfig,
  type ErrorContext
} from './error-handling';

// Re-export existing helpers for backward compatibility
export {
  MOCK_SPORTS_DATA,
  MOCK_TEAMS_DATA,
  setupOnboardingMocks,
  setupFailingMocks,
  clearBrowserStorage,
  SportsSelectionHelpers,
  OnboardingFlowHelpers,
  AccessibilityHelpers,
  ResponsiveHelpers,
  ErrorHandlingHelpers,
  VisualTestHelpers,
  PerformanceHelpers
} from './onboarding-helpers';

/**
 * Utility function to create a complete test suite with all helpers
 */
import { Page, TestInfo } from '@playwright/test';

export function createOnboardingTestSuite(page: Page, testInfo?: TestInfo) {
  const errorHandling = new ErrorHandlingStrategies(page, testInfo);
  const waitStrategies = new WaitStrategies(page);

  return {
    // Page objects
    flow: new OnboardingFlowPage(page),

    // Specialized helpers
    teamSelection: new TeamSelectionTestHelpers(page),
    preferences: new PreferencesTestHelpers(page),
    completion: new CompletionTestHelpers(page),

    // Utilities
    wait: waitStrategies,
    errorHandling,

    // Legacy helpers for backward compatibility
    sportsSelection: new (require('./onboarding-helpers').SportsSelectionHelpers)(page),
    navigation: new (require('./onboarding-helpers').OnboardingFlowHelpers)(page),
    accessibility: new (require('./onboarding-helpers').AccessibilityHelpers)(page),
    responsive: new (require('./onboarding-helpers').ResponsiveHelpers)(page),
    visual: new (require('./onboarding-helpers').VisualTestHelpers)(page),
    performance: new (require('./onboarding-helpers').PerformanceHelpers)(page),

    // Common setup functions
    async setupMocks() {
      const { setupOnboardingMocks } = require('./onboarding-helpers');
      await setupOnboardingMocks(page);
    },

    async clearStorage() {
      const { clearBrowserStorage } = require('./onboarding-helpers');
      await clearBrowserStorage(page);
    },

    async setupFailingMocks() {
      const { setupFailingMocks } = require('./onboarding-helpers');
      await setupFailingMocks(page);
    }
  };
}

/**
 * Quick setup function for common test patterns
 */
export async function setupOnboardingTest(page: Page, options: {
  mockApis?: boolean;
  clearStorage?: boolean;
  testMode?: boolean;
} = {}) {
  const {
    mockApis = true,
    clearStorage = true,
    testMode = true
  } = options;

  // Set test mode flags
  if (testMode) {
    await page.addInitScript(() => {
      (window as any).__PLAYWRIGHT_TEST__ = true;
      (window as any).__TEST_MODE__ = true;
    });
  }

  // Clear storage if requested
  if (clearStorage) {
    const { clearBrowserStorage } = require('./onboarding-helpers');
    await clearBrowserStorage(page);
  }

  // Setup API mocks if requested
  if (mockApis) {
    const { setupOnboardingMocks } = require('./onboarding-helpers');
    await setupOnboardingMocks(page);
  }
}

/**
 * Common test patterns and workflows
 */
export const TestPatterns = {
  /**
   * Complete a full onboarding flow with standard selections
   */
  async completeStandardFlow(suite: ReturnType<typeof createOnboardingTestSuite>) {
    // Step 1: Welcome
    const welcomePage = await suite.flow.navigateToStep(1);
    await welcomePage.verifyStep();
    await welcomePage.clickContinue();

    // Step 2: Sports Selection
    const sportsPage = await suite.flow.navigateToStep(2);
    await sportsPage.verifySportsStep();
    await sportsPage.selectMultipleSports(['nfl', 'nba']);
    await sportsPage.clickContinue();

    // Step 3: Team Selection
    const teamsPage = await suite.flow.navigateToStep(3);
    await teamsPage.verifyTeamsStep();
    await suite.teamSelection.selectMultipleTeams(['Patriots', 'Lakers']);
    await teamsPage.clickContinue();

    // Step 4: Preferences
    const prefsPage = await suite.flow.navigateToStep(4);
    await prefsPage.verifyPreferencesStep();
    await suite.preferences.setStandardPreferences();
    await prefsPage.clickContinue();

    // Step 5: Completion
    const completionPage = await suite.flow.navigateToStep(5);
    await completionPage.verifyCompletionStep();

    return completionPage;
  },

  /**
   * Test error recovery pattern
   */
  async testErrorRecovery(suite: ReturnType<typeof createOnboardingTestSuite>, step: number) {
    return await suite.errorHandling.withErrorHandling(
      async () => {
        const stepPage = await suite.flow.navigateToStep(step);
        await stepPage.verifyStep();
        return stepPage;
      },
      `Navigate to step ${step}`,
      { retries: 3, continueOnError: false }
    );
  },

  /**
   * Validate accessibility across all steps
   */
  async validateAccessibility(suite: ReturnType<typeof createOnboardingTestSuite>) {
    const results = [];

    for (let step = 1; step <= 5; step++) {
      try {
        await suite.flow.navigateToStep(step);
        const focusOrder = await suite.accessibility.checkFocusOrder();
        const hasValidLabels = await suite.accessibility.verifyAriaLabels();

        results.push({
          step,
          focusOrder,
          hasValidLabels,
          passed: hasValidLabels
        });
      } catch (error) {
        results.push({
          step,
          error: (error as Error).message,
          passed: false
        });
      }
    }

    return results;
  }
};