import { test, expect, devices } from '@playwright/test';

test.describe('Team Selector Mobile Responsiveness', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the onboarding team selection step
    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');
  });

  test('should work on iPhone 12', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Check if team selector is visible and properly sized
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    await expect(teamSelector).toBeVisible();

    // Get the bounding box to check sizing
    const box = await teamSelector.boundingBox();
    expect(box?.width).toBeGreaterThan(300); // Should be reasonably wide on mobile

    // Open dropdown
    await teamSelector.click();

    // Check dropdown appears properly on mobile
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Search input should be properly sized
    const searchInput = page.getByPlaceholder('Search for teams...');
    await expect(searchInput).toBeVisible();

    const searchBox = await searchInput.boundingBox();
    expect(searchBox?.width).toBeGreaterThan(200);

    await context.close();
  });

  test('should work on Pixel 5', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['Pixel 5'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Test touch interactions
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    await expect(teamSelector).toBeVisible();

    // Tap to open
    await teamSelector.tap();

    // Dropdown should open
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Test scrolling in dropdown if there are many teams
    const dropdown = page.locator('[cmdk-list]');
    await expect(dropdown).toBeVisible();

    // Touch interaction for search
    const searchInput = page.getByPlaceholder('Search for teams...');
    await searchInput.tap();
    await searchInput.fill('Lakers');

    await page.waitForTimeout(500);

    await context.close();
  });

  test('should work on iPad', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPad Pro'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Team selector should adapt to tablet size
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    await expect(teamSelector).toBeVisible();

    // Should have appropriate padding and spacing on tablet
    const box = await teamSelector.boundingBox();
    expect(box?.width).toBeGreaterThan(400); // Should be wider on tablet

    // Open dropdown
    await teamSelector.click();

    // Dropdown should be properly positioned
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    const dropdown = page.locator('[cmdk-list]');
    const dropdownBox = await dropdown.boundingBox();

    // Should have reasonable max height on tablet
    expect(dropdownBox?.height).toBeLessThanOrEqual(300);

    await context.close();
  });

  test('should handle landscape orientation', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12 landscape'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Check team selector in landscape mode
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    await expect(teamSelector).toBeVisible();

    // Open dropdown
    await teamSelector.tap();

    // Should handle reduced height appropriately
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    const dropdown = page.locator('[cmdk-list]');
    const dropdownBox = await dropdown.boundingBox();

    // Should adjust max height for landscape
    expect(dropdownBox?.height).toBeLessThanOrEqual(200);

    await context.close();
  });

  test('should have touch-friendly target sizes', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Main button should be touch-friendly (minimum 44px)
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    const mainBox = await teamSelector.boundingBox();
    expect(mainBox?.height).toBeGreaterThanOrEqual(44);

    // Open dropdown and test a team selection
    await teamSelector.tap();
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Mock some teams being available
    const searchInput = page.getByPlaceholder('Search for teams...');
    await searchInput.tap();
    await searchInput.fill('Lakers');
    await page.waitForTimeout(500);

    // Team option buttons should be touch-friendly
    const teamOptions = page.locator('[cmdk-item]');
    if (await teamOptions.count() > 0) {
      const firstOption = teamOptions.first();
      const optionBox = await firstOption.boundingBox();
      expect(optionBox?.height).toBeGreaterThanOrEqual(44);
    }

    await context.close();
  });

  test('should handle virtual keyboard properly', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Open team selector
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    await teamSelector.tap();

    // Tap on search input to trigger virtual keyboard
    const searchInput = page.getByPlaceholder('Search for teams...');
    await searchInput.tap();

    // Virtual keyboard should not break the layout
    await expect(searchInput).toBeFocused();

    // The dropdown should still be visible and functional
    const dropdown = page.locator('[cmdk-list]');
    await expect(dropdown).toBeVisible();

    // Should be able to type
    await searchInput.fill('Lakers');
    await expect(searchInput).toHaveValue('Lakers');

    await context.close();
  });

  test('should handle text scaling accessibility', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12'],
    });
    const page = await context.newPage();

    // Simulate larger text sizes for accessibility
    await page.addStyleTag({
      content: `
        * {
          font-size: 1.2em !important;
        }
      `
    });

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Components should still work with larger text
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    await expect(teamSelector).toBeVisible();

    // Text should not overflow
    const box = await teamSelector.boundingBox();
    expect(box?.height).toBeGreaterThan(44); // Should grow to accommodate larger text

    // Open dropdown
    await teamSelector.tap();
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    // Dropdown should still be functional
    const searchInput = page.getByPlaceholder('Search for teams...');
    await expect(searchInput).toBeVisible();

    await context.close();
  });

  test('should work with one-handed use patterns', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Team selector should be reachable with thumb
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    const box = await teamSelector.boundingBox();

    // Should be in the lower portion of the screen for thumb reach
    const viewportSize = page.viewportSize();
    if (viewportSize) {
      const relativePosition = (box?.y || 0) / viewportSize.height;
      expect(relativePosition).toBeGreaterThan(0.3); // Should be below top 30% of screen
    }

    // Tap interactions should work reliably
    await teamSelector.tap();
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    await context.close();
  });

  test('should maintain performance on mobile', async ({ browser }) => {
    const context = await browser.newContext({
      ...devices['iPhone 12'],
    });
    const page = await context.newPage();

    await page.goto('/onboarding/step/3');
    await page.waitForLoadState('networkidle');

    // Measure interaction timing
    const startTime = Date.now();

    // Open dropdown
    const teamSelector = page.getByRole('combobox', { name: 'Select teams' });
    await teamSelector.tap();

    // Wait for dropdown to be visible
    await page.waitForSelector('[cmdk-list]', { state: 'visible' });

    const openTime = Date.now() - startTime;

    // Should open quickly on mobile (under 300ms)
    expect(openTime).toBeLessThan(300);

    // Test search performance
    const searchStartTime = Date.now();
    const searchInput = page.getByPlaceholder('Search for teams...');
    await searchInput.tap();
    await searchInput.fill('Lakers');

    // Wait for debounce
    await page.waitForTimeout(350);

    const searchTime = Date.now() - searchStartTime;

    // Search should complete within reasonable time (debounce + processing)
    expect(searchTime).toBeLessThan(800);

    await context.close();
  });
});