# Onboarding Test Utilities

This directory contains comprehensive test utilities for reliable and maintainable onboarding flow testing. These utilities implement Task 5 Sub-task 3 from the onboarding bug fix tasks, providing page object models, wait strategies, and specialized helpers to address the 100% test failure rate.

## Overview

The test utilities are organized into several specialized modules:

- **Page Object Models** - Reliable element location and interaction patterns
- **Wait Strategies** - Robust waiting utilities to prevent flaky tests
- **Specialized Helpers** - Domain-specific utilities for each onboarding step
- **Error Handling** - Retry mechanisms and failure recovery strategies

## Quick Start

```typescript
import { test, expect } from '@playwright/test';
import { createOnboardingTestSuite, setupOnboardingTest } from './test-utils';

test('complete onboarding flow', async ({ page }, testInfo) => {
  // Setup test environment
  await setupOnboardingTest(page, {
    mockApis: true,
    clearStorage: true,
    testMode: true
  });

  // Create test suite with all utilities
  const suite = createOnboardingTestSuite(page, testInfo);

  // Navigate using page objects
  const welcomePage = await suite.flow.navigateToStep(1);
  await welcomePage.verifyStep();

  const sportsPage = await suite.flow.navigateToStep(2);
  await sportsPage.selectSport('nfl');
  await sportsPage.clickContinue();

  // ... continue with remaining steps
});
```

## Core Components

### 1. Page Object Models (`page-objects.ts`)

Provides reliable, maintainable page representations for each onboarding step:

```typescript
// Base class with common functionality
class BaseOnboardingPage {
  get continueButton(): Locator;
  get backButton(): Locator;
  async waitForPageLoad(): Promise<void>;
  async verifyStep(): Promise<void>;
}

// Step-specific page objects
class SportsSelectionStepPage extends BaseOnboardingPage {
  async selectSport(sportId: string): Promise<void>;
  async isSportSelected(sportId: string): Promise<boolean>;
  async getSelectedCount(): Promise<number>;
}

// Orchestration class
class OnboardingFlowPage {
  public welcomeStep: WelcomeStepPage;
  public sportsStep: SportsSelectionStepPage;
  // ... other steps

  async navigateToStep(step: number): Promise<BaseOnboardingPage>;
}
```

### 2. Wait Strategies (`wait-strategies.ts`)

Robust waiting utilities that prevent timing-related test failures:

```typescript
class WaitStrategies {
  // Basic element waiting
  async waitForElement(locator: Locator, condition: 'visible' | 'hidden' | 'stable'): Promise<void>;

  // Smart waiting with multiple conditions
  async smartWait(locator: Locator, options: {
    condition?: WaitCondition;
    text?: string | RegExp;
    attribute?: { name: string; value: string | RegExp };
    timeout?: number;
    stable?: boolean;
  }): Promise<void>;

  // Network and API waiting
  async waitForApiResponse(urlPattern: string | RegExp): Promise<void>;
  async waitForNetworkIdle(): Promise<void>;

  // Advanced waiting patterns
  async waitWithRetry<T>(action: () => Promise<T>, options: WaitOptions): Promise<T>;
  async waitForStability(locator: Locator, stableTime?: number): Promise<void>;
}
```

### 3. Team Selection Helpers (`team-selection-helpers.ts`)

Specialized utilities for complex team selection interactions:

```typescript
class TeamSelectionTestHelpers {
  async waitForTeamsToLoad(): Promise<void>;
  async selectTeam(teamName: string): Promise<void>;
  async setTeamAffinity(teamName: string, score: number): Promise<void>;
  async selectMultipleTeams(teamNames: string[]): Promise<void>;
  async verifySelectedCount(expectedCount: number): Promise<void>;

  // Handles virtualized lists and scrolling
  async scrollToTeam(teamName: string): Promise<void>;

  // State validation
  async isTeamSelected(teamName: string): Promise<boolean>;
  async getSelectedTeams(): Promise<string[]>;
}
```

