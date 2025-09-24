/**
 * useDebug Hook
 *
 * React hook for accessing debugging utilities and error reporting
 * in development. Provides easy access to logging, error reporting,
 * and debugging tools for React components.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { debugManager, logStateChange, logOnboardingEvent, logAuthEvent } from '@/lib/debug-utilities';
import { errorReporting, ErrorLevel, ErrorCategory } from '@/lib/error-reporting';

export interface UseDebugReturn {
  // Logging functions
  logStateChange: (component: string, previousState: any, newState: any) => void;
  logOnboardingEvent: (step: number, event: string, data?: any) => void;
  logAuthEvent: (event: string, data?: any) => void;
  logError: (level: ErrorLevel, category: ErrorCategory, message: string, error?: Error, context?: any) => string;

  // Error reporting shortcuts
  reportComponentError: (componentName: string, error: Error, context?: any) => string;
  reportApiError: (message: string, error?: Error, context?: any) => string;
  reportOnboardingError: (step: number, message: string, error?: Error, context?: any) => string;

  // Debug data access
  getErrorReports: () => any[];
  getDebugData: () => Record<string, any>;
  getErrorMetrics: () => any;

  // Session info
  sessionId: string;
  isDebugging: boolean;

  // Export/Clear functions
  exportDebugData: () => any;
  clearDebugData: () => void;
}

/**
 * React hook for debugging and error reporting utilities
 */
export function useDebug(componentName?: string): UseDebugReturn {
  const [sessionId] = useState(() => debugManager.getSessionId());
  const [isDebugging] = useState(() => process.env.NODE_ENV === 'development');

  // Enhanced state change logging with component context
  const handleLogStateChange = useCallback((
    component: string,
    previousState: any,
    newState: any
  ) => {
    const fullComponentName = componentName ? `${componentName}.${component}` : component;
    logStateChange(fullComponentName, previousState, newState);
  }, [componentName]);

  // Enhanced onboarding event logging
  const handleLogOnboardingEvent = useCallback((
    step: number,
    event: string,
    data?: any
  ) => {
    const eventData = {
      ...data,
      component: componentName,
      timestamp: Date.now(),
    };
    logOnboardingEvent(step, event, eventData);
  }, [componentName]);

  // Enhanced auth event logging
  const handleLogAuthEvent = useCallback((
    event: string,
    data?: any
  ) => {
    const eventData = {
      ...data,
      component: componentName,
      timestamp: Date.now(),
    };
    logAuthEvent(event, eventData);
  }, [componentName]);

  // Generic error logging with component context
  const handleLogError = useCallback((
    level: ErrorLevel,
    category: ErrorCategory,
    message: string,
    error?: Error,
    context?: any
  ) => {
    const enhancedContext = {
      ...context,
      component: componentName,
      sessionId,
    };
    return errorReporting.reportError(level, category, message, error, enhancedContext);
  }, [componentName, sessionId]);

  // Component-specific error reporting
  const handleReportComponentError = useCallback((
    componentName: string,
    error: Error,
    context?: any
  ) => {
    const enhancedContext = {
      ...context,
      parentComponent: componentName,
      sessionId,
    };
    return errorReporting.reportComponentError(componentName, error, enhancedContext);
  }, [componentName, sessionId]);

  // API error reporting with context
  const handleReportApiError = useCallback((
    message: string,
    error?: Error,
    context?: any
  ) => {
    const enhancedContext = {
      ...context,
      component: componentName,
      sessionId,
    };
    return errorReporting.reportApiError(message, error, enhancedContext);
  }, [componentName, sessionId]);

  // Onboarding error reporting with context
  const handleReportOnboardingError = useCallback((
    step: number,
    message: string,
    error?: Error,
    context?: any
  ) => {
    const enhancedContext = {
      ...context,
      component: componentName,
      sessionId,
    };
    return errorReporting.reportOnboardingError(step, message, error, enhancedContext);
  }, [componentName, sessionId]);

  // Data access functions
  const getErrorReports = useCallback(() => errorReporting.getReports(), []);
  const getDebugData = useCallback(() => debugManager.getDebugData(), []);
  const getErrorMetrics = useCallback(() => errorReporting.getMetrics(), []);

  // Export/Clear functions
  const exportDebugData = useCallback(() => debugManager.exportDebugData(), []);
  const clearDebugData = useCallback(() => debugManager.clearDebugData(), []);

  // Log component mount/unmount in development
  useEffect(() => {
    if (!isDebugging || !componentName) return;

    handleLogStateChange('lifecycle', null, 'mounted');

    return () => {
      handleLogStateChange('lifecycle', 'mounted', 'unmounted');
    };
  }, [componentName, isDebugging, handleLogStateChange]);

  return useMemo(() => ({
    // Logging functions
    logStateChange: handleLogStateChange,
    logOnboardingEvent: handleLogOnboardingEvent,
    logAuthEvent: handleLogAuthEvent,
    logError: handleLogError,

    // Error reporting shortcuts
    reportComponentError: handleReportComponentError,
    reportApiError: handleReportApiError,
    reportOnboardingError: handleReportOnboardingError,

    // Debug data access
    getErrorReports,
    getDebugData,
    getErrorMetrics,

    // Session info
    sessionId,
    isDebugging,

    // Export/Clear functions
    exportDebugData,
    clearDebugData,
  }), [
    handleLogStateChange,
    handleLogOnboardingEvent,
    handleLogAuthEvent,
    handleLogError,
    handleReportComponentError,
    handleReportApiError,
    handleReportOnboardingError,
    getErrorReports,
    getDebugData,
    getErrorMetrics,
    sessionId,
    isDebugging,
    exportDebugData,
    clearDebugData,
  ]);
}

