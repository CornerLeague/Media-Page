/**
 * TypeScript type definitions for Corner League Media backend API
 * Generated from OpenAPI specification
 *
 * These types provide type safety for frontend-backend communication
 * and are compatible with the existing frontend API client.
 */

// ===== COMMON TYPES =====

export interface APIResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

// ===== ENUMS =====

export type ContentFrequency = 'minimal' | 'standard' | 'comprehensive';

export type NewsType = 'injuries' | 'trades' | 'roster' | 'general' | 'scores' | 'analysis';

export type ContentCategory = 'injuries' | 'trades' | 'roster' | 'general' | 'scores' | 'analysis';

export type GameStatus = 'SCHEDULED' | 'LIVE' | 'FINAL' | 'POSTPONED' | 'CANCELLED';

export type GameResult = 'W' | 'L' | 'T';

export type ExperienceType = 'watch_party' | 'tailgate' | 'viewing' | 'meetup';

export type IngestionStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'duplicate';

export type InteractionType =
  | 'article_view'
  | 'article_share'
  | 'team_follow'
  | 'team_unfollow'
  | 'game_view'
  | 'experience_register'
  | 'ticket_view'
  | 'search'
  | 'feed_scroll';

export type EntityType =
  | 'article'
  | 'team'
  | 'game'
  | 'player'
  | 'experience'
  | 'ticket_deal'
  | 'ai_summary';

// ===== BASE INTERFACES =====

export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface TimestampEntity {
  created_at: string;
  updated_at: string;
}

// ===== SPORTS ENTITIES =====

export interface Sport extends BaseEntity {
  name: string;
  slug: string;
  has_teams: boolean;
  icon?: string;
  is_active: boolean;
  display_order: number;
}

export interface League extends BaseEntity {
  sport_id: string;
  name: string;
  slug: string;
  abbreviation?: string;
  is_active: boolean;
  season_start_month?: number;
  season_end_month?: number;
  sport?: Sport;
}

export interface Team extends BaseEntity {
  sport_id: string;
  league_id: string;
  name: string;
  market: string;
  slug: string;
  abbreviation?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  is_active: boolean;
  external_id?: string;
  sport?: Sport;
  league?: League;
}

// ===== USER & AUTHENTICATION =====

export interface ClerkUser {
  id: string;
  email_address: string;
  first_name?: string;
  last_name?: string;
  image_url?: string;
  created_at: number;
  updated_at: number;
}

export interface UserSportPreference extends BaseEntity {
  user_id: string;
  sport_id: string;
  rank: number;
  is_active: boolean;
  sport?: Sport;
}

export interface UserTeamPreference extends BaseEntity {
  user_id: string;
  team_id: string;
  affinity_score: number;
  is_active: boolean;
  team?: Team;
}

export interface UserNewsPreference extends BaseEntity {
  user_id: string;
  news_type: NewsType;
  enabled: boolean;
  priority: number;
}

export interface UserNotificationSettings extends BaseEntity {
  user_id: string;
  push_enabled: boolean;
  email_enabled: boolean;
  game_reminders: boolean;
  news_alerts: boolean;
  score_updates: boolean;
}

export interface UserProfile extends BaseEntity {
  clerk_user_id: string;
  email?: string;
  display_name?: string;
  avatar_url?: string;
  content_frequency: ContentFrequency;
  is_active: boolean;
  onboarding_completed_at?: string;
  last_active_at: string;
  sport_preferences: UserSportPreference[];
  team_preferences: UserTeamPreference[];
  news_preferences: UserNewsPreference[];
  notification_settings?: UserNotificationSettings;
}

// ===== USER REQUESTS =====

export interface UserCreateRequest {
  clerk_user_id: string;
  display_name?: string;
  email?: string;
  sports: Array<{
    sport_id: string;
    name: string;
    rank: number;
    has_teams: boolean;
  }>;
  teams: Array<{
    team_id: string;
    name: string;
    sport_id: string;
    league: string;
    affinity_score: number;
  }>;
  preferences: {
    news_types: Array<{
      type: NewsType;
      enabled: boolean;
      priority: number;
    }>;
    notifications: {
      push: boolean;
      email: boolean;
      game_reminders: boolean;
      news_alerts: boolean;
      score_updates: boolean;
    };
    content_frequency: ContentFrequency;
  };
}

