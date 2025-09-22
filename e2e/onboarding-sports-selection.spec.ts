/**
 * Comprehensive Playwright tests for onboarding flow with special focus on sports selection
 * Tests sports card interactions, drag-and-drop, accessibility, and mobile responsiveness
 */

import { test, expect, Page, Locator } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

// Mock sports data for testing
const MOCK_SPORTS = [
  { id: 'nfl', name: 'Football', icon: '🏈', isPopular: true, hasTeams: true },
  { id: 'nba', name: 'Basketball', icon: '🏀', isPopular: true, hasTeams: true },
  { id: 'mlb', name: 'Baseball', icon: '⚾', isPopular: true, hasTeams: true },
  { id: 'nhl', name: 'Hockey', icon: '🏒', isPopular: true, hasTeams: true },
  { id: 'mls', name: 'Soccer', icon: '⚽', isPopular: false, hasTeams: true },
  { id: 'tennis', name: 'Tennis', icon: '🎾', isPopular: false, hasTeams: false },
  { id: 'golf', name: 'Golf', icon: '⛳', isPopular: false, hasTeams: false },
];

const MOCK_TEAMS = [
  { id: 'patriots', name: 'Patriots', market: 'New England', sport: 'nfl' },
  { id: 'chiefs', name: 'Chiefs', market: 'Kansas City', sport: 'nfl' },
  { id: 'lakers', name: 'Lakers', market: 'Los Angeles', sport: 'nba' },
  { id: 'celtics', name: 'Celtics', market: 'Boston', sport: 'nba' },
];

/**
 * Page Object Model for Onboarding Sports Selection
 */
class SportsSelectionPageObject {
  constructor(private page: Page) {}

  // Navigation methods
  async goto(step: number = 2) {
    await this.page.goto(`/onboarding/step/${step}`);
    await this.waitForPageLoad();
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    // First wait for the main content to load
    await this.page.waitForSelector('main', { timeout: 10000 });
    // Then wait for either sports cards or loading indicator
    try {
      await this.page.waitForSelector('[data-testid^="sport-card-"], [data-testid="loading-sports"]', { timeout: 15000 });
    } catch (error) {
      console.log('Neither sports cards nor loading indicator found. Page content:', await this.page.textContent('body'));
      throw error;
    }
  }

  // Sport card interaction methods
  async getSportCard(sportId: string): Promise<Locator> {
    return this.page.locator(`[data-testid="sport-card-${sportId}"]`);
  }

  async clickSportCard(sportId: string) {
    const card = await this.getSportCard(sportId);
    await card.click();
    // Wait for selection state to update
    await this.page.waitForTimeout(100);
  }

  async isSportSelected(sportId: string): Promise<boolean> {
    const card = await this.getSportCard(sportId);
    const selected = await card.getAttribute('data-selected');
    return selected === 'true';
  }

  async getSportRank(sportId: string): Promise<number | null> {
    const card = await this.getSportCard(sportId);
    const rankText = await card.locator('p:has-text("st", "nd", "rd", "th")').textContent();
    if (!rankText) return null;
    const match = rankText.match(/^(\d+)/);
    return match ? parseInt(match[1]) : null;
  }

  async getSelectedSportsCount(): Promise<number> {
    const selectedCards = await this.page.locator('[data-testid^="sport-card-"][data-selected="true"]').count();
    return selectedCards;
  }

  async getAllSportCards(): Promise<Locator> {
    return this.page.locator('[data-testid^="sport-card-"]');
  }

  // Drag and drop methods
  async dragSportToPosition(fromSportId: string, toSportId: string) {
    const fromCard = await this.getSportCard(fromSportId);
    const toCard = await this.getSportCard(toSportId);
    await fromCard.dragTo(toCard);
    await this.page.waitForTimeout(500); // Wait for drag operation to complete
  }

