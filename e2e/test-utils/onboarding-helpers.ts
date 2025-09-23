/**
 * Test utilities for onboarding flow testing
 * Provides reusable helpers for Playwright tests
 */

import { Page, Locator, expect } from '@playwright/test';

// Mock data constants
export const MOCK_SPORTS_DATA = [
  { id: 'nfl', name: 'Football', icon: '🏈', isPopular: true, hasTeams: true },
  { id: 'nba', name: 'Basketball', icon: '🏀', isPopular: true, hasTeams: true },
  { id: 'mlb', name: 'Baseball', icon: '⚾', isPopular: true, hasTeams: true },
  { id: 'nhl', name: 'Hockey', icon: '🏒', isPopular: true, hasTeams: true },
  { id: 'mls', name: 'Soccer', icon: '⚽', isPopular: false, hasTeams: true },
  { id: 'tennis', name: 'Tennis', icon: '🎾', isPopular: false, hasTeams: false },
  { id: 'golf', name: 'Golf', icon: '⛳', isPopular: false, hasTeams: false },
];

export const MOCK_TEAMS_DATA = [
  { id: 'patriots', name: 'Patriots', market: 'New England', sport: 'nfl' },
  { id: 'chiefs', name: 'Chiefs', market: 'Kansas City', sport: 'nfl' },
  { id: 'lakers', name: 'Lakers', market: 'Los Angeles', sport: 'nba' },
  { id: 'celtics', name: 'Celtics', market: 'Boston', sport: 'nba' },
  { id: 'redsox', name: 'Red Sox', market: 'Boston', sport: 'mlb' },
  { id: 'bruins', name: 'Bruins', market: 'Boston', sport: 'nhl' },
];

/**
 * Set up standard API mocks for onboarding tests
 */
export async function setupOnboardingMocks(page: Page) {
  // Mock sports API
  await page.route('**/api/v1/onboarding/sports', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          sports: MOCK_SPORTS_DATA,
          total: MOCK_SPORTS_DATA.length,
        },
      }),
    });
  });

  // Mock teams API
  await page.route('**/api/v1/onboarding/teams**', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          teams: MOCK_TEAMS_DATA,
          total: MOCK_TEAMS_DATA.length,
        },
      }),
    });
  });

  // Mock onboarding step API
  await page.route('**/api/v1/onboarding/step', async route => {
    const method = route.request().method();
    if (method === 'GET') {
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
    } else if (method === 'PUT' || method === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            success: true,
            step: 2,
            message: 'Step updated successfully',
          },
        }),
      });
    }
  });

  // Mock completion API
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
}

/**
 * Set up API mocks that simulate failures
 */
export async function setupFailingMocks(page: Page) {
  await page.route('**/api/v1/onboarding/sports', async route => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({
        error: 'Internal server error',
        message: 'Failed to retrieve sports data',
      }),
    });
  });
}

/**
 * Clear browser storage for clean test state
 */
export async function clearBrowserStorage(page: Page) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

/**
 * Sports Selection Test Helpers
 */
export class SportsSelectionHelpers {
  constructor(private page: Page) {}

  async navigateToSportsSelection() {
    await this.page.goto('/onboarding/step/2');
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForSelector('[data-testid^="sport-card-"]', { timeout: 15000 });
  }

  async getSportCard(sportId: string): Promise<Locator> {
    return this.page.locator(`[data-testid="sport-card-${sportId}"]`);
  }

  async clickSport(sportId: string) {
    const card = await this.getSportCard(sportId);
    await card.click();
    await this.page.waitForTimeout(100); // Wait for state update
  }

  async isSportSelected(sportId: string): Promise<boolean> {
    const card = await this.getSportCard(sportId);
    const selected = await card.getAttribute('data-selected');
    return selected === 'true';
  }

