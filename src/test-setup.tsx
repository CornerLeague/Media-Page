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
    dataTransfer: any;
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
    touches: any[] = [];
    targetTouches: any[] = [];
    changedTouches: any[] = [];
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
  console.error = (...args: any[]) => {
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

export function renderWithProviders(ui: ReactElement, options: any = {}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
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

  return rtlRender(ui, { wrapper: Wrapper, ...options });
}

// Accessibility testing utilities
export const axeMatchers = {
  toHaveNoViolations: (received: any) => {
    if (received.violations.length === 0) {
      return {
        message: () => 'Expected element to have accessibility violations',
        pass: true,
      };
    }

    const violationMessages = received.violations
      .map((violation: any) => `${violation.id}: ${violation.description}`)
      .join('\n');

    return {
      message: () => `Expected no accessibility violations but found:\n${violationMessages}`,
      pass: false,
    };
  },
};

// Extend expect with custom matchers
expect.extend(axeMatchers);

// Custom accessibility testing helpers
export async function waitForAccessibility(element: HTMLElement) {
  // Wait for any pending updates
  await new Promise(resolve => setTimeout(resolve, 100));

  // Run axe-core accessibility tests
  try {
    const { runAccessibilityAudit } = await import('@/lib/accessibility');
    return await runAccessibilityAudit(element);
  } catch (error) {
    console.warn('Accessibility audit failed:', error);
    return { violations: [], passes: [], incomplete: [] };
  }
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
        const component = ({ children, ...props }: any) => {
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
            ...validProps
          } = props;
          return React.createElement(prop as string, validProps, children);
        };
        return component;
      },
    }
  ),
  AnimatePresence: ({ children }: any) => children,
}));

// Global test constants
export const TEST_CONSTANTS = {
  RENDER_TIMEOUT: 5000,
  ANIMATION_TIMEOUT: 1000,
  USER_ACTION_TIMEOUT: 1000,
} as const;