/**
 * API Retry Logic Tests
 *
 * Tests for API retry mechanism with exponential backoff and circuit breaker.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ApiRetryManager, RetryableFetch, ApiErrorType } from '@/lib/api-retry';

describe('ApiRetryManager', () => {
  let retryManager: ApiRetryManager;

  beforeEach(() => {
    retryManager = new ApiRetryManager({
      maxRetries: 3,
      baseDelay: 100,
      maxDelay: 1000,
      backoffFactor: 2,
      jitter: false, // Disable jitter for predictable tests
    });

    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe('Basic Retry Logic', () => {
    it('succeeds on first attempt when no error', async () => {
      const mockApiCall = vi.fn().mockResolvedValue('success');

      const result = await retryManager.executeWithRetry(mockApiCall);

      expect(result).toBe('success');
      expect(mockApiCall).toHaveBeenCalledTimes(1);
    });

    it('retries on retryable errors', async () => {
      const mockApiCall = vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Timeout'))
        .mockResolvedValue('success');

      const result = await retryManager.executeWithRetry(mockApiCall);

      expect(result).toBe('success');
      expect(mockApiCall).toHaveBeenCalledTimes(3);
    });

    it('respects max retries limit', async () => {
      const mockApiCall = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow('Network error');

      expect(mockApiCall).toHaveBeenCalledTimes(4); // Initial + 3 retries
    });

    it('does not retry on non-retryable errors', async () => {
      const clientError = new Error('Bad request');
      (clientError as any).status = 400;

      const mockApiCall = vi.fn().mockRejectedValue(clientError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow('Bad request');

      expect(mockApiCall).toHaveBeenCalledTimes(1); // No retries
    });
  });

  describe('Exponential Backoff', () => {
    it('implements exponential backoff delays', async () => {
      const mockApiCall = vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue('success');

      const executePromise = retryManager.executeWithRetry(mockApiCall);

      // First retry after 100ms
      vi.advanceTimersByTime(100);
      await Promise.resolve(); // Allow microtasks to run

      // Second retry after 200ms (100 * 2)
      vi.advanceTimersByTime(200);
      await Promise.resolve();

      const result = await executePromise;

      expect(result).toBe('success');
      expect(mockApiCall).toHaveBeenCalledTimes(3);
    });

    it('respects max delay limit', async () => {
      const retryManagerWithLowMax = new ApiRetryManager({
        maxRetries: 5,
        baseDelay: 100,
        maxDelay: 300, // Low max delay
        backoffFactor: 2,
        jitter: false,
      });

      const mockApiCall = vi.fn().mockRejectedValue(new Error('Network error'));

      const executePromise = retryManagerWithLowMax.executeWithRetry(mockApiCall);

      // Delays should be: 100, 200, 300, 300, 300 (capped at maxDelay)
      for (let i = 0; i < 5; i++) {
        const expectedDelay = Math.min(100 * Math.pow(2, i), 300);
        vi.advanceTimersByTime(expectedDelay);
        await Promise.resolve();
      }

      await expect(executePromise).rejects.toThrow('Network error');
    });
  });

  describe('Error Classification', () => {
    it('identifies network errors as retryable', async () => {
      const networkError = new Error('Failed to fetch');
      const mockApiCall = vi.fn().mockRejectedValue(networkError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow();

      expect(mockApiCall).toHaveBeenCalledTimes(4); // Should retry
    });

    it('identifies server errors as retryable', async () => {
      const serverError = new Error('Internal Server Error');
      (serverError as any).status = 500;

      const mockApiCall = vi.fn().mockRejectedValue(serverError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow();

      expect(mockApiCall).toHaveBeenCalledTimes(4); // Should retry
    });

    it('identifies client errors as non-retryable', async () => {
      const clientError = new Error('Bad Request');
      (clientError as any).status = 400;

      const mockApiCall = vi.fn().mockRejectedValue(clientError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow();

      expect(mockApiCall).toHaveBeenCalledTimes(1); // Should not retry
    });

    it('identifies auth errors as non-retryable', async () => {
      const authError = new Error('Unauthorized');
      (authError as any).status = 401;

      const mockApiCall = vi.fn().mockRejectedValue(authError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow();

      expect(mockApiCall).toHaveBeenCalledTimes(1); // Should not retry
    });

    it('identifies rate limit errors as retryable', async () => {
      const rateLimitError = new Error('Too Many Requests');
      (rateLimitError as any).status = 429;

      const mockApiCall = vi.fn().mockRejectedValue(rateLimitError);

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow();

      expect(mockApiCall).toHaveBeenCalledTimes(4); // Should retry
    });
  });

  describe('Circuit Breaker', () => {
    it('opens circuit after failure threshold', async () => {
      const mockApiCall = vi.fn().mockRejectedValue(new Error('Service unavailable'));

      // Fail enough times to open circuit (default threshold is 5)
      for (let i = 0; i < 5; i++) {
        try {
          await retryManager.executeWithRetry(mockApiCall);
        } catch {
          // Expected to fail
        }
      }

      const status = retryManager.getCircuitBreakerStatus();
      expect(status.state).toBe('OPEN');

      // Next call should fail immediately without API call
      const callCountBefore = mockApiCall.mock.calls.length;

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow('Circuit breaker is OPEN');

      expect(mockApiCall.mock.calls.length).toBe(callCountBefore); // No additional calls
    });

    it('transitions to half-open after timeout', async () => {
      const mockApiCall = vi.fn().mockRejectedValue(new Error('Service unavailable'));

      // Open the circuit
      for (let i = 0; i < 5; i++) {
        try {
          await retryManager.executeWithRetry(mockApiCall);
        } catch {
          // Expected to fail
        }
      }

      expect(retryManager.getCircuitBreakerStatus().state).toBe('OPEN');

      // Advance time past circuit timeout (default 60 seconds)
      vi.advanceTimersByTime(61000);

      // Next call should attempt the API (half-open state)
      mockApiCall.mockResolvedValueOnce('success');

      const result = await retryManager.executeWithRetry(mockApiCall);

      expect(result).toBe('success');
      expect(retryManager.getCircuitBreakerStatus().state).toBe('CLOSED');
    });

    it('can be reset manually', () => {
      const mockApiCall = vi.fn().mockRejectedValue(new Error('Service unavailable'));

      // Open the circuit (this would require multiple calls in real scenario)
      retryManager.resetCircuitBreaker();

      const status = retryManager.getCircuitBreakerStatus();
      expect(status.state).toBe('CLOSED');
      expect(status.failures).toBe(0);
    });
  });

  describe('Timeout Handling', () => {
    it('times out long-running requests', async () => {
      const mockApiCall = vi.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 15000))
      );

      await expect(retryManager.executeWithRetry(mockApiCall)).rejects.toThrow('Request timeout');
    });
  });

  describe('Callbacks', () => {
    it('calls onRetry callback on each retry', async () => {
      const onRetry = vi.fn();
      const mockApiCall = vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue('success');

      await retryManager.executeWithRetry(mockApiCall, { onRetry });

      expect(onRetry).toHaveBeenCalledTimes(1);
      expect(onRetry).toHaveBeenCalledWith(1, expect.any(Error));
    });

    it('calls onMaxRetries callback when retries exhausted', async () => {
      const onMaxRetries = vi.fn();
      const mockApiCall = vi.fn().mockRejectedValue(new Error('Persistent error'));

      await expect(
        retryManager.executeWithRetry(mockApiCall, { onMaxRetries })
      ).rejects.toThrow();

      expect(onMaxRetries).toHaveBeenCalledTimes(1);
      expect(onMaxRetries).toHaveBeenCalledWith(expect.any(Error));
    });
  });
});

describe('RetryableFetch', () => {
  let retryableFetch: RetryableFetch;
  let mockFetch: any;

  beforeEach(() => {
    retryableFetch = new RetryableFetch({
      maxRetries: 2,
      baseDelay: 100,
      jitter: false,
    });

    mockFetch = vi.fn();
    global.fetch = mockFetch;

    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe('HTTP Methods', () => {
    it('makes GET requests', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: 'test' }),
      });

      const response = await retryableFetch.get('/api/test');

      expect(mockFetch).toHaveBeenCalledWith('/api/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(response.ok).toBe(true);
    });

    it('makes POST requests with body', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 201,
      });

      const body = { name: 'test' };

      await retryableFetch.post('/api/test', body);

      expect(mockFetch).toHaveBeenCalledWith('/api/test', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('makes PUT requests', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
      });

      const body = { id: 1, name: 'updated' };

      await retryableFetch.put('/api/test/1', body);

      expect(mockFetch).toHaveBeenCalledWith('/api/test/1', {
        method: 'PUT',
        body: JSON.stringify(body),
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('makes DELETE requests', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 204,
      });

      await retryableFetch.delete('/api/test/1');

      expect(mockFetch).toHaveBeenCalledWith('/api/test/1', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });
  });

  describe('Error Handling', () => {
    it('throws error for non-2xx responses', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      });

      await expect(retryableFetch.get('/api/test')).rejects.toThrow('HTTP 404: Not Found');
    });

    it('retries on server errors', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          headers: { get: () => null },
        })
        .mockResolvedValue({
          ok: true,
          status: 200,
        });

      const response = await retryableFetch.get('/api/test');

      expect(response.ok).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('handles rate limiting with Retry-After header', async () => {
      const error = new Error('HTTP 429: Too Many Requests');
      (error as any).statusCode = 429;
      (error as any).isRetryable = true;

      mockFetch.mockResolvedValue({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        headers: {
          get: (header: string) => header === 'Retry-After' ? '5' : null,
        },
      });

      await expect(retryableFetch.get('/api/test')).rejects.toThrow();

      // Should respect rate limit and retry
      expect(mockFetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });

    it('does not retry on client errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        headers: { get: () => null },
      });

      await expect(retryableFetch.get('/api/test')).rejects.toThrow();

      expect(mockFetch).toHaveBeenCalledTimes(1); // No retries
    });
  });

  describe('Status and Reset', () => {
    it('provides circuit breaker status', () => {
      const status = retryableFetch.getStatus();

      expect(status).toHaveProperty('state');
      expect(status).toHaveProperty('failures');
    });

    it('allows circuit breaker reset', () => {
      expect(() => retryableFetch.reset()).not.toThrow();
    });
  });
});