/**
 * Hook for debugging onboarding components specifically
 */
export function useOnboardingDebug(step: number, componentName?: string) {
  const debug = useDebug(componentName);

  const logOnboardingStateChange = useCallback((previousState: any, newState: any) => {
    debug.logOnboardingEvent(step, 'state_change', {
      previousState,
      newState,
      component: componentName,
    });
  }, [debug, step, componentName]);

  const logOnboardingAction = useCallback((action: string, data?: any) => {
    debug.logOnboardingEvent(step, action, {
      ...data,
      component: componentName,
    });
  }, [debug, step, componentName]);

  const reportOnboardingError = useCallback((message: string, error?: Error, context?: any) => {
    return debug.reportOnboardingError(step, message, error, {
      ...context,
      component: componentName,
    });
  }, [debug, step, componentName]);

  return {
    ...debug,
    logOnboardingStateChange,
    logOnboardingAction,
    reportOnboardingError: reportOnboardingError as typeof debug.reportOnboardingError,
    step,
  };
}

/**
 * Hook for debugging authentication components specifically
 */
export function useAuthDebug(componentName?: string) {
  const debug = useDebug(componentName);

  const logAuthStateChange = useCallback((event: string, data?: any) => {
    debug.logAuthEvent(event, {
      ...data,
      component: componentName,
    });
  }, [debug, componentName]);

  const reportAuthError = useCallback((message: string, error?: Error, context?: any) => {
    return debug.logError(
      ErrorLevel.ERROR,
      ErrorCategory.AUTHENTICATION,
      message,
      error,
      {
        ...context,
        component: componentName,
      }
    );
  }, [debug, componentName]);

  return {
    ...debug,
    logAuthStateChange,
    reportAuthError,
  };
}

/**
 * Hook for debugging API-related components
 */
export function useApiDebug(componentName?: string) {
  const debug = useDebug(componentName);

  const reportApiError = useCallback((endpoint: string, error?: Error, context?: any) => {
    return debug.reportApiError(
      `API error in ${componentName}: ${endpoint}`,
      error,
      {
        ...context,
        endpoint,
        component: componentName,
      }
    );
  }, [debug, componentName]);

  const logApiCall = useCallback((endpoint: string, method: string, data?: any) => {
    debug.logStateChange('api_call', null, {
      endpoint,
      method,
      data,
      timestamp: Date.now(),
    });
  }, [debug]);

  return {
    ...debug,
    reportApiError: reportApiError as typeof debug.reportApiError,
    logApiCall,
  };
}

export default useDebug;