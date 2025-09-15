import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // Clear any existing test data
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Clear localStorage and sessionStorage
  await page.goto(config.projects[0].use.baseURL || 'http://localhost:8080');
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  await browser.close();
}

export default globalSetup;