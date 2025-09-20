import { test, expect } from '@playwright/test';

test.describe('Continue Button Fix Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Set up test mode to bypass authentication
    await page.addInitScript(() => {
      (window as any).__PLAYWRIGHT_TEST__ = true;
    });

    // Navigate to page first, then clear localStorage
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('Continue button becomes enabled when sports are selected', async ({ page }) => {
    // Navigate to sports selection
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();
    await page.getByRole('button', { name: /get started/i }).click();

    // Verify we're on sports selection
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();

    // Verify Continue button is initially disabled
    const continueButton = page.getByRole('button', { name: /continue/i });
    await expect(continueButton).toBeDisabled();

    // Select first sport
    const firstCheckbox = page.getByRole('checkbox').first();
    await firstCheckbox.click();

    // Wait a moment for state to update
    await page.waitForTimeout(500);

    // Verify Continue button becomes enabled
    await expect(continueButton).toBeEnabled();

    // Select second sport
    const secondCheckbox = page.getByRole('checkbox').nth(1);
    await secondCheckbox.click();

    // Wait a moment for state to update
    await page.waitForTimeout(500);

    // Verify Continue button remains enabled
    await expect(continueButton).toBeEnabled();

    // Verify we can click the Continue button (it should work now)
    await continueButton.click();

    // Verify we moved to the next step (team selection or next page)
    await expect(page.getByText(/select and rank your favorite sports/i)).not.toBeVisible();
  });

  test('Continue button stays disabled when no sports selected', async ({ page }) => {
    // Navigate to sports selection
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();
    await page.getByRole('button', { name: /get started/i }).click();

    // Verify we're on sports selection
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();

    // Verify Continue button is disabled
    const continueButton = page.getByRole('button', { name: /continue/i });
    await expect(continueButton).toBeDisabled();

    // Wait to ensure it stays disabled
    await page.waitForTimeout(2000);
    await expect(continueButton).toBeDisabled();
  });
});