/**
 * Debug Utilities for Corner League Media
 *
 * Development-specific debugging tools and utilities for troubleshooting
 * onboarding flow, authentication, and API issues.
 */

import { errorReporting, ErrorLevel, ErrorCategory } from '@/lib/error-reporting';
import { ApiClient, ApiClientError } from '@/lib/api-client';

// Debug configuration
export interface DebugConfig {
  enableConsoleLogging: boolean;
  enableNetworkLogging: boolean;
  enableStateLogging: boolean;
  enablePerformanceLogging: boolean;
  enableErrorReporting: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

// Default debug configuration
const DEFAULT_DEBUG_CONFIG: DebugConfig = {
  enableConsoleLogging: process.env.NODE_ENV === 'development',
  enableNetworkLogging: process.env.NODE_ENV === 'development',
  enableStateLogging: process.env.NODE_ENV === 'development',
  enablePerformanceLogging: process.env.NODE_ENV === 'development',
  enableErrorReporting: true,
  logLevel: process.env.NODE_ENV === 'development' ? 'debug' : 'error',
};

/**
 * Debug Manager for development debugging
 */
export class DebugManager {
  private config: DebugConfig;
  private sessionId: string;
  private debugData: Map<string, any> = new Map();

  constructor(config?: Partial<DebugConfig>) {
    this.config = { ...DEFAULT_DEBUG_CONFIG, ...config };
    this.sessionId = this.generateSessionId();

    if (this.config.enableConsoleLogging) {
      this.setupConsoleOverrides();
    }
  }

