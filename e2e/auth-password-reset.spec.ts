/**
 * Password Reset Flow Tests
 *
 * Tests the complete password reset functionality including form validation,
 * email sending, error handling, and user experience flows
 */

import { test, expect } from '@playwright/test';
import {
  setupMockAuth,
  goToSignInPage,
  requestPasswordReset,
  testUsers,
  setupTestEnvironment,
  enableTestMode,
  expectErrorMessage,
  expectSuccessMessage,
  mockNetworkError,
  clearNetworkMocks,
  waitForLoadingToComplete
} from './auth-utils';

test.describe('Password Reset Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);
  });

  test.describe('Password Reset Navigation', () => {
    test('should navigate to password reset from sign-in page', async ({ page }) => {
      await goToSignInPage(page);

      // Click forgot password link
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Should show password reset form
      await expect(page.getByText('Reset Password')).toBeVisible();
      await expect(page.getByText(/enter your email.*reset your password/i)).toBeVisible();
    });

    test('should show back button to return to sign-in', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Should show back button
      const backButton = page.locator('button:has(svg)').first(); // Arrow left icon
      await expect(backButton).toBeVisible();

      // Click back button
      await backButton.click();

      // Should return to sign-in form
      await expect(page.getByText('Sign In')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('should hide forgot password link in sign-up mode', async ({ page }) => {
      await goToSignInPage(page);

      // Switch to sign-up mode
      await page.getByRole('button', { name: /sign up/i }).click();

      // Forgot password link should not be visible
      await expect(page.getByRole('button', { name: /forgot.*password/i })).not.toBeVisible();
    });
  });

  test.describe('Password Reset Form', () => {
    test.beforeEach(async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();
    });

    test('should display proper form elements', async ({ page }) => {
      // Should show title and description
      await expect(page.getByText('Reset Password')).toBeVisible();
      await expect(page.getByText(/enter your email.*reset your password/i)).toBeVisible();

      // Should show email input with icon
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toBeVisible();
      await expect(emailInput).toHaveAttribute('placeholder', /enter your email/i);

      // Should show mail icon
      await expect(page.locator('svg').first()).toBeVisible(); // Mail icon

      // Should show submit button
      await expect(page.getByRole('button', { name: /send reset email/i })).toBeVisible();
    });

    test('should successfully send password reset email', async ({ page }) => {
      await requestPasswordReset(page, testUsers.validUser.email);

      // Should show success message
      await expectSuccessMessage(page, /password reset email sent.*check your inbox/i);

      // Should show back to sign-in button
      await expect(page.getByRole('button', { name: /back to sign in/i })).toBeVisible();

      // Form should be hidden
      await expect(page.locator('input[type="email"]')).not.toBeVisible();
      await expect(page.getByRole('button', { name: /send reset email/i })).not.toBeVisible();
    });

    test('should validate email format', async ({ page }) => {
      // Try with invalid email format
      await page.fill('input[type="email"]', 'invalid-email');
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show validation error
      await expect(page.getByText(/please enter a valid email address/i)).toBeVisible();

      // Should not show success message
      await expect(page.getByText(/password reset email sent/i)).not.toBeVisible();
    });

    test('should require email address', async ({ page }) => {
      // Try to submit empty form
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show required field error
      await expect(page.getByText(/email address is required/i)).toBeVisible();

      // Submit button should be disabled for empty email
      await expect(page.getByRole('button', { name: /send reset email/i })).toBeDisabled();
    });

    test('should enable/disable submit button based on email input', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: /send reset email/i });
      const emailInput = page.locator('input[type="email"]');

      // Initially disabled for empty input
      await expect(submitButton).toBeDisabled();

      // Enable when email is entered
      await emailInput.fill('test@example.com');
      await expect(submitButton).toBeEnabled();

      // Disable when email is cleared
      await emailInput.fill('');
      await expect(submitButton).toBeDisabled();

      // Enable for whitespace-trimmed input
      await emailInput.fill('  test@example.com  ');
      await expect(submitButton).toBeEnabled();
    });

    test('should clear errors when user starts typing', async ({ page }) => {
      // Trigger validation error
      await page.fill('input[type="email"]', 'invalid');
      await page.getByRole('button', { name: /send reset email/i }).click();
      await expect(page.getByText(/valid email address/i)).toBeVisible();

      // Start typing
      await page.fill('input[type="email"]', 'valid@');

      // Error should be cleared
      await expect(page.getByText(/valid email address/i)).not.toBeVisible();
    });

    test('should show loading state during email sending', async ({ page }) => {
      // Mock delayed email sending
      await page.addInitScript(() => {
        const originalReset = (window as any).__FIREBASE_AUTH_MOCK__.sendPasswordResetEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.sendPasswordResetEmail = async (...args: any[]) => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return originalReset(...args);
        };
      });

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show loading state
      const submitButton = page.getByRole('button', { name: /send reset email/i });
      await expect(submitButton.locator('.animate-spin')).toBeVisible();
      await expect(submitButton).toBeDisabled();
      await expect(page.locator('input[type="email"]')).toBeDisabled();

      // Wait for completion
      await waitForLoadingToComplete(page);
      await expectSuccessMessage(page);
    });
  });

  test.describe('Error Handling', () => {
    test.beforeEach(async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();
    });

    test('should handle invalid email address error', async ({ page }) => {
      // Mock Firebase error for invalid email
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.sendPasswordResetEmail = async (email: string) => {
          throw new Error('Invalid email address');
        };
      });

      await page.fill('input[type="email"]', 'valid@email.com');
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show error message
      await expectErrorMessage(page, 'Invalid email address');

      // Form should remain visible for retry
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.getByRole('button', { name: /send reset email/i })).toBeVisible();
    });

    test('should handle user not found error', async ({ page }) => {
      // Mock Firebase error for user not found
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.sendPasswordResetEmail = async (email: string) => {
          throw new Error('User not found');
        };
      });

      await page.fill('input[type="email"]', 'nonexistent@email.com');
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show error message
      await expectErrorMessage(page, 'User not found');
    });

    test('should handle network errors gracefully', async ({ page }) => {
      await mockNetworkError(page);

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show generic error (since network failed)
      await expectErrorMessage(page);

      await clearNetworkMocks(page);
    });

    test('should handle rate limiting errors', async ({ page }) => {
      // Mock rate limiting error
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.sendPasswordResetEmail = async (email: string) => {
          throw new Error('Too many requests. Please try again later.');
        };
      });

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Should show rate limiting error
      await expectErrorMessage(page, /too many requests.*try again later/i);
    });

    test('should clear errors when retrying', async ({ page }) => {
      // Trigger an error first
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.sendPasswordResetEmail = async (email: string) => {
          throw new Error('Network error');
        };
      });

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.getByRole('button', { name: /send reset email/i }).click();
      await expectErrorMessage(page);

      // Clear the mock error and retry
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.sendPasswordResetEmail = async (email: string) => {
          return Promise.resolve();
        };
      });

      await page.getByRole('button', { name: /send reset email/i }).click();

      // Error should be cleared and success should show
      await expect(page.locator('.alert-destructive')).not.toBeVisible();
      await expectSuccessMessage(page);
    });
  });

  test.describe('Success Flow', () => {
    test.beforeEach(async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();
    });

    test('should show success state with instructions', async ({ page }) => {
      await requestPasswordReset(page, testUsers.validUser.email);

      // Should show success icon and message
      await expect(page.locator('.alert:not(.alert-destructive)')).toBeVisible();
      await expect(page.getByText(/password reset email sent/i)).toBeVisible();
      await expect(page.getByText(/check your inbox.*follow the instructions/i)).toBeVisible();

      // Should show check circle icon
      await expect(page.locator('svg[data-testid="check-circle"], .check-circle')).toBeVisible();
    });

    test('should hide form after successful submission', async ({ page }) => {
      await requestPasswordReset(page, testUsers.validUser.email);

      // Form elements should be hidden
      await expect(page.locator('input[type="email"]')).not.toBeVisible();
      await expect(page.getByRole('button', { name: /send reset email/i })).not.toBeVisible();
      await expect(page.getByText(/enter your email address/i)).not.toBeVisible();
    });

    test('should provide way to return to sign-in after success', async ({ page }) => {
      await requestPasswordReset(page, testUsers.validUser.email);

      // Should show back to sign-in button
      const backButton = page.getByRole('button', { name: /back to sign in/i });
      await expect(backButton).toBeVisible();

      // Click to return to sign-in
      await backButton.click();

      // Should be back on sign-in page
      await expect(page.getByText('Sign In')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('should show remember password link after success', async ({ page }) => {
      await requestPasswordReset(page, testUsers.validUser.email);

      // Should show remember password text and link
      await expect(page.getByText(/remember your password/i)).toBeVisible();

      // Should have sign-in link
      const signInLink = page.getByRole('button', { name: /sign in/i }).last();
      await expect(signInLink).toBeVisible();

      // Click sign-in link
      await signInLink.click();

      // Should return to sign-in page
      await expect(page.getByText('Sign In')).toBeVisible();
    });
  });

  test.describe('Form Accessibility', () => {
    test.beforeEach(async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();
    });

    test('should have proper form labels and accessibility', async ({ page }) => {
      // Email input should have proper label
      await expect(page.getByLabel(/email address/i)).toBeVisible();

      // Input should have proper placeholder
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toHaveAttribute('placeholder', /enter your email/i);

      // Submit button should be properly labeled
      await expect(page.getByRole('button', { name: /send reset email/i })).toBeVisible();
    });

    test('should support keyboard navigation', async ({ page }) => {
      // Tab to email input
      await page.keyboard.press('Tab');
      await expect(page.locator('input[type="email"]')).toBeFocused();

      // Tab to submit button
      await page.keyboard.press('Tab');
      await expect(page.getByRole('button', { name: /send reset email/i })).toBeFocused();

      // Tab to back button
      await page.keyboard.press('Tab');
      const backButton = page.locator('button:has(svg)').first();
      await expect(backButton).toBeFocused();
    });

    test('should submit form with Enter key', async ({ page }) => {
      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.locator('input[type="email"]').press('Enter');

      // Should submit and show success
      await expectSuccessMessage(page);
    });

    test('should announce errors to screen readers', async ({ page }) => {
      // Trigger validation error
      await page.fill('input[type="email"]', 'invalid');
      await page.getByRole('button', { name: /send reset email/i }).click();

      // Error should be in an alert role for screen readers
      await expect(page.locator('[role="alert"], .alert')).toBeVisible();
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('should adapt to mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Form should be properly sized for mobile
      const card = page.locator('.card, [data-testid="password-reset-card"]');
      await expect(card).toBeVisible();

      // Input should be full width
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toHaveClass(/w-full/);

      // Button should be full width
      const submitButton = page.getByRole('button', { name: /send reset email/i });
      await expect(submitButton).toHaveClass(/w-full/);
    });

    test('should handle mobile keyboard interactions', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Focus email input
      await page.locator('input[type="email"]').focus();

      // Should show email keyboard on mobile
      await expect(page.locator('input[type="email"]')).toHaveAttribute('type', 'email');
    });
  });
});