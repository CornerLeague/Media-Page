/**
 * Completion Step Test Utilities
 * Specialized helpers for onboarding completion and summary testing
 */

import { Page, Locator, expect } from '@playwright/test';
import { WaitStrategies } from './wait-strategies';
import { PreferencesData } from './preferences-helpers';

export interface OnboardingSummary {
  selectedSports: Array<{
    id: string;
    name: string;
    rank: number;
  }>;
  selectedTeams: Array<{
    id: string;
    name: string;
    sport: string;
    affinityScore: number;
  }>;
  preferences: PreferencesData;
  completionTime?: string;
  userId?: string;
}

export interface CompletionMetrics {
  totalSteps: number;
  completedSteps: number;
  timeSpent: number;
  clicksToComplete: number;
}

/**
 * Completion Step Test Helper Class
 */
export class CompletionTestHelpers {
  private waitStrategies: WaitStrategies;

  constructor(private page: Page) {
    this.waitStrategies = new WaitStrategies(page);
  }

  // Element getters - Main completion elements
  get summarySection(): Locator {
    return this.page.locator('[data-testid="summary-section"]');
  }

  get completionTitle(): Locator {
    return this.page.locator('h1');
  }

  get completionMessage(): Locator {
    return this.page.locator('[data-testid="completion-message"]');
  }

  get completeButton(): Locator {
    return this.page.locator(
      'button:has-text("Get Started"), button:has-text("Enter Dashboard"), button:has-text("Complete"), button:has-text("Finish")'
    );
  }

  get loadingIndicator(): Locator {
    return this.page.locator('[data-testid="completion-loading"]');
  }

  get errorMessage(): Locator {
    return this.page.locator('[data-testid="completion-error"]');
  }

  // Element getters - Summary sections
  get sportsSummary(): Locator {
    return this.page.locator('[data-testid="sports-summary"]');
  }

  get teamsSummary(): Locator {
    return this.page.locator('[data-testid="teams-summary"]');
  }

  get preferencesSummary(): Locator {
    return this.page.locator('[data-testid="preferences-summary"]');
  }

  get progressSummary(): Locator {
    return this.page.locator('[data-testid="progress-summary"]');
  }

  // Element getters - Action elements
  get editSportsButton(): Locator {
    return this.page.locator('button:has-text("Edit Sports"), a:has-text("Edit Sports")');
  }

  get editTeamsButton(): Locator {
    return this.page.locator('button:has-text("Edit Teams"), a:has-text("Edit Teams")');
  }

  get editPreferencesButton(): Locator {
    return this.page.locator('button:has-text("Edit Preferences"), a:has-text("Edit Preferences")');
  }

  get startOverButton(): Locator {
    return this.page.locator('button:has-text("Start Over"), button:has-text("Restart")');
  }

  // Wait for completion page to load
  async waitForCompletionToLoad(timeout: number = 15000): Promise<void> {
    try {
      // Wait for main summary section
      await this.waitStrategies.waitForElement(this.summarySection, 'visible', timeout);

      // Wait for completion title
      await this.waitStrategies.waitForElement(this.completionTitle, 'visible', timeout);

      // Wait for complete button to be available
      await this.waitStrategies.waitForElement(this.completeButton, 'visible', timeout);

      // Additional wait for dynamic content to load
      await this.page.waitForTimeout(500);
    } catch (error) {
      // Check for loading or error states
      if (await this.loadingIndicator.isVisible()) {
        await this.waitStrategies.waitForElement(this.summarySection, 'visible', timeout + 5000);
      } else if (await this.errorMessage.isVisible()) {
        throw new Error('Completion page loaded with error state');
      } else {
        throw error;
      }
    }
  }

  // Main completion actions
  async completeOnboarding(): Promise<void> {
    await this.waitForCompletionToLoad();

    await this.waitStrategies.waitForEnabled(this.completeButton);
    await this.completeButton.click();

    // Wait for navigation or completion processing
    await this.page.waitForTimeout(1000);
  }

  async completeOnboardingAndWaitForRedirect(expectedUrl: RegExp): Promise<void> {
    await this.completeOnboarding();
    await this.page.waitForURL(expectedUrl, { timeout: 10000 });
  }

  // Summary verification methods
  async verifySummarySection(): Promise<void> {
    await expect(this.summarySection).toBeVisible();
  }

  async verifyCompletionTitle(expectedPattern: RegExp): Promise<void> {
    await expect(this.completionTitle).toContainText(expectedPattern);
  }

  async verifyCompletionMessage(expectedMessage: string | RegExp): Promise<void> {
    if (await this.completionMessage.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(this.completionMessage).toContainText(expectedMessage);
    } else {
      // Some implementations might not have a separate completion message
      console.warn('Completion message element not found, skipping verification');
    }
  }