  async dragSportByHandle(sportId: string, targetSportId: string) {
    const sourceHandle = this.page.locator(`[data-testid="sport-card-${sportId}"] [data-drag-handle="true"]`);
    const targetCard = await this.getSportCard(targetSportId);
    await sourceHandle.dragTo(targetCard);
    await this.page.waitForTimeout(500);
  }

  // Button interaction methods
  async clickSelectAll() {
    await this.page.click('button:has-text("Select All")');
    await this.page.waitForTimeout(200);
  }

  async clickClearAll() {
    await this.page.click('button:has-text("Clear All")');
    await this.page.waitForTimeout(200);
  }

  async clickPopularSports() {
    await this.page.click('button:has-text("Popular Sports")');
    await this.page.waitForTimeout(200);
  }

  async clickContinue() {
    await this.page.click('button:has-text("Continue")');
  }

  async clickBack() {
    await this.page.click('button:has-text("Back")');
  }

  async isContinueDisabled(): Promise<boolean> {
    const continueButton = this.page.locator('button:has-text("Continue")');
    return await continueButton.isDisabled();
  }

  // Status and validation methods
  async getSelectionStatusText(): Promise<string> {
    return await this.page.locator('text=/\d+ sports selected/').textContent() || '';
  }

  async getProgressPercentage(): Promise<number> {
    const progressText = await this.page.locator('text=/%\s+complete/').textContent();
    const match = progressText?.match(/(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }

  async getStepIndicator(): Promise<string> {
    return await this.page.locator('text=/Step \d+ of \d+/').textContent() || '';
  }

  // Accessibility and keyboard navigation
  async navigateWithKeyboard(sportId: string, key: string) {
    const card = await this.getSportCard(sportId);
    await card.focus();
    await this.page.keyboard.press(key);
  }

  async selectSportWithKeyboard(sportId: string) {
    const card = await this.getSportCard(sportId);
    await card.focus();
    await this.page.keyboard.press('Enter');
  }

  async checkAccessibilityAttributes(sportId: string) {
    const card = await this.getSportCard(sportId);
    const role = await card.getAttribute('role');
    const ariaSelected = await card.getAttribute('aria-selected');
    const ariaLabel = await card.getAttribute('aria-label');
    const tabIndex = await card.getAttribute('tabindex');
    
    return { role, ariaSelected, ariaLabel, tabIndex };
  }

  // Error state methods
  async hasErrorState(): Promise<boolean> {
    return await this.page.locator('[data-testid="error-message"]').isVisible();
  }

  async hasOfflineIndicator(): Promise<boolean> {
    return await this.page.locator('text="Working Offline"').isVisible();
  }

  // Layout and responsive methods
  async isLayoutResponsive(): Promise<boolean> {
    const layout = this.page.locator('[data-testid="onboarding-layout"]');
    return await layout.isVisible();
  }
}

/**
 * Test setup and mock configuration
 */
test.beforeEach(async ({ page }) => {
  // Set up API mocks for reliable testing
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

  // Clear local storage safely - only if the page has loaded
  try {
    await page.goto('http://localhost:8080');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  } catch (error) {
    // Ignore localStorage clearing errors for now
    console.log('Could not clear storage:', error);
  }
});

test.describe('Onboarding Sports Selection - Core Functionality', () => {
  let sportsPage: SportsSelectionPageObject;

  test.beforeEach(async ({ page }) => {
    sportsPage = new SportsSelectionPageObject(page);
  });

  test('displays sports selection step correctly', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Verify page structure
    await expect(page.locator('h1')).toContainText('Choose Your Sports');
    await expect(page.locator('text=Select and rank your favorite sports')).toBeVisible();
    await expect(page.locator('text=Step 2 of 5')).toBeVisible();
    
    // Verify progress indicator
    const progressPercentage = await sportsPage.getProgressPercentage();
    expect(progressPercentage).toBeGreaterThan(0);
    
    // Verify sports cards are loaded
    const sportsCount = await (await sportsPage.getAllSportCards()).count();
    expect(sportsCount).toBeGreaterThan(0);
  });

  test('sports cards are clickable and show visual feedback', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Initially no sports should be selected
    expect(await sportsPage.getSelectedSportsCount()).toBe(0);
    expect(await sportsPage.isContinueDisabled()).toBe(true);
    
    // Click a sport card
    await sportsPage.clickSportCard('nfl');
    
    // Verify selection state
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
    expect(await sportsPage.getSelectedSportsCount()).toBe(1);
    expect(await sportsPage.getSportRank('nfl')).toBe(1);
    expect(await sportsPage.isContinueDisabled()).toBe(false);
    
    // Verify status text updates
    const statusText = await sportsPage.getSelectionStatusText();
    expect(statusText).toContain('1 sports selected');
  });

  test('supports multiple sport selections with ranking', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Select multiple sports
    await sportsPage.clickSportCard('nfl');
    await sportsPage.clickSportCard('nba');
    await sportsPage.clickSportCard('mlb');
    
    // Verify selections and rankings
    expect(await sportsPage.getSelectedSportsCount()).toBe(3);
    expect(await sportsPage.getSportRank('nfl')).toBe(1);
    expect(await sportsPage.getSportRank('nba')).toBe(2);
    expect(await sportsPage.getSportRank('mlb')).toBe(3);
    
    // Verify all are marked as selected
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
    expect(await sportsPage.isSportSelected('nba')).toBe(true);
    expect(await sportsPage.isSportSelected('mlb')).toBe(true);
  });

