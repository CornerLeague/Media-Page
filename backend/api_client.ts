/**
 * TypeScript API Client for Corner League Media Backend
 *
 * Provides a fully typed client for the backend API with support for
 * enhanced search functionality, caching, and error handling.
 */

// Types based on backend schemas
export interface TeamResponse {
  id: string;
  sport_id: string;
  league_id?: string;
  name: string;
  market: string;
  slug: string;
  abbreviation?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  is_active: boolean;
  external_id?: string;
  official_name?: string;
  short_name?: string;
  country_code?: string;
  founding_year?: number;
  sport_name?: string;
  league_name?: string;
  display_name?: string;
  computed_short_name?: string;
  computed_official_name?: string;
  leagues: LeagueInfo[];
}

export interface LeagueInfo {
  id: string;
  name: string;
  slug: string;
  country_code?: string;
  league_level?: number;
  competition_type?: string;
  is_primary: boolean;
  season_start_year?: number;
  position_last_season?: number;
}

export interface SearchMatchInfo {
  field: string;
  value: string;
  highlighted: string;
}

export interface EnhancedTeamResponse extends TeamResponse {
  search_matches: SearchMatchInfo[];
  relevance_score?: number;
}

export interface SearchMetadata {
  query?: string;
  total_matches: number;
  response_time_ms: number;
  filters_applied: Record<string, any>;
  timestamp: string;
}

export interface TeamsPaginatedResponse {
  items: TeamResponse[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface EnhancedTeamsPaginatedResponse {
  items: EnhancedTeamResponse[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
  search_metadata: SearchMetadata;
}

export interface TeamSearchSuggestion {
  suggestion: string;
  type: 'team_name' | 'market' | 'abbreviation';
  team_count: number;
  preview_teams: string[];
}

export interface SearchSuggestionsResponse {
  query: string;
  suggestions: TeamSearchSuggestion[];
  response_time_ms: number;
}

export interface SportResponse {
  id: string;
  name: string;
  slug: string;
  has_teams: boolean;
  icon?: string;
  is_active: boolean;
  display_order: number;
  leagues_count?: number;
}

export interface TeamSearchParams {
  query?: string;
  sport_id?: string;
  league_id?: string;
  market?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}

// Error classes
export class ApiClientError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'ApiClientError';
  }
}

export class ApiClientTimeoutError extends ApiClientError {
  constructor(message: string) {
    super(message);
    this.name = 'ApiClientTimeoutError';
  }
}

export class ApiClientValidationError extends ApiClientError {
  constructor(message: string) {
    super(message);
    this.name = 'ApiClientValidationError';
  }
}

// Simple cache implementation
class SearchCache {
  private cache = new Map<string, { data: any; expires: number }>();

  constructor(private ttlMs: number = 300000) {} // 5 minutes default

