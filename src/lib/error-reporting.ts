/**
 * Error Reporting and Logging System
 *
 * Comprehensive error tracking, reporting, and logging for onboarding flow
 * with privacy-conscious data collection and debugging support.
 */

export enum ErrorLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export enum ErrorCategory {
  AUTHENTICATION = 'authentication',
  API_REQUEST = 'api_request',
  DATA_VALIDATION = 'data_validation',
  SESSION_MANAGEMENT = 'session_management',
  NETWORK = 'network',
  UI_COMPONENT = 'ui_component',
  ONBOARDING_FLOW = 'onboarding_flow',
  BROWSER_COMPATIBILITY = 'browser_compatibility',
  PERFORMANCE = 'performance',
  USER_INPUT = 'user_input',
}

export interface ErrorContext {
  userId?: string;
  sessionId?: string;
  step?: number;
  url?: string;
  userAgent?: string;
  timestamp: number;
  additional?: Record<string, any>;
}

export interface ErrorReport {
  id: string;
  level: ErrorLevel;
  category: ErrorCategory;
  message: string;
  error?: Error;
  context: ErrorContext;
  stackTrace?: string;
  fingerprint?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface ErrorMetrics {
  totalErrors: number;
  errorsByLevel: Record<ErrorLevel, number>;
  errorsByCategory: Record<ErrorCategory, number>;
  commonErrors: Array<{ message: string; count: number; lastSeen: number }>;
  trends: {
    last24h: number;
    lastWeek: number;
    lastMonth: number;
  };
}

/**
 * Error Reporting Manager
 */
export class ErrorReportingManager {
  private reports: ErrorReport[] = [];
  private maxReports = 100;
  private storageKey = 'corner-league-error-reports';
  private metricsKey = 'corner-league-error-metrics';
  private sessionId: string;
  private isEnabled = true;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.loadStoredReports();
    this.setupGlobalErrorHandlers();
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Report an error
   */
  reportError(
    level: ErrorLevel,
    category: ErrorCategory,
    message: string,
    error?: Error,
    context?: Partial<ErrorContext>
  ): string {
    if (!this.isEnabled) return '';

    const report: ErrorReport = {
      id: this.generateErrorId(),
      level,
      category,
      message,
      error,
      context: {
        sessionId: this.sessionId,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
        ...context,
      },
      stackTrace: error?.stack,
      fingerprint: this.generateFingerprint(message, error),
      tags: this.generateTags(category, level),
      metadata: this.collectMetadata(),
    };

    this.addReport(report);
    this.updateMetrics(report);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      this.logToConsole(report);
    }

    return report.id;
  }

  /**
   * Report authentication error
   */
  reportAuthError(message: string, error?: Error, context?: any): string {
    return this.reportError(
      ErrorLevel.ERROR,
      ErrorCategory.AUTHENTICATION,
      message,
      error,
      context
    );
  }

  /**
   * Report API error
   */
  reportApiError(message: string, error?: Error, context?: any): string {
    const level = this.determineApiErrorLevel(error);
    return this.reportError(
      level,
      ErrorCategory.API_REQUEST,
      message,
      error,
      {
        ...context,
        status: error && 'status' in error ? (error as any).status : undefined,
        statusText: error && 'statusText' in error ? (error as any).statusText : undefined,
      }
    );
  }

  /**
   * Report validation error
   */
  reportValidationError(message: string, validationErrors: any, context?: any): string {
    return this.reportError(
      ErrorLevel.WARNING,
      ErrorCategory.DATA_VALIDATION,
      message,
      undefined,
      {
        ...context,
        validationErrors,
      }
    );
  }

  /**
   * Report UI component error
   */
  reportComponentError(componentName: string, error: Error, context?: any): string {
    return this.reportError(
      ErrorLevel.ERROR,
      ErrorCategory.UI_COMPONENT,
      `Error in component: ${componentName}`,
      error,
      {
        ...context,
        componentName,
      }
    );
  }

  /**
   * Report onboarding flow error
   */
  reportOnboardingError(
    step: number,
    message: string,
    error?: Error,
    context?: any
  ): string {
    return this.reportError(
      ErrorLevel.ERROR,
      ErrorCategory.ONBOARDING_FLOW,
      message,
      error,
      {
        ...context,
        step,
      }
    );
  }

  /**
   * Report performance issue
   */
  reportPerformanceIssue(metric: string, value: number, threshold: number, context?: any): string {
    return this.reportError(
      ErrorLevel.WARNING,
      ErrorCategory.PERFORMANCE,
      `Performance issue: ${metric} (${value}ms) exceeded threshold (${threshold}ms)`,
      undefined,
      {
        ...context,
        metric,
        value,
        threshold,
      }
    );
  }

