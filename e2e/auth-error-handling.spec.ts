/**
 * Authentication Error Handling Tests
 *
 * Tests comprehensive error handling scenarios including network errors,
 * validation errors, Firebase errors, and user-friendly error messages
 */

import { test, expect } from '@playwright/test';
import {
  setupMockAuth,
  goToSignInPage,
  goToSignUpPage,
  signInWithEmail,
  signUpWithEmail,
  signInWithGoogle,
  openUserProfileDialog,
  testUsers,
  setupTestEnvironment,
  enableTestMode,
  expectErrorMessage,
  mockNetworkError,
  clearNetworkMocks,
  waitForLoadingToComplete
} from './auth-utils';

test.describe('Authentication Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);
  });

  test.describe('Sign-In Error Handling', () => {
    test('should handle invalid email format', async ({ page }) => {
      await goToSignInPage(page);

      // Try various invalid email formats
      const invalidEmails = [
        'invalid-email',
        'test@',
        '@domain.com',
        'test..test@domain.com',
        'test@domain',
        'spaces in@email.com'
      ];

      for (const email of invalidEmails) {
        await page.fill('input[type="email"]', email);
        await page.fill('input[type="password"]', 'password123');

        // HTML5 validation should prevent submission or show custom error
        const emailInput = page.locator('input[type="email"]');
        await expect(emailInput).toHaveAttribute('type', 'email');

        // The browser's built-in validation should handle this
        const isValid = await emailInput.evaluate((input: HTMLInputElement) => input.validity.valid);
        expect(isValid).toBeFalsy();
      }
    });

    test('should handle wrong password error', async ({ page }) => {
      // Mock Firebase auth error for wrong password
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (email: string, password: string) => {
          if (password === 'wrongpassword') {
            throw new Error('Invalid email or password');
          }
          return (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail.original(email, password);
        };
      });

      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, 'wrongpassword');

      // Should show user-friendly error message
      await expectErrorMessage(page, /invalid email or password/i);

      // Form should remain usable for retry
      await expect(page.locator('input[type="email"]')).toBeEnabled();
      await expect(page.locator('input[type="password"]')).toBeEnabled();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeEnabled();
    });

    test('should handle user not found error', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (email: string, password: string) => {
          if (email === 'nonexistent@email.com') {
            throw new Error('User not found');
          }
          throw new Error('Invalid email or password');
        };
      });

      await goToSignInPage(page);
      await signInWithEmail(page, 'nonexistent@email.com', 'password123');

      // Should show generic error for security (don't reveal if user exists)
      await expectErrorMessage(page, /invalid email or password/i);
    });

    test('should handle too many attempts error', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
          throw new Error('Too many unsuccessful sign-in attempts. Please try again later.');
        };
      });

      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, 'anypassword');

      await expectErrorMessage(page, /too many.*attempts.*try again later/i);
    });

    test('should handle disabled account error', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
          throw new Error('Your account has been disabled. Please contact support.');
        };
      });

      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);

      await expectErrorMessage(page, /account.*disabled.*contact support/i);
    });

    test('should handle network connectivity errors', async ({ page }) => {
      await goToSignInPage(page);
      await mockNetworkError(page);

      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);

      // Should show network error or generic error
      await expectErrorMessage(page);

      // Clear network mock and retry should work
      await clearNetworkMocks(page);
      await page.getByRole('button', { name: /sign in/i }).click();
      // Should succeed now (depending on implementation)
    });

    test('should handle Google sign-in errors', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithGoogle = async () => {
          throw new Error('Google sign-in failed. Please try again.');
        };
      });

      await goToSignInPage(page);
      await signInWithGoogle(page);

      await expectErrorMessage(page, /google sign.*failed.*try again/i);
    });

    test('should handle popup blocked error for Google sign-in', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithGoogle = async () => {
          throw new Error('Popup blocked by browser. Please allow popups and try again.');
        };
      });

      await goToSignInPage(page);
      await signInWithGoogle(page);

      await expectErrorMessage(page, /popup blocked.*allow popups/i);
    });
  });

  test.describe('Sign-Up Error Handling', () => {
    test('should handle email already in use error', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.createAccountWithEmail = async (email: string) => {
          if (email === testUsers.validUser.email) {
            throw new Error('An account with this email already exists');
          }
          return { uid: 'new-user', email, emailVerified: false };
        };
      });

      await goToSignUpPage(page);
      await signUpWithEmail(page, testUsers.validUser.email, 'newpassword123', 'newpassword123');

      await expectErrorMessage(page, /account.*email already exists/i);

      // Should suggest signing in instead
      await expect(page.getByText(/already have an account/i)).toBeVisible();
    });

    test('should handle weak password error', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.createAccountWithEmail = async (email: string, password: string) => {
          if (password.length < 6) {
            throw new Error('Password must be at least 6 characters long');
          }
          return { uid: 'new-user', email, emailVerified: false };
        };
      });

      await goToSignUpPage(page);
      await signUpWithEmail(page, 'newuser@test.com', '123', '123');

      await expectErrorMessage(page, /password.*at least 6 characters/i);
    });

    test('should handle password mismatch client-side', async ({ page }) => {
      await goToSignUpPage(page);

      await page.fill('input[type="email"]', 'newuser@test.com');
      await page.fill('input[type="password"]', 'password123');
      await page.fill('input[placeholder*="Confirm"]', 'differentpassword');
      await page.getByRole('button', { name: /create account/i }).click();

      // Should show client-side validation error
      await expectErrorMessage(page, /passwords do not match/i);
    });

    test('should handle invalid email domain error', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.createAccountWithEmail = async (email: string) => {
          if (email.includes('invalid-domain')) {
            throw new Error('Invalid email domain');
          }
          return { uid: 'new-user', email, emailVerified: false };
        };
      });

      await goToSignUpPage(page);
      await signUpWithEmail(page, 'test@invalid-domain.fake', 'password123', 'password123');

      await expectErrorMessage(page, /invalid email domain/i);
    });

    test('should handle registration disabled error', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.createAccountWithEmail = async () => {
          throw new Error('Account registration is currently disabled');
        };
      });

      await goToSignUpPage(page);
      await signUpWithEmail(page, 'newuser@test.com', 'password123', 'password123');

      await expectErrorMessage(page, /registration.*disabled/i);
    });
  });

  test.describe('Profile Management Error Handling', () => {
    test.beforeEach(async ({ page }) => {
      // Sign in before profile tests
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await page.waitForTimeout(1000); // Wait for auth state
    });

    test('should handle display name update errors', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.updateUserProfile = async () => {
          throw new Error('Failed to update profile. Please try again.');
        };
      });

      await openUserProfileDialog(page);

      await page.fill('input[id="displayName"]', 'New Display Name');
      await page.getByRole('button', { name: /update profile/i }).click();

      await expectErrorMessage(page, /failed to update profile/i);

      // Form should remain usable
      await expect(page.locator('input[id="displayName"]')).toBeEnabled();
      await expect(page.getByRole('button', { name: /update profile/i })).toBeEnabled();
    });

    test('should handle password change with wrong current password', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.reauthenticateWithPassword = async (password: string) => {
          if (password !== testUsers.validUser.password) {
            throw new Error('Current password is incorrect');
          }
        };
      });

      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      await page.fill('input[id="currentPassword"]', 'wrongpassword');
      await page.fill('input[id="newPassword"]', 'newpassword123');
      await page.fill('input[id="confirmPassword"]', 'newpassword123');
      await page.getByRole('button', { name: /update password/i }).click();

      await expectErrorMessage(page, /current password is incorrect/i);
    });

    test('should handle email verification send failure', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.sendEmailVerification = async () => {
          throw new Error('Failed to send verification email. Please try again later.');
        };
      });

      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      // Mock unverified email first
      await page.addInitScript(() => {
        if ((window as any).__FIREBASE_AUTH_MOCK__.currentUser) {
          (window as any).__FIREBASE_AUTH_MOCK__.currentUser.emailVerified = false;
        }
      });

      await page.reload();
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      await page.getByRole('button', { name: /send verification/i }).click();

      await expectErrorMessage(page, /failed to send verification email/i);
    });

    test('should handle session timeout during profile operations', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.updateUserProfile = async () => {
          throw new Error('Session expired. Please sign in again.');
        };
      });

      await openUserProfileDialog(page);

      await page.fill('input[id="displayName"]', 'New Name');
      await page.getByRole('button', { name: /update profile/i }).click();

      await expectErrorMessage(page, /session expired.*sign in again/i);
    });
  });

  test.describe('Network and Connectivity Errors', () => {
    test('should handle intermittent network failures', async ({ page }) => {
      await goToSignInPage(page);

      // Mock intermittent network failure
      let failCount = 0;
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (...args: any[]) => {
          const count = (window as any).failCount || 0;
          (window as any).failCount = count + 1;

          if (count < 2) {
            throw new Error('Network error. Please check your connection.');
          }
          return originalSignIn(...args);
        };
      });

      // First attempt should fail
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await expectErrorMessage(page, /network error.*check.*connection/i);

      // Second attempt should also fail
      await page.getByRole('button', { name: /sign in/i }).click();
      await expectErrorMessage(page);

      // Third attempt should succeed
      await page.getByRole('button', { name: /sign in/i }).click();
      // Should eventually succeed
    });

    test('should handle slow network connections', async ({ page }) => {
      await goToSignInPage(page);

      // Mock very slow response
      await page.addInitScript(() => {
        const originalSignIn = (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail;
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async (...args: any[]) => {
          await new Promise(resolve => setTimeout(resolve, 5000));
          return originalSignIn(...args);
        };
      });

      await page.fill('input[type="email"]', testUsers.validUser.email);
      await page.fill('input[type="password"]', testUsers.validUser.password);
      await page.getByRole('button', { name: /sign in/i }).click();

      // Should show loading state for extended period
      const signInButton = page.getByRole('button', { name: /sign in/i });
      await expect(signInButton.locator('.animate-spin')).toBeVisible();
      await expect(signInButton).toBeDisabled();

      // Form should be disabled during loading
      await expect(page.locator('input[type="email"]')).toBeDisabled();
      await expect(page.locator('input[type="password"]')).toBeDisabled();
    });

    test('should handle API server errors', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
          throw new Error('Server error (500). Please try again later.');
        };
      });

      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);

      await expectErrorMessage(page, /server error.*try again later/i);
    });
  });

  test.describe('Error Message UX', () => {
    test('should display errors in accessible alert components', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, 'invalid@email.com', 'wrongpassword');

      // Error should be in an alert role for screen readers
      const errorAlert = page.locator('[role="alert"], .alert-destructive');
      await expect(errorAlert).toBeVisible();
      await expect(errorAlert).toContainText(/invalid email or password/i);

      // Should have proper ARIA attributes
      await expect(errorAlert).toHaveAttribute('role', 'alert');
    });

    test('should clear errors when user starts correcting them', async ({ page }) => {
      await goToSignInPage(page);
      await signInWithEmail(page, 'invalid@email.com', 'wrongpassword');
      await expectErrorMessage(page);

      // Start typing in email field
      await page.fill('input[type="email"]', 'corrected@email.com');

      // Error should be cleared
      await expect(page.locator('[role="alert"], .alert-destructive')).not.toBeVisible();
    });

    test('should show specific error messages for different failure types', async ({ page }) => {
      const errorScenarios = [
        {
          setup: () => page.addInitScript(() => {
            (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
              throw new Error('Invalid email or password');
            };
          }),
          expectedMessage: /invalid email or password/i
        },
        {
          setup: () => page.addInitScript(() => {
            (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
              throw new Error('Too many requests');
            };
          }),
          expectedMessage: /too many requests/i
        },
        {
          setup: () => page.addInitScript(() => {
            (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
              throw new Error('Network error');
            };
          }),
          expectedMessage: /network error/i
        }
      ];

      for (const scenario of errorScenarios) {
        await scenario.setup();
        await goToSignInPage(page);
        await signInWithEmail(page, testUsers.validUser.email, 'anypassword');
        await expectErrorMessage(page, scenario.expectedMessage);
      }
    });

    test('should prevent multiple error messages from stacking', async ({ page }) => {
      await goToSignInPage(page);

      // Trigger multiple errors quickly
      await signInWithEmail(page, 'invalid1@email.com', 'wrongpassword');
      await expectErrorMessage(page);

      await signInWithEmail(page, 'invalid2@email.com', 'wrongpassword');

      // Should only show one error message at a time
      const errorAlerts = page.locator('[role="alert"], .alert-destructive');
      await expect(errorAlerts).toHaveCount(1);
    });

    test('should provide helpful error recovery suggestions', async ({ page }) => {
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
          throw new Error('Account with this email already exists. Please sign in instead.');
        };
      });

      await goToSignUpPage(page);
      await signUpWithEmail(page, testUsers.validUser.email, 'password123', 'password123');

      // Should show error with helpful suggestion
      await expectErrorMessage(page, /already exists.*sign in instead/i);

      // Should still show the toggle to switch to sign-in mode
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });
  });

  test.describe('Form State During Errors', () => {
    test('should re-enable form after error', async ({ page }) => {
      await goToSignInPage(page);

      // Mock error with delay to test loading state
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
          await new Promise(resolve => setTimeout(resolve, 500));
          throw new Error('Authentication failed');
        };
      });

      await signInWithEmail(page, testUsers.validUser.email, 'wrongpassword');

      // Wait for error to appear
      await expectErrorMessage(page);

      // Form should be re-enabled for retry
      await expect(page.locator('input[type="email"]')).toBeEnabled();
      await expect(page.locator('input[type="password"]')).toBeEnabled();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeEnabled();
      await expect(page.getByRole('button', { name: /continue with google/i })).toBeEnabled();
    });

    test('should preserve form data after recoverable errors', async ({ page }) => {
      await goToSignInPage(page);

      const email = testUsers.validUser.email;
      const password = 'wrongpassword';

      await signInWithEmail(page, email, password);
      await expectErrorMessage(page);

      // Form should preserve the email but clear password for security
      await expect(page.locator('input[type="email"]')).toHaveValue(email);
      // Password might be cleared for security reasons - this is implementation dependent
    });

    test('should handle rapid successive error scenarios', async ({ page }) => {
      await goToSignInPage(page);

      // Mock different errors for rapid succession
      let errorCount = 0;
      await page.addInitScript(() => {
        (window as any).__FIREBASE_AUTH_MOCK__.signInWithEmail = async () => {
          const count = (window as any).errorCount || 0;
          (window as any).errorCount = count + 1;

          const errors = [
            'Network error',
            'Invalid credentials',
            'Too many attempts'
          ];
          throw new Error(errors[count % errors.length]);
        };
      });

      // Try multiple times rapidly
      for (let i = 0; i < 3; i++) {
        await signInWithEmail(page, testUsers.validUser.email, 'wrongpassword');
        await expectErrorMessage(page);
        await page.waitForTimeout(100); // Small delay between attempts
      }

      // Form should still be functional
      await expect(page.locator('input[type="email"]')).toBeEnabled();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeEnabled();
    });
  });
});