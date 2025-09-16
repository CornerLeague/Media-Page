/**
 * TypeScript types generated from SQLAlchemy models
 * Generated on: 2025-09-15T19:01:55.593413
 *
 * This file is auto-generated. Do not edit manually.
 * To regenerate, run: python app/database/utils/generate_types.py
 */

// ===== ENUMS =====


export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
  MODERATOR = 'moderator',
}

export type UserRoleType = 'user' | 'admin' | 'moderator';

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
}

export type UserStatusType = 'active' | 'inactive' | 'suspended';

export enum TeamStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ARCHIVED = 'archived',
}

export type TeamStatusType = 'active' | 'inactive' | 'archived';

export enum Sport {
  NFL = 'nfl',
  NBA = 'nba',
  MLB = 'mlb',
  NHL = 'nhl',
  MLS = 'mls',
  COLLEGE_FOOTBALL = 'college_football',
  COLLEGE_BASKETBALL = 'college_basketball',
}

export type SportType = 'nfl' | 'nba' | 'mlb' | 'nhl' | 'mls' | 'college_football' | 'college_basketball';

export enum League {
  NFL = 'NFL',
  NBA = 'NBA',
  MLB = 'MLB',
  NHL = 'NHL',
  MLS = 'MLS',
  NCAA_FB = 'NCAA_FB',
  NCAA_BB = 'NCAA_BB',
}

export type LeagueType = 'NFL' | 'NBA' | 'MLB' | 'NHL' | 'MLS' | 'NCAA_FB' | 'NCAA_BB';

export enum ArticleStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
  DELETED = 'deleted',
}

export type ArticleStatusType = 'draft' | 'published' | 'archived' | 'deleted';

export enum ContentCategory {
  NEWS = 'news',
  ANALYSIS = 'analysis',
  OPINION = 'opinion',
  RUMORS = 'rumors',
  INJURY_REPORT = 'injury_report',
  TRADE = 'trade',
  DRAFT = 'draft',
  GAME_RECAP = 'game_recap',
}

export type ContentCategoryType = 'news' | 'analysis' | 'opinion' | 'rumors' | 'injury_report' | 'trade' | 'draft' | 'game_recap';

export enum GameStatus {
  SCHEDULED = 'scheduled',
  LIVE = 'live',
  COMPLETED = 'completed',
  POSTPONED = 'postponed',
  CANCELLED = 'cancelled',
}

export type GameStatusType = 'scheduled' | 'live' | 'completed' | 'postponed' | 'cancelled';

export enum IngestionStatus {
  SUCCESS = 'success',
  DUPLICATE = 'duplicate',
  ERROR = 'error',
  SKIP = 'skip',
}

export type IngestionStatusType = 'success' | 'duplicate' | 'error' | 'skip';

export enum ArticleClassificationCategory {
  INJURY = 'injury',
  ROSTER = 'roster',
  TRADE = 'trade',
  GENERAL = 'general',
  DEPTH_CHART = 'depth_chart',
  GAME_RECAP = 'game_recap',
  ANALYSIS = 'analysis',
  RUMORS = 'rumors',
}

export type ArticleClassificationCategoryType = 'injury' | 'roster' | 'trade' | 'general' | 'depth_chart' | 'game_recap' | 'analysis' | 'rumors';

export enum AgentType {
  SCORES = 'scores',
  NEWS = 'news',
  DEPTH_CHART = 'depth_chart',
  TICKETS = 'tickets',
  EXPERIENCES = 'experiences',
  PLANNER = 'planner',
  CONTENT_CLASSIFICATION = 'content_classification',
}

export type AgentTypeType = 'scores' | 'news' | 'depth_chart' | 'tickets' | 'experiences' | 'planner' | 'content_classification';

export enum RunStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export type RunStatusType = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export enum JobType {
  SCRAPE_NEWS = 'scrape_news',
  SCRAPE_SCORES = 'scrape_scores',
  SCRAPE_DEPTH_CHART = 'scrape_depth_chart',
  SCRAPE_TICKETS = 'scrape_tickets',
  SCRAPE_EXPERIENCES = 'scrape_experiences',
  CLASSIFY_CONTENT = 'classify_content',
}

export type JobTypeType = 'scrape_news' | 'scrape_scores' | 'scrape_depth_chart' | 'scrape_tickets' | 'scrape_experiences' | 'classify_content';

