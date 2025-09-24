/**
 * Team Selection Test Utilities
 * Specialized helpers for team selection step testing
 */

import { Page, Locator, expect } from '@playwright/test';
import { WaitStrategies } from './wait-strategies';

export interface TeamData {
  id: string;
  name: string;
  market: string;
  sportId: string;
  league: string;
  logo: string;
}

export interface TeamSelection {
  teamId: string;
  isSelected: boolean;
  affinityScore: number;
}

/**
 * Team Selection Test Helper Class
 */
export class TeamSelectionTestHelpers {
  private waitStrategies: WaitStrategies;

  constructor(private page: Page) {
    this.waitStrategies = new WaitStrategies(page);
  }

  // Element getters
  get teamsContainer(): Locator {
    return this.page.locator('[data-testid="teams-container"]');
  }

  get virtualizedList(): Locator {
    return this.page.locator('[data-testid="virtualized-team-list"]');
  }

  get noTeamsMessage(): Locator {
    return this.page.locator('text="No teams available for selected sports"');
  }

  get noSportsSelectedMessage(): Locator {
    return this.page.locator('text="Please go back and select your sports first."');
  }

  get loadingIndicator(): Locator {
    return this.page.locator('text="Loading teams...", text="Loading..."');
  }

  get errorMessage(): Locator {
    return this.page.locator('[data-testid="teams-error"]');
  }

  get searchInput(): Locator {
    return this.page.locator('[data-testid="team-search-input"]');
  }

  get leagueFilter(): Locator {
    return this.page.locator('[data-testid="league-filter"]');
  }

  // Team interaction helpers
  async waitForTeamsToLoad(timeout: number = 15000): Promise<void> {
    try {
      // Wait for either teams container or error states
      await this.waitStrategies.waitForAny([
        () => this.waitStrategies.waitForElement(this.teamsContainer, 'visible', timeout),
        () => this.waitStrategies.waitForElement(this.noSportsSelectedMessage, 'visible', timeout),
        () => this.waitStrategies.waitForElement(this.errorMessage, 'visible', timeout)
      ], timeout);

      // If teams container is visible, wait for actual teams to load
      if (await this.teamsContainer.isVisible()) {
        // Wait for virtualized list or team items to appear
        await this.waitStrategies.waitForAny([
          () => this.waitStrategies.waitForElement(this.virtualizedList, 'visible', 5000),
          () => this.waitStrategies.waitForElement(this.page.locator('[data-testid^="team-item-"]').first(), 'visible', 5000)
        ], 10000);
      }
    } catch (error) {
      // Check for loading state and extend timeout if needed
      if (await this.loadingIndicator.isVisible()) {
        await this.waitStrategies.waitForElement(this.teamsContainer, 'visible', timeout + 10000);
      } else {
        throw error;
      }
    }
  }

  async findTeamElement(teamName: string): Promise<Locator> {
    // Try different selectors to find the team
    const selectors = [
      `[data-testid="team-item-${teamName.toLowerCase().replace(/\s+/g, '-')}"]`,
      `text="${teamName}"`,
      `text*="${teamName}"`,
      `text="${teamName.split(' ').pop()}"` // Try just the team name without market
    ];

    for (const selector of selectors) {
      const element = this.page.locator(selector).first();
      if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
        return element;
      }
    }

