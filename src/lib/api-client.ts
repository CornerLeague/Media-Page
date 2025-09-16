/**
 * API Client for Corner League Media Backend Integration
 *
 * This module provides a typed interface for FastAPI backend integration with Clerk authentication.
 * It includes Clerk JWT authentication, error handling, and request/response types.
 */

import { UserPreferences } from './types/onboarding-types';

// API Base Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  VERSION: 'v1',
  TIMEOUT: 10000,
} as const;

// Clerk Authentication Types
export interface ClerkAuthContext {
  getToken: () => Promise<string | null>;
  isSignedIn: boolean;
  userId?: string;
}

export interface ClerkUser {
  id: string;
  emailAddress: string;
  firstName?: string;
  lastName?: string;
  imageUrl?: string;
  createdAt: number;
  updatedAt: number;
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
  clerkUserId: string;
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
  clerkUserId: string;
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

// HTTP Client Class
export class ApiClient {
  private baseUrl: string;
  private clerkAuth: ClerkAuthContext | null = null;

  constructor(baseUrl = API_CONFIG.BASE_URL) {
    this.baseUrl = `${baseUrl}/api/${API_CONFIG.VERSION}`;
  }

  // Clerk Authentication Methods
  setClerkAuth(auth: ClerkAuthContext): void {
    this.clerkAuth = auth;
  }

  getClerkAuth(): ClerkAuthContext | null {
    return this.clerkAuth;
  }

  private async getAuthToken(): Promise<string | null> {
    if (!this.clerkAuth || !this.clerkAuth.isSignedIn) {
      return null;
    }

    try {
      return await this.clerkAuth.getToken();
    } catch (error) {
      console.error('Failed to get Clerk token:', error);
      return null;
    }
  }

  // Core HTTP Methods
  private async request<T>(
    endpoint: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
      body?: any;
      params?: Record<string, string | number | boolean>;
      skipAuth?: boolean;
      timeout?: number;
    } = {}
  ): Promise<T> {
    const {
      method = 'GET',
      body,
      params,
      skipAuth = false,
      timeout = API_CONFIG.TIMEOUT,
    } = options;

    // Build URL with query parameters
    const url = new URL(`${this.baseUrl}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    // Build headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add Clerk authentication if not skipped and user is signed in
    if (!skipAuth && this.clerkAuth?.isSignedIn) {
      try {
        const token = await this.getAuthToken();
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
      } catch (error) {
        console.error('Failed to set authorization header:', error);
        throw new Error('Authentication failed');
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

        throw new ApiClientError(errorData, response.status);
      }

      const result: ApiResponse<T> = await response.json();
      return result.data;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiClientError) {
        throw error;
      }

      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiClientError({
          code: 'TIMEOUT',
          message: `Request timed out after ${timeout}ms`,
          timestamp: new Date().toISOString(),
        }, 408);
      }

      throw new ApiClientError({
        code: 'NETWORK_ERROR',
        message: error instanceof Error ? error.message : 'Network request failed',
        timestamp: new Date().toISOString(),
      }, 0);
    }
  }

  // User API Methods
  async getCurrentUser(): Promise<UserProfile> {
    return this.request<UserProfile>('/users/me');
  }

  async createUser(userData: CreateUserRequest): Promise<UserProfile> {
    return this.request<UserProfile>('/users', {
      method: 'POST',
      body: userData,
    });
  }

  async updateUserPreferences(preferences: UpdateUserPreferencesRequest): Promise<UserProfile> {
    return this.request<UserProfile>('/users/me/preferences', {
      method: 'PATCH',
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

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request<{ status: string; timestamp: string }>('/health', {
      skipAuth: true,
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

// Clerk-integrated API client hook
export const useClerkApiClient = () => {
  // This will be used in React components to set up the API client with Clerk auth
  return apiClient;
};

// Hook for React Query integration with Clerk authentication
export const createApiQueryClient = (clerkAuth?: ClerkAuthContext) => {
  // Set Clerk auth if provided
  if (clerkAuth) {
    apiClient.setClerkAuth(clerkAuth);
  }

  return {
    // User queries
    getCurrentUser: () => ({
      queryKey: ['user', 'current'],
      queryFn: () => apiClient.getCurrentUser(),
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: clerkAuth?.isSignedIn ?? false,
    }),

    // Home dashboard queries
    getHomeData: () => ({
      queryKey: ['home', 'data'],
      queryFn: () => apiClient.getHomeData(),
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: clerkAuth?.isSignedIn ?? false,
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
      queryFn: () => apiClient.getTeamDashboard(teamId),
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: (clerkAuth?.isSignedIn ?? false) && !!teamId,
    }),
  };
};

export default apiClient;