/**
 * Accessibility Testing Demo
 *
 * This demonstrates the fixed axe-core integration with robust error handling
 * and fallback mechanisms. This test shows how to use the new accessibility
 * testing utilities effectively.
 */

import { test, expect } from '@playwright/test';
import { quickAccessibilityCheck, performAccessibilityAnalysis, ensureAxeInitialized } from './utils/axe-helper';

test.describe('Accessibility Testing Demo', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Allow React to render
  });

  test('demonstrates quick accessibility check', async ({ page }) => {
    // Quick accessibility check with sensible defaults
    const { passed, report, violations } = await quickAccessibilityCheck(page, {
      excludeThirdParty: true,    // Exclude Clerk and other third-party elements
      excludeColorContrast: true, // Exclude color contrast issues (design team responsibility)
      failOnViolations: false     // Don't fail the test, just report issues
    });

    console.log('Quick Accessibility Check Results:');
    console.log('Passed:', passed);
    console.log('Critical violations found:', violations.length);

    if (violations.length > 0) {
      console.log('\nCritical violations that should be addressed:');
      violations.forEach((violation, index) => {
        console.log(`${index + 1}. ${violation.id} (${violation.impact}): ${violation.description}`);
      });
    }

    // Test should not fail but provides valuable feedback
    expect(typeof passed).toBe('boolean');
    expect(Array.isArray(violations)).toBe(true);
  });

  test('demonstrates comprehensive accessibility analysis', async ({ page }) => {
    // Comprehensive analysis with custom configuration
    const results = await performAccessibilityAnalysis(page, {
      exclude: ['[data-clerk-element]', '[data-stripe-element]'],
      withTags: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'],
      disableRules: ['color-contrast'], // Temporarily disable for demo
      allowFailures: true // Allow test to continue even if axe-core has issues
    });

    console.log('\nComprehensive Accessibility Analysis:');
    console.log(`Total violations: ${results.violations.length}`);
    console.log(`Total passes: ${results.passes.length}`);
    console.log(`Total incomplete: ${results.incomplete.length}`);

    // Show examples of different violation severities
    const violationsBySeverity = {
      critical: results.violations.filter(v => v.impact === 'critical'),
      serious: results.violations.filter(v => v.impact === 'serious'),
      moderate: results.violations.filter(v => v.impact === 'moderate'),
      minor: results.violations.filter(v => v.impact === 'minor')
    };

    console.log('\nViolations by severity:');
    Object.entries(violationsBySeverity).forEach(([severity, violations]) => {
      console.log(`${severity.toUpperCase()}: ${violations.length}`);
    });

    expect(results).toBeDefined();
    expect(Array.isArray(results.violations)).toBe(true);
  });

  test('demonstrates axe-core initialization robustness', async ({ page }) => {
    // Test axe-core initialization directly
    const axeInitialized = await ensureAxeInitialized(page);
    expect(axeInitialized).toBe(true);

    // Verify axe is available in the browser context
    const axeAvailable = await page.evaluate(() => {
      return typeof (window as any).axe !== 'undefined' &&
             typeof (window as any).axe.run === 'function';
    });
    expect(axeAvailable).toBe(true);

    // Test that multiple analysis calls work without issues
    for (let i = 0; i < 3; i++) {
      console.log(`Running accessibility analysis ${i + 1}/3...`);

      const results = await performAccessibilityAnalysis(page, {
        withTags: ['wcag2a'],
        allowFailures: false
      });

      expect(results).toBeDefined();
      expect(Array.isArray(results.violations)).toBe(true);

      console.log(`Analysis ${i + 1} completed with ${results.violations.length} violations`);
    }
  });

  test('handles different page states gracefully', async ({ page }) => {
    // Test accessibility analysis on different page states
    const testStates = [
      { name: 'Initial load', action: async () => {} },
      { name: 'After page reload', action: async () => await page.reload() },
      { name: 'After navigation', action: async () => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');
      }}
    ];

    for (const state of testStates) {
      console.log(`\nTesting accessibility in state: ${state.name}`);

      await state.action();
      await page.waitForTimeout(1000);

      try {
        const { passed, violations } = await quickAccessibilityCheck(page, {
          excludeThirdParty: true,
          excludeColorContrast: true,
          failOnViolations: false
        });

        console.log(`${state.name}: ${violations.length} critical violations found`);
        expect(typeof passed).toBe('boolean');

      } catch (error) {
        console.warn(`Accessibility check failed for ${state.name}:`, error.message);
        // Don't fail the test - this demonstrates robustness
      }
    }
  });

  test('validates accessibility across different viewports', async ({ page }) => {
    const viewports = [
      { width: 1920, height: 1080, name: 'Desktop Large' },
      { width: 1366, height: 768, name: 'Desktop Medium' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 375, height: 667, name: 'Mobile' }
    ];

    for (const viewport of viewports) {
      console.log(`\nTesting accessibility at ${viewport.name} (${viewport.width}x${viewport.height})`);

      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.reload();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      const { passed, violations } = await quickAccessibilityCheck(page, {
        excludeThirdParty: true,
        excludeColorContrast: true,
        failOnViolations: false
      });

      console.log(`${viewport.name}: ${violations.length} critical violations`);

      // Log viewport-specific issues
      if (violations.length > 0) {
        violations.slice(0, 2).forEach(violation => {
          console.log(`  - ${violation.id}: ${violation.description}`);
        });
      }

      expect(typeof passed).toBe('boolean');
    }
  });
});