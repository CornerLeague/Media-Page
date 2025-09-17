import { test, expect } from '@playwright/test';

/**
 * Focused test to reproduce the "Failed to save preferences" error
 * This test goes directly to the onboarding flow and attempts completion
 */

test.describe('Onboarding Save Error Investigation', () => {
  test.beforeEach(async ({ page }) => {
    // Listen for all console messages
    page.on('console', msg => {
      console.log(`Console ${msg.type()}: ${msg.text()}`);
    });

    // Listen for page errors
    page.on('pageerror', error => {
      console.log(`Page Error: ${error.message}`);
    });

    // Listen for failed requests
    page.on('response', response => {
      if (!response.ok() && response.url().includes('localhost')) {
        console.log(`❌ Request failed: ${response.method()} ${response.url()} - ${response.status()}`);
      }
    });

    // Clear storage and navigate
    await page.goto('http://localhost:8080');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('Navigate to onboarding and attempt to complete', async ({ page }) => {
    console.log('🔍 Testing onboarding completion error...');

    // Wait for page to load
    await page.waitForTimeout(3000);

    // Take initial screenshot
    await page.screenshot({ path: 'onboarding-initial.png', fullPage: true });

    // Check what's on the page
    const pageTitle = await page.title();
    const url = page.url();
    console.log(`Page title: ${pageTitle}`);
    console.log(`Current URL: ${url}`);

    // Look for onboarding elements
    const onboardingSelectors = [
      'text=Welcome',
      'text=Get Started',
      'text=Select Sports',
      'text=Choose Your Sports',
      'text=sports selected',
      '[data-testid*="sport"]',
      'input[type="checkbox"]'
    ];

    let foundOnboarding = false;
    for (const selector of onboardingSelectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        console.log(`✅ Found onboarding element: ${selector} (${count})`);
        foundOnboarding = true;
      }
    }

    if (!foundOnboarding) {
      // Try to navigate to onboarding directly
      console.log('No onboarding elements found, trying direct navigation...');
      await page.goto('http://localhost:8080/onboarding');
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'onboarding-direct.png', fullPage: true });
    }

    // Now try to go through the onboarding flow
    await navigateOnboardingFlow(page);
  });

  test('Test API endpoints directly', async ({ page }) => {
    console.log('🌐 Testing API endpoints...');

    // Test backend health
    const healthTest = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        return { success: true, status: response.status, data };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    console.log('Health endpoint test:', healthTest);

    // Test user creation endpoint (the one failing in onboarding)
    const userCreateTest = await page.evaluate(async () => {
      try {
        const testData = {
          clerkUserId: 'test-123',
          sports: [{ sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true }],
          teams: [{ teamId: 'team-1', name: 'Test Team', sportId: 'nfl', league: 'NFL', affinityScore: 85 }],
          preferences: {
            newsTypes: [{ type: 'general', enabled: true, priority: 1 }],
            notifications: {
              push: false,
              email: false,
              gameReminders: false,
              newsAlerts: false,
              scoreUpdates: false,
            },
            contentFrequency: 'standard'
          }
        };

        const response = await fetch('http://localhost:8000/api/v1/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(testData)
        });

        const responseText = await response.text();
        let data;
        try {
          data = JSON.parse(responseText);
        } catch {
          data = responseText;
        }

        return {
          success: response.ok,
          status: response.status,
          statusText: response.statusText,
          data
        };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    console.log('User creation endpoint test:', userCreateTest);
  });
});

async function navigateOnboardingFlow(page) {
  console.log('🚀 Starting onboarding flow navigation...');

  // Step 1: Welcome/Get Started
  const getStartedButton = page.locator('button', { hasText: /get started|continue|start/i });
  if (await getStartedButton.isVisible({ timeout: 5000 })) {
    console.log('✅ Found Get Started button');
    await getStartedButton.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'onboarding-after-start.png', fullPage: true });
  }

  // Step 2: Sports Selection
  const sportsCheckboxes = page.locator('input[type="checkbox"]');
  const checkboxCount = await sportsCheckboxes.count();
  console.log(`Found ${checkboxCount} sport checkboxes`);

  if (checkboxCount > 0) {
    // Select first 2 sports
    await sportsCheckboxes.nth(0).click();
    await page.waitForTimeout(500);
    if (checkboxCount > 1) {
      await sportsCheckboxes.nth(1).click();
      await page.waitForTimeout(500);
    }

    console.log('✅ Selected sports');
    await page.screenshot({ path: 'onboarding-sports-selected.png', fullPage: true });

    // Continue from sports
    const continueButton = page.locator('button', { hasText: /continue/i });
    if (await continueButton.isVisible()) {
      await continueButton.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'onboarding-after-sports.png', fullPage: true });
    }
  }

  // Step 3: Team Selection (if present)
  const teamElements = page.locator('[data-testid*="team"], .team-card');
  const teamCount = await teamElements.count();
  console.log(`Found ${teamCount} team elements`);

  if (teamCount > 0) {
    await teamElements.first().click();
    await page.waitForTimeout(500);
    console.log('✅ Selected team');
  }

  // Continue from teams
  const teamContinueButton = page.locator('button', { hasText: /continue/i });
  if (await teamContinueButton.isVisible()) {
    await teamContinueButton.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'onboarding-after-teams.png', fullPage: true });
  }

  // Step 4: Preferences (if present)
  const preferenceElements = page.locator('input[type="checkbox"], select');
  const prefCount = await preferenceElements.count();
  console.log(`Found ${prefCount} preference elements`);

  if (prefCount > 0) {
    // Toggle first preference
    await preferenceElements.first().click();
    await page.waitForTimeout(500);
    console.log('✅ Set preferences');
  }

  // Continue from preferences
  const prefContinueButton = page.locator('button', { hasText: /continue/i });
  if (await prefContinueButton.isVisible()) {
    await prefContinueButton.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'onboarding-after-preferences.png', fullPage: true });
  }

  // Step 5: Final completion
  console.log('🏁 Attempting final completion...');

  // Look for completion button
  const completionButtons = [
    page.locator('button', { hasText: /complete|finish|done|save|get started/i }),
    page.locator('button[type="submit"]'),
    page.locator('[data-testid*="complete"]'),
    page.locator('[data-testid*="finish"]')
  ];

  let foundCompletionButton = false;
  for (const buttonLocator of completionButtons) {
    const count = await buttonLocator.count();
    if (count > 0) {
      const button = buttonLocator.first();
      if (await button.isVisible()) {
        console.log(`✅ Found completion button: ${await button.textContent()}`);
        foundCompletionButton = true;

        // Click and wait for result
        console.log('Clicking completion button...');
        await button.click();

        // Wait for any network activity
        await page.waitForTimeout(3000);

        // Check for error messages
        const errorSelectors = [
          '[role="alert"]',
          '.error',
          '.text-destructive',
          '.text-red-500',
          '[data-testid*="error"]'
        ];

        for (const selector of errorSelectors) {
          const errorElements = page.locator(selector);
          const errorCount = await errorElements.count();
          if (errorCount > 0) {
            const errorText = await errorElements.allTextContents();
            console.log(`❌ Found error messages (${selector}):`, errorText);
          }
        }

        // Take final screenshot
        await page.screenshot({ path: 'onboarding-final-result.png', fullPage: true });
        break;
      }
    }
  }

  if (!foundCompletionButton) {
    console.log('⚠️ No completion button found');

    // List all buttons on the page
    const allButtons = page.locator('button');
    const buttonCount = await allButtons.count();
    console.log(`Found ${buttonCount} total buttons on page`);

    for (let i = 0; i < Math.min(buttonCount, 10); i++) {
      const buttonText = await allButtons.nth(i).textContent();
      console.log(`  Button ${i + 1}: "${buttonText}"`);
    }
  }

  // Final state check
  const currentUrl = page.url();
  console.log(`Final URL: ${currentUrl}`);

  // Check localStorage for onboarding state
  const storageData = await page.evaluate(() => {
    const keys = Object.keys(localStorage);
    const data = {};
    keys.forEach(key => {
      if (key.includes('corner-league') || key.includes('onboarding')) {
        try {
          data[key] = JSON.parse(localStorage.getItem(key));
        } catch {
          data[key] = localStorage.getItem(key);
        }
      }
    });
    return data;
  });

  console.log('Final localStorage state:', JSON.stringify(storageData, null, 2));
}