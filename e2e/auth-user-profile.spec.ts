/**
 * User Profile Component Tests
 *
 * Tests the UserProfile dropdown, dialog, and all profile management functionality
 */

import { test, expect } from '@playwright/test';
import {
  setupMockAuth,
  goToSignInPage,
  signInWithEmail,
  signInWithGoogle,
  waitForAuthState,
  expectUserAuthenticated,
  openUserProfileDialog,
  updateDisplayName,
  changePassword,
  sendEmailVerification,
  testUsers,
  setupTestEnvironment,
  enableTestMode,
  expectErrorMessage,
  expectSuccessMessage
} from './auth-utils';

test.describe('User Profile Component', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);

    // Sign in before each test
    await goToSignInPage(page);
    await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
    await waitForAuthState(page, true);
  });

  test.describe('Profile Dropdown', () => {
    test('should display user avatar and name in dropdown trigger', async ({ page }) => {
      // Check profile trigger button
      const profileTrigger = page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])');
      await expect(profileTrigger).toBeVisible();

      // Should show user avatar
      await expect(profileTrigger.locator('img, .avatar')).toBeVisible();

      // Should show display name or email
      await expect(profileTrigger).toContainText(/test/i);
    });

    test('should open dropdown menu on click', async ({ page }) => {
      // Click profile trigger
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();

      // Dropdown menu should be visible
      await expect(page.locator('[role="menu"]')).toBeVisible();

      // Should show user info
      await expect(page.getByText(testUsers.validUser.email)).toBeVisible();
    });

    test('should display correct user information in dropdown', async ({ page }) => {
      // Click profile trigger
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();

      // Should show user email
      await expect(page.getByText(testUsers.validUser.email)).toBeVisible();

      // Should show display name if available
      if (testUsers.validUser.displayName) {
        await expect(page.getByText(testUsers.validUser.displayName)).toBeVisible();
      }
    });

    test('should have profile settings menu item', async ({ page }) => {
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();

      const profileMenuItem = page.getByRole('menuitem', { name: /profile settings/i });
      await expect(profileMenuItem).toBeVisible();
      await expect(profileMenuItem.locator('svg')).toBeVisible(); // User icon
    });

    test('should have sign out menu item', async ({ page }) => {
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();

      const signOutMenuItem = page.getByRole('menuitem', { name: /sign out/i });
      await expect(signOutMenuItem).toBeVisible();
      await expect(signOutMenuItem.locator('svg')).toBeVisible(); // LogOut icon
    });

    test('should close dropdown when clicking outside', async ({ page }) => {
      // Open dropdown
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await expect(page.locator('[role="menu"]')).toBeVisible();

      // Click outside
      await page.click('body');

      // Dropdown should close
      await expect(page.locator('[role="menu"]')).not.toBeVisible();
    });

    test('should close dropdown on Escape key', async ({ page }) => {
      // Open dropdown
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await expect(page.locator('[role="menu"]')).toBeVisible();

      // Press Escape
      await page.keyboard.press('Escape');

      // Dropdown should close
      await expect(page.locator('[role="menu"]')).not.toBeVisible();
    });
  });

  test.describe('Profile Dialog', () => {
    test('should open profile dialog from dropdown', async ({ page }) => {
      await openUserProfileDialog(page);

      // Dialog should be visible
      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.getByText('Profile Settings')).toBeVisible();
      await expect(page.getByText('Manage your account settings and preferences')).toBeVisible();
    });

    test('should display tabs for different sections', async ({ page }) => {
      await openUserProfileDialog(page);

      // Should have three tabs
      await expect(page.getByRole('tab', { name: /profile/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /security/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /account/i })).toBeVisible();
    });

    test('should start on profile tab by default', async ({ page }) => {
      await openUserProfileDialog(page);

      // Profile tab should be selected
      await expect(page.getByRole('tab', { name: /profile/i })).toHaveAttribute('data-state', 'active');

      // Profile content should be visible
      await expect(page.getByText('Profile Information')).toBeVisible();
    });

    test('should switch between tabs', async ({ page }) => {
      await openUserProfileDialog(page);

      // Switch to security tab
      await page.getByRole('tab', { name: /security/i }).click();
      await expect(page.getByRole('tab', { name: /security/i })).toHaveAttribute('data-state', 'active');
      await expect(page.getByText('Email Verification')).toBeVisible();

      // Switch to account tab
      await page.getByRole('tab', { name: /account/i }).click();
      await expect(page.getByRole('tab', { name: /account/i })).toHaveAttribute('data-state', 'active');
      await expect(page.getByText('Account Information')).toBeVisible();

      // Switch back to profile tab
      await page.getByRole('tab', { name: /profile/i }).click();
      await expect(page.getByRole('tab', { name: /profile/i })).toHaveAttribute('data-state', 'active');
      await expect(page.getByText('Profile Information')).toBeVisible();
    });

    test('should close dialog on overlay click', async ({ page }) => {
      await openUserProfileDialog(page);
      await expect(page.getByRole('dialog')).toBeVisible();

      // Click overlay (outside dialog content)
      await page.locator('[data-radix-dialog-overlay]').click();

      // Dialog should close
      await expect(page.getByRole('dialog')).not.toBeVisible();
    });

    test('should close dialog on Escape key', async ({ page }) => {
      await openUserProfileDialog(page);
      await expect(page.getByRole('dialog')).toBeVisible();

      // Press Escape
      await page.keyboard.press('Escape');

      // Dialog should close
      await expect(page.getByRole('dialog')).not.toBeVisible();
    });
  });

  test.describe('Profile Tab', () => {
    test('should display user avatar and information', async ({ page }) => {
      await openUserProfileDialog(page);

      // Should show large avatar
      await expect(page.locator('.avatar, [data-testid="user-avatar"]')).toBeVisible();

      // Should show user email
      await expect(page.getByText(testUsers.validUser.email)).toBeVisible();

      // Should show display name field
      await expect(page.locator('input[id="displayName"]')).toBeVisible();
    });

    test('should update display name successfully', async ({ page }) => {
      const newDisplayName = 'Updated Test User';
      await updateDisplayName(page, newDisplayName);

      // Should show success message
      await expectSuccessMessage(page, 'Profile updated successfully');

      // Display name field should show updated value
      await expect(page.locator('input[id="displayName"]')).toHaveValue(newDisplayName);
    });

    test('should validate display name input', async ({ page }) => {
      await openUserProfileDialog(page);

      // Clear display name
      await page.fill('input[id="displayName"]', '');

      // Update button should be disabled
      await expect(page.getByRole('button', { name: /update profile/i })).toBeDisabled();

      // Fill with whitespace only
      await page.fill('input[id="displayName"]', '   ');
      await expect(page.getByRole('button', { name: /update profile/i })).toBeDisabled();

      // Fill with valid name
      await page.fill('input[id="displayName"]', 'Valid Name');
      await expect(page.getByRole('button', { name: /update profile/i })).toBeEnabled();
    });

    test('should show loading state during profile update', async ({ page }) => {
      await openUserProfileDialog(page);

      // Mock delayed profile update
      await page.addInitScript(() => {
        const originalUpdate = (window as any).__FIREBASE_AUTH_MOCK__.updateUserProfile;
        (window as any).__FIREBASE_AUTH_MOCK__.updateUserProfile = async (...args: any[]) => {
          await new Promise(resolve => setTimeout(resolve, 1000));
          return originalUpdate(...args);
        };
      });

      await page.fill('input[id="displayName"]', 'Loading Test');
      await page.getByRole('button', { name: /update profile/i }).click();

      // Should show loading state
      const updateButton = page.getByRole('button', { name: /update profile/i });
      await expect(updateButton.locator('.animate-spin')).toBeVisible();
      await expect(updateButton).toBeDisabled();

      // Form should be disabled
      await expect(page.locator('input[id="displayName"]')).toBeDisabled();
    });

    test('should clear success/error messages when typing', async ({ page }) => {
      await openUserProfileDialog(page);

      // Trigger a successful update first
      await page.fill('input[id="displayName"]', 'Test Update');
      await page.getByRole('button', { name: /update profile/i }).click();
      await expectSuccessMessage(page);

      // Start typing in the field
      await page.fill('input[id="displayName"]', 'New Text');

      // Success message should be cleared
      await expect(page.locator('.alert:not(.alert-destructive)')).not.toBeVisible();
    });

    test('should display email as read-only', async ({ page }) => {
      await openUserProfileDialog(page);

      const emailInput = page.locator('input').filter({ hasText: testUsers.validUser.email });
      await expect(emailInput).toBeDisabled();

      // Should show explanation text
      await expect(page.getByText(/email address cannot be changed/i)).toBeVisible();
    });
  });

  test.describe('Security Tab', () => {
    test('should display email verification status', async ({ page }) => {
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      // Should show email verification section
      await expect(page.getByText('Email Verification')).toBeVisible();
      await expect(page.getByText('Email Status:')).toBeVisible();

      // Should show verification badge
      await expect(page.locator('.badge, [data-testid="verification-badge"]')).toBeVisible();
    });

    test('should send email verification for unverified emails', async ({ page }) => {
      // Mock unverified email state
      await page.addInitScript(() => {
        if ((window as any).__FIREBASE_AUTH_MOCK__.currentUser) {
          (window as any).__FIREBASE_AUTH_MOCK__.currentUser.emailVerified = false;
        }
      });

      await sendEmailVerification(page);

      // Should show success message
      await expectSuccessMessage(page, 'Verification email sent');
    });

    test('should change password with current password verification', async ({ page }) => {
      const currentPassword = testUsers.validUser.password;
      const newPassword = 'NewSecurePassword123!';

      await changePassword(page, currentPassword, newPassword);

      // Should show success message
      await expectSuccessMessage(page, 'Password updated successfully');

      // Form should be cleared
      await expect(page.locator('input[id="currentPassword"]')).toHaveValue('');
      await expect(page.locator('input[id="newPassword"]')).toHaveValue('');
      await expect(page.locator('input[id="confirmPassword"]')).toHaveValue('');
    });

    test('should validate password change form', async ({ page }) => {
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      const updateButton = page.getByRole('button', { name: /update password/i });

      // Button should be disabled initially
      await expect(updateButton).toBeDisabled();

      // Fill current password only
      await page.fill('input[id="currentPassword"]', 'test123');
      await expect(updateButton).toBeDisabled();

      // Fill new password (too short)
      await page.fill('input[id="newPassword"]', '123');
      await expect(updateButton).toBeDisabled();

      // Fill valid new password
      await page.fill('input[id="newPassword"]', 'ValidPass123!');
      await expect(updateButton).toBeDisabled();

      // Fill mismatched confirm password
      await page.fill('input[id="confirmPassword"]', 'DifferentPass123!');
      await expect(updateButton).toBeDisabled();
      await expect(page.getByText('Passwords do not match')).toBeVisible();

      // Fill matching confirm password
      await page.fill('input[id="confirmPassword"]', 'ValidPass123!');
      await expect(updateButton).toBeEnabled();
      await expect(page.getByText('Passwords do not match')).not.toBeVisible();
    });

    test('should handle incorrect current password', async ({ page }) => {
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      // Fill form with incorrect current password
      await page.fill('input[id="currentPassword"]', 'wrongpassword');
      await page.fill('input[id="newPassword"]', 'NewValidPass123!');
      await page.fill('input[id="confirmPassword"]', 'NewValidPass123!');
      await page.getByRole('button', { name: /update password/i }).click();

      // Should show error message
      await expectErrorMessage(page, 'Current password is incorrect');
    });

    test('should clear error messages when typing', async ({ page }) => {
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /security/i }).click();

      // Trigger an error first
      await page.fill('input[id="currentPassword"]', 'wrongpassword');
      await page.fill('input[id="newPassword"]', 'NewValidPass123!');
      await page.fill('input[id="confirmPassword"]', 'NewValidPass123!');
      await page.getByRole('button', { name: /update password/i }).click();
      await expectErrorMessage(page);

      // Start typing in any field
      await page.fill('input[id="currentPassword"]', 'w');

      // Error should be cleared
      await expect(page.locator('.alert-destructive')).not.toBeVisible();
    });
  });

  test.describe('Account Tab', () => {
    test('should display account metadata', async ({ page }) => {
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /account/i }).click();

      // Should show account information
      await expect(page.getByText('Account Information')).toBeVisible();

      // Should display user ID
      await expect(page.getByText('User ID')).toBeVisible();
      await expect(page.getByText('mock-email-uid')).toBeVisible(); // From mock

      // Should display email verification status
      await expect(page.getByText('Email Verified')).toBeVisible();

      // Should display sign-in providers
      await expect(page.getByText('Sign-in Providers')).toBeVisible();
    });

    test('should display creation and last sign-in dates', async ({ page }) => {
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /account/i }).click();

      // Should show account creation date
      await expect(page.getByText('Account Created')).toBeVisible();

      // Should show last sign-in date
      await expect(page.getByText('Last Sign In')).toBeVisible();
    });

    test('should display correct provider information', async ({ page }) => {
      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /account/i }).click();

      // Should show email/password provider
      await expect(page.getByText('Email/Password')).toBeVisible();
    });
  });

  test.describe('Google OAuth User Profile', () => {
    test('should display Google user information correctly', async ({ page }) => {
      // Sign in with Google instead
      await page.goto('/auth/sign-in');
      await signInWithGoogle(page);
      await waitForAuthState(page, true);

      await openUserProfileDialog(page);

      // Should show Google profile photo
      await expect(page.locator('img[src*="example.com/photo.jpg"]')).toBeVisible();

      // Should show Google display name
      await expect(page.getByText('Test Google User')).toBeVisible();

      // Should show Google email
      await expect(page.getByText('test@gmail.com')).toBeVisible();
    });

    test('should show Google provider in account tab', async ({ page }) => {
      // Sign in with Google
      await page.goto('/auth/sign-in');
      await signInWithGoogle(page);
      await waitForAuthState(page, true);

      await openUserProfileDialog(page);
      await page.getByRole('tab', { name: /account/i }).click();

      // Should show Google provider
      await expect(page.getByText('google.com')).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    test('should adapt to mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      // Profile trigger should hide text on small screens
      const profileTrigger = page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])');
      await expect(profileTrigger).toBeVisible();

      // Text should be hidden on mobile (hidden sm:inline class)
      const profileText = profileTrigger.locator('span');
      await expect(profileText).toHaveClass(/hidden/);
    });

    test('should make profile dialog scrollable on small screens', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      await openUserProfileDialog(page);

      // Dialog should be visible and scrollable
      const dialog = page.getByRole('dialog');
      await expect(dialog).toBeVisible();
      await expect(dialog).toHaveClass(/overflow-y-auto/);
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should support keyboard navigation in dropdown', async ({ page }) => {
      // Tab to profile trigger
      await page.keyboard.press('Tab');
      // Continue tabbing until we reach the profile trigger
      // This might need adjustment based on page content

      // Open dropdown with Enter
      await page.keyboard.press('Enter');
      await expect(page.locator('[role="menu"]')).toBeVisible();

      // Navigate menu items with arrow keys
      await page.keyboard.press('ArrowDown');
      await expect(page.getByRole('menuitem', { name: /profile settings/i })).toBeFocused();

      await page.keyboard.press('ArrowDown');
      await expect(page.getByRole('menuitem', { name: /sign out/i })).toBeFocused();

      // Close with Escape
      await page.keyboard.press('Escape');
      await expect(page.locator('[role="menu"]')).not.toBeVisible();
    });

    test('should support keyboard navigation in dialog tabs', async ({ page }) => {
      await openUserProfileDialog(page);

      // Tab to the tab list
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Navigate tabs with arrow keys
      await page.keyboard.press('ArrowRight');
      await expect(page.getByRole('tab', { name: /security/i })).toBeFocused();

      await page.keyboard.press('ArrowRight');
      await expect(page.getByRole('tab', { name: /account/i })).toBeFocused();

      await page.keyboard.press('ArrowLeft');
      await expect(page.getByRole('tab', { name: /security/i })).toBeFocused();
    });
  });
});