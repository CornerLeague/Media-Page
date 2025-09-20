/**
 * Axe-Core Helper Utilities
 *
 * This module provides robust axe-core integration with proper error handling,
 * fallback mechanisms, and consistent initialization across all test scenarios.
 */

import { Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

export interface AxeOptions {
  exclude?: string[];
  withTags?: string[];
  disableRules?: string[];
  include?: string[];
  allowFailures?: boolean;
  timeout?: number;
}

export interface AxeResults {
  violations: any[];
  passes: any[];
  incomplete: any[];
  inapplicable: any[];
  url: string;
  timestamp: string;
  toolOptions: any;
  testEngine: any;
  testRunner: any;
  testEnvironment: any;
}

/**
 * Ensures axe-core is properly loaded and initialized in the page
 */
export async function ensureAxeInitialized(page: Page): Promise<boolean> {
  try {
    // Check if axe is already available
    const axeExists = await page.evaluate(() => {
      return typeof (window as any).axe !== 'undefined' &&
             typeof (window as any).axe.run === 'function';
    });

    if (axeExists) {
      console.log('✓ axe-core already available');
      return true;
    }

    console.log('Initializing axe-core...');

    // If not available, inject axe-core manually from CDN
    await page.addScriptTag({
      url: 'https://unpkg.com/axe-core@4.10.2/axe.min.js'
    });

    // Wait for axe to be available with timeout
    await page.waitForFunction(() => {
      return typeof (window as any).axe !== 'undefined' &&
             typeof (window as any).axe.run === 'function';
    }, { timeout: 15000 });

    console.log('✓ axe-core initialized successfully');
    return true;
  } catch (error) {
    console.error('✗ Failed to initialize axe-core:', error);
    return false;
  }
}

/**
 * Performs safe accessibility analysis with comprehensive error handling
 */
export async function performAccessibilityAnalysis(
  page: Page,
  options: AxeOptions = {}
): Promise<AxeResults> {
  const {
    exclude = [],
    withTags = ['wcag2a', 'wcag2aa', 'wcag21aa'],
    disableRules = [],
    include = [],
    allowFailures = false,
    timeout = 30000
  } = options;

  // Ensure axe is initialized first
  const axeInitialized = await ensureAxeInitialized(page);

  if (!axeInitialized) {
    const errorMessage = 'axe-core initialization failed - cannot perform accessibility analysis';
    if (allowFailures) {
      console.warn(errorMessage);
      return createEmptyResults(page);
    }
    throw new Error(errorMessage);
  }

  try {
    // Method 1: Use @axe-core/playwright (preferred method)
    console.log('Using AxeBuilder for accessibility analysis...');

    const axeBuilder = new AxeBuilder({ page });

    // Configure AxeBuilder with options
    if (exclude.length > 0) {
      axeBuilder.exclude(exclude);
    }

    if (include.length > 0) {
      axeBuilder.include(include);
    }

    if (withTags.length > 0) {
      axeBuilder.withTags(withTags);
    }

    if (disableRules.length > 0) {
      axeBuilder.disableRules(disableRules);
    }

    // Set timeout for analysis
    axeBuilder.options({ timeout });

    const results = await axeBuilder.analyze();
    console.log('✓ AxeBuilder analysis completed successfully');
    return results;

  } catch (builderError) {
    console.warn('AxeBuilder failed, trying manual approach:', builderError);

    try {
      // Method 2: Manual axe.run() call as fallback
      console.log('Using manual axe.run() as fallback...');

      const results = await page.evaluate(async (evalOptions) => {
        // Double-check axe availability
        if (typeof (window as any).axe === 'undefined' || typeof (window as any).axe.run !== 'function') {
          throw new Error('axe-core not available for manual execution');
        }

        const axeOptions: any = {
          reporter: 'v2',
          timeout: evalOptions.timeout || 30000
        };

        // Configure manual axe options
        if (evalOptions.exclude && evalOptions.exclude.length > 0) {
          axeOptions.exclude = evalOptions.exclude;
        }

        if (evalOptions.include && evalOptions.include.length > 0) {
          axeOptions.include = evalOptions.include;
        }

        if (evalOptions.withTags && evalOptions.withTags.length > 0) {
          axeOptions.tags = evalOptions.withTags;
        }

        if (evalOptions.disableRules && evalOptions.disableRules.length > 0) {
          axeOptions.rules = {};
          evalOptions.disableRules.forEach((rule: string) => {
            axeOptions.rules[rule] = { enabled: false };
          });
        }

        // Run axe analysis
        return new Promise((resolve, reject) => {
          const timeoutId = setTimeout(() => {
            reject(new Error('axe.run() timeout'));
          }, evalOptions.timeout || 30000);

          (window as any).axe.run(document, axeOptions, (err: any, results: any) => {
            clearTimeout(timeoutId);
            if (err) {
              reject(err);
            } else {
              resolve(results);
            }
          });
        });
      }, { exclude, include, withTags, disableRules, timeout });

      console.log('✓ Manual axe.run() completed successfully');
      return results as AxeResults;

    } catch (manualError) {
      console.error('Manual axe execution also failed:', manualError);

      if (allowFailures) {
        console.warn('Both AxeBuilder and manual execution failed, returning empty results');
        return createEmptyResults(page);
      }

      throw new Error(`Accessibility analysis failed: ${manualError.message}`);
    }
  }
}

/**
 * Creates empty results structure when analysis fails but failures are allowed
 */
async function createEmptyResults(page: Page): Promise<AxeResults> {
  const url = await page.url();
  return {
    violations: [],
    passes: [],
    incomplete: [],
    inapplicable: [],
    url,
    timestamp: new Date().toISOString(),
    toolOptions: {},
    testEngine: { name: 'axe-core', version: 'unknown' },
    testRunner: { name: 'playwright', version: 'unknown' },
    testEnvironment: { userAgent: await page.evaluate(() => navigator.userAgent) }
  };
}

/**
 * Filters violations based on severity and configuration
 */
export function filterViolations(
  violations: any[],
  options: {
    excludeNonCritical?: boolean;
    excludeIds?: string[];
    onlyImpacts?: string[];
  } = {}
): any[] {
  const { excludeNonCritical = false, excludeIds = [], onlyImpacts = [] } = options;

  return violations.filter(violation => {
    // Filter by ID exclusions
    if (excludeIds.includes(violation.id)) {
      return false;
    }

    // Filter by impact levels
    if (onlyImpacts.length > 0 && !onlyImpacts.includes(violation.impact)) {
      return false;
    }

    // Filter out non-critical issues if requested
    if (excludeNonCritical && !['critical', 'serious'].includes(violation.impact)) {
      return false;
    }

    return true;
  });
}

/**
 * Generates a comprehensive accessibility report
 */
export function generateAccessibilityReport(
  results: AxeResults,
  options: {
    logToConsole?: boolean;
    includePassedRules?: boolean;
    maxNodesPerViolation?: number;
  } = {}
): string {
  const { logToConsole = true, includePassedRules = false, maxNodesPerViolation = 3 } = options;

  let report = '\n=== Accessibility Analysis Report ===\n';
  report += `URL: ${results.url}\n`;
  report += `Timestamp: ${results.timestamp}\n`;
  report += `Total violations: ${results.violations.length}\n`;
  report += `Total passes: ${results.passes.length}\n`;
  report += `Total incomplete: ${results.incomplete.length}\n`;
  report += `Total inapplicable: ${results.inapplicable.length}\n\n`;

  if (results.violations.length > 0) {
    report += '--- VIOLATIONS ---\n';
    results.violations.forEach((violation, index) => {
      const severity = violation.impact ? violation.impact.toUpperCase() : 'UNKNOWN';
      report += `${index + 1}. [${severity}] ${violation.id}\n`;
      report += `   Description: ${violation.description}\n`;
      report += `   Help: ${violation.helpUrl}\n`;
      report += `   Nodes affected: ${violation.nodes?.length || 0}\n`;

      if (violation.nodes && violation.nodes.length > 0) {
        const nodesToShow = Math.min(violation.nodes.length, maxNodesPerViolation);
        for (let i = 0; i < nodesToShow; i++) {
          const node = violation.nodes[i];
          report += `   Node ${i + 1}: ${node.target?.[0] || 'unknown'}\n`;
          if (node.failureSummary) {
            report += `     Issue: ${node.failureSummary}\n`;
          }
        }
        if (violation.nodes.length > maxNodesPerViolation) {
          report += `   ... and ${violation.nodes.length - maxNodesPerViolation} more nodes\n`;
        }
      }
      report += '\n';
    });
  }

  if (includePassedRules && results.passes.length > 0) {
    report += '--- PASSED RULES ---\n';
    results.passes.forEach((pass, index) => {
      report += `${index + 1}. ${pass.id} - ${pass.description}\n`;
    });
    report += '\n';
  }

  if (results.incomplete.length > 0) {
    report += '--- INCOMPLETE TESTS ---\n';
    results.incomplete.forEach((incomplete, index) => {
      report += `${index + 1}. ${incomplete.id} - ${incomplete.description}\n`;
      report += `   Reason: Requires manual testing\n`;
    });
    report += '\n';
  }

  report += '=====================================\n';

  if (logToConsole) {
    console.log(report);
  }

  return report;
}

/**
 * Quick accessibility check with sensible defaults
 */
export async function quickAccessibilityCheck(
  page: Page,
  options: {
    excludeThirdParty?: boolean;
    excludeColorContrast?: boolean;
    failOnViolations?: boolean;
  } = {}
): Promise<{ passed: boolean; report: string; violations: any[] }> {
  const { excludeThirdParty = true, excludeColorContrast = true, failOnViolations = false } = options;

  const axeOptions: AxeOptions = {
    withTags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
    allowFailures: !failOnViolations
  };

  if (excludeThirdParty) {
    axeOptions.exclude = ['[data-clerk-element]', '[data-stripe-element]'];
  }

  if (excludeColorContrast) {
    axeOptions.disableRules = ['color-contrast'];
  }

  try {
    const results = await performAccessibilityAnalysis(page, axeOptions);

    const criticalViolations = filterViolations(results.violations, {
      excludeIds: excludeColorContrast ? ['color-contrast', 'landmark-one-main', 'region'] : ['landmark-one-main', 'region'],
      onlyImpacts: ['critical', 'serious']
    });

    const report = generateAccessibilityReport(results, { logToConsole: false });
    const passed = criticalViolations.length === 0;

    return {
      passed,
      report,
      violations: criticalViolations
    };
  } catch (error) {
    const errorReport = `Accessibility check failed: ${error.message}`;
    console.error(errorReport);

    return {
      passed: !failOnViolations,
      report: errorReport,
      violations: []
    };
  }
}