/**
 * Reset Onboarding E2E Test
 *
 * End-to-end test for the reset onboarding functionality including
 * navigation, user interactions, and API calls.
 */

import { test, expect } from '@playwright/test';
import { setupTestEnvironment, mockFirebaseAuth, mockApiEndpoints } from '../utils/test-helpers';

test.describe('Reset Onboarding Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Set up test environment
    await setupTestEnvironment(page);

    // Mock Firebase auth
    await mockFirebaseAuth(page, {
      uid: 'test-user',
      email: 'test@example.com',
      displayName: 'Test User',
    });

    // Mock API endpoints
    await mockApiEndpoints(page, {
      // Mock user profile data
      '/api/v1/users/me': {
        method: 'GET',
        response: {
          data: {
            id: 'test-user',
            firebaseUserId: 'test-user',
            email: 'test@example.com',
            displayName: 'Test User',
            sports: [
              { sportId: '1', name: 'Basketball', rank: 1, hasTeams: true },
              { sportId: '2', name: 'Football', rank: 2, hasTeams: true },
            ],
            teams: [
              { teamId: '1', name: 'Lakers', sportId: '1', league: 'NBA', affinityScore: 85 },
              { teamId: '2', name: 'Warriors', sportId: '1', league: 'NBA', affinityScore: 75 },
            ],
            preferences: {
              newsTypes: [
                { type: 'injuries', enabled: true, priority: 1 },
                { type: 'trades', enabled: true, priority: 2 },
              ],
              notifications: {
                push: true,
                email: false,
                gameReminders: true,
                newsAlerts: false,
                scoreUpdates: true,
              },
              contentFrequency: 'standard',
            },
          },
        },
      },
      // Mock reset endpoint
      '/api/v1/onboarding/reset': {
        method: 'POST',
        response: { data: null },
      },
    });
  });

  test('should display reset onboarding option in preferences page', async ({ page }) => {
    // Navigate to preferences page
    await page.goto('/preferences');

    // Wait for page to load
    await expect(page.getByText('Edit Preferences')).toBeVisible();

    // Scroll down to find the danger zone
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Check that danger zone exists
    await expect(page.getByText('Danger Zone')).toBeVisible();

    // Check that reset onboarding option exists
    await expect(page.getByText('Reset Onboarding')).toBeVisible();
    await expect(page.getByText('Delete all preferences and restart the onboarding process')).toBeVisible();
  });

  test('should open confirmation dialog when reset button is clicked', async ({ page }) => {
    await page.goto('/preferences');

    // Scroll to danger zone
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Click reset onboarding button
    await page.getByRole('button', { name: 'Reset Onboarding' }).click();

    // Check dialog opens
    await expect(page.getByText('Reset Onboarding?')).toBeVisible();
    await expect(page.getByText('This action will permanently delete all your current preferences')).toBeVisible();

    // Check warning content
    await expect(page.getByText('Selected sports and their rankings')).toBeVisible();
    await expect(page.getByText('Favorite teams and affinity scores')).toBeVisible();
    await expect(page.getByText('Content preferences and notification settings')).toBeVisible();
    await expect(page.getByText('You will be redirected to the onboarding flow')).toBeVisible();

    // Check buttons are present
    await expect(page.getByRole('button', { name: 'Cancel' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Reset Onboarding' })).toBeVisible();
  });

  test('should cancel reset when cancel button is clicked', async ({ page }) => {
    await page.goto('/preferences');

    // Open dialog
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.getByRole('button', { name: 'Reset Onboarding' }).click();
    await expect(page.getByText('Reset Onboarding?')).toBeVisible();

    // Click cancel
    await page.getByRole('button', { name: 'Cancel' }).click();

    // Dialog should close
    await expect(page.getByText('Reset Onboarding?')).not.toBeVisible();

    // Should still be on preferences page
    await expect(page.getByText('Edit Preferences')).toBeVisible();
  });

  test('should perform reset and redirect to onboarding when confirmed', async ({ page }) => {
    // Set up response tracking
    const resetRequests: any[] = [];
    await page.route('/api/v1/onboarding/reset', (route) => {
      resetRequests.push({
        method: route.request().method(),
        url: route.request().url(),
      });
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: null }),
      });
    });

    await page.goto('/preferences');

    // Open dialog and confirm
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.getByRole('button', { name: 'Reset Onboarding' }).click();
    await expect(page.getByText('Reset Onboarding?')).toBeVisible();

    // Click confirm
    await page.getByRole('button', { name: 'Reset Onboarding' }).last().click();

    // Check API call was made
    await page.waitForTimeout(100);
    expect(resetRequests).toHaveLength(1);
    expect(resetRequests[0].method).toBe('POST');

    // Check for success toast
    await expect(page.getByText('Onboarding Reset')).toBeVisible();
    await expect(page.getByText('Your preferences have been reset. Redirecting to onboarding...')).toBeVisible();

    // Wait for redirect (should happen after 1.5s)
    await page.waitForURL('/onboarding', { timeout: 3000 });
    expect(page.url()).toContain('/onboarding');
  });

  test('should show loading state during reset operation', async ({ page }) => {
    // Mock slow response
    await page.route('/api/v1/onboarding/reset', async (route) => {
      // Delay response to test loading state
      await new Promise(resolve => setTimeout(resolve, 500));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: null }),
      });
    });

    await page.goto('/preferences');

    // Open dialog and start reset
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.getByRole('button', { name: 'Reset Onboarding' }).click();
    await page.getByRole('button', { name: 'Reset Onboarding' }).last().click();

    // Check loading state
    await expect(page.getByText('Resetting...')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Cancel' })).toBeDisabled();

    // Wait for completion
    await expect(page.getByText('Onboarding Reset')).toBeVisible({ timeout: 2000 });
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock error response
    await page.route('/api/v1/onboarding/reset', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'INTERNAL_ERROR',
          message: 'Failed to reset onboarding',
          timestamp: new Date().toISOString(),
        }),
      });
    });

    await page.goto('/preferences');

    // Perform reset
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.getByRole('button', { name: 'Reset Onboarding' }).click();
    await page.getByRole('button', { name: 'Reset Onboarding' }).last().click();

    // Check error toast
    await expect(page.getByText('Reset Failed')).toBeVisible();
    await expect(page.getByText('Failed to reset onboarding. Please try again or contact support.')).toBeVisible();

    // Should still be on preferences page
    await expect(page.getByText('Edit Preferences')).toBeVisible();

    // Dialog should remain open for retry
    await expect(page.getByText('Reset Onboarding?')).toBeVisible();
  });

  test('should have proper accessibility features', async ({ page }) => {
    await page.goto('/preferences');

    // Check accessibility of the reset button
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    const resetButton = page.getByRole('button', { name: 'Reset Onboarding' });
    await expect(resetButton).toBeVisible();

    // Check that button is keyboard accessible
    await resetButton.focus();
    await expect(resetButton).toBeFocused();

    // Open dialog with keyboard
    await page.keyboard.press('Enter');
    await expect(page.getByText('Reset Onboarding?')).toBeVisible();

    // Check dialog accessibility
    const dialog = page.getByRole('alertdialog');
    await expect(dialog).toBeVisible();

    // Check focus management
    const cancelButton = page.getByRole('button', { name: 'Cancel' });
    await expect(cancelButton).toBeFocused();

    // Navigate with keyboard
    await page.keyboard.press('Tab');
    const confirmButton = page.getByRole('button', { name: 'Reset Onboarding' }).last();
    await expect(confirmButton).toBeFocused();

    // Close with escape
    await page.keyboard.press('Escape');
    await expect(page.getByText('Reset Onboarding?')).not.toBeVisible();
  });
});