  private getCacheKey(endpoint: string, params: Record<string, any>): string {
    const paramStr = Object.entries(params)
      .filter(([_, value]) => value !== null && value !== undefined)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}=${value}`)
      .join('&');
    return `${endpoint}?${paramStr}`;
  }

  get(endpoint: string, params: Record<string, any>): any | null {
    const key = this.getCacheKey(endpoint, params);
    const cached = this.cache.get(key);

    if (cached && Date.now() < cached.expires) {
      return cached.data;
    }

    if (cached) {
      this.cache.delete(key);
    }

    return null;
  }

  set(endpoint: string, params: Record<string, any>, data: any): void {
    const key = this.getCacheKey(endpoint, params);
    this.cache.set(key, {
      data,
      expires: Date.now() + this.ttlMs
    });
  }

  clear(): void {
    this.cache.clear();
  }

  getStats(): { cachedItems: number; ttlMs: number } {
    return {
      cachedItems: this.cache.size,
      ttlMs: this.ttlMs
    };
  }
}

export interface ApiClientOptions {
  baseUrl?: string;
  timeout?: number;
  cacheTtlMs?: number;
  maxRetries?: number;
}

/**
 * Corner League Media API Client
 *
 * Features:
 * - Fully typed methods with validation
 * - Request caching for performance
 * - Automatic retry with exponential backoff
 * - Comprehensive error handling
 * - Search debouncing support
 */
export class CornerLeagueApiClient {
  private baseUrl: string;
  private timeout: number;
  private maxRetries: number;
  private cache: SearchCache;
  private abortController?: AbortController;
  private lastSearchPromise?: Promise<any>;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = (options.baseUrl || 'http://127.0.0.1:8001').replace(/\/$/, '');
    this.timeout = options.timeout || 30000;
    this.maxRetries = options.maxRetries || 3;
    this.cache = new SearchCache(options.cacheTtlMs);
  }

  private async request<T>(
    method: string,
    endpoint: string,
    params?: Record<string, any>
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    let lastError: Error;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url.toString(), {
          method,
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

          try {
            const errorData = JSON.parse(errorText);
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } catch {
            // Use default message if JSON parsing fails
          }

          if (response.status >= 500 && attempt < this.maxRetries) {
            // Retry server errors
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
            continue;
          }

          throw new ApiClientError(errorMessage, response.status);
        }

        return await response.json();

      } catch (error) {
        lastError = error as Error;

        if (error instanceof ApiClientError) {
          throw error;
        }

        if (error instanceof Error && error.name === 'AbortError') {
          if (attempt === this.maxRetries) {
            throw new ApiClientTimeoutError(`Request timed out after ${this.maxRetries} retries`);
          }
        } else if (attempt === this.maxRetries) {
          throw new ApiClientError(`Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }

        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }

    throw lastError!;
  }

  /**
   * Search teams with basic pagination
   */
  async searchTeams(params: TeamSearchParams = {}, useCache = true): Promise<TeamsPaginatedResponse> {
    const searchParams = {
      query: params.query,
      sport_id: params.sport_id,
      league_id: params.league_id,
      market: params.market,
      is_active: params.is_active ?? true,
      page: params.page ?? 1,
      page_size: params.page_size ?? 20,
    };

    // Check cache first
    if (useCache) {
      const cached = this.cache.get('/api/teams/search', searchParams);
      if (cached) {
        return cached;
      }
    }

    const result = await this.request<TeamsPaginatedResponse>('GET', '/api/teams/search', searchParams);

    // Cache the result
    if (useCache) {
      this.cache.set('/api/teams/search', searchParams, result);
    }

    return result;
  }

  /**
   * Enhanced team search with highlighting, relevance scoring, and metadata
   */
  async searchTeamsEnhanced(params: TeamSearchParams = {}, useCache = true): Promise<EnhancedTeamsPaginatedResponse> {
    const searchParams = {
      query: params.query,
      sport_id: params.sport_id,
      league_id: params.league_id,
      market: params.market,
      is_active: params.is_active ?? true,
      page: params.page ?? 1,
      page_size: params.page_size ?? 20,
    };

    // Check cache first
    if (useCache) {
      const cached = this.cache.get('/api/teams/search-enhanced', searchParams);
      if (cached) {
        return cached;
      }
    }

    const result = await this.request<EnhancedTeamsPaginatedResponse>('GET', '/api/teams/search-enhanced', searchParams);

    // Cache the result
    if (useCache) {
      this.cache.set('/api/teams/search-enhanced', searchParams, result);
    }

    return result;
  }

  /**
   * Get search suggestions/autocomplete for team search
   */
  async getSearchSuggestions(query: string, limit = 10, useCache = true): Promise<SearchSuggestionsResponse> {
    if (query.length < 1) {
      throw new Error('Query must be at least 1 character long');
    }

    const params = { query, limit };

    // Check cache first
    if (useCache) {
      const cached = this.cache.get('/api/teams/search-suggestions', params);
      if (cached) {
        return cached;
      }
    }

    const result = await this.request<SearchSuggestionsResponse>('GET', '/api/teams/search-suggestions', params);

    // Cache the result
    if (useCache) {
      this.cache.set('/api/teams/search-suggestions', params, result);
    }

    return result;
  }

  /**
   * Debounced team search - cancels previous search if called again quickly
   */
  async searchTeamsDebounced(
    query?: string,
    params: Omit<TeamSearchParams, 'query'> = {},
    debounceMs = 300
  ): Promise<EnhancedTeamsPaginatedResponse | null> {
    // Cancel previous search
    if (this.abortController) {
      this.abortController.abort();
    }

    this.abortController = new AbortController();

    try {
      // Wait for debounce period
      await new Promise((resolve, reject) => {
        const timeoutId = setTimeout(resolve, debounceMs);
        this.abortController!.signal.addEventListener('abort', () => {
          clearTimeout(timeoutId);
          reject(new Error('Cancelled'));
        });
      });

      // Perform search
      return await this.searchTeamsEnhanced({ ...params, query });

    } catch (error) {
      if (error instanceof Error && error.message === 'Cancelled') {
        return null; // Search was cancelled
      }
      throw error;
    }
  }

  /**
   * Get all sports
   */
  async getSports(
    includeLeagues = false,
    includeInactive = false,
    useCache = true
  ): Promise<SportResponse[]> {
    const params = {
      include_leagues: includeLeagues,
      include_inactive: includeInactive,
    };

    // Check cache first
    if (useCache) {
      const cached = this.cache.get('/api/sports', params);
      if (cached) {
        return cached;
      }
    }

    const result = await this.request<SportResponse[]>('GET', '/api/sports', params);

    // Cache the result
    if (useCache) {
      this.cache.set('/api/sports', params, result);
    }

    return result;
  }

  /**
   * Clear all cached API results
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { cachedItems: number; ttlMs: number } {
    return this.cache.getStats();
  }

  /**
   * Cancel any ongoing debounced searches
   */
  cancelDebouncedSearch(): void {
    if (this.abortController) {
      this.abortController.abort();
    }
  }
}

// Convenience functions
export function createClient(options?: ApiClientOptions): CornerLeagueApiClient {
  return new CornerLeagueApiClient(options);
}

export async function quickSearch(query: string, params?: Omit<TeamSearchParams, 'query'>): Promise<EnhancedTeamsPaginatedResponse> {
  const client = createClient();
  return await client.searchTeamsEnhanced({ ...params, query });
}

export async function quickSuggestions(query: string, limit?: number): Promise<SearchSuggestionsResponse> {
  const client = createClient();
  return await client.getSearchSuggestions(query, limit);
}

// Export default instance
export const apiClient = createClient();

// Example usage
export async function exampleUsage() {
  const client = createClient();

  try {
    // Enhanced search with highlighting
    const results = await client.searchTeamsEnhanced({ query: 'Chicago' });
    console.log(`Found ${results.total} teams in ${results.search_metadata.response_time_ms.toFixed(1)}ms`);

    for (const team of results.items.slice(0, 3)) {
      console.log(`- ${team.display_name} (relevance: ${team.relevance_score})`);
      for (const match of team.search_matches) {
        console.log(`  ${match.field}: ${match.highlighted}`);
      }
    }

    // Get search suggestions
    const suggestions = await client.getSearchSuggestions('Chi');
    console.log('\nSuggestions for "Chi":');
    for (const suggestion of suggestions.suggestions.slice(0, 5)) {
      console.log(`- ${suggestion.suggestion} (${suggestion.type}) - ${suggestion.team_count} teams`);
    }

  } catch (error) {
    console.error('API Error:', error);
  }
}