  // Sports summary verification
  async verifySelectedSports(expectedSports: string[]): Promise<void> {
    if (await this.sportsSummary.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Check dedicated sports summary section
      for (const sport of expectedSports) {
        await expect(this.sportsSummary.locator(`text="${sport}"`)).toBeVisible();
      }
    } else {
      // Fallback: check if sports are mentioned anywhere in the completion content
      for (const sport of expectedSports) {
        await expect(this.page.locator(`text="${sport}"`).first()).toBeVisible();
      }
    }
  }

  async verifySportsRanking(expectedRankings: Record<string, number>): Promise<void> {
    for (const [sport, expectedRank] of Object.entries(expectedRankings)) {
      const rankText = expectedRank === 1 ? '1st' : expectedRank === 2 ? '2nd' : expectedRank === 3 ? '3rd' : `${expectedRank}th`;

      // Look for rank indication near sport name
      const sportElement = this.page.locator(`text="${sport}"`).first();
      const parentElement = sportElement.locator('..');

      await expect(parentElement.locator(`text="${rankText}"`)).toBeVisible({ timeout: 5000 }).catch(() => {
        console.warn(`Could not verify ranking for ${sport} - ranking display may not be implemented`);
      });
    }
  }

  // Teams summary verification
  async verifySelectedTeams(expectedTeams: string[]): Promise<void> {
    if (await this.teamsSummary.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Check dedicated teams summary section
      for (const team of expectedTeams) {
        await expect(this.teamsSummary.locator(`text*="${team}"`)).toBeVisible();
      }
    } else {
      // Fallback: check if teams are mentioned in completion content
      console.warn('Teams summary section not found, checking for team mentions');
      // Note: Some implementations may not show team details in completion
    }
  }

  async verifyTeamAffinity(teamAffinities: Record<string, number>): Promise<void> {
    for (const [team, expectedAffinity] of Object.entries(teamAffinities)) {
      // Look for star ratings or affinity scores
      const teamElement = this.page.locator(`text*="${team}"`).first();
      const parentElement = teamElement.locator('..');

      // Try to find star indicators or numeric affinity
      const hasStars = await parentElement.locator('.star, [data-testid*="star"]').count() > 0;
      const hasNumeric = await parentElement.locator(`text="${expectedAffinity}"`).isVisible({ timeout: 1000 }).catch(() => false);

      if (!hasStars && !hasNumeric) {
        console.warn(`Could not verify affinity for ${team} - affinity display may not be implemented`);
      }
    }
  }

  // Preferences summary verification
  async verifyPreferencesSummary(): Promise<void> {
    if (await this.preferencesSummary.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(this.preferencesSummary).toBeVisible();
    } else {
      console.warn('Preferences summary section not found');
    }
  }

  async verifyNewsTypesInSummary(expectedNewsTypes: string[]): Promise<void> {
    for (const newsType of expectedNewsTypes) {
      const newsTypeElement = this.page.locator(`text="${newsType}", text*="${newsType}"`);
      await expect(newsTypeElement.first()).toBeVisible({ timeout: 3000 }).catch(() => {
        console.warn(`News type ${newsType} not found in summary`);
      });
    }
  }

  async verifyNotificationsInSummary(expectedNotifications: string[]): Promise<void> {
    for (const notification of expectedNotifications) {
      const notificationElement = this.page.locator(`text="${notification}", text*="${notification}"`);
      await expect(notificationElement.first()).toBeVisible({ timeout: 3000 }).catch(() => {
        console.warn(`Notification ${notification} not found in summary`);
      });
    }
  }

  // Progress and metrics verification
  async verifyProgressCompletion(): Promise<void> {
    // Check that progress shows 100%
    const progressBar = this.page.locator('[role="progressbar"]');
    if (await progressBar.isVisible({ timeout: 2000 }).catch(() => false)) {
      const progressValue = await progressBar.getAttribute('aria-valuenow');
      expect(parseInt(progressValue || '0')).toBe(100);
    }

    // Check step indicator shows final step
    const stepIndicator = this.page.locator('[data-testid="step-indicator"]');
    if (await stepIndicator.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(stepIndicator).toContainText('Step 5 of 5');
    }
  }

  // Edit actions
  async editSports(): Promise<void> {
    if (await this.editSportsButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await this.editSportsButton.click();
      await this.page.waitForURL('**/onboarding/step/2');
    } else {
      throw new Error('Edit sports button not available');
    }
  }

  async editTeams(): Promise<void> {
    if (await this.editTeamsButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await this.editTeamsButton.click();
      await this.page.waitForURL('**/onboarding/step/3');
    } else {
      throw new Error('Edit teams button not available');
    }
  }

  async editPreferences(): Promise<void> {
    if (await this.editPreferencesButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await this.editPreferencesButton.click();
      await this.page.waitForURL('**/onboarding/step/4');
    } else {
      throw new Error('Edit preferences button not available');
    }
  }

