/**
 * Basic Auth Functionality Tests
 *
 * Tests the core authentication functionality with the actual UI components
 * and Firebase integration using the real implementation.
 */

import { test, expect } from '@playwright/test';

test.describe('Basic Authentication Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Setup test environment
    await page.addInitScript(() => {
      (window as any).__PLAYWRIGHT_TEST__ = true;
      (window as any).__TEST_ENV__ = {
        VITE_FIREBASE_API_KEY: 'mock-api-key',
        VITE_FIREBASE_AUTH_DOMAIN: 'mock-project.firebaseapp.com',
        VITE_FIREBASE_PROJECT_ID: 'mock-project-id',
        VITE_TEST_MODE: 'true'
      };
    });
  });

  test('should show sign-in page for unauthenticated users', async ({ page }) => {
    await page.goto('/');

    // Should redirect to sign-in page or show sign-in content
    await page.waitForLoadState('networkidle');

    // Check for either the auth form or sign-in button
    const hasAuthForm = await page.locator('[data-testid="sign-in-form"]').isVisible().catch(() => false);
    const hasSignInButton = await page.getByText('Sign In').isVisible().catch(() => false);

    expect(hasAuthForm || hasSignInButton).toBe(true);
  });

  test('should show sign-in form elements', async ({ page }) => {
    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    // Wait for the auth form to load
    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    // Check for form elements
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /continue with google/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should validate form inputs', async ({ page }) => {
    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    // Test that sign in button is disabled when fields are empty
    const signInButton = page.getByRole('button', { name: /sign in/i });
    await expect(signInButton).toBeDisabled();

    // Fill only email
    await page.fill('input[type="email"]', 'test@example.com');
    await expect(signInButton).toBeDisabled();

    // Fill password too
    await page.fill('input[type="password"]', 'password123');
    await expect(signInButton).toBeEnabled();
  });

  test('should toggle between sign in and sign up modes', async ({ page }) => {
    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    // Should be in sign-in mode initially
    await expect(page.locator('[data-testid="auth-form-title"]')).toContainText('Sign In');

    // Look for sign up toggle - this might be implemented differently
    const signUpButton = page.getByText(/sign up|create account|don't have an account/i);
    if (await signUpButton.isVisible()) {
      await signUpButton.click();

      // Check if mode changed
      const title = await page.locator('[data-testid="auth-form-title"]').textContent();
      expect(title).toMatch(/create account|sign up/i);
    }
  });

  test('should show loading states', async ({ page }) => {
    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    // Fill form
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');

    // Mock delayed response for testing loading state
    await page.addInitScript(() => {
      // Override fetch to simulate delay
      const originalFetch = window.fetch;
      window.fetch = async (...args) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        return originalFetch(...args);
      };
    });

    // Click sign in and check for loading state
    const signInButton = page.getByRole('button', { name: /sign in/i });
    await signInButton.click();

    // Should show loading spinner
    await expect(page.locator('.animate-spin')).toBeVisible({ timeout: 2000 });
  });

  test('should show Google sign-in button', async ({ page }) => {
    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    const googleButton = page.getByRole('button', { name: /continue with google/i });
    await expect(googleButton).toBeVisible();

    // Check for Google icon (Chrome icon is used as placeholder)
    await expect(googleButton.locator('svg')).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    // Tab through form elements
    await page.keyboard.press('Tab');
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeFocused();

    await page.keyboard.press('Tab');
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeFocused();
  });

  test('should allow test mode bypass for protected routes', async ({ page }) => {
    // Enable test mode
    await page.addInitScript(() => {
      (window as any).__PLAYWRIGHT_TEST__ = true;
    });

    // Try to access a protected route
    await page.goto('/?test=true');
    await page.waitForLoadState('networkidle');

    // Should not redirect to sign-in page due to test mode
    await expect(page).not.toHaveURL(/\/auth\/sign-in/);
  });

  test('should show proper error states', async ({ page }) => {
    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    // Test with invalid email format
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', 'password123');

    // The HTML5 email validation should prevent submission
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toHaveAttribute('type', 'email');

    // Ensure it's a valid email input that will trigger browser validation
    const validity = await emailInput.evaluate((el: HTMLInputElement) => el.validity.valid);
    expect(validity).toBe(false);
  });

  test('should maintain responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/auth/sign-in');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('[data-testid="sign-in-form"]')).toBeVisible({ timeout: 10000 });

    // Check that form is properly sized
    const formCard = page.locator('[data-testid="sign-in-form"]');
    const boundingBox = await formCard.boundingBox();

    expect(boundingBox).toBeTruthy();
    if (boundingBox) {
      expect(boundingBox.width).toBeLessThanOrEqual(375); // Should fit in viewport
    }
  });
});