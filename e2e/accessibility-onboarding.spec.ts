/**
 * Accessibility-focused E2E tests for onboarding flow
 * Tests WCAG 2.1 AA compliance, keyboard navigation, screen reader support
 */

import { test, expect, Page } from '@playwright/test';
import { injectAxe, checkA11y, getViolations, AxeResults } from 'axe-playwright';

class AccessibilityTestHelper {
  constructor(private page: Page) {}

  async runAccessibilityAudit(selector?: string) {
    const results = await getViolations(this.page, selector, {
      rules: {
        // Enable all WCAG 2.1 AA rules
        'color-contrast': { enabled: true },
        'keyboard-navigation': { enabled: true },
        'focus-visible': { enabled: true },
        'aria-labels': { enabled: true },
        'heading-order': { enabled: true },
        'landmark-roles': { enabled: true },
        'list-structure': { enabled: true },
        'tab-index': { enabled: true },
        'form-labels': { enabled: true },
        'button-names': { enabled: true },
        'link-names': { enabled: true },
        'image-alt': { enabled: true },
        'input-labels': { enabled: true },
        'skip-links': { enabled: true },
      },
      tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
    });

    return results;
  }

  async checkColorContrast() {
    const violations = await this.runAccessibilityAudit();
    const contrastViolations = violations.filter(v => v.id === 'color-contrast');
    return contrastViolations;
  }

  async checkKeyboardNavigation() {
    // Test tab order
    const focusableElements = await this.page.locator(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ).all();

    const tabOrder = [];
    for (const element of focusableElements) {
      if (await element.isVisible()) {
        await element.focus();
        const tagName = await element.evaluate(el => el.tagName);
        const textContent = (await element.textContent())?.trim() || '';
        tabOrder.push({ tagName, textContent });
      }
    }

    return tabOrder;
  }

  async checkAriaLabels() {
    const violations = await this.runAccessibilityAudit();
    const ariaViolations = violations.filter(v =>
      v.id.includes('aria') || v.id.includes('label')
    );
    return ariaViolations;
  }

  async checkHeadingStructure() {
    const headings = await this.page.locator('h1, h2, h3, h4, h5, h6').all();
    const headingStructure = [];

    for (const heading of headings) {
      if (await heading.isVisible()) {
        const level = await heading.evaluate(el => el.tagName.toLowerCase());
        const text = (await heading.textContent())?.trim() || '';
        headingStructure.push({ level, text });
      }
    }

    return headingStructure;
  }

  async checkFormAccessibility() {
    const violations = await this.runAccessibilityAudit();
    const formViolations = violations.filter(v =>
      v.id.includes('label') || v.id.includes('input') || v.id.includes('form')
    );
    return formViolations;
  }

  async simulateScreenReader() {
    // Check for aria-live regions
    const liveRegions = await this.page.locator('[aria-live]').all();
    const announcements = [];

    for (const region of liveRegions) {
      if (await region.isVisible()) {
        const content = await region.textContent();
        announcements.push(content?.trim());
      }
    }

    return announcements;
  }

  async checkFocusManagement() {
    const focusedElement = await this.page.locator(':focus');
    const hasFocus = await focusedElement.count() > 0;

    if (hasFocus) {
      const tagName = await focusedElement.evaluate(el => el.tagName);
      const ariaLabel = await focusedElement.getAttribute('aria-label');
      const textContent = await focusedElement.textContent();

      return {
        hasFocus: true,
        element: {
          tagName,
          ariaLabel,
          textContent: textContent?.trim(),
        },
      };
    }

    return { hasFocus: false };
  }
}

