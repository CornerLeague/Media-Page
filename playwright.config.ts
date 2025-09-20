import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './e2e',

  /* Run tests in files in parallel */
  fullyParallel: true,

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/playwright-report.json' }],
    ['junit', { outputFile: 'test-results/playwright-results.xml' }],
    ...(process.env.CI ? [['github']] : []),
  ],

  /* Output directory for test artifacts */
  outputDir: 'test-results/',

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:8080',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Take screenshot on failure */
    screenshot: 'only-on-failure',

    /* Capture video on failure */
    video: 'retain-on-failure',

    /* Global test timeout */
    actionTimeout: 10000,
    navigationTimeout: 30000,

    /* Enable JavaScript and ignore HTTPS errors */
    javaScriptEnabled: true,
    ignoreHTTPSErrors: true,

    /* Set viewport size */
    viewport: { width: 1280, height: 720 },
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        /* Extra time for React hydration */
        actionTimeout: 15000,
      },
    },

    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        /* Extra time for React hydration */
        actionTimeout: 15000,
      },
    },

    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        /* Extra time for React hydration */
        actionTimeout: 15000,
      },
    },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: {
        ...devices['Pixel 5'],
        /* Extra time for React hydration on mobile */
        actionTimeout: 20000,
      },
    },
    {
      name: 'Mobile Safari',
      use: {
        ...devices['iPhone 12'],
        /* Extra time for React hydration on mobile */
        actionTimeout: 20000,
      },
    },

    /* Accessibility testing project - runs only accessibility tests */
    {
      name: 'accessibility',
      use: {
        ...devices['Desktop Chrome'],
        /* More time for accessibility scans */
        actionTimeout: 30000,
        /* Ensure consistent rendering for a11y tests */
        viewport: { width: 1280, height: 720 },
      },
      testMatch: '**/accessibility*.spec.ts',
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    /* Wait for server to be ready */
    stdout: 'pipe',
    stderr: 'pipe',
    /* Kill server on exit */
    ignoreHTTPSErrors: true,
  },

  /* Global setup and teardown */
  globalSetup: './e2e/global-setup.ts',

  /* Test timeout - increased for React hydration */
  timeout: 60 * 1000,
  expect: {
    timeout: 10 * 1000,
  },

  /* Test isolation */
  preserveOutput: 'failures-only',
});