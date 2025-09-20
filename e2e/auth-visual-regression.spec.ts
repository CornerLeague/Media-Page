/**
 * Authentication Visual Regression Tests
 *
 * Tests visual consistency and appearance of authentication components
 * across different states, themes, and screen sizes
 */

import { test, expect } from '@playwright/test';
import {
  setupMockAuth,
  goToSignInPage,
  goToSignUpPage,
  signInWithEmail,
  openUserProfileDialog,
  testUsers,
  setupTestEnvironment,
  enableTestMode,
  requestPasswordReset
} from './auth-utils';

test.describe('Authentication Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);
  });

  test.describe('Sign-In Page Visual Tests', () => {
    test('should match sign-in page baseline - desktop', async ({ page }) => {
      await goToSignInPage(page);

      // Wait for page to fully load
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);

      // Take screenshot of the entire sign-in form
      await expect(page).toHaveScreenshot('auth-signin-desktop.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match sign-in page baseline - mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await goToSignInPage(page);

      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot('auth-signin-mobile.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match sign-in page with error state', async ({ page }) => {
      await goToSignInPage(page);

      // Trigger error state
      await page.fill('input[type="email"]', 'invalid@email.com');
      await page.fill('input[type="password"]', 'wrongpassword');
      await page.getByRole('button', { name: /sign in/i }).click();

      // Wait for error to appear
      await page.waitForSelector('[role="alert"]', { timeout: 5000 });
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('auth-signin-error.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match sign-in page loading state', async ({ page }) => {
      // Mock delayed response for loading state
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (...args: any[]) => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          return originalSignIn(...args);
        };
      });

      await goToSignInPage(page);

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);
      await page.getByRole('button', { name: /sign in/i }).click();

      // Wait for loading state to appear
      await page.waitForSelector('.animate-spin', { timeout: 1000 });

      await expect(page).toHaveScreenshot('auth-signin-loading.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match Google sign-in button styling', async ({ page }) => {
      await goToSignInPage(page);

      // Focus on just the Google button area
      const googleButton = page.getByRole('button', { name: /continue with google/i });
      await expect(googleButton).toBeVisible();

      await expect(googleButton).toHaveScreenshot('auth-google-button.png', {
        threshold: 0.1,
        maxDiffPixels: 500
      });
    });

    test('should match form focus states', async ({ page }) => {
      await goToSignInPage(page);

      // Focus email input
      await page.locator('input[type="email"]').focus();
      await page.waitForTimeout(200);

      await expect(page.locator('input[type="email"]')).toHaveScreenshot('auth-email-input-focused.png', {
        threshold: 0.1,
        maxDiffPixels: 300
      });

      // Focus password input
      await page.locator('input[type="password"]').focus();
      await page.waitForTimeout(200);

      await expect(page.locator('input[type="password"]')).toHaveScreenshot('auth-password-input-focused.png', {
        threshold: 0.1,
        maxDiffPixels: 300
      });
    });
  });

  test.describe('Sign-Up Page Visual Tests', () => {
    test('should match sign-up page baseline', async ({ page }) => {
      await goToSignUpPage(page);

      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot('auth-signup-desktop.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match sign-up page with password confirmation', async ({ page }) => {
      await goToSignUpPage(page);

      // Fill out form partially to show all fields
      await page.fill('input[type="email"]', 'newuser@test.com');
      await page.fill('input[type="password"]', 'password123');

      // Show confirm password field is visible
      const confirmField = page.locator('input[placeholder*="Confirm"]');
      await expect(confirmField).toBeVisible();

      await expect(page).toHaveScreenshot('auth-signup-form-filled.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match password mismatch error state', async ({ page }) => {
      await goToSignUpPage(page);

      await page.fill('input[type="email"]', 'newuser@test.com');
      await page.fill('input[type="password"]', 'password123');
      await page.fill('input[placeholder*="Confirm"]', 'differentpassword');
      await page.getByRole('button', { name: /create account/i }).click();

      // Wait for error message
      await page.waitForSelector(':text("Passwords do not match")', { timeout: 2000 });

      await expect(page).toHaveScreenshot('auth-signup-password-mismatch.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match mode toggle transitions', async ({ page }) => {
      await goToSignInPage(page);

      // Capture sign-in mode
      await expect(page).toHaveScreenshot('auth-signin-mode.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });

      // Toggle to sign-up mode
      await page.getByRole('button', { name: /sign up/i }).click();
      await page.waitForTimeout(300);

      // Capture sign-up mode
      await expect(page).toHaveScreenshot('auth-signup-mode.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });

      // Toggle back to sign-in
      await page.getByRole('button', { name: /sign in/i }).click();
      await page.waitForTimeout(300);

      // Should match original state
      await expect(page).toHaveScreenshot('auth-signin-mode-return.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });
  });

  test.describe('Password Reset Visual Tests', () => {
    test('should match password reset form', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('auth-password-reset-form.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match password reset success state', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      await requestPasswordReset(page, testUsers.validUser.email);

      // Wait for success message to appear
      await page.waitForSelector('[role="alert"]:not(.alert-destructive)', { timeout: 2000 });
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('auth-password-reset-success.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match password reset validation error', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Trigger validation error
      await page.fill('input[type="email"]', 'invalid-email');
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Wait for error
      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot('auth-password-reset-error.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });
  });

  test.describe('User Profile Visual Tests', () => {
    test.beforeEach(async ({ page }) => {
      // Sign in before profile tests
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await page.waitForTimeout(1000);
    });

    test('should match user profile dropdown', async ({ page }) => {
      // Click to open dropdown
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();

      await page.waitForTimeout(300);

      // Screenshot the dropdown menu
      const dropdown = page.locator('[role="menu"]');
      await expect(dropdown).toHaveScreenshot('auth-profile-dropdown.png', {
        threshold: 0.1,
        maxDiffPixels: 500
      });
    });

    test('should match profile dialog - profile tab', async ({ page }) => {
      await openUserProfileDialog(page);

      await page.waitForTimeout(500);

      // Screenshot the profile tab
      await expect(page.getByRole('dialog')).toHaveScreenshot('auth-profile-dialog-profile-tab.png', {
        threshold: 0.2,
        maxDiffPixels: 1500
      });
    });

    test('should match profile dialog - security tab', async ({ page }) => {
      await openUserProfileDialog(page);

      await page.getByRole('tab', { name: /security/i }).click();
      await page.waitForTimeout(300);

      await expect(page.getByRole('dialog')).toHaveScreenshot('auth-profile-dialog-security-tab.png', {
        threshold: 0.2,
        maxDiffPixels: 1500
      });
    });

    test('should match profile dialog - account tab', async ({ page }) => {
      await openUserProfileDialog(page);

      await page.getByRole('tab', { name: /account/i }).click();
      await page.waitForTimeout(300);

      await expect(page.getByRole('dialog')).toHaveScreenshot('auth-profile-dialog-account-tab.png', {
        threshold: 0.2,
        maxDiffPixels: 1500
      });
    });

    test('should match profile update success state', async ({ page }) => {
      await openUserProfileDialog(page);

      // Update display name
      await page.fill('input[id="displayName"]', 'Updated Test User');
      await page.getByRole('button', { name: /update profile/i }).click();

      // Wait for success message
      await page.waitForSelector('.alert:not(.alert-destructive)', { timeout: 2000 });
      await page.waitForTimeout(300);

      await expect(page.getByRole('dialog')).toHaveScreenshot('auth-profile-update-success.png', {
        threshold: 0.2,
        maxDiffPixels: 1500
      });
    });

    test('should match mobile profile dialog', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      await openUserProfileDialog(page);
      await page.waitForTimeout(500);

      await expect(page.getByRole('dialog')).toHaveScreenshot('auth-profile-dialog-mobile.png', {
        threshold: 0.2,
        maxDiffPixels: 1500
      });
    });
  });

  test.describe('Theme Visual Tests', () => {
    test('should match dark theme sign-in page', async ({ page }) => {
      await goToSignInPage(page);

      // Switch to dark theme if toggle exists
      const themeToggle = page.locator('[data-testid="theme-toggle"], button:has([data-testid="theme-icon"])');
      if (await themeToggle.count() > 0) {
        await themeToggle.click();
        await page.waitForTimeout(500);

        await expect(page).toHaveScreenshot('auth-signin-dark-theme.png', {
          fullPage: false,
          threshold: 0.2,
          maxDiffPixels: 1000
        });
      }
    });

    test('should match light theme sign-in page', async ({ page }) => {
      await goToSignInPage(page);

      // Ensure light theme is active
      const themeToggle = page.locator('[data-testid="theme-toggle"], button:has([data-testid="theme-icon"])');
      if (await themeToggle.count() > 0) {
        // Click twice to ensure light mode
        await themeToggle.click();
        await page.waitForTimeout(200);
        await themeToggle.click();
        await page.waitForTimeout(500);
      }

      await expect(page).toHaveScreenshot('auth-signin-light-theme.png', {
        fullPage: false,
        threshold: 0.2,
        maxDiffPixels: 1000
      });
    });

    test('should match theme toggle consistency across auth components', async ({ page }) => {
      await goToSignInPage(page);

      const themeToggle = page.locator('[data-testid="theme-toggle"], button:has([data-testid="theme-icon"])');
      if (await themeToggle.count() > 0) {
        // Test sign-in in dark theme
        await themeToggle.click();
        await page.waitForTimeout(300);

        // Toggle to sign-up
        await page.getByRole('button', { name: /sign up/i }).click();
        await page.waitForTimeout(300);

        await expect(page).toHaveScreenshot('auth-signup-dark-theme.png', {
          fullPage: false,
          threshold: 0.2,
          maxDiffPixels: 1000
        });

        // Go to password reset
        await page.getByRole('button', { name: /sign in/i }).click();
        await page.getByRole('button', { name: /forgot.*password/i }).click();
        await page.waitForTimeout(300);

        await expect(page).toHaveScreenshot('auth-password-reset-dark-theme.png', {
          fullPage: false,
          threshold: 0.2,
          maxDiffPixels: 1000
        });
      }
    });
  });

  test.describe('Responsive Design Visual Tests', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1280, height: 720 },
      { name: 'large-desktop', width: 1920, height: 1080 }
    ];

    for (const viewport of viewports) {
      test(`should match sign-in page on ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await goToSignInPage(page);

        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(500);

        await expect(page).toHaveScreenshot(`auth-signin-${viewport.name}.png`, {
          fullPage: false,
          threshold: 0.2,
          maxDiffPixels: 1000
        });
      });
    }

    test('should match profile dropdown on different screen sizes', async ({ page }) => {
      // Sign in first
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await page.waitForTimeout(1000);

      for (const viewport of viewports.slice(0, 3)) { // Skip large desktop for dropdown
        await page.setViewportSize({ width: viewport.width, height: viewport.height });

        await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
        await page.waitForTimeout(300);

        const dropdown = page.locator('[role="menu"]');
        await expect(dropdown).toHaveScreenshot(`auth-profile-dropdown-${viewport.name}.png`, {
          threshold: 0.2,
          maxDiffPixels: 800
        });

        // Close dropdown for next iteration
        await page.keyboard.press('Escape');
      }
    });
  });

  test.describe('Component State Visual Tests', () => {
    test('should match form validation states', async ({ page }) => {
      await goToSignInPage(page);

      // Fill invalid email
      await page.fill('input[type="email"]', 'invalid-email');
      await page.locator('input[type="email"]').blur();

      // Capture invalid email state
      await expect(page.locator('input[type="email"]')).toHaveScreenshot('auth-email-invalid-state.png', {
        threshold: 0.1,
        maxDiffPixels: 300
      });

      // Fill valid email
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.locator('input[type="email"]').blur();

      // Capture valid email state
      await expect(page.locator('input[type="email"]')).toHaveScreenshot('auth-email-valid-state.png', {
        threshold: 0.1,
        maxDiffPixels: 300
      });
    });

    test('should match button disabled/enabled states', async ({ page }) => {
      await goToSignInPage(page);

      // Initially disabled state
      const signInButton = page.getByRole('button', { name: /sign in/i });
      await expect(signInButton).toHaveScreenshot('auth-button-disabled.png', {
        threshold: 0.1,
        maxDiffPixels: 200
      });

      // Fill form to enable button
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);

      // Enabled state
      await expect(signInButton).toHaveScreenshot('auth-button-enabled.png', {
        threshold: 0.1,
        maxDiffPixels: 200
      });
    });

    test('should match hover states', async ({ page }) => {
      await goToSignInPage(page);

      // Fill form to enable button
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);

      // Hover over sign-in button
      const signInButton = page.getByRole('button', { name: /sign in/i });
      await signInButton.hover();
      await page.waitForTimeout(200);

      await expect(signInButton).toHaveScreenshot('auth-button-hover.png', {
        threshold: 0.1,
        maxDiffPixels: 200
      });

      // Hover over Google button
      const googleButton = page.getByRole('button', { name: /continue with google/i });
      await googleButton.hover();
      await page.waitForTimeout(200);

      await expect(googleButton).toHaveScreenshot('auth-google-button-hover.png', {
        threshold: 0.1,
        maxDiffPixels: 200
      });
    });
  });

  test.describe('Animation and Transition Visual Tests', () => {
    test('should capture loading spinner animation frame', async ({ page }) => {
      // Mock delayed response for loading state
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (...args: any[]) => {
          await new Promise(resolve => setTimeout(resolve, 3000));
          return originalSignIn(...args);
        };
      });

      await goToSignInPage(page);

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);
      await page.getByRole('button', { name: /sign in/i }).click();

      // Wait for spinner to appear and capture mid-animation
      await page.waitForSelector('.animate-spin', { timeout: 1000 });
      await page.waitForTimeout(500);

      const spinner = page.locator('.animate-spin').first();
      await expect(spinner).toHaveScreenshot('auth-loading-spinner.png', {
        threshold: 0.3, // Higher threshold due to animation
        maxDiffPixels: 500
      });
    });

    test('should capture alert fade-in transition', async ({ page }) => {
      await goToSignInPage(page);

      // Trigger error to show alert animation
      await page.fill('input[type="email"]', 'invalid@email.com');
      await page.fill('input[type="password"]', 'wrongpassword');
      await page.getByRole('button', { name: /sign in/i }).click();

      // Wait for alert to start appearing
      await page.waitForSelector('[role="alert"]', { timeout: 2000 });
      await page.waitForTimeout(100); // Capture during transition

      const alert = page.locator('[role="alert"]');
      await expect(alert).toHaveScreenshot('auth-alert-transition.png', {
        threshold: 0.2,
        maxDiffPixels: 500
      });
    });
  });
});