# Test Timeout Configuration Guide

This guide explains the enhanced timeout configurations implemented for improved test reliability when dealing with slower loading elements and async operations.

## Overview

The test infrastructure has been enhanced with comprehensive timeout configurations that automatically adjust based on the environment (CI, debug mode, etc.) and provide specific timeouts for different types of operations.

## Key Files Modified

### 1. Core Timeout Configuration
- **`src/utils/test-timeouts.ts`** - Centralized timeout configuration module
- **`src/test-setup.tsx`** - Enhanced Vitest utilities with timeout handling
- **`vitest.config.ts`** - Updated with environment-aware timeouts
- **`playwright.config.ts`** - Enhanced with dynamic timeout adjustments

### 2. Playwright Utilities
- **`e2e/utils/wait-helpers.ts`** - New comprehensive wait utilities
- **`e2e/utils/axe-helper.ts`** - Enhanced accessibility testing timeouts
- **`e2e/auth-utils.ts`** - Improved authentication testing timeouts

## Timeout Categories

### Environment-Based Adjustments
Timeouts automatically adjust based on environment:

```typescript
// Normal development: 1x multiplier
// CI environment: 2x multiplier
// Debug mode: 3x multiplier
// Explicit slow tests: 3x multiplier
```

### Operation-Specific Timeouts

#### Component Rendering
- **FAST_RENDER**: 500ms - Simple components
- **STANDARD_RENDER**: 2000ms - Standard components
- **SLOW_RENDER**: 5000ms - Complex components with data
- **COMPLEX_RENDER**: 8000ms - Very complex components

#### Animations & Transitions
- **FAST_ANIMATION**: 300ms - Quick animations
- **STANDARD_ANIMATION**: 1000ms - Standard animations
- **SLOW_ANIMATION**: 2500ms - Complex animations
- **COMPLEX_ANIMATION**: 4000ms - Multi-stage animations

#### API & Network Operations
- **API_FAST**: 1500ms - Fast API calls
- **API_STANDARD**: 3000ms - Standard API calls
- **API_SLOW**: 6000ms - Slow API calls
- **API_COMPLEX**: 10000ms - Complex API operations

#### Form Operations
- **FORM_VALIDATION**: 1000ms - Form validation
- **FORM_SUBMISSION**: 4000ms - Form submission
- **FILE_UPLOAD_SMALL**: 5000ms - Small file uploads
- **FILE_UPLOAD_LARGE**: 15000ms - Large file uploads

#### Accessibility Testing
- **A11Y_AUDIT_BASIC**: 3000ms - Basic accessibility audit
- **A11Y_AUDIT_STANDARD**: 5000ms - Standard accessibility audit
- **A11Y_AUDIT_COMPLEX**: 8000ms - Complex page audit

## Usage Examples

### Vitest Component Testing

```typescript
import { renderWithProviders, waitForAsyncComponent, TEST_TIMEOUTS } from '../test-setup';

// Basic usage with default timeouts
const result = renderWithProviders(<MyComponent />);

// Enhanced usage with async handling
const result = renderWithProviders(<MyComponent />, {
  waitForAsync: true,
  timeout: TEST_TIMEOUTS.SLOW_RENDER
});

// Wait for async operations to complete
await waitForAsyncComponent(
  () => fireEvent.click(submitButton),
  {
    loadingTimeout: TEST_TIMEOUTS.DATA_LOADING,
    errorTimeout: TEST_TIMEOUTS.API_CALL_STANDARD
  }
);

// Wait for API calls with retry logic
const data = await waitForApiCall(
  () => fetch('/api/data'),
  {
    timeout: TEST_TIMEOUTS.API_SLOW,
    retries: 3,
    retryDelay: 1000
  }
);
```

### Playwright E2E Testing

```typescript
import { waitForElementVisible, waitForLoadingComplete, waitForFormSubmission } from './utils/wait-helpers';

// Wait for elements with appropriate timeouts
await waitForElementVisible(page, '[data-testid="dashboard"]', {
  timeout: TIMEOUTS.SLOW_RENDER
});

// Wait for loading to complete
await waitForLoadingComplete(page, {
  timeout: TIMEOUTS.DATA_LOADING,
  loadingSelectors: ['.custom-loader', '[aria-busy="true"]']
});

// Handle form submission with timeout
const result = await waitForFormSubmission(
  page,
  async () => {
    await page.click('[data-testid="submit-button"]');
  },
  {
    timeout: TIMEOUTS.FORM_SUBMISSION,
    successSelectors: ['.success-message'],
    errorSelectors: ['.error-message']
  }
);
```

## Best Practices

### 1. Choose Appropriate Timeouts
- Use **FAST** timeouts for simple operations
- Use **STANDARD** timeouts for typical operations
- Use **SLOW** timeouts for complex operations
- Use **COMPLEX** timeouts for very heavy operations

### 2. Environment Considerations
- Timeouts automatically adjust for CI and debug environments
- Set `SLOW_TESTS=true` for explicitly slow test suites
- Use `DEBUG=true` for debugging with extended timeouts

### 3. Error Handling
- All timeout utilities include proper error messages
- Failed operations include timeout duration in error messages
- Retry logic is built into API call utilities

### 4. Performance Testing
- Use `measureRenderTime()` for performance measurements
- Set appropriate thresholds based on timeout categories
- Monitor test execution times in CI

## Configuration

### Environment Variables
```bash
# Standard environment
npm test

# CI environment (automatically detected)
CI=true npm test

# Debug mode with extended timeouts
DEBUG=true npm test

# Explicitly slow test environment
SLOW_TESTS=true npm test
```

### Timeout Customization
```typescript
// Get timeout for specific operation
const timeout = getTimeoutForOperation('API_STANDARD', 1.5); // 1.5x multiplier

// Get timeout from category
const timeout = getTimeoutForCategory('SLOW', 'RENDER');

// Environment info for debugging
console.log(TIMEOUT_ENV_INFO);
// { isCI: false, isDebug: true, multiplier: 3.0, nodeEnv: 'test' }
```

## Migration Guide

### From Old Timeouts
```typescript
// OLD
await expect(element).toBeVisible({ timeout: 5000 });

// NEW
await expect(element).toBeVisible({ timeout: TEST_TIMEOUTS.STANDARD_RENDER });
```

### Enhanced Wait Functions
```typescript
// OLD
await page.waitForSelector('.loading', { state: 'hidden' });

// NEW
await waitForLoadingComplete(page, {
  timeout: TIMEOUTS.DATA_LOADING,
  loadingSelectors: ['.loading', '.spinner']
});
```

## Troubleshooting

### Test Timeouts
1. Check if environment multipliers are being applied correctly
2. Use appropriate timeout category for the operation
3. Consider if the operation genuinely needs more time
4. Check for actual performance issues in the application

### Flaky Tests
1. Use retry logic in `waitWithRetry()` for unreliable operations
2. Ensure proper loading state handling
3. Use `waitForElementStable()` for elements that might be moving
4. Add appropriate polling intervals for dynamic content

### CI Failures
1. Timeouts automatically increase in CI environments
2. Check CI-specific timeout multipliers
3. Consider network latency in CI environments
4. Review test artifacts and failure patterns

## Monitoring

The timeout configuration includes built-in monitoring:
- Environment detection and adjustment logging
- Performance measurement utilities
- Error reporting with timeout context
- Test execution time tracking

This enhanced timeout system ensures reliable test execution across different environments while maintaining good performance for faster operations.