    throw new Error(`Team "${teamName}" not found. Available teams may not include this team.`);
  }

  async selectTeam(teamName: string): Promise<void> {
    await this.waitForTeamsToLoad();

    const teamElement = await this.findTeamElement(teamName);
    await teamElement.scrollIntoViewIfNeeded();

    // Find the checkbox associated with this team
    const checkbox = teamElement.locator('..').locator('input[type="checkbox"]').first();

    // If checkbox is not found, try clicking on the team element itself
    if (!await checkbox.isVisible({ timeout: 1000 }).catch(() => false)) {
      await teamElement.click();
    } else {
      await checkbox.click();
    }

    // Wait for selection to register
    await this.page.waitForTimeout(200);
  }

  async deselectTeam(teamName: string): Promise<void> {
    await this.waitForTeamsToLoad();

    const teamElement = await this.findTeamElement(teamName);
    const checkbox = teamElement.locator('..').locator('input[type="checkbox"]').first();

    if (await checkbox.isChecked()) {
      await checkbox.click();
      await this.page.waitForTimeout(200);
    }
  }

  async isTeamSelected(teamName: string): Promise<boolean> {
    try {
      const teamElement = await this.findTeamElement(teamName);
      const checkbox = teamElement.locator('..').locator('input[type="checkbox"]').first();

      if (await checkbox.isVisible({ timeout: 1000 }).catch(() => false)) {
        return await checkbox.isChecked();
      }

      // Alternative: check for selected styling
      const hasSelectedClass = await teamElement.locator('..').getAttribute('class');
      return hasSelectedClass?.includes('selected') || hasSelectedClass?.includes('checked') || false;
    } catch {
      return false;
    }
  }

  async setTeamAffinity(teamName: string, score: number): Promise<void> {
    if (score < 1 || score > 5) {
      throw new Error('Affinity score must be between 1 and 5');
    }

    await this.waitForTeamsToLoad();

    const teamElement = await this.findTeamElement(teamName);
    await teamElement.scrollIntoViewIfNeeded();

    // Ensure team is selected first
    if (!await this.isTeamSelected(teamName)) {
      await this.selectTeam(teamName);
      await this.page.waitForTimeout(300); // Wait for affinity controls to appear
    }

    // Find star rating controls (should be visible after selection)
    const starControls = teamElement.locator('..').locator('[data-testid^="star-"], button[aria-label*="star"]');

    if (await starControls.count() > 0) {
      const starButton = starControls.nth(score - 1);
      await starButton.click();
    } else {
      // Alternative: look for generic rating buttons
      const ratingButtons = teamElement.locator('..').locator('button').all();
      const buttons = await ratingButtons;

      if (buttons.length >= score) {
        await buttons[score - 1].click();
      } else {
        console.warn(`Could not find affinity controls for team: ${teamName}`);
      }
    }

    await this.page.waitForTimeout(200);
  }

  async getTeamAffinity(teamName: string): Promise<number> {
    try {
      const teamElement = await this.findTeamElement(teamName);

      // Look for active star indicators
      const activeStars = await teamElement.locator('..').locator('[data-testid^="star-"][data-active="true"], .star-active').count();

      if (activeStars > 0) {
        return activeStars;
      }

      // Alternative: check for aria-valuenow on rating component
      const ratingElement = teamElement.locator('..').locator('[role="slider"], [aria-valuenow]').first();
      if (await ratingElement.isVisible({ timeout: 1000 }).catch(() => false)) {
        const value = await ratingElement.getAttribute('aria-valuenow');
        return value ? parseInt(value) : 0;
      }

      return 0;
    } catch {
      return 0;
    }
  }

  async selectMultipleTeams(teamNames: string[]): Promise<void> {
    for (const teamName of teamNames) {
      await this.selectTeam(teamName);
    }
  }

  async getSelectedTeamsCount(): Promise<number> {
    try {
      // Count checked checkboxes in teams container
      const checkedBoxes = this.teamsContainer.locator('input[type="checkbox"]:checked');
      return await checkedBoxes.count();
    } catch {
      return 0;
    }
  }

  async getSelectedTeams(): Promise<string[]> {
    const selectedTeams: string[] = [];

    try {
      const teamElements = await this.teamsContainer.locator('[data-testid^="team-item-"]').all();

      for (const teamElement of teamElements) {
        const checkbox = teamElement.locator('input[type="checkbox"]');
        if (await checkbox.isChecked()) {
          const teamText = await teamElement.textContent();
          if (teamText) {
            selectedTeams.push(teamText.trim());
          }
        }
      }
    } catch (error) {
      console.warn('Could not get selected teams:', error);
    }

    return selectedTeams;
  }

  // Search and filter functionality
  async searchTeams(query: string): Promise<void> {
    if (await this.searchInput.isVisible({ timeout: 1000 }).catch(() => false)) {
      await this.searchInput.fill(query);
      await this.page.waitForTimeout(500); // Wait for search results
    } else {
      console.warn('Team search functionality not implemented in current UI');
    }
  }

  async filterByLeague(league: string): Promise<void> {
    if (await this.leagueFilter.isVisible({ timeout: 1000 }).catch(() => false)) {
      await this.leagueFilter.selectOption(league);
      await this.page.waitForTimeout(500);
    } else {
      console.warn('League filter functionality not implemented in current UI');
    }
  }

  async clearSearch(): Promise<void> {
    if (await this.searchInput.isVisible({ timeout: 1000 }).catch(() => false)) {
      await this.searchInput.fill('');
      await this.page.waitForTimeout(500);
    }
  }

  // Validation helpers
  async verifyTeamVisible(teamName: string): Promise<void> {
    const teamElement = await this.findTeamElement(teamName);
    await expect(teamElement).toBeVisible();
  }

  async verifyTeamSelected(teamName: string): Promise<void> {
    const isSelected = await this.isTeamSelected(teamName);
    expect(isSelected).toBe(true);
  }

  async verifyTeamNotSelected(teamName: string): Promise<void> {
    const isSelected = await this.isTeamSelected(teamName);
    expect(isSelected).toBe(false);
  }

  async verifySelectedCount(expectedCount: number): Promise<void> {
    const actualCount = await this.getSelectedTeamsCount();
    expect(actualCount).toBe(expectedCount);
  }

  async verifyTeamAffinity(teamName: string, expectedScore: number): Promise<void> {
    const actualScore = await this.getTeamAffinity(teamName);
    expect(actualScore).toBe(expectedScore);
  }

  // State checking helpers
  async hasNoSportsSelected(): Promise<boolean> {
    return await this.noSportsSelectedMessage.isVisible();
  }

  async hasNoTeamsAvailable(): Promise<boolean> {
    return await this.noTeamsMessage.isVisible();
  }

  async isLoading(): Promise<boolean> {
    return await this.loadingIndicator.isVisible();
  }

  async hasError(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  async getAvailableTeams(): Promise<string[]> {
    await this.waitForTeamsToLoad();

    const teams: string[] = [];
    try {
      const teamElements = await this.teamsContainer.locator('[data-testid^="team-item-"]').all();

      for (const teamElement of teamElements) {
        const text = await teamElement.textContent();
        if (text) {
          teams.push(text.trim());
        }
      }
    } catch (error) {
      console.warn('Could not get available teams:', error);
    }

    return teams;
  }

  // Virtualized list helpers (for large team lists)
  async scrollToTeam(teamName: string): Promise<void> {
    // If using virtualized list, might need to scroll to make team visible
    if (await this.virtualizedList.isVisible({ timeout: 1000 }).catch(() => false)) {
      // Scroll within the virtualized container
      let found = false;
      let attempts = 0;
      const maxAttempts = 20;

      while (!found && attempts < maxAttempts) {
        try {
          const teamElement = await this.findTeamElement(teamName);
          await teamElement.scrollIntoViewIfNeeded();
          found = true;
        } catch {
          // Scroll down within the virtualized list
          await this.virtualizedList.evaluate(el => el.scrollBy(0, 200));
          await this.page.waitForTimeout(200);
          attempts++;
        }
      }

      if (!found) {
        throw new Error(`Team "${teamName}" not found after scrolling through list`);
      }
    }
  }

  // Mock data helpers for testing
  async setupTeamsMockData(teams: TeamData[]): Promise<void> {
    await this.page.route('**/api/v1/onboarding/teams**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(teams)
      });
    });
  }

  async simulateTeamsApiError(): Promise<void> {
    await this.page.route('**/api/v1/onboarding/teams**', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error',
          message: 'Failed to load teams'
        })
      });
    });
  }

  async simulateSlowTeamsResponse(delay: number = 3000): Promise<void> {
    await this.page.route('**/api/v1/onboarding/teams**', async route => {
      await new Promise(resolve => setTimeout(resolve, delay));
      await route.continue();
    });
  }
}