### 4. Preferences Helpers (`preferences-helpers.ts`)

Utilities for preferences form interactions:

```typescript
class PreferencesTestHelpers {
  // Individual preference controls
  async toggleNewsType(newsType: keyof NewsTypePreferences): Promise<void>;
  async toggleNotification(notificationType: keyof NotificationPreferences): Promise<void>;
  async selectContentFrequency(frequency: 'minimal' | 'standard' | 'comprehensive'): Promise<void>;

  // Bulk operations
  async setAllPreferences(preferences: PreferencesData): Promise<void>;
  async setStandardPreferences(): Promise<void>;
  async setComprehensivePreferences(): Promise<void>;

  // State validation
  async verifyAllPreferences(preferences: PreferencesData): Promise<void>;
  async captureCurrentPreferences(): Promise<PreferencesData>;
}
```

### 5. Completion Helpers (`completion-helpers.ts`)

Utilities for completion step verification and final onboarding:

```typescript
class CompletionTestHelpers {
  async waitForCompletionToLoad(): Promise<void>;
  async completeOnboarding(): Promise<void>;
  async completeOnboardingAndWaitForRedirect(expectedUrl: RegExp): Promise<void>;

  // Summary verification
  async verifySelectedSports(expectedSports: string[]): Promise<void>;
  async verifySelectedTeams(expectedTeams: string[]): Promise<void>;
  async verifySportsRanking(expectedRankings: Record<string, number>): Promise<void>;

  // Comprehensive verification
  async verifyFullCompletion(expectedData: {
    sports: string[];
    teams?: string[];
    hasPreferences?: boolean;
    redirectUrl?: RegExp;
  }): Promise<void>;
}
```

### 6. Error Handling (`error-handling.ts`)

Retry mechanisms and failure recovery strategies:

```typescript
class ErrorHandlingStrategies {
  // Retry logic with exponential backoff
  async executeWithRetry<T>(action: () => Promise<T>, config: RetryConfig): Promise<T>;

  // Safe interactions with automatic retry
  async safeClick(locator: Locator, options?: ClickOptions): Promise<void>;
  async safeNavigate(url: string, options?: NavigationOptions): Promise<void>;

  // Error context capture for debugging
  async captureErrorContext(error: Error, step: string): Promise<ErrorContext>;

  // Recovery strategies
  async recoverFromFailure(failureType: 'navigation' | 'element' | 'api' | 'timeout'): Promise<void>;
  async smartRecovery(error: Error): Promise<void>;

  // Network simulation for testing
  async simulateNetworkIssues(type: 'timeout' | 'failure' | 'slow' | 'intermittent'): Promise<void>;
}
```

## Test Patterns

The utilities include common test patterns for typical scenarios:

### Complete Flow Testing

```typescript
const suite = createOnboardingTestSuite(page, testInfo);
const completionPage = await TestPatterns.completeStandardFlow(suite);
```

### Error Recovery Testing

```typescript
const stepPage = await TestPatterns.testErrorRecovery(suite, 3);
```

### Accessibility Validation

```typescript
const results = await TestPatterns.validateAccessibility(suite);
expect(results.every(r => r.passed)).toBe(true);
```

## Migration from Existing Tests

To migrate existing tests to use these utilities:

### Before (Fragile)

```typescript
test('onboarding flow', async ({ page }) => {
  await page.goto('/onboarding/step/1');
  await page.waitForSelector('main'); // May timeout
  await page.click('button:has-text("Continue")'); // May fail if button not ready

  await page.goto('/onboarding/step/2');
  await page.click('[data-testid="sport-card-nfl"]'); // May not exist
  // ... brittle selectors and timing
});
```

### After (Robust)

