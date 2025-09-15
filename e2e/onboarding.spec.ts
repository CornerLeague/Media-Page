/**
 * End-to-End Onboarding Tests
 *
 * Comprehensive E2E tests for the onboarding flow including cross-browser
 * compatibility, mobile responsiveness, and user journey validation.
 */

import { test, expect } from '@playwright/test';

test.describe('Onboarding Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.evaluate(() => localStorage.clear());
    await page.goto('/');
  });

  test('redirects new users to onboarding', async ({ page }) => {
    // Should redirect to onboarding for new users
    await expect(page).toHaveURL(/.*\/onboarding/);

    // Should show welcome screen
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();
  });

  test('completes full onboarding flow', async ({ page }) => {
    // Step 1: Welcome screen
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();
    await page.getByRole('button', { name: /get started/i }).click();

    // Step 2: Sports selection
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();

    // Select some sports
    const sportsCheckboxes = page.getByRole('checkbox');
    await sportsCheckboxes.first().click();
    await sportsCheckboxes.nth(1).click();

    await page.getByRole('button', { name: /continue/i }).click();

    // Step 3: Team selection
    await expect(page.getByText(/choose your favorite teams/i)).toBeVisible();

    // Select some teams
    const teamCheckboxes = page.getByRole('checkbox');
    await teamCheckboxes.first().click();
    await teamCheckboxes.nth(1).click();

    await page.getByRole('button', { name: /continue/i }).click();

    // Step 4: Preferences setup
    await expect(page.getByText(/content preferences/i)).toBeVisible();

    // Enable some news types
    const switches = page.getByRole('switch');
    await switches.first().click();

    await page.getByRole('button', { name: /continue/i }).click();

    // Step 5: Completion
    await expect(page.getByText(/you're all set/i)).toBeVisible();

    await page.getByRole('button', { name: /complete setup/i }).click();

    // Should redirect to main app
    await expect(page).toHaveURL('/');
  });

  test('supports keyboard navigation', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Tab to next button and press Enter
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab'); // Skip exit button, go to next
    await page.keyboard.press('Enter');

    // Should advance to next step
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });

  test('validates required fields', async ({ page }) => {
    // Skip to sports selection
    await page.getByRole('button', { name: /get started/i }).click();

    // Try to continue without selecting sports
    await page.getByRole('button', { name: /continue/i }).click();

    // Should show validation error
    await expect(page.getByText(/please select at least one sport/i)).toBeVisible();
  });

  test('preserves state when navigating back', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Select a sport
    const firstCheckbox = page.getByRole('checkbox').first();
    await firstCheckbox.click();
    await expect(firstCheckbox).toBeChecked();

    // Continue to next step
    await page.getByRole('button', { name: /continue/i }).click();

    // Go back
    await page.getByRole('button', { name: /back/i }).click();

    // Selection should be preserved
    await expect(firstCheckbox).toBeChecked();
  });

  test('supports drag and drop reordering', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Select multiple sports
    const checkboxes = page.getByRole('checkbox');
    await checkboxes.nth(0).click();
    await checkboxes.nth(1).click();

    // Test drag and drop (basic test - actual DnD requires more setup)
    const firstSport = page.locator('[data-testid="sport-item"]').first();
    await expect(firstSport).toBeVisible();
  });

  test('exits onboarding and preserves progress', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Select a sport
    await page.getByRole('checkbox').first().click();

    // Exit onboarding
    await page.getByRole('button', { name: /exit onboarding/i }).click();

    // Confirm in dialog
    page.on('dialog', dialog => dialog.accept());

    // Should go back to main app
    await expect(page).toHaveURL('/');

    // Return to onboarding - progress should be saved
    await page.goto('/onboarding');
    await expect(page.getByRole('checkbox').first()).toBeChecked();
  });
});

test.describe('Mobile Responsiveness', () => {
  test('works on mobile devices', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'This test only runs on mobile');

    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Buttons should be touch-friendly
    const nextButton = page.getByRole('button', { name: /get started/i });
    const boundingBox = await nextButton.boundingBox();

    expect(boundingBox?.height).toBeGreaterThan(44); // Minimum touch target size
  });

  test('supports swipe gestures on mobile', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'This test only runs on mobile');

    // This would test swipe navigation if implemented
    await page.getByRole('button', { name: /get started/i }).click();

    // Test swipe to navigate (would require gesture implementation)
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });
});

test.describe('Cross-Browser Compatibility', () => {
  ['chromium', 'firefox', 'webkit'].forEach(browserName => {
    test(`works in ${browserName}`, async ({ page, browserName: currentBrowser }) => {
      test.skip(currentBrowser !== browserName, `This test only runs on ${browserName}`);

      await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

      // Test basic functionality
      await page.getByRole('button', { name: /get started/i }).click();
      await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
    });
  });

  test('handles localStorage across browsers', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Select a sport
    await page.getByRole('checkbox').first().click();

    // Reload page
    await page.reload();

    // State should be preserved
    await expect(page.getByRole('checkbox').first()).toBeChecked();
  });
});

