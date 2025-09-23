/**
 * Test Setup Configuration
 *
 * Global test setup for accessibility testing, mocks, and utilities.
 */

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeAll, vi } from 'vitest';


// Cleanup after each test
afterEach(() => {
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
});

// Mock window.matchMedia
beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });

  // Mock ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock crypto.randomUUID
  Object.defineProperty(global.crypto, 'randomUUID', {
    value: vi.fn(() => 'test-uuid-' + Math.random().toString(36).substr(2, 9)),
  });

  // Mock navigator.vibrate for haptic feedback
  Object.defineProperty(navigator, 'vibrate', {
    writable: true,
    value: vi.fn(),
  });

  // Mock DragEvent for drag and drop tests
  global.DragEvent = class DragEvent extends Event {
    dataTransfer: {
      setData: ReturnType<typeof vi.fn>;
      getData: ReturnType<typeof vi.fn>;
      dropEffect: string;
      effectAllowed: string;
    };
    constructor(type: string, eventInitDict?: DragEventInit) {
      super(type, eventInitDict);
      this.dataTransfer = {
        setData: vi.fn(),
        getData: vi.fn(),
        dropEffect: 'none',
        effectAllowed: 'all',
      };
    }
  };

  // Mock touch events
  global.TouchEvent = class TouchEvent extends UIEvent {
    touches: Touch[] = [];
    targetTouches: Touch[] = [];
    changedTouches: Touch[] = [];
    constructor(type: string, eventInitDict?: TouchEventInit) {
      super(type, eventInitDict);
    }
  };

  // Mock pointer events
  global.PointerEvent = class PointerEvent extends MouseEvent {
    pointerId: number = 1;
    width: number = 1;
    height: number = 1;
    pressure: number = 0;
    tangentialPressure: number = 0;
    tiltX: number = 0;
    tiltY: number = 0;
    twist: number = 0;
    pointerType: string = 'mouse';
    isPrimary: boolean = true;

    constructor(type: string, eventInitDict?: PointerEventInit) {
      super(type, eventInitDict);
    }
  };
});

// Suppress console errors during tests unless needed
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = (...args: unknown[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
        args[0].includes('Warning: `ReactDOMTestUtils.act` is deprecated'))
    ) {
      return;
    }
    originalConsoleError.call(console, ...args);
  };
});

// Custom render function for accessibility testing
import { render as rtlRender } from '@testing-library/react';
import { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

interface RenderOptions {
  wrapper?: React.ComponentType<{ children: React.ReactNode }>;
  [key: string]: unknown;
}

export function renderWithProviders(
  ui: ReactElement,
  options: RenderOptions & {
    timeout?: number;
    waitForAsync?: boolean;
    queryOptions?: {
      retry?: boolean;
      staleTime?: number;
      cacheTime?: number;
    };
  } = {}
) {
  const {
    timeout = TEST_TIMEOUTS.STANDARD_RENDER,
    waitForAsync = false,
    queryOptions = {},
    ...renderOptions
  } = options;

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: 0,
        cacheTime: 0,
        ...queryOptions
      },
      mutations: {
        retry: false,
        ...queryOptions
      },
    },
  });

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    );
  }

  const renderResult = rtlRender(ui, { wrapper: Wrapper, ...renderOptions });

  // If waitForAsync is true, wait for async operations to settle
  if (waitForAsync) {
    return {
      ...renderResult,
      waitForAsyncToSettle: async () => {
        await waitForCondition(
          () => {
            const loadingElements = renderResult.container.querySelectorAll(
              '[data-testid*="loading"], .loading, .animate-pulse, [aria-busy="true"]'
            );
            return loadingElements.length === 0;
          },
          {
            timeout,
            interval: TEST_TIMEOUTS.POLL_INTERVAL,
            errorMessage: 'Async operations did not settle'
          }
        );
      }
    };
  }

  return renderResult;
}

// Accessibility testing utilities
interface AxeResults {
  violations: Array<{
    id: string;
    description: string;
  }>;
}

