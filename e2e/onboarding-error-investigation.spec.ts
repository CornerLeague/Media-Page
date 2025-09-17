import { test, expect, Page } from '@playwright/test';

/**
 * Comprehensive Onboarding Error Investigation Test
 *
 * This test investigates the "Failed to save preferences" error by:
 * 1. Running through the complete onboarding flow
 * 2. Monitoring all network requests and responses
 * 3. Capturing console errors and JavaScript errors
 * 4. Checking API connectivity and authentication
 * 5. Verifying error handling and user feedback
 */

interface NetworkRequest {
  url: string;
  method: string;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  payload?: any;
  response?: any;
  error?: string;
}

interface TestResults {
  consoleErrors: string[];
  jsErrors: string[];
  networkRequests: NetworkRequest[];
  apiErrors: string[];
  authErrors: string[];
  validationErrors: string[];
  finalError?: string;
}

test.describe('Onboarding Error Investigation', () => {
  let results: TestResults;

  test.beforeEach(async ({ page }) => {
    // Initialize results tracking
    results = {
      consoleErrors: [],
      jsErrors: [],
      networkRequests: [],
      apiErrors: [],
      authErrors: [],
      validationErrors: [],
    };

    // Setup comprehensive error tracking
    await setupErrorTracking(page, results);

    // Clear all browser storage to start fresh
    await page.goto('http://localhost:8080');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('Complete onboarding flow with error investigation', async ({ page }) => {
    console.log('🔍 Starting comprehensive onboarding error investigation...');

    // Step 1: Check initial state and API connectivity
    await checkApiConnectivity(page, results);

    // Step 2: Navigate through onboarding steps
    await navigateWelcomeStep(page, results);
    await navigateSportsSelection(page, results);
    await navigateTeamSelection(page, results);
    await navigatePreferencesSetup(page, results);

    // Step 3: Attempt to complete onboarding (where the error occurs)
    await attemptOnboardingCompletion(page, results);

    // Step 4: Generate comprehensive report
    await generateErrorReport(results);
  });

  test('API endpoint testing', async ({ page }) => {
    console.log('🌐 Testing API endpoints directly...');

    // Test health check endpoint
    const healthResponse = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        return {
          status: response.status,
          ok: response.ok,
          data: await response.json().catch(() => null)
        };
      } catch (error) {
        return { error: error.message };
      }
    });

    console.log('Health check response:', healthResponse);

    // Test user creation endpoint
    const userTestResponse = await page.evaluate(async () => {
      try {
        const testData = {
          clerkUserId: 'test-user-id',
          sports: [],
          teams: [],
          preferences: {
            newsTypes: [],
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

        return {
          status: response.status,
          ok: response.ok,
          statusText: response.statusText,
          data: await response.json().catch(() => null)
        };
      } catch (error) {
        return { error: error.message };
      }
    });

    console.log('User creation test response:', userTestResponse);
  });

  test('Authentication flow testing', async ({ page }) => {
    console.log('🔐 Testing authentication flow...');

    // Check if Clerk is properly initialized
    const clerkStatus = await page.evaluate(() => {
      return {
        clerkLoaded: typeof window.Clerk !== 'undefined',
        publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
        authState: window.Clerk ? {
          isSignedIn: window.Clerk.user !== null,
          userId: window.Clerk.user?.id,
        } : null
      };
    });

    console.log('Clerk status:', clerkStatus);
  });
});

async function setupErrorTracking(page: Page, results: TestResults) {
  // Track console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const errorText = msg.text();
      results.consoleErrors.push(errorText);
      console.log('❌ Console Error:', errorText);
    }
  });

  // Track JavaScript errors
  page.on('pageerror', error => {
    const errorMessage = error.message;
    results.jsErrors.push(errorMessage);
    console.log('💥 JavaScript Error:', errorMessage);
  });

  // Track network requests and responses
  page.on('request', request => {
    const url = request.url();
    if (url.includes('localhost:8000') || url.includes('api')) {
      console.log(`🌐 Request: ${request.method()} ${url}`);
    }
  });

  page.on('response', async response => {
    const url = response.url();

    if (url.includes('localhost:8000') || url.includes('api')) {
      const networkRequest: NetworkRequest = {
        url,
        method: response.request().method(),
        status: response.status(),
        statusText: response.statusText(),
        headers: await response.allHeaders(),
      };

      // Try to get request payload
      try {
        const request = response.request();
        if (request.method() !== 'GET') {
          networkRequest.payload = request.postDataJSON();
        }
      } catch (e) {
        // Ignore if unable to get payload
      }

      // Try to get response data
      try {
        if (response.status() >= 400) {
          networkRequest.response = await response.json().catch(() => response.text());
          networkRequest.error = `HTTP ${response.status()}: ${response.statusText()}`;
          results.apiErrors.push(networkRequest.error);
        } else {
          networkRequest.response = await response.json().catch(() => 'Non-JSON response');
        }
      } catch (e) {
        networkRequest.error = 'Failed to read response';
      }

      results.networkRequests.push(networkRequest);

      if (!response.ok()) {
        console.log(`❌ API Error: ${networkRequest.method} ${url} - ${response.status()} ${response.statusText()}`);
      } else {
        console.log(`✅ API Success: ${networkRequest.method} ${url} - ${response.status()}`);
      }
    }
  });
}