  /**
   * Add report to collection
   */
  private addReport(report: ErrorReport): void {
    this.reports.push(report);

    // Trim to max reports
    if (this.reports.length > this.maxReports) {
      this.reports = this.reports.slice(-this.maxReports);
    }

    this.saveReports();
  }

  /**
   * Update error metrics
   */
  private updateMetrics(report: ErrorReport): void {
    try {
      const metrics = this.getMetrics();

      // Update totals
      metrics.totalErrors++;
      metrics.errorsByLevel[report.level] = (metrics.errorsByLevel[report.level] || 0) + 1;
      metrics.errorsByCategory[report.category] = (metrics.errorsByCategory[report.category] || 0) + 1;

      // Update common errors
      const commonError = metrics.commonErrors.find(e => e.message === report.message);
      if (commonError) {
        commonError.count++;
        commonError.lastSeen = report.context.timestamp;
      } else {
        metrics.commonErrors.push({
          message: report.message,
          count: 1,
          lastSeen: report.context.timestamp,
        });
      }

      // Keep only top 20 common errors
      metrics.commonErrors.sort((a, b) => b.count - a.count);
      metrics.commonErrors = metrics.commonErrors.slice(0, 20);

      // Update trends
      const now = Date.now();
      const oneDayAgo = now - (24 * 60 * 60 * 1000);
      const oneWeekAgo = now - (7 * 24 * 60 * 60 * 1000);
      const oneMonthAgo = now - (30 * 24 * 60 * 60 * 1000);

      metrics.trends.last24h = this.reports.filter(r => r.context.timestamp > oneDayAgo).length;
      metrics.trends.lastWeek = this.reports.filter(r => r.context.timestamp > oneWeekAgo).length;
      metrics.trends.lastMonth = this.reports.filter(r => r.context.timestamp > oneMonthAgo).length;

      this.saveMetrics(metrics);
    } catch (error) {
      console.warn('Failed to update error metrics:', error);
    }
  }