```typescript
test('onboarding flow', async ({ page }, testInfo) => {
  await setupOnboardingTest(page);
  const suite = createOnboardingTestSuite(page, testInfo);

  const welcomePage = await suite.flow.navigateToStep(1);
  await welcomePage.verifyStep();
  await welcomePage.clickContinue();

  const sportsPage = await suite.flow.navigateToStep(2);
  await sportsPage.waitForSportsToLoad();
  await sportsPage.selectSport('nfl');
  await sportsPage.verifySelectionCount(1);
  // ... reliable interactions
});
```

## Key Benefits

### 1. Reliability
- Robust wait strategies prevent timing-related failures
- Automatic retry logic handles transient issues
- Smart element location with fallback strategies

### 2. Maintainability
- Page object models abstract away implementation details
- Centralized element selectors reduce maintenance burden
- Clear separation between test logic and UI interactions

### 3. Debugging
- Comprehensive error context capture
- Automatic screenshots on failures
- Detailed logging for troubleshooting

### 4. Reusability
- Modular design allows mixing and matching utilities
- Common patterns reduce code duplication
- Backward compatibility with existing helpers

## Configuration

### Default Setup

```typescript
await setupOnboardingTest(page, {
  mockApis: true,        // Setup API mocks
  clearStorage: true,    // Clear localStorage/sessionStorage
  testMode: true         // Set test mode flags
});
```

### Custom Retry Configuration

```typescript
await suite.errorHandling.executeWithRetry(
  action,
  {
    maxRetries: 5,
    retryDelay: 2000,
    exponentialBackoff: true,
    retryCondition: (error) => /network|timeout/i.test(error.message)
  }
);
```

### Viewport Testing

```typescript
// Test mobile responsiveness
await suite.responsive.setMobileViewport();
await suite.responsive.verifyTouchTargetSize('[data-testid="sport-card-nfl"]', 44);

// Test desktop layout
await suite.responsive.setDesktopViewport();
```

## Best Practices

### 1. Use Page Objects for Navigation
```typescript
// Good
const sportsPage = await suite.flow.navigateToStep(2);
await sportsPage.selectSport('nfl');

// Avoid
await page.goto('/onboarding/step/2');
await page.click('[data-testid="sport-card-nfl"]');
```

### 2. Wait for Stable State
```typescript
// Wait for elements to be stable before interaction
await suite.wait.smartWait(element, { stable: true });
```

### 3. Use Error Handling for Critical Operations
```typescript
const result = await suite.errorHandling.withErrorHandling(
  () => criticalOperation(),
  'Critical Operation',
  { retries: 3, continueOnError: false }
);
```

### 4. Verify State Before Proceeding
```typescript
await sportsPage.verifySelectionCount(2);
await teamsPage.verifyTeamSelected('Patriots');
```

## Files Structure

```
e2e/test-utils/
├── README.md                    # This documentation
├── index.ts                     # Main exports and utilities
├── page-objects.ts              # Page object models
├── wait-strategies.ts           # Wait and timing utilities
├── team-selection-helpers.ts    # Team selection specialized helpers
├── preferences-helpers.ts       # Preferences form utilities
├── completion-helpers.ts        # Completion step utilities
├── error-handling.ts           # Error handling and retry strategies
├── onboarding-helpers.ts       # Existing helpers (maintained for compatibility)
└── example-usage.spec.ts       # Example usage patterns
```

## Success Criteria Met

✅ **Tests provide reliable regression protection**
- Robust wait strategies prevent timing issues
- Error handling with retry logic handles transient failures
- Page object models abstract away fragile selectors

✅ **Common test utilities and helpers are available**
- Comprehensive utility classes for each onboarding step
- Reusable patterns and workflows
- Backward compatibility with existing helpers

✅ **Page object models exist for onboarding steps**
- Dedicated page objects for all 5 onboarding steps
- Base class with common functionality
- Orchestration class for flow management

✅ **Proper wait strategies are implemented**
- Smart waiting with multiple conditions
- Network and API waiting utilities
- Stability and animation waiting
- Exponential backoff retry mechanisms

This comprehensive test utility suite addresses the core issues identified in the bug report and provides a foundation for reliable onboarding flow testing going forward.