export interface UserUpdateRequest {
  display_name?: string;
  content_frequency?: ContentFrequency;
  avatar_url?: string;
}

export interface PreferencesUpdateRequest {
  sports?: Array<{
    sport_id: string;
    rank: number;
  }>;
  teams?: Array<{
    team_id: string;
    affinity_score: number;
  }>;
  preferences?: {
    news_types?: Array<{
      type: NewsType;
      enabled: boolean;
      priority: number;
    }>;
    notifications?: {
      push_enabled?: boolean;
      email_enabled?: boolean;
      game_reminders?: boolean;
      news_alerts?: boolean;
      score_updates?: boolean;
    };
    content_frequency?: ContentFrequency;
  };
}

// ===== GAMES & SCORES =====

export interface Game extends BaseEntity {
  sport_id: string;
  league_id: string;
  home_team_id: string;
  away_team_id: string;
  scheduled_at: string;
  status: GameStatus;
  period?: string;
  time_remaining?: string;
  home_score: number;
  away_score: number;
  external_id?: string;
  venue?: string;
  season?: number;
  week?: number;
  home_team?: Team;
  away_team?: Team;
  sport?: Sport;
  league?: League;
}

export interface GameEvent extends BaseEntity {
  game_id: string;
  event_type: string;
  event_time?: string;
  description: string;
  team_id?: string;
  player_name?: string;
  points_value: number;
  game?: Game;
  team?: Team;
}

export interface RecentResult {
  game_id: string;
  result: GameResult;
  diff: number;
  date: string;
  opponent?: string;
}

// ===== CONTENT =====

export interface FeedSource extends BaseEntity {
  name: string;
  url: string;
  website?: string;
  description?: string;
  is_active: boolean;
  fetch_interval_minutes: number;
  last_fetched_at?: string;
  last_success_at?: string;
  failure_count: number;
}

export interface FeedSnapshot extends BaseEntity {
  feed_source_id: string;
  url_hash: string;
  content_hash: string;
  minhash_signature?: string;
  raw_content: Record<string, any>;
  processed_at?: string;
  status: IngestionStatus;
  error_message?: string;
}

export interface ArticleSport {
  sport: Sport;
  relevance_score: number;
}

export interface ArticleTeam {
  team: Team;
  relevance_score: number;
  mentioned_players: string[];
}

export interface Article extends BaseEntity {
  feed_snapshot_id?: string;
  title: string;
  summary?: string;
  content?: string;
  author?: string;
  source: string;
  category: ContentCategory;
  priority: number;
  published_at: string;
  url?: string;
  image_url?: string;
  external_id?: string;
  word_count?: number;
  reading_time_minutes?: number;
  sentiment_score?: number;
  is_active: boolean;
  sports: ArticleSport[];
  teams: ArticleTeam[];
}

export interface AISummary extends BaseEntity {
  user_id?: string;
  team_id?: string;
  sport_id?: string;
  summary_text: string;
  summary_type: string;
  source_article_ids: string[];
  confidence_score?: number;
  generated_at: string;
  expires_at?: string;
  is_active: boolean;
}

// ===== PLAYERS =====

export interface Player extends BaseEntity {
  team_id: string;
  name: string;
  jersey_number?: number;
  position?: string;
  experience_years?: number;
  height?: string;
  weight?: number;
  is_active: boolean;
  external_id?: string;
  team?: Team;
}

export interface DepthChartEntry extends BaseEntity {
  team_id: string;
  player_id: string;
  position: string;
  depth_order: number;
  week?: number;
  season?: number;
  is_active: boolean;
  team?: Team;
  player?: Player;
}

// ===== TICKETS =====

export interface TicketProvider extends BaseEntity {
  name: string;
  website?: string;
  api_endpoint?: string;
  is_active: boolean;
}

export interface TicketDeal extends BaseEntity {
  provider_id: string;
  game_id?: string;
  team_id?: string;
  section: string;
  price: number;
  quantity?: number;
  deal_score: number;
  external_url?: string;
  external_id?: string;
  valid_until?: string;
  is_active: boolean;
  provider?: TicketProvider;
  game?: Game;
  team?: Team;
}

// ===== EXPERIENCES =====

