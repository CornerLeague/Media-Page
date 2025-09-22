/**
 * Playwright base test with enhanced axe-core initialization
 *
 * This fixture ensures axe-core is pre-loaded globally for all accessibility tests,
 * providing better performance and consistency while maintaining all the robust
 * error handling from the axe-helper utility.
 */

import { test as base, Page } from '@playwright/test';

interface AxeFixtures {
  axePage: Page;
}

/**
 * Enhanced page fixture that pre-loads axe-core globally
 */
export const test = base.extend<AxeFixtures>({
  axePage: async ({ page }, use) => {
    // Add init script to pre-load axe-core for every page in this test
    await page.addInitScript(() => {
      // Mark that global axe setup was attempted for this page
      (window as any).__AXE_GLOBAL_SETUP__ = true;

      // Pre-load axe-core immediately when page loads
      if (typeof (window as any).axe === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/axe-core@4.10.2/axe.min.js';
        script.async = false; // Load synchronously to ensure availability
        script.onload = () => {
          console.log('✓ axe-core pre-loaded via fixture');
          (window as any).__AXE_GLOBAL_LOADED__ = true;
        };
        script.onerror = () => {
          console.warn('Global axe-core pre-loading failed via fixture - fallback will be used');
          (window as any).__AXE_GLOBAL_FAILED__ = true;
        };

        // Add to head immediately
        if (document.head) {
          document.head.appendChild(script);
        } else {
          // If head doesn't exist yet, wait for it
          const observer = new MutationObserver(() => {
            if (document.head) {
              document.head.appendChild(script);
              observer.disconnect();
            }
          });
          observer.observe(document, { childList: true, subtree: true });
        }
      } else {
        (window as any).__AXE_GLOBAL_LOADED__ = true;
      }
    });

    await use(page);
  },
});

export { expect } from '@playwright/test';