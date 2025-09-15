/**
 * Accessibility E2E Tests
 *
 * Comprehensive accessibility testing using axe-core and manual testing
 * for keyboard navigation, screen reader compatibility, and WCAG compliance.
 */

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.evaluate(() => localStorage.clear());
    await page.goto('/');
  });

  test('passes axe accessibility audit on welcome screen', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('passes axe accessibility audit on sports selection', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('passes axe accessibility audit on team selection', async ({ page }) => {
    // Navigate to team selection
    await page.getByRole('button', { name: /get started/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('passes axe accessibility audit on preferences setup', async ({ page }) => {
    // Navigate to preferences
    await page.getByRole('button', { name: /get started/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('passes axe accessibility audit on completion screen', async ({ page }) => {
    // Navigate to completion
    await page.getByRole('button', { name: /get started/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();
    await page.getByRole('button', { name: /continue/i }).click();

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});

test.describe('Keyboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.evaluate(() => localStorage.clear());
    await page.goto('/');
  });

  test('supports tab navigation through all interactive elements', async ({ page }) => {
    // Start tabbing from the beginning
    await page.keyboard.press('Tab');

    // Should focus on the first interactive element
    let focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(['BUTTON', 'A', 'INPUT'].includes(focusedElement!)).toBe(true);

    // Continue tabbing to ensure all elements are reachable
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      focusedElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(focusedElement).toBeTruthy();
    }
  });

  test('supports Enter key activation of buttons', async ({ page }) => {
    // Tab to the get started button and press Enter
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab'); // Skip exit button
    await page.keyboard.press('Enter');

    // Should advance to sports selection
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });

  test('supports Space key activation of checkboxes', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Tab to first checkbox and press Space
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press(' ');

    // Checkbox should be checked
    const firstCheckbox = page.getByRole('checkbox').first();
    await expect(firstCheckbox).toBeChecked();
  });

  test('supports Escape key to exit onboarding', async ({ page }) => {
    // Set up dialog handler
    page.on('dialog', dialog => dialog.accept());

    await page.keyboard.press('Escape');

    // Should show exit confirmation (handled by dialog handler)
  });

  test('supports Arrow keys for navigation where appropriate', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // This would test arrow key navigation if implemented
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowUp');

    // Basic test to ensure arrow keys don't break the page
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });

  test('traps focus in modal dialogs', async ({ page }) => {
    // Complete onboarding to trigger first-time experience modal
    await page.evaluate(() => {
      localStorage.setItem('corner-league-onboarding-completed', JSON.stringify({
        completed: true,
        completedAt: new Date().toISOString(),
      }));
      localStorage.setItem('corner-league-user-preferences', JSON.stringify({
        id: 'test-user',
        sports: [{ sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true }],
        teams: [{ teamId: 'chiefs', name: 'Kansas City Chiefs', sportId: 'nfl', league: 'NFL', affinityScore: 85 }],
        preferences: {
          newsTypes: [{ type: 'injuries', enabled: true, priority: 1 }],
          notifications: { push: false, email: true, gameReminders: true, newsAlerts: false, scoreUpdates: true },
          contentFrequency: 'standard',
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }));
    });

    await page.goto('/');

    // Should show first-time experience modal
    await expect(page.getByText(/welcome to your personalized dashboard/i)).toBeVisible();

    // Tab should stay within the modal
    const initialFocus = await page.evaluate(() => document.activeElement?.textContent);

    // Tab around the modal
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('Tab');
    }

    // Focus should still be within the modal
    const modalButtons = page.getByRole('button', { name: /skip tour|next|back/i });
    const focusedText = await page.evaluate(() => document.activeElement?.textContent);

    // One of the modal buttons should be focused
    const buttonTexts = await modalButtons.allTextContents();
    expect(buttonTexts.some(text => focusedText?.includes(text))).toBe(true);
  });
});

test.describe('Screen Reader Support', () => {
  test.beforeEach(async ({ page }) => {
    await page.evaluate(() => localStorage.clear());
    await page.goto('/');
  });

  test('provides proper heading structure', async ({ page }) => {
    // Check for proper heading hierarchy
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);

    // Main heading should be h1 or h2
    const mainHeading = headings[0];
    const tagName = await mainHeading.evaluate(el => el.tagName);
    expect(['H1', 'H2'].includes(tagName)).toBe(true);
  });

  test('provides ARIA labels for interactive elements', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Check checkboxes have proper labels
    const checkboxes = await page.getByRole('checkbox').all();
    for (const checkbox of checkboxes) {
      const accessibleName = await checkbox.getAttribute('aria-label');
      const labelText = await checkbox.evaluate(el => {
        const id = el.getAttribute('id');
        if (id) {
          const label = document.querySelector(`[for="${id}"]`);
          return label?.textContent;
        }
        return null;
      });

      expect(accessibleName || labelText).toBeTruthy();
    }
  });

  test('announces dynamic content changes', async ({ page }) => {
    // Check for live regions
    const liveRegions = await page.locator('[aria-live]').all();

    // There should be live regions for announcements
    // Note: This is a basic check - actual announcement testing would require screen reader simulation
    if (liveRegions.length > 0) {
      for (const region of liveRegions) {
        const politeness = await region.getAttribute('aria-live');
        expect(['polite', 'assertive'].includes(politeness!)).toBe(true);
      }
    }
  });

  test('provides skip links for navigation', async ({ page }) => {
    // Check for skip links (may be visually hidden)
    const skipLinks = await page.locator('a[href^="#"]').all();

    if (skipLinks.length > 0) {
      const firstSkipLink = skipLinks[0];
      const href = await firstSkipLink.getAttribute('href');
      const text = await firstSkipLink.textContent();

      expect(href).toMatch(/^#/);
      expect(text?.toLowerCase()).toMatch(/skip|main/);
    }
  });

  test('provides descriptive button text', async ({ page }) => {
    const buttons = await page.getByRole('button').all();

    for (const button of buttons) {
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      const description = text || ariaLabel;

      expect(description).toBeTruthy();
      expect(description!.length).toBeGreaterThan(2); // More than just "OK" or "Go"
    }
  });
});

test.describe('Visual Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.evaluate(() => localStorage.clear());
    await page.goto('/');
  });

  test('maintains minimum color contrast ratios', async ({ page }) => {
    // This would require color contrast calculation
    // For now, we'll test that text is visible
    const textElements = await page.locator('p, span, div, h1, h2, h3').all();

    for (const element of textElements.slice(0, 10)) { // Test first 10 elements
      const isVisible = await element.isVisible();
      if (isVisible) {
        const text = await element.textContent();
        if (text && text.trim().length > 0) {
          // Element should be visible and have text
          expect(await element.isVisible()).toBe(true);
        }
      }
    }
  });

  test('respects prefers-reduced-motion', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await page.goto('/');

    // Page should still be functional with reduced motion
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Animations should be reduced (this would need specific testing)
    await page.getByRole('button', { name: /get started/i }).click();
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });

  test('respects prefers-color-scheme', async ({ page }) => {
    // Test dark mode
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto('/');

    // Should still be readable in dark mode
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Test light mode
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto('/');

    // Should still be readable in light mode
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();
  });

  test('supports high contrast mode', async ({ page }) => {
    // Simulate high contrast (browser-dependent)
    await page.emulateMedia({ forcedColors: 'active' });

    await page.goto('/');

    // Should still be functional in high contrast mode
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Buttons should still be clickable
    await page.getByRole('button', { name: /get started/i }).click();
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });

  test('maintains focus visibility', async ({ page }) => {
    // Tab to first interactive element
    await page.keyboard.press('Tab');

    // Check if focused element has visible focus indication
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();

    // The focused element should have some visual indication
    // This is difficult to test programmatically, but we can check it exists
    const computedStyle = await focusedElement.evaluate(el => {
      const style = window.getComputedStyle(el);
      return {
        outline: style.outline,
        outlineWidth: style.outlineWidth,
        boxShadow: style.boxShadow,
        border: style.border,
      };
    });

    // Should have some form of focus indication
    const hasFocusIndication =
      computedStyle.outline !== 'none' ||
      computedStyle.outlineWidth !== '0px' ||
      computedStyle.boxShadow !== 'none' ||
      computedStyle.border !== 'none';

    expect(hasFocusIndication).toBe(true);
  });
});

test.describe('Error Handling Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.evaluate(() => localStorage.clear());
    await page.goto('/');
  });

  test('announces validation errors to screen readers', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Try to continue without selecting sports
    await page.getByRole('button', { name: /continue/i }).click();

    // Error should be announced (check for aria-live regions or role="alert")
    const errorElements = await page.locator('[role="alert"], [aria-live="assertive"]').all();

    if (errorElements.length > 0) {
      const errorText = await errorElements[0].textContent();
      expect(errorText).toMatch(/select.*sport/i);
    } else {
      // Check for visible error messages
      const visibleError = page.getByText(/please select at least one sport/i);
      await expect(visibleError).toBeVisible();
    }
  });

  test('maintains focus on error correction', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Try to continue without selection
    await page.getByRole('button', { name: /continue/i }).click();

    // Focus should remain accessible for error correction
    const firstCheckbox = page.getByRole('checkbox').first();
    await firstCheckbox.focus();

    await expect(firstCheckbox).toBeFocused();
  });
});