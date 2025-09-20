/**
 * Protected Route Tests
 *
 * Tests authentication-based route protection, redirects, and auth state management
 */

import { test, expect } from '@playwright/test';
import {
  setupMockAuth,
  goToSignInPage,
  signInWithEmail,
  signOut,
  waitForAuthState,
  expectUserAuthenticated,
  expectUserNotAuthenticated,
  testUsers,
  setupTestEnvironment,
  enableTestMode,
  disableTestMode
} from './auth-utils';

test.describe('Protected Routes', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
  });

  test.describe('Authentication Required Routes', () => {
    test('should redirect unauthenticated users to sign-in', async ({ page }) => {
      await disableTestMode(page);

      // Try to access protected route without authentication
      await page.goto('/dashboard');

      // Should redirect to sign-in page
      await expect(page).toHaveURL(/\/auth\/sign-in/);
      await expectUserNotAuthenticated(page);
    });

    test('should allow authenticated users to access protected routes', async ({ page }) => {
      await enableTestMode(page);

      // Sign in first
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Now access protected route
      await page.goto('/dashboard');

      // Should be able to access the route
      await expectUserAuthenticated(page);
      await expect(page).toHaveURL('/dashboard');
    });

    test('should preserve intended destination after sign-in', async ({ page }) => {
      await disableTestMode(page);

      // Try to access specific protected route
      await page.goto('/dashboard?section=profile');

      // Should redirect to sign-in
      await expect(page).toHaveURL(/\/auth\/sign-in/);

      // Enable test mode and sign in
      await enableTestMode(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Should redirect back to intended destination
      // Note: This behavior depends on the implementation of the redirect logic
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/dashboard/);
    });

    test('should handle deep-linked protected routes', async ({ page }) => {
      await disableTestMode(page);

      // Try to access deeply nested protected route
      await page.goto('/user/settings/profile');

      // Should redirect to sign-in
      await expect(page).toHaveURL(/\/auth\/sign-in/);
    });
  });

  test.describe('Route Access Control', () => {
    test('should allow access to public routes without authentication', async ({ page }) => {
      await disableTestMode(page);

      // Access public routes
      const publicRoutes = ['/', '/auth/sign-in', '/about', '/contact'];

      for (const route of publicRoutes) {
        await page.goto(route);

        // Should not redirect to sign-in (except for sign-in route itself)
        if (route !== '/auth/sign-in') {
          await expect(page).not.toHaveURL(/\/auth\/sign-in/);
        }
      }
    });

    test('should allow unauthenticated access to onboarding routes (test bypass)', async ({ page }) => {
      await disableTestMode(page);

      // The ProtectedRoute component has special handling for onboarding routes
      await page.goto('/onboarding');

      // Should allow access even when not authenticated
      await expect(page).not.toHaveURL(/\/auth\/sign-in/);
    });

    test('should respect test mode bypass', async ({ page }) => {
      await enableTestMode(page);

      // Access protected route with test mode enabled
      await page.goto('/dashboard');

      // Should not redirect because test mode is enabled
      await expect(page).not.toHaveURL(/\/auth\/sign-in/);
    });

    test('should respect URL parameter test bypass', async ({ page }) => {
      await disableTestMode(page);

      // Access protected route with test=true parameter
      await page.goto('/dashboard?test=true');

      // Should not redirect because test parameter is present
      await expect(page).not.toHaveURL(/\/auth\/sign-in/);
    });
  });

  test.describe('Authentication State Changes', () => {
    test('should redirect to sign-in when user signs out', async ({ page }) => {
      await enableTestMode(page);

      // Sign in and navigate to protected route
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);
      await page.goto('/dashboard');

      // Disable test mode to enforce authentication
      await disableTestMode(page);

      // Sign out
      await signOut(page);

      // Should redirect to sign-in page
      await expect(page).toHaveURL(/\/auth\/sign-in/);
      await expectUserNotAuthenticated(page);
    });

    test('should handle authentication state during page load', async ({ page }) => {
      await enableTestMode(page);

      // Sign in
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate to protected route
      await page.goto('/dashboard');

      // Disable test mode after navigation
      await disableTestMode(page);

      // Reload page to test authentication state persistence
      await page.reload();

      // Should still be authenticated and not redirect
      await expectUserAuthenticated(page);
      await expect(page).toHaveURL('/dashboard');
    });
  });

  test.describe('Loading States', () => {
    test('should show loading state while checking authentication', async ({ page }) => {
      await disableTestMode(page);

      // Mock delayed auth state check
      await page.addInitScript(() => {
        const originalOnAuthStateChanged = (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged;
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged = (callback: any) => {
          // Delay the auth state callback
          setTimeout(() => {
            callback(null); // Not authenticated
          }, 1000);
          return () => {};
        };
      });

      await page.goto('/dashboard');

      // Should show loading state initially
      await expect(page.getByText(/loading/i)).toBeVisible();
      await expect(page.locator('.animate-spin')).toBeVisible();

      // Eventually should redirect to sign-in
      await expect(page).toHaveURL(/\/auth\/sign-in/, { timeout: 15000 });
    });

    test('should not show loading flash when already authenticated', async ({ page }) => {
      await enableTestMode(page);

      // Sign in first
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate to protected route
      await page.goto('/dashboard');

      // Should immediately show content without loading flash
      await expectUserAuthenticated(page);
      await expect(page.getByText(/loading/i)).not.toBeVisible();
    });
  });

  test.describe('Route Transitions', () => {
    test('should maintain authentication across route changes', async ({ page }) => {
      await enableTestMode(page);

      // Sign in
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate between different protected routes
      const protectedRoutes = ['/dashboard', '/profile', '/settings'];

      for (const route of protectedRoutes) {
        await page.goto(route);
        await expectUserAuthenticated(page);

        // Should not show loading or redirect
        await expect(page.getByText(/loading/i)).not.toBeVisible();
        await expect(page).not.toHaveURL(/\/auth\/sign-in/);
      }
    });

    test('should handle browser back/forward navigation', async ({ page }) => {
      await enableTestMode(page);

      // Sign in
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate through several routes
      await page.goto('/dashboard');
      await page.goto('/profile');
      await page.goto('/settings');

      // Use browser back button
      await page.goBack();
      await expectUserAuthenticated(page);
      await expect(page).toHaveURL('/profile');

      await page.goBack();
      await expectUserAuthenticated(page);
      await expect(page).toHaveURL('/dashboard');

      // Use browser forward button
      await page.goForward();
      await expectUserAuthenticated(page);
      await expect(page).toHaveURL('/profile');
    });
  });

  test.describe('Multiple Tab Behavior', () => {
    test('should sync authentication state across tabs', async ({ browser }) => {
      const context = await browser.newContext();
      const page1 = await context.newPage();
      const page2 = await context.newPage();

      // Setup both pages
      await setupTestEnvironment(page1);
      await setupMockAuth(page1);
      await enableTestMode(page1);

      await setupTestEnvironment(page2);
      await setupMockAuth(page2);
      await enableTestMode(page2);

      // Sign in on first tab
      await goToSignInPage(page1);
      await signInWithEmail(page1, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page1, true);

      // Navigate to protected route on second tab
      await page2.goto('/dashboard');

      // Second tab should also be authenticated
      await expectUserAuthenticated(page2);

      // Sign out on first tab
      await signOut(page1);

      // Second tab should also be signed out
      await page2.reload();
      await expectUserNotAuthenticated(page2);

      await context.close();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle authentication errors gracefully', async ({ page }) => {
      await disableTestMode(page);

      // Mock authentication error
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged = (callback: any) => {
          // Simulate auth error
          setTimeout(() => {
            callback(null);
          }, 100);
          return () => {};
        };
      });

      await page.goto('/dashboard');

      // Should redirect to sign-in despite error
      await expect(page).toHaveURL(/\/auth\/sign-in/);
    });

    test('should handle network errors during auth check', async ({ page }) => {
      await disableTestMode(page);

      // Mock network failure
      await page.route('**/*', route => {
        if (route.request().url().includes('firebase')) {
          route.abort('failed');
        } else {
          route.continue();
        }
      });

      await page.goto('/dashboard');

      // Should still redirect to sign-in as fallback
      await expect(page).toHaveURL(/\/auth\/sign-in/);
    });
  });
});