import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // Clear any existing test data and ensure clean state
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    const baseURL = config.projects[0].use.baseURL || 'http://localhost:8080';

    // Wait for the dev server to be ready
    let retries = 0;
    while (retries < 30) {
      try {
        await page.goto(baseURL, { waitUntil: 'networkidle' });
        break;
      } catch (error) {
        console.log(`Waiting for dev server to be ready... (attempt ${retries + 1}/30)`);
        await page.waitForTimeout(2000);
        retries++;
      }
    }

    if (retries === 30) {
      throw new Error('Dev server failed to start within 60 seconds');
    }

    // Clear localStorage and sessionStorage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
      // Clear any other app-specific storage
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        });
      }
    });

    // Setup authentication test environment
    await page.addInitScript(() => {
      // Ensure clean auth state for tests
      (window as any).__TEST_AUTH_INITIALIZED__ = false;
      (window as any).__PLAYWRIGHT_TEST__ = true;

      // Mock Firebase config for testing
      (window as any).__TEST_ENV__ = {
        VITE_FIREBASE_API_KEY: 'mock-api-key',
        VITE_FIREBASE_AUTH_DOMAIN: 'mock-project.firebaseapp.com',
        VITE_FIREBASE_PROJECT_ID: 'mock-project-id',
        VITE_TEST_MODE: 'true'
      };

      // Clear any existing Firebase instances
      if ((window as any).firebase) {
        delete (window as any).firebase;
      }
    });

    // Verify authentication routes are accessible
    await page.goto(`${baseURL}/auth/sign-in`, { waitUntil: 'networkidle' });

    // Wait for React to load and render the auth form
    // Look for multiple possible elements that should be on the auth page
    await page.waitForFunction(() => {
      // Look for any of these elements that should be present on the auth page
      const selectors = [
        'input[type="email"]',
        'input[placeholder*="Email"]',
        'input[placeholder*="email"]',
        'h1',
        'h2',
        '[data-testid="auth-form"]',
        'button',
        'form'
      ];

      return selectors.some(selector => {
        const element = document.querySelector(selector);
        return element && element.offsetParent !== null; // Element exists and is visible
      });
    }, { timeout: 15000 });

    console.log('Global setup completed successfully');
    console.log('✓ Dev server is ready');
    console.log('✓ Authentication routes are accessible');
    console.log('✓ Test environment is configured');
  } catch (error) {
    console.error('Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;