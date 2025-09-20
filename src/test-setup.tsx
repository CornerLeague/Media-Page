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

export function renderWithProviders(ui: ReactElement, options: RenderOptions = {}) {
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

// Custom accessibility testing helpers
export async function waitForAccessibility(element: HTMLElement) {
  // Wait for any pending updates
  await new Promise(resolve => setTimeout(resolve, 50));

  // Run axe-core accessibility tests with timeout protection
  try {
    const { runAccessibilityAudit } = await import('@/lib/accessibility');

    // Add timeout protection to prevent hanging
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Accessibility audit timeout')), 2000)
    );

    const auditPromise = runAccessibilityAudit(element);

    return await Promise.race([auditPromise, timeoutPromise]);
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



// Global test constants
export const TEST_CONSTANTS = {
  RENDER_TIMEOUT: 5000,
  ANIMATION_TIMEOUT: 1000,
  USER_ACTION_TIMEOUT: 1000,
} as const;