/**
 * API Client for Corner League Media Backend Integration
 *
 * This module provides a typed interface for FastAPI backend integration with Firebase authentication.
 * It includes Firebase JWT authentication, error handling, retry logic, and request/response types.
 */

import { ApiRetryManager, RetryConfig } from '@/lib/api-retry';
import { logApiRequest, logApiResponse, logApiError } from '@/lib/debug-utilities';
import { getSportUUIDs, sportSlugsToUuids } from '@/lib/sport-id-mapper';

// User Preferences Type Definition
export interface UserPreferences {
  newsTypes: Array<{
    type: string;
    enabled: boolean;
    priority: number;
  }>;
  notifications: {
    push: boolean;
    email: boolean;
    gameReminders: boolean;
    newsAlerts: boolean;
    scoreUpdates: boolean;
  };
  contentFrequency: 'minimal' | 'standard' | 'comprehensive';
}

// API Base Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  VERSION: 'v1',
  TIMEOUT: 10000,
} as const;

// Firebase Authentication Types
export interface FirebaseAuthContext {
  getIdToken: (forceRefresh?: boolean) => Promise<string | null>;
  isAuthenticated: boolean;
  userId?: string;
}

export interface FirebaseUser {
  uid: string;
  email: string | null;
  displayName?: string | null;
  photoURL?: string | null;
  emailVerified: boolean;
}

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// User API Types
export interface CreateUserRequest {
  firebaseUserId: string;
  displayName?: string;
  email?: string;
  sports: Array<{
    sportId: string;
    name: string;
    rank: number;
    hasTeams: boolean;
  }>;
  teams: Array<{
    teamId: string;
    name: string;
    sportId: string;
    league: string;
    affinityScore: number;
  }>;
  preferences: {
    newsTypes: Array<{
      type: string;
      enabled: boolean;
      priority: number;
    }>;
    notifications: {
      push: boolean;
      email: boolean;
      gameReminders: boolean;
      newsAlerts: boolean;
      scoreUpdates: boolean;
    };
    contentFrequency: 'minimal' | 'standard' | 'comprehensive';
  };
}

export interface UpdateUserPreferencesRequest {
  sports?: CreateUserRequest['sports'];
  teams?: CreateUserRequest['teams'];
  preferences?: CreateUserRequest['preferences'];
}

export interface UserProfile {
  id: string;
  firebaseUserId: string;
  displayName?: string;
  email?: string;
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}

// Sports Content Types
export interface SportsFeedItem {
  id: string;
  title: string;
  summary: string;
  content: string;
  source: string;
  author?: string;
  publishedAt: string;
  category: 'injuries' | 'trades' | 'roster' | 'general' | 'scores' | 'analysis';
  teams: string[];
  sports: string[];
  priority: number;
  imageUrl?: string;
  externalUrl?: string;
}

// New Dashboard Types
export interface GameScore {
  gameId: string;
  status: 'FINAL' | 'LIVE' | 'SCHEDULED';
  home: {
    id: string;
    name?: string;
    pts: number;
  };
  away: {
    id: string;
    name?: string;
    pts: number;
  };
  period?: string;
  timeRemaining?: string;
}

export interface RecentResult {
  gameId: string;
  result: 'W' | 'L' | 'T';
  diff: number;
  date: string;
  opponent?: string;
}

export interface AISummary {
  text: string;
  generated_at: string;
}

export interface NewsArticle {
  id: string;
  title: string;
  category: 'injuries' | 'roster' | 'trade' | 'general';
  published_at: string;
  summary?: string;
  url?: string;
}

export interface DepthChartEntry {
  position: string;
  player_name: string;
  depth_order: number;
  jersey_number?: number;
  experience?: string;
}

export interface TicketDeal {
  provider: string;
  price: number;
  section: string;
  deal_score: number;
  game_date?: string;
  quantity?: number;
}