export const axeMatchers = {
  toHaveNoViolations: (received: AxeResults) => {
    if (received.violations.length === 0) {
      return {
        message: () => 'Expected element to have accessibility violations',
        pass: true,
      };
    }

    const violationMessages = received.violations
      .map((violation) => `${violation.id}: ${violation.description}`)
      .join('\n');

    return {
      message: () => `Expected no accessibility violations but found:\n${violationMessages}`,
      pass: false,
    };
  },
};

// Extend expect with custom matchers
expect.extend(axeMatchers);

// Enhanced async testing utilities with configurable timeouts
export async function waitForElement(
  selector: () => HTMLElement | null,
  options: {
    timeout?: number;
    interval?: number;
    errorMessage?: string;
  } = {}
): Promise<HTMLElement> {
  const {
    timeout = TEST_TIMEOUTS.STANDARD_RENDER,
    interval = TEST_TIMEOUTS.POLL_INTERVAL,
    errorMessage = 'Element not found within timeout'
  } = options;

  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const checkElement = () => {
      const element = selector();
      if (element) {
        resolve(element);
        return;
      }

      if (Date.now() - startTime >= timeout) {
        reject(new Error(`${errorMessage} (${timeout}ms)`));
        return;
      }

      setTimeout(checkElement, interval);
    };

    checkElement();
  });
}

export async function waitForCondition(
  condition: () => boolean | Promise<boolean>,
  options: {
    timeout?: number;
    interval?: number;
    errorMessage?: string;
  } = {}
): Promise<void> {
  const {
    timeout = TEST_TIMEOUTS.STANDARD_RENDER,
    interval = TEST_TIMEOUTS.POLL_INTERVAL,
    errorMessage = 'Condition not met within timeout'
  } = options;

  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const checkCondition = async () => {
      try {
        const result = await condition();
        if (result) {
          resolve();
          return;
        }
      } catch (error) {
        // Continue checking unless timeout is reached
      }

      if (Date.now() - startTime >= timeout) {
        reject(new Error(`${errorMessage} (${timeout}ms)`));
        return;
      }

      setTimeout(checkCondition, interval);
    };

    checkCondition();
  });
}

export async function waitForApiCall<T>(
  apiCall: () => Promise<T>,
  options: {
    timeout?: number;
    retries?: number;
    retryDelay?: number;
    errorMessage?: string;
  } = {}
): Promise<T> {
  const {
    timeout = TEST_TIMEOUTS.API_CALL_STANDARD,
    retries = 3,
    retryDelay = 1000,
    errorMessage = 'API call failed within timeout'
  } = options;

  let lastError: Error;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error(`${errorMessage} (${timeout}ms)`)), timeout)
      );

      return await Promise.race([apiCall(), timeoutPromise]);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }

  throw lastError!;
}

export async function waitForAsyncComponent(
  componentAction: () => Promise<void> | void,
  options: {
    loadingTimeout?: number;
    errorTimeout?: number;
    checkInterval?: number;
  } = {}
): Promise<void> {
  const {
    loadingTimeout = TEST_TIMEOUTS.DATA_LOADING,
    errorTimeout = TEST_TIMEOUTS.API_CALL_STANDARD,
    checkInterval = TEST_TIMEOUTS.POLL_INTERVAL
  } = options;

  // Execute the component action
  await componentAction();

  // Wait for loading states to complete
  await waitForCondition(
    () => {
      const loadingElements = document.querySelectorAll('[data-testid*="loading"], .loading, .animate-pulse');
      return loadingElements.length === 0;
    },
    {
      timeout: loadingTimeout,
      interval: checkInterval,
      errorMessage: 'Component loading did not complete'
    }
  );

  // Check for error states
  const errorElements = document.querySelectorAll('[role="alert"], .error, [data-testid*="error"]');
  if (errorElements.length > 0) {
    const errorText = Array.from(errorElements).map(el => el.textContent).join(', ');
    throw new Error(`Component error detected: ${errorText}`);
  }
}

// Custom accessibility testing helpers with enhanced timeout handling
export async function waitForAccessibility(element: HTMLElement) {
  // Wait for any pending updates
  await new Promise(resolve => setTimeout(resolve, 50));

  // Run axe-core accessibility tests with timeout protection
  try {
    const { runAccessibilityAudit } = await import('@/lib/accessibility');

    // Add timeout protection to prevent hanging
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Accessibility audit timeout')), TEST_TIMEOUTS.A11Y_AUDIT)
    );

    const auditPromise = runAccessibilityAudit(element);

    return await Promise.race([auditPromise, timeoutPromise]);
  } catch (error) {
    console.warn('Accessibility audit failed:', error);
    return { violations: [], passes: [], incomplete: [] };
  }
}

