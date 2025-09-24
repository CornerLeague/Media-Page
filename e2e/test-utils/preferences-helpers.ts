/**
 * Preferences Step Test Utilities
 * Specialized helpers for preferences configuration testing
 */

import { Page, Locator, expect } from '@playwright/test';
import { WaitStrategies } from './wait-strategies';

export interface NewsTypePreferences {
  injuries: boolean;
  trades: boolean;
  scores: boolean;
  analysis: boolean;
  rumors: boolean;
  standings: boolean;
}

export interface NotificationPreferences {
  push: boolean;
  email: boolean;
  sms: boolean;
  inApp: boolean;
}

export interface ContentPreferences {
  frequency: 'minimal' | 'standard' | 'comprehensive';
  gameAlerts: boolean;
  breakingNews: boolean;
  dailyDigest: boolean;
}

export interface PreferencesData {
  newsTypes: Partial<NewsTypePreferences>;
  notifications: Partial<NotificationPreferences>;
  content: Partial<ContentPreferences>;
}

/**
 * Preferences Test Helper Class
 */
export class PreferencesTestHelpers {
  private waitStrategies: WaitStrategies;

  constructor(private page: Page) {
    this.waitStrategies = new WaitStrategies(page);
  }

  // Element getters - News Types section
  get newsTypesSection(): Locator {
    return this.page.locator('[data-testid="news-types-section"]');
  }

  getNewsTypeSwitch(newsType: keyof NewsTypePreferences): Locator {
    return this.page.locator(`label[for="${newsType}"]`);
  }

  getNewsTypeToggle(newsType: keyof NewsTypePreferences): Locator {
    return this.page.locator(`input[id="${newsType}"]`);
  }

  // Element getters - Notifications section
  get notificationsSection(): Locator {
    return this.page.locator('[data-testid="notifications-section"]');
  }

  getNotificationSwitch(notificationType: keyof NotificationPreferences): Locator {
    return this.page.locator(`label[for="${notificationType}"]`);
  }

  getNotificationToggle(notificationType: keyof NotificationPreferences): Locator {
    return this.page.locator(`input[id="${notificationType}"]`);
  }

  // Element getters - Content Frequency section
  get contentFrequencySection(): Locator {
    return this.page.locator('[data-testid="content-frequency-section"]');
  }

  get contentFrequencyRadios(): Locator {
    return this.page.locator('input[name="contentFrequency"]');
  }

  getContentFrequencyRadio(frequency: ContentPreferences['frequency']): Locator {
    return this.page.locator(`input[value="${frequency}"]`);
  }

  // Element getters - Additional preferences
  get gameAlertsToggle(): Locator {
    return this.page.locator('input[id="gameAlerts"]');
  }

  get breakingNewsToggle(): Locator {
    return this.page.locator('input[id="breakingNews"]');
  }

  get dailyDigestToggle(): Locator {
    return this.page.locator('input[id="dailyDigest"]');
  }

  // Validation elements
  get preferencesForm(): Locator {
    return this.page.locator('form, [data-testid="preferences-form"]');
  }

  get loadingIndicator(): Locator {
    return this.page.locator('[data-testid="preferences-loading"]');
  }

  get errorMessage(): Locator {
    return this.page.locator('[data-testid="preferences-error"]');
  }

  // Wait for page to load
  async waitForPreferencesToLoad(timeout: number = 10000): Promise<void> {
    try {
      // Wait for main form elements to be visible
      await this.waitStrategies.waitForElement(this.preferencesForm, 'visible', timeout);

      // Wait for at least one radio button to be visible (content frequency)
      await this.waitStrategies.waitForElement(
        this.contentFrequencyRadios.first(),
        'visible',
        timeout
      );

      // Additional wait for form to be fully interactive
      await this.page.waitForTimeout(300);
    } catch (error) {
      // Check if there's an error or loading state
      if (await this.loadingIndicator.isVisible()) {
        await this.waitStrategies.waitForElement(this.preferencesForm, 'visible', timeout + 5000);
      } else {
        throw error;
      }
    }
  }

  // News Types actions
  async toggleNewsType(newsType: keyof NewsTypePreferences): Promise<void> {
    await this.waitForPreferencesToLoad();

    const switchElement = this.getNewsTypeSwitch(newsType);
    await this.waitStrategies.waitForElement(switchElement, 'visible');
    await switchElement.click();
    await this.page.waitForTimeout(200); // Wait for state change
  }

  async setNewsType(newsType: keyof NewsTypePreferences, enabled: boolean): Promise<void> {
    const currentState = await this.isNewsTypeEnabled(newsType);
    if (currentState !== enabled) {
      await this.toggleNewsType(newsType);
    }
  }