  test('allows deselecting sports', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Select and then deselect a sport
    await sportsPage.clickSportCard('nfl');
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
    
    await sportsPage.clickSportCard('nfl');
    expect(await sportsPage.isSportSelected('nfl')).toBe(false);
    expect(await sportsPage.getSelectedSportsCount()).toBe(0);
    expect(await sportsPage.isContinueDisabled()).toBe(true);
  });

  test('quick selection buttons work correctly', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Test Popular Sports button
    await sportsPage.clickPopularSports();
    const popularCount = await sportsPage.getSelectedSportsCount();
    expect(popularCount).toBeGreaterThan(0);
    
    // Test Clear All button
    await sportsPage.clickClearAll();
    expect(await sportsPage.getSelectedSportsCount()).toBe(0);
    
    // Test Select All button
    await sportsPage.clickSelectAll();
    const allCount = await sportsPage.getSelectedSportsCount();
    expect(allCount).toBe(MOCK_SPORTS.length);
  });

  test('navigation works correctly', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Select a sport to enable continue
    await sportsPage.clickSportCard('nfl');
    
    // Test continue navigation
    await sportsPage.clickContinue();
    await page.waitForURL('**/onboarding/step/3');
    
    // Test back navigation
    await sportsPage.clickBack();
    await page.waitForURL('**/onboarding/step/2');
    
    // Verify selection persists
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
  });
});

test.describe('Onboarding Sports Selection - Drag and Drop', () => {
  let sportsPage: SportsSelectionPageObject;

  test.beforeEach(async ({ page }) => {
    sportsPage = new SportsSelectionPageObject(page);
  });

  test('supports drag and drop reordering of selected sports', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Select multiple sports first
    await sportsPage.clickSportCard('nfl');
    await sportsPage.clickSportCard('nba');
    await sportsPage.clickSportCard('mlb');
    
    // Verify initial order
    expect(await sportsPage.getSportRank('nfl')).toBe(1);
    expect(await sportsPage.getSportRank('nba')).toBe(2);
    expect(await sportsPage.getSportRank('mlb')).toBe(3);
    
    // Drag NBA to first position
    await sportsPage.dragSportByHandle('nba', 'nfl');
    
    // Verify new order
    expect(await sportsPage.getSportRank('nba')).toBe(1);
    expect(await sportsPage.getSportRank('nfl')).toBe(2);
    expect(await sportsPage.getSportRank('mlb')).toBe(3);
  });

  test('drag handle is separate from card click area', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Click the drag handle should not select the sport
    const dragHandle = page.locator('[data-testid="sport-card-nfl"] [data-drag-handle="true"]');
    await dragHandle.click();
    
    // Sport should not be selected
    expect(await sportsPage.isSportSelected('nfl')).toBe(false);
    
    // Click the card itself should select the sport
    await sportsPage.clickSportCard('nfl');
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
  });
});