async function checkApiConnectivity(page: Page, results: TestResults) {
  console.log('🔗 Checking API connectivity...');

  // Check if backend is running
  const backendStatus = await page.evaluate(async () => {
    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      return {
        accessible: true,
        status: response.status,
        data: await response.json().catch(() => null)
      };
    } catch (error) {
      return {
        accessible: false,
        error: error.message
      };
    }
  });

  console.log('Backend status:', backendStatus);

  if (!backendStatus.accessible) {
    results.apiErrors.push('Backend API is not accessible');
  }
}

async function navigateWelcomeStep(page: Page, results: TestResults) {
  console.log('👋 Navigating welcome step...');

  await page.waitForTimeout(2000);

  // Check if we're on the welcome screen
  const welcomeElements = await page.locator('h1, h2, h3').filter({ hasText: /welcome/i }).count();
  if (welcomeElements > 0) {
    console.log('✅ Welcome screen detected');

    // Look for Get Started button
    const getStartedButton = page.locator('button', { hasText: /get started|continue/i });
    if (await getStartedButton.isVisible()) {
      await getStartedButton.click();
      await page.waitForTimeout(1000);
      console.log('✅ Clicked Get Started');
    }
  } else {
    console.log('⚠️ Welcome screen not found, might already be past this step');
  }

  await page.screenshot({ path: 'debug-welcome-step.png', fullPage: true });
}

async function navigateSportsSelection(page: Page, results: TestResults) {
  console.log('🏈 Navigating sports selection...');

  await page.waitForTimeout(1000);

  // Look for sports selection elements
  const sportsCheckboxes = page.locator('input[type="checkbox"]');
  const checkboxCount = await sportsCheckboxes.count();

  console.log(`Found ${checkboxCount} sport checkboxes`);

  if (checkboxCount > 0) {
    // Select first 2 sports
    await sportsCheckboxes.nth(0).click();
    await page.waitForTimeout(500);
    await sportsCheckboxes.nth(1).click();
    await page.waitForTimeout(500);

    console.log('✅ Selected 2 sports');

    // Check if continue button is enabled
    const continueButton = page.locator('button', { hasText: /continue/i });
    if (await continueButton.isVisible()) {
      await continueButton.click();
      await page.waitForTimeout(1000);
      console.log('✅ Clicked Continue from sports selection');
    }
  } else {
    console.log('⚠️ No sports checkboxes found');
  }

  await page.screenshot({ path: 'debug-sports-step.png', fullPage: true });
}

async function navigateTeamSelection(page: Page, results: TestResults) {
  console.log('👥 Navigating team selection...');

  await page.waitForTimeout(1000);

  // Look for team selection elements
  const teamElements = page.locator('[data-testid*="team"], .team-card, input[type="checkbox"]');
  const teamCount = await teamElements.count();

  console.log(`Found ${teamCount} team elements`);

  if (teamCount > 0) {
    // Select first team if available
    await teamElements.first().click();
    await page.waitForTimeout(500);
    console.log('✅ Selected a team');
  }

  // Try to continue
  const continueButton = page.locator('button', { hasText: /continue/i });
  if (await continueButton.isVisible()) {
    await continueButton.click();
    await page.waitForTimeout(1000);
    console.log('✅ Clicked Continue from team selection');
  }

  await page.screenshot({ path: 'debug-teams-step.png', fullPage: true });
}