  async getSportRank(sportId: string): Promise<number | null> {
    const card = await this.getSportCard(sportId);
    const rankElement = card.locator('p:has-text("st"), p:has-text("nd"), p:has-text("rd"), p:has-text("th")');
    const rankText = await rankElement.textContent();
    if (!rankText) return null;
    const match = rankText.match(/^(\d+)/);
    return match ? parseInt(match[1]) : null;
  }

  async getSelectedSportsCount(): Promise<number> {
    return await this.page.locator('[data-testid^="sport-card-"][data-selected="true"]').count();
  }

  async selectMultipleSports(sportIds: string[]) {
    for (const sportId of sportIds) {
      await this.clickSport(sportId);
    }
  }

  async dragSportToSport(fromSportId: string, toSportId: string) {
    const fromCard = await this.getSportCard(fromSportId);
    const toCard = await this.getSportCard(toSportId);
    await fromCard.dragTo(toCard);
    await this.page.waitForTimeout(500);
  }

  async clickActionButton(buttonText: string) {
    await this.page.click(`button:has-text("${buttonText}")`);
    await this.page.waitForTimeout(200);
  }

  async verifySelectionCount(expectedCount: number) {
    const actualCount = await this.getSelectedSportsCount();
    expect(actualCount).toBe(expectedCount);
  }

  async verifyRankings(expectedRankings: Record<string, number>) {
    for (const [sportId, expectedRank] of Object.entries(expectedRankings)) {
      const actualRank = await this.getSportRank(sportId);
      expect(actualRank).toBe(expectedRank);
    }
  }
}

/**
 * Navigation and Flow Helpers
 */
export class OnboardingFlowHelpers {
  constructor(private page: Page) {}

  async navigateToStep(step: number) {
    await this.page.goto(`/onboarding/step/${step}`);
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForSelector('main', { timeout: 10000 });
  }

  async clickContinue() {
    const continueButton = this.page.locator('button:has-text("Continue"), button:has-text("Get Started")');
    await continueButton.click();
  }

  async clickBack() {
    const backButton = this.page.locator('button:has-text("Back")');
    await backButton.click();
  }

  async isContinueDisabled(): Promise<boolean> {
    const continueButton = this.page.locator('button:has-text("Continue"), button:has-text("Get Started")');
    return await continueButton.isDisabled();
  }

  async getCurrentStep(): Promise<number> {
    const stepText = await this.page.textContent('text=/Step \\d+ of \\d+/');
    const match = stepText?.match(/Step (\d+)/);
    return match ? parseInt(match[1]) : 0;
  }

