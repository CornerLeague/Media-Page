# Enhanced Waiting Strategies for Dynamic Content

This document provides comprehensive guidance on using the enhanced waiting strategies implemented for better handling of dynamic content, async operations, and flaky test scenarios.

## Overview

The enhanced waiting strategies provide intelligent, adaptive timeout handling with improved reliability for testing dynamic applications. These utilities are designed to handle:

- Dynamic content loading with smart detection
- Async operations with retry mechanisms
- Element stability and interaction readiness
- Form submissions and API responses
- Modal and component lifecycle management
- Performance-aware waiting with environment adjustments

## Core Components

### 1. SmartContentWaiter

Intelligent content loading detection that adapts to different loading patterns.

#### Basic Usage

```typescript
import { SmartContentWaiter } from '@/test-setup';

// Wait for content to load in a container
await SmartContentWaiter.waitForContentLoaded(container, {
  timeout: 5000,
  checkVisibility: true,
  checkInteractivity: false,
  minContentLength: 10
});
```

#### Features

- **Automatic loading indicator detection** - Recognizes common loading patterns
- **Error state detection** - Throws early when errors are detected
- **Content validation** - Ensures minimum content requirements are met
- **Visibility checks** - Verifies content is actually visible
- **Interactivity validation** - Ensures interactive elements are ready

#### Configuration Options

```typescript
interface ContentWaitOptions {
  timeout?: number;                    // Maximum wait time
  interval?: number;                   // Polling interval
  retries?: number;                   // Number of retry attempts
  retryDelay?: number;                // Delay between retries
  loadingSelectors?: string[];        // Custom loading indicators
  errorSelectors?: string[];          // Custom error indicators
  minContentLength?: number;          // Minimum text content length
  checkVisibility?: boolean;          // Verify element visibility
  checkInteractivity?: boolean;       // Verify element interactivity
  onRetry?: (attempt: number, error: Error) => void;
}
```

### 2. ElementWaiter

Enhanced element waiting with stability checks and interaction readiness.

#### Basic Usage

```typescript
import { ElementWaiter } from '@/test-setup';

// Wait for element to be stable and ready
const element = await ElementWaiter.waitForElementStable(
  '[data-testid="submit-button"]',
  container,
  {
    timeout: 3000,
    checkStability: true,
    stabilityThreshold: 200,
    minSize: { width: 1, height: 1 }
  }
);
```

#### Features

- **Stability detection** - Waits for elements to stop moving/resizing
- **Bounds validation** - Ensures elements have proper dimensions
- **Interaction readiness** - Verifies elements are ready for user interaction
- **Retry logic** - Handles flaky element detection

### 3. AsyncOperationWaiter

Sophisticated async operation handling with intelligent retry logic.

#### Basic Usage

```typescript
import { AsyncOperationWaiter } from '@/test-setup';

// API call with retry and validation
const result = await AsyncOperationWaiter.waitForAsyncOperation(
  async () => {
    const response = await fetch('/api/data');
    return response.json();
  },
  {
    timeout: 10000,
    retries: 3,
    retryDelay: 1000,
    validateResult: (data) => data && data.status === 'success'
  }
);
```

#### Features

- **Exponential backoff** - Smart retry timing
- **Result validation** - Ensures operation results meet criteria
- **Error transformation** - Customize error handling per attempt
- **Timeout protection** - Prevents hanging operations
- **Abort signal support** - Cancellable operations

### 4. PlaywrightContentWaiter (E2E Tests)

Playwright-specific waiting strategies for end-to-end testing.

#### Basic Usage

```typescript
import { PlaywrightContentWaiter } from '@/e2e/utils/enhanced-playwright-waits';

// Wait for dynamic content in Playwright
await PlaywrightContentWaiter.waitForDynamicContent(page, {
  timeout: 10000,
  waitForImages: true,
  waitForFonts: true,
  networkIdleTimeout: 5000
});
```

#### Features

- **Network idle detection** - Waits for network activity to settle
- **Image loading** - Ensures all images are loaded
- **Font loading** - Waits for web fonts to load
- **Multi-step validation** - Comprehensive content readiness checks