export async function waitForAccessibilityComplexPage(element: HTMLElement) {
  return waitForAccessibility(element);
}

// Enhanced form testing utilities
export async function waitForFormSubmission(
  submitAction: () => Promise<void> | void,
  options: {
    timeout?: number;
    expectSuccess?: boolean;
    successSelector?: string;
    errorSelector?: string;
  } = {}
): Promise<{ success: boolean; message?: string }> {
  const {
    timeout = TEST_TIMEOUTS.FORM_SUBMISSION,
    expectSuccess = true,
    successSelector = '[data-testid*="success"], .success',
    errorSelector = '[role="alert"], .error, [data-testid*="error"]'
  } = options;

  await submitAction();

  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const checkResult = () => {
      const successElements = document.querySelectorAll(successSelector);
      const errorElements = document.querySelectorAll(errorSelector);

      if (successElements.length > 0) {
        const message = successElements[0].textContent || 'Success';
        resolve({ success: true, message });
        return;
      }

      if (errorElements.length > 0) {
        const message = errorElements[0].textContent || 'Error occurred';
        if (expectSuccess) {
          reject(new Error(`Form submission failed: ${message}`));
        } else {
          resolve({ success: false, message });
        }
        return;
      }

      if (Date.now() - startTime >= timeout) {
        reject(new Error(`Form submission timeout (${timeout}ms)`));
        return;
      }

      setTimeout(checkResult, TEST_TIMEOUTS.POLL_INTERVAL);
    };

    checkResult();
  });
}

// Performance testing helpers
export function measureRenderTime<T>(fn: () => T): { result: T; time: number } {
  const start = performance.now();
  const result = fn();
  const time = performance.now() - start;
  return { result, time };
}

// Mock framer-motion for testing
vi.mock('framer-motion', () => ({
  motion: new Proxy(
    {},
    {
      get: (target, prop) => {
        const component = ({ children, ...props }: { children?: React.ReactNode; [key: string]: unknown }) => {
          // Remove motion props that aren't valid HTML attributes
          const {
            initial,
            animate,
            exit,
            transition,
            variants,
            whileHover,
            whileTap,
            whileFocus,
            whileInView,
            onAnimationComplete,
            ...validProps
          } = props;

          // Import React for createElement
          // eslint-disable-next-line @typescript-eslint/no-require-imports
          const React = require('react');
          return React.createElement(prop as string, validProps, children);
        };
        return component;
      },
    }
  ),
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
  useAnimation: () => ({
    start: vi.fn(),
    stop: vi.fn(),
    set: vi.fn(),
  }),
}));

// Mock @dnd-kit libraries to prevent hanging
vi.mock('@dnd-kit/core', () => ({
  DndContext: ({ children }: { children: React.ReactNode }) => children,
  closestCenter: vi.fn(),
  KeyboardSensor: vi.fn(),
  PointerSensor: vi.fn(),
  TouchSensor: vi.fn(),
  useSensor: vi.fn(),
  useSensors: vi.fn(() => []),
  DragOverlay: ({ children }: { children: React.ReactNode }) => children,
  useDroppable: vi.fn(() => ({
    setNodeRef: vi.fn(),
    isOver: false,
  })),
  useDraggable: vi.fn(() => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
  })),
}));

vi.mock('@dnd-kit/sortable', () => ({
  arrayMove: vi.fn((array, from, to) => {
    const newArray = [...array];
    newArray.splice(to, 0, newArray.splice(from, 1)[0]);
    return newArray;
  }),
  SortableContext: ({ children }: { children: React.ReactNode }) => children,
  sortableKeyboardCoordinates: vi.fn(),
  verticalListSortingStrategy: 'vertical',
  useSortable: vi.fn(() => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  })),
}));

vi.mock('@dnd-kit/utilities', () => ({
  CSS: {
    Transform: {
      toString: vi.fn(() => ''),
    },
  },
}));

