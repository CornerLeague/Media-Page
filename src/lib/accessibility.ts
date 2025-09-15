/**
 * Accessibility Utilities
 *
 * This module provides utilities for accessibility testing, ARIA management,
 * focus handling, and keyboard navigation support.
 */

import React, { useEffect, useRef, useCallback } from 'react';

// ARIA Live Region Types
export type LiveRegionPoliteness = 'off' | 'polite' | 'assertive';

// Focus Management Hook
export const useFocusManagement = () => {
  const focusableElementsSelector = [
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    'a[href]',
    'area[href]',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable]:not([contenteditable="false"])',
  ].join(', ');

  const getFocusableElements = useCallback((container: HTMLElement): HTMLElement[] => {
    return Array.from(container.querySelectorAll(focusableElementsSelector));
  }, [focusableElementsSelector]);

  const trapFocus = useCallback((container: HTMLElement) => {
    const focusableElements = getFocusableElements(container);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);

    // Focus the first element when trap is activated
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }, [getFocusableElements]);

  const restoreFocus = useCallback(() => {
    const activeElement = document.activeElement as HTMLElement;
    if (activeElement && activeElement.blur) {
      activeElement.blur();
    }
  }, []);

  return {
    getFocusableElements,
    trapFocus,
    restoreFocus,
  };
};

// Keyboard Navigation Hook
export const useKeyboardNavigation = (
  onEnter?: () => void,
  onEscape?: () => void,
  onArrowKeys?: (direction: 'up' | 'down' | 'left' | 'right') => void
) => {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    switch (e.key) {
      case 'Enter':
        if (onEnter) {
          e.preventDefault();
          onEnter();
        }
        break;
      case 'Escape':
        if (onEscape) {
          e.preventDefault();
          onEscape();
        }
        break;
      case 'ArrowUp':
        if (onArrowKeys) {
          e.preventDefault();
          onArrowKeys('up');
        }
        break;
      case 'ArrowDown':
        if (onArrowKeys) {
          e.preventDefault();
          onArrowKeys('down');
        }
        break;
      case 'ArrowLeft':
        if (onArrowKeys) {
          e.preventDefault();
          onArrowKeys('left');
        }
        break;
      case 'ArrowRight':
        if (onArrowKeys) {
          e.preventDefault();
          onArrowKeys('right');
        }
        break;
    }
  }, [onEnter, onEscape, onArrowKeys]);

  return { handleKeyDown };
};

// Live Region Hook for Screen Reader Announcements
export const useLiveRegion = (politeness: LiveRegionPoliteness = 'polite') => {
  const liveRegionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Create live region if it doesn't exist
    if (!liveRegionRef.current) {
      const liveRegion = document.createElement('div');
      liveRegion.setAttribute('aria-live', politeness);
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.setAttribute('class', 'sr-only');
      liveRegion.style.position = 'absolute';
      liveRegion.style.left = '-10000px';
      liveRegion.style.width = '1px';
      liveRegion.style.height = '1px';
      liveRegion.style.overflow = 'hidden';

      document.body.appendChild(liveRegion);
      liveRegionRef.current = liveRegion;
    }

    return () => {
      if (liveRegionRef.current) {
        document.body.removeChild(liveRegionRef.current);
        liveRegionRef.current = null;
      }
    };
  }, [politeness]);

  const announce = useCallback((message: string, priority: LiveRegionPoliteness = politeness) => {
    if (liveRegionRef.current) {
      // Update politeness if different
      if (liveRegionRef.current.getAttribute('aria-live') !== priority) {
        liveRegionRef.current.setAttribute('aria-live', priority);
      }

      // Clear and then set the message to ensure it's announced
      liveRegionRef.current.textContent = '';
      setTimeout(() => {
        if (liveRegionRef.current) {
          liveRegionRef.current.textContent = message;
        }
      }, 100);
    }
  }, [politeness]);

  return { announce };
};

// Skip Link Component Helper
export const useSkipLink = () => {
  const skipLinkRef = useRef<HTMLAnchorElement>(null);

  const createSkipLink = useCallback((targetId: string, label: string = 'Skip to main content') => {
    const skipLink = document.createElement('a');
    skipLink.href = `#${targetId}`;
    skipLink.textContent = label;
    skipLink.className = 'skip-link sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-foreground';

    // Insert at the beginning of the document
    document.body.insertBefore(skipLink, document.body.firstChild);
    skipLinkRef.current = skipLink;

    return () => {
      if (skipLinkRef.current) {
        document.body.removeChild(skipLinkRef.current);
        skipLinkRef.current = null;
      }
    };
  }, []);

  return { createSkipLink };
};

