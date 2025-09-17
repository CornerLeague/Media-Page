/**
 * Custom Onboarding Error Detection Test
 *
 * This test systematically goes through the onboarding flow to identify specific errors,
 * focusing on common issues like state management, validation, and navigation problems.
 */

import { test, expect } from '@playwright/test';

test.describe('Onboarding Error Detection', () => {
  let consoleErrors: string[] = [];
  let jsErrors: string[] = [];
  let networkErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    // Clear error arrays
    consoleErrors = [];
    jsErrors = [];
    networkErrors = [];

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

    // Listen for network errors
    page.on('response', response => {
      if (!response.ok()) {
        networkErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    // Navigate to page and clear localStorage to start fresh
    await page.goto('http://localhost:8080');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('Check for basic onboarding flow errors', async ({ page }) => {
    console.log('🔍 Starting onboarding error detection...');

    // Step 1: Check if we're redirected to onboarding
    await page.waitForTimeout(2000);
    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);

    // Check if onboarding is visible
    const hasWelcomeHeading = await page.locator('h1, h2, h3').filter({ hasText: /welcome/i }).count() > 0;
    const hasSportsSelection = await page.locator('text=Select Sports').count() > 0;

    console.log('Has welcome heading:', hasWelcomeHeading);
    console.log('Has sports selection:', hasSportsSelection);

    // Take screenshot of current state
    await page.screenshot({ path: 'onboarding-initial-state.png', fullPage: true });

    // Check for any visible error messages
    const errorMessages = await page.locator('[role="alert"], .error, .text-destructive, .text-red-500').allTextContents();
    if (errorMessages.length > 0) {
      console.log('❌ Error messages found:', errorMessages);
    }

    // Step 2: Test sports selection if we're on that step
    if (hasSportsSelection) {
      console.log('Testing sports selection...');

      // Check if checkboxes exist and are functional
      const checkboxes = page.locator('input[type="checkbox"]');
      const checkboxCount = await checkboxes.count();
      console.log('Checkbox count:', checkboxCount);

      if (checkboxCount > 0) {
        // Try to click first checkbox
        try {
          await checkboxes.first().click();
          await page.waitForTimeout(1000);

          // Check if selection counter updated
          const selectionText = await page.locator('text=/\\d+ sports? selected/i').textContent();
          console.log('Selection counter:', selectionText);

          // Try to continue
          const continueButton = page.locator('button', { hasText: /continue/i });
          const isContinueVisible = await continueButton.isVisible();
          console.log('Continue button visible:', isContinueVisible);

          if (isContinueVisible) {
            await continueButton.click();
            await page.waitForTimeout(2000);

            const newUrl = page.url();
            console.log('URL after continue:', newUrl);

            // Take screenshot after continue
            await page.screenshot({ path: 'onboarding-after-continue.png', fullPage: true });
          }
        } catch (error) {
          console.log('❌ Error during sports selection:', error.message);
        }
      }
    }

    // Step 3: Check for validation errors
    console.log('Testing validation...');
    const continueButtons = page.locator('button', { hasText: /continue/i });
    if (await continueButtons.count() > 0) {
      // Try to continue without making selections
      await continueButtons.first().click();
      await page.waitForTimeout(1000);

      const validationErrors = await page.locator('[role="alert"], .error, .text-destructive').allTextContents();
      console.log('Validation errors after empty continue:', validationErrors);
    }

    // Step 4: Report all errors found
    console.log('\n📊 ERROR SUMMARY:');
    console.log('Console errors:', consoleErrors.length);
    if (consoleErrors.length > 0) {
      consoleErrors.forEach((error, i) => console.log(`  ${i + 1}. ${error}`));
    }

    console.log('JavaScript errors:', jsErrors.length);
    if (jsErrors.length > 0) {
      jsErrors.forEach((error, i) => console.log(`  ${i + 1}. ${error}`));
    }

    console.log('Network errors:', networkErrors.length);
    if (networkErrors.length > 0) {
      networkErrors.forEach((error, i) => console.log(`  ${i + 1}. ${error}`));
    }

    // Step 5: Check localStorage state
    const localStorageData = await page.evaluate(() => {
      const keys = Object.keys(localStorage);
      const data: Record<string, any> = {};
      keys.forEach(key => {
        try {
          data[key] = JSON.parse(localStorage.getItem(key) || '');
        } catch {
          data[key] = localStorage.getItem(key);
        }
      });
      return data;
    });

    console.log('LocalStorage data:', JSON.stringify(localStorageData, null, 2));
  });
});