test.describe('Onboarding Accessibility Tests', () => {
  let a11yHelper: AccessibilityTestHelper;

  test.beforeEach(async ({ page }) => {
    a11yHelper = new AccessibilityTestHelper(page);
    await injectAxe(page);

    // Mock API responses
    await page.route('**/api/v1/onboarding/sports', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            sports: [
              { id: '1', name: 'Football', icon: '🏈', description: 'American Football' },
              { id: '2', name: 'Basketball', icon: '🏀', description: 'Basketball' },
              { id: '3', name: 'Baseball', icon: '⚾', description: 'Baseball' },
            ],
            total: 3,
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
            teams: [
              { id: 'team-1', name: 'Patriots', market: 'New England', league: 'NFL' },
              { id: 'team-2', name: 'Lakers', market: 'Los Angeles', league: 'NBA' },
            ],
            total: 2,
          },
        }),
      });
    });
  });

  test.describe('WCAG 2.1 AA Compliance', () => {
    test('welcome step meets WCAG 2.1 AA standards', async ({ page }) => {
      await page.goto('/onboarding/step/1');
      await page.waitForLoadState('networkidle');

      const violations = await a11yHelper.runAccessibilityAudit();

      // Should have no critical or serious violations
      const criticalViolations = violations.filter(v =>
        v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalViolations).toHaveLength(0);

      // Check specific accessibility features
      await expect(page.locator('[role="progressbar"]')).toBeVisible();
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('main')).toBeVisible();
    });

    test('sports selection step meets WCAG 2.1 AA standards', async ({ page }) => {
      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="sport-card"]');

      const violations = await a11yHelper.runAccessibilityAudit();
      const criticalViolations = violations.filter(v =>
        v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalViolations).toHaveLength(0);

      // Check sport cards have proper accessibility
      const sportCards = page.locator('[data-testid="sport-card"]');
      const firstCard = sportCards.first();

      await expect(firstCard).toHaveAttribute('role', 'button');
      await expect(firstCard).toHaveAttribute('tabindex', '0');
      await expect(firstCard).toHaveAttribute('aria-selected');
    });

    test('team selection step meets WCAG 2.1 AA standards', async ({ page }) => {
      await page.goto('/onboarding/step/3');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="team-card"]');

      const violations = await a11yHelper.runAccessibilityAudit();
      const criticalViolations = violations.filter(v =>
        v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalViolations).toHaveLength(0);

      // Check search and filter controls
      const searchInput = page.locator('[data-testid="team-search"]');
      await expect(searchInput).toHaveAttribute('aria-label');

      const filterSelect = page.locator('[data-testid="league-filter"]');
      await expect(filterSelect).toHaveAttribute('aria-label');
    });

    test('preferences step meets WCAG 2.1 AA standards', async ({ page }) => {
      await page.goto('/onboarding/step/4');
      await page.waitForLoadState('networkidle');

      const violations = await a11yHelper.runAccessibilityAudit();
      const criticalViolations = violations.filter(v =>
        v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalViolations).toHaveLength(0);

      // Check form accessibility
      const formViolations = await a11yHelper.checkFormAccessibility();
      expect(formViolations).toHaveLength(0);

      // Check fieldsets and legends
      await expect(page.locator('fieldset')).toHaveCount(3); // News types, notifications, frequency
      await expect(page.locator('legend')).toHaveCount(3);
    });

    test('completion step meets WCAG 2.1 AA standards', async ({ page }) => {
      await page.goto('/onboarding/step/5');
      await page.waitForLoadState('networkidle');

      const violations = await a11yHelper.runAccessibilityAudit();
      const criticalViolations = violations.filter(v =>
        v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalViolations).toHaveLength(0);

      // Check summary accessibility
      await expect(page.locator('[role="region"][aria-labelledby]')).toHaveCount(3); // Sports, teams, preferences summaries
    });
  });

  test.describe('Color Contrast', () => {
    test('all text has sufficient color contrast', async ({ page }) => {
      const testSteps = [1, 2, 3, 4, 5];

      for (const step of testSteps) {
        await page.goto(`/onboarding/step/${step}`);
        await page.waitForLoadState('networkidle');

        const contrastViolations = await a11yHelper.checkColorContrast();

        expect(contrastViolations).toHaveLength(0);
      }
    });

    test('interactive elements have sufficient contrast in all states', async ({ page }) => {
      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="sport-card"]');

      const sportCard = page.locator('[data-testid="sport-card"]').first();

      // Test normal state
      let violations = await a11yHelper.checkColorContrast();
      expect(violations).toHaveLength(0);

      // Test hover state
      await sportCard.hover();
      violations = await a11yHelper.checkColorContrast();
      expect(violations).toHaveLength(0);

      // Test focused state
      await sportCard.focus();
      violations = await a11yHelper.checkColorContrast();
      expect(violations).toHaveLength(0);

      // Test selected state
      await sportCard.click();
      violations = await a11yHelper.checkColorContrast();
      expect(violations).toHaveLength(0);
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('supports tab navigation through all interactive elements', async ({ page }) => {
      await page.goto('/onboarding/step/1');
      await page.waitForLoadState('networkidle');

      // Start from the beginning
      await page.keyboard.press('Tab');

      const focusState = await a11yHelper.checkFocusManagement();
      expect(focusState.hasFocus).toBe(true);

      // Continue button should be focusable
      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Get Started")');
      await continueButton.focus();

      const buttonFocus = await a11yHelper.checkFocusManagement();
      expect(buttonFocus.hasFocus).toBe(true);
      expect(buttonFocus.element?.tagName).toBe('BUTTON');
    });

    test('supports arrow key navigation for sport cards', async ({ page }) => {
      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="sport-card"]');

      // Focus first sport card
      const firstCard = page.locator('[data-testid="sport-card"]').first();
      await firstCard.focus();

      let focusState = await a11yHelper.checkFocusManagement();
      expect(focusState.hasFocus).toBe(true);

      // Use arrow keys to navigate
      await page.keyboard.press('ArrowRight');

      focusState = await a11yHelper.checkFocusManagement();
      expect(focusState.hasFocus).toBe(true);

      // Use Enter/Space to select
      await page.keyboard.press('Enter');

      const selectedCard = page.locator('[data-testid="sport-card"][aria-selected="true"]');
      await expect(selectedCard).toHaveCount(1);
    });

    test('supports keyboard interaction for team selection', async ({ page }) => {
      await page.goto('/onboarding/step/3');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="team-card"]');

      // Test search input keyboard accessibility
      const searchInput = page.locator('[data-testid="team-search"]');
      await searchInput.focus();
      await searchInput.type('Lakers');

      // Verify filtering works with keyboard
      await expect(page.locator('[data-testid="team-card"]:has-text("Lakers")')).toBeVisible();

      // Clear search with keyboard
      await searchInput.press('Control+a');
      await searchInput.press('Delete');

      await expect(page.locator('[data-testid="team-card"]')).toHaveCount(2);
    });

    test('supports keyboard navigation for preferences form', async ({ page }) => {
      await page.goto('/onboarding/step/4');
      await page.waitForLoadState('networkidle');

      // Navigate to first checkbox
      const firstCheckbox = page.locator('input[type="checkbox"]').first();
      await firstCheckbox.focus();

      let focusState = await a11yHelper.checkFocusManagement();
      expect(focusState.hasFocus).toBe(true);

      // Toggle with Space
      await page.keyboard.press(' ');
      await expect(firstCheckbox).toBeChecked();

      // Navigate to radio buttons
      const firstRadio = page.locator('input[type="radio"]').first();
      await firstRadio.focus();

      focusState = await a11yHelper.checkFocusManagement();
      expect(focusState.hasFocus).toBe(true);

      // Select with Enter
      await page.keyboard.press('Enter');
      await expect(firstRadio).toBeChecked();
    });

    test('trap focus within modal dialogs', async ({ page }) => {
      // This test would be relevant if there are modal dialogs in the onboarding
      // For example, help dialogs or confirmation modals
      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');

      // If there's a help button that opens a modal
      const helpButton = page.locator('[data-testid="help-button"]');
      if (await helpButton.count() > 0) {
        await helpButton.click();

        // Test focus trap
        const modal = page.locator('[role="dialog"]');
        await expect(modal).toBeVisible();

        // Focus should be trapped within modal
        await page.keyboard.press('Tab');
        const focusState = await a11yHelper.checkFocusManagement();

        // Focus should be within the modal
        const modalElement = await modal.elementHandle();
        const focusedElement = await page.evaluateHandle(() => document.activeElement);

        const isWithinModal = await page.evaluate(
          ([modal, focused]) => modal.contains(focused),
          [modalElement, focusedElement]
        );

        expect(isWithinModal).toBe(true);
      }
    });
  });

  test.describe('Screen Reader Support', () => {
    test('provides proper heading structure', async ({ page }) => {
      await page.goto('/onboarding/step/1');
      await page.waitForLoadState('networkidle');

      const headingStructure = await a11yHelper.checkHeadingStructure();

      // Should have a proper heading hierarchy
      expect(headingStructure.length).toBeGreaterThan(0);

      // First heading should be h1
      expect(headingStructure[0].level).toBe('h1');

      // No heading level should be skipped
      for (let i = 1; i < headingStructure.length; i++) {
        const currentLevel = parseInt(headingStructure[i].level.charAt(1));
        const previousLevel = parseInt(headingStructure[i - 1].level.charAt(1));
        expect(currentLevel - previousLevel).toBeLessThanOrEqual(1);
      }
    });

    test('provides live region announcements for dynamic content', async ({ page }) => {
      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="sport-card"]');

      // Select a sport and check for announcements
      const sportCard = page.locator('[data-testid="sport-card"]').first();
      await sportCard.click();

      const announcements = await a11yHelper.simulateScreenReader();

      // Should announce selection state changes
      expect(announcements.some(announcement =>
        announcement?.includes('selected') || announcement?.includes('added')
      )).toBe(true);
    });

    test('provides descriptive labels for all interactive elements', async ({ page }) => {
      await page.goto('/onboarding/step/3');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="team-card"]');

      const violations = await a11yHelper.checkAriaLabels();
      expect(violations).toHaveLength(0);

      // Check specific elements have labels
      const searchInput = page.locator('[data-testid="team-search"]');
      const searchLabel = await searchInput.getAttribute('aria-label');
      expect(searchLabel).toBeTruthy();

      const filterSelect = page.locator('[data-testid="league-filter"]');
      const filterLabel = await filterSelect.getAttribute('aria-label');
      expect(filterLabel).toBeTruthy();
    });

    test('provides progress information to screen readers', async ({ page }) => {
      await page.goto('/onboarding/step/3');
      await page.waitForLoadState('networkidle');

      const progressBar = page.locator('[role="progressbar"]');

      await expect(progressBar).toHaveAttribute('aria-valuenow');
      await expect(progressBar).toHaveAttribute('aria-valuemin', '0');
      await expect(progressBar).toHaveAttribute('aria-valuemax', '100');

      const progressLabel = await progressBar.getAttribute('aria-label');
      expect(progressLabel).toBeTruthy();
    });

    test('announces errors and status changes', async ({ page }) => {
      // Mock API error
      await page.route('**/api/v1/onboarding/step', async route => {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'VALIDATION_ERROR',
            message: 'Please select at least one sport',
            timestamp: new Date().toISOString(),
          }),
        });
      });

      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');

      // Try to continue without selecting anything
      const continueButton = page.locator('button:has-text("Continue")');
      await continueButton.click();

      // Error should be announced to screen readers
      const errorRegion = page.locator('[role="alert"]');
      await expect(errorRegion).toBeVisible();

      const errorText = await errorRegion.textContent();
      expect(errorText).toContain('select');
    });
  });

  test.describe('Focus Management', () => {
    test('maintains focus during step transitions', async ({ page }) => {
      await page.goto('/onboarding/step/1');
      await page.waitForLoadState('networkidle');

      const continueButton = page.locator('button:has-text("Continue"), button:has-text("Get Started")');
      await continueButton.focus();
      await continueButton.click();

      // After navigation, focus should be managed appropriately
      await page.waitForLoadState('networkidle');

      const focusState = await a11yHelper.checkFocusManagement();
      expect(focusState.hasFocus).toBe(true);

      // Focus should be on a logical element (like main heading or first interactive element)
      const focusedElement = page.locator(':focus');
      const tagName = await focusedElement.evaluate(el => el.tagName);

      expect(['H1', 'BUTTON', 'INPUT'].includes(tagName)).toBe(true);
    });

    test('restores focus when navigating back', async ({ page }) => {
      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');

      const backButton = page.locator('button:has-text("Back")');
      await backButton.focus();
      await backButton.click();

      await page.waitForLoadState('networkidle');

      // Focus should be restored appropriately
      const focusState = await a11yHelper.checkFocusManagement();
      expect(focusState.hasFocus).toBe(true);
    });

    test('manages focus for dynamically added content', async ({ page }) => {
      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('[data-testid="sport-card"]');

      // Select a sport
      const sportCard = page.locator('[data-testid="sport-card"]').first();
      await sportCard.click();

      // If ranking controls appear, they should be focusable
      const rankingControl = page.locator('[data-testid="sport-ranking"]');
      if (await rankingControl.count() > 0) {
        await rankingControl.focus();

        const focusState = await a11yHelper.checkFocusManagement();
        expect(focusState.hasFocus).toBe(true);
      }
    });

    test('provides skip links for navigation', async ({ page }) => {
      await page.goto('/onboarding/step/1');
      await page.waitForLoadState('networkidle');

      // Press Tab to reveal skip links
      await page.keyboard.press('Tab');

      const skipLink = page.locator('a:has-text("Skip to main content")');
      if (await skipLink.count() > 0) {
        await expect(skipLink).toBeVisible();

        await skipLink.click();

        // Should jump to main content
        const mainContent = page.locator('main');
        const focusedElement = page.locator(':focus');

        // Focus should be within main content area
        const isWithinMain = await page.evaluate(() => {
          const main = document.querySelector('main');
          const focused = document.activeElement;
          return main?.contains(focused);
        });

        expect(isWithinMain).toBe(true);
      }
    });
  });

  test.describe('High Contrast Mode', () => {
    test('works in high contrast mode', async ({ page }) => {
      // Simulate high contrast mode
      await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'dark' });
      await page.addStyleTag({
        content: `
          @media (prefers-contrast: high) {
            * {
              background-color: black !important;
              color: white !important;
              border-color: white !important;
            }
          }
        `
      });

      await page.goto('/onboarding/step/2');
      await page.waitForLoadState('networkidle');

      // Content should still be accessible
      const violations = await a11yHelper.runAccessibilityAudit();
      const contrastViolations = violations.filter(v => v.id === 'color-contrast');

      // Should not have contrast violations in high contrast mode
      expect(contrastViolations).toHaveLength(0);
    });
  });

  test.describe('Reduced Motion', () => {
    test('respects reduced motion preferences', async ({ page }) => {
      await page.emulateMedia({ reducedMotion: 'reduce' });

      await page.goto('/onboarding/step/1');
      await page.waitForLoadState('networkidle');

      // Animations should be disabled or reduced
      const animatedElements = page.locator('[class*="animate"], [style*="transition"]');

      for (const element of await animatedElements.all()) {
        const computedStyle = await element.evaluate(el => {
          const style = getComputedStyle(el);
          return {
            animationDuration: style.animationDuration,
            transitionDuration: style.transitionDuration,
          };
        });

        // Animations should be disabled or very short
        expect(
          computedStyle.animationDuration === '0s' ||
          computedStyle.transitionDuration === '0s' ||
          computedStyle.animationDuration === 'none'
        ).toBe(true);
      }
    });
  });
});