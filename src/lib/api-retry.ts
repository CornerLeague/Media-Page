/**
 * API Retry Logic with Exponential Backoff
 *
 * Enhanced retry mechanism for API calls with configurable backoff strategies,
 * circuit breaker pattern, and intelligent error classification.
 */

export interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffFactor: number;
  jitter: boolean;
  retryCondition?: (error: any) => boolean;
  onRetry?: (attempt: number, error: any) => void;
  onMaxRetries?: (error: any) => void;
}

export interface CircuitBreakerConfig {
  failureThreshold: number;
  timeout: number;
  monitoringPeriod: number;
}

export interface RetryableError extends Error {
  isRetryable: boolean;
  statusCode?: number;
  retryAfter?: number;
}

export enum ApiErrorType {
  NETWORK_ERROR = 'network_error',
  TIMEOUT_ERROR = 'timeout_error',
  SERVER_ERROR = 'server_error',
  CLIENT_ERROR = 'client_error',
  RATE_LIMIT_ERROR = 'rate_limit_error',
  AUTH_ERROR = 'auth_error',
  UNKNOWN_ERROR = 'unknown_error',
}

/**
 * Circuit Breaker implementation
 */
class CircuitBreaker {
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private failures: number = 0;
  private lastFailureTime: number = 0;
  private successCount: number = 0;

  constructor(private config: CircuitBreakerConfig) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime < this.config.timeout) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
      this.successCount = 0;
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    if (this.state === 'HALF_OPEN') {
      this.successCount++;
      if (this.successCount >= 3) { // Require 3 successes to close
        this.state = 'CLOSED';
      }
    }
  }

  private onFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();

    if (this.failures >= this.config.failureThreshold) {
      this.state = 'OPEN';
    }
  }

  getState(): string {
    return this.state;
  }

  reset(): void {
    this.state = 'CLOSED';
    this.failures = 0;
    this.lastFailureTime = 0;
    this.successCount = 0;
  }
}

/**
 * Enhanced retry utility with exponential backoff
 */
export class ApiRetryManager {
  private circuitBreaker: CircuitBreaker;
  private defaultRetryConfig: RetryConfig = {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 30000,
    backoffFactor: 2,
    jitter: true,
    retryCondition: this.defaultRetryCondition.bind(this),
  };

  constructor(
    private retryConfig: Partial<RetryConfig> = {},
    circuitBreakerConfig?: CircuitBreakerConfig
  ) {
    const circuitConfig = circuitBreakerConfig || {
      failureThreshold: 5,
      timeout: 60000, // 1 minute
      monitoringPeriod: 300000, // 5 minutes
    };

    this.circuitBreaker = new CircuitBreaker(circuitConfig);
  }

