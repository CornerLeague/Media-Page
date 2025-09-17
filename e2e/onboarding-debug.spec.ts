/**
 * Onboarding Debug Test
 *
 * Comprehensive investigation of the onboarding flow to identify
 * why users can't continue after selecting sports
 */

import { test, expect } from '@playwright/test';

test.describe('Onboarding Debug Investigation', () => {
  let consoleMessages: string[] = [];
  let jsErrors: string[] = [];
  let networkFailures: string[] = [];

  test.beforeEach(async ({ page }) => {
    // Clear arrays
    consoleMessages = [];
    jsErrors = [];
    networkFailures = [];

    // Listen for console messages
    page.on('console', msg => {
      consoleMessages.push(`[${msg.type()}] ${msg.text()}`);
    });

    // Listen for JS errors
    page.on('pageerror', error => {
      jsErrors.push(`JS Error: ${error.message}`);
    });

    // Listen for network failures
    page.on('response', response => {
      if (!response.ok() && response.status() !== 404) {
        networkFailures.push(`Network Error: ${response.status()} ${response.url()}`);
      }
    });

    // Start fresh
    await page.goto('http://localhost:8080');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('Investigate onboarding flow step by step', async ({ page }) => {
    console.log('🚀 Starting onboarding flow investigation...');

    // Take initial screenshot
    await page.screenshot({ path: 'debug-01-initial-load.png', fullPage: true });

    // Wait a bit for any async operations
    await page.waitForTimeout(3000);

    // Check what's actually on the page
    const pageTitle = await page.title();
    const currentUrl = page.url();
    console.log(`📍 Page title: "${pageTitle}"`);
    console.log(`📍 Current URL: ${currentUrl}`);

    // Look for any headings on the page
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents();
    console.log('📍 Found headings:', headings);

    // Look for any visible text containing "welcome" or "onboarding"
    const welcomeElements = await page.locator('text=/welcome/i').allTextContents();
    const onboardingElements = await page.locator('text=/onboarding/i').allTextContents();
    console.log('📍 Welcome elements:', welcomeElements);
    console.log('📍 Onboarding elements:', onboardingElements);

    // Check if we're on the onboarding page
    const isOnOnboardingPage = currentUrl.includes('/onboarding') ||
                               welcomeElements.length > 0 ||
                               onboardingElements.length > 0;

    if (!isOnOnboardingPage) {
      console.log('❌ Not on onboarding page, trying to navigate there...');
      await page.goto('http://localhost:8080/onboarding');
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'debug-02-onboarding-direct.png', fullPage: true });
    }

    // Look for any buttons on the page
    const buttons = await page.locator('button').allTextContents();
    console.log('📍 Found buttons:', buttons);

    // Try to find and click "Get Started" button
    const getStartedButton = page.locator('button', { hasText: /get started|continue|start/i }).first();
    const getStartedVisible = await getStartedButton.isVisible().catch(() => false);

    if (getStartedVisible) {
      console.log('✅ Found Get Started button, clicking...');
      await getStartedButton.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'debug-03-after-get-started.png', fullPage: true });
    } else {
      console.log('❌ No Get Started button found');
    }

    // Now check for sports selection
    console.log('🏈 Looking for sports selection...');

    // Look for sports-related content
    const sportsText = await page.locator('text=/sport/i').allTextContents();
    const sportsHeadings = await page.locator('h1, h2, h3', { hasText: /sport/i }).allTextContents();
    console.log('📍 Sports text found:', sportsText);
    console.log('📍 Sports headings:', sportsHeadings);

    // Look for checkboxes (sports selection)
    const checkboxes = page.locator('input[type="checkbox"], [role="checkbox"]');
    const checkboxCount = await checkboxes.count();
    console.log(`📍 Found ${checkboxCount} checkboxes`);

    if (checkboxCount > 0) {
      console.log('✅ Sports selection found, testing selection...');

      // Try to select first sport
      const firstCheckbox = checkboxes.first();
      const isFirstVisible = await firstCheckbox.isVisible().catch(() => false);

      if (isFirstVisible) {
        console.log('📱 Clicking first sport...');
        await firstCheckbox.click();
        await page.waitForTimeout(1000);

        // Check if it's actually selected
        const isChecked = await firstCheckbox.isChecked().catch(() => false);
        console.log(`📱 First sport checked: ${isChecked}`);

        // Take screenshot after selection
        await page.screenshot({ path: 'debug-04-first-sport-selected.png', fullPage: true });

        // Try to select a second sport
        if (checkboxCount > 1) {
          console.log('📱 Clicking second sport...');
          const secondCheckbox = checkboxes.nth(1);
          await secondCheckbox.click();
          await page.waitForTimeout(1000);

          const isSecondChecked = await secondCheckbox.isChecked().catch(() => false);
          console.log(`📱 Second sport checked: ${isSecondChecked}`);

          await page.screenshot({ path: 'debug-05-two-sports-selected.png', fullPage: true });
        }

        // Look for selection counter
        const selectionCounter = await page.locator('text=/\\d+.*sport.*selected/i').textContent().catch(() => null);
        console.log(`📊 Selection counter: ${selectionCounter}`);

        // Check for continue button
        const continueButton = page.locator('button', { hasText: /continue/i });
        const continueVisible = await continueButton.isVisible().catch(() => false);
        const continueEnabled = await continueButton.isEnabled().catch(() => false);

        console.log(`🔘 Continue button visible: ${continueVisible}`);
        console.log(`🔘 Continue button enabled: ${continueEnabled}`);

        if (continueVisible) {
          if (continueEnabled) {
            console.log('✅ Clicking continue button...');
            await continueButton.click();
            await page.waitForTimeout(3000);

            // Check if we moved to next step
            const newUrl = page.url();
            const newHeadings = await page.locator('h1, h2, h3').allTextContents();
            console.log(`📍 URL after continue: ${newUrl}`);
            console.log(`📍 New headings: ${newHeadings}`);

            await page.screenshot({ path: 'debug-06-after-continue.png', fullPage: true });

            // Check if we're on teams selection
            const teamElements = await page.locator('text=/team/i').allTextContents();
            console.log('📍 Team elements found:', teamElements);

          } else {
            console.log('❌ Continue button is disabled');

            // Check for validation errors
            const errorElements = await page.locator('[role="alert"], .error, .text-destructive, .text-red-500').allTextContents();
            console.log('📍 Error messages:', errorElements);
          }
        } else {
          console.log('❌ Continue button not visible');
        }
      } else {
        console.log('❌ First checkbox not visible');
      }
    } else {
      console.log('❌ No sports checkboxes found');
    }

    // Check localStorage state
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

    console.log('💾 localStorage data:', JSON.stringify(localStorageData, null, 2));

    // Final report
    console.log('\n📋 INVESTIGATION SUMMARY:');
    console.log(`📊 Console messages: ${consoleMessages.length}`);
    if (consoleMessages.length > 0) {
      console.log('   Messages:');
      consoleMessages.forEach((msg, i) => console.log(`   ${i + 1}. ${msg}`));
    }

    console.log(`❌ JS errors: ${jsErrors.length}`);
    if (jsErrors.length > 0) {
      jsErrors.forEach((error, i) => console.log(`   ${i + 1}. ${error}`));
    }

    console.log(`🌐 Network failures: ${networkFailures.length}`);
    if (networkFailures.length > 0) {
      networkFailures.forEach((error, i) => console.log(`   ${i + 1}. ${error}`));
    }

    // Take final screenshot
    await page.screenshot({ path: 'debug-07-final-state.png', fullPage: true });
  });

  test('Test alternative sport selection methods', async ({ page }) => {
    console.log('🔄 Testing alternative sport selection methods...');

    // Go to onboarding
    await page.goto('http://localhost:8080/onboarding');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Try to get past welcome screen
    const getStartedButton = page.locator('button', { hasText: /get started|continue/i }).first();
    const getStartedVisible = await getStartedButton.isVisible().catch(() => false);

    if (getStartedVisible) {
      await getStartedButton.click();
      await page.waitForTimeout(2000);
    }

    // Try different ways to select sports
    console.log('🧪 Testing different selection methods...');

    // Method 1: Click on sport cards
    const sportCards = page.locator('[role="checkbox"], .sport-card, [data-testid*="sport"]');
    const cardCount = await sportCards.count();
    console.log(`Method 1: Found ${cardCount} sport cards`);

    if (cardCount > 0) {
      await sportCards.first().click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'debug-method1-card-click.png', fullPage: true });
    }

    // Method 2: Look for text containing sport names
    const sportNames = ['NFL', 'NBA', 'MLB', 'NHL', 'Soccer', 'Football', 'Basketball'];

    for (const sportName of sportNames) {
      const sportElement = page.locator(`text=${sportName}`).first();
      const isVisible = await sportElement.isVisible().catch(() => false);

      if (isVisible) {
        console.log(`📱 Found ${sportName}, attempting click...`);
        await sportElement.click();
        await page.waitForTimeout(500);
        break;
      }
    }

    await page.screenshot({ path: 'debug-method2-text-click.png', fullPage: true });

    // Method 3: Use keyboard navigation
    console.log('⌨️ Testing keyboard navigation...');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    await page.screenshot({ path: 'debug-method3-keyboard.png', fullPage: true });

    // Check final state
    const finalButtons = await page.locator('button').allTextContents();
    console.log('🔘 Final buttons:', finalButtons);

    const continueButton = page.locator('button', { hasText: /continue/i });
    const continueEnabled = await continueButton.isEnabled().catch(() => false);
    console.log(`🔘 Continue enabled after all methods: ${continueEnabled}`);
  });
});