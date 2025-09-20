import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Enable console logging
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  try {
    console.log('Navigating to auth page...');
    await page.goto('http://localhost:8080/auth/sign-in', { waitUntil: 'networkidle' });

    console.log('Waiting for page to load...');
    await page.waitForTimeout(5000);

    console.log('Taking screenshot...');
    await page.screenshot({ path: 'debug-auth-page.png', fullPage: true });

    console.log('Checking page content...');
    const title = await page.title();
    console.log('Page title:', title);

    const bodyText = await page.textContent('body');
    console.log('Page text content:', bodyText?.substring(0, 500));

    const inputs = await page.$$eval('input', inputs => inputs.map(input => ({
      type: input.type,
      placeholder: input.placeholder,
      visible: input.offsetParent !== null
    })));
    console.log('Input elements:', inputs);

    const buttons = await page.$$eval('button', buttons => buttons.map(button => ({
      text: button.textContent,
      visible: button.offsetParent !== null
    })));
    console.log('Button elements:', buttons);

    const forms = await page.$$eval('form', forms => forms.length);
    console.log('Form elements count:', forms);

  } catch (error) {
    console.error('Error:', error);
  }

  await browser.close();
})();