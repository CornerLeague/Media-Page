/**
 * Example Test File Demonstrating New Test Utilities
 * This file shows how to use the enhanced test utilities
 * Remove this file once actual tests are updated
 */

import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';
import {
  createOnboardingTestSuite,
  setupOnboardingTest,
  TestPatterns
} from './index';

test.describe('Enhanced Onboarding Test Utilities Demo', () => {
  test.beforeEach(async ({ page }) => {
    // Setup test environment with new utilities
    await setupOnboardingTest(page, {
      mockApis: true,
      clearStorage: true,
      testMode: true
    });

    // Inject axe for accessibility testing
    await injectAxe(page);
  });

  test('demonstrates page object model usage', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Using page objects for reliable element interaction
    const welcomePage = await suite.flow.navigateToStep(1);
    await welcomePage.verifyWelcomeContent();

    const sportsPage = await suite.flow.navigateToStep(2);
    await sportsPage.verifySportsStep();
    await sportsPage.waitForSportsToLoad();

    // Robust sports selection
    await sportsPage.selectSport('nfl');
    await sportsPage.selectSport('nba');

    // Verify selection state
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
    expect(await sportsPage.isSportSelected('nba')).toBe(true);
    await sportsPage.verifySelectionCount(2);

    await sportsPage.clickContinue();

    // Team selection with specialized helpers
    const teamsPage = await suite.flow.navigateToStep(3);
    await suite.teamSelection.waitForTeamsToLoad();

    await suite.teamSelection.selectTeam('New England Patriots');
    await suite.teamSelection.setTeamAffinity('New England Patriots', 4);

    await suite.teamSelection.verifyTeamSelected('New England Patriots');
    await suite.teamSelection.verifyTeamAffinity('New England Patriots', 4);
  });

  test('demonstrates error handling and retry strategies', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Test with error handling wrapper
    const sportsPage = await suite.errorHandling.withErrorHandling(
      async () => {
        const page = await suite.flow.navigateToStep(2);
        await page.verifySportsStep();
        return page;
      },
      'Navigate to sports selection',
      { retries: 3, continueOnError: false }
    );

    // Safe click with automatic retry
    const sportCard = sportsPage!.getSportCard('nfl');
    await suite.errorHandling.safeClick(sportCard, {
      timeout: 10000,
      retries: 3,
      scrollIntoView: true,
      waitForEnabled: true
    });

    // Execute with custom retry logic
    await suite.errorHandling.executeWithRetry(
      async () => {
        await sportsPage!.clickContinue();
        await suite.wait.waitForNetworkIdle();
      },
      {
        maxRetries: 3,
        retryDelay: 1000,
        exponentialBackoff: true
      },
      'Continue to next step'
    );
  });

  test('demonstrates smart wait strategies', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Navigate and wait for page to be fully ready
    await suite.errorHandling.safeNavigate('/onboarding/step/2');
    await suite.wait.waitForPageReady();

    // Smart wait with multiple conditions
    const sportsContainer = page.locator('[data-testid^="sport-card-"]');
    await suite.wait.smartWait(sportsContainer, {
      condition: 'visible',
      timeout: 15000,
      stable: true
    });

    // Wait for specific count of elements
    await suite.wait.waitForCount(sportsContainer, 4, 10000);

    // Wait for animations to complete before interaction
    await suite.wait.waitForAnimations();
  });

  test('demonstrates preferences testing', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Navigate to preferences step
    await suite.flow.navigateToStep(4);
    await suite.preferences.waitForPreferencesToLoad();

    // Set comprehensive preferences using helper
    await suite.preferences.setComprehensivePreferences();

    // Verify all preferences were set correctly
    await suite.preferences.verifyAllPreferences({
      newsTypes: {
        scores: true,
        injuries: true,
        trades: true,
        analysis: true
      },
      notifications: {
        push: true,
        email: true,
        sms: true
      },
      content: {
        frequency: 'comprehensive'
      }
    });

    // Capture current state for comparison
    const currentPrefs = await suite.preferences.captureCurrentPreferences();
    expect(currentPrefs.content.frequency).toBe('comprehensive');
  });

  test('demonstrates completion testing', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Use test pattern for complete flow
    const completionPage = await TestPatterns.completeStandardFlow(suite);

    // Comprehensive completion verification
    await suite.completion.verifyFullCompletion({
      sports: ['Football', 'Basketball'],
      teams: ['Patriots', 'Lakers'],
      hasPreferences: true,
      redirectUrl: /.*\/$/
    });

    // Capture completion metrics
    const metrics = await suite.completion.getCompletionMetrics();
    expect(metrics.totalSteps).toBe(5);
    expect(metrics.completedSteps).toBe(5);
  });

  test('demonstrates accessibility testing integration', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Test accessibility across all steps
    const a11yResults = await TestPatterns.validateAccessibility(suite);

    // Verify all steps pass accessibility checks
    for (const result of a11yResults) {
      expect(result.passed).toBe(true);
      expect(result.hasValidLabels).toBe(true);
    }

    // Run axe checks on completion step
    await suite.flow.navigateToStep(5);
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });

  test('demonstrates responsive testing', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Test mobile viewport
    await suite.responsive.setMobileViewport();
    await suite.flow.navigateToStep(2);

    // Verify touch targets are appropriately sized
    const sportCards = page.locator('[data-testid^="sport-card-"]');
    await suite.responsive.verifyTouchTargetSize('[data-testid^="sport-card-"]', 44);

    // Test touch interaction
    await suite.responsive.testTouchInteraction('[data-testid="sport-card-nfl"]');

    // Switch to desktop and verify layout adapts
    await suite.responsive.setDesktopViewport();
    await page.waitForTimeout(500); // Wait for layout adjustment
  });

  test('demonstrates error simulation and recovery', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Simulate network issues
    await suite.errorHandling.simulateNetworkIssues('slow', 2000);

    // Navigate with error handling
    await suite.errorHandling.safeNavigate('/onboarding/step/2', {
      timeout: 15000,
      retries: 3,
      waitForLoad: true
    });

    // Test recovery from simulated API failure
    await suite.teamSelection.simulateTeamsApiError();

    const teamsPage = await suite.flow.navigateToStep(3);

    // Verify error state is handled gracefully
    const hasError = await suite.teamSelection.hasError();
    if (hasError) {
      // Recovery strategy
      await suite.errorHandling.recoverFromFailure('api');
      await teamsPage.navigateTo(); // Retry navigation
    }
  });

  test('demonstrates visual regression testing', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Take screenshots at each step for visual comparison
    for (let step = 1; step <= 5; step++) {
      await suite.flow.navigateToStep(step);
      await suite.visual.takeStepScreenshot(step);

      // Test dark mode
      await suite.visual.enableDarkMode();
      await suite.visual.takeStepScreenshot(step, 'dark');

      // Test high contrast
      await suite.visual.enableHighContrast();
      await suite.visual.takeStepScreenshot(step, 'high-contrast');

      // Reset to normal mode
      await page.emulateMedia({ colorScheme: 'light' });
    }
  });

  test('demonstrates performance monitoring', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Measure page load performance
    const loadTime = await suite.performance.measurePageLoadTime();
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds

    // Measure interaction performance
    const interactionTime = await suite.performance.measureInteractionTime(async () => {
      await suite.flow.navigateToStep(2);
      const sportsPage = suite.flow.sportsStep;
      await sportsPage.selectSport('nfl');
    });
    expect(interactionTime).toBeLessThan(1000); // Should interact within 1 second

    // Collect detailed metrics
    const metrics = await suite.performance.collectMetrics();
    expect(metrics.firstContentfulPaint).toBeLessThan(3000);
    expect(metrics.domContentLoaded).toBeLessThan(2000);
  });

  test('demonstrates custom retry conditions', async ({ page }, testInfo) => {
    const suite = createOnboardingTestSuite(page, testInfo);

    // Create custom retry condition for specific errors
    const networkRetryCondition = suite.errorHandling.createRetryCondition([
      /network.*failed/i,
      /timeout.*exceeded/i,
      /connection.*refused/i
    ]);

    // Use custom retry logic
    const result = await suite.errorHandling.executeWithRetry(
      async () => {
        await suite.flow.navigateToStep(3);
        await suite.teamSelection.waitForTeamsToLoad();
        return 'success';
      },
      {
        maxRetries: 5,
        retryDelay: 2000,
        exponentialBackoff: true,
        retryCondition: networkRetryCondition
      },
      'Load teams with network retry logic'
    );

    expect(result).toBe('success');
  });
});

// Cleanup after all tests
test.afterAll(async ({ browser }) => {
  // Ensure all pages are closed
  const contexts = browser.contexts();
  for (const context of contexts) {
    await context.close();
  }
});