  async getProgressPercentage(): Promise<number> {
    const progressText = await this.page.textContent('text=/%\\s+complete/');
    const match = progressText?.match(/(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }

  async verifyStepContent(step: number, expectedTitle: RegExp) {
    await expect(this.page.locator('h1')).toContainText(expectedTitle);
    await expect(this.page.locator('text=/Step \\d+ of \\d+/')).toContainText(`Step ${step} of 5`);
  }

  async waitForNavigation(expectedUrl: RegExp) {
    await this.page.waitForURL(expectedUrl);
  }
}

/**
 * Accessibility Test Helpers
 */
export class AccessibilityHelpers {
  constructor(private page: Page) {}

  async checkFocusOrder(): Promise<Array<{ tagName: string; text: string; ariaLabel: string | null }>> {
    const focusableElements = await this.page.locator(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ).all();

    const focusOrder = [];
    for (const element of focusableElements) {
      const tagName = await element.evaluate(el => el.tagName.toLowerCase());
      const text = await element.textContent();
      const ariaLabel = await element.getAttribute('aria-label');

      focusOrder.push({
        tagName,
        text: text?.substring(0, 30) || '',
        ariaLabel,
      });
    }

    return focusOrder;
  }

  async testKeyboardNavigation(steps: number = 5): Promise<Array<string | null>> {
    const navigationResults = [];

    for (let i = 0; i < steps; i++) {
      await this.page.keyboard.press('Tab');
      const focusedElement = await this.page.evaluate(() => {
        return document.activeElement?.getAttribute('data-testid') || 
               document.activeElement?.tagName?.toLowerCase() ||
               null;
      });
      navigationResults.push(focusedElement);
    }

    return navigationResults;
  }

  async verifyAriaLabels(): Promise<boolean> {
    const interactiveElements = await this.page.locator('button, [role="button"], input, select').all();
    
    for (const element of interactiveElements) {
      const text = await element.textContent();
      const ariaLabel = await element.getAttribute('aria-label');
      const ariaLabelledBy = await element.getAttribute('aria-labelledby');
      
      if (!text && !ariaLabel && !ariaLabelledBy) {
        return false; // Found unlabeled interactive element
      }
    }
    
    return true;
  }
}

/**
 * Mobile and Responsive Test Helpers
 */
export class ResponsiveHelpers {
  constructor(private page: Page) {}

  async setMobileViewport() {
    await this.page.setViewportSize({ width: 375, height: 667 });
  }

  async setTabletViewport() {
    await this.page.setViewportSize({ width: 768, height: 1024 });
  }

  async setDesktopViewport() {
    await this.page.setViewportSize({ width: 1280, height: 720 });
  }

  async testTouchInteraction(selector: string) {
    const element = this.page.locator(selector);
    await element.tap();
    await this.page.waitForTimeout(100);
  }

  async verifyTouchTargetSize(selector: string, minSize: number = 44) {
    const element = this.page.locator(selector);
    const box = await element.boundingBox();
    
    if (box) {
      expect(box.width).toBeGreaterThanOrEqual(minSize);
      expect(box.height).toBeGreaterThanOrEqual(minSize);
    }
  }
}

/**
 * Error Handling Test Helpers
 */
export class ErrorHandlingHelpers {
  constructor(private page: Page) {}

  async simulateNetworkError(urlPattern: string) {
    await this.page.route(urlPattern, async route => {
      await route.abort('failed');
    });
  }

  async simulateSlowNetwork(urlPattern: string, delay: number = 5000) {
    await this.page.route(urlPattern, async route => {
      await new Promise(resolve => setTimeout(resolve, delay));
      await route.continue();
    });
  }

  async hasErrorMessage(): Promise<boolean> {
    return await this.page.locator('[data-testid="error-message"], [role="alert"]').isVisible();
  }

  async hasOfflineIndicator(): Promise<boolean> {
    return await this.page.locator('text="Working Offline"').isVisible();
  }

  async hasLoadingIndicator(): Promise<boolean> {
    return await this.page.locator('[data-testid="loading-sports"], .animate-spin').isVisible();
  }
}

/**
 * Visual Testing Helpers
 */
export class VisualTestHelpers {
  constructor(private page: Page) {}

  async takeStepScreenshot(stepNumber: number, variant: string = '') {
    const filename = variant 
      ? `onboarding-step-${stepNumber}-${variant}.png`
      : `onboarding-step-${stepNumber}.png`;
    
    await expect(this.page).toHaveScreenshot(filename);
  }

  async takeElementScreenshot(selector: string, filename: string) {
    const element = this.page.locator(selector);
    await expect(element).toHaveScreenshot(filename);
  }

  async enableDarkMode() {
    await this.page.emulateMedia({ colorScheme: 'dark' });
  }

  async enableHighContrast() {
    await this.page.emulateMedia({ colorScheme: 'dark', forcedColors: 'active' });
  }

  async enableReducedMotion() {
    await this.page.emulateMedia({ reducedMotion: 'reduce' });
  }
}

/**
 * Performance Test Helpers
 */
export class PerformanceHelpers {
  constructor(private page: Page) {}

  async measurePageLoadTime(): Promise<number> {
    const startTime = Date.now();
    await this.page.waitForLoadState('networkidle');
    return Date.now() - startTime;
  }

  async measureInteractionTime(action: () => Promise<void>): Promise<number> {
    const startTime = Date.now();
    await action();
    return Date.now() - startTime;
  }

  async collectMetrics() {
    return await this.page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
      };
    });
  }
}