  async isNewsTypeEnabled(newsType: keyof NewsTypePreferences): Promise<boolean> {
    try {
      const toggle = this.getNewsTypeToggle(newsType);
      return await toggle.isChecked();
    } catch {
      // Fallback: check switch state via aria attributes
      const switchElement = this.getNewsTypeSwitch(newsType);
      const ariaChecked = await switchElement.getAttribute('aria-checked');
      return ariaChecked === 'true';
    }
  }

  async setMultipleNewsTypes(newsTypes: Partial<NewsTypePreferences>): Promise<void> {
    for (const [newsType, enabled] of Object.entries(newsTypes)) {
      await this.setNewsType(newsType as keyof NewsTypePreferences, enabled as boolean);
    }
  }

  // Notification actions
  async toggleNotification(notificationType: keyof NotificationPreferences): Promise<void> {
    await this.waitForPreferencesToLoad();

    const switchElement = this.getNotificationSwitch(notificationType);
    await this.waitStrategies.waitForElement(switchElement, 'visible');
    await switchElement.click();
    await this.page.waitForTimeout(200);
  }

  async setNotification(notificationType: keyof NotificationPreferences, enabled: boolean): Promise<void> {
    const currentState = await this.isNotificationEnabled(notificationType);
    if (currentState !== enabled) {
      await this.toggleNotification(notificationType);
    }
  }

  async isNotificationEnabled(notificationType: keyof NotificationPreferences): Promise<boolean> {
    try {
      const toggle = this.getNotificationToggle(notificationType);
      return await toggle.isChecked();
    } catch {
      const switchElement = this.getNotificationSwitch(notificationType);
      const ariaChecked = await switchElement.getAttribute('aria-checked');
      return ariaChecked === 'true';
    }
  }

  async setMultipleNotifications(notifications: Partial<NotificationPreferences>): Promise<void> {
    for (const [notificationType, enabled] of Object.entries(notifications)) {
      await this.setNotification(notificationType as keyof NotificationPreferences, enabled as boolean);
    }
  }

  // Content Frequency actions
  async selectContentFrequency(frequency: ContentPreferences['frequency']): Promise<void> {
    await this.waitForPreferencesToLoad();

    const radio = this.getContentFrequencyRadio(frequency);
    await this.waitStrategies.waitForElement(radio, 'visible');
    await radio.click();
    await this.page.waitForTimeout(200);
  }

  async getSelectedContentFrequency(): Promise<ContentPreferences['frequency'] | null> {
    const frequencies: ContentPreferences['frequency'][] = ['minimal', 'standard', 'comprehensive'];

    for (const frequency of frequencies) {
      const radio = this.getContentFrequencyRadio(frequency);
      if (await radio.isChecked()) {
        return frequency;
      }
    }

    return null;
  }

  // Additional preference actions
  async toggleGameAlerts(): Promise<void> {
    if (await this.gameAlertsToggle.isVisible({ timeout: 1000 }).catch(() => false)) {
      await this.gameAlertsToggle.click();
      await this.page.waitForTimeout(200);
    } else {
      console.warn('Game alerts toggle not found in current UI');
    }
  }

  async toggleBreakingNews(): Promise<void> {
    if (await this.breakingNewsToggle.isVisible({ timeout: 1000 }).catch(() => false)) {
      await this.breakingNewsToggle.click();
      await this.page.waitForTimeout(200);
    } else {
      console.warn('Breaking news toggle not found in current UI');
    }
  }

  async toggleDailyDigest(): Promise<void> {
    if (await this.dailyDigestToggle.isVisible({ timeout: 1000 }).catch(() => false)) {
      await this.dailyDigestToggle.click();
      await this.page.waitForTimeout(200);
    } else {
      console.warn('Daily digest toggle not found in current UI');
    }
  }

  // Bulk preference setting
  async setAllPreferences(preferences: PreferencesData): Promise<void> {
    // Set news type preferences
    if (preferences.newsTypes) {
      await this.setMultipleNewsTypes(preferences.newsTypes);
    }

    // Set notification preferences
    if (preferences.notifications) {
      await this.setMultipleNotifications(preferences.notifications);
    }

    // Set content preferences
    if (preferences.content) {
      if (preferences.content.frequency) {
        await this.selectContentFrequency(preferences.content.frequency);
      }

      if (preferences.content.gameAlerts !== undefined) {
        const current = await this.gameAlertsToggle.isChecked().catch(() => false);
        if (current !== preferences.content.gameAlerts) {
          await this.toggleGameAlerts();
        }
      }

      if (preferences.content.breakingNews !== undefined) {
        const current = await this.breakingNewsToggle.isChecked().catch(() => false);
        if (current !== preferences.content.breakingNews) {
          await this.toggleBreakingNews();
        }
      }

      if (preferences.content.dailyDigest !== undefined) {
        const current = await this.dailyDigestToggle.isChecked().catch(() => false);
        if (current !== preferences.content.dailyDigest) {
          await this.toggleDailyDigest();
        }
      }
    }
  }

