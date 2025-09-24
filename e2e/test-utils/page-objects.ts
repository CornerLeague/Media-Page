/**
 * Page Object Models for Onboarding Flow
 * Provides reliable element location and interaction patterns
 */

import { Page, Locator, expect } from '@playwright/test';
import { WaitStrategies } from './wait-strategies';

export interface OnboardingState {
  currentStep: number;
  selectedSports: Array<{ sportId: string; rank: number }>;
  selectedTeams: Array<{ teamId: string; affinityScore: number }>;
  preferences: {
    newsTypes: Record<string, boolean>;
    notifications: Record<string, boolean>;
    contentFrequency: 'minimal' | 'standard' | 'comprehensive';
  } | null;
}

/**
 * Base Page Object for all onboarding steps
 * Contains common elements and functionality
 */
export class BaseOnboardingPage {
  protected waitStrategies: WaitStrategies;

  constructor(
    protected page: Page,
    protected expectedStep: number,
    protected expectedTitle: RegExp
  ) {
    this.waitStrategies = new WaitStrategies(page);
  }

  // Navigation elements
  get mainContent(): Locator {
    return this.page.locator('[data-testid="main-content"]');
  }

  get stepIndicator(): Locator {
    return this.page.locator('[data-testid="step-indicator"]');
  }

  get progressBar(): Locator {
    return this.page.locator('[role="progressbar"]');
  }

  get continueButton(): Locator {
    return this.page.locator('[data-testid="continue-button"]');
  }

  get backButton(): Locator {
    return this.page.locator('[data-testid="back-button"]');
  }

  get pageTitle(): Locator {
    return this.page.locator('h1');
  }