export interface FanExperience {
  type: 'watch_party' | 'tailgate' | 'viewing' | 'meetup';
  title: string;
  start_time: string;
  location?: string;
  description?: string;
  attendees?: number;
}

export interface TeamDashboard {
  team: {
    id: string;
    name: string;
    market?: string;
    league?: string;
    logo?: string;
    colors?: {
      primary: string;
      secondary: string;
    };
  };
  latestScore?: GameScore;
  recentResults: RecentResult[];
  summary: AISummary;
  news: NewsArticle[];
  depthChart: DepthChartEntry[];
  ticketDeals: TicketDeal[];
  experiences: FanExperience[];
}

export interface HomeData {
  most_liked_team_id: string;
  user_teams: Array<{
    team_id: string;
    name: string;
    affinity_score: number;
  }>;
}

// Onboarding API Types
export interface OnboardingSport {
  id: string;
  name: string;
  icon: string;
  hasTeams: boolean;
  isPopular: boolean;
}

export interface OnboardingTeam {
  id: string;
  name: string;
  market: string;
  sportId: string;
  league: string;
  logo?: string;
  colors?: {
    primary: string;
    secondary: string;
  };
}

export interface OnboardingStatus {
  currentStep: number;
  totalSteps: number;
  isComplete: boolean;
  selectedSports: Array<{
    sportId: string;
    rank: number;
  }>;
  selectedTeams: Array<{
    teamId: string;
    sportId: string;
    affinityScore: number;
  }>;
  preferences: {
    newsTypes: Array<{
      type: string;
      enabled: boolean;
      priority: number;
    }>;
    notifications: {
      push: boolean;
      email: boolean;
      gameReminders: boolean;
      newsAlerts: boolean;
      scoreUpdates: boolean;
    };
    contentFrequency: 'minimal' | 'standard' | 'comprehensive';
  };
}

// Backend API compatible onboarding status
export interface OnboardingStatusResponse {
  hasCompletedOnboarding: boolean;
  currentStep?: number | null;
}

export interface UpdateOnboardingStepRequest {
  step: number;
  data?: {
    sports?: Array<{
      sportId: string;
      rank: number;
    }>;
    teams?: Array<{
      teamId: string;
      sportId: string;
      affinityScore: number;
    }>;
    preferences?: OnboardingStatus['preferences'];
  };
}

export interface CompleteOnboardingRequest {
  sports: Array<{
    sportId: string;
    name: string;
    rank: number;
    hasTeams: boolean;
  }>;
  teams: Array<{
    teamId: string;
    name: string;
    sportId: string;
    league: string;
    affinityScore: number;
  }>;
  preferences: OnboardingStatus['preferences'];
}

// HTTP Client Class
export class ApiClient {
  private baseUrl: string;
  private firebaseAuth: FirebaseAuthContext | null = null;
  private retryManager: ApiRetryManager;
  private enableRetries: boolean;

  constructor(
    baseUrl = API_CONFIG.BASE_URL,
    retryConfig?: Partial<RetryConfig>,
    enableRetries = true
  ) {
    this.baseUrl = `${baseUrl}/api/${API_CONFIG.VERSION}`;
    this.retryManager = new ApiRetryManager(retryConfig);
    this.enableRetries = enableRetries;
  }

  // Firebase Authentication Methods
  setFirebaseAuth(auth: FirebaseAuthContext): void {
    this.firebaseAuth = auth;
  }

  getFirebaseAuth(): FirebaseAuthContext | null {
    return this.firebaseAuth;
  }

  private async getAuthToken(): Promise<string | null> {
    if (!this.firebaseAuth || !this.firebaseAuth.isAuthenticated) {
      return null;
    }

    try {
      return await this.firebaseAuth.getIdToken();
    } catch (error) {
      console.error('Failed to get Firebase token:', error);
      return null;
    }
  }