test.describe('Onboarding Sports Selection - Accessibility', () => {
  let sportsPage: SportsSelectionPageObject;

  test.beforeEach(async ({ page }) => {
    sportsPage = new SportsSelectionPageObject(page);
    await injectAxe(page);
  });

  test('sports selection step is accessible', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Run comprehensive accessibility check
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
      rules: {
        'color-contrast': { enabled: true },
        'keyboard-navigation': { enabled: true },
        'focus-management': { enabled: true },
      },
    });
  });

  test('sport cards have proper accessibility attributes', async ({ page }) => {
    await sportsPage.goto(2);
    
    const attrs = await sportsPage.checkAccessibilityAttributes('nfl');
    
    expect(attrs.role).toBe('button');
    expect(attrs.tabIndex).toBe('0');
    expect(attrs.ariaSelected).toBe('false');
    expect(attrs.ariaLabel).toContain('Select Football');
    
    // After selection
    await sportsPage.clickSportCard('nfl');
    const selectedAttrs = await sportsPage.checkAccessibilityAttributes('nfl');
    
    expect(selectedAttrs.ariaSelected).toBe('true');
    expect(selectedAttrs.ariaLabel).toContain('Deselect Football');
    expect(selectedAttrs.ariaLabel).toContain('ranked #1');
  });

  test('supports keyboard navigation and selection', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Tab to first sport card
    await page.keyboard.press('Tab');
    
    // Use Enter to select
    await sportsPage.selectSportWithKeyboard('nfl');
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
    
    // Use Space to deselect
    const card = await sportsPage.getSportCard('nfl');
    await card.focus();
    await page.keyboard.press('Space');
    expect(await sportsPage.isSportSelected('nfl')).toBe(false);
  });

  test('maintains focus management during interactions', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Focus on a sport card
    const card = await sportsPage.getSportCard('nfl');
    await card.focus();
    
    // Select with keyboard
    await page.keyboard.press('Enter');
    
    // Focus should remain on the card
    const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
    expect(focusedElement).toBe('sport-card-nfl');
  });

  test('provides proper screen reader announcements', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Check for proper heading structure
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);
    
    // Check for status announcements
    await sportsPage.clickSportCard('nfl');
    const statusText = await sportsPage.getSelectionStatusText();
    expect(statusText).toBeTruthy();
    
    // Check for progress indication
    await expect(page.locator('[role="progressbar"], [aria-label*="progress"]')).toBeVisible();
  });
});

test.describe('Onboarding Sports Selection - Mobile and Responsive', () => {
  let sportsPage: SportsSelectionPageObject;

  test.beforeEach(async ({ page }) => {
    sportsPage = new SportsSelectionPageObject(page);
  });

  test('works correctly on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await sportsPage.goto(2);
    
    // Verify layout adapts to mobile
    expect(await sportsPage.isLayoutResponsive()).toBe(true);
    
    // Test card interactions on mobile
    await sportsPage.clickSportCard('nfl');
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
    
    // Test navigation buttons are accessible
    expect(await sportsPage.isContinueDisabled()).toBe(false);
    
    // Test quick action buttons work on mobile
    await sportsPage.clickPopularSports();
    expect(await sportsPage.getSelectedSportsCount()).toBeGreaterThan(1);
  });

  test('touch interactions work correctly', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await sportsPage.goto(2);
    
    // Simulate touch interaction
    const card = await sportsPage.getSportCard('nfl');
    await card.tap();
    
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
  });

  test('adapts to different screen sizes', async ({ page }) => {
    const viewports = [
      { width: 320, height: 568 }, // Small mobile
      { width: 768, height: 1024 }, // Tablet
      { width: 1024, height: 768 }, // Tablet landscape
      { width: 1920, height: 1080 }, // Desktop
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await sportsPage.goto(2);
      
      // Verify layout works at all sizes
      expect(await sportsPage.isLayoutResponsive()).toBe(true);
      
      // Verify interactions work
      await sportsPage.clickSportCard('nfl');
      expect(await sportsPage.isSportSelected('nfl')).toBe(true);
      
      // Clear selection for next iteration
      await sportsPage.clickSportCard('nfl');
    }
  });
});