  /**
   * Generate error ID
   */
  private generateErrorId(): string {
    return `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate error fingerprint for deduplication
   */
  private generateFingerprint(message: string, error?: Error): string {
    const base = message + (error?.name || '') + (error?.stack?.split('\n')[0] || '');
    return btoa(base).substr(0, 16);
  }

  /**
   * Generate tags for categorization
   */
  private generateTags(category: ErrorCategory, level: ErrorLevel): string[] {
    const tags = [category, level];

    // Add environment tags
    if (process.env.NODE_ENV) {
      tags.push(`env:${process.env.NODE_ENV}`);
    }

    // Add browser tags
    if (navigator.userAgent.includes('Chrome')) tags.push('browser:chrome');
    if (navigator.userAgent.includes('Firefox')) tags.push('browser:firefox');
    if (navigator.userAgent.includes('Safari')) tags.push('browser:safari');

    // Add platform tags
    if (navigator.platform.includes('Mac')) tags.push('platform:mac');
    if (navigator.platform.includes('Win')) tags.push('platform:windows');
    if (navigator.platform.includes('Linux')) tags.push('platform:linux');

    return tags;
  }

  /**
   * Collect system metadata
   */
  private collectMetadata(): Record<string, any> {
    try {
      return {
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
        screen: {
          width: screen.width,
          height: screen.height,
          pixelRatio: window.devicePixelRatio,
        },
        connection: (navigator as any).connection ? {
          effectiveType: (navigator as any).connection.effectiveType,
          downlink: (navigator as any).connection.downlink,
        } : undefined,
        memory: (performance as any).memory ? {
          used: (performance as any).memory.usedJSHeapSize,
          total: (performance as any).memory.totalJSHeapSize,
          limit: (performance as any).memory.jsHeapSizeLimit,
        } : undefined,
        timing: {
          navigationStart: performance.timing?.navigationStart,
          loadEventEnd: performance.timing?.loadEventEnd,
        },
      };
    } catch {
      return {};
    }
  }

  /**
   * Determine API error level based on status
   */
  private determineApiErrorLevel(error?: Error): ErrorLevel {
    if (!error || !('status' in error)) {
      return ErrorLevel.ERROR;
    }

    const status = (error as any).status;

    if (status >= 500) return ErrorLevel.ERROR;
    if (status === 429) return ErrorLevel.WARNING;
    if (status >= 400) return ErrorLevel.WARNING;

    return ErrorLevel.INFO;
  }

  /**
   * Log error to console
   */
  private logToConsole(report: ErrorReport): void {
    const style = this.getConsoleStyle(report.level);

    console.group(`%c[${report.level.toUpperCase()}] ${report.category}`, style);
    console.log('Message:', report.message);
    if (report.error) {
      console.error('Error:', report.error);
    }
    console.log('Context:', report.context);
    if (report.metadata) {
      console.log('Metadata:', report.metadata);
    }
    console.groupEnd();
  }

  /**
   * Get console styling for error level
   */
  private getConsoleStyle(level: ErrorLevel): string {
    switch (level) {
      case ErrorLevel.DEBUG:
        return 'color: #888; font-weight: normal;';
      case ErrorLevel.INFO:
        return 'color: #2196F3; font-weight: normal;';
      case ErrorLevel.WARNING:
        return 'color: #FF9800; font-weight: bold;';
      case ErrorLevel.ERROR:
        return 'color: #F44336; font-weight: bold;';
      case ErrorLevel.CRITICAL:
        return 'color: #FFFFFF; background-color: #F44336; font-weight: bold; padding: 2px 4px;';
      default:
        return 'color: #000; font-weight: normal;';
    }
  }

  /**
   * Setup global error handlers
   */
  private setupGlobalErrorHandlers(): void {
    // Global JavaScript errors
    window.addEventListener('error', (event) => {
      this.reportError(
        ErrorLevel.ERROR,
        ErrorCategory.UI_COMPONENT,
        event.message,
        new Error(event.message),
        {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
        }
      );
    });

    // Unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.reportError(
        ErrorLevel.ERROR,
        ErrorCategory.API_REQUEST,
        'Unhandled promise rejection',
        event.reason instanceof Error ? event.reason : new Error(String(event.reason)),
        {
          type: 'unhandledrejection',
        }
      );
    });
  }

  /**
   * Get all error reports
   */
  getReports(): ErrorReport[] {
    return [...this.reports];
  }

  /**
   * Get error reports by level
   */
  getReportsByLevel(level: ErrorLevel): ErrorReport[] {
    return this.reports.filter(r => r.level === level);
  }

  /**
   * Get error reports by category
   */
  getReportsByCategory(category: ErrorCategory): ErrorReport[] {
    return this.reports.filter(r => r.category === category);
  }

  /**
   * Get error metrics
   */
  getMetrics(): ErrorMetrics {
    try {
      const stored = localStorage.getItem(this.metricsKey);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch {
      // Fall through to default
    }

    return {
      totalErrors: 0,
      errorsByLevel: {} as Record<ErrorLevel, number>,
      errorsByCategory: {} as Record<ErrorCategory, number>,
      commonErrors: [],
      trends: {
        last24h: 0,
        lastWeek: 0,
        lastMonth: 0,
      },
    };
  }

  /**
   * Clear all error reports
   */
  clearReports(): void {
    this.reports = [];
    this.saveReports();
    this.saveMetrics(this.getMetrics());
  }

  /**
   * Export error reports for debugging
   */
  exportReports(): any {
    return {
      reports: this.reports,
      metrics: this.getMetrics(),
      sessionId: this.sessionId,
      exportedAt: new Date().toISOString(),
    };
  }

  /**
   * Enable/disable error reporting
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  /**
   * Save reports to localStorage
   */
  private saveReports(): void {
    try {
      // Only store essential data to avoid quota issues
      const essential = this.reports.map(r => ({
        id: r.id,
        level: r.level,
        category: r.category,
        message: r.message,
        timestamp: r.context.timestamp,
        fingerprint: r.fingerprint,
        tags: r.tags,
      }));

      localStorage.setItem(this.storageKey, JSON.stringify(essential));
    } catch (error) {
      console.warn('Failed to save error reports:', error);
    }
  }

  /**
   * Load reports from localStorage
   */
  private loadStoredReports(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        this.reports = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load stored error reports:', error);
    }
  }

  /**
   * Save metrics to localStorage
   */
  private saveMetrics(metrics: ErrorMetrics): void {
    try {
      localStorage.setItem(this.metricsKey, JSON.stringify(metrics));
    } catch (error) {
      console.warn('Failed to save error metrics:', error);
    }
  }
}

// Export singleton instance
export const errorReporting = new ErrorReportingManager();

// Convenience functions
export const reportError = (
  level: ErrorLevel,
  category: ErrorCategory,
  message: string,
  error?: Error,
  context?: any
): string => {
  return errorReporting.reportError(level, category, message, error, context);
};

export const reportAuthError = (message: string, error?: Error, context?: any): string => {
  return errorReporting.reportAuthError(message, error, context);
};

export const reportApiError = (message: string, error?: Error, context?: any): string => {
  return errorReporting.reportApiError(message, error, context);
};

export const reportOnboardingError = (
  step: number,
  message: string,
  error?: Error,
  context?: any
): string => {
  return errorReporting.reportOnboardingError(step, message, error, context);
};

export default errorReporting;