  // Validation helpers
  async verifyNewsTypeState(newsType: keyof NewsTypePreferences, expectedState: boolean): Promise<void> {
    const actualState = await this.isNewsTypeEnabled(newsType);
    expect(actualState).toBe(expectedState);
  }

  async verifyNotificationState(notificationType: keyof NotificationPreferences, expectedState: boolean): Promise<void> {
    const actualState = await this.isNotificationEnabled(notificationType);
    expect(actualState).toBe(expectedState);
  }

  async verifyContentFrequency(expectedFrequency: ContentPreferences['frequency']): Promise<void> {
    const actualFrequency = await this.getSelectedContentFrequency();
    expect(actualFrequency).toBe(expectedFrequency);
  }

  async verifyAllPreferences(preferences: PreferencesData): Promise<void> {
    // Verify news types
    if (preferences.newsTypes) {
      for (const [newsType, expectedState] of Object.entries(preferences.newsTypes)) {
        await this.verifyNewsTypeState(newsType as keyof NewsTypePreferences, expectedState as boolean);
      }
    }

    // Verify notifications
    if (preferences.notifications) {
      for (const [notificationType, expectedState] of Object.entries(preferences.notifications)) {
        await this.verifyNotificationState(notificationType as keyof NotificationPreferences, expectedState as boolean);
      }
    }

    // Verify content frequency
    if (preferences.content?.frequency) {
      await this.verifyContentFrequency(preferences.content.frequency);
    }
  }

  // State capture for testing
  async captureCurrentPreferences(): Promise<PreferencesData> {
    const preferences: PreferencesData = {
      newsTypes: {},
      notifications: {},
      content: {}
    };

    // Capture news types
    const newsTypes: (keyof NewsTypePreferences)[] = ['injuries', 'trades', 'scores', 'analysis', 'rumors', 'standings'];
    for (const newsType of newsTypes) {
      try {
        preferences.newsTypes[newsType] = await this.isNewsTypeEnabled(newsType);
      } catch {
        // Skip if not available
      }
    }

    // Capture notifications
    const notificationTypes: (keyof NotificationPreferences)[] = ['push', 'email', 'sms', 'inApp'];
    for (const notificationType of notificationTypes) {
      try {
        preferences.notifications[notificationType] = await this.isNotificationEnabled(notificationType);
      } catch {
        // Skip if not available
      }
    }

    // Capture content frequency
    try {
      preferences.content.frequency = await this.getSelectedContentFrequency() || 'standard';
    } catch {
      preferences.content.frequency = 'standard';
    }

    return preferences;
  }

  // Form validation helpers
  async isFormValid(): Promise<boolean> {
    // Check if continue button is enabled (basic validation)
    const continueButton = this.page.locator('[data-testid="continue-button"]');
    return !(await continueButton.isDisabled());
  }

  async hasValidationErrors(): Promise<boolean> {
    const errorElements = this.page.locator('[role="alert"], .error-message, [data-testid*="error"]');
    return (await errorElements.count()) > 0;
  }

  async getValidationErrors(): Promise<string[]> {
    const errors: string[] = [];
    const errorElements = await this.page.locator('[role="alert"], .error-message, [data-testid*="error"]').all();

    for (const element of errorElements) {
      const text = await element.textContent();
      if (text?.trim()) {
        errors.push(text.trim());
      }
    }

    return errors;
  }

  // Mock data helpers
  async setupPreferencesMockData(preferences: PreferencesData): Promise<void> {
    await this.page.route('**/api/v1/onboarding/preferences', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(preferences)
      });
    });
  }

  async simulatePreferencesApiError(): Promise<void> {
    await this.page.route('**/api/v1/onboarding/preferences', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error',
          message: 'Failed to save preferences'
        })
      });
    });
  }

  // Common preference patterns for testing
  async setMinimalPreferences(): Promise<void> {
    await this.setAllPreferences({
      newsTypes: {
        scores: true,
        injuries: false,
        trades: false
      },
      notifications: {
        push: false,
        email: true,
        sms: false
      },
      content: {
        frequency: 'minimal'
      }
    });
  }

  async setStandardPreferences(): Promise<void> {
    await this.setAllPreferences({
      newsTypes: {
        scores: true,
        injuries: true,
        trades: true,
        analysis: false
      },
      notifications: {
        push: true,
        email: true,
        sms: false
      },
      content: {
        frequency: 'standard'
      }
    });
  }

  async setComprehensivePreferences(): Promise<void> {
    await this.setAllPreferences({
      newsTypes: {
        scores: true,
        injuries: true,
        trades: true,
        analysis: true,
        rumors: true,
        standings: true
      },
      notifications: {
        push: true,
        email: true,
        sms: true,
        inApp: true
      },
      content: {
        frequency: 'comprehensive',
        gameAlerts: true,
        breakingNews: true,
        dailyDigest: true
      }
    });
  }
}