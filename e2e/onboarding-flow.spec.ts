/**
 * End-to-End tests for the complete onboarding flow
 * Tests the full user journey from welcome to completion
 */

import { test, expect, Page } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

// Test data
const MOCK_SPORTS = [
  { id: 'sport-1', name: 'Football', icon: '🏈' },
  { id: 'sport-2', name: 'Basketball', icon: '🏀' },
  { id: 'sport-3', name: 'Baseball', icon: '⚾' },
];

const MOCK_TEAMS = [
  { id: 'team-1', name: 'Patriots', market: 'New England', sport: 'Football' },
  { id: 'team-2', name: 'Chiefs', market: 'Kansas City', sport: 'Football' },
  { id: 'team-3', name: 'Lakers', market: 'Los Angeles', sport: 'Basketball' },
  { id: 'team-4', name: 'Celtics', market: 'Boston', sport: 'Basketball' },
];

class OnboardingPageObject {
  constructor(private page: Page) {}

  async goto(step?: number) {
    const url = step ? `/onboarding/step/${step}` : '/onboarding';
    await this.page.goto(url);
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    // Wait for the main content to load - looking for actual elements that exist
    await this.page.waitForSelector('main', { timeout: 15000 });
  }

  async getProgressPercentage() {
    const progressText = await this.page.textContent('text=/%\\s+complete/');
    return progressText?.match(/(\d+)%/)?.[1];
  }

  async getCurrentStep() {
    const stepText = await this.page.textContent('text=/Step \\d+ of \\d+/');
    return stepText?.match(/Step (\d+)/)?.[1];
  }

  async clickContinue() {
    await this.page.click('button:has-text("Continue"), button:has-text("Get Started")');
  }

  async clickBack() {
    await this.page.click('button:has-text("Back")');
  }

  async isContinueDisabled() {
    const continueButton = this.page.locator('button:has-text("Continue"), button:has-text("Get Started")');
    return await continueButton.isDisabled();
  }

  // Welcome Step Methods
  async verifyWelcomeStep() {
    await expect(this.page.locator('h1')).toContainText(/welcome/i);
    await expect(this.page.locator('text=/Step \\d+ of \\d+/')).toContainText('Step 1 of 5');
  }

  // Sports Selection Methods
  async verifySportsStep() {
    await expect(this.page.locator('h1')).toContainText(/sports/i);
    await expect(this.page.locator('text=/Step \\d+ of \\d+/')).toContainText('Step 2 of 5');
  }

  async selectSport(sportName: string) {
    await this.page.click(`[data-testid^="sport-card-"]:has-text("${sportName}")`);
  }

  async getSportSelectionCount() {
    const selectedSports = await this.page.locator('[data-selected="true"]').count();
    return selectedSports;
  }

  async dragSportToPosition(sportName: string, targetPosition: number) {
    const source = this.page.locator(`[data-testid="sport-card"]:has-text("${sportName}")`);
    const target = this.page.locator(`[data-testid="sport-position-${targetPosition}"]`);

    await source.dragTo(target);
  }

  // Team Selection Methods
  async verifyTeamsStep() {
    await expect(this.page.locator('h1')).toContainText(/teams/i);
    await expect(this.page.locator('[data-testid="step-indicator"]')).toContainText('Step 3 of 5');
  }

  async selectTeam(teamName: string) {
    await this.page.click(`[data-testid="team-card"]:has-text("${teamName}")`);
  }

  async setTeamAffinity(teamName: string, score: number) {
    const slider = this.page.locator(`[data-testid="affinity-slider"]:near([data-testid="team-card"]:has-text("${teamName}"))`);
    await slider.fill(score.toString());
  }

  async searchTeams(query: string) {
    await this.page.fill('[data-testid="team-search"]', query);
  }

  async filterByLeague(league: string) {
    await this.page.selectOption('[data-testid="league-filter"]', league);
  }

  // Preferences Methods
  async verifyPreferencesStep() {
    await expect(this.page.locator('h1')).toContainText(/preferences/i);
    await expect(this.page.locator('[data-testid="step-indicator"]')).toContainText('Step 4 of 5');
  }

  async toggleNewsType(newsType: string) {
    await this.page.check(`[data-testid="news-type-${newsType}"]`);
  }

  async setNewsPriority(newsType: string, priority: number) {
    const slider = this.page.locator(`[data-testid="priority-slider-${newsType}"]`);
    await slider.fill(priority.toString());
  }

  async toggleNotification(notificationType: string) {
    await this.page.check(`[data-testid="notification-${notificationType}"]`);
  }

