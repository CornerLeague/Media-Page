/**
 * Touch and Gesture Hooks for Mobile Optimization
 *
 * This module provides hooks for handling touch events, gestures, and mobile-specific interactions.
 * It includes swipe detection, long press, tap handling, and device capability detection.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

// Touch event types
interface TouchPosition {
  x: number;
  y: number;
}

interface SwipeConfig {
  minSwipeDistance: number;
  maxSwipeTime: number;
  preventDefaultTouchmoveEvent: boolean;
  deltaDirection: 'x' | 'y';
}

interface SwipeHandlers {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onSwipeStart?: (event: TouchEvent) => void;
  onSwipeEnd?: (event: TouchEvent) => void;
}

const defaultSwipeConfig: SwipeConfig = {
  minSwipeDistance: 50,
  maxSwipeTime: 500,
  preventDefaultTouchmoveEvent: false,
  deltaDirection: 'x',
};

// Device capability detection
export const useDeviceCapabilities = () => {
  const [capabilities, setCapabilities] = useState({
    isTouchDevice: false,
    isIOSDevice: false,
    isAndroidDevice: false,
    hasHapticFeedback: false,
    supportsPointerEvents: false,
    screenSize: 'desktop' as 'mobile' | 'tablet' | 'desktop',
    orientation: 'portrait' as 'portrait' | 'landscape',
  });

  useEffect(() => {
    const detectCapabilities = () => {
      const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;

      setCapabilities({
        isTouchDevice: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
        isIOSDevice: /iPad|iPhone|iPod/.test(userAgent) && !(window as any).MSStream,
        isAndroidDevice: /Android/.test(userAgent),
        hasHapticFeedback: 'vibrate' in navigator,
        supportsPointerEvents: 'PointerEvent' in window,
        screenSize: window.innerWidth < 768 ? 'mobile' : window.innerWidth < 1024 ? 'tablet' : 'desktop',
        orientation: window.innerHeight > window.innerWidth ? 'portrait' : 'landscape',
      });
    };

    detectCapabilities();

    const handleResize = () => {
      setCapabilities(prev => ({
        ...prev,
        screenSize: window.innerWidth < 768 ? 'mobile' : window.innerWidth < 1024 ? 'tablet' : 'desktop',
        orientation: window.innerHeight > window.innerWidth ? 'portrait' : 'landscape',
      }));
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  return capabilities;
};

// Swipe gesture hook
export const useSwipeGesture = (
  handlers: SwipeHandlers,
  config: Partial<SwipeConfig> = {}
) => {
  const element = useRef<HTMLElement | null>(null);
  const touchStart = useRef<TouchPosition | null>(null);
  const touchEnd = useRef<TouchPosition | null>(null);
  const swipeStartTime = useRef<number>(0);

  const fullConfig = { ...defaultSwipeConfig, ...config };

  const handleTouchStart = useCallback((e: TouchEvent) => {
    touchEnd.current = null;
    touchStart.current = {
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    };
    swipeStartTime.current = Date.now();
    handlers.onSwipeStart?.(e);
  }, [handlers]);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (fullConfig.preventDefaultTouchmoveEvent) {
      e.preventDefault();
    }
  }, [fullConfig.preventDefaultTouchmoveEvent]);

  const handleTouchEnd = useCallback((e: TouchEvent) => {
    if (!touchStart.current) return;

    touchEnd.current = {
      x: e.changedTouches[0].clientX,
      y: e.changedTouches[0].clientY,
    };

    const swipeTime = Date.now() - swipeStartTime.current;
    if (swipeTime > fullConfig.maxSwipeTime) return;

    const deltaX = touchStart.current.x - touchEnd.current.x;
    const deltaY = touchStart.current.y - touchEnd.current.y;
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);

    // Determine primary swipe direction
    const isHorizontalSwipe = absDeltaX > absDeltaY;
    const primaryDelta = isHorizontalSwipe ? absDeltaX : absDeltaY;

    if (primaryDelta < fullConfig.minSwipeDistance) return;

    // Call appropriate handler based on direction
    if (isHorizontalSwipe) {
      if (deltaX > 0) {
        handlers.onSwipeLeft?.();
      } else {
        handlers.onSwipeRight?.();
      }
    } else {
      if (deltaY > 0) {
        handlers.onSwipeUp?.();
      } else {
        handlers.onSwipeDown?.();
      }
    }

    handlers.onSwipeEnd?.(e);
  }, [handlers, fullConfig]);

  const attachSwipeListeners = useCallback((el: HTMLElement | null) => {
    if (element.current) {
      element.current.removeEventListener('touchstart', handleTouchStart);
      element.current.removeEventListener('touchmove', handleTouchMove);
      element.current.removeEventListener('touchend', handleTouchEnd);
    }

    element.current = el;

    if (el) {
      el.addEventListener('touchstart', handleTouchStart, { passive: true });
      el.addEventListener('touchmove', handleTouchMove, { passive: !fullConfig.preventDefaultTouchmoveEvent });
      el.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
  }, [handleTouchStart, handleTouchMove, handleTouchEnd, fullConfig.preventDefaultTouchmoveEvent]);

  useEffect(() => {
    return () => {
      if (element.current) {
        element.current.removeEventListener('touchstart', handleTouchStart);
        element.current.removeEventListener('touchmove', handleTouchMove);
        element.current.removeEventListener('touchend', handleTouchEnd);
      }
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd]);

  return { attachSwipeListeners };
};

// Long press hook
export const useLongPress = (
  onLongPress: (event: MouseEvent | TouchEvent) => void,
  options: {
    delay?: number;
    shouldPreventDefault?: boolean;
    threshold?: number;
  } = {}
) => {
  const {
    delay = 500,
    shouldPreventDefault = true,
    threshold = 10,
  } = options;

  const timeout = useRef<NodeJS.Timeout>();
  const target = useRef<EventTarget>();
  const startPos = useRef<{ x: number; y: number }>();

  const start = useCallback((event: MouseEvent | TouchEvent) => {
    if (shouldPreventDefault) {
      event.preventDefault();
    }

    const pos = 'touches' in event ? {
      x: event.touches[0].clientX,
      y: event.touches[0].clientY,
    } : {
      x: event.clientX,
      y: event.clientY,
    };

    startPos.current = pos;
    target.current = event.target;

    timeout.current = setTimeout(() => {
      onLongPress(event);
    }, delay);
  }, [onLongPress, delay, shouldPreventDefault]);

  const clear = useCallback((event: MouseEvent | TouchEvent, shouldTriggerClick = true) => {
    timeout.current && clearTimeout(timeout.current);
    target.current = undefined;
    startPos.current = undefined;
  }, []);

  const move = useCallback((event: MouseEvent | TouchEvent) => {
    if (!startPos.current) return;

    const pos = 'touches' in event ? {
      x: event.touches[0].clientX,
      y: event.touches[0].clientY,
    } : {
      x: event.clientX,
      y: event.clientY,
    };

    const distance = Math.sqrt(
      Math.pow(pos.x - startPos.current.x, 2) +
      Math.pow(pos.y - startPos.current.y, 2)
    );

    if (distance > threshold) {
      clear(event);
    }
  }, [clear, threshold]);

  return {
    onMouseDown: start,
    onMouseUp: clear,
    onMouseLeave: clear,
    onMouseMove: move,
    onTouchStart: start,
    onTouchEnd: clear,
    onTouchMove: move,
  };
};

// Haptic feedback hook
export const useHapticFeedback = () => {
  const { hasHapticFeedback } = useDeviceCapabilities();

  const triggerHaptic = useCallback((
    pattern: 'light' | 'medium' | 'heavy' | 'notification' | 'error' | 'success' | number[]
  ) => {
    if (!hasHapticFeedback) return;

    try {
      switch (pattern) {
        case 'light':
          navigator.vibrate(10);
          break;
        case 'medium':
          navigator.vibrate(20);
          break;
        case 'heavy':
          navigator.vibrate(50);
          break;
        case 'notification':
          navigator.vibrate([100, 50, 100]);
          break;
        case 'error':
          navigator.vibrate([200, 100, 200, 100, 200]);
          break;
        case 'success':
          navigator.vibrate([50, 25, 50]);
          break;
        default:
          if (Array.isArray(pattern)) {
            navigator.vibrate(pattern);
          }
      }
    } catch (error) {
      console.warn('Haptic feedback failed:', error);
    }
  }, [hasHapticFeedback]);

  return { triggerHaptic, hasHapticFeedback };
};

// Touch-friendly button hook
export const useTouchOptimizedButton = (
  onClick: () => void,
  options: {
    hapticFeedback?: 'light' | 'medium' | 'heavy';
    longPressAction?: () => void;
    preventDoubleClick?: boolean;
  } = {}
) => {
  const { triggerHaptic } = useHapticFeedback();
  const [isPressed, setIsPressed] = useState(false);
  const lastClickTime = useRef(0);

  const handleClick = useCallback(() => {
    const now = Date.now();

    // Prevent double clicks
    if (options.preventDoubleClick && now - lastClickTime.current < 300) {
      return;
    }

    lastClickTime.current = now;

    if (options.hapticFeedback) {
      triggerHaptic(options.hapticFeedback);
    }

    onClick();
  }, [onClick, options.hapticFeedback, options.preventDoubleClick, triggerHaptic]);

  const longPressProps = useLongPress(
    () => {
      if (options.longPressAction) {
        triggerHaptic('medium');
        options.longPressAction();
      }
    },
    { delay: 600 }
  );

  return {
    onClick: handleClick,
    onPointerDown: () => setIsPressed(true),
    onPointerUp: () => setIsPressed(false),
    onPointerLeave: () => setIsPressed(false),
    style: {
      touchAction: 'manipulation' as const, // Improve tap responsiveness
      userSelect: 'none' as const, // Prevent text selection
      WebkitTapHighlightColor: 'transparent', // Remove iOS tap highlight
    },
    'data-pressed': isPressed,
  };
};

// Pull to refresh hook
export const usePullToRefresh = (
  onRefresh: () => Promise<void> | void,
  options: {
    threshold?: number;
    maxPullDistance?: number;
    resistance?: number;
  } = {}
) => {
  const {
    threshold = 80,
    maxPullDistance = 120,
    resistance = 0.5,
  } = options;

  const [isPulling, setIsPulling] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);

  const elementRef = useRef<HTMLElement>(null);
  const startY = useRef(0);
  const currentY = useRef(0);
  const isEnabled = useRef(true);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (!isEnabled.current || isRefreshing) return;

    startY.current = e.touches[0].clientY;
    currentY.current = startY.current;
  }, [isRefreshing]);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (!isEnabled.current || isRefreshing) return;

    currentY.current = e.touches[0].clientY;
    const deltaY = currentY.current - startY.current;

    if (deltaY > 0 && elementRef.current?.scrollTop === 0) {
      e.preventDefault();
      const distance = Math.min(deltaY * resistance, maxPullDistance);
      setPullDistance(distance);
      setIsPulling(distance > 10);
    }
  }, [isRefreshing, resistance, maxPullDistance]);

  const handleTouchEnd = useCallback(async () => {
    if (!isEnabled.current || isRefreshing) return;

    if (pullDistance >= threshold) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } catch (error) {
        console.error('Pull to refresh failed:', error);
      } finally {
        setIsRefreshing(false);
      }
    }

    setIsPulling(false);
    setPullDistance(0);
  }, [pullDistance, threshold, onRefresh, isRefreshing]);

  const attachPullToRefresh = useCallback((element: HTMLElement | null) => {
    if (elementRef.current) {
      elementRef.current.removeEventListener('touchstart', handleTouchStart);
      elementRef.current.removeEventListener('touchmove', handleTouchMove);
      elementRef.current.removeEventListener('touchend', handleTouchEnd);
    }

    elementRef.current = element;

    if (element) {
      element.addEventListener('touchstart', handleTouchStart, { passive: false });
      element.addEventListener('touchmove', handleTouchMove, { passive: false });
      element.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
  }, [handleTouchStart, handleTouchMove, handleTouchEnd]);

  return {
    attachPullToRefresh,
    isPulling,
    isRefreshing,
    pullDistance,
    isEnabled: isEnabled.current,
    setEnabled: (enabled: boolean) => {
      isEnabled.current = enabled;
    },
  };
};