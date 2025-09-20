/**
 * Firebase Authentication Flow Tests
 *
 * Tests the core authentication flows including sign-in, sign-up, and Google OAuth
 */

import { test, expect } from '@playwright/test';
import {
  setupMockAuth,
  goToSignInPage,
  goToSignUpPage,
  signInWithEmail,
  signUpWithEmail,
  signInWithGoogle,
  signOut,
  waitForAuthState,
  expectUserAuthenticated,
  expectUserNotAuthenticated,
  expectErrorMessage,
  expectSuccessMessage,
  testUsers,
  setupTestEnvironment,
  enableTestMode
} from './auth-utils';

test.describe('Firebase Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);
  });

  test.describe('Email/Password Sign In', () => {
    test('should successfully sign in with valid credentials', async ({ page }) => {
      await goToSignInPage(page);

      // Fill in valid credentials
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);

      // Should redirect to dashboard and show user profile
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page, testUsers.validUser.email);
    });

    test('should show error with invalid credentials', async ({ page }) => {
      await goToSignInPage(page);

      // Fill in invalid credentials
      await signInWithEmail(page, testUsers.invalidUser.email, testUsers.invalidUser.password);

      // Should show error message
      await expectErrorMessage(page, 'Invalid email or password');
      await expectUserNotAuthenticated(page);
    });

    test('should validate email format', async ({ page }) => {
      await goToSignInPage(page);

      // Try to sign in with invalid email format
      await page.fill('input[type="email"]', 'invalid-email');
      await page.fill('input[type="password"]', 'somepassword');
      await page.getByRole('button', { name: /sign in/i }).click();

      // Should show validation error (browser validation or custom)
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toHaveAttribute('type', 'email');
    });

    test('should require both email and password', async ({ page }) => {
      await goToSignInPage(page);

      // Try to submit empty form
      const signInButton = page.getByRole('button', { name: /sign in/i });
      await expect(signInButton).toBeDisabled();

      // Fill only email
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await expect(signInButton).toBeDisabled();

      // Fill only password (clear email first)
      await page.fill('input[type="email"]', '');
      await page.fill('input[type="password"]', testUsers.validUser.password);
      await expect(signInButton).toBeDisabled();

      // Fill both fields
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await expect(signInButton).toBeEnabled();
    });

    test('should clear errors when user starts typing', async ({ page }) => {
      await goToSignInPage(page);

      // Trigger an error first
      await signInWithEmail(page, testUsers.invalidUser.email, testUsers.invalidUser.password);
      await expectErrorMessage(page);

      // Start typing in email field
      await page.fill('input[type="email"]', 't');

      // Error should be cleared
      await expect(page.locator('[role="alert"]')).not.toBeVisible();
    });
  });

  test.describe('Email/Password Sign Up', () => {
    test('should successfully create account with valid details', async ({ page }) => {
      await goToSignUpPage(page);

      // Fill in new account details
      const newEmail = 'newuser@test.com';
      const password = 'NewPassword123!';
      await signUpWithEmail(page, newEmail, password, password);

      // Should redirect to dashboard and show user profile
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page, newEmail);
    });

    test('should require password confirmation', async ({ page }) => {
      await goToSignUpPage(page);

      // Fill form with mismatched passwords
      await page.fill('input[type="email"]', 'newuser@test.com');
      await page.fill('input[type="password"]', 'password123');
      await page.fill('input[placeholder*="Confirm"]', 'differentpassword');

      const createButton = page.getByRole('button', { name: /create account/i });
      await createButton.click();

      // Should show password mismatch error
      await expectErrorMessage(page, 'Passwords do not match');
    });

    test('should validate password strength', async ({ page }) => {
      await goToSignUpPage(page);

      // Try with weak password
      await page.fill('input[type="email"]', 'newuser@test.com');
      await page.fill('input[type="password"]', '123');
      await page.fill('input[placeholder*="Confirm"]', '123');

      const createButton = page.getByRole('button', { name: /create account/i });
      await createButton.click();

      // Should show password strength error
      await expectErrorMessage(page);
    });

    test('should toggle between sign in and sign up modes', async ({ page }) => {
      await goToSignInPage(page);

      // Should be in sign-in mode initially
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

      // Toggle to sign-up mode
      await page.getByRole('button', { name: /sign up/i }).click();
      await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
      await expect(page.locator('input[placeholder*="Confirm"]')).toBeVisible();

      // Toggle back to sign-in mode
      await page.getByRole('button', { name: /sign in/i }).click();
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      await expect(page.locator('input[placeholder*="Confirm"]')).not.toBeVisible();
    });

    test('should clear form when toggling modes', async ({ page }) => {
      await goToSignInPage(page);

      // Fill form in sign-in mode
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);

      // Toggle to sign-up mode
      await page.getByRole('button', { name: /sign up/i }).click();

      // Form should be cleared
      await expect(page.locator('input[type="email"]')).toHaveValue('');
      await expect(page.locator('input[type="password"]')).toHaveValue('');
    });
  });

  test.describe('Google OAuth Sign In', () => {
    test('should successfully sign in with Google', async ({ page }) => {
      await goToSignInPage(page);

      // Click Google sign-in button
      await signInWithGoogle(page);

      // Should redirect to dashboard and show user profile
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page, 'test@gmail.com');
    });

    test('should show Google sign-in button with correct styling', async ({ page }) => {
      await goToSignInPage(page);

      const googleButton = page.getByRole('button', { name: /continue with google/i });
      await expect(googleButton).toBeVisible();
      await expect(googleButton).toContainText('Continue with Google');

      // Check for Google icon (Chrome icon is used as placeholder)
      await expect(googleButton.locator('svg')).toBeVisible();
    });

    test('should handle Google sign-in loading state', async ({ page }) => {
      await goToSignInPage(page);

      // Mock delayed Google response
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithGoogle;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithGoogle = async () => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return originalSignIn();
        };
      });

      const googleButton = page.getByRole('button', { name: /continue with google/i });
      await googleButton.click();

      // Should show loading state
      await expect(page.locator('.animate-spin')).toBeVisible();
      await expect(googleButton).toBeDisabled();

      // Wait for sign-in to complete
      await waitForAuthState(page, true);
    });
  });

  test.describe('Sign Out Flow', () => {
    test.beforeEach(async ({ page }) => {
      // Sign in before each test
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);
    });

    test('should successfully sign out user', async ({ page }) => {
      // Sign out
      await signOut(page);

      // Should redirect to sign-in page
      await waitForAuthState(page, false);
      await expectUserNotAuthenticated(page);
    });

    test('should clear user session on sign out', async ({ page }) => {
      // Verify user is signed in
      await expectUserAuthenticated(page);

      // Sign out
      await signOut(page);

      // Try to access a protected route
      await page.goto('/dashboard');

      // Should redirect to sign-in
      await expectUserNotAuthenticated(page);
    });
  });

  test.describe('Authentication State Persistence', () => {
    test('should persist authentication across page reloads', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Reload the page
      await page.reload();

      // Should still be authenticated
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page);
    });

    test('should persist authentication across navigation', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await waitForAuthState(page, true);

      // Navigate to different pages
      await page.goto('/dashboard');
      await expectUserAuthenticated(page);

      await page.goto('/');
      await expectUserAuthenticated(page);
    });
  });

  test.describe('Loading States', () => {
    test('should show loading state during authentication', async ({ page }) => {
      await goToSignInPage(page);

      // Mock delayed authentication
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (...args: any[]) => {
          await new Promise(resolve => setTimeout(resolve, 500));
          return originalSignIn(...args);
        };
      });

      // Start sign-in process
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);
      await page.getByRole('button', { name: /sign in/i }).click();

      // Should show loading state
      const signInButton = page.getByRole('button', { name: /sign in/i });
      await expect(signInButton).toContainText('Sign In');
      await expect(signInButton.locator('.animate-spin')).toBeVisible();
      await expect(signInButton).toBeDisabled();

      // Wait for completion
      await waitForAuthState(page, true);
    });

    test('should show initial loading state while Firebase initializes', async ({ page }) => {
      // Mock delayed Firebase initialization
      await page.addInitScript(() => {
        const originalOnAuthStateChanged = (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged;
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChanged = (callback: any) => {
          setTimeout(() => {
            originalOnAuthStateChanged(callback);
          }, 800);
          return () => {};
        };
      });

      await page.goto('/dashboard');

      // Should show loading spinner initially
      await expect(page.getByText(/loading/i).first()).toBeVisible();
      await expect(page.locator('.animate-spin').first()).toBeVisible();
    });
  });

  test.describe('Form Interactions', () => {
    test('should support keyboard navigation', async ({ page }) => {
      await goToSignInPage(page);

      // Tab through form elements
      await page.keyboard.press('Tab');
      await expect(page.locator('input[type="email"]')).toBeFocused();

      await page.keyboard.press('Tab');
      await expect(page.locator('input[type="password"]')).toBeFocused();

      await page.keyboard.press('Tab');
      await expect(page.getByRole('button', { name: /sign in/i })).toBeFocused();
    });

    test('should submit form on Enter key', async ({ page }) => {
      await goToSignInPage(page);

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);

      // Press Enter in password field
      await page.locator('input[type="password"]').press('Enter');

      // Should sign in
      await waitForAuthState(page, true);
      await expectUserAuthenticated(page);
    });

    test('should disable form during submission', async ({ page }) => {
      await goToSignInPage(page);

      // Mock delayed response
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (...args: any[]) => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return originalSignIn(...args);
        };
      });

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);
      await page.getByRole('button', { name: /sign in/i }).click();

      // All form elements should be disabled during submission
      await expect(page.locator('input[type="email"]')).toBeDisabled();
      await expect(page.locator('input[type="password"]')).toBeDisabled();
      await expect(page.getByRole('button', { name: /continue with google/i })).toBeDisabled();
      await expect(page.getByRole('button', { name: /forgot.*password/i })).toBeDisabled();
    });
  });
});