export enum ExperienceType {
  WATCH_PARTY = 'watch_party',
  MEETUP = 'meetup',
  BAR_EVENT = 'bar_event',
  COMMUNITY_EVENT = 'community_event',
  FAN_FEST = 'fan_fest',
  TAILGATE = 'tailgate',
}

export type ExperienceTypeType = 'watch_party' | 'meetup' | 'bar_event' | 'community_event' | 'fan_fest' | 'tailgate';

export enum SeatQuality {
  PREMIUM = 'premium',
  GOOD = 'good',
  AVERAGE = 'average',
  POOR = 'poor',
}

export type SeatQualityType = 'premium' | 'good' | 'average' | 'poor';


// ===== DATABASE MODELS =====

/**
 * User database model
 * Table: users
 */
export interface User {
  /** Clerk user ID for authentication */
  clerk_user_id: string;
  /** User email address */
  email: string;
  /** Unique username */
  username?: string;
  /** User first name */
  first_name?: string;
  /** User last name */
  last_name?: string;
  /** Profile image URL */
  image_url?: string;
  /** User role */
  role?: string;
  /** User account status */
  status?: string;
  /** User preferences as JSON */
  preferences?: Record<string, any>;
  /** Last login timestamp */
  last_login?: string;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * User creation payload (excludes auto-generated fields)
 */
export interface CreateUser extends Omit<User, 'id' | 'created_at' | 'updated_at'> {}

/**
 * User update payload (all fields optional except id)
 */
export interface UpdateUser extends Partial<Omit<User, 'id'>> {
  id: string;
}


/**
 * UserTeam database model
 * Table: user_teams
 */
export interface UserTeam {
  /** User ID */
  user_id: string;
  /** Team ID */
  team_id: string;
  /** When user started following team */
  followed_at: string;
  /** Whether notifications are enabled for this team */
  notifications_enabled?: boolean;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * UserTeam creation payload (excludes auto-generated fields)
 */
export interface CreateUserTeam extends Omit<UserTeam, 'id' | 'created_at' | 'updated_at'> {}

/**
 * UserTeam update payload (all fields optional except id)
 */
export interface UpdateUserTeam extends Partial<Omit<UserTeam, 'id'>> {
  id: string;
}


/**
 * UserPreferenceHistory database model
 * Table: user_preference_history
 */
export interface UserPreferenceHistory {
  /** User ID */
  user_id: string;
  /** Previous preferences */
  old_preferences?: Record<string, any>;
  /** New preferences */
  new_preferences: Record<string, any>;
  /** List of changed preference fields */
  changed_fields: any[];
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * UserPreferenceHistory creation payload (excludes auto-generated fields)
 */
export interface CreateUserPreferenceHistory extends Omit<UserPreferenceHistory, 'id' | 'created_at' | 'updated_at'> {}

/**
 * UserPreferenceHistory update payload (all fields optional except id)
 */
export interface UpdateUserPreferenceHistory extends Partial<Omit<UserPreferenceHistory, 'id'>> {
  id: string;
}


/**
 * Team database model
 * Table: teams
 */
export interface Team {
  /** External API team ID */
  external_id?: string;
  /** Team name */
  name: string;
  /** Team city */
  city?: string;
  /** Team abbreviation (e.g., NYY, LAL) */
  abbreviation: string;
  /** Sport type */
  sport: string;
  /** League */
  league: string;
  /** Conference (e.g., AFC, NFC, Eastern, Western) */
  conference?: string;
  /** Division (e.g., East, West, North, South) */
  division?: string;
  /** Team logo URL */
  logo_url?: string;
  /** Primary team color (hex code) */
  primary_color?: string;
  /** Secondary team color (hex code) */
  secondary_color?: string;
  /** Team status */
  status?: string;
  /** Number of users following this team */
  follower_count?: number;
  /** Full-text search vector (computed) */
  search_vector?: any;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * Team creation payload (excludes auto-generated fields)
 */
export interface CreateTeam extends Omit<Team, 'id' | 'created_at' | 'updated_at'> {}

/**
 * Team update payload (all fields optional except id)
 */
export interface UpdateTeam extends Partial<Omit<Team, 'id'>> {
  id: string;
}


/**
 * TeamStats database model
 * Table: team_stats
 */
export interface TeamStats {
  /** Team ID */
  team_id: string;
  /** Season identifier (e.g., '2024', '2023-24') */
  season: string;
  /** Number of games played */
  games_played?: number;
  /** Number of wins */
  wins?: number;
  /** Number of losses */
  losses?: number;
  /** Number of ties (if applicable) */
  ties?: number;
  /** Total points scored */
  points_for?: number;
  /** Total points allowed */
  points_against?: number;
  /** Win percentage (computed) */
  win_percentage?: number;
  /** Additional sport-specific statistics */
  extended_stats?: Record<string, any>;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * TeamStats creation payload (excludes auto-generated fields)
 */
export interface CreateTeamStats extends Omit<TeamStats, 'id' | 'created_at' | 'updated_at'> {}

/**
 * TeamStats update payload (all fields optional except id)
 */
export interface UpdateTeamStats extends Partial<Omit<TeamStats, 'id'>> {
  id: string;
}


/**
 * Article database model
 * Table: articles
 */
export interface Article {
  /** Primary deduplication key (hash of source URL) */
  url_hash: string;
  /** Article title */
  title: string;
  /** Full article content */
  content?: string;
  /** Article summary or excerpt */
  summary?: string;
  /** Article author */
  author?: string;
  /** Name of the content source */
  source_name: string;
  /** Original article URL */
  source_url: string;
  /** Original publication timestamp */
  published_at?: string;
  /** Content category */
  category?: string;
  /** Content tags */
  tags?: any[];
  /** Sentiment score (-1.0 to 1.0) */
  sentiment_score?: number;
  /** Readability score (0-100) */
  readability_score?: number;
  /** Related team IDs */
  team_ids?: any[];
  /** AI-generated summary */
  ai_summary?: string;
  /** AI-generated tags */
  ai_tags?: any[];
  /** AI-predicted category */
  ai_category?: string;
  /** AI prediction confidence (0.0 to 1.0) */
  ai_confidence?: number;
  /** Number of views */
  view_count?: number;
  /** Number of shares */
  share_count?: number;
  /** Number of likes */
  like_count?: number;
  /** Article status */
  status?: string;
  /** Full-text search vector (computed) */
  search_vector?: any;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * Article creation payload (excludes auto-generated fields)
 */
export interface CreateArticle extends Omit<Article, 'id' | 'created_at' | 'updated_at'> {}

/**
 * Article update payload (all fields optional except id)
 */
export interface UpdateArticle extends Partial<Omit<Article, 'id'>> {
  id: string;
}


/**
 * ArticleClassification database model
 * Table: article_classification
 */
export interface ArticleClassification {
  id: string;
  article_id: string;
  category: string;
  confidence: number;
  rationale_json?: Record<string, any>;
  model_version?: string;
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * ArticleClassification creation payload (excludes auto-generated fields)
 */
export interface CreateArticleClassification extends Omit<ArticleClassification, 'id' | 'created_at' | 'updated_at'> {}

/**
 * ArticleClassification update payload (all fields optional except id)
 */
export interface UpdateArticleClassification extends Partial<Omit<ArticleClassification, 'id'>> {
  id: string;
}


/**
 * ArticleEntity database model
 * Table: article_entities
 */
export interface ArticleEntity {
  id: string;
  article_id: string;
  entity_type: string;
  value: string;
  confidence?: number;
  start_pos?: number;
  end_pos?: number;
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * ArticleEntity creation payload (excludes auto-generated fields)
 */
export interface CreateArticleEntity extends Omit<ArticleEntity, 'id' | 'created_at' | 'updated_at'> {}

/**
 * ArticleEntity update payload (all fields optional except id)
 */
export interface UpdateArticleEntity extends Partial<Omit<ArticleEntity, 'id'>> {
  id: string;
}


/**
 * Game database model
 * Table: games
 */
export interface Game {
  /** External API game ID */
  external_id?: string;
  /** Home team ID */
  home_team_id: string;
  /** Away team ID */
  away_team_id: string;
  /** Scheduled game start time */
  scheduled_at: string;
  /** Game venue/stadium */
  venue?: string;
  /** Season identifier (e.g., '2024', '2023-24') */
  season: string;
  /** Week number (for sports with weeks) */
  week?: number;
  /** Current game status */
  status?: string;
  /** Current quarter/period */
  quarter?: number;
  /** Time remaining in current period */
  time_remaining?: string;
  /** Home team score */
  home_score?: number;
  /** Away team score */
  away_score?: number;
  /** Detailed final score breakdown */
  final_score?: Record<string, any>;
  /** Game statistics and metadata */
  stats?: Record<string, any>;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * Game creation payload (excludes auto-generated fields)
 */
export interface CreateGame extends Omit<Game, 'id' | 'created_at' | 'updated_at'> {}

/**
 * Game update payload (all fields optional except id)
 */
export interface UpdateGame extends Partial<Omit<Game, 'id'>> {
  id: string;
}


/**
 * Score database model
 * Table: score
 */
export interface Score {
  id: string;
  game_id: string;
  team_id: string;
  pts?: number;
  period?: number;
  period_pts?: number;
  is_final?: boolean;
  updated_at: string;
  /** Record creation timestamp */
  created_at: string;
}

/**
 * Score creation payload (excludes auto-generated fields)
 */
export interface CreateScore extends Omit<Score, 'id' | 'created_at' | 'updated_at'> {}

/**
 * Score update payload (all fields optional except id)
 */
export interface UpdateScore extends Partial<Omit<Score, 'id'>> {
  id: string;
}


/**
 * FeedSource database model
 * Table: feed_sources
 */
export interface FeedSource {
  /** Unique feed source name */
  name: string;
  /** Feed URL */
  url: string;
  /** Feed type (rss, json, api, etc.) */
  feed_type: string;
  /** Whether source is actively being processed */
  is_active?: boolean;
  /** Last fetch attempt timestamp */
  last_fetched_at?: string;
  /** Last successful fetch timestamp */
  last_successful_fetch_at?: string;
  /** Fetch interval in minutes */
  fetch_interval_minutes?: number;
  /** Feed-specific configuration */
  config?: Record<string, any>;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * FeedSource creation payload (excludes auto-generated fields)
 */
export interface CreateFeedSource extends Omit<FeedSource, 'id' | 'created_at' | 'updated_at'> {}

/**
 * FeedSource update payload (all fields optional except id)
 */
export interface UpdateFeedSource extends Partial<Omit<FeedSource, 'id'>> {
  id: string;
}


/**
 * IngestionLog database model
 * Table: ingestion_logs
 */
export interface IngestionLog {
  /** Source feed ID */
  source_id?: string;
  /** URL hash for deduplication */
  url_hash: string;
  /** Original content URL */
  source_url: string;
  /** Ingestion attempt result */
  ingestion_status: string;
  /** Error message if ingestion failed */
  error_message?: string;
  /** Original article if this is a duplicate */
  duplicate_of?: string;
  /** Similarity score for near-duplicate detection */
  similarity_score?: number;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * IngestionLog creation payload (excludes auto-generated fields)
 */
export interface CreateIngestionLog extends Omit<IngestionLog, 'id' | 'created_at' | 'updated_at'> {}

/**
 * IngestionLog update payload (all fields optional except id)
 */
export interface UpdateIngestionLog extends Partial<Omit<IngestionLog, 'id'>> {
  id: string;
}


/**
 * SearchAnalytics database model
 * Table: search_analytics
 */
export interface SearchAnalytics {
  /** User who performed the search (null for anonymous) */
  user_id?: string;
  /** Search query text */
  query: string;
  /** Number of results returned */
  results_count: number;
  /** Article IDs that were clicked from results */
  clicked_results?: any[];
  /** Full-text search vector for query analysis (computed) */
  search_vector?: any;
  /** Primary key UUID */
  id?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * SearchAnalytics creation payload (excludes auto-generated fields)
 */
export interface CreateSearchAnalytics extends Omit<SearchAnalytics, 'id' | 'created_at' | 'updated_at'> {}

/**
 * SearchAnalytics update payload (all fields optional except id)
 */
export interface UpdateSearchAnalytics extends Partial<Omit<SearchAnalytics, 'id'>> {
  id: string;
}


/**
 * UserSportPref database model
 * Table: user_sport_prefs
 */
export interface UserSportPref {
  id: string;
  user_id: string;
  sport_id: string;
  rank: number;
  created_at: string;
  updated_at: string;
}

/**
 * UserSportPref creation payload (excludes auto-generated fields)
 */
export interface CreateUserSportPref extends Omit<UserSportPref, 'id' | 'created_at' | 'updated_at'> {}

/**
 * UserSportPref update payload (all fields optional except id)
 */
export interface UpdateUserSportPref extends Partial<Omit<UserSportPref, 'id'>> {
  id: string;
}


/**
 * DepthChart database model
 * Table: depth_chart
 */
export interface DepthChart {
  id: string;
  team_id: string;
  position: string;
  player_name: string;
  player_number?: string;
  depth_order: number;
  source: string;
  source_url?: string;
  captured_at: string;
  season_year?: number;
  week?: number;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * DepthChart creation payload (excludes auto-generated fields)
 */
export interface CreateDepthChart extends Omit<DepthChart, 'id' | 'created_at' | 'updated_at'> {}

/**
 * DepthChart update payload (all fields optional except id)
 */
export interface UpdateDepthChart extends Partial<Omit<DepthChart, 'id'>> {
  id: string;
}


/**
 * TicketDeal database model
 * Table: ticket_deal
 */
export interface TicketDeal {
  id: string;
  game_id: string;
  provider: string;
  section?: string;
  row?: string;
  seat_numbers?: string;
  price: number;
  fees_est?: number;
  total_price?: number;
  seat_quality?: string;
  availability?: number;
  deal_score?: number;
  provider_url?: string;
  captured_at: string;
  expires_at?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * TicketDeal creation payload (excludes auto-generated fields)
 */
export interface CreateTicketDeal extends Omit<TicketDeal, 'id' | 'created_at' | 'updated_at'> {}

/**
 * TicketDeal update payload (all fields optional except id)
 */
export interface UpdateTicketDeal extends Partial<Omit<TicketDeal, 'id'>> {
  id: string;
}


/**
 * Experience database model
 * Table: experience
 */
export interface Experience {
  id: string;
  team_id?: string;
  game_id?: string;
  type: string;
  title: string;
  description?: string;
  url?: string;
  venue?: string;
  address?: string;
  start_time?: string;
  end_time?: string;
  location_geo?: Record<string, any>;
  quality_score?: number;
  price_range?: string;
  capacity?: number;
  captured_at: string;
  source: string;
  source_url?: string;
  /** Record creation timestamp */
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * Experience creation payload (excludes auto-generated fields)
 */
export interface CreateExperience extends Omit<Experience, 'id' | 'created_at' | 'updated_at'> {}

/**
 * Experience update payload (all fields optional except id)
 */
export interface UpdateExperience extends Partial<Omit<Experience, 'id'>> {
  id: string;
}


/**
 * AgentRun database model
 * Table: agent_run
 */
export interface AgentRun {
  id: string;
  agent_type: string;
  subject_key: string;
  status?: string;
  started_at?: string;
  finished_at?: string;
  duration_seconds?: number;
  meta_json?: Record<string, any>;
  error_text?: string;
  items_processed?: number;
  items_created?: number;
  items_updated?: number;
  items_failed?: number;
  created_at: string;
  /** Record last update timestamp */
  updated_at: string;
}

/**
 * AgentRun creation payload (excludes auto-generated fields)
 */
export interface CreateAgentRun extends Omit<AgentRun, 'id' | 'created_at' | 'updated_at'> {}

/**
 * AgentRun update payload (all fields optional except id)
 */
export interface UpdateAgentRun extends Partial<Omit<AgentRun, 'id'>> {
  id: string;
}


/**
 * ScrapeJob database model
 * Table: scrape_job
 */
export interface ScrapeJob {
  id: string;
  subject_type: string;
  subject_id?: string;
  job_type: string;
  priority?: number;
  scheduled_for: string;
  status?: string;
  last_run_at?: string;
  last_run_id?: string;
  retry_count?: number;
  max_retries?: number;
  config_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

/**
 * ScrapeJob creation payload (excludes auto-generated fields)
 */
export interface CreateScrapeJob extends Omit<ScrapeJob, 'id' | 'created_at' | 'updated_at'> {}

/**
 * ScrapeJob update payload (all fields optional except id)
 */
export interface UpdateScrapeJob extends Partial<Omit<ScrapeJob, 'id'>> {
  id: string;
}



// ===== API RESPONSE TYPES =====

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface SearchResponse<T = any> {
  results: T[];
  query: string;
  total: number;
  suggestions?: string[];
}

// ===== USER PREFERENCES =====

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  timezone: string;
  email_notifications: boolean;
  push_notifications: boolean;
  favorite_sports: string[];
  content_categories: ContentCategoryType[];
  ai_summary_enabled: boolean;
}

export interface UserSportPreference {
  sport_id: string;
  sport_name: string;
  sport_display_name: string;
  rank: number;
  has_teams: boolean;
}

export interface UserTeamPreference {
  team_id: string;
  team_name: string;
  team_city: string;
  team_abbreviation: string;
  sport: SportType;
  league: LeagueType;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  followed_at: string;
  notifications_enabled: boolean;
}

// ===== GAME & SCORING =====

export interface GameScore {
  game_id: string;
  start_time: string;
  venue?: string;
  game_status: GameStatusType;
  home_team_name: string;
  home_team_abbr: string;
  home_team_logo?: string;
  home_score: number;
  home_is_final: boolean;
  away_team_name: string;
  away_team_abbr: string;
  away_team_logo?: string;
  away_score: number;
  away_is_final: boolean;
}

export interface LiveScore {
  game_id: string;
  team_id: string;
  pts: number;
  period?: number;
  period_pts?: number;
  is_final: boolean;
  updated_at: string;
}

// ===== CONTENT & ARTICLES =====

export interface ArticleWithClassification extends Article {
  classifications: ArticleClassification[];
  entities: ArticleEntity[];
}

export interface PersonalizedArticle {
  id: string;
  title: string;
  summary?: string;
  author?: string;
  source_name: string;
  source_url: string;
  published_at?: string;
  category?: ContentCategoryType;
  tags: string[];
  ai_summary?: string;
  sentiment_score?: number;
  view_count: number;
  like_count: number;
}

// ===== TEAM DASHBOARD =====

export interface TeamDashboard {
  team: {
    id: string;
    name: string;
    city?: string;
    abbreviation: string;
    sport: SportType;
    league: LeagueType;
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
  };
  latest_score?: GameScore;
  recent_results: GameScore[];
  summary?: {
    text: string;
    generated_at: string;
  };
  news: PersonalizedArticle[];
  depth_chart: DepthChart[];
  ticket_deals: TicketDeal[];
  experiences: Experience[];
}

// ===== PIPELINE & OPERATIONS =====

export interface AgentRunSummary {
  id: string;
  agent_type: AgentTypeType;
  subject_key: string;
  status: RunStatusType;
  started_at?: string;
  finished_at?: string;
  duration_seconds?: number;
  items_processed?: number;
  items_created?: number;
  items_updated?: number;
  items_failed?: number;
  error_text?: string;
}

export interface IngestionStats {
  total_attempts: number;
  successful: number;
  duplicates: number;
  errors: number;
  duplicate_rate: number;
  success_rate: number;
  error_rate: number;
}

export interface SearchAnalyticsSummary {
  total_searches: number;
  unique_users: number;
  avg_results_per_search: number;
  zero_result_rate: number;
  click_through_rate: number;
}

// ===== WEBSOCKET EVENTS =====

export interface WebSocketEvent {
  type: string;
  timestamp: string;
  data: any;
}

export interface ScoreUpdateEvent extends WebSocketEvent {
  type: 'score_update';
  data: {
    game_id: string;
    team_id: string;
    score: LiveScore;
  };
}

export interface BreakingNewsEvent extends WebSocketEvent {
  type: 'breaking_news';
  data: {
    article: Article;
    teams: string[];
  };
}

export interface TicketUpdateEvent extends WebSocketEvent {
  type: 'ticket_update';
  data: {
    game_id: string;
    deals: TicketDeal[];
  };
}

// ===== UTILITY TYPES =====

export type EntityType = 'team' | 'player' | 'coach' | 'venue' | 'league' | 'person' | 'organization';

export type SortOrder = 'asc' | 'desc';

export interface SortOption {
  field: string;
  order: SortOrder;
}

export interface FilterOption {
  field: string;
  value: any;
  operator?: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'like';
}

export interface QueryOptions {
  page?: number;
  limit?: number;
  sort?: SortOption[];
  filters?: FilterOption[];
  search?: string;
}

