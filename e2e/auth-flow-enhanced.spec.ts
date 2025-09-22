/**
 * Enhanced Authentication Flow Tests
 *
 * Demonstrates the use of enhanced waiting strategies for more reliable
 * authentication flow testing with better handling of dynamic content.
 */

import { test, expect } from '@playwright/test';
import {
  PlaywrightContentWaiter,
  PlaywrightInteractionWaiter,
  FlakeResistantRunner,
  playwrightWaitStrategies
} from './utils/enhanced-playwright-waits';
import {
  setupMockAuth,
  goToSignInPage,
  signInWithEmail,
  testUsers,
  setupTestEnvironment,
  enableTestMode
} from './auth-utils';

test.describe('Enhanced Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);
  });

  test('should handle sign-in with enhanced waiting strategies', async ({ page }) => {
    // Navigate to sign-in page with smart waiting
    await FlakeResistantRunner.runWithRetry(
      async () => {
        await goToSignInPage(page);
        
        // Wait for page to be fully ready for interaction
        await playwrightWaitStrategies.forPageReady(page, {
          timeout: 10000,
          waitForImages: false,
          waitForFonts: true
        });
      },
      {
        maxRetries: 3,
        retryCondition: FlakeResistantRunner.retryConditions.allCommonFlakes
      }
    );

    // Wait for form to be ready for interaction
    const emailInput = await PlaywrightInteractionWaiter.waitForInteractionReady(
      page,
      'input[type="email"]',
      {
        timeout: 5000,
        ensureVisible: true,
        ensureEnabled: true,
        ensureStable: true
      }
    );

    const passwordInput = await PlaywrightInteractionWaiter.waitForInteractionReady(
      page,
      'input[type="password"]',
      {
        timeout: 5000,
        ensureVisible: true,
        ensureEnabled: true
      }
    );

    // Fill credentials with safe interaction methods
    await PlaywrightInteractionWaiter.safeFill(
      page,
      'input[type="email"]',
      testUsers.validUser.email,
      {
        clearFirst: true,
        validateInput: true,
        timeout: 3000
      }
    );

    await PlaywrightInteractionWaiter.safeFill(
      page,
      'input[type="password"]',
      testUsers.validUser.password,
      {
        clearFirst: true,
        validateInput: false, // Password validation disabled for security
        timeout: 3000
      }
    );

    // Submit form with enhanced form submission handling
    const submitResult = await playwrightWaitStrategies.forFormSubmission(
      page,
      async () => {
        await PlaywrightInteractionWaiter.safeClick(
          page,
          'button[type="submit"], button:has-text("Sign In")',
          {
            timeout: 3000,
            retries: 2
          }
        );
      },
      {
        timeout: 10000
      }
    );

    expect(submitResult.success).toBe(true);

    // Wait for authentication state change and navigation
    await playwrightWaitStrategies.forRouteChange(
      page,
      /dashboard|profile|home/,
      {
        timeout: 8000,
        waitForImages: false,
        networkIdleTimeout: 5000
      }
    );

    // Verify user is authenticated with enhanced content waiting
    await PlaywrightContentWaiter.waitForDynamicContent(page, {
      timeout: 8000,
      contentSelectors: [
        '[data-testid*="user"]',
        '[data-testid*="profile"]',
        '.user-info',
        '.authenticated'
      ],
      minContentElements: 1,
      retries: 2
    });

    // Verify user email is displayed
    const userEmailElement = page.locator(`text=${testUsers.validUser.email}`);
    await expect(userEmailElement).toBeVisible({ timeout: 5000 });
  });

  test('should handle authentication errors with retry logic', async ({ page }) => {
    await goToSignInPage(page);

    // Wait for page readiness
    await playwrightWaitStrategies.forPageReady(page);

    // Attempt sign-in with invalid credentials using retry logic
    const authResult = await FlakeResistantRunner.runWithRetry(
      async () => {
        // Fill invalid credentials
        await PlaywrightInteractionWaiter.safeFill(
          page,
          'input[type="email"]',
          testUsers.invalidUser.email
        );

        await PlaywrightInteractionWaiter.safeFill(
          page,
          'input[type="password"]',
          testUsers.invalidUser.password
        );

        // Submit and wait for response
        return await playwrightWaitStrategies.forFormSubmission(
          page,
          async () => {
            await PlaywrightInteractionWaiter.safeClick(
              page,
              'button[type="submit"], button:has-text("Sign In")'
            );
          }
        );
      },
      {
        maxRetries: 2,
        retryCondition: (error) => {
          // Only retry on network/loading errors, not auth errors
          return FlakeResistantRunner.retryConditions.networkErrors(error) ||
                 FlakeResistantRunner.retryConditions.loadingErrors(error);
        }
      }
    );

    // Should get error response
    expect(authResult.success).toBe(false);
    expect(authResult.message).toContain('Invalid');

    // Wait for error message to be stable and visible
    const errorElement = await PlaywrightInteractionWaiter.waitForInteractionReady(
      page,
      '[role="alert"], .error, [data-testid*="error"]',
      {
        timeout: 5000,
        ensureVisible: true,
        ensureStable: true
      }
    );

    await expect(errorElement).toContainText(/invalid|error/i);
  });

  test('should handle slow network conditions', async ({ page }) => {
    // Simulate slow network
    await page.route('**/*', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1s delay
      await route.continue();
    });

    await goToSignInPage(page);

    // Use extended timeouts for slow network conditions
    await PlaywrightContentWaiter.waitForDynamicContent(page, {
      timeout: 15000, // Extended timeout for slow network
      networkIdleTimeout: 8000,
      retries: 3,
      retryDelay: 2000
    });

    // Form should still be interactive despite slow network
    const emailInput = await PlaywrightInteractionWaiter.waitForInteractionReady(
      page,
      'input[type="email"]',
      {
        timeout: 10000,
        retries: 3
      }
    );

    expect(emailInput).toBeTruthy();
  });

  test('should handle modal authentication flows', async ({ page }) => {
    // Navigate to a page that might show auth modal
    await page.goto('/protected-route');

    // Wait for auth modal to appear
    const modal = await playwrightWaitStrategies.forModalReady(
      page,
      '[role="dialog"], .modal, [data-testid*="auth-modal"]',
      {
        timeout: 8000,
        ensureStable: true
      }
    );

    // Fill auth form within modal
    await PlaywrightInteractionWaiter.safeFill(
      page,
      'input[type="email"]',
      testUsers.validUser.email
    );

    await PlaywrightInteractionWaiter.safeFill(
      page,
      'input[type="password"]',
      testUsers.validUser.password
    );

    // Submit modal form
    await playwrightWaitStrategies.forFormSubmission(
      page,
      async () => {
        await PlaywrightInteractionWaiter.safeClick(
          page,
          'button[type="submit"]'
        );
      }
    );

    // Wait for modal to close and content to load
    await PlaywrightContentWaiter.waitForDynamicContent(page, {
      timeout: 10000,
      loadingSelectors: [
        '.modal',
        '[role="dialog"]',
        '[data-testid*="loading"]'
      ],
      retries: 2
    });

    // Verify we can access protected content
    await expect(page.locator('[data-testid*="protected"]')).toBeVisible({
      timeout: 5000
    });
  });

  test('should handle API-driven authentication state', async ({ page }) => {
    await goToSignInPage(page);

    // Wait for page and API readiness
    await playwrightWaitStrategies.forApiOperation(
      page,
      async () => {
        await playwrightWaitStrategies.forPageReady(page);
      },
      {
        expectedResponses: ['/api/auth/status', '/api/config'],
        timeout: 10000
      }
    );

    // Perform authentication
    await PlaywrightInteractionWaiter.safeFill(
      page,
      'input[type="email"]',
      testUsers.validUser.email
    );

    await PlaywrightInteractionWaiter.safeFill(
      page,
      'input[type="password"]',
      testUsers.validUser.password
    );

    // Submit with API response waiting
    await playwrightWaitStrategies.forApiOperation(
      page,
      async () => {
        await PlaywrightInteractionWaiter.safeClick(
          page,
          'button[type="submit"]'
        );
      },
      {
        expectedResponses: ['/api/auth/login'],
        timeout: 8000
      }
    );

    // Wait for authentication state to propagate
    await PlaywrightContentWaiter.waitForDynamicContent(page, {
      timeout: 8000,
      contentSelectors: ['[data-authenticated="true"]'],
      retries: 3
    });

    expect(page.url()).toMatch(/dashboard|profile|home/);
  });

  test('should handle multiple authentication attempts', async ({ page }) => {
    await goToSignInPage(page);
    await playwrightWaitStrategies.forPageReady(page);

    // Simulate multiple failed attempts followed by success
    const attempts = [
      { email: 'wrong@email.com', password: 'wrongpass', shouldSucceed: false },
      { email: testUsers.invalidUser.email, password: testUsers.invalidUser.password, shouldSucceed: false },
      { email: testUsers.validUser.email, password: testUsers.validUser.password, shouldSucceed: true }
    ];

    for (const [index, attempt] of attempts.entries()) {
      // Clear previous values
      await page.fill('input[type="email"]', '');
      await page.fill('input[type="password"]', '');

      // Fill credentials
      await PlaywrightInteractionWaiter.safeFill(
        page,
        'input[type="email"]',
        attempt.email
      );

      await PlaywrightInteractionWaiter.safeFill(
        page,
        'input[type="password"]',
        attempt.password
      );

      // Submit with retry logic for flaky network
      const result = await FlakeResistantRunner.runWithRetry(
        async () => {
          return await playwrightWaitStrategies.forFormSubmission(
            page,
            async () => {
              await PlaywrightInteractionWaiter.safeClick(
                page,
                'button[type="submit"]'
              );
            }
          );
        },
        {
          maxRetries: 2,
          retryCondition: FlakeResistantRunner.retryConditions.allCommonFlakes
        }
      );

      if (attempt.shouldSucceed) {
        expect(result.success).toBe(true);
        
        // Wait for successful navigation
        await playwrightWaitStrategies.forRouteChange(
          page,
          /dashboard|profile|home/
        );
        
        break; // Success, exit loop
      } else {
        expect(result.success).toBe(false);
        
        // Wait for error message to be stable
        await PlaywrightInteractionWaiter.waitForInteractionReady(
          page,
          '[role="alert"], .error',
          { timeout: 3000 }
        );
      }
    }
  });
});