  // Common actions
  async navigateTo(): Promise<void> {
    await this.page.goto(`/onboarding/step/${this.expectedStep}`, {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    await this.waitForPageLoad();
  }

  async waitForPageLoad(): Promise<void> {
    // Wait for main content to be visible
    await this.waitStrategies.waitForElement(this.mainContent, 'visible', 15000);

    // Wait for step indicator to show correct step
    await this.waitStrategies.waitForText(
      this.stepIndicator,
      new RegExp(`Step ${this.expectedStep} of 5`),
      10000
    );

    // Wait for page title to load
    await this.waitStrategies.waitForText(this.pageTitle, this.expectedTitle, 10000);
  }

  async clickContinue(): Promise<void> {
    await this.waitStrategies.waitForElement(this.continueButton, 'visible');
    await this.waitStrategies.waitForEnabled(this.continueButton);
    await this.continueButton.click();
  }

  async clickBack(): Promise<void> {
    if (this.expectedStep > 1) {
      await this.waitStrategies.waitForElement(this.backButton, 'visible');
      await this.backButton.click();
    }
  }

  async isContinueDisabled(): Promise<boolean> {
    return await this.continueButton.isDisabled();
  }

  async getCurrentStep(): Promise<number> {
    const stepText = await this.stepIndicator.textContent();
    const match = stepText?.match(/Step (\d+)/);
    return match ? parseInt(match[1]) : 0;
  }

  async getProgressPercentage(): Promise<number> {
    const progressValue = await this.progressBar.getAttribute('aria-valuenow');
    return progressValue ? parseInt(progressValue) : 0;
  }

  async verifyStep(): Promise<void> {
    await expect(this.pageTitle).toContainText(this.expectedTitle);
    await expect(this.stepIndicator).toContainText(`Step ${this.expectedStep} of 5`);
  }

  async waitForNavigation(expectedUrl: RegExp, timeout: number = 10000): Promise<void> {
    await this.page.waitForURL(expectedUrl, { timeout });
  }
}

/**
 * Welcome Step Page Object (Step 1)
 */
export class WelcomeStepPage extends BaseOnboardingPage {
  constructor(page: Page) {
    super(page, 1, /welcome/i);
  }

  async verifyWelcomeContent(): Promise<void> {
    await this.verifyStep();
    await expect(this.getProgressPercentage()).resolves.toBe(20);
  }
}

/**
 * Sports Selection Step Page Object (Step 2)
 */
export class SportsSelectionStepPage extends BaseOnboardingPage {
  constructor(page: Page) {
    super(page, 2, /choose.*sports/i);
  }

  // Sports selection elements
  get sportsContainer(): Locator {
    return this.page.locator('[data-testid^="sport-card-"]');
  }

  get selectedSportsCount(): Locator {
    return this.page.locator('text=/\\d+ sports selected/');
  }

  get loadingIndicator(): Locator {
    return this.page.locator('[data-testid="loading-sports"]');
  }

  get errorMessage(): Locator {
    return this.page.locator('[data-testid="error-message"]');
  }

  get offlineIndicator(): Locator {
    return this.page.locator('text="Working Offline"');
  }

  // Action buttons
  get selectPopularButton(): Locator {
    return this.page.locator('button:has-text("Popular Sports")');
  }

  get selectAllButton(): Locator {
    return this.page.locator('button:has-text("Select All")');
  }

  get clearAllButton(): Locator {
    return this.page.locator('button:has-text("Clear All")');
  }

  // Sport card selectors
  getSportCard(sportId: string): Locator {
    return this.page.locator(`[data-testid="sport-card-${sportId}"]`);
  }

  getSelectedSports(): Locator {
    return this.page.locator('[data-testid^="sport-card-"][data-selected="true"]');
  }

  // Actions
  async waitForSportsToLoad(): Promise<void> {
    // Wait for either sports to load or error/loading state
    await Promise.race([
      this.waitStrategies.waitForElement(this.sportsContainer.first(), 'visible', 15000),
      this.waitStrategies.waitForElement(this.errorMessage, 'visible', 15000),
      this.waitStrategies.waitForElement(this.loadingIndicator, 'visible', 5000)
    ]);
  }

  async selectSport(sportId: string): Promise<void> {
    const sportCard = this.getSportCard(sportId);
    await this.waitStrategies.waitForElement(sportCard, 'visible');
    await sportCard.click();
    await this.page.waitForTimeout(300); // Wait for selection animation
  }

  async deselectSport(sportId: string): Promise<void> {
    const sportCard = this.getSportCard(sportId);
    const isSelected = await sportCard.getAttribute('data-selected') === 'true';
    if (isSelected) {
      await sportCard.click();
      await this.page.waitForTimeout(300);
    }
  }

  async isSportSelected(sportId: string): Promise<boolean> {
    const sportCard = this.getSportCard(sportId);
    const selected = await sportCard.getAttribute('data-selected');
    return selected === 'true';
  }

  async getSportRank(sportId: string): Promise<number | null> {
    const sportCard = this.getSportCard(sportId);
    const rankElement = sportCard.locator('p:has-text("st"), p:has-text("nd"), p:has-text("rd"), p:has-text("th")');

    try {
      const rankText = await rankElement.textContent({ timeout: 1000 });
      if (!rankText) return null;
      const match = rankText.match(/^(\d+)/);
      return match ? parseInt(match[1]) : null;
    } catch {
      return null;
    }
  }

  async getSelectedCount(): Promise<number> {
    return await this.getSelectedSports().count();
  }

  async selectMultipleSports(sportIds: string[]): Promise<void> {
    for (const sportId of sportIds) {
      await this.selectSport(sportId);
    }
  }

  async dragSportToPosition(fromSportId: string, toSportId: string): Promise<void> {
    const fromCard = this.getSportCard(fromSportId);
    const toCard = this.getSportCard(toSportId);

    await this.waitStrategies.waitForElement(fromCard, 'visible');
    await this.waitStrategies.waitForElement(toCard, 'visible');

    await fromCard.dragTo(toCard);
    await this.page.waitForTimeout(500);
  }

  async clickActionButton(action: 'popular' | 'all' | 'clear'): Promise<void> {
    const buttonMap = {
      popular: this.selectPopularButton,
      all: this.selectAllButton,
      clear: this.clearAllButton
    };

    const button = buttonMap[action];
    await this.waitStrategies.waitForElement(button, 'visible');
    await button.click();
    await this.page.waitForTimeout(200);
  }

  async verifySelectionCount(expectedCount: number): Promise<void> {
    const actualCount = await this.getSelectedCount();
    expect(actualCount).toBe(expectedCount);
  }

  async verifySportsStep(): Promise<void> {
    await this.verifyStep();
    await expect(this.getProgressPercentage()).resolves.toBe(40);
    await this.waitForSportsToLoad();
  }

  async hasErrorState(): Promise<boolean> {
    return await this.errorMessage.isVisible() || await this.offlineIndicator.isVisible();
  }
}

/**
 * Team Selection Step Page Object (Step 3)
 */
export class TeamSelectionStepPage extends BaseOnboardingPage {
  constructor(page: Page) {
    super(page, 3, /select.*teams/i);
  }

  // Team selection elements
  get teamsContainer(): Locator {
    return this.page.locator('[data-testid="teams-container"]');
  }

  get noSportsMessage(): Locator {
    return this.page.locator('text="Please go back and select your sports first."');
  }

  get loadingTeams(): Locator {
    return this.page.locator('text="Loading teams..."');
  }

  // Actions
  async waitForTeamsToLoad(): Promise<void> {
    try {
      await this.waitStrategies.waitForElement(this.teamsContainer, 'visible', 15000);
    } catch (error) {
      // Check if there's a "no sports selected" state
      const hasNoSportsMessage = await this.noSportsMessage.isVisible();
      if (hasNoSportsMessage) {
        throw new Error('Cannot load teams - no sports selected. Go back to sports selection first.');
      }

      // Check if still loading
      const isLoading = await this.loadingTeams.isVisible();
      if (isLoading) {
        await this.waitStrategies.waitForElement(this.teamsContainer, 'visible', 20000);
      } else {
        throw error;
      }
    }
  }

  async selectTeam(teamName: string): Promise<void> {
    await this.waitForTeamsToLoad();

    const teamElement = this.page.locator(`text="${teamName}"`).first();
    await teamElement.scrollIntoViewIfNeeded();

    // Find and click the checkbox for this team
    const checkbox = teamElement.locator('..').locator('input[type="checkbox"]').first();
    await checkbox.click();
  }

  async setTeamAffinity(teamName: string, score: number): Promise<void> {
    await this.waitForTeamsToLoad();

    const teamElement = this.page.locator(`text="${teamName}"`).first();
    await teamElement.scrollIntoViewIfNeeded();

    // Find the star rating buttons (only visible if team is selected)
    const starButton = teamElement.locator('..').locator('button').nth(score - 1);
    await starButton.click();
  }

  async isTeamSelected(teamName: string): Promise<boolean> {
    const teamElement = this.page.locator(`text="${teamName}"`).first();
    const checkbox = teamElement.locator('..').locator('input[type="checkbox"]').first();
    return await checkbox.isChecked();
  }

  async verifyTeamsStep(): Promise<void> {
    await this.verifyStep();
    await expect(this.getProgressPercentage()).resolves.toBe(60);
  }

  async hasNoSportsState(): Promise<boolean> {
    return await this.noSportsMessage.isVisible();
  }
}

/**
 * Preferences Step Page Object (Step 4)
 */
export class PreferencesStepPage extends BaseOnboardingPage {
  constructor(page: Page) {
    super(page, 4, /preferences/i);
  }

  // Preference elements
  get newsTypeSwitches(): Locator {
    return this.page.locator('label[for="injuries"], label[for="trades"], label[for="scores"]');
  }

  get notificationSwitches(): Locator {
    return this.page.locator('label[for="push"], label[for="email"], label[for="sms"]');
  }

  get contentFrequencyRadios(): Locator {
    return this.page.locator('input[name="contentFrequency"]');
  }

  // Actions
  async toggleNewsType(newsType: string): Promise<void> {
    const toggle = this.page.locator(`label[for="${newsType}"]`);
    await this.waitStrategies.waitForElement(toggle, 'visible');
    await toggle.click();
  }

  async toggleNotification(notificationType: string): Promise<void> {
    const toggle = this.page.locator(`label[for="${notificationType}"]`);
    await this.waitStrategies.waitForElement(toggle, 'visible');
    await toggle.click();
  }

  async selectContentFrequency(frequency: 'minimal' | 'standard' | 'comprehensive'): Promise<void> {
    const radio = this.page.locator(`input[value="${frequency}"]`);
    await this.waitStrategies.waitForElement(radio, 'visible');
    await radio.click();
  }

  async verifyPreferencesStep(): Promise<void> {
    await this.verifyStep();
    await expect(this.getProgressPercentage()).resolves.toBe(80);

    // Wait for form elements to load
    await this.waitStrategies.waitForElement(this.contentFrequencyRadios.first(), 'visible');
  }
}

/**
 * Completion Step Page Object (Step 5)
 */
export class CompletionStepPage extends BaseOnboardingPage {
  constructor(page: Page) {
    super(page, 5, /complete|congratulations|set/i);
  }

  // Completion elements
  get summarySection(): Locator {
    return this.page.locator('[data-testid="summary-section"]');
  }

  get completeButton(): Locator {
    return this.page.locator('button:has-text("Get Started"), button:has-text("Enter Dashboard"), button:has-text("Complete")');
  }

  // Actions
  async completeOnboarding(): Promise<void> {
    await this.waitStrategies.waitForElement(this.completeButton, 'visible');
    await this.waitStrategies.waitForEnabled(this.completeButton);
    await this.completeButton.click();
  }

  async verifySummaryContent(): Promise<void> {
    await this.waitStrategies.waitForElement(this.summarySection, 'visible');
  }

  async verifySelectedSports(expectedSports: string[]): Promise<void> {
    for (const sport of expectedSports) {
      await expect(this.page.locator(`text="${sport}"`).first()).toBeVisible();
    }
  }

  async verifyCompletionStep(): Promise<void> {
    await this.verifyStep();
    await expect(this.getProgressPercentage()).resolves.toBe(100);
    await this.verifySummaryContent();
  }
}

/**
 * Main Onboarding Flow Page Object
 * Orchestrates all step page objects
 */
export class OnboardingFlowPage {
  public welcomeStep: WelcomeStepPage;
  public sportsStep: SportsSelectionStepPage;
  public teamsStep: TeamSelectionStepPage;
  public preferencesStep: PreferencesStepPage;
  public completionStep: CompletionStepPage;

  constructor(private page: Page) {
    this.welcomeStep = new WelcomeStepPage(page);
    this.sportsStep = new SportsSelectionStepPage(page);
    this.teamsStep = new TeamSelectionStepPage(page);
    this.preferencesStep = new PreferencesStepPage(page);
    this.completionStep = new CompletionStepPage(page);
  }

  async navigateToStep(step: number): Promise<BaseOnboardingPage> {
    const stepPages = [
      null, // index 0 unused
      this.welcomeStep,
      this.sportsStep,
      this.teamsStep,
      this.preferencesStep,
      this.completionStep
    ];

    const stepPage = stepPages[step];
    if (!stepPage) {
      throw new Error(`Invalid step number: ${step}. Must be 1-5.`);
    }

    await stepPage.navigateTo();
    return stepPage;
  }

  async getOnboardingState(): Promise<OnboardingState> {
    return await this.page.evaluate(() => {
      const stored = localStorage.getItem('onboarding_status');
      return stored ? JSON.parse(stored) : {
        currentStep: 1,
        selectedSports: [],
        selectedTeams: [],
        preferences: null
      };
    });
  }

  async setOnboardingState(state: Partial<OnboardingState>): Promise<void> {
    await this.page.evaluate((state) => {
      const currentState = localStorage.getItem('onboarding_status');
      const parsedState = currentState ? JSON.parse(currentState) : {};
      const newState = { ...parsedState, ...state };
      localStorage.setItem('onboarding_status', JSON.stringify(newState));
    }, state);
  }

  async clearOnboardingState(): Promise<void> {
    await this.page.evaluate(() => {
      localStorage.removeItem('onboarding_status');
    });
  }
}