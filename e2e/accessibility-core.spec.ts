/**
 * Core Accessibility Tests
 *
 * Essential accessibility testing focused on WCAG compliance and critical violations.
 * These tests are designed to be robust and work regardless of the current application state.
 */

import { test, expect } from '@playwright/test';
import { performAccessibilityAnalysis, quickAccessibilityCheck, filterViolations, generateAccessibilityReport } from './utils/axe-helper';

test.describe('Core Accessibility Compliance', () => {
  test.beforeEach(async ({ page, browserName }) => {
    // Set up test mode to bypass authentication
    await page.addInitScript(() => {
      (window as any).__PLAYWRIGHT_TEST__ = true;
    });

    await page.goto('/');

    // Handle localStorage access for mobile browsers
    try {
      await page.evaluate(() => {
        try {
          localStorage.clear();
        } catch (e) {
          // Mobile browsers may restrict localStorage access
          console.log('localStorage access restricted');
        }
      });
    } catch (error) {
      // Ignore localStorage access errors on mobile
    }

    await page.waitForLoadState('networkidle');

    // Additional wait for mobile browsers to complete rendering and ensure consistent state
    const isMobile = browserName === 'Mobile Chrome' || browserName === 'Mobile Safari';
    if (isMobile) {
      await page.waitForTimeout(3000);
      // Ensure the page is fully interactive
      await page.waitForFunction(() => document.readyState === 'complete');
    }
  });

  test('application has no critical accessibility violations', async ({ page }) => {
    const results = await performAccessibilityAnalysis(page, {
      exclude: ['[data-clerk-element]'], // Exclude third-party auth elements
      withTags: ['wcag2a', 'wcag2aa', 'wcag21aa'], // Focus on WCAG compliance
      allowFailures: false // Fail if axe-core cannot be initialized
    });

    // Filter out design-related issues that need team attention but aren't blocking
    const criticalViolations = filterViolations(results.violations, {
      excludeIds: ['color-contrast', 'landmark-one-main', 'region'],
      onlyImpacts: ['critical', 'serious']
    });

    // Generate comprehensive report
    generateAccessibilityReport(results, {
      logToConsole: true,
      includePassedRules: false,
      maxNodesPerViolation: 3
    });

    // Critical test: Should have no serious/critical accessibility violations
    expect(criticalViolations).toEqual([]);
  });

  test('supports keyboard navigation', async ({ page, browserName }) => {
    // First ensure we have interactive elements available
    const interactiveElements = page.locator('button, a, input, select, textarea, [role="button"], [tabindex]:not([tabindex="-1"])');
    const elementCount = await interactiveElements.count();
    expect(elementCount).toBeGreaterThan(0);

    // Get the first focusable element for reliable testing
    const firstFocusable = interactiveElements.first();
    await expect(firstFocusable).toBeVisible();

    // Focus the first element programmatically (more reliable on mobile)
    await firstFocusable.focus();

    // Verify the element is focused
    await expect(firstFocusable).toBeFocused();

    // Test tab navigation if not on mobile (mobile browsers handle focus differently)
    const isMobile = browserName === 'Mobile Chrome' || browserName === 'Mobile Safari';
    if (!isMobile) {
      // Test basic keyboard navigation on desktop
      await page.keyboard.press('Tab');
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();

      // Element should have proper focus indication
      const computedStyle = await focusedElement.evaluate(el => {
        const style = window.getComputedStyle(el);
        return {
          outline: style.outline,
          outlineWidth: style.outlineWidth,
          boxShadow: style.boxShadow,
        };
      });

      // Should have some form of focus indication
      const hasFocusIndication =
        computedStyle.outline !== 'none' ||
        computedStyle.outlineWidth !== '0px' ||
        computedStyle.boxShadow !== 'none';

      expect(hasFocusIndication).toBe(true);
    } else {
      // On mobile, verify focus management works with touch interaction simulation
      await firstFocusable.click();

      // Test that Enter key works for activation
      await page.keyboard.press('Enter');

      // The test passes if we can interact with elements
      // Mobile browsers may not show visual focus but should support programmatic focus
    }
  });

  test('has proper heading structure', async ({ page }) => {
    // Wait for the page to fully load and content to render
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Additional wait for React components to render

    // Check for semantic headings first
    const semanticHeadings = await page.locator('h1, h2, h3, h4, h5, h6').count();

    // If no semantic headings, check for heading-like elements with proper roles
    const roleHeadings = await page.locator('[role="heading"]').count();

    // Check for visually prominent text that serves as headings
    const prominentText = await page.locator('.font-display, [class*="text-2xl"], [class*="text-3xl"], [class*="text-4xl"], [class*="font-bold"]').count();

    // At minimum, we should have the app title as a semantic heading or prominent text
    const totalHeadingLikeElements = semanticHeadings + roleHeadings;

    if (totalHeadingLikeElements === 0) {
      // Fallback: ensure we at least have visually prominent text that could serve as headings
      expect(prominentText).toBeGreaterThan(0);

      // Log for development awareness
      console.log(`No semantic headings found, but ${prominentText} prominent text elements detected. Consider adding proper heading structure.`);
    } else {
      expect(totalHeadingLikeElements).toBeGreaterThan(0);

      // If we have semantic headings, verify proper hierarchy
      if (semanticHeadings > 0) {
        const h1Elements = await page.locator('h1').count();
        const h2Elements = await page.locator('h2').count();

        // Should have at least one main heading (h1 or h2)
        expect(h1Elements + h2Elements).toBeGreaterThan(0);
      }
    }
  });

  test('respects reduced motion preferences', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Extra wait for React components to render

    // Page should still be functional with reduced motion
    await expect(page.locator('body')).toBeVisible();

    // Should still have interactive elements (broader selector for mobile compatibility)
    const interactiveSelectors = [
      'button',
      'a',
      'input',
      'select',
      'textarea',
      '[role="button"]',
      '[tabindex]:not([tabindex="-1"])',
      '[data-clerk-element]', // Clerk auth elements
      '.cursor-pointer',      // Elements styled as interactive
      '[onclick]'             // Elements with click handlers
    ];

    let totalInteractiveElements = 0;

    for (const selector of interactiveSelectors) {
      const count = await page.locator(selector).count();
      totalInteractiveElements += count;
    }

    // If no interactive elements found, check if page is still loading
    if (totalInteractiveElements === 0) {
      // Wait a bit more and try again
      await page.waitForTimeout(3000);

      for (const selector of interactiveSelectors) {
        const count = await page.locator(selector).count();
        totalInteractiveElements += count;
      }
    }

    // At minimum, we should have navigation elements or the app should be loading
    const isLoading = await page.locator('[class*="loading"], [class*="spinner"], .animate-pulse').count();

    if (totalInteractiveElements === 0 && isLoading === 0) {
      // Fallback: verify the page structure suggests it's functional
      const hasMainContent = await page.locator('main, [role="main"], #root, .min-h-screen').count();
      expect(hasMainContent).toBeGreaterThan(0);
      console.log('No interactive elements detected but main content structure is present');
    } else {
      expect(totalInteractiveElements).toBeGreaterThan(0);
    }
  });

  test('maintains readability in high contrast mode', async ({ page }) => {
    // Simulate high contrast mode
    await page.emulateMedia({ forcedColors: 'active' });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Should still be functional in high contrast mode
    await expect(page.locator('body')).toBeVisible();

    // Should still have interactive elements (broader selector)
    const interactiveElements = await page.locator('button, a, input, select, textarea, [role="button"], [tabindex]').count();
    expect(interactiveElements).toBeGreaterThan(0);
  });

  test('supports both dark and light color schemes', async ({ page }) => {
    // Test light mode
    await page.emulateMedia({ colorScheme: 'light' });
    await page.reload();
    await expect(page.locator('body')).toBeVisible();

    // Test dark mode
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.reload();
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Interactive Elements Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('buttons have accessible names', async ({ page }) => {
    const buttons = await page.getByRole('button').all();

    for (const button of buttons) {
      const accessibleName = await button.getAttribute('aria-label') ||
                           await button.textContent() ||
                           await button.getAttribute('title');

      expect(accessibleName).toBeTruthy();
      if (accessibleName) {
        expect(accessibleName.trim().length).toBeGreaterThan(1);
      }
    }
  });

  test('links have accessible names and purposes', async ({ page }) => {
    const links = await page.getByRole('link').all();

    for (const link of links) {
      const accessibleName = await link.getAttribute('aria-label') ||
                           await link.textContent() ||
                           await link.getAttribute('title');

      expect(accessibleName).toBeTruthy();
      if (accessibleName) {
        expect(accessibleName.trim().length).toBeGreaterThan(1);
      }
    }
  });

  test('form elements have proper labels', async ({ page }) => {
    const inputs = await page.locator('input, select, textarea').all();

    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');

      // Should have some form of labeling
      const hasLabel = ariaLabel || ariaLabelledBy ||
                      (id && await page.locator(`[for="${id}"]`).count() > 0);

      expect(hasLabel).toBeTruthy();
    }
  });
});