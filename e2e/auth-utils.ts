/**
 * Authentication Test Utilities
 *
 * Provides reusable utilities and fixtures for Firebase authentication testing
 */

import { Page, expect } from '@playwright/test';

/**
 * Test user credentials for consistent testing
 */
export const testUsers = {
  validUser: {
    email: 'test@cornerleague.com',
    password: 'TestPassword123!',
    displayName: 'Test User'
  },
  validUser2: {
    email: 'test2@cornerleague.com',
    password: 'TestPassword456!',
    displayName: 'Test User 2'
  },
  invalidUser: {
    email: 'invalid@test.com',
    password: 'wrongpassword'
  }
};

/**
 * Mock Firebase Auth for testing
 */
export async function setupMockAuth(page: Page) {
  await page.addInitScript(() => {
    // Mock Firebase Auth for testing
    (window as any).__FIREBASE_AUTH_MOCK__ = {
      currentUser: null,
      onAuthStateChangedCallbacks: [],

      // Mock Google sign-in
      signInWithGoogle: async () => {
        const mockUser = {
          uid: 'mock-google-uid',
          email: 'test@gmail.com',
          displayName: 'Test Google User',
          photoURL: 'https://example.com/photo.jpg',
          emailVerified: true,
          providerData: [{ providerId: 'google.com' }],
          metadata: {
            creationTime: new Date().toISOString(),
            lastSignInTime: new Date().toISOString()
          }
        };
        (window as any).__FIREBASE_AUTH_MOCK__.currentUser = mockUser;
        (window as any).__FIREBASE_AUTH_MOCK__.triggerAuthStateChange(mockUser);
        return mockUser;
      },

      // Mock email/password sign-in
      signInWithEmail: async (email: string, password: string) => {
        if (email === 'test@cornerleague.com' && password === 'TestPassword123!') {
          const mockUser = {
            uid: 'mock-email-uid',
            email: email,
            displayName: 'Test User',
            photoURL: null,
            emailVerified: true,
            providerData: [{ providerId: 'password' }],
            metadata: {
              creationTime: new Date().toISOString(),
              lastSignInTime: new Date().toISOString()
            }
          };
          (window as any).__FIREBASE_AUTH_MOCK__.currentUser = mockUser;
          (window as any).__FIREBASE_AUTH_MOCK__.triggerAuthStateChange(mockUser);
          return mockUser;
        } else {
          throw new Error('Invalid email or password');
        }
      },

      // Mock account creation
      createAccountWithEmail: async (email: string, password: string) => {
        const mockUser = {
          uid: 'mock-new-uid',
          email: email,
          displayName: null,
          photoURL: null,
          emailVerified: false,
          providerData: [{ providerId: 'password' }],
          metadata: {
            creationTime: new Date().toISOString(),
            lastSignInTime: new Date().toISOString()
          }
        };
        (window as any).__FIREBASE_AUTH_MOCK__.currentUser = mockUser;
        (window as any).__FIREBASE_AUTH_MOCK__.triggerAuthStateChange(mockUser);
        return mockUser;
      },

      // Mock sign out
      signOut: async () => {
        (window as any).__FIREBASE_AUTH_MOCK__.currentUser = null;
        (window as any).__FIREBASE_AUTH_MOCK__.triggerAuthStateChange(null);
      },

      // Mock password reset
      sendPasswordResetEmail: async (email: string) => {
        if (!email.includes('@')) {
          throw new Error('Invalid email address');
        }
        // Simulate successful password reset email
        return Promise.resolve();
      },

      // Mock email verification
      sendEmailVerification: async () => {
        return Promise.resolve();
      },

      // Mock profile update
      updateUserProfile: async (updates: any) => {
        if ((window as any).__FIREBASE_AUTH_MOCK__.currentUser) {
          Object.assign((window as any).__FIREBASE_AUTH_MOCK__.currentUser, updates);
          (window as any).__FIREBASE_AUTH_MOCK__.triggerAuthStateChange(
            (window as any).__FIREBASE_AUTH_MOCK__.currentUser
          );
        }
        return Promise.resolve();
      },

      // Mock password update
      updateUserPassword: async (newPassword: string) => {
        if (newPassword.length < 6) {
          throw new Error('Password must be at least 6 characters');
        }
        return Promise.resolve();
      },

      // Mock reauthentication
      reauthenticateWithPassword: async (password: string) => {
        if (password !== 'TestPassword123!') {
          throw new Error('Current password is incorrect');
        }
        return Promise.resolve();
      },

      // Mock auth state change listener
      onAuthStateChanged: (callback: any) => {
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChangedCallbacks.push(callback);
        // Immediately call with current user state
        callback((window as any).__FIREBASE_AUTH_MOCK__.currentUser);
        return () => {
          const index = (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChangedCallbacks.indexOf(callback);
          if (index > -1) {
            (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChangedCallbacks.splice(index, 1);
          }
        };
      },

      // Helper to trigger auth state changes
      triggerAuthStateChange: (user: any) => {
        (window as any).__FIREBASE_AUTH_MOCK__.onAuthStateChangedCallbacks.forEach((callback: any) => {
          callback(user);
        });
      }
    };
  });
}

/**
 * Navigate to the sign-in page and wait for it to load
 */
export async function goToSignInPage(page: Page) {
  await page.goto('/auth/sign-in');
  // Wait for the auth form to load - just check for email input which should be unique
  await expect(page.locator('input[type="email"]').first()).toBeVisible();
}

/**
 * Navigate to the sign-up page and wait for it to load
 */
export async function goToSignUpPage(page: Page) {
  await page.goto('/auth/sign-in');
  // Click the sign-up toggle
  await page.getByRole('button', { name: /sign up/i }).click();
  await expect(page.getByRole('heading', { name: 'Create Account' })).toBeVisible();
}

/**
 * Perform email/password sign-in
 */
export async function signInWithEmail(page: Page, email: string, password: string) {
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.getByRole('button', { name: /sign in/i }).click();
}

/**
 * Perform email/password sign-up
 */
export async function signUpWithEmail(page: Page, email: string, password: string, confirmPassword?: string) {
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  if (confirmPassword !== undefined) {
    await page.fill('input[placeholder*="Confirm"]', confirmPassword);
  }
  await page.getByRole('button', { name: /create account/i }).click();
}

/**
 * Perform Google sign-in
 */
export async function signInWithGoogle(page: Page) {
  await page.getByRole('button', { name: /continue with google/i }).click();
}

/**
 * Sign out the current user
 */
export async function signOut(page: Page) {
  // Click user profile dropdown
  await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
  // Click sign out
  await page.getByRole('menuitem', { name: /sign out/i }).click();
}

/**
 * Wait for authentication state to settle
 */
export async function waitForAuthState(page: Page, authenticated: boolean = true) {
  if (authenticated) {
    // Wait for user profile to be visible
    await expect(page.locator('[data-testid="user-profile"], button:has([data-testid="user-avatar"])')).toBeVisible();
  } else {
    // Wait for sign-in form to be visible
    await expect(page.locator('[data-testid="sign-in-form"], .sign-in-card')).toBeVisible();
  }
}

/**
 * Verify user is authenticated
 */
export async function expectUserAuthenticated(page: Page, userEmail?: string) {
  await expect(page.locator('[data-testid="user-profile"], button:has([data-testid="user-avatar"])')).toBeVisible();

  if (userEmail) {
    // Click profile dropdown to check email
    await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
    await expect(page.getByText(userEmail)).toBeVisible();
    // Close dropdown by clicking outside
    await page.keyboard.press('Escape');
  }
}

/**
 * Verify user is not authenticated
 */
export async function expectUserNotAuthenticated(page: Page) {
  await expect(page.locator('[data-testid="sign-in-form"], .sign-in-card')).toBeVisible();
  await expect(page.locator('[data-testid="user-profile"]')).not.toBeVisible();
}

/**
 * Fill out the password reset form
 */
export async function requestPasswordReset(page: Page, email: string) {
  await page.getByRole('button', { name: /forgot.*password/i }).click();
  await expect(page.getByText('Reset Password')).toBeVisible();
  await page.fill('input[type="email"]', email);
  await page.getByRole('button', { name: /send reset email/i }).click();
}

/**
 * Open user profile dialog
 */
export async function openUserProfileDialog(page: Page) {
  await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
  await page.getByRole('menuitem', { name: /profile settings/i }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
}

/**
 * Update user profile display name
 */
export async function updateDisplayName(page: Page, newDisplayName: string) {
  await openUserProfileDialog(page);

  // Navigate to profile tab if not already there
  await page.getByRole('tab', { name: /profile/i }).click();

  // Update display name
  await page.fill('input[id="displayName"]', '');
  await page.fill('input[id="displayName"]', newDisplayName);
  await page.getByRole('button', { name: /update profile/i }).click();

  // Wait for success message
  await expect(page.getByText(/profile updated successfully/i)).toBeVisible();
}

/**
 * Change user password
 */
export async function changePassword(page: Page, currentPassword: string, newPassword: string) {
  await openUserProfileDialog(page);

  // Navigate to security tab
  await page.getByRole('tab', { name: /security/i }).click();

  // Fill password change form
  await page.fill('input[id="currentPassword"]', currentPassword);
  await page.fill('input[id="newPassword"]', newPassword);
  await page.fill('input[id="confirmPassword"]', newPassword);
  await page.getByRole('button', { name: /update password/i }).click();

  // Wait for success message
  await expect(page.getByText(/password updated successfully/i)).toBeVisible();
}

/**
 * Send email verification
 */
export async function sendEmailVerification(page: Page) {
  await openUserProfileDialog(page);

  // Navigate to security tab
  await page.getByRole('tab', { name: /security/i }).click();

  // Click send verification button
  await page.getByRole('button', { name: /send verification/i }).click();

  // Wait for success message
  await expect(page.getByText(/verification email sent/i)).toBeVisible();
}

/**
 * Mock network errors for testing error handling
 */
export async function mockNetworkError(page: Page) {
  await page.route('**/*', route => {
    route.abort('failed');
  });
}

/**
 * Clear all network route mocks
 */
export async function clearNetworkMocks(page: Page) {
  await page.unroute('**/*');
}

/**
 * Wait for loading state to complete
 */
export async function waitForLoadingToComplete(page: Page) {
  // Wait for any loading spinners to disappear
  await expect(page.locator('.animate-spin, [data-testid="loading"]')).not.toBeVisible();
}

/**
 * Check for error messages
 */
export async function expectErrorMessage(page: Page, expectedError?: string) {
  const errorAlert = page.locator('[role="alert"], .alert-destructive');
  await expect(errorAlert).toBeVisible();

  if (expectedError) {
    await expect(errorAlert).toContainText(expectedError);
  }
}

/**
 * Check for success messages
 */
export async function expectSuccessMessage(page: Page, expectedMessage?: string) {
  const successAlert = page.locator('.alert:not(.alert-destructive), [data-testid="success-message"]');
  await expect(successAlert).toBeVisible();

  if (expectedMessage) {
    await expect(successAlert).toContainText(expectedMessage);
  }
}

/**
 * Set up test mode bypass for authentication
 */
export async function enableTestMode(page: Page) {
  await page.addInitScript(() => {
    (window as any).__PLAYWRIGHT_TEST__ = true;
  });
}

/**
 * Disable test mode bypass
 */
export async function disableTestMode(page: Page) {
  await page.addInitScript(() => {
    (window as any).__PLAYWRIGHT_TEST__ = false;
  });
}

/**
 * Mock Firebase environment for testing
 */
export async function setupTestEnvironment(page: Page) {
  await page.addInitScript(() => {
    // Mock environment variables
    (window as any).__TEST_ENV__ = {
      VITE_FIREBASE_API_KEY: 'mock-api-key',
      VITE_FIREBASE_AUTH_DOMAIN: 'mock-project.firebaseapp.com',
      VITE_FIREBASE_PROJECT_ID: 'mock-project-id',
      VITE_TEST_MODE: 'true'
    };
  });
}