## Convenience Functions

### testUtils

Pre-configured utilities for common testing scenarios:

```typescript
import { testUtils } from '@/test-setup';

// Quick content loading
await testUtils.waitForContent(container, 5000);

// Form readiness
const form = await testUtils.waitForFormReady('[data-testid="form"]');

// Modal readiness
const modal = await testUtils.waitForModalReady();

// API calls with validation
const result = await testUtils.apiCall(
  () => fetch('/api/endpoint'),
  { timeout: 5000, retries: 3 }
);

// Element stability
const element = await testUtils.waitForStableElement('[data-testid="button"]');
```

### waitStrategies

High-level strategies for common patterns:

```typescript
import { waitStrategies } from '@/test-setup';

// Page ready (comprehensive check)
await waitStrategies.forPageReady({
  timeout: 10000,
  checkVisibility: true,
  checkInteractivity: true
});

// Form ready for interaction
const form = await waitStrategies.forFormReady('[data-testid="form"]');

// Modal ready with animations
const modal = await waitStrategies.forModalReady('[role="dialog"]');

// API response with validation
const response = await waitStrategies.forApiResponse(
  () => apiCall(),
  { validateResponse: (data) => data.success }
);
```

## Enhanced renderWithProviders

The `renderWithProviders` function now supports enhanced waiting options:

```typescript
// Basic enhanced rendering
const result = renderWithProviders(<Component />, {
  smartWaiting: true,        // Use smart content detection
  waitForContent: true,      // Auto-wait for content
  waitOptions: {
    checkVisibility: true,
    checkInteractivity: true
  }
});

// Wait for render to complete
await result.ready;

// Use enhanced methods
await result.waitForSmartContent();
const element = await result.waitForStableElement('[data-testid="button"]');
await result.waitForInteractiveContent();
```

## Timeout Configuration

All waiting strategies use the centralized timeout configuration with environment-aware adjustments:

```typescript
import { TEST_TIMEOUTS } from '@/test-setup';

// Available timeout categories
TEST_TIMEOUTS.INSTANT           // 100ms (adjusted for CI)
TEST_TIMEOUTS.FAST_RENDER       // 500ms (adjusted for CI)
TEST_TIMEOUTS.STANDARD_RENDER   // 2000ms (adjusted for CI)
TEST_TIMEOUTS.DATA_FETCH        // 3000ms (adjusted for CI)
TEST_TIMEOUTS.API_STANDARD      // 3000ms (adjusted for CI)
TEST_TIMEOUTS.FORM_SUBMISSION   // 4000ms (adjusted for CI)

// Environment multipliers:
// - CI: 2x timeouts
// - Debug mode: 5x timeouts
// - Slow tests: 3x timeouts
```

## Error Handling and Debugging

### Retry Callbacks

Monitor retry attempts for debugging:

```typescript
await SmartContentWaiter.waitForContentLoaded(container, {
  retries: 3,
  onRetry: (attempt, error) => {
    console.log(`Retry attempt ${attempt}: ${error.message}`);
  }
});
```

### Error States

Enhanced error detection and reporting:

```typescript
// Automatically detects and reports error states
try {
  await SmartContentWaiter.waitForContentLoaded(container);
} catch (error) {
  // Error will include details about what failed
  console.error('Content loading failed:', error.message);
  // e.g., "Error state detected: Failed to load user data"
}
```

### Abort Operations

Cancel long-running operations:

```typescript
const abortController = new AbortController();

// Cancel after 5 seconds
setTimeout(() => abortController.abort(), 5000);

await SmartContentWaiter.waitForContentLoaded(container, {
  abortSignal: abortController.signal
});
```

## Best Practices

### 1. Choose the Right Strategy

- **SmartContentWaiter** - For dynamic content loading
- **ElementWaiter** - For element stability and interaction
- **AsyncOperationWaiter** - For API calls and async operations
- **testUtils** - For quick, common operations
- **waitStrategies** - For high-level, comprehensive scenarios

### 2. Use Appropriate Timeouts

