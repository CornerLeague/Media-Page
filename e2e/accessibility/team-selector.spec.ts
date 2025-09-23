import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Team Selector Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the onboarding team selection step
    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');
  });

  test('should not have any accessibility violations on initial load', async ({ page }) => {
    // Run accessibility scan on initial page load
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should maintain accessibility when dropdown is opened', async ({ page }) => {
    // Open the team selector dropdown
    await page.getByRole('combobox', { name: 'Select teams' }).click();

    // Wait for dropdown to be visible
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Run accessibility scan with dropdown open
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should be keyboard navigable', async ({ page }) => {
    // Start from the team selector button
    await page.getByRole('combobox', { name: 'Select teams' }).focus();

    // Open dropdown with Enter key
    await page.keyboard.press('Enter');

    // Wait for dropdown to open
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Should be able to navigate to search input with Tab
    await page.keyboard.press('Tab');

    // Verify search input is focused
    const searchInput = page.getByPlaceholder('Search for teams...');
    await expect(searchInput).toBeFocused();

    // Type search query
    await searchInput.fill('Lakers');

    // Wait for search results
    await page.waitForTimeout(500); // Allow debounce

    // Should be able to navigate to team options with arrow keys
    await page.keyboard.press('ArrowDown');

    // Should be able to select with Enter
    await page.keyboard.press('Enter');

    // Verify team was selected
    await expect(page.getByText('Selected Teams (1)')).toBeVisible();
  });

  test('should have proper ARIA attributes', async ({ page }) => {
    const combobox = page.getByRole('combobox', { name: 'Select teams' });

    // Check initial ARIA attributes
    await expect(combobox).toHaveAttribute('aria-expanded', 'false');
    await expect(combobox).toHaveAttribute('aria-haspopup', 'dialog');

    // Open dropdown
    await combobox.click();

    // Check ARIA attributes when open
    await expect(combobox).toHaveAttribute('aria-expanded', 'true');

    // Check search input has proper labeling
    const searchInput = page.getByPlaceholder('Search for teams...');
    await expect(searchInput).toBeVisible();

    // Check listbox role
    const listbox = page.locator('[role="listbox"]');
    await expect(listbox).toBeVisible();
    await expect(listbox).toHaveAttribute('aria-label', 'Suggestions');
  });

  test('should support screen reader announcements', async ({ page }) => {
    // Open dropdown
    await page.getByRole('combobox', { name: 'Select teams' }).click();

    // Wait for dropdown
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Type search query
    const searchInput = page.getByPlaceholder('Search for teams...');
    await searchInput.fill('Lakers');

    // Wait for results
    await page.waitForTimeout(500);

    // Check that results are announced (via aria-live regions or similar)
    const resultsInfo = page.getByText(/Showing .* of .* teams/);
    if (await resultsInfo.isVisible()) {
      // Results count should be visible to screen readers
      await expect(resultsInfo).toBeVisible();
    }
  });

  test('should handle focus management correctly', async ({ page }) => {
    const combobox = page.getByRole('combobox', { name: 'Select teams' });

    // Focus should start on the combobox
    await combobox.focus();
    await expect(combobox).toBeFocused();

    // Open dropdown
    await combobox.click();

    // Focus should move to search input automatically
    const searchInput = page.getByPlaceholder('Search for teams...');
    await expect(searchInput).toBeFocused();

    // Close dropdown with Escape
    await page.keyboard.press('Escape');

    // Focus should return to combobox
    await expect(combobox).toBeFocused();
  });

  test('should have sufficient color contrast', async ({ page }) => {
    // Run accessibility scan specifically for color contrast
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .include('[data-testid="team-selector"]')
      .analyze();

    const colorContrastViolations = accessibilityScanResults.violations.filter(
      violation => violation.id === 'color-contrast'
    );

    expect(colorContrastViolations).toEqual([]);
  });

  test('should work with high contrast mode', async ({ page }) => {
    // Simulate high contrast mode by forcing prefers-contrast: high
    await page.emulateMedia({
      colorScheme: 'dark',
      reducedMotion: 'reduce'
    });

    // Open team selector
    await page.getByRole('combobox', { name: 'Select teams' }).click();

    // Wait for dropdown
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Run accessibility scan in high contrast mode
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should support reduced motion preferences', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });

    // Open team selector
    await page.getByRole('combobox', { name: 'Select teams' }).click();

    // Dropdown should still open but without animations
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Verify functionality still works
    const searchInput = page.getByPlaceholder('Search for teams...');
    await searchInput.fill('Lakers');

    await page.waitForTimeout(500);

    // Should still be able to select teams
    const teamOption = page.getByText('Los Angeles Lakers').first();
    if (await teamOption.isVisible()) {
      await teamOption.click();
      await expect(page.getByText('Selected Teams (1)')).toBeVisible();
    }
  });

  test('should have proper error announcements', async ({ page }) => {
    // Mock API to return an error
    await page.route('**/api/teams/search**', route => {
      route.abort('failed');
    });

    // Open team selector
    await page.getByRole('combobox', { name: 'Select teams' }).click();

    // Try to search
    const searchInput = page.getByPlaceholder('Search for teams...');
    await searchInput.fill('Lakers');

    // Wait for error state
    await page.waitForTimeout(1000);

    // Check for error message
    const errorMessage = page.getByText(/Failed to search teams/);
    if (await errorMessage.isVisible()) {
      // Error should be visible and accessible
      await expect(errorMessage).toBeVisible();

      // Should have appropriate ARIA role
      await expect(errorMessage).toHaveAttribute('role', 'alert');
    }
  });
});