/**
 * Manual Bug Hunting Test for Onboarding Flow
 *
 * This test systematically goes through the onboarding flow to identify bugs,
 * UI issues, JavaScript errors, and accessibility problems.
 */

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Onboarding Bug Hunt', () => {
  let consoleErrors: string[] = [];
  let jsErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    // Clear error arrays
    consoleErrors = [];
    jsErrors = [];

    // Listen for console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Listen for JavaScript errors
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });

    // Set up test mode to bypass authentication
    await page.addInitScript(() => {
      (window as any).__PLAYWRIGHT_TEST__ = true;
    });

    // Navigate to page and clear localStorage
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('Step 1: Welcome Screen Analysis', async ({ page }) => {
    console.log('🔍 Analyzing Welcome Screen...');

    // Take screenshot
    await page.screenshot({ path: 'bug-hunt-welcome.png', fullPage: true });

    // Check if redirected to onboarding
    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);

    // Look for the welcome heading
    const welcomeHeading = page.getByRole('heading', { name: /welcome to corner league media/i });
    const isWelcomeVisible = await welcomeHeading.isVisible();
    console.log('Welcome heading visible:', isWelcomeVisible);

    if (!isWelcomeVisible) {
      // Check what's actually on the page
      const pageText = await page.textContent('body');
      console.log('Page content preview:', pageText?.substring(0, 500));

      // Check for any error messages
      const errorElements = await page.locator('[role="alert"], .error, .text-destructive').all();
      for (const error of errorElements) {
        const errorText = await error.textContent();
        console.log('Error found:', errorText);
      }
    }

    // Check for Get Started button
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    const isGetStartedVisible = await getStartedButton.isVisible();
    console.log('Get Started button visible:', isGetStartedVisible);

    // Check accessibility
    const accessibilityResults = await new AxeBuilder({ page }).analyze();
    const criticalViolations = accessibilityResults.violations.filter(v =>
      ['critical', 'serious'].includes(v.impact || '')
    );
    console.log('Critical accessibility violations:', criticalViolations.length);

    if (criticalViolations.length > 0) {
      console.log('Accessibility issues:', criticalViolations.map(v => ({ id: v.id, impact: v.impact })));
    }

    console.log('Console errors:', consoleErrors);
    console.log('JS errors:', jsErrors);
  });

  test('Step 2: Navigation to Sports Selection', async ({ page }) => {
    console.log('🔍 Testing navigation to Sports Selection...');

    // Ensure we're on welcome screen first
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Click Get Started
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    await getStartedButton.click();

    // Wait for navigation
    await page.waitForTimeout(1000);

    // Take screenshot
    await page.screenshot({ path: 'bug-hunt-sports-selection.png', fullPage: true });

    // Check if we're on sports selection
    const sportsHeading = page.getByText(/select and rank your favorite sports/i);
    const isSportsVisible = await sportsHeading.isVisible();
    console.log('Sports selection heading visible:', isSportsVisible);

    if (!isSportsVisible) {
      const pageText = await page.textContent('body');
      console.log('Current page content:', pageText?.substring(0, 500));
    }

    // Check for sports checkboxes
    const checkboxes = await page.getByRole('checkbox').all();
    console.log('Number of sport checkboxes found:', checkboxes.length);

    // Check each checkbox
    for (let i = 0; i < Math.min(checkboxes.length, 5); i++) {
      const checkbox = checkboxes[i];
      const isVisible = await checkbox.isVisible();
      const isEnabled = await checkbox.isEnabled();
      const label = await checkbox.getAttribute('aria-label') ||
                   await page.locator(`label[for="${await checkbox.getAttribute('id')}"]`).textContent();
      console.log(`Checkbox ${i}: visible=${isVisible}, enabled=${isEnabled}, label="${label}"`);
    }

    // Check Continue button state
    const continueButton = page.getByRole('button', { name: /continue/i });
    const isContinueVisible = await continueButton.isVisible();
    const isContinueEnabled = await continueButton.isEnabled();
    console.log('Continue button: visible=${isContinueVisible}, enabled=${isContinueEnabled}');

    console.log('Console errors:', consoleErrors);
    console.log('JS errors:', jsErrors);
  });

  test('Step 3: Sports Selection Interaction', async ({ page }) => {
    console.log('🔍 Testing Sports Selection interactions...');

    // Navigate to sports selection
    await page.getByRole('button', { name: /get started/i }).click();
    await page.waitForTimeout(1000);

    // Try to click Continue without selecting sports (validation test)
    const continueButton = page.getByRole('button', { name: /continue/i });
    await continueButton.click();

    // Check for validation messages
    await page.waitForTimeout(500);
    const validationMessages = await page.locator('.text-destructive, [role="alert"]').allTextContents();
    console.log('Validation messages:', validationMessages);

    // Select first sport
    const firstCheckbox = page.getByRole('checkbox').first();
    await firstCheckbox.click();
    await page.waitForTimeout(500);

    // Check if selection counter updates
    const selectionCounter = page.getByText(/\d+ sports? selected/i);
    const isCounterVisible = await selectionCounter.isVisible();
    console.log('Selection counter visible:', isCounterVisible);

    if (isCounterVisible) {
      const counterText = await selectionCounter.textContent();
      console.log('Counter text:', counterText);
    }

    // Select second sport
    const secondCheckbox = page.getByRole('checkbox').nth(1);
    await secondCheckbox.click();
    await page.waitForTimeout(500);

    // Check updated counter
    const updatedCounter = await page.getByText(/\d+ sports? selected/i).textContent();
    console.log('Updated counter:', updatedCounter);

    // Check Continue button is now enabled
    const isContinueEnabled = await continueButton.isEnabled();
    console.log('Continue button enabled after selection:', isContinueEnabled);

    // Try to continue
    if (isContinueEnabled) {
      await continueButton.click();
      await page.waitForTimeout(2000);

      // Check what happened
      const currentUrl = page.url();
      console.log('URL after continue:', currentUrl);

      const pageContent = await page.textContent('body');
      console.log('Page content after continue:', pageContent?.substring(0, 300));
    }

    console.log('Console errors:', consoleErrors);
    console.log('JS errors:', jsErrors);
  });

  test('Step 4: Complete Flow Analysis', async ({ page }) => {
    console.log('🔍 Testing complete onboarding flow...');

    // Step 1: Welcome
    await page.getByRole('button', { name: /get started/i }).click();
    await page.waitForTimeout(1000);

    // Step 2: Sports Selection
    await page.getByRole('checkbox').first().click();
    await page.waitForTimeout(500);
    await page.getByRole('checkbox').nth(1).click();
    await page.waitForTimeout(500);

    const continueButton = page.getByRole('button', { name: /continue/i });
    await continueButton.click();
    await page.waitForTimeout(2000);

    // Take screenshot of next step
    await page.screenshot({ path: 'bug-hunt-step3.png', fullPage: true });

    // Check what step we're on
    const stepContent = await page.textContent('body');
    console.log('Step 3 content preview:', stepContent?.substring(0, 500));

    // Look for team selection elements
    const teamCheckboxes = await page.getByRole('checkbox').all();
    console.log('Team checkboxes found:', teamCheckboxes.length);

    if (teamCheckboxes.length > 0) {
      // Select some teams
      await teamCheckboxes[0].click();
      await page.waitForTimeout(500);

      if (teamCheckboxes.length > 1) {
        await teamCheckboxes[1].click();
        await page.waitForTimeout(500);
      }

      // Continue to next step
      const nextContinue = page.getByRole('button', { name: /continue/i });
      const isNextContinueEnabled = await nextContinue.isEnabled();
      console.log('Next continue button enabled:', isNextContinueEnabled);

      if (isNextContinueEnabled) {
        await nextContinue.click();
        await page.waitForTimeout(2000);

        // Take screenshot of preferences step
        await page.screenshot({ path: 'bug-hunt-preferences.png', fullPage: true });

        const preferencesContent = await page.textContent('body');
        console.log('Preferences step content:', preferencesContent?.substring(0, 500));
      }
    }

    console.log('Final console errors:', consoleErrors);
    console.log('Final JS errors:', jsErrors);
  });

  test('Step 5: Error Recovery Testing', async ({ page }) => {
    console.log('🔍 Testing error recovery...');

    // Test corrupted localStorage
    await page.evaluate(() => {
      localStorage.setItem('corner-league-onboarding-state', 'invalid json data');
    });

    await page.reload();
    await page.waitForTimeout(1000);

    const isPageFunctional = await page.getByRole('heading', { name: /welcome to corner league media/i }).isVisible();
    console.log('Page functional after corrupted localStorage:', isPageFunctional);

    // Test network failure
    await page.context().setOffline(true);
    await page.getByRole('button', { name: /get started/i }).click();
    await page.waitForTimeout(1000);

    const worksOffline = await page.getByText(/select and rank your favorite sports/i).isVisible();
    console.log('Works offline:', worksOffline);

    await page.context().setOffline(false);

    console.log('Error recovery console errors:', consoleErrors);
    console.log('Error recovery JS errors:', jsErrors);
  });
});