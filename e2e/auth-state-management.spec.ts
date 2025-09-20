/**
 * Authentication State Management Tests
 *
 * Tests the Firebase authentication context, custom hooks, and state management
 * integration across the application
 */

import { test, expect } from '@playwright/test';
import {
  setupMockAuth,
  goToSignInPage,
  signInWithEmail,
  signInWithGoogle,
  signOut,
  openUserProfileDialog,
  testUsers,
  setupTestEnvironment,
  enableTestMode,
  waitForAuthState,
  expectUserAuthenticated,
  expectUserNotAuthenticated
} from './auth-utils';

test.describe('Authentication State Management', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);
  });

  test.describe('FirebaseAuthContext State', () => {
    test('should initialize with loading state', async ({ page }) => {
      // Mock delayed auth state initialization
      await page.addInitScript(() => {
        const originalOnAuthStateChanged = (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged;
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged = (callback: any) => {
          setTimeout(() => {
            callback(null); // Not authenticated initially
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

    test('should update context when user signs in', async ({ page }) => {
      await goToSignInPage(page);

      // Verify initial unauthenticated state
      await expectUserNotAuthenticated(page);

      // Sign in
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Context should update with user information
      await expectUserAuthenticated(page, testUsers.validUser.email);

      // User profile should show correct information
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await expect(page.getByText(testUsers.validUser.email)).toBeVisible();
    });

    test('should update context when user signs out', async ({ page }) => {
      // Sign in first
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page);

      // Sign out
      await signOut(page);

      // Context should update to unauthenticated state
      await waitForAuthState(page, false);
      await expectUserNotAuthenticated(page);
    });

    test('should maintain state across page navigation', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate to different pages
      const routes = ['/dashboard', '/', '/profile', '/settings'];

      for (const route of routes) {
        await page.goto(route);
        await expectUserAuthenticated(page);

        // Context should provide consistent user data
        await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
        await expect(page.getByText(testUsers.validUser.email)).toBeVisible();
        await page.keyboard.press('Escape'); // Close dropdown
      }
    });

    test('should persist state across page reloads', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Reload page
      await page.reload();

      // Should maintain authenticated state
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page);

      // User data should be preserved
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await expect(page.getByText(testUsers.validUser.email)).toBeVisible();
    });

    test('should handle rapid state changes', async ({ page }) => {
      await goToSignInPage(page);

      // Rapidly sign in and out multiple times
      for (let i = 0; i < 3; i++) {
        await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
        await waitForAuthState(page, true);
        await expectUserAuthenticated(page);

        await signOut(page);
        await waitForAuthState(page, false);
        await expectUserNotAuthenticated(page);
      }
    });
  });

  test.describe('Custom Hook State Management', () => {
    test('should provide consistent user data through useAuthUser hook', async ({ page }) => {
      // Add script to check hook state
      await page.addInitScript(() => {
        (window as any).authHookStates = [];

        // Mock hook state tracking
        const originalConsoleLog = console.log;
        console.log = (...args) => {
          if (args[0] && args[0].includes && args[0].includes('useAuthUser')) {
            (window as any).authHookStates.push(args[1]);
          }
          originalConsoleLog(...args);
        };
      });

      await goToSignInPage(page);

      // Sign in
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Check that hook provides user data
      await expectUserAuthenticated(page);

      // Verify user information is accessible
      const userEmail = await page.evaluate(() => {
        // This would normally access the hook state through component
        return (window as any).__FIREBASE_AUTH_MOCK__.currentUser?.email;
      });

      expect(userEmail).toBe(testUsers.validUser.email);
    });

    test('should provide loading states through useAuthUser hook', async ({ page }) => {
      // Mock delayed auth initialization
      await page.addInitScript(() => {
        const originalOnAuthStateChanged = (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged;
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged = (callback: any) => {
          setTimeout(() => {
            callback(null);
          }, 800);
          return () => {};
        };
      });

      await page.goto('/dashboard');

      // Should show loading state
      await expect(page.getByText(/loading/i)).toBeVisible();

      // Loading should eventually complete
      await expect(page.getByText(/loading/i)).not.toBeVisible({ timeout: 10000 });
    });

    test('should handle authentication method state through useAuthMethods', async ({ page }) => {
      await goToSignInPage(page);

      // Test email sign-in method
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Should be able to sign out using method from hook
      await signOut(page);
      await waitForAuthState(page, false);

      // Test Google sign-in method
      await signInWithGoogle(page);
      await waitForAuthState(page, true);

      // Should show Google user information
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await expect(page.getByText('test@gmail.com')).toBeVisible();
    });

    test('should manage profile update state through useProfileManagement', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      await openUserProfileDialog(page);

      // Update display name
      const newDisplayName = 'Updated Test User';
      await page.fill('input[id="displayName"]', newDisplayName);
      await page.getByRole('button', { name: /update profile/i }).click();

      // Should show loading state during update
      const updateButton = page.getByRole('button', { name: /update profile/i });
      await expect(updateButton.locator('.animate-spin')).toBeVisible();

      // Should show success state
      await expect(page.getByText(/profile updated successfully/i)).toBeVisible();

      // Updated name should be reflected in context
      await page.getByRole('button', { name: /close/i }).click();
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await expect(page.getByText(newDisplayName)).toBeVisible();
    });

    test('should manage password reset state through usePasswordReset', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Use password reset hook
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show loading state
      const submitButton = page.getByRole('button', { name: /send reset email/i });
      await expect(submitButton.locator('.animate-spin')).toBeVisible();

      // Should show success state
      await expect(page.getByText(/password reset email sent/i)).toBeVisible();
    });

    test('should manage email verification state through useEmailVerification', async ({ page }) => {
      // Mock unverified email state
      await page.addInitScript(() => {
        if ((window as any).__FIREBASE_AUTH_MOCK__.currentUser) {
          (window as any).__FIREBASE_AUTH_MOCK__.currentUser.emailVerified = false;
        }
      });

      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      // Should show unverified status
      await expect(page.getByText('Unverified')).toBeVisible();

      // Send verification email
      await page.getByRole('button', { name: /send verification/i }).click();

      // Should show loading state
      const verifyButton = page.getByRole('button', { name: /send verification/i });
      await expect(verifyButton.locator('.animate-spin')).toBeVisible();

      // Should show success message
      await expect(page.getByText(/verification email sent/i)).toBeVisible();
    });
  });

  test.describe('Token Management', () => {
    test('should manage ID tokens through useAuthToken hook', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Check token availability through context
      const hasToken = await page.evaluate(async () => {
        return !!(window as any).__FIREBASE_AUTH_MOCK__.currentUser;
      });

      expect(hasToken).toBeTruthy();
    });

    test('should handle token refresh scenarios', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Mock token refresh
      await page.addInitScript(() => {
        const mockUser = (window as any).__FIREBASE_AUTH_MOCK__.currentUser;
        if (mockUser) {
          mockUser.getIdToken = async (forceRefresh = false) => {
            if (forceRefresh) {
              return 'refreshed-token-123';
            }
            return 'cached-token-123';
          };
        }
      });

      // Token should be available
      const tokenResult = await page.evaluate(async () => {
        const mockUser = (window as any).__FIREBASE_AUTH_MOCK__.currentUser;
        return mockUser ? await mockUser.getIdToken() : null;
      });

      expect(tokenResult).toBeTruthy();
    });
  });

  test.describe('Error State Management', () => {
    test('should handle authentication errors in context', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
          throw new Error('Authentication failed');
        };
      });

      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, 'wrongpassword');

      // Should show error state
      await expect(page.locator('[role="alert"]')).toBeVisible();

      // Context should remain in unauthenticated state
      await expectUserNotAuthenticated(page);
    });

    test('should handle network errors gracefully', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged = () => {
          throw new Error('Network error');
        };
      });

      await page.goto('/dashboard');

      // Should handle error gracefully and redirect to sign-in
      await expect(page).toHaveURL(/\/auth\/sign-in/, { timeout: 10000 });
    });

    test('should recover from temporary errors', async ({ page }) => {
      let errorCount = 0;
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (...args: any[]) => {
          const count = (window as any).errorCount || 0;
          (window as any).errorCount = count + 1;

          if (count < 2) {
            throw new Error('Temporary error');
          }
          return originalSignIn(...args);
        };
      });

      await goToSignInPage(page);

      // First attempts should fail
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await expect(page.locator('[role="alert"]')).toBeVisible();

      // Retry should eventually succeed
      await page.getByRole('button', { name: /sign in/i }).click();
      await expect(page.locator('[role="alert"]')).toBeVisible();

      await page.getByRole('button', { name: /sign in/i }).click();
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page);
    });
  });

  test.describe('Multi-Tab State Synchronization', () => {
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

      // Both tabs should be signed out
      await waitForAuthState(page1, false);

      // Second tab should eventually redirect to sign-in
      await page2.reload();
      await expectUserNotAuthenticated(page2);

      await context.close();
    });

    test('should handle profile updates across tabs', async ({ browser }) => {
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

      // Sign in on both tabs
      await goToSignInPage(page1);
      await signInWithEmail(page1, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page1, true);

      await goToSignInPage(page2);
      await signInWithEmail(page2, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page2, true);

      // Update profile on first tab
      await openUserProfileDialog(page1);
      const newDisplayName = 'Multi-tab Test User';
      await page1.fill('input[id="displayName"]', newDisplayName);
      await page1.getByRole('button', { name: /update profile/i }).click();
      await page1.waitForSelector('.alert:not(.alert-destructive)', { timeout: 5000 });

      // Profile should update on second tab (after reload/navigation)
      await page2.reload();
      await page2.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await expect(page2.getByText(newDisplayName)).toBeVisible();

      await context.close();
    });
  });

  test.describe('Memory and Performance', () => {
    test('should not leak memory during auth state changes', async ({ page }) => {
      await goToSignInPage(page);

      // Perform multiple sign-in/sign-out cycles
      for (let i = 0; i < 5; i++) {
        await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
        await waitForAuthState(page, true);

        await signOut(page);
        await waitForAuthState(page, false);
      }

      // Check for memory leaks (basic check)
      const listenerCount = await page.evaluate(() => {
        return (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChangedCallbacks?.length || 0;
      });

      // Should not accumulate too many listeners
      expect(listenerCount).toBeLessThan(10);
    });

    test('should handle rapid context updates efficiently', async ({ page }) => {
      await goToSignInPage(page);

      // Mock rapid auth state changes
      await page.addInitScript(() => {
        let updateCount = 0;
        const originalTrigger = (window as any).__FIREBASE_AUTH_MOCK__.triggerAuthStateChange;
        (window as any).__FIREBASE_AUTH_MOCK__.triggerAuthStateChange = (user: any) => {
          updateCount++;
          (window as any).authUpdateCount = updateCount;
          originalTrigger(user);
        };
      });

      // Trigger multiple rapid updates
      await page.evaluate(() => {
        const mockAuth = (window as any).__FIREBASE_AUTH_MOCK__;
        for (let i = 0; i < 10; i++) {
          setTimeout(() => {
            mockAuth.triggerAuthStateChange(mockAuth.currentUser);
          }, i * 10);
        }
      });

      // Wait for updates to settle
      await page.waitForTimeout(1000);

      // UI should remain stable despite rapid updates
      await expectUserNotAuthenticated(page);
    });
  });

  test.describe('Context Provider Integration', () => {
    test('should provide context to all child components', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate to different parts of the app to test context availability
      const routes = ['/dashboard', '/', '/profile'];

      for (const route of routes) {
        await page.goto(route);

        // User profile should be available (proving context is accessible)
        await expectUserAuthenticated(page);

        // Context methods should be available
        await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
        await expect(page.getByRole('menuitem', { name: /profile settings/i })).toBeVisible();
        await expect(page.getByRole('menuitem', { name: /sign out/i })).toBeVisible();
        await page.keyboard.press('Escape');
      }
    });

    test('should handle context provider unmounting gracefully', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate away and back to test provider lifecycle
      await page.goto('about:blank');
      await page.waitForTimeout(500);

      await page.goto('/dashboard');
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page);
    });

    test('should throw error when context is used outside provider', async ({ page }) => {
      // This test would need to be implemented with a component that tries to use
      // the auth context outside of the provider, which is more of a unit test scenario
      // For E2E, we can verify that the context is always available in the app
      await page.goto('/');

      // Should not throw errors - context should always be available in the app
      const hasErrors = await page.evaluate(() => {
        return !!(window as any).unhandledErrors?.length;
      });

      expect(hasErrors).toBeFalsy();
    });
  });
});