```typescript
// Quick operations
{ timeout: TEST_TIMEOUTS.FAST_RENDER }

// Standard content loading
{ timeout: TEST_TIMEOUTS.DATA_FETCH }

// Complex operations or slow APIs
{ timeout: TEST_TIMEOUTS.API_COMPLEX }

// Form submissions
{ timeout: TEST_TIMEOUTS.FORM_SUBMISSION }
```

### 3. Implement Proper Error Handling

```typescript
try {
  await SmartContentWaiter.waitForContentLoaded(container, {
    retries: 3,
    onRetry: (attempt, error) => {
      // Log retry attempts for debugging
      console.warn(`Retry ${attempt}:`, error.message);
    }
  });
} catch (error) {
  // Handle final failure
  throw new Error(`Content loading failed: ${error.message}`);
}
```

### 4. Use Validation When Appropriate

```typescript
// Validate API responses
const data = await AsyncOperationWaiter.waitForAsyncOperation(
  apiCall,
  {
    validateResult: (result) => result && result.status === 'success',
    retries: 3
  }
);

// Validate content requirements
await SmartContentWaiter.waitForContentLoaded(container, {
  minContentLength: 50,  // Ensure meaningful content
  checkVisibility: true, // Ensure content is visible
  checkInteractivity: true // Ensure interactive elements work
});
```

### 5. Optimize for CI Environments

The strategies automatically adjust timeouts for CI environments, but you can also:

```typescript
// Use environment-aware configurations
const timeout = process.env.CI
  ? TEST_TIMEOUTS.DATA_FETCH * 2
  : TEST_TIMEOUTS.DATA_FETCH;

await SmartContentWaiter.waitForContentLoaded(container, { timeout });
```

## Migration Guide

### From Basic waitFor

```typescript
// Old approach
await waitFor(() => {
  expect(screen.getByTestId('content')).toBeInTheDocument();
}, { timeout: 5000 });

// New approach
await SmartContentWaiter.waitForContentLoaded(container, {
  timeout: 5000,
  checkVisibility: true
});
expect(screen.getByTestId('content')).toBeVisible();
```

### From Manual Retry Logic

```typescript
// Old approach
let retries = 3;
while (retries > 0) {
  try {
    const result = await apiCall();
    return result;
  } catch (error) {
    retries--;
    if (retries === 0) throw error;
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

// New approach
const result = await AsyncOperationWaiter.waitForAsyncOperation(
  apiCall,
  { retries: 3, retryDelay: 1000 }
);
```

### From Playwright Basic Waits

```typescript
// Old approach
await page.waitForLoadState('networkidle');
await page.waitForSelector('[data-testid="content"]', { state: 'visible' });

// New approach
await PlaywrightContentWaiter.waitForDynamicContent(page, {
  timeout: 10000,
  waitForImages: true,
  checkVisibility: true
});
```

## Performance Considerations

### 1. Timeout Tuning

- Use shorter timeouts for fast operations
- Reserve longer timeouts for complex scenarios
- Consider environment multipliers (CI gets 2x timeouts)

### 2. Retry Strategy

- Use fewer retries for reliable operations
- Increase retries for known flaky scenarios
- Implement exponential backoff for network operations

### 3. Polling Intervals

- Use faster polling for quick changes (50-100ms)
- Use slower polling for expensive checks (250ms+)
- Balance responsiveness vs. CPU usage

## Troubleshooting

### Common Issues

1. **Timeout too short**: Increase timeout or check for blocking operations
2. **Element not stable**: Increase stability threshold or check for animations
3. **Content not detected**: Verify loading/content selectors are correct
4. **False positives**: Use validation functions to ensure correct results

### Debug Tips

1. Enable retry callbacks to see what's happening
2. Use smaller timeouts initially to identify slow operations
3. Check browser dev tools for network activity
4. Verify element selectors in browser inspector

## Examples

See the comprehensive examples in:
- `/src/__tests__/examples/enhanced-waiting-examples.test.tsx`
- Individual test files throughout the codebase

These examples demonstrate real-world usage patterns and edge cases handled by the enhanced waiting strategies.