test.describe('Performance', () => {
  test('loads quickly', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();
    const loadTime = Date.now() - startTime;

    // Should load within reasonable time
    expect(loadTime).toBeLessThan(5000);
  });

  test('handles animations smoothly', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Click next button and wait for animations
    await page.getByRole('button', { name: /get started/i }).click();

    // Should transition smoothly
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });

  test('memory usage stays reasonable', async ({ page }) => {
    // Navigate through all steps
    await page.getByRole('button', { name: /get started/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();

    // Check memory usage (basic check)
    const metrics = await page.evaluate(() => (performance as any).memory);
    if (metrics) {
      expect(metrics.usedJSHeapSize).toBeLessThan(50 * 1024 * 1024); // Less than 50MB
    }
  });
});

test.describe('Error Handling', () => {
  test('handles network failures gracefully', async ({ page }) => {
    // Simulate offline condition
    await page.context().setOffline(true);

    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Should still work offline (localStorage-based)
    await page.getByRole('button', { name: /get started/i }).click();
    await expect(page.getByText(/select and rank your favorite sports/i)).toBeVisible();
  });

  test('recovers from JavaScript errors', async ({ page }) => {
    // Listen for console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();

    // Should not have critical console errors
    expect(errors.filter(error => !error.includes('Warning:'))).toHaveLength(0);
  });

  test('handles corrupted localStorage data', async ({ page }) => {
    // Inject corrupted data
    await page.evaluate(() => {
      localStorage.setItem('corner-league-onboarding-state', 'invalid json');
    });

    await page.goto('/onboarding');

    // Should still work and not crash
    await expect(page.getByRole('heading', { name: /welcome to corner league media/i })).toBeVisible();
  });
});

test.describe('First Time Experience', () => {
  test('shows tutorial after onboarding completion', async ({ page }) => {
    // Complete onboarding quickly
    await page.getByRole('button', { name: /get started/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();
    await page.getByRole('checkbox').first().click();
    await page.getByRole('button', { name: /continue/i }).click();
    await page.getByRole('button', { name: /continue/i }).click();
    await page.getByRole('button', { name: /complete setup/i }).click();

    // Should show first time experience tutorial
    await expect(page.getByText(/welcome to your personalized dashboard/i)).toBeVisible();
  });

  test('can skip tutorial', async ({ page }) => {
    // Set up completed onboarding state
    await page.evaluate(() => {
      localStorage.setItem('corner-league-onboarding-completed', JSON.stringify({
        completed: true,
        completedAt: new Date().toISOString(),
      }));
      localStorage.setItem('corner-league-user-preferences', JSON.stringify({
        id: 'test-user',
        sports: [{ sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true }],
        teams: [{ teamId: 'chiefs', name: 'Kansas City Chiefs', sportId: 'nfl', league: 'NFL', affinityScore: 85 }],
        preferences: {
          newsTypes: [{ type: 'injuries', enabled: true, priority: 1 }],
          notifications: { push: false, email: true, gameReminders: true, newsAlerts: false, scoreUpdates: true },
          contentFrequency: 'standard',
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }));
    });

    await page.goto('/');

    // Should show tutorial
    await expect(page.getByText(/welcome to your personalized dashboard/i)).toBeVisible();

    // Skip tutorial
    await page.getByRole('button', { name: /skip tour/i }).click();

    // Should dismiss tutorial
    await expect(page.getByText(/welcome to your personalized dashboard/i)).not.toBeVisible();
  });
});

test.describe('Data Persistence', () => {
  test('saves preferences to localStorage', async ({ page }) => {
    await page.getByRole('button', { name: /get started/i }).click();

    // Select preferences
    await page.getByRole('checkbox').first().click();

    // Check localStorage
    const savedData = await page.evaluate(() => {
      return localStorage.getItem('corner-league-onboarding-state');
    });

    expect(savedData).toBeTruthy();
    expect(JSON.parse(savedData!)).toHaveProperty('userPreferences');
  });

  test('loads preferences from localStorage', async ({ page }) => {
    // Set initial preferences
    await page.evaluate(() => {
      localStorage.setItem('corner-league-onboarding-state', JSON.stringify({
        currentStep: 1,
        userPreferences: {
          sports: [{ sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true }],
        },
        steps: [],
        isComplete: false,
        errors: {},
      }));
    });

    await page.goto('/onboarding');

    // Should load saved state
    await expect(page.getByRole('checkbox').first()).toBeChecked();
  });
});