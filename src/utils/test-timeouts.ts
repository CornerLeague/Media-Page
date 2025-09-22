/**
 * Comprehensive Test Timeout Configuration
 *
 * Centralized timeout configurations for all test frameworks (Vitest, Playwright)
 * with environment-aware adjustments and detailed categorization.
 */

// Environment detection for timeout adjustments
const isCI = process.env.CI === 'true';
const isDebug = process.env.DEBUG === 'true' || process.env.NODE_ENV === 'test-debug';
const isSlow = process.env.SLOW_TESTS === 'true';

// Base multipliers for different environments
const ENV_MULTIPLIERS = {
  ci: 2.0,          // CI environments are often slower
  debug: 5.0,       // Debug mode needs longer timeouts
  slow: 3.0,        // Explicitly slow test environment
  normal: 1.0       // Standard development environment
} as const;

function getEnvironmentMultiplier(): number {
  if (isDebug) return ENV_MULTIPLIERS.debug;
  if (isCI) return ENV_MULTIPLIERS.ci;
  if (isSlow) return ENV_MULTIPLIERS.slow;
  return ENV_MULTIPLIERS.normal;
}

function adjustTimeout(baseTimeout: number): number {
  return Math.round(baseTimeout * getEnvironmentMultiplier());
}

// Base timeout values (in milliseconds)
const BASE_TIMEOUTS = {
  // Component Rendering Timeouts
  INSTANT: 100,                    // Immediate operations
  FAST_RENDER: 500,               // Simple components
  STANDARD_RENDER: 2000,          // Standard components
  SLOW_RENDER: 5000,              // Complex components with data
  COMPLEX_RENDER: 8000,           // Very complex components

  // Animation and Transition Timeouts
  MICRO_ANIMATION: 150,           // Micro-interactions
  FAST_ANIMATION: 300,            // Quick animations
  STANDARD_ANIMATION: 1000,       // Standard animations
  SLOW_ANIMATION: 2500,           // Complex animations
  COMPLEX_ANIMATION: 4000,        // Multi-stage animations

  // User Interaction Timeouts
  CLICK: 500,                     // Simple clicks
  USER_ACTION: 1000,              // Standard user actions
  USER_ACTION_SLOW: 2500,         // Complex user interactions
  FORM_INTERACTION: 3000,         // Form filling and validation

  // API and Network Timeouts
  API_FAST: 1500,                 // Fast API calls
  API_STANDARD: 3000,             // Standard API calls
  API_SLOW: 6000,                 // Slow API calls
  API_COMPLEX: 10000,             // Complex API operations
  NETWORK_REQUEST: 3000,          // General network requests
  NETWORK_SLOW: 8000,             // Slow network operations

  // Component-Specific Timeouts
  MODAL_OPEN: 1500,               // Modal opening/closing
  DROPDOWN_OPEN: 800,             // Dropdown opening
  TOOLTIP_SHOW: 400,              // Tooltip display
  SIDEBAR_TOGGLE: 600,            // Sidebar animations
  TAB_SWITCH: 500,                // Tab switching
  ACCORDION_TOGGLE: 700,          // Accordion expand/collapse

  // Form Operation Timeouts
  FORM_VALIDATION: 1000,          // Form validation
  FORM_SUBMISSION: 4000,          // Form submission
  FORM_SUBMISSION_SLOW: 8000,     // Slow form operations
  FILE_UPLOAD_SMALL: 5000,        // Small file uploads
  FILE_UPLOAD_LARGE: 15000,       // Large file uploads

  // Data Loading Timeouts
  DATA_FETCH: 3000,               // Standard data fetching
  DATA_FETCH_SLOW: 6000,          // Slow data operations
  LIST_LOAD: 2000,                // List loading
  TABLE_LOAD: 4000,               // Table data loading
  SEARCH_RESULTS: 2500,           // Search operations

  // Accessibility Testing Timeouts
  A11Y_AUDIT_BASIC: 3000,         // Basic accessibility audit
  A11Y_AUDIT_STANDARD: 5000,      // Standard accessibility audit
  A11Y_AUDIT_COMPLEX: 8000,       // Complex page audit
  A11Y_AUDIT_FULL: 12000,         // Comprehensive audit

  // Authentication and Authorization
  AUTH_LOGIN: 3000,               // Login operations
  AUTH_LOGOUT: 2000,              // Logout operations
  AUTH_TOKEN_REFRESH: 2500,       // Token refresh
  AUTH_SOCIAL: 5000,              // Social login (OAuth)

  // Page Navigation Timeouts
  PAGE_LOAD: 5000,                // Page loading
  PAGE_LOAD_SLOW: 10000,          // Slow page loading
  ROUTE_CHANGE: 2000,             // Route changes
  DEEP_LINK: 3000,                // Deep link navigation

  // Test Environment Timeouts
  SETUP: 2000,                    // Test setup
  TEARDOWN: 1500,                 // Test cleanup
  MOCK_SETUP: 500,                // Mock setup
  JSDOM_SETUP: 1500,              // JSDOM initialization

  // Polling and Retry Configuration
  POLL_INTERVAL: 50,              // Fast polling interval
  POLL_INTERVAL_STANDARD: 100,    // Standard polling interval
  POLL_INTERVAL_SLOW: 250,        // Slow polling interval
  RETRY_DELAY: 500,               // Retry delay
  RETRY_DELAY_SLOW: 1000,         // Slow retry delay

  // Browser-Specific Timeouts
  BROWSER_READY: 2000,            // Browser ready state
  VIEWPORT_CHANGE: 800,           // Viewport changes
  SCROLL_ANIMATION: 600,          // Scroll animations
  FOCUS_CHANGE: 300,              // Focus changes

  // Performance Testing
  PERFORMANCE_MEASURE: 5000,      // Performance measurements
  MEMORY_LEAK_CHECK: 8000,        // Memory leak detection
} as const;