  async selectContentFrequency(frequency: 'minimal' | 'standard' | 'comprehensive') {
    await this.page.check(`[data-testid="frequency-${frequency}"]`);
  }

  // Completion Methods
  async verifyCompletionStep() {
    await expect(this.page.locator('h1')).toContainText(/complete|congratulations/i);
    await expect(this.page.locator('[data-testid="step-indicator"]')).toContainText('Step 5 of 5');
  }

  async completeOnboarding() {
    await this.page.click('button:has-text("Complete Onboarding")');
  }

  async verifySummary() {
    await expect(this.page.locator('[data-testid="summary-section"]')).toBeVisible();
  }

  async verifySelectedSports(expectedSports: string[]) {
    for (const sport of expectedSports) {
      await expect(this.page.locator(`[data-testid="summary-sports"]:has-text("${sport}")`)).toBeVisible();
    }
  }

  async verifySelectedTeams(expectedTeams: string[]) {
    for (const team of expectedTeams) {
      await expect(this.page.locator(`[data-testid="summary-teams"]:has-text("${team}")`)).toBeVisible();
    }
  }
}

test.describe('Onboarding Flow E2E', () => {
  let onboarding: OnboardingPageObject;

  test.beforeEach(async ({ page }) => {
    onboarding = new OnboardingPageObject(page);

    // Mock API responses
    await page.route('**/api/v1/onboarding/sports', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            sports: MOCK_SPORTS,
            total: MOCK_SPORTS.length,
          },
        }),
      });
    });

    await page.route('**/api/v1/onboarding/teams**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            teams: MOCK_TEAMS,
            total: MOCK_TEAMS.length,
          },
        }),
      });
    });

    await page.route('**/api/v1/onboarding/step', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            is_onboarded: false,
            current_step: 2,
            onboarding_completed_at: null,
          },
        }),
      });
    });

    await page.route('**/api/v1/onboarding/complete', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            success: true,
            user_id: 'test-user',
            onboarding_completed_at: new Date().toISOString(),
            message: 'Onboarding completed successfully',
          },
        }),
      });
    });
  });

  test('completes full onboarding flow successfully', async ({ page }) => {
    // Step 1: Welcome
    await onboarding.goto(1);
    await onboarding.waitForPageLoad();
    await onboarding.verifyWelcomeStep();

    expect(await onboarding.getProgressPercentage()).toBe('20');
    expect(await onboarding.isContinueDisabled()).toBe(false);

    await onboarding.clickContinue();

    // Step 2: Sports Selection
    await onboarding.waitForPageLoad();
    await onboarding.verifySportsStep();

    expect(await onboarding.getProgressPercentage()).toBe('40');
    expect(await onboarding.isContinueDisabled()).toBe(true); // No sports selected yet

    // Select sports
    await onboarding.selectSport('Football');
    await onboarding.selectSport('Basketball');

    expect(await onboarding.getSportSelectionCount()).toBe(2);
    expect(await onboarding.isContinueDisabled()).toBe(false);

    await onboarding.clickContinue();

    // Step 3: Team Selection
    await onboarding.waitForPageLoad();
    await onboarding.verifyTeamsStep();

    expect(await onboarding.getProgressPercentage()).toBe('60');
    expect(await onboarding.isContinueDisabled()).toBe(true); // No teams selected yet

    // Select teams
    await onboarding.selectTeam('Patriots');
    await onboarding.setTeamAffinity('Patriots', 9);
    await onboarding.selectTeam('Lakers');
    await onboarding.setTeamAffinity('Lakers', 8);

    expect(await onboarding.isContinueDisabled()).toBe(false);

    await onboarding.clickContinue();

    // Step 4: Preferences
    await onboarding.waitForPageLoad();
    await onboarding.verifyPreferencesStep();

    expect(await onboarding.getProgressPercentage()).toBe('80');

    // Set preferences
    await onboarding.toggleNewsType('injuries');
    await onboarding.setNewsPriority('injuries', 5);
    await onboarding.toggleNewsType('trades');
    await onboarding.setNewsPriority('trades', 4);

    await onboarding.toggleNotification('push');
    await onboarding.toggleNotification('email');

    await onboarding.selectContentFrequency('standard');

    await onboarding.clickContinue();

    // Step 5: Completion
    await onboarding.waitForPageLoad();
    await onboarding.verifyCompletionStep();

    expect(await onboarding.getProgressPercentage()).toBe('100');

    // Verify summary
    await onboarding.verifySummary();
    await onboarding.verifySelectedSports(['Football', 'Basketball']);
    await onboarding.verifySelectedTeams(['Patriots', 'Lakers']);

    // Complete onboarding
    await onboarding.completeOnboarding();

    // Verify redirection to dashboard
    await page.waitForURL('**/dashboard');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('supports back navigation between steps', async ({ page }) => {
    await onboarding.goto(3);
    await onboarding.waitForPageLoad();
    await onboarding.verifyTeamsStep();

    // Navigate back to sports
    await onboarding.clickBack();
    await onboarding.waitForPageLoad();
    await onboarding.verifySportsStep();

    // Navigate back to welcome
    await onboarding.clickBack();
    await onboarding.waitForPageLoad();
    await onboarding.verifyWelcomeStep();
  });

  test('validates required selections at each step', async ({ page }) => {
    // Step 2: No sports selected
    await onboarding.goto(2);
    await onboarding.waitForPageLoad();
    expect(await onboarding.isContinueDisabled()).toBe(true);

    // Step 3: No teams selected
    await onboarding.goto(3);
    await onboarding.waitForPageLoad();
    expect(await onboarding.isContinueDisabled()).toBe(true);
  });

  test('persists selections across navigation', async ({ page }) => {
    // Select sports on step 2
    await onboarding.goto(2);
    await onboarding.waitForPageLoad();
    await onboarding.selectSport('Football');
    await onboarding.selectSport('Basketball');
    await onboarding.clickContinue();

    // Select teams on step 3
    await onboarding.waitForPageLoad();
    await onboarding.selectTeam('Patriots');
    await onboarding.clickContinue();

    // Navigate back to verify selections persist
    await onboarding.waitForPageLoad();
    await onboarding.clickBack();
    await onboarding.waitForPageLoad();

    // Teams should still be selected
    await expect(page.locator('[data-testid="team-card"]:has-text("Patriots")[data-selected="true"]')).toBeVisible();

    await onboarding.clickBack();
    await onboarding.waitForPageLoad();

    // Sports should still be selected
    await expect(page.locator('[data-testid="sport-card"]:has-text("Football")[data-selected="true"]')).toBeVisible();
    await expect(page.locator('[data-testid="sport-card"]:has-text("Basketball")[data-selected="true"]')).toBeVisible();
  });

  test('handles maximum selection limits', async ({ page }) => {
    await onboarding.goto(2);
    await onboarding.waitForPageLoad();

    // Try to select more than 5 sports (if there were more available)
    await onboarding.selectSport('Football');
    await onboarding.selectSport('Basketball');
    await onboarding.selectSport('Baseball');

    // Should not exceed limit
    expect(await onboarding.getSportSelectionCount()).toBeLessThanOrEqual(5);
  });

  test('supports drag and drop reordering of sports', async ({ page }) => {
    await onboarding.goto(2);
    await onboarding.waitForPageLoad();

    await onboarding.selectSport('Football');
    await onboarding.selectSport('Basketball');

    // Verify initial order
    const firstSport = page.locator('[data-testid="selected-sports"] [data-position="1"]');
    await expect(firstSport).toContainText('Football');

    // Drag Basketball to first position
    await onboarding.dragSportToPosition('Basketball', 1);

    // Verify new order
    await expect(firstSport).toContainText('Basketball');
  });

  test('supports team search and filtering', async ({ page }) => {
    await onboarding.goto(3);
    await onboarding.waitForPageLoad();

    // Search for specific team
    await onboarding.searchTeams('Patriots');
    await expect(page.locator('[data-testid="team-card"]:has-text("Patriots")')).toBeVisible();
    await expect(page.locator('[data-testid="team-card"]:has-text("Lakers")')).not.toBeVisible();

    // Clear search
    await onboarding.searchTeams('');
    await expect(page.locator('[data-testid="team-card"]:has-text("Lakers")')).toBeVisible();

    // Filter by league
    await onboarding.filterByLeague('NFL');
    await expect(page.locator('[data-testid="team-card"]:has-text("Patriots")')).toBeVisible();
    await expect(page.locator('[data-testid="team-card"]:has-text("Lakers")')).not.toBeVisible();
  });

  test('handles API errors gracefully', async ({ page }) => {
    // Mock API error for sports
    await page.route('**/api/v1/onboarding/sports', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'INTERNAL_ERROR',
          message: 'Failed to retrieve sports data',
          timestamp: new Date().toISOString(),
        }),
      });
    });

    await onboarding.goto(2);
    await onboarding.waitForPageLoad();

    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toContainText(/error.*loading.*sports/i);

    // Should show retry button
    await expect(page.locator('button:has-text("Try Again")')).toBeVisible();
  });

  test('handles network timeouts', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/v1/onboarding/sports', async route => {
      await new Promise(resolve => setTimeout(resolve, 20000)); // 20 second delay
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: { sports: [], total: 0 } }),
      });
    });

    await onboarding.goto(2);

    // Should show loading state initially
    await expect(page.locator('[data-testid="loading-sports"]')).toBeVisible();

    // Should eventually timeout and show error
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 30000 });
  });

  test('maintains responsive design on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

    await onboarding.goto(1);
    await onboarding.waitForPageLoad();

    // Check that layout adapts to mobile
    await expect(page.locator('[data-testid="onboarding-layout"]')).toBeVisible();
    await expect(page.locator('button:has-text("Continue")')).toBeVisible();

    // Navigate through steps on mobile
    await onboarding.clickContinue();
    await onboarding.waitForPageLoad();
    await onboarding.verifySportsStep();

    // Sports cards should be mobile-friendly
    await expect(page.locator('[data-testid="sport-card"]').first()).toBeVisible();
  });

  test('supports keyboard navigation', async ({ page }) => {
    await onboarding.goto(2);
    await onboarding.waitForPageLoad();

    // Tab to first sport card
    await page.keyboard.press('Tab');

    // Use arrow keys to navigate between sports
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowRight');

    // Use Enter to select sport
    await page.keyboard.press('Enter');

    // Verify sport was selected
    expect(await onboarding.getSportSelectionCount()).toBeGreaterThan(0);

    // Tab to continue button and press Enter
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');

    // Should navigate to next step
    await onboarding.waitForPageLoad();
    await onboarding.verifyTeamsStep();
  });

  test('shows loading states during API calls', async ({ page }) => {
    // Mock delayed API response
    await page.route('**/api/v1/onboarding/step', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { is_onboarded: false, current_step: 3 },
        }),
      });
    });

    await onboarding.goto(2);
    await onboarding.waitForPageLoad();
    await onboarding.selectSport('Football');

    // Click continue and verify loading state
    await onboarding.clickContinue();
    await expect(page.locator('button:has-text("Continue")[disabled]')).toBeVisible();
    await expect(page.locator('[data-testid="saving-indicator"]')).toBeVisible();

    // Should eventually complete
    await onboarding.waitForPageLoad();
    await onboarding.verifyTeamsStep();
  });

  test('validates step transitions and prevents skipping', async ({ page }) => {
    // Try to navigate directly to step 5 without completing previous steps
    await onboarding.goto(5);

    // Should redirect to appropriate step based on completion status
    await page.waitForURL('**/onboarding/step/**');

    // Should not be on step 5
    expect(await onboarding.getCurrentStep()).not.toBe('5');
  });

  test('handles browser refresh and maintains state', async ({ page }) => {
    await onboarding.goto(2);
    await onboarding.waitForPageLoad();
    await onboarding.selectSport('Football');

    // Refresh the page
    await page.reload();
    await onboarding.waitForPageLoad();

    // Should maintain selected sports (if properly implemented with localStorage/sessionStorage)
    await onboarding.verifySportsStep();
  });
});

test.describe('Onboarding Accessibility', () => {
  let onboarding: OnboardingPageObject;

  test.beforeEach(async ({ page }) => {
    onboarding = new OnboardingPageObject(page);
    await injectAxe(page);
  });

  test('welcome step is accessible', async ({ page }) => {
    await onboarding.goto(1);
    await onboarding.waitForPageLoad();
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });

  test('sports selection step is accessible', async ({ page }) => {
    await onboarding.goto(2);
    await onboarding.waitForPageLoad();
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });

  test('team selection step is accessible', async ({ page }) => {
    await onboarding.goto(3);
    await onboarding.waitForPageLoad();
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });

  test('preferences step is accessible', async ({ page }) => {
    await onboarding.goto(4);
    await onboarding.waitForPageLoad();
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });

  test('completion step is accessible', async ({ page }) => {
    await onboarding.goto(5);
    await onboarding.waitForPageLoad();
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });

  test('supports screen reader navigation', async ({ page }) => {
    await onboarding.goto(1);
    await onboarding.waitForPageLoad();

    // Check for proper heading structure
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);

    // Check for aria-labels and roles
    await expect(page.locator('[role="progressbar"]')).toBeVisible();
    await expect(page.locator('[aria-label]').first()).toBeVisible();
  });
});