  /**
   * Execute API call with retry logic
   */
  async executeWithRetry<T>(
    apiCall: () => Promise<T>,
    customConfig?: Partial<RetryConfig>
  ): Promise<T> {
    const config = { ...this.defaultRetryConfig, ...this.retryConfig, ...customConfig };

    return this.circuitBreaker.call(async () => {
      let lastError: any;

      for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
        try {
          const result = await this.executeWithTimeout(apiCall, 10000); // 10s timeout
          return result;
        } catch (error) {
          lastError = error;

          // Don't retry on last attempt
          if (attempt === config.maxRetries) {
            break;
          }

          // Check if error is retryable
          if (!config.retryCondition!(error)) {
            throw error;
          }

          // Calculate delay with exponential backoff
          const delay = this.calculateDelay(attempt, config);

          // Call retry callback
          if (config.onRetry) {
            config.onRetry(attempt + 1, error);
          }

          // Wait before retry
          await this.delay(delay);
        }
      }

      // Call max retries callback
      if (config.onMaxRetries) {
        config.onMaxRetries(lastError);
      }

      throw lastError;
    });
  }

  /**
   * Execute with timeout
   */
  private async executeWithTimeout<T>(
    apiCall: () => Promise<T>,
    timeoutMs: number
  ): Promise<T> {
    return Promise.race([
      apiCall(),
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Request timeout')), timeoutMs)
      ),
    ]);
  }

  /**
   * Calculate delay with exponential backoff and jitter
   */
  private calculateDelay(attempt: number, config: RetryConfig): number {
    let delay = Math.min(
      config.baseDelay * Math.pow(config.backoffFactor, attempt),
      config.maxDelay
    );

    // Add jitter to prevent thundering herd
    if (config.jitter) {
      delay = delay * (0.5 + Math.random() * 0.5);
    }

    return Math.floor(delay);
  }

  /**
   * Default retry condition
   */
  private defaultRetryCondition(error: any): boolean {
    const errorType = this.classifyError(error);

    switch (errorType) {
      case ApiErrorType.NETWORK_ERROR:
      case ApiErrorType.TIMEOUT_ERROR:
      case ApiErrorType.SERVER_ERROR:
        return true;

      case ApiErrorType.RATE_LIMIT_ERROR:
        return true; // Retry with backoff

      case ApiErrorType.CLIENT_ERROR:
      case ApiErrorType.AUTH_ERROR:
        return false; // Don't retry client errors

      default:
        return false;
    }
  }

  /**
   * Classify error type
   */
  private classifyError(error: any): ApiErrorType {
    // Network errors
    if (error.name === 'NetworkError' || error.message?.includes('fetch')) {
      return ApiErrorType.NETWORK_ERROR;
    }

    // Timeout errors
    if (error.message?.includes('timeout') || error.name === 'TimeoutError') {
      return ApiErrorType.TIMEOUT_ERROR;
    }

    // HTTP status codes
    if (error.status || error.statusCode) {
      const status = error.status || error.statusCode;

      if (status >= 500) {
        return ApiErrorType.SERVER_ERROR;
      }

      if (status === 429) {
        return ApiErrorType.RATE_LIMIT_ERROR;
      }

      if (status === 401 || status === 403) {
        return ApiErrorType.AUTH_ERROR;
      }

      if (status >= 400) {
        return ApiErrorType.CLIENT_ERROR;
      }
    }

    return ApiErrorType.UNKNOWN_ERROR;
  }

  /**
   * Delay utility
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get circuit breaker status
   */
  getCircuitBreakerStatus(): { state: string; failures: number } {
    return {
      state: this.circuitBreaker.getState(),
      failures: (this.circuitBreaker as any).failures,
    };
  }

  /**
   * Reset circuit breaker
   */
  resetCircuitBreaker(): void {
    this.circuitBreaker.reset();
  }
}

/**
 * Enhanced fetch with retry logic
 */
export class RetryableFetch {
  private retryManager: ApiRetryManager;

  constructor(retryConfig?: Partial<RetryConfig>) {
    this.retryManager = new ApiRetryManager(retryConfig);
  }

  async fetch(url: string, options: RequestInit = {}): Promise<Response> {
    return this.retryManager.executeWithRetry(async () => {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      // Throw error for non-2xx responses
      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`) as RetryableError;
        error.statusCode = response.status;
        error.isRetryable = response.status >= 500 || response.status === 429;

        // Parse rate limit headers
        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After');
          if (retryAfter) {
            error.retryAfter = parseInt(retryAfter, 10) * 1000; // Convert to ms
          }
        }

        throw error;
      }

      return response;
    });
  }

  async get(url: string, options?: RequestInit): Promise<Response> {
    return this.fetch(url, { ...options, method: 'GET' });
  }

  async post(url: string, body?: any, options?: RequestInit): Promise<Response> {
    return this.fetch(url, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put(url: string, body?: any, options?: RequestInit): Promise<Response> {
    return this.fetch(url, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete(url: string, options?: RequestInit): Promise<Response> {
    return this.fetch(url, { ...options, method: 'DELETE' });
  }

  getStatus() {
    return this.retryManager.getCircuitBreakerStatus();
  }

  reset() {
    this.retryManager.resetCircuitBreaker();
  }
}

// Export singleton instances
export const defaultRetryManager = new ApiRetryManager();
export const retryableFetch = new RetryableFetch();

export default {
  ApiRetryManager,
  RetryableFetch,
  defaultRetryManager,
  retryableFetch,
};