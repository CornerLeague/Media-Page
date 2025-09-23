/**
 * API Performance Optimization Layer
 *
 * Provides request batching, caching, and performance monitoring
 * for the API client to improve onboarding flow performance.
 */

import { QueryClient } from '@tanstack/react-query';

// Performance metrics collection
interface APIMetrics {
  requestCount: number;
  totalResponseTime: number;
  averageResponseTime: number;
  cacheHitRate: number;
  errorRate: number;
  lastUpdated: Date;
}

class APIPerformanceMonitor {
  private metrics: APIMetrics = {
    requestCount: 0,
    totalResponseTime: 0,
    averageResponseTime: 0,
    cacheHitRate: 0,
    errorRate: 0,
    lastUpdated: new Date(),
  };

  private cacheHits = 0;
  private cacheAttempts = 0;
  private errors = 0;

  recordRequest(responseTime: number, fromCache: boolean = false) {
    this.metrics.requestCount++;
    this.metrics.totalResponseTime += responseTime;
    this.metrics.averageResponseTime = this.metrics.totalResponseTime / this.metrics.requestCount;

    this.cacheAttempts++;
    if (fromCache) {
      this.cacheHits++;
    }
    this.metrics.cacheHitRate = (this.cacheHits / this.cacheAttempts) * 100;
    this.metrics.lastUpdated = new Date();
  }

  recordError() {
    this.errors++;
    this.metrics.errorRate = (this.errors / this.metrics.requestCount) * 100;
  }

  getMetrics(): APIMetrics {
    return { ...this.metrics };
  }

  reset() {
    this.metrics = {
      requestCount: 0,
      totalResponseTime: 0,
      averageResponseTime: 0,
      cacheHitRate: 0,
      errorRate: 0,
      lastUpdated: new Date(),
    };
    this.cacheHits = 0;
    this.cacheAttempts = 0;
    this.errors = 0;
  }
}

// Request batching for efficient API calls
interface BatchedRequest {
  id: string;
  endpoint: string;
  params: Record<string, any>;
  resolve: (data: any) => void;
  reject: (error: any) => void;
  timestamp: number;
}

class APIBatcher {
  private pendingRequests: Map<string, BatchedRequest[]> = new Map();
  private batchTimeout: NodeJS.Timeout | null = null;
  private readonly BATCH_DELAY = 50; // 50ms batching window
  private readonly MAX_BATCH_SIZE = 10;

  async batchRequest<T>(
    endpoint: string,
    params: Record<string, any>,
    fetchFn: (batchedParams: Record<string, any>[]) => Promise<T[]>
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const requestId = Math.random().toString(36).substr(2, 9);
      const request: BatchedRequest = {
        id: requestId,
        endpoint,
        params,
        resolve,
        reject,
        timestamp: Date.now(),
      };

      // Add to batch
      if (!this.pendingRequests.has(endpoint)) {
        this.pendingRequests.set(endpoint, []);
      }
      this.pendingRequests.get(endpoint)!.push(request);

      // Schedule batch execution
      this.scheduleBatchExecution(endpoint, fetchFn);
    });
  }

  private scheduleBatchExecution<T>(
    endpoint: string,
    fetchFn: (batchedParams: Record<string, any>[]) => Promise<T[]>
  ) {
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
    }

    this.batchTimeout = setTimeout(() => {
      this.executeBatch(endpoint, fetchFn);
    }, this.BATCH_DELAY);

    // Execute immediately if batch is full
    const requests = this.pendingRequests.get(endpoint) || [];
    if (requests.length >= this.MAX_BATCH_SIZE) {
      clearTimeout(this.batchTimeout);
      this.executeBatch(endpoint, fetchFn);
    }
  }

  private async executeBatch<T>(
    endpoint: string,
    fetchFn: (batchedParams: Record<string, any>[]) => Promise<T[]>
  ) {
    const requests = this.pendingRequests.get(endpoint) || [];
    if (requests.length === 0) return;

    this.pendingRequests.delete(endpoint);

    try {
      const batchedParams = requests.map(req => req.params);
      const results = await fetchFn(batchedParams);

      // Resolve each request with its corresponding result
      requests.forEach((request, index) => {
        if (results[index]) {
          request.resolve(results[index]);
        } else {
          request.reject(new Error('No result for batched request'));
        }
      });
    } catch (error) {
      // Reject all requests in the batch
      requests.forEach(request => {
        request.reject(error);
      });
    }
  }
}

// Memory-efficient cache implementation
class MemoryCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly MAX_CACHE_SIZE = 100;

  set(key: string, data: any, ttl: number = this.DEFAULT_TTL) {
    // Implement LRU eviction if cache is full
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  get(key: string): any | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    // Check if expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    // Move to end (LRU)
    this.cache.delete(key);
    this.cache.set(key, entry);

    return entry.data;
  }

  clear() {
    this.cache.clear();
  }

  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.MAX_CACHE_SIZE,
      keys: Array.from(this.cache.keys()),
    };
  }
}