// High Contrast Mode Detection
export const useHighContrastMode = () => {
  const [isHighContrast, setIsHighContrast] = React.useState(false);

  React.useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');

    const updateHighContrast = () => {
      setIsHighContrast(mediaQuery.matches);
    };

    updateHighContrast();
    mediaQuery.addEventListener('change', updateHighContrast);

    return () => {
      mediaQuery.removeEventListener('change', updateHighContrast);
    };
  }, []);

  return isHighContrast;
};

// Reduced Motion Detection
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState(false);

  React.useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const updateMotionPreference = () => {
      setPrefersReducedMotion(mediaQuery.matches);
    };

    updateMotionPreference();
    mediaQuery.addEventListener('change', updateMotionPreference);

    return () => {
      mediaQuery.removeEventListener('change', updateMotionPreference);
    };
  }, []);

  return prefersReducedMotion;
};

// Color Contrast Utilities
export const getContrastRatio = (color1: string, color2: string): number => {
  const getLuminance = (color: string): number => {
    // Convert hex to RGB
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16) / 255;
    const g = parseInt(hex.substr(2, 2), 16) / 255;
    const b = parseInt(hex.substr(4, 2), 16) / 255;

    // Calculate relative luminance
    const getRGB = (c: number) => {
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    };

    return 0.2126 * getRGB(r) + 0.7152 * getRGB(g) + 0.0722 * getRGB(b);
  };

  const lum1 = getLuminance(color1);
  const lum2 = getLuminance(color2);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);

  return (brightest + 0.05) / (darkest + 0.05);
};

export const meetsWCAGStandards = (
  color1: string,
  color2: string,
  level: 'AA' | 'AAA' = 'AA',
  size: 'normal' | 'large' = 'normal'
): boolean => {
  const ratio = getContrastRatio(color1, color2);

  if (level === 'AAA') {
    return size === 'large' ? ratio >= 4.5 : ratio >= 7;
  }

  return size === 'large' ? ratio >= 3 : ratio >= 4.5;
};

// ARIA Utilities
export const generateAriaAttributes = (options: {
  label?: string;
  labelledBy?: string;
  describedBy?: string;
  expanded?: boolean;
  selected?: boolean;
  pressed?: boolean;
  current?: boolean | 'page' | 'step' | 'location' | 'date' | 'time';
  level?: number;
  posInSet?: number;
  setSize?: number;
  live?: LiveRegionPoliteness;
  atomic?: boolean;
  busy?: boolean;
  invalid?: boolean;
  required?: boolean;
  disabled?: boolean;
  hidden?: boolean;
}) => {
  const attrs: Record<string, any> = {};

  if (options.label) attrs['aria-label'] = options.label;
  if (options.labelledBy) attrs['aria-labelledby'] = options.labelledBy;
  if (options.describedBy) attrs['aria-describedby'] = options.describedBy;
  if (typeof options.expanded === 'boolean') attrs['aria-expanded'] = options.expanded;
  if (typeof options.selected === 'boolean') attrs['aria-selected'] = options.selected;
  if (typeof options.pressed === 'boolean') attrs['aria-pressed'] = options.pressed;
  if (options.current !== undefined) attrs['aria-current'] = options.current;
  if (options.level) attrs['aria-level'] = options.level;
  if (options.posInSet) attrs['aria-posinset'] = options.posInSet;
  if (options.setSize) attrs['aria-setsize'] = options.setSize;
  if (options.live) attrs['aria-live'] = options.live;
  if (typeof options.atomic === 'boolean') attrs['aria-atomic'] = options.atomic;
  if (typeof options.busy === 'boolean') attrs['aria-busy'] = options.busy;
  if (typeof options.invalid === 'boolean') attrs['aria-invalid'] = options.invalid;
  if (typeof options.required === 'boolean') attrs['aria-required'] = options.required;
  if (typeof options.disabled === 'boolean') attrs['aria-disabled'] = options.disabled;
  if (typeof options.hidden === 'boolean') attrs['aria-hidden'] = options.hidden;

  return attrs;
};

// Accessibility Testing Helper
export const runAccessibilityAudit = async (element: HTMLElement): Promise<{
  violations: any[];
  passes: any[];
  incomplete: any[];
}> => {
  try {
    // Dynamic import to avoid bundling axe-core in production
    const axe = await import('axe-core');
    const results = await axe.run(element);

    return {
      violations: results.violations,
      passes: results.passes,
      incomplete: results.incomplete,
    };
  } catch (error) {
    console.error('Accessibility audit failed:', error);
    return {
      violations: [],
      passes: [],
      incomplete: [],
    };
  }
};