/**
 * Debug Provider Component
 *
 * Provides debugging context and UI for development.
 * Automatically includes debug panel toggle and global error boundaries.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { DebugPanel } from './DebugPanel';
import { debugManager } from '@/lib/debug-utilities';
import { errorReporting } from '@/lib/error-reporting';

// Only provide debugging in development
const isDevelopment = process.env.NODE_ENV === 'development';

interface DebugContextType {
  isDebugPanelOpen: boolean;
  toggleDebugPanel: () => void;
  reportError: (error: Error, context?: any) => void;
  sessionId: string;
}

const DebugContext = createContext<DebugContextType | null>(null);

interface DebugProviderProps {
  children: ReactNode;
  enableKeyboardShortcuts?: boolean;
  enableGlobalErrorBoundary?: boolean;
}

export const DebugProvider: React.FC<DebugProviderProps> = ({
  children,
  enableKeyboardShortcuts = true,
  enableGlobalErrorBoundary = true,
}) => {
  const [isDebugPanelOpen, setIsDebugPanelOpen] = useState(false);
  const [sessionId] = useState(() => debugManager.getSessionId());

  const toggleDebugPanel = () => {
    setIsDebugPanelOpen(!isDebugPanelOpen);
  };

  const reportError = (error: Error, context?: any) => {
    if (isDevelopment) {
      errorReporting.reportComponentError(
        'DebugProvider',
        error,
        { ...context, sessionId }
      );
    }
  };

  // Keyboard shortcuts for debug panel
  useEffect(() => {
    if (!isDevelopment || !enableKeyboardShortcuts) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + Shift + D to toggle debug panel
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'D') {
        event.preventDefault();
        toggleDebugPanel();
      }

      // Ctrl/Cmd + Shift + E to export debug data
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'E') {
        event.preventDefault();
        const data = debugManager.exportDebugData();
        console.log('Debug data exported:', data);

        // Also download as file
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `debug-export-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }

      // Ctrl/Cmd + Shift + C to clear debug data
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
        event.preventDefault();
        debugManager.clearDebugData();
        errorReporting.clearReports();
        console.log('Debug data cleared');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enableKeyboardShortcuts]);

  // Global error boundary
  useEffect(() => {
    if (!isDevelopment || !enableGlobalErrorBoundary) return;

    const handleError = (event: ErrorEvent) => {
      reportError(
        new Error(event.message),
        {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          source: 'window.error',
        }
      );
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const error = event.reason instanceof Error
        ? event.reason
        : new Error(String(event.reason));

      reportError(error, {
        source: 'unhandledrejection',
        reason: event.reason,
      });
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [enableGlobalErrorBoundary, reportError]);

  // Log provider initialization
  useEffect(() => {
    if (isDevelopment) {
      console.log('🔧 Debug Provider initialized');
      console.log('Keyboard shortcuts:');
      console.log('  Ctrl/Cmd + Shift + D: Toggle Debug Panel');
      console.log('  Ctrl/Cmd + Shift + E: Export Debug Data');
      console.log('  Ctrl/Cmd + Shift + C: Clear Debug Data');
    }
  }, []);

  const contextValue: DebugContextType = {
    isDebugPanelOpen,
    toggleDebugPanel,
    reportError,
    sessionId,
  };

  if (!isDevelopment) {
    return <>{children}</>;
  }

  return (
    <DebugContext.Provider value={contextValue}>
      {children}
      {isDebugPanelOpen && (
        <DebugPanel
          isOpen={isDebugPanelOpen}
          onToggle={toggleDebugPanel}
        />
      )}
      {!isDebugPanelOpen && (
        <DebugPanel
          isOpen={false}
          onToggle={toggleDebugPanel}
        />
      )}
    </DebugContext.Provider>
  );
};

/**
 * Hook to access debug context
 */
export const useDebugContext = () => {
  const context = useContext(DebugContext);

  if (!isDevelopment) {
    // Return no-op functions in production
    return {
      isDebugPanelOpen: false,
      toggleDebugPanel: () => {},
      reportError: () => {},
      sessionId: '',
    };
  }

  if (!context) {
    throw new Error('useDebugContext must be used within a DebugProvider');
  }

  return context;
};

/**
 * Higher-order component for adding debug capabilities to components
 */
export function withDebug<P extends object>(
  Component: React.ComponentType<P>,
  componentName?: string
) {
  if (!isDevelopment) {
    return Component;
  }

  const DebugWrappedComponent = (props: P) => {
    const { reportError } = useDebugContext();

    const handleError = (error: Error, errorInfo?: any) => {
      reportError(error, {
        component: componentName || Component.name,
        props,
        errorInfo,
      });
    };

    // Simple error boundary wrapper
    try {
      return <Component {...props} />;
    } catch (error) {
      handleError(error as Error);
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <h3 className="text-red-800 font-medium">Component Error</h3>
          <p className="text-red-600 text-sm mt-1">
            {componentName || Component.name} encountered an error
          </p>
          <pre className="text-red-500 text-xs mt-2 overflow-x-auto">
            {error instanceof Error ? error.message : String(error)}
          </pre>
        </div>
      );
    }
  };

  DebugWrappedComponent.displayName = `withDebug(${componentName || Component.name})`;
  return DebugWrappedComponent;
}

export default DebugProvider;