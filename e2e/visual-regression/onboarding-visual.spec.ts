/**
 * Visual Regression Tests for Onboarding Flow
 *
 * Tests visual consistency and performance across different viewport sizes
 * and user interactions during the onboarding process.
 */

import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

// Visual test configuration
const VISUAL_TEST_CONFIG = {
  threshold: 0.3, // 30% pixel difference threshold
  animations: 'disabled' as const,
  clip: { x: 0, y: 0, width: 1280, height: 720 },
};

// Viewport configurations for responsive testing
const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 720 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 667 },
];

// Mock data for consistent visual tests
const MOCK_TEAM_DATA = [
  { id: 'chiefs', name: 'Kansas City Chiefs', league: 'NFL', logo: '🏈' },
  { id: 'lakers', name: 'Los Angeles Lakers', league: 'NBA', logo: '🏀' },
  { id: 'yankees', name: 'New York Yankees', league: 'MLB', logo: '⚾' },
];

test.describe('Onboarding Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set up consistent test environment
    await page.addInitScript(() => {
      // Disable animations for consistent screenshots
      const style = document.createElement('style');
      style.textContent = `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `;
      document.head.appendChild(style);

      // Mock Date for consistent timestamps
      const mockDate = new Date('2024-01-15T10:00:00Z');
      const originalDate = Date;
      globalThis.Date = class extends originalDate {
        constructor(...args: any[]) {
          if (args.length === 0) {
            super(mockDate.getTime());
          } else {
            super(...args);
          }
        }
        static now() {
          return mockDate.getTime();
        }
      } as any;
    });

    // Mock API responses for consistent data
    await page.route('**/api/onboarding/**', async (route) => {
      const url = route.request().url();

      if (url.includes('/teams')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: MOCK_TEAM_DATA }),
        });
      } else if (url.includes('/status')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            hasCompletedOnboarding: false,
            currentStep: 1,
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Mock Firebase Auth
    await page.addInitScript(() => {
      (window as any).__FIREBASE_AUTH_MOCK__ = {
        isAuthenticated: true,
        user: { uid: 'test-user-123' },
      };
    });
  });

  VIEWPORTS.forEach(({ name, width, height }) => {
    test.describe(`${name} viewport (${width}x${height})`, () => {
      test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width, height });
      });

      test(`should render welcome step correctly on ${name}`, async ({ page }) => {
        await page.goto('/onboarding/step/1');

        // Wait for content to load
        await expect(page.getByText('Welcome to Corner League Media')).toBeVisible();

        // Take screenshot with performance timing
        const startTime = performance.now();
        await page.screenshot({
          path: `test-results/visual/onboarding-welcome-${name}.png`,
          ...VISUAL_TEST_CONFIG,
        });
        const screenshotTime = performance.now() - startTime;

        // Screenshot should be taken quickly (under 500ms)
        expect(screenshotTime).toBeLessThan(500);

        // Compare against baseline
        await expect(page).toHaveScreenshot(`onboarding-welcome-${name}.png`, {
          threshold: VISUAL_TEST_CONFIG.threshold,
        });
      });

      test(`should render sports selection correctly on ${name}`, async ({ page }) => {
        await page.goto('/onboarding/step/2');

        // Wait for sports grid to load
        await expect(page.getByText('Select Your Sports')).toBeVisible();
        await page.waitForSelector('[data-testid="sports-grid"]', { timeout: 5000 });

        // Test loading state performance
        const loadingStart = performance.now();
        await page.screenshot({
          path: `test-results/visual/sports-selection-${name}.png`,
          ...VISUAL_TEST_CONFIG,
        });
        const loadingTime = performance.now() - loadingStart;

        expect(loadingTime).toBeLessThan(500);

        await expect(page).toHaveScreenshot(`sports-selection-${name}.png`, {
          threshold: VISUAL_TEST_CONFIG.threshold,
        });
      });

      test(`should render team selection correctly on ${name}`, async ({ page }) => {
        // Set up sports selection in localStorage
        await page.addInitScript(() => {
          localStorage.setItem('corner-league-onboarding', JSON.stringify({
            selectedSports: [
              { sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true },
            ],
          }));
        });

        await page.goto('/onboarding/step/3');

        // Wait for teams to load
        await expect(page.getByText('Select Your Teams')).toBeVisible();
        await page.waitForSelector('[data-testid="teams-container"]', { timeout: 5000 });

        // Performance check for team list rendering
        const renderStart = performance.now();
        await page.screenshot({
          path: `test-results/visual/team-selection-${name}.png`,
          ...VISUAL_TEST_CONFIG,
        });
        const renderTime = performance.now() - renderStart;

        expect(renderTime).toBeLessThan(500);

        await expect(page).toHaveScreenshot(`team-selection-${name}.png`, {
          threshold: VISUAL_TEST_CONFIG.threshold,
        });
      });

      test(`should handle team selection interactions on ${name}`, async ({ page }) => {
        await page.addInitScript(() => {
          localStorage.setItem('corner-league-onboarding', JSON.stringify({
            selectedSports: [
              { sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true },
            ],
          }));
        });

        await page.goto('/onboarding/step/3');

        await expect(page.getByText('Select Your Teams')).toBeVisible();

        // Find and click a team checkbox
        const firstCheckbox = page.locator('input[type="checkbox"]').first();
        await firstCheckbox.waitFor();

        const interactionStart = performance.now();
        await firstCheckbox.click();

        // Wait for visual feedback
        await page.waitForTimeout(100);

        await page.screenshot({
          path: `test-results/visual/team-selected-${name}.png`,
          ...VISUAL_TEST_CONFIG,
        });

        const interactionTime = performance.now() - interactionStart;

        // Interaction should be fast
        expect(interactionTime).toBeLessThan(200);

        await expect(page).toHaveScreenshot(`team-selected-${name}.png`, {
          threshold: VISUAL_TEST_CONFIG.threshold,
        });
      });
    });
  });

  test.describe('Accessibility Visual Tests', () => {
    test('should maintain visual accessibility standards', async ({ page }) => {
      await page.goto('/onboarding/step/1');

      // Inject axe for accessibility testing
      await injectAxe(page);

      // Check accessibility before taking screenshot
      await checkA11y(page, null, {
        detailedReport: true,
        detailedReportOptions: { html: true },
      });

      // Take high contrast screenshot for accessibility review
      await page.emulateMedia({ colorScheme: 'dark' });
      await page.screenshot({
        path: 'test-results/visual/onboarding-dark-mode.png',
        ...VISUAL_TEST_CONFIG,
      });

      await page.emulateMedia({ colorScheme: 'light' });
      await page.screenshot({
        path: 'test-results/visual/onboarding-light-mode.png',
        ...VISUAL_TEST_CONFIG,
      });
    });
  });

  test.describe('Performance Visual Tests', () => {
    test('should handle large team datasets visually', async ({ page }) => {
      // Mock large dataset
      await page.route('**/api/onboarding/teams**', async (route) => {
        const largeDataset = Array.from({ length: 100 }, (_, i) => ({
          id: `team-${i}`,
          name: `Team ${i + 1}`,
          league: `League ${(i % 4) + 1}`,
          logo: '🏈',
        }));

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: largeDataset }),
        });
      });

      await page.addInitScript(() => {
        localStorage.setItem('corner-league-onboarding', JSON.stringify({
          selectedSports: [
            { sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true },
          ],
        }));
      });

      const loadStart = performance.now();
      await page.goto('/onboarding/step/3');

      await expect(page.getByText('Select Your Teams')).toBeVisible();
      await page.waitForSelector('[data-testid="teams-container"]', { timeout: 10000 });

      const loadTime = performance.now() - loadStart;
      console.log(`Large dataset load time: ${loadTime}ms`);

      // Should handle large datasets efficiently
      expect(loadTime).toBeLessThan(2000);

      // Scroll performance test
      const scrollStart = performance.now();
      await page.mouse.wheel(0, 500);
      await page.waitForTimeout(100);
      const scrollTime = performance.now() - scrollStart;

      expect(scrollTime).toBeLessThan(100);

      await page.screenshot({
        path: 'test-results/visual/large-team-dataset.png',
        ...VISUAL_TEST_CONFIG,
      });
    });

    test('should handle form validation states', async ({ page }) => {
      await page.goto('/onboarding/step/2');

      // Try to continue without selecting sports
      await page.click('button:has-text("Continue")');

      // Wait for validation feedback
      await page.waitForTimeout(100);

      await page.screenshot({
        path: 'test-results/visual/validation-error-state.png',
        ...VISUAL_TEST_CONFIG,
      });

      // Select a sport and see success state
      const firstSportCard = page.locator('[data-testid="sport-card"]').first();
      await firstSportCard.click();

      await page.waitForTimeout(100);

      await page.screenshot({
        path: 'test-results/visual/validation-success-state.png',
        ...VISUAL_TEST_CONFIG,
      });
    });
  });

  test.describe('Animation Performance Tests', () => {
    test('should handle smooth transitions between steps', async ({ page }) => {
      // Enable animations for this test
      await page.addInitScript(() => {
        const style = document.querySelector('style');
        if (style) style.remove();
      });

      await page.goto('/onboarding/step/1');

      // Measure transition time
      const transitionStart = performance.now();

      await page.click('button:has-text("Get Started")');
      await expect(page.getByText('Select Your Sports')).toBeVisible();

      const transitionTime = performance.now() - transitionStart;

      // Navigation should be smooth and fast
      expect(transitionTime).toBeLessThan(1000);

      await page.screenshot({
        path: 'test-results/visual/step-transition.png',
        ...VISUAL_TEST_CONFIG,
      });
    });
  });
});