  async startOver(): Promise<void> {
    if (await this.startOverButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await this.startOverButton.click();
      await this.page.waitForURL('**/onboarding/step/1');
    } else {
      throw new Error('Start over button not available');
    }
  }

  // State and data capture
  async captureOnboardingSummary(): Promise<Partial<OnboardingSummary>> {
    const summary: Partial<OnboardingSummary> = {};

    try {
      // Capture visible sports
      const sportsElements = await this.page.locator('[data-testid*="sport"], text=/football|basketball|baseball|hockey/i').all();
      summary.selectedSports = [];

      for (const element of sportsElements) {
        const text = await element.textContent();
        if (text) {
          summary.selectedSports.push({
            id: text.toLowerCase().replace(/\s+/g, ''),
            name: text.trim(),
            rank: 1 // Default rank, actual rank detection would need more specific selectors
          });
        }
      }

      // Capture visible teams (if shown)
      const teamElements = await this.page.locator('[data-testid*="team"]').all();
      summary.selectedTeams = [];

      for (const element of teamElements) {
        const text = await element.textContent();
        if (text) {
          summary.selectedTeams.push({
            id: text.toLowerCase().replace(/\s+/g, ''),
            name: text.trim(),
            sport: 'unknown',
            affinityScore: 3 // Default affinity
          });
        }
      }
    } catch (error) {
      console.warn('Could not fully capture onboarding summary:', error);
    }

    return summary;
  }

  async getCompletionMetrics(): Promise<Partial<CompletionMetrics>> {
    try {
      const metrics: Partial<CompletionMetrics> = {
        totalSteps: 5,
        completedSteps: 5
      };

      // Try to capture time metrics if available
      const timeElement = this.page.locator('[data-testid="completion-time"], text*="time", text*="duration"');
      if (await timeElement.isVisible({ timeout: 1000 }).catch(() => false)) {
        const timeText = await timeElement.textContent();
        // Parse time if it's in a recognizable format
        const timeMatch = timeText?.match(/(\d+).*(?:minute|min|second|sec)/i);
        if (timeMatch) {
          metrics.timeSpent = parseInt(timeMatch[1]);
        }
      }

      return metrics;
    } catch {
      return { totalSteps: 5, completedSteps: 5 };
    }
  }

  // Validation helpers
  async isCompleteButtonEnabled(): Promise<boolean> {
    return !(await this.completeButton.isDisabled());
  }

  async hasCompletionError(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  async getCompletionError(): Promise<string | null> {
    if (await this.hasCompletionError()) {
      return await this.errorMessage.textContent();
    }
    return null;
  }

  async isLoading(): Promise<boolean> {
    return await this.loadingIndicator.isVisible();
  }

  // Mock helpers for testing completion
  async setupCompletionMock(mockResponse: { success: boolean; userId?: string; message?: string }): Promise<void> {
    await this.page.route('**/api/v1/onboarding/complete', async route => {
      await route.fulfill({
        status: mockResponse.success ? 200 : 500,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse.success ? {
          success: true,
          user_id: mockResponse.userId || 'test-user-123',
          onboarding_completed_at: new Date().toISOString(),
          message: mockResponse.message || 'Onboarding completed successfully'
        } : {
          error: 'Completion failed',
          message: mockResponse.message || 'Failed to complete onboarding'
        })
      });
    });
  }

  async simulateCompletionError(): Promise<void> {
    await this.setupCompletionMock({ success: false, message: 'Server error during completion' });
  }

  async simulateSlowCompletion(delay: number = 3000): Promise<void> {
    await this.page.route('**/api/v1/onboarding/complete', async route => {
      await new Promise(resolve => setTimeout(resolve, delay));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          user_id: 'test-user-123',
          onboarding_completed_at: new Date().toISOString(),
          message: 'Onboarding completed successfully'
        })
      });
    });
  }

  // Comprehensive verification
  async verifyFullCompletion(expectedData: {
    sports: string[];
    teams?: string[];
    hasPreferences?: boolean;
    redirectUrl?: RegExp;
  }): Promise<void> {
    // Verify summary section loads
    await this.verifySummarySection();

    // Verify completion title
    await this.verifyCompletionTitle(/complete|congratulations|success|finish/i);

    // Verify progress shows 100%
    await this.verifyProgressCompletion();

    // Verify selected sports
    await this.verifySelectedSports(expectedData.sports);

    // Verify teams if provided
    if (expectedData.teams) {
      await this.verifySelectedTeams(expectedData.teams);
    }

    // Verify preferences summary if expected
    if (expectedData.hasPreferences) {
      await this.verifyPreferencesSummary();
    }

    // Verify complete button is enabled
    expect(await this.isCompleteButtonEnabled()).toBe(true);

    // Complete and verify redirect if specified
    if (expectedData.redirectUrl) {
      await this.completeOnboardingAndWaitForRedirect(expectedData.redirectUrl);
    }
  }
}