  // Core HTTP Methods with Retry Support
  private async request<T>(
    endpoint: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
      body?: any;
      params?: Record<string, string | number | boolean>;
      skipAuth?: boolean;
      timeout?: number;
      retryConfig?: Partial<RetryConfig>;
      skipRetry?: boolean;
    } = {}
  ): Promise<T> {
    const {
      method = 'GET',
      body,
      params,
      skipAuth = false,
      timeout = API_CONFIG.TIMEOUT,
      retryConfig,
      skipRetry = false,
    } = options;

    // Build URL with query parameters
    const url = new URL(`${this.baseUrl}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    // Create the actual request function
    const makeRequest = async (): Promise<T> => {
      const startTime = Date.now();

      // Log API request for debugging
      logApiRequest(method, endpoint, body);

      // Build headers (fresh for each attempt to handle token refresh)
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add Firebase authentication if not skipped and user is signed in
      if (!skipAuth && this.firebaseAuth?.isAuthenticated) {
        try {
          const token = await this.getAuthToken();
          if (token) {
            headers['Authorization'] = `Bearer ${token}`;
          }
        } catch (error) {
          console.error('Failed to set authorization header:', error);
          const authError = new ApiClientError({
            code: 'AUTH_ERROR',
            message: 'Authentication failed',
            timestamp: new Date().toISOString(),
          }, 401);

          logApiError(method, endpoint, authError, Date.now() - startTime);
          throw authError;
        }
      }

      // Create request with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(url.toString(), {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData: ApiError = await response.json().catch(() => ({
            code: 'HTTP_ERROR',
            message: `HTTP ${response.status}: ${response.statusText}`,
            timestamp: new Date().toISOString(),
          }));

          const apiError = new ApiClientError(errorData, response.status);

          // Enhance error with retry information
          (apiError as any).isRetryable = response.status >= 500 || response.status === 429;
          (apiError as any).retryAfter = response.headers.get('Retry-After');

          // Log API error for debugging
          logApiError(method, endpoint, apiError, Date.now() - startTime);

          throw apiError;
        }

        const result = await response.json();

        // Log successful API response for debugging
        logApiResponse(method, endpoint, result, Date.now() - startTime);

        // Handle both wrapped and direct response formats
        if (result && typeof result === 'object' && 'data' in result) {
          // Wrapped format: { data: T, message?: string, status: string, timestamp: string }
          return result.data;
        } else {
          // Direct format: T (raw data)
          return result;
        }
      } catch (error) {
        clearTimeout(timeoutId);

        if (error instanceof ApiClientError) {
          // Log already handled ApiClientError
          logApiError(method, endpoint, error, Date.now() - startTime);
          throw error;
        }

        if (error instanceof Error && error.name === 'AbortError') {
          const timeoutError = new ApiClientError({
            code: 'TIMEOUT',
            message: `Request timed out after ${timeout}ms`,
            timestamp: new Date().toISOString(),
          }, 408);

          logApiError(method, endpoint, timeoutError, Date.now() - startTime);
          throw timeoutError;
        }

        // Network or other errors
        const networkError = new ApiClientError({
          code: 'NETWORK_ERROR',
          message: error instanceof Error ? error.message : 'Network request failed',
          timestamp: new Date().toISOString(),
        }, 0);

        logApiError(method, endpoint, networkError, Date.now() - startTime);

        (networkError as any).isRetryable = true;
        throw networkError;
      }
    };

    // Use retry logic if enabled and not explicitly skipped
    if (this.enableRetries && !skipRetry) {
      return this.retryManager.executeWithRetry(makeRequest, {
        ...retryConfig,
        onRetry: (attempt, error) => {
          console.log(`API request retry ${attempt} for ${method} ${endpoint}:`, error.message);
          // Call custom retry callback if provided
          retryConfig?.onRetry?.(attempt, error);
        },
        onMaxRetries: (error) => {
          console.error(`API request failed after max retries for ${method} ${endpoint}:`, error);
          retryConfig?.onMaxRetries?.(error);
        },
      });
    } else {
      return makeRequest();
    }
  }

  // User API Methods
  async getCurrentUser(): Promise<UserProfile> {
    return this.request<UserProfile>('/users/me');
  }

  async createUser(userData: CreateUserRequest): Promise<UserProfile> {
    return this.request<UserProfile>('/users/me', {
      method: 'PUT',
      body: userData,
    });
  }

  async updateUserPreferences(preferences: UpdateUserPreferencesRequest): Promise<UserProfile> {
    return this.request<UserProfile>('/users/me/preferences', {
      method: 'PUT',
      body: preferences,
    });
  }

  async deleteUser(): Promise<void> {
    return this.request<void>('/users/me', {
      method: 'DELETE',
    });
  }

  // Sports Content API Methods
  async getSportsFeed(params?: {
    page?: number;
    pageSize?: number;
    category?: string;
    teamId?: string;
    sportId?: string;
  }): Promise<PaginatedResponse<SportsFeedItem>> {
    return this.request<PaginatedResponse<SportsFeedItem>>('/sports/feed', {
      params,
    });
  }

  async getTeamDashboard(teamId: string): Promise<TeamDashboard> {
    return this.request<TeamDashboard>(`/teams/${teamId}/dashboard`);
  }

  async getPersonalizedContent(): Promise<SportsFeedItem[]> {
    return this.request<SportsFeedItem[]>('/sports/personalized');
  }

  // New Dashboard API Methods
  async getHomeData(): Promise<HomeData> {
    return this.request<HomeData>('/me/home');
  }

  // Onboarding API Methods
  async getOnboardingStatus(): Promise<OnboardingStatusResponse> {
    return this.request<OnboardingStatusResponse>('/auth/onboarding-status');
  }

  async updateOnboardingStep(data: UpdateOnboardingStepRequest): Promise<OnboardingStatus> {
    return this.request<OnboardingStatus>('/onboarding/step', {
      method: 'PUT',
      body: data,
    });
  }

  async getOnboardingSports(): Promise<OnboardingSport[]> {
    return this.request<OnboardingSport[]>('/onboarding/sports');
  }

  async getOnboardingTeams(sportIds: string[]): Promise<OnboardingTeam[]> {
    // Convert sport slugs to UUIDs for backend compatibility
    const sportUuids = sportSlugsToUuids(sportIds);

    if (sportUuids.length === 0) {
      console.warn('No valid sport UUIDs found for slugs:', sportIds);
      return [];
    }

    return this.request<OnboardingTeam[]>('/onboarding/teams', {
      params: { sport_ids: sportUuids.join(',') },
    });
  }

  async completeOnboarding(data: CompleteOnboardingRequest): Promise<UserProfile> {
    return this.request<UserProfile>('/onboarding/complete', {
      method: 'POST',
      body: data,
    });
  }

  async resetOnboarding(): Promise<void> {
    return this.request<void>('/onboarding/reset', {
      method: 'POST',
    });
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request<{ status: string; timestamp: string }>('/health', {
      skipAuth: true,
    });
  }

  // Retry and Circuit Breaker Management
  enableRetry(enable: boolean = true): void {
    this.enableRetries = enable;
  }

  getCircuitBreakerStatus(): { state: string; failures: number } {
    return this.retryManager.getCircuitBreakerStatus();
  }

  resetCircuitBreaker(): void {
    this.retryManager.resetCircuitBreaker();
  }

  // Request with custom retry configuration
  async requestWithRetry<T>(
    endpoint: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
      body?: any;
      params?: Record<string, string | number | boolean>;
      skipAuth?: boolean;
      timeout?: number;
    } = {},
    retryConfig?: Partial<RetryConfig>
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      retryConfig,
    });
  }

  // Request without retry (for operations that should not be retried)
  async requestWithoutRetry<T>(
    endpoint: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
      body?: any;
      params?: Record<string, string | number | boolean>;
      skipAuth?: boolean;
      timeout?: number;
    } = {}
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      skipRetry: true,
    });
  }
}

// Custom Error Class
export class ApiClientError extends Error {
  public readonly apiError: ApiError;
  public readonly statusCode: number;

  constructor(apiError: ApiError, statusCode: number) {
    super(apiError.message);
    this.name = 'ApiClientError';
    this.apiError = apiError;
    this.statusCode = statusCode;
  }

  get code(): string {
    return this.apiError.code;
  }

  get details(): Record<string, any> | undefined {
    return this.apiError.details;
  }

  get timestamp(): string {
    return this.apiError.timestamp;
  }
}

// Default client instance
export const apiClient = new ApiClient();

// Firebase-integrated API client hook
export const useFirebaseApiClient = () => {
  // This will be used in React components to set up the API client with Firebase auth
  return apiClient;
};

// Hook for React Query integration with Firebase authentication
export const createApiQueryClient = (firebaseAuth?: FirebaseAuthContext) => {
  // Set Firebase auth if provided
  if (firebaseAuth) {
    apiClient.setFirebaseAuth(firebaseAuth);
  }

  return {
    // User queries
    getCurrentUser: () => ({
      queryKey: ['user', 'current'],
      queryFn: () => {
        if (!firebaseAuth?.isAuthenticated) {
          return Promise.reject(new Error('Authentication required'));
        }
        return apiClient.getCurrentUser();
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: firebaseAuth?.isAuthenticated ?? false,
    }),

    // Home dashboard queries
    getHomeData: () => ({
      queryKey: ['home', 'data'],
      queryFn: () => {
        if (!firebaseAuth?.isAuthenticated) {
          return Promise.reject(new Error('Authentication required'));
        }
        return apiClient.getHomeData();
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: firebaseAuth?.isAuthenticated ?? false,
    }),

    // Sports feed queries
    getSportsFeed: (params?: Parameters<typeof apiClient.getSportsFeed>[0]) => ({
      queryKey: ['sports', 'feed', params],
      queryFn: () => apiClient.getSportsFeed(params),
      staleTime: 2 * 60 * 1000, // 2 minutes
    }),

    // Team dashboard queries
    getTeamDashboard: (teamId: string) => ({
      queryKey: ['team', 'dashboard', teamId],
      queryFn: () => {
        if (!firebaseAuth?.isAuthenticated) {
          return Promise.reject(new Error('Authentication required'));
        }
        if (!teamId) {
          return Promise.reject(new Error('Team ID required'));
        }
        return apiClient.getTeamDashboard(teamId);
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: (firebaseAuth?.isAuthenticated ?? false) && !!teamId,
    }),

    // Onboarding queries
    getOnboardingStatus: () => ({
      queryKey: ['auth', 'onboarding-status'],
      queryFn: () => {
        if (!firebaseAuth?.isAuthenticated) {
          return Promise.reject(new Error('Authentication required'));
        }
        return apiClient.getOnboardingStatus();
      },
      staleTime: 1 * 60 * 1000, // 1 minute
      enabled: firebaseAuth?.isAuthenticated ?? false,
    }),

    getOnboardingSports: () => ({
      queryKey: ['onboarding', 'sports'],
      queryFn: () => apiClient.getOnboardingSports(),
      staleTime: 30 * 60 * 1000, // 30 minutes (static data)
    }),

    getOnboardingTeams: (sportIds: string[]) => {
      // Convert to UUIDs for consistent cache keys
      const sportUuids = sportSlugsToUuids(sportIds);

      return {
        queryKey: ['onboarding', 'teams', sportUuids],
        queryFn: () => apiClient.getOnboardingTeams(sportIds),
        staleTime: 30 * 60 * 1000, // 30 minutes (static data)
        enabled: sportIds.length > 0,
      };
    },
  };
};

export default apiClient;