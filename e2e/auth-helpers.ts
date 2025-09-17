import { Page } from '@playwright/test';

/**
 * Mock authentication state for E2E tests
 * This bypasses Clerk authentication by setting up a mock user session
 */
export async function mockAuthenticatedUser(page: Page) {
  // Mock the Clerk user and auth state by injecting into the browser
  await page.addInitScript(() => {
    // Mock localStorage items that Clerk might use
    const mockUser = {
      id: 'test-user-id',
      firstName: 'Test',
      lastName: 'User',
      primaryEmailAddress: { emailAddress: 'test@example.com' },
    };

    // Mock the auth state
    localStorage.setItem('__clerk_client_jwt', JSON.stringify({
      jwt: 'mock-jwt-token',
      exp: Date.now() + 86400000, // 24 hours from now
    }));

    // Set up window variables that might be used
    (window as any).__CLERK_TEST_MODE__ = true;
    (window as any).__CLERK_MOCK_USER__ = mockUser;
  });
}

/**
 * Navigate to a protected route with authentication
 */
export async function authenticatedGoto(page: Page, url: string) {
  await mockAuthenticatedUser(page);
  await page.goto(url);

  // Wait for authentication to be processed
  await page.waitForTimeout(1000);
}

/**
 * Clear authentication state
 */
export async function clearAuthState(page: Page) {
  await page.evaluate(() => {
    localStorage.removeItem('__clerk_client_jwt');
    sessionStorage.clear();
  });
}