// Environment-adjusted timeouts
export const TEST_TIMEOUTS = Object.fromEntries(
  Object.entries(BASE_TIMEOUTS).map(([key, value]) => [
    key,
    adjustTimeout(value)
  ])
) as Record<keyof typeof BASE_TIMEOUTS, number>;

// Playwright-specific timeout configurations
export const PLAYWRIGHT_TIMEOUTS = {
  // Page timeouts
  PAGE_LOAD: adjustTimeout(10000),
  PAGE_LOAD_SLOW: adjustTimeout(20000),
  NAVIGATION: adjustTimeout(15000),

  // Action timeouts
  ACTION_DEFAULT: adjustTimeout(5000),
  ACTION_SLOW: adjustTimeout(10000),

  // Element wait timeouts
  ELEMENT_VISIBLE: adjustTimeout(5000),
  ELEMENT_HIDDEN: adjustTimeout(3000),
  ELEMENT_STABLE: adjustTimeout(2000),

  // Network timeouts
  NETWORK_IDLE: adjustTimeout(8000),
  LOAD_STATE: adjustTimeout(10000),

  // Test execution timeouts
  TEST_TIMEOUT: adjustTimeout(30000),
  TEST_TIMEOUT_SLOW: adjustTimeout(60000),

  // Browser context timeouts
  CONTEXT_SETUP: adjustTimeout(5000),
  CONTEXT_TEARDOWN: adjustTimeout(3000),
} as const;

// Vitest-specific timeout configurations
export const VITEST_TIMEOUTS = {
  // Test execution
  TEST_TIMEOUT: adjustTimeout(5000),
  TEST_TIMEOUT_SLOW: adjustTimeout(10000),

  // Hook timeouts
  HOOK_TIMEOUT: adjustTimeout(3000),
  HOOK_TIMEOUT_SLOW: adjustTimeout(6000),

  // Async operations
  ASYNC_TIMEOUT: adjustTimeout(8000),
  MOCK_TIMEOUT: adjustTimeout(2000),
} as const;

