/**
 * API Client for Corner League Media Backend Integration
 *
 * This module provides a typed interface for FastAPI backend integration with Firebase authentication.
 * It includes Firebase JWT authentication, error handling, and request/response types.
 */

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

// Team Search API Types
export interface TeamSearchParams {
  query?: string;        // Search team name or market
  sport_id?: string;     // UUID filter by sport
  league_id?: string;    // UUID filter by league
  market?: string;       // Filter by market/city
  is_active?: boolean;   // Filter by active status (default: true)
  page?: number;         // Page number (default: 1)
  page_size?: number;    // Items per page (1-100, default: 20)
}

// Enhanced Team Search Types
export interface SearchMatchInfo {
  field: string;
  value: string;
  highlighted: string;
}

export interface EnhancedTeam extends Team {
  search_matches: SearchMatchInfo[];
  relevance_score: number;
}

export interface EnhancedTeamSearchResponse {
  items: EnhancedTeam[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
  search_metadata: {
    query?: string;
    total_matches: number;
    response_time_ms: number;
    filters_applied: Record<string, any>;
    timestamp: string;
  };
}

export interface SearchSuggestion {
  suggestion: string;
  type: 'team_name' | 'market' | 'league' | 'sport';
  team_count: number;
  preview_teams: string[];
}

export interface SearchSuggestionsResponse {
  query: string;
  suggestions: SearchSuggestion[];
  response_time_ms: number;
}

export interface Team {
  id: string;
  sport_id: string;
  league_id: string;
  name: string;           // "Lakers"
  market: string;         // "Los Angeles"
  slug: string;           // "los-angeles-lakers"
  abbreviation: string;   // "LAL"
  logo_url?: string;
  primary_color?: string; // "#552583"
  secondary_color?: string; // "#FDB927"
  is_active: boolean;
  sport_name: string;     // "Basketball"
  league_name: string;    // "NBA"
  display_name: string;   // "Los Angeles Lakers"
  short_name: string;     // "LAL"
}

export interface TeamSearchResponse {
  items: Team[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

// Onboarding API Types
export interface OnboardingSport {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  icon_url?: string;
  description?: string;
  popularity_rank: number;   // Lower = more popular
  is_active: boolean;
  display_order: number;
  has_teams: boolean;
}

export interface OnboardingTeam {
  id: string;
  sport_id: string;
  league_id: string;
  name: string;
  market: string;
  display_name: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  sport_name: string;
  league_name: string;
  abbreviation: string;
  is_active: boolean;
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

  constructor(baseUrl = API_CONFIG.BASE_URL) {
    this.baseUrl = `${baseUrl}/api/${API_CONFIG.VERSION}`;
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

    // Add Firebase authentication if not skipped and user is signed in
    if (!skipAuth && this.firebaseAuth?.isAuthenticated) {
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

  // Team Search API Methods
  async searchTeams(params?: TeamSearchParams): Promise<TeamSearchResponse> {
    return this.request<TeamSearchResponse>('/teams/search', {
      params: params as Record<string, string | number | boolean>,
      skipAuth: true, // Team search is public
    });
  }

  // Enhanced Team Search API Methods
  async searchTeamsEnhanced(params?: TeamSearchParams): Promise<EnhancedTeamSearchResponse> {
    return this.request<EnhancedTeamSearchResponse>('/teams/search-enhanced', {
      params: params as Record<string, string | number | boolean>,
      skipAuth: true, // Team search is public
    });
  }

  async getSearchSuggestions(query: string): Promise<SearchSuggestionsResponse> {
    return this.request<SearchSuggestionsResponse>('/teams/search-suggestions', {
      params: { query },
      skipAuth: true, // Search suggestions are public
    });
  }

  // Onboarding API Methods
  async getOnboardingStatus(): Promise<OnboardingStatus> {
    try {
      return this.request<OnboardingStatus>('/onboarding/status');
    } catch (error) {
      // If authentication fails, try the new user fallback endpoint
      if (error instanceof ApiClientError && (error.statusCode === 401 || error.statusCode === 403)) {
        console.warn('Authentication failed for onboarding status, using new user fallback');
        const fallbackResponse = await this.request<OnboardingStatus>('/onboarding/status/new-user', {
          skipAuth: true
        });

        // Transform the response to match the expected OnboardingStatus interface
        return {
          currentStep: fallbackResponse.current_step || 1,
          totalSteps: 5,
          isComplete: fallbackResponse.is_onboarded || false,
          selectedSports: [],
          selectedTeams: [],
          preferences: {
            newsTypes: [
              { type: 'injuries', enabled: true, priority: 1 },
              { type: 'trades', enabled: true, priority: 2 },
              { type: 'roster', enabled: true, priority: 3 },
              { type: 'general', enabled: true, priority: 4 }
            ],
            notifications: {
              push: true,
              email: false,
              gameReminders: true,
              newsAlerts: true,
              scoreUpdates: true
            },
            contentFrequency: 'standard'
          }
        };
      }
      throw error; // Re-throw if it's not an auth error
    }
  }

  async updateOnboardingStep(data: UpdateOnboardingStepRequest): Promise<OnboardingStatus> {
    return this.request<OnboardingStatus>('/onboarding/step', {
      method: 'PUT',
      body: data,
    });
  }

  async getOnboardingSports(): Promise<OnboardingSport[]> {
    return this.request<OnboardingSport[]>('/onboarding/sports', {
      skipAuth: true, // Onboarding sports are public
    });
  }

  async getOnboardingTeams(sportIds: string[]): Promise<OnboardingTeam[]> {
    return this.request<OnboardingTeam[]>('/onboarding/teams', {
      params: { sport_ids: sportIds.join(',') },
      skipAuth: true, // Onboarding teams are public
    });
  }

  async completeOnboarding(data: CompleteOnboardingRequest): Promise<UserProfile> {
    return this.request<UserProfile>('/onboarding/complete', {
      method: 'POST',
      body: data,
    });
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
      queryFn: () => apiClient.getCurrentUser(),
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: firebaseAuth?.isAuthenticated ?? false,
    }),

    // Home dashboard queries
    getHomeData: () => ({
      queryKey: ['home', 'data'],
      queryFn: () => apiClient.getHomeData(),
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
      queryFn: () => apiClient.getTeamDashboard(teamId),
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: (firebaseAuth?.isAuthenticated ?? false) && !!teamId,
    }),

    // Onboarding queries
    getOnboardingStatus: () => ({
      queryKey: ['onboarding', 'status'],
      queryFn: async () => {
        try {
          return await apiClient.getOnboardingStatus();
        } catch (error) {
          // If we get a 401 or 403, use the fallback endpoint directly
          if (error instanceof ApiClientError && (error.statusCode === 401 || error.statusCode === 403)) {
            console.warn('Authentication failed for onboarding status, using new user fallback');
            try {
              const fallbackResponse = await apiClient.request<{
                is_onboarded: boolean;
                current_step: number;
                onboarding_completed_at: string | null;
              }>('/onboarding/status/new-user', {
                skipAuth: true
              });
              // Transform backend response to frontend format
              return {
                currentStep: fallbackResponse.current_step || 1,
                totalSteps: 5,
                isComplete: fallbackResponse.is_onboarded || false,
                selectedSports: [],
                selectedTeams: [],
                preferences: {
                  newsTypes: [
                    { type: 'injuries', enabled: true, priority: 1 },
                    { type: 'trades', enabled: true, priority: 2 },
                    { type: 'roster', enabled: true, priority: 3 },
                    { type: 'general', enabled: true, priority: 4 }
                  ],
                  notifications: {
                    push: true,
                    email: false,
                    gameReminders: true,
                    newsAlerts: true,
                    scoreUpdates: true
                  },
                  contentFrequency: 'standard' as const
                }
              };
            } catch (fallbackError) {
              console.error('Fallback endpoint also failed:', fallbackError);
              // Return default new user status if both endpoints fail
              return {
                currentStep: 1,
                totalSteps: 5,
                isComplete: false,
                selectedSports: [],
                selectedTeams: [],
                preferences: {
                  newsTypes: [
                    { type: 'injuries', enabled: true, priority: 1 },
                    { type: 'trades', enabled: true, priority: 2 },
                    { type: 'roster', enabled: true, priority: 3 },
                    { type: 'general', enabled: true, priority: 4 }
                  ],
                  notifications: {
                    push: true,
                    email: false,
                    gameReminders: true,
                    newsAlerts: true,
                    scoreUpdates: true
                  },
                  contentFrequency: 'standard' as const
                }
              };
            }
          }
          throw error;
        }
      },
      staleTime: 1 * 60 * 1000, // 1 minute
      retry: false, // Disable React Query retries - let our custom logic handle fallbacks
      enabled: true, // Always enabled - fallback logic handles unauthenticated users
    }),

    getOnboardingSports: () => ({
      queryKey: ['onboarding', 'sports'],
      queryFn: () => apiClient.getOnboardingSports(),
      staleTime: 30 * 60 * 1000, // 30 minutes (static data)
    }),

    getOnboardingTeams: (sportIds: string[]) => ({
      queryKey: ['onboarding', 'teams', sportIds],
      queryFn: () => apiClient.getOnboardingTeams(sportIds),
      staleTime: 30 * 60 * 1000, // 30 minutes (static data)
      enabled: sportIds.length > 0,
    }),

    // Team search queries
    searchTeams: (params?: TeamSearchParams) => ({
      queryKey: ['teams', 'search', params],
      queryFn: () => apiClient.searchTeams(params),
      staleTime: 15 * 60 * 1000, // 15 minutes
      enabled: false, // Enable manually for search
    }),

    // Enhanced team search queries
    searchTeamsEnhanced: (params?: TeamSearchParams) => ({
      queryKey: ['teams', 'search-enhanced', params],
      queryFn: () => apiClient.searchTeamsEnhanced(params),
      staleTime: 5 * 60 * 1000, // 5 minutes
      enabled: false, // Enable manually for search
    }),

    getSearchSuggestions: (query: string) => ({
      queryKey: ['teams', 'search-suggestions', query],
      queryFn: () => apiClient.getSearchSuggestions(query),
      staleTime: 10 * 60 * 1000, // 10 minutes
      enabled: query.length >= 2, // Only enable for meaningful queries
    }),
  };
};

export default apiClient;