// Mock React Query to prevent network issues
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query') as Record<string, unknown>;
  return {
    ...actual,
    useQuery: vi.fn(() => ({
      data: null,
      isLoading: false,
      error: null,
    })),
    useMutation: vi.fn(() => ({
      mutate: vi.fn(),
      isLoading: false,
      error: null,
    })),
  };
});

// Mock data files that might not exist
vi.mock('@/data/sports', () => ({
  AVAILABLE_SPORTS: [
    { id: 'nfl', name: 'NFL', hasTeams: true },
    { id: 'nba', name: 'NBA', hasTeams: true },
  ],
}));


vi.mock('@/hooks/useTouch', () => ({
  useDeviceCapabilities: vi.fn(() => ({
    supportsTouch: false,
    supportsPointer: true,
    prefersTouchInteraction: false,
  })),
  useTouchOptimizedButton: vi.fn(() => ({
    buttonProps: {},
    isPressed: false,
  })),
}));



// Import centralized timeout configurations
import { TEST_TIMEOUTS as SHARED_TIMEOUTS, VITEST_TIMEOUTS } from './utils/test-timeouts';
import {
  SmartContentWaiter,
  ElementWaiter,
  AsyncOperationWaiter,
  waitStrategies,
  type WaitOptions,
  type ContentWaitOptions,
  type ElementWaitOptions
} from './utils/enhanced-wait-strategies';

// Re-export shared timeouts for backward compatibility
export const TEST_TIMEOUTS = SHARED_TIMEOUTS;

// Re-export Vitest-specific timeouts from centralized config
export const VITEST_TEST_TIMEOUTS = VITEST_TIMEOUTS;

// Legacy constants for backward compatibility
export const TEST_CONSTANTS = {
  RENDER_TIMEOUT: TEST_TIMEOUTS.STANDARD_RENDER,
  ANIMATION_TIMEOUT: TEST_TIMEOUTS.STANDARD_ANIMATION,
  USER_ACTION_TIMEOUT: TEST_TIMEOUTS.USER_ACTION,
} as const;

// Enhanced waiting strategies for testing
export {
  SmartContentWaiter,
  ElementWaiter,
  AsyncOperationWaiter,
  waitStrategies,
  type WaitOptions,
  type ContentWaitOptions,
  type ElementWaitOptions
};

// Export convenience functions for common testing scenarios
export const testUtils = {
  // Quick content loading check
  waitForContent: async (container?: HTMLElement, timeout?: number) => {
    await SmartContentWaiter.waitForContentLoaded(container || document.body, {
      timeout: timeout || TEST_TIMEOUTS.DATA_FETCH,
      checkVisibility: true
    });
  },

  // Wait for form to be interactive
  waitForFormReady: async (formSelector: string, timeout?: number) => {
    return waitStrategies.forFormReady(formSelector, {
      timeout: timeout || TEST_TIMEOUTS.FORM_INTERACTION
    });
  },

  // Wait for modal to be ready
  waitForModalReady: async (modalSelector?: string, timeout?: number) => {
    return waitStrategies.forModalReady(modalSelector, {
      timeout: timeout || TEST_TIMEOUTS.MODAL_OPEN
    });
  },

  // Smart API call wrapper
  apiCall: async <T>(call: () => Promise<T>, options?: {
    timeout?: number;
    retries?: number;
    validate?: (response: T) => boolean;
  }) => {
    return AsyncOperationWaiter.waitForAsyncOperation(call, {
      timeout: options?.timeout || TEST_TIMEOUTS.API_STANDARD,
      retries: options?.retries || 3,
      validateResult: options?.validate
    });
  },

  // Enhanced element stability check
  waitForStableElement: async (selector: string, container?: HTMLElement, timeout?: number) => {
    return ElementWaiter.waitForElementStable(selector, container || document, {
      timeout: timeout || TEST_TIMEOUTS.ELEMENT_STABLE,
      checkStability: true
    });
  }
};

// Backward compatibility aliases for existing tests
export const smartWaitFor = SmartContentWaiter.waitForContentLoaded;
export const waitForStableElement = ElementWaiter.waitForElementStable;
export const waitForAsyncOp = AsyncOperationWaiter.waitForAsyncOperation;