  private generateSessionId(): string {
    return `debug-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Enhanced console logging with context
   */
  private setupConsoleOverrides(): void {
    if (typeof window === 'undefined') return;

    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;

    // Override console.log to add debug context
    console.log = (...args: any[]) => {
      if (this.shouldLog('debug')) {
        originalLog('[DEBUG]', new Date().toISOString(), ...args);
      }
    };

    // Override console.error to capture errors
    console.error = (...args: any[]) => {
      if (this.shouldLog('error')) {
        originalError('[ERROR]', new Date().toISOString(), ...args);

        // Also report to error reporting system
        if (this.config.enableErrorReporting) {
          const errorMessage = args.map(arg =>
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
          ).join(' ');

          errorReporting.reportError(
            ErrorLevel.ERROR,
            ErrorCategory.UI_COMPONENT,
            `Console error: ${errorMessage}`,
            args.find(arg => arg instanceof Error) || undefined,
            { sessionId: this.sessionId }
          );
        }
      }
    };

    // Override console.warn
    console.warn = (...args: any[]) => {
      if (this.shouldLog('warn')) {
        originalWarn('[WARN]', new Date().toISOString(), ...args);
      }
    };
  }

  private shouldLog(level: string): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    const configLevel = levels.indexOf(this.config.logLevel);
    const messageLevel = levels.indexOf(level);
    return messageLevel >= configLevel;
  }

  /**
   * Log API request details
   */
  logApiRequest(method: string, url: string, data?: any): void {
    if (!this.config.enableNetworkLogging) return;

    const requestData = {
      method,
      url,
      data: data ? this.sanitizeData(data) : undefined,
      timestamp: Date.now(),
      sessionId: this.sessionId,
    };

    console.log('🌐 API Request:', requestData);
    this.storeDebugData(`api-request-${Date.now()}`, requestData);
  }

  /**
   * Log API response details
   */
  logApiResponse(method: string, url: string, response: any, duration?: number): void {
    if (!this.config.enableNetworkLogging) return;

    const responseData = {
      method,
      url,
      response: this.sanitizeData(response),
      duration,
      timestamp: Date.now(),
      sessionId: this.sessionId,
    };

    console.log('📡 API Response:', responseData);
    this.storeDebugData(`api-response-${Date.now()}`, responseData);
  }

  /**
   * Log API error details
   */
  logApiError(method: string, url: string, error: ApiClientError | Error, duration?: number): void {
    if (!this.config.enableNetworkLogging) return;

    const errorData = {
      method,
      url,
      error: {
        message: error.message,
        name: error.name,
        stack: error.stack,
        ...(error instanceof ApiClientError ? {
          statusCode: error.statusCode,
          code: error.code,
          details: error.details,
        } : {}),
      },
      duration,
      timestamp: Date.now(),
      sessionId: this.sessionId,
    };

    console.error('❌ API Error:', errorData);
    this.storeDebugData(`api-error-${Date.now()}`, errorData);

    // Report to error reporting system
    if (this.config.enableErrorReporting) {
      errorReporting.reportApiError(
        `API ${method} ${url} failed`,
        error,
        { duration, sessionId: this.sessionId }
      );
    }
  }

  /**
   * Log state changes
   */
  logStateChange(component: string, previousState: any, newState: any): void {
    if (!this.config.enableStateLogging) return;

    const stateData = {
      component,
      previousState: this.sanitizeData(previousState),
      newState: this.sanitizeData(newState),
      timestamp: Date.now(),
      sessionId: this.sessionId,
    };

    console.log('🔄 State Change:', stateData);
    this.storeDebugData(`state-change-${component}-${Date.now()}`, stateData);
  }

  /**
   * Log performance metrics
   */
  logPerformance(metric: string, value: number, context?: any): void {
    if (!this.config.enablePerformanceLogging) return;

    const perfData = {
      metric,
      value,
      unit: 'ms',
      context: context ? this.sanitizeData(context) : undefined,
      timestamp: Date.now(),
      sessionId: this.sessionId,
    };

    const emoji = value > 1000 ? '🐌' : value > 500 ? '⚠️' : '⚡';
    console.log(`${emoji} Performance:`, perfData);
    this.storeDebugData(`performance-${metric}-${Date.now()}`, perfData);

    // Report slow operations
    if (value > 2000 && this.config.enableErrorReporting) {
      errorReporting.reportPerformanceIssue(metric, value, 2000, {
        sessionId: this.sessionId,
        ...context
      });
    }
  }

  /**
   * Log onboarding flow events
   */
  logOnboardingEvent(step: number, event: string, data?: any): void {
    if (!this.config.enableStateLogging) return;

    const eventData = {
      step,
      event,
      data: data ? this.sanitizeData(data) : undefined,
      timestamp: Date.now(),
      sessionId: this.sessionId,
    };

    console.log('🚀 Onboarding Event:', eventData);
    this.storeDebugData(`onboarding-${step}-${event}-${Date.now()}`, eventData);
  }

  /**
   * Log authentication events
   */
  logAuthEvent(event: string, data?: any): void {
    if (!this.config.enableStateLogging) return;

    const eventData = {
      event,
      data: data ? this.sanitizeData(data) : undefined,
      timestamp: Date.now(),
      sessionId: this.sessionId,
    };

    console.log('🔐 Auth Event:', eventData);
    this.storeDebugData(`auth-${event}-${Date.now()}`, eventData);
  }

  /**
   * Sanitize sensitive data for logging
   */
  private sanitizeData(data: any): any {
    if (!data) return data;

    if (typeof data === 'string') {
      // Mask email addresses
      return data.replace(/([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g, '***@$2');
    }

    if (Array.isArray(data)) {
      return data.map(item => this.sanitizeData(item));
    }

    if (typeof data === 'object') {
      const sanitized: any = {};
      for (const [key, value] of Object.entries(data)) {
        // Skip sensitive fields
        if (key.toLowerCase().includes('password') ||
            key.toLowerCase().includes('token') ||
            key.toLowerCase().includes('secret')) {
          sanitized[key] = '[REDACTED]';
        } else {
          sanitized[key] = this.sanitizeData(value);
        }
      }
      return sanitized;
    }

    return data;
  }

  /**
   * Store debug data for later retrieval
   */
  private storeDebugData(key: string, data: any): void {
    this.debugData.set(key, data);

    // Keep only last 100 entries to prevent memory issues
    if (this.debugData.size > 100) {
      const firstKey = this.debugData.keys().next().value;
      this.debugData.delete(firstKey);
    }
  }

  /**
   * Get all debug data
   */
  getDebugData(): Record<string, any> {
    const result: Record<string, any> = {};
    for (const [key, value] of this.debugData.entries()) {
      result[key] = value;
    }
    return result;
  }

  /**
   * Export debug data for support
   */
  exportDebugData(): any {
    return {
      sessionId: this.sessionId,
      config: this.config,
      debugData: this.getDebugData(),
      errorReports: errorReporting.getReports(),
      errorMetrics: errorReporting.getMetrics(),
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      environment: process.env.NODE_ENV,
    };
  }

  /**
   * Clear all debug data
   */
  clearDebugData(): void {
    this.debugData.clear();
    console.log('🧹 Debug data cleared');
  }

  /**
   * Update debug configuration
   */
  updateConfig(newConfig: Partial<DebugConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ Debug config updated:', this.config);
  }

  /**
   * Get current session ID
   */
  getSessionId(): string {
    return this.sessionId;
  }
}

// Singleton instance
export const debugManager = new DebugManager();

// Convenience functions
export const logApiRequest = (method: string, url: string, data?: any) =>
  debugManager.logApiRequest(method, url, data);

export const logApiResponse = (method: string, url: string, response: any, duration?: number) =>
  debugManager.logApiResponse(method, url, response, duration);

export const logApiError = (method: string, url: string, error: ApiClientError | Error, duration?: number) =>
  debugManager.logApiError(method, url, error, duration);

export const logStateChange = (component: string, previousState: any, newState: any) =>
  debugManager.logStateChange(component, previousState, newState);

export const logPerformance = (metric: string, value: number, context?: any) =>
  debugManager.logPerformance(metric, value, context);

export const logOnboardingEvent = (step: number, event: string, data?: any) =>
  debugManager.logOnboardingEvent(step, event, data);

export const logAuthEvent = (event: string, data?: any) =>
  debugManager.logAuthEvent(event, data);

export const exportDebugData = () => debugManager.exportDebugData();

export const clearDebugData = () => debugManager.clearDebugData();

// Make debug functions available globally in development
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  (window as any).__cornerLeagueDebug = {
    debugManager,
    logApiRequest,
    logApiResponse,
    logApiError,
    logStateChange,
    logPerformance,
    logOnboardingEvent,
    logAuthEvent,
    exportDebugData,
    clearDebugData,
    errorReporting,
  };

  console.log('🔧 Corner League Debug utilities loaded. Access via window.__cornerLeagueDebug');
}

export default debugManager;