export interface FanExperience extends BaseEntity {
  team_id?: string;
  game_id?: string;
  sport_id?: string;
  title: string;
  description?: string;
  experience_type: ExperienceType;
  start_time: string;
  end_time?: string;
  location?: string;
  organizer?: string;
  max_attendees?: number;
  current_attendees: number;
  price?: number;
  external_url?: string;
  is_active: boolean;
  team?: Team;
  game?: Game;
  sport?: Sport;
}

export interface UserExperienceRegistration extends BaseEntity {
  user_id: string;
  experience_id: string;
  registered_at: string;
  status: string;
  user?: UserProfile;
  experience?: FanExperience;
}

// ===== ANALYTICS =====

export interface UserInteraction extends BaseEntity {
  user_id: string;
  interaction_type: InteractionType;
  entity_type: EntityType;
  entity_id: string;
  metadata: Record<string, any>;
}

export interface ContentPerformance extends BaseEntity {
  content_type: EntityType;
  content_id: string;
  metric_name: string;
  metric_value: number;
  date_recorded: string;
}

// ===== DASHBOARD & AGGREGATED DATA =====

export interface TeamDashboard {
  team: Team;
  latest_score?: Game;
  recent_results: RecentResult[];
  summary: AISummary;
  news: Article[];
  depth_chart: DepthChartEntry[];
  ticket_deals: TicketDeal[];
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

// ===== API REQUEST PARAMETERS =====

export interface SportsSearchParams {
  is_active?: boolean;
}

export interface LeaguesSearchParams {
  sport_id?: string;
  is_active?: boolean;
}

export interface TeamsSearchParams {
  league_id?: string;
  sport_id?: string;
  is_active?: boolean;
}

export interface ArticlesSearchParams {
  page?: number;
  page_size?: number;
  category?: ContentCategory;
  team_id?: string;
  sport_id?: string;
  search?: string;
}

export interface GamesSearchParams {
  date?: string;
  team_id?: string;
  status?: GameStatus;
  sport_id?: string;
  league_id?: string;
}

export interface PersonalizedContentParams {
  limit?: number;
}

// ===== FRONTEND-COMPATIBLE TYPES =====
// These maintain compatibility with existing frontend types

export interface SportsFeedItem extends Article {
  // Legacy alias for compatibility
  teams: string[];
  sports: string[];
}

export interface GameScore extends Game {
  // Simplified format for display
  gameId: string;
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
}

export interface NewsArticle {
  id: string;
  title: string;
  category: ContentCategory;
  published_at: string;
  summary?: string;
  url?: string;
}

// ===== TYPE UTILITIES =====

export type CreateRequest<T> = Omit<T, 'id' | 'created_at' | 'updated_at'>;
export type UpdateRequest<T> = Partial<Omit<T, 'id' | 'created_at' | 'updated_at'>>;

// API Client Error Types
export class APIClientError extends Error {
  public readonly apiError: ErrorResponse;
  public readonly statusCode: number;

  constructor(apiError: ErrorResponse, statusCode: number) {
    super(apiError.message);
    this.name = 'APIClientError';
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

// ===== WEBSOCKET TYPES =====

export interface WebSocketMessage<T = any> {
  type: string;
  data: T;
  timestamp: string;
}

export interface GameUpdateMessage extends WebSocketMessage<Game> {
  type: 'game_update';
}

export interface NewsAlertMessage extends WebSocketMessage<Article> {
  type: 'news_alert';
}

export interface ScoreUpdateMessage extends WebSocketMessage<GameEvent> {
  type: 'score_update';
}

export type WSMessage = GameUpdateMessage | NewsAlertMessage | ScoreUpdateMessage;

// ===== FORM VALIDATION TYPES =====

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface FormErrors {
  [key: string]: string | string[];
}

// ===== EXPORT ALL TYPES =====

export type {
  // Re-export existing frontend types for backward compatibility
  UserPreferences,
  SportPreference,
  TeamPreference,
  UserSettings,
  NotificationSettings,
  Sport as LegacySport,
  League as LegacyLeague,
  Team as LegacyTeam,
  OnboardingStep,
  OnboardingState,
  OnboardingAction,
} from './onboarding-types';

// Default exports for commonly used types
export default {
  APIResponse,
  ErrorResponse,
  PaginatedResponse,
  UserProfile,
  Article,
  Game,
  Team,
  Sport,
  League,
  TeamDashboard,
  HomeData,
};