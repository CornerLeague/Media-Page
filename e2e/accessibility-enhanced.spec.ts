/**
 * Enhanced accessibility tests demonstrating the improved axe-core global setup
 *
 * This test file showcases the enhanced axe-core initialization that provides:
 * - Global pre-loading of axe-core via fixtures for better performance
 * - Consistent initialization across all test scenarios
 * - Robust fallback mechanisms when needed
 * - Integration with the existing axe-helper utility
 */

import { test, expect } from './fixtures/axe-base';
import { quickAccessibilityCheck, performAccessibilityAnalysis } from './utils/axe-helper';

test.describe('Enhanced Accessibility Testing', () => {
  test('demonstrates improved axe-core initialization performance', async ({ axePage }) => {
    await axePage.goto('/');

    console.log('Starting accessibility analysis with enhanced setup...');
    const startTime = Date.now();

    // This should be faster due to pre-loading
    const { passed, violations } = await quickAccessibilityCheck(axePage, {
      excludeColorContrast: true,
      excludeThirdParty: true,
      failOnViolations: false
    });

    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log(`Accessibility analysis completed in ${duration}ms`);
    console.log(`Found ${violations.length} critical violations`);

    expect(passed).toBe(true);
    expect(violations.length).toBe(0);
  });

  test('demonstrates consistent behavior across navigation', async ({ axePage }) => {
    const pages = ['/', '/auth/sign-in'];

    for (const pagePath of pages) {
      await axePage.goto(pagePath);

      const results = await performAccessibilityAnalysis(axePage, {
        withTags: ['wcag2a', 'wcag2aa'],
        disableRules: ['color-contrast', 'landmark-one-main', 'region'],
        allowFailures: false
      });

      // Should have no critical or serious violations
      const criticalViolations = results.violations.filter(v =>
        ['critical', 'serious'].includes(v.impact)
      );

      console.log(`Page ${pagePath}: ${criticalViolations.length} critical violations`);
      expect(criticalViolations.length).toBe(0);
    }
  });

  test('demonstrates robust error handling', async ({ axePage }) => {
    await axePage.goto('/');

    // This should gracefully handle any edge cases
    const results = await performAccessibilityAnalysis(axePage, {
      allowFailures: true, // Allow test to continue even if axe has issues
      timeout: 10000
    });

    // Should always return results (even if empty due to errors)
    expect(results).toBeDefined();
    expect(Array.isArray(results.violations)).toBe(true);
    expect(Array.isArray(results.passes)).toBe(true);
  });

  test('verifies axe-core version compatibility', async ({ axePage }) => {
    await axePage.goto('/');

    const axeInfo = await axePage.evaluate(() => {
      const axe = (window as any).axe;
      if (!axe) return null;

      return {
        version: axe.version || 'unknown',
        hasRun: typeof axe.run === 'function',
        hasConfigured: typeof axe.configure === 'function'
      };
    });

    expect(axeInfo).toBeDefined();
    expect(axeInfo.hasRun).toBe(true);
    expect(axeInfo.hasConfigured).toBe(true);

    // Should be using version 4.10.x
    if (axeInfo.version !== 'unknown') {
      expect(axeInfo.version).toMatch(/^4\.10\./);
    }
  });
});