test.describe('Onboarding Sports Selection - Error Handling', () => {
  let sportsPage: SportsSelectionPageObject;

  test.beforeEach(async ({ page }) => {
    sportsPage = new SportsSelectionPageObject(page);
  });

  test('handles API failures gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/v1/onboarding/sports', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error',
        }),
      });
    });
    
    await sportsPage.goto(2);
    
    // Should show offline indicator
    expect(await sportsPage.hasOfflineIndicator()).toBe(true);
    
    // Should still allow interactions with fallback data
    await sportsPage.clickSportCard('nfl');
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
  });

  test('maintains state during network interruptions', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Select sports
    await sportsPage.clickSportCard('nfl');
    await sportsPage.clickSportCard('nba');
    
    // Simulate network failure for save operation
    await page.route('**/api/v1/onboarding/step', async route => {
      await route.abort('failed');
    });
    
    // Continue should still work (using localStorage)
    await sportsPage.clickContinue();
    
    // Should navigate despite API failure
    await page.waitForURL('**/onboarding/step/3');
  });
});

test.describe('Onboarding Sports Selection - Performance', () => {
  let sportsPage: SportsSelectionPageObject;

  test.beforeEach(async ({ page }) => {
    sportsPage = new SportsSelectionPageObject(page);
  });

  test('loads quickly and responds to interactions promptly', async ({ page }) => {
    const startTime = Date.now();
    await sportsPage.goto(2);
    const loadTime = Date.now() - startTime;
    
    // Should load within reasonable time
    expect(loadTime).toBeLessThan(5000);
    
    // Interactions should be responsive
    const interactionStart = Date.now();
    await sportsPage.clickSportCard('nfl');
    const interactionTime = Date.now() - interactionStart;
    
    expect(interactionTime).toBeLessThan(1000);
    expect(await sportsPage.isSportSelected('nfl')).toBe(true);
  });

  test('handles rapid interactions without issues', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Rapidly select multiple sports
    const sports = ['nfl', 'nba', 'mlb', 'nhl'];
    for (const sport of sports) {
      await sportsPage.clickSportCard(sport);
    }
    
    // All should be selected correctly
    expect(await sportsPage.getSelectedSportsCount()).toBe(sports.length);
    
    // Rankings should be correct
    for (let i = 0; i < sports.length; i++) {
      expect(await sportsPage.getSportRank(sports[i])).toBe(i + 1);
    }
  });
});

test.describe('Onboarding Sports Selection - Visual Regression', () => {
  let sportsPage: SportsSelectionPageObject;

  test.beforeEach(async ({ page }) => {
    sportsPage = new SportsSelectionPageObject(page);
  });

  test('sports selection step visual baseline', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Take screenshot of initial state
    await expect(page).toHaveScreenshot('sports-selection-initial.png');
  });

  test('selected sports visual state', async ({ page }) => {
    await sportsPage.goto(2);
    
    // Select some sports
    await sportsPage.clickSportCard('nfl');
    await sportsPage.clickSportCard('nba');
    
    // Take screenshot of selected state
    await expect(page).toHaveScreenshot('sports-selection-with-selections.png');
  });

  test('mobile sports selection visual baseline', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await sportsPage.goto(2);
    
    await expect(page).toHaveScreenshot('sports-selection-mobile.png');
  });

  test('dark mode sports selection', async ({ page }) => {
    // Enable dark mode
    await page.emulateMedia({ colorScheme: 'dark' });
    await sportsPage.goto(2);
    
    await expect(page).toHaveScreenshot('sports-selection-dark-mode.png');
  });
});