// Timeout categories for easy selection
export const TIMEOUT_CATEGORIES = {
  // Quick operations (< 1 second)
  QUICK: {
    INSTANT: TEST_TIMEOUTS.INSTANT,
    MICRO_ANIMATION: TEST_TIMEOUTS.MICRO_ANIMATION,
    FAST_ANIMATION: TEST_TIMEOUTS.FAST_ANIMATION,
    CLICK: TEST_TIMEOUTS.CLICK,
    POLL_INTERVAL: TEST_TIMEOUTS.POLL_INTERVAL,
  },

  // Standard operations (1-3 seconds)
  STANDARD: {
    RENDER: TEST_TIMEOUTS.STANDARD_RENDER,
    ANIMATION: TEST_TIMEOUTS.STANDARD_ANIMATION,
    USER_ACTION: TEST_TIMEOUTS.USER_ACTION,
    API_CALL: TEST_TIMEOUTS.API_STANDARD,
    DATA_FETCH: TEST_TIMEOUTS.DATA_FETCH,
  },

  // Slow operations (3-8 seconds)
  SLOW: {
    RENDER: TEST_TIMEOUTS.SLOW_RENDER,
    ANIMATION: TEST_TIMEOUTS.SLOW_ANIMATION,
    USER_ACTION: TEST_TIMEOUTS.USER_ACTION_SLOW,
    API_CALL: TEST_TIMEOUTS.API_SLOW,
    FORM_SUBMISSION: TEST_TIMEOUTS.FORM_SUBMISSION,
  },

  // Complex operations (8+ seconds)
  COMPLEX: {
    RENDER: TEST_TIMEOUTS.COMPLEX_RENDER,
    ANIMATION: TEST_TIMEOUTS.COMPLEX_ANIMATION,
    API_CALL: TEST_TIMEOUTS.API_COMPLEX,
    A11Y_AUDIT: TEST_TIMEOUTS.A11Y_AUDIT_COMPLEX,
    FILE_UPLOAD: TEST_TIMEOUTS.FILE_UPLOAD_LARGE,
  },
} as const;

// Utility functions for timeout selection
export function getTimeoutForOperation(
  operation: keyof typeof TEST_TIMEOUTS,
  multiplier: number = 1
): number {
  return Math.round(TEST_TIMEOUTS[operation] * multiplier);
}

export function getTimeoutForCategory(
  category: keyof typeof TIMEOUT_CATEGORIES,
  operation: string
): number {
  const categoryTimeouts = TIMEOUT_CATEGORIES[category];
  const timeout = (categoryTimeouts as any)[operation];

  if (!timeout) {
    console.warn(`Timeout not found for ${category}.${operation}, using standard render timeout`);
    return TEST_TIMEOUTS.STANDARD_RENDER;
  }

  return timeout;
}

// Environment information for debugging
export const TIMEOUT_ENV_INFO = {
  isCI,
  isDebug,
  isSlow,
  multiplier: getEnvironmentMultiplier(),
  nodeEnv: process.env.NODE_ENV,
} as const;

// Legacy compatibility (for existing tests)
export const TEST_CONSTANTS = {
  RENDER_TIMEOUT: TEST_TIMEOUTS.STANDARD_RENDER,
  ANIMATION_TIMEOUT: TEST_TIMEOUTS.STANDARD_ANIMATION,
  USER_ACTION_TIMEOUT: TEST_TIMEOUTS.USER_ACTION,
} as const;

// Export commonly used timeout presets
export const QUICK_TIMEOUTS = TIMEOUT_CATEGORIES.QUICK;
export const STANDARD_TIMEOUTS = TIMEOUT_CATEGORIES.STANDARD;
export const SLOW_TIMEOUTS = TIMEOUT_CATEGORIES.SLOW;
export const COMPLEX_TIMEOUTS = TIMEOUT_CATEGORIES.COMPLEX;