// Enhanced query client configuration for optimal performance
export function createOptimizedQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Optimized stale time for different data types
        staleTime: 5 * 60 * 1000, // 5 minutes for general data
        gcTime: 10 * 60 * 1000, // 10 minutes garbage collection

        // Smart retry strategy
        retry: (failureCount, error) => {
          // Don't retry on 4xx errors (except 429 rate limit)
          if (error && typeof error === 'object' && 'status' in error) {
            const status = (error as any).status;
            if (status >= 400 && status < 500 && status !== 429) {
              return false;
            }
          }
          return failureCount < 3;
        },

        // Exponential backoff with jitter
        retryDelay: (attemptIndex) => {
          const baseDelay = Math.min(1000 * 2 ** attemptIndex, 30000);
          const jitter = Math.random() * 1000;
          return baseDelay + jitter;
        },

        // Network mode optimization
        networkMode: 'online',

        // Refetch configuration
        refetchOnWindowFocus: false,
        refetchOnReconnect: 'always',
        refetchOnMount: true,
      },
      mutations: {
        retry: 1,
        networkMode: 'online',
      },
    },
  });
}

// Prefetching strategies for onboarding flow
export class OnboardingPrefetcher {
  constructor(private queryClient: QueryClient) {}

  // Prefetch next step data
  async prefetchNextStep(currentStep: number, userContext: any) {
    const prefetchPromises: Promise<any>[] = [];

    switch (currentStep) {
      case 1: // Welcome -> Sports Selection
        prefetchPromises.push(
          this.queryClient.prefetchQuery({
            queryKey: ['sports', 'onboarding'],
            queryFn: () => this.fetchSports(),
            staleTime: 10 * 60 * 1000, // 10 minutes for sports data
          })
        );
        break;

      case 2: // Sports Selection -> Team Selection
        if (userContext.selectedSports) {
          prefetchPromises.push(
            this.queryClient.prefetchQuery({
              queryKey: ['teams', 'onboarding', userContext.selectedSports],
              queryFn: () => this.fetchTeams(userContext.selectedSports),
              staleTime: 15 * 60 * 1000, // 15 minutes for team data
            })
          );
        }
        break;

      case 3: // Team Selection -> Preferences
        prefetchPromises.push(
          this.queryClient.prefetchQuery({
            queryKey: ['preferences', 'defaults'],
            queryFn: () => this.fetchDefaultPreferences(),
            staleTime: 30 * 60 * 1000, // 30 minutes for preference defaults
          })
        );
        break;
    }

    await Promise.allSettled(prefetchPromises);
  }

  // Prefetch critical path assets
  async prefetchCriticalAssets() {
    // Prefetch commonly used team logos
    const criticalLogos = [
      '/logos/nfl-teams.webp',
      '/logos/nba-teams.webp',
      '/logos/mlb-teams.webp',
    ];

    const prefetchPromises = criticalLogos.map(logo =>
      new Promise((resolve) => {
        const img = new Image();
        img.onload = resolve;
        img.onerror = resolve; // Don't fail on image errors
        img.src = logo;
      })
    );

    await Promise.allSettled(prefetchPromises);
  }

  private async fetchSports() {
    // Implement sports fetching logic
    return [];
  }

  private async fetchTeams(sportIds: string[]) {
    // Implement teams fetching logic
    return [];
  }

  private async fetchDefaultPreferences() {
    // Implement preferences fetching logic
    return {};
  }
}

// Create singleton instances
export const performanceMonitor = new APIPerformanceMonitor();
export const apiBatcher = new APIBatcher();
export const memoryCache = new MemoryCache();

// Performance wrapper for API calls
export function withPerformanceMonitoring<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  endpoint: string
): T {
  return (async (...args: any[]) => {
    const startTime = performance.now();
    const cacheKey = `${endpoint}-${JSON.stringify(args)}`;

    // Check cache first
    const cachedResult = memoryCache.get(cacheKey);
    if (cachedResult) {
      const endTime = performance.now();
      performanceMonitor.recordRequest(endTime - startTime, true);
      return cachedResult;
    }

    try {
      const result = await fn(...args);
      const endTime = performance.now();
      const responseTime = endTime - startTime;

      // Cache successful results
      memoryCache.set(cacheKey, result);
      performanceMonitor.recordRequest(responseTime, false);

      // Log slow requests
      if (responseTime > 1000) {
        console.warn(`Slow API request: ${endpoint} took ${responseTime.toFixed(2)}ms`);
      }

      return result;
    } catch (error) {
      const endTime = performance.now();
      performanceMonitor.recordRequest(endTime - startTime, false);
      performanceMonitor.recordError();
      throw error;
    }
  }) as T;
}

// Export performance utilities
export {
  APIPerformanceMonitor,
  APIBatcher,
  MemoryCache,
};