async function navigatePreferencesSetup(page: Page, results: TestResults) {
  console.log('⚙️ Navigating preferences setup...');

  await page.waitForTimeout(1000);

  // Look for preference controls
  const preferenceControls = page.locator('input[type="checkbox"], select, input[type="radio"]');
  const controlCount = await preferenceControls.count();

  console.log(`Found ${controlCount} preference controls`);

  if (controlCount > 0) {
    // Toggle some preferences
    const checkboxes = page.locator('input[type="checkbox"]');
    const checkboxCount = await checkboxes.count();

    if (checkboxCount > 0) {
      await checkboxes.first().click();
      await page.waitForTimeout(300);
      console.log('✅ Toggled first preference');
    }
  }

  await page.screenshot({ path: 'debug-preferences-step.png', fullPage: true });
}

async function attemptOnboardingCompletion(page: Page, results: TestResults) {
  console.log('🏁 Attempting onboarding completion...');

  await page.waitForTimeout(1000);

  // Look for completion button
  const completeButton = page.locator('button', { hasText: /complete|finish|done/i });

  if (await completeButton.isVisible()) {
    console.log('Found completion button, clicking...');

    // Clear previous errors
    results.consoleErrors = [];
    results.jsErrors = [];
    results.apiErrors = [];

    // Click complete and wait for response
    await completeButton.click();

    // Wait for any network activity to complete
    await page.waitForTimeout(3000);

    // Check for error messages on the page
    const errorMessages = await page.locator('[role="alert"], .error, .text-destructive, .text-red-500').allTextContents();

    if (errorMessages.length > 0) {
      results.finalError = errorMessages.join('; ');
      console.log('❌ Error messages found:', errorMessages);
    }

    // Check if we're still on onboarding or redirected
    const currentUrl = page.url();
    console.log('Current URL after completion attempt:', currentUrl);

  } else {
    console.log('⚠️ No completion button found');
  }

  await page.screenshot({ path: 'debug-completion-attempt.png', fullPage: true });
}

async function generateErrorReport(results: TestResults) {
  console.log('\n📊 COMPREHENSIVE ERROR INVESTIGATION REPORT');
  console.log('=====================================');

  console.log('\n🚨 Console Errors:');
  if (results.consoleErrors.length === 0) {
    console.log('  ✅ No console errors detected');
  } else {
    results.consoleErrors.forEach((error, i) => {
      console.log(`  ${i + 1}. ${error}`);
    });
  }

  console.log('\n💥 JavaScript Errors:');
  if (results.jsErrors.length === 0) {
    console.log('  ✅ No JavaScript errors detected');
  } else {
    results.jsErrors.forEach((error, i) => {
      console.log(`  ${i + 1}. ${error}`);
    });
  }

  console.log('\n🌐 API Requests:');
  if (results.networkRequests.length === 0) {
    console.log('  ⚠️ No API requests detected');
  } else {
    results.networkRequests.forEach((req, i) => {
      console.log(`  ${i + 1}. ${req.method} ${req.url} - ${req.status} ${req.statusText}`);
      if (req.error) {
        console.log(`     Error: ${req.error}`);
      }
      if (req.payload) {
        console.log(`     Payload:`, JSON.stringify(req.payload, null, 2));
      }
      if (req.response && req.status >= 400) {
        console.log(`     Response:`, JSON.stringify(req.response, null, 2));
      }
    });
  }

  console.log('\n🔐 Authentication Issues:');
  if (results.authErrors.length === 0) {
    console.log('  ✅ No authentication errors detected');
  } else {
    results.authErrors.forEach((error, i) => {
      console.log(`  ${i + 1}. ${error}`);
    });
  }

  console.log('\n❌ Final Error:');
  if (results.finalError) {
    console.log(`  ${results.finalError}`);
  } else {
    console.log('  ✅ No final error message detected');
  }

  console.log('\n🔍 DIAGNOSIS:');
  if (results.apiErrors.length > 0) {
    console.log('  - API connectivity issues detected');
    console.log('  - Backend may not be running or accessible');
    console.log('  - Check if backend server is started on localhost:8000');
  }

  if (results.authErrors.length > 0) {
    console.log('  - Authentication issues detected');
    console.log('  - Clerk configuration may be incorrect');
    console.log('  - Check CLERK_PUBLISHABLE_KEY and other Clerk settings');
  }

  if (results.networkRequests.length === 0) {
    console.log('  - No API requests made, possible frontend issue');
    console.log('  - Check if API client is properly configured');
  }

  console.log('\n=====================================');
}