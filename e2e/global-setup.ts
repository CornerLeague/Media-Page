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

    console.log('Global setup completed successfully');
  } catch (error) {
    console.error('Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;