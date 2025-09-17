/**
 * Onboarding Flow Test with Authentication Bypass
 *
 * This test bypasses authentication to test the actual onboarding flow
 * and identify issues with sport selection continuation
 */

import { test, expect } from '@playwright/test';

test.describe('Onboarding Flow - Authentication Bypassed', () => {
  let consoleMessages: string[] = [];
  let jsErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    // Clear arrays
    consoleMessages = [];
    jsErrors = [];

    // Listen for console messages
    page.on('console', msg => {
      consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
    });

    // Listen for JS errors
    page.on('pageerror', error => {
      jsErrors.push(`JS Error: ${error.message}`);
    });

    // Set up test mode to bypass authentication
    await page.addInitScript(() => {
      (window as any).__PLAYWRIGHT_TEST__ = true;
    });

    // Navigate and clear storage
    await page.goto('http://localhost:8080');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('Complete onboarding flow with authentication bypassed', async ({ page }) => {
    console.log('🚀 Testing onboarding flow with auth bypass...');

    // Force navigation to onboarding
    await page.goto('http://localhost:8080/onboarding');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Take screenshot
    await page.screenshot({ path: 'bypass-01-onboarding-page.png', fullPage: true });

    const currentUrl = page.url();
    console.log(`📍 Current URL: ${currentUrl}`);

    // Check if we successfully reached onboarding
    expect(currentUrl).toContain('/onboarding');

    // Look for onboarding content
    const headings = await page.locator('h1, h2, h3').allTextContents();
    console.log('📍 Found headings:', headings);

    // Step 1: Welcome screen - look for Get Started button
    const getStartedButton = page.locator('button', { hasText: /get started|start|begin/i });
    const getStartedVisible = await getStartedButton.isVisible().catch(() => false);

    if (getStartedVisible) {
      console.log('✅ Found Get Started button on welcome screen');
      await getStartedButton.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'bypass-02-after-get-started.png', fullPage: true });
    } else {
      console.log('⚠️ No Get Started button found, checking if already on sports selection...');
    }

    // Step 2: Sports Selection - This is where the issue should be
    console.log('🏈 Testing sports selection...');

    // Look for sports selection indicators
    const sportsHeading = page.locator('h1, h2, h3', { hasText: /sport|choose.*sport/i });
    const sportsHeadingVisible = await sportsHeading.isVisible().catch(() => false);

    if (sportsHeadingVisible) {
      console.log('✅ Sports selection page found');

      // Look for sport cards/checkboxes
      const sportCheckboxes = page.locator('input[type="checkbox"], [role="checkbox"]');
      const checkboxCount = await sportCheckboxes.count();
      console.log(`📊 Found ${checkboxCount} sport checkboxes`);

      if (checkboxCount > 0) {
        console.log('📱 Testing sport selection...');

        // Select first sport
        console.log('Selecting first sport...');
        await sportCheckboxes.first().click();
        await page.waitForTimeout(1000);

        const firstChecked = await sportCheckboxes.first().isChecked().catch(() => false);
        console.log(`✅ First sport selected: ${firstChecked}`);

        // Select second sport
        if (checkboxCount > 1) {
          console.log('Selecting second sport...');
          await sportCheckboxes.nth(1).click();
          await page.waitForTimeout(1000);

          const secondChecked = await sportCheckboxes.nth(1).isChecked().catch(() => false);
          console.log(`✅ Second sport selected: ${secondChecked}`);
        }

        await page.screenshot({ path: 'bypass-03-sports-selected.png', fullPage: true });

        // Check selection counter
        const selectionCounter = await page.locator('text=/\\d+.*sport.*selected/i').textContent().catch(() => null);
        console.log(`📊 Selection counter shows: ${selectionCounter}`);

        // CRITICAL TEST: Check continue button state
        const continueButton = page.locator('button', { hasText: /continue/i });
        const continueExists = await continueButton.count() > 0;
        const continueVisible = await continueButton.isVisible().catch(() => false);
        const continueEnabled = await continueButton.isEnabled().catch(() => false);

        console.log(`🔘 Continue button exists: ${continueExists}`);
        console.log(`🔘 Continue button visible: ${continueVisible}`);
        console.log(`🔘 Continue button enabled: ${continueEnabled}`);

        // Try to click continue if it exists and is enabled
        if (continueExists && continueVisible && continueEnabled) {
          console.log('🎯 Attempting to click continue button...');

          const beforeUrl = page.url();
          await continueButton.click();
          await page.waitForTimeout(3000);

          const afterUrl = page.url();
          console.log(`📍 URL before continue: ${beforeUrl}`);
          console.log(`📍 URL after continue: ${afterUrl}`);

          await page.screenshot({ path: 'bypass-04-after-continue.png', fullPage: true });

          // Check if we moved to next step
          const newHeadings = await page.locator('h1, h2, h3').allTextContents();
          console.log('📍 New headings after continue:', newHeadings);

          // Check for team selection elements
          const teamElements = await page.locator('text=/team|select.*team/i').allTextContents();
          console.log('📍 Team-related elements found:', teamElements);

          // Success check
          const movedToNextStep = afterUrl !== beforeUrl ||
                                  teamElements.length > 0 ||
                                  newHeadings.some(h => h.toLowerCase().includes('team'));

          if (movedToNextStep) {
            console.log('✅ SUCCESS: Moved to next step after sport selection');
          } else {
            console.log('❌ FAILED: Did not move to next step after sport selection');
          }

        } else {
          console.log('❌ ISSUE IDENTIFIED: Continue button is not available or enabled');

          if (!continueExists) {
            console.log('   - Continue button does not exist in DOM');
          } else if (!continueVisible) {
            console.log('   - Continue button exists but is not visible');
          } else if (!continueEnabled) {
            console.log('   - Continue button is visible but disabled');
          }

          // Check for validation errors
          const errorMessages = await page.locator('[role="alert"], .error, .text-destructive, .text-red-500').allTextContents();
          if (errorMessages.length > 0) {
            console.log('📍 Error messages found:', errorMessages);
          }

          // Check localStorage state for debugging
          const storageData = await page.evaluate(() => {
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
          console.log('💾 Current localStorage state:', JSON.stringify(storageData, null, 2));
        }

      } else {
        console.log('❌ ISSUE: No sport checkboxes found on sports selection page');
      }

    } else {
      console.log('❌ ISSUE: Sports selection page not found');

      // Check what page we're actually on
      const allText = await page.locator('body').textContent();
      console.log('📍 Current page text contains:', allText?.substring(0, 500) + '...');
    }

    // Final error summary
    console.log('\n📋 ERROR SUMMARY:');
    console.log(`❌ JS errors: ${jsErrors.length}`);
    if (jsErrors.length > 0) {
      jsErrors.forEach((error, i) => console.log(`   ${i + 1}. ${error}`));
    }

    // Check for React/hook errors in console
    const reactErrors = consoleMessages.filter(msg =>
      msg.includes('Error') ||
      msg.includes('Warning') ||
      msg.includes('useOnboarding') ||
      msg.includes('validation')
    );

    if (reactErrors.length > 0) {
      console.log('⚠️ React/validation related messages:');
      reactErrors.forEach((error, i) => console.log(`   ${i + 1}. ${error}`));
    }
  });

  test('Test sport selection validation logic specifically', async ({ page }) => {
    console.log('🧪 Testing sport selection validation logic...');

    // Set up test mode and go to onboarding
    await page.goto('http://localhost:8080/onboarding');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Skip welcome screen if present
    const getStartedButton = page.locator('button', { hasText: /get started/i });
    const getStartedVisible = await getStartedButton.isVisible().catch(() => false);
    if (getStartedVisible) {
      await getStartedButton.click();
      await page.waitForTimeout(2000);
    }

    // Test validation states
    console.log('🔍 Testing validation states...');

    // Check initial state - continue should be disabled
    const continueButton = page.locator('button', { hasText: /continue/i });
    const initiallyEnabled = await continueButton.isEnabled().catch(() => false);
    console.log(`🔘 Continue button initially enabled: ${initiallyEnabled}`);

    // Select one sport
    const checkboxes = page.locator('input[type="checkbox"], [role="checkbox"]');
    const checkboxCount = await checkboxes.count();

    if (checkboxCount > 0) {
      console.log('📱 Selecting one sport to test validation...');
      await checkboxes.first().click();
      await page.waitForTimeout(1000);

      // Check if continue becomes enabled
      const enabledAfterOne = await continueButton.isEnabled().catch(() => false);
      console.log(`🔘 Continue enabled after selecting 1 sport: ${enabledAfterOne}`);

      // Check validation message/counter
      const validationText = await page.locator('text=/\\d+.*sport.*selected/i').textContent().catch(() => null);
      console.log(`📊 Validation text: ${validationText}`);

      // Test deselection
      console.log('📱 Testing deselection...');
      await checkboxes.first().click(); // deselect
      await page.waitForTimeout(1000);

      const enabledAfterDeselect = await continueButton.isEnabled().catch(() => false);
      console.log(`🔘 Continue enabled after deselecting: ${enabledAfterDeselect}`);

      // Re-select and test continue
      console.log('📱 Re-selecting and testing continue...');
      await checkboxes.first().click();
      await page.waitForTimeout(1000);

      const finalEnabled = await continueButton.isEnabled().catch(() => false);
      if (finalEnabled) {
        console.log('✅ Continue button is properly enabled, testing click...');
        await continueButton.click();
        await page.waitForTimeout(2000);

        const newUrl = page.url();
        console.log(`📍 URL after continue: ${newUrl}`);

        // Check if navigation occurred
        const hasNavigated = !newUrl.includes('/onboarding') ||
                            newUrl.includes('/onboarding') && newUrl !== 'http://localhost:8080/onboarding';

        console.log(`🎯 Navigation successful: ${hasNavigated}`);
      } else {
        console.log('❌ Continue button remains disabled even after sport selection');
      }
    }

    await page.screenshot({ path: 'validation-test-final.png', fullPage: true });
  });
});