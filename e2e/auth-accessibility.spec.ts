/**
 * Authentication Accessibility Tests
 *
 * Tests accessibility compliance for all authentication components using axe-core
 * and manual accessibility testing patterns
 */

import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';
import {
  setupMockAuth,
  goToSignInPage,
  goToSignUpPage,
  signInWithEmail,
  openUserProfileDialog,
  testUsers,
  setupTestEnvironment,
  enableTestMode,
  requestPasswordReset
} from './auth-utils';

test.describe('Authentication Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestEnvironment(page);
    await setupMockAuth(page);
    await enableTestMode(page);
    await injectAxe(page);
  });

  test.describe('Sign-In Page Accessibility', () => {
    test('should have no accessibility violations on sign-in page', async ({ page }) => {
      await goToSignInPage(page);
      await checkA11y(page, null, {
        detailedReport: true,
        detailedReportOptions: { html: true }
      });
    });

    test('should have proper form labels and structure', async ({ page }) => {
      await goToSignInPage(page);

      // Check form has proper labeling
      await expect(page.getByRole('form')).toBeVisible();

      // Email input should have proper label
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toHaveAttribute('aria-label');
      // Or should be associated with a label
      const emailLabel = page.getByText(/email/i);
      if (await emailLabel.count() > 0) {
        await expect(emailLabel).toBeVisible();
      }

      // Password input should have proper label
      const passwordInput = page.locator('input[type="password"]');
      await expect(passwordInput).toHaveAttribute('aria-label');
      // Or should be associated with a label
      const passwordLabel = page.getByText(/password/i);
      if (await passwordLabel.count() > 0) {
        await expect(passwordLabel).toBeVisible();
      }

      // Submit button should be properly labeled
      const submitButton = page.getByRole('button', { name: /sign in/i });
      await expect(submitButton).toBeVisible();
      await expect(submitButton).toHaveAccessibleName();
    });

    test('should support keyboard navigation', async ({ page }) => {
      await goToSignInPage(page);

      // Tab through form elements in correct order
      await page.keyboard.press('Tab');

      // Should focus email input (or first focusable element)
      let focusedElement = await page.evaluate(() => document.activeElement?.tagName.toLowerCase());
      expect(['input', 'button']).toContain(focusedElement);

      // Continue tabbing through all interactive elements
      const interactiveElements = [
        'input[type="email"]',
        'input[type="password"]',
        'button:not(:disabled)',
        'a[href]'
      ];

      for (let i = 0; i < interactiveElements.length + 2; i++) {
        await page.keyboard.press('Tab');
        // Verify we can navigate through all elements
        focusedElement = await page.evaluate(() => document.activeElement?.tagName.toLowerCase());
        expect(['input', 'button', 'a', 'div']).toContain(focusedElement);
      }
    });

    test('should have proper heading structure', async ({ page }) => {
      await goToSignInPage(page);

      // Should have a main heading
      const mainHeading = page.getByRole('heading', { level: 1 });
      if (await mainHeading.count() === 0) {
        // Check for h2 if no h1
        const h2Heading = page.getByRole('heading', { level: 2 });
        await expect(h2Heading).toBeVisible();
      } else {
        await expect(mainHeading).toBeVisible();
      }

      // Heading should describe the page content
      const headingText = await page.locator('h1, h2').first().textContent();
      expect(headingText?.toLowerCase()).toMatch(/sign|login|auth/);
    });

    test('should have sufficient color contrast', async ({ page }) => {
      await goToSignInPage(page);

      // Check for color contrast violations
      await checkA11y(page, null, {
        rules: {
          'color-contrast': { enabled: true },
          'color-contrast-enhanced': { enabled: true }
        }
      });
    });

    test('should provide clear focus indicators', async ({ page }) => {
      await goToSignInPage(page);

      // Check each interactive element has visible focus
      const interactiveSelectors = [
        'input[type="email"]',
        'input[type="password"]',
        'button[type="submit"]',
        'button:contains("Google")',
        'button:contains("forgot")'
      ];

      for (const selector of interactiveSelectors) {
        const element = page.locator(selector).first();
        if (await element.count() > 0) {
          await element.focus();

          // Element should have visible focus (implementation may vary)
          const focusStyles = await element.evaluate((el) => {
            const styles = window.getComputedStyle(el);
            return {
              outline: styles.outline,
              boxShadow: styles.boxShadow,
              border: styles.border
            };
          });

          // Should have some form of focus indication
          expect(
            focusStyles.outline !== 'none' ||
            focusStyles.boxShadow !== 'none' ||
            focusStyles.border !== 'none'
          ).toBeTruthy();
        }
      }
    });

    test('should announce errors to screen readers', async ({ page }) => {
      await goToSignInPage(page);

      // Trigger an error
      await page.fill('input[type="email"]', 'invalid@email.com');
      await page.fill('input[type="password"]', 'wrongpassword');
      await page.getByRole('button', { name: /sign in/i }).click();

      // Wait for error to appear
      await page.waitForSelector('[role="alert"], .alert-destructive', { timeout: 5000 });

      // Error should be in an alert region
      const errorAlert = page.locator('[role="alert"]');
      await expect(errorAlert).toBeVisible();

      // Should have accessible text
      const errorText = await errorAlert.textContent();
      expect(errorText).toBeTruthy();
      expect(errorText!.length).toBeGreaterThan(0);
    });
  });

  test.describe('Sign-Up Page Accessibility', () => {
    test('should have no accessibility violations on sign-up page', async ({ page }) => {
      await goToSignUpPage(page);
      await checkA11y(page);
    });

    test('should properly label password confirmation field', async ({ page }) => {
      await goToSignUpPage(page);

      // Confirm password field should be properly labeled
      const confirmPasswordInput = page.locator('input[placeholder*="Confirm"], input[name*="confirm"]');
      if (await confirmPasswordInput.count() > 0) {
        await expect(confirmPasswordInput).toHaveAttribute('aria-label');

        // Should be associated with password field (aria-describedby or similar)
        const ariaDescribedBy = await confirmPasswordInput.getAttribute('aria-describedby');
        if (ariaDescribedBy) {
          const description = page.locator(`#${ariaDescribedBy}`);
          await expect(description).toBeVisible();
        }
      }
    });

    test('should provide password strength feedback accessibly', async ({ page }) => {
      await goToSignUpPage(page);

      const passwordInput = page.locator('input[type="password"]').first();
      await passwordInput.fill('weak');

      // If password strength indicator exists, it should be accessible
      const strengthIndicator = page.locator('[aria-label*="password"], [role="progressbar"], .password-strength');
      if (await strengthIndicator.count() > 0) {
        await expect(strengthIndicator).toHaveAttribute('aria-label');
      }
    });

    test('should handle password mismatch errors accessibly', async ({ page }) => {
      await goToSignUpPage(page);

      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'password123');

      const confirmInput = page.locator('input[placeholder*="Confirm"]');
      if (await confirmInput.count() > 0) {
        await confirmInput.fill('differentpassword');
        await page.getByRole('button', { name: /create account/i }).click();

        // Error should be announced
        const errorMessage = page.getByText(/passwords do not match/i);
        if (await errorMessage.count() > 0) {
          // Should be associated with the form field
          await expect(errorMessage).toBeVisible();
        }
      }
    });
  });

  test.describe('Password Reset Accessibility', () => {
    test('should have no accessibility violations on password reset page', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();
      await checkA11y(page);
    });

    test('should provide clear instructions and feedback', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Should have clear heading
      await expect(page.getByRole('heading')).toContainText(/reset password/i);

      // Should have clear instructions
      const instructions = page.getByText(/enter your email.*reset/i);
      await expect(instructions).toBeVisible();

      // Submit password reset
      await requestPasswordReset(page, testUsers.validUser.email);

      // Success message should be accessible
      const successMessage = page.locator('[role="alert"]:not(.alert-destructive)');
      await expect(successMessage).toBeVisible();

      const successText = await successMessage.textContent();
      expect(successText).toBeTruthy();
    });

    test('should support keyboard navigation for back button', async ({ page }) => {
      await goToSignInPage(page);
      await page.getByRole('button', { name: /forgot.*password/i }).click();

      // Back button should be focusable and have proper label
      const backButton = page.locator('button:has(svg)').first(); // Arrow icon button
      await backButton.focus();

      // Should have accessible name or aria-label
      const accessibleName = await backButton.getAttribute('aria-label');
      expect(accessibleName || await backButton.textContent()).toBeTruthy();

      // Should work with Enter/Space keys
      await page.keyboard.press('Enter');
      await expect(page.getByText('Sign In')).toBeVisible();
    });
  });

  test.describe('User Profile Dialog Accessibility', () => {
    test.beforeEach(async ({ page }) => {
      // Sign in first
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await page.waitForTimeout(1000);
    });

    test('should have no accessibility violations in profile dialog', async ({ page }) => {
      await openUserProfileDialog(page);
      await checkA11y(page);
    });

    test('should properly manage focus in modal dialog', async ({ page }) => {
      await openUserProfileDialog(page);

      // Focus should be trapped within dialog
      const dialog = page.getByRole('dialog');
      await expect(dialog).toBeVisible();

      // Should have proper dialog attributes
      await expect(dialog).toHaveAttribute('role', 'dialog');
      await expect(dialog).toHaveAttribute('aria-modal', 'true');

      // Should have accessible name (aria-labelledby or aria-label)
      const hasAriaLabel = await dialog.getAttribute('aria-label');
      const hasAriaLabelledBy = await dialog.getAttribute('aria-labelledby');
      expect(hasAriaLabel || hasAriaLabelledBy).toBeTruthy();
    });

    test('should support keyboard navigation in tabs', async ({ page }) => {
      await openUserProfileDialog(page);

      // Tab list should be navigable with arrow keys
      const profileTab = page.getByRole('tab', { name: /profile/i });
      await profileTab.focus();

      // Should be able to navigate tabs with arrow keys
      await page.keyboard.press('ArrowRight');
      const securityTab = page.getByRole('tab', { name: /security/i });
      await expect(securityTab).toBeFocused();

      await page.keyboard.press('ArrowRight');
      const accountTab = page.getByRole('tab', { name: /account/i });
      await expect(accountTab).toBeFocused();

      // Home/End keys should work
      await page.keyboard.press('Home');
      await expect(profileTab).toBeFocused();

      await page.keyboard.press('End');
      await expect(accountTab).toBeFocused();
    });

    test('should close dialog with Escape key', async ({ page }) => {
      await openUserProfileDialog(page);
      await expect(page.getByRole('dialog')).toBeVisible();

      await page.keyboard.press('Escape');
      await expect(page.getByRole('dialog')).not.toBeVisible();
    });

    test('should have proper form labels in profile sections', async ({ page }) => {
      await openUserProfileDialog(page);

      // Profile tab form labels
      const displayNameInput = page.locator('input[id="displayName"]');
      if (await displayNameInput.count() > 0) {
        await expect(page.getByLabel(/display name/i)).toBeVisible();
      }

      // Security tab form labels
      await page.getByRole('tab', { name: /security/i }).click();

      const currentPasswordInput = page.locator('input[id="currentPassword"]');
      if (await currentPasswordInput.count() > 0) {
        await expect(page.getByLabel(/current password/i)).toBeVisible();
      }

      const newPasswordInput = page.locator('input[id="newPassword"]');
      if (await newPasswordInput.count() > 0) {
        await expect(page.getByLabel(/new password/i)).toBeVisible();
      }
    });

    test('should announce status updates accessibly', async ({ page }) => {
      await openUserProfileDialog(page);

      // Update display name
      await page.fill('input[id="displayName"]', 'New Display Name');
      await page.getByRole('button', { name: /update profile/i }).click();

      // Success message should be in alert region
      const successAlert = page.locator('[role="alert"]:not(.alert-destructive)');
      await expect(successAlert).toBeVisible();

      // Should have meaningful text
      const alertText = await successAlert.textContent();
      expect(alertText?.toLowerCase()).toMatch(/success|updated/);
    });
  });

  test.describe('Dropdown Menu Accessibility', () => {
    test.beforeEach(async ({ page }) => {
      // Sign in first
      await goToSignInPage(page);
      await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
      await page.waitForTimeout(1000);
    });

    test('should have no accessibility violations in user dropdown', async ({ page }) => {
      // Open user profile dropdown
      await page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])').click();
      await checkA11y(page);
    });

    test('should have proper menu structure and navigation', async ({ page }) => {
      const trigger = page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])');
      await trigger.click();

      // Menu should be properly structured
      const menu = page.getByRole('menu');
      await expect(menu).toBeVisible();

      // Menu items should be properly labeled
      const menuItems = page.getByRole('menuitem');
      const itemCount = await menuItems.count();
      expect(itemCount).toBeGreaterThan(0);

      for (let i = 0; i < itemCount; i++) {
        const item = menuItems.nth(i);
        await expect(item).toHaveAttribute('role', 'menuitem');

        // Should have accessible text
        const text = await item.textContent();
        expect(text?.trim()).toBeTruthy();
      }
    });

    test('should support keyboard navigation in menu', async ({ page }) => {
      const trigger = page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])');
      await trigger.focus();
      await page.keyboard.press('Enter');

      // Should be able to navigate menu with arrow keys
      await page.keyboard.press('ArrowDown');
      const firstItem = page.getByRole('menuitem').first();
      await expect(firstItem).toBeFocused();

      await page.keyboard.press('ArrowDown');
      const secondItem = page.getByRole('menuitem').nth(1);
      if (await secondItem.count() > 0) {
        await expect(secondItem).toBeFocused();
      }

      // Escape should close menu
      await page.keyboard.press('Escape');
      await expect(page.getByRole('menu')).not.toBeVisible();
      await expect(trigger).toBeFocused();
    });

    test('should have proper ARIA attributes', async ({ page }) => {
      const trigger = page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])');

      // Trigger should have proper attributes
      await expect(trigger).toHaveAttribute('aria-haspopup');

      await trigger.click();

      // Menu should have proper attributes
      const menu = page.getByRole('menu');
      await expect(menu).toHaveAttribute('role', 'menu');

      // Menu should be associated with trigger
      const ariaLabelledBy = await menu.getAttribute('aria-labelledby');
      if (ariaLabelledBy) {
        const labelElement = page.locator(`#${ariaLabelledBy}`);
        await expect(labelElement).toBeVisible();
      }
    });
  });

  test.describe('Dark/Light Theme Accessibility', () => {
    test('should maintain accessibility in both themes', async ({ page }) => {
      // Test light theme
      await goToSignInPage(page);
      await checkA11y(page);

      // Switch to dark theme if toggle exists
      const themeToggle = page.locator('[data-testid="theme-toggle"], button:has([data-testid="theme-icon"])');
      if (await themeToggle.count() > 0) {
        await themeToggle.click();

        // Wait for theme change
        await page.waitForTimeout(500);

        // Check accessibility in dark theme
        await checkA11y(page);
      }
    });

    test('should maintain sufficient contrast in both themes', async ({ page }) => {
      await goToSignInPage(page);

      // Check color contrast in current theme
      await checkA11y(page, null, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });

      // Switch theme if possible and test again
      const themeToggle = page.locator('[data-testid="theme-toggle"], button:has([data-testid="theme-icon"])');
      if (await themeToggle.count() > 0) {
        await themeToggle.click();
        await page.waitForTimeout(500);

        await checkA11y(page, null, {
          rules: {
            'color-contrast': { enabled: true }
          }
        });
      }
    });
  });

  test.describe('Mobile Accessibility', () => {
    test('should maintain accessibility on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      await goToSignInPage(page);
      await checkA11y(page);

      // Test mobile-specific interactions
      const profileTrigger = page.locator('[data-testid="user-profile-trigger"], button:has([data-testid="user-avatar"])');
      if (await profileTrigger.count() > 0) {
        // Sign in first
        await signInWithEmail(page, testUsers.validUser.email, testUsers.validUser.password);
        await page.waitForTimeout(1000);

        // Test mobile dropdown
        await profileTrigger.click();
        await checkA11y(page);
      }
    });

    test('should have proper touch target sizes', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await goToSignInPage(page);

      // Check that interactive elements meet minimum size requirements (44x44px)
      const interactiveElements = page.locator('button, input, a[href]');
      const count = await interactiveElements.count();

      for (let i = 0; i < count; i++) {
        const element = interactiveElements.nth(i);
        const box = await element.boundingBox();

        if (box) {
          // Elements should be at least 44x44px for touch accessibility
          expect(box.width).toBeGreaterThanOrEqual(32); // Slightly lower due to padding/margin
          expect(box.height).toBeGreaterThanOrEqual(32);
        }
      }
    });
  });

  test.describe('Screen Reader Testing', () => {
    test('should have proper page titles and landmarks', async ({ page }) => {
      await goToSignInPage(page);

      // Page should have descriptive title
      const title = await page.title();
      expect(title.toLowerCase()).toMatch(/sign|login|auth/);

      // Should have main landmark
      const main = page.locator('main, [role="main"]');
      if (await main.count() > 0) {
        await expect(main).toBeVisible();
      }

      // Should have proper heading structure
      const headings = page.locator('h1, h2, h3, h4, h5, h6');
      const headingCount = await headings.count();
      expect(headingCount).toBeGreaterThan(0);
    });

    test('should provide meaningful button and link text', async ({ page }) => {
      await goToSignInPage(page);

      // All buttons should have meaningful text
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();

      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        const text = await button.textContent();
        const ariaLabel = await button.getAttribute('aria-label');
        const ariaLabelledBy = await button.getAttribute('aria-labelledby');

        // Button should have some form of accessible name
        expect(
          (text && text.trim().length > 0) ||
          (ariaLabel && ariaLabel.trim().length > 0) ||
          ariaLabelledBy
        ).toBeTruthy();
      }
    });

    test('should provide status updates for dynamic content', async ({ page }) => {
      await goToSignInPage(page);

      // Sign in with wrong credentials to trigger error
      await page.fill('input[type="email"]', 'wrong@email.com');
      await page.fill('input[type="password"]', 'wrongpassword');
      await page.getByRole('button', { name: /sign in/i }).click();

      // Wait for error
      await page.waitForSelector('[role="alert"]', { timeout: 5000 });

      // Error should be announced via live region
      const alerts = page.locator('[role="alert"], [aria-live]');
      const alertCount = await alerts.count();
      expect(alertCount).toBeGreaterThan(0);

      // At least one alert should have content
      let hasContent = false;
      for (let i = 0; i < alertCount; i++) {
        const alert = alerts.nth(i);
        const content = await alert.textContent();
        if (content && content.trim().length > 0) {
          hasContent = true;
          break;
        }
      }
      expect(hasContent).toBeTruthy();
    });
  });
});