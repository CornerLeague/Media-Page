/**
 * Supabase Database Schema Types
 *
 * This file defines the TypeScript types for the Supabase database schema.
 * It includes Row, Insert, and Update types for all tables with RLS policies.
 */

// Generated types for Supabase database
export interface Database {
  public: {
    Tables: {
      users: {
        Row: UserRow;
        Insert: UserInsert;
        Update: UserUpdate;
      };
      user_sports: {
        Row: UserSportRow;
        Insert: UserSportInsert;
        Update: UserSportUpdate;
      };
      user_teams: {
        Row: UserTeamRow;
        Insert: UserTeamInsert;
        Update: UserTeamUpdate;
      };
      user_preferences: {
        Row: UserPreferencesRow;
        Insert: UserPreferencesInsert;
        Update: UserPreferencesUpdate;
      };
      sports: {
        Row: SportRow;
        Insert: SportInsert;
        Update: SportUpdate;
      };
      teams: {
        Row: TeamRow;
        Insert: TeamInsert;
        Update: TeamUpdate;
      };
      leagues: {
        Row: LeagueRow;
        Insert: LeagueInsert;
        Update: LeagueUpdate;
      };
      articles: {
        Row: ArticleRow;
        Insert: ArticleInsert;
        Update: ArticleUpdate;
      };
      article_teams: {
        Row: ArticleTeamRow;
        Insert: ArticleTeamInsert;
        Update: ArticleTeamUpdate;
      };
      article_sports: {
        Row: ArticleSportRow;
        Insert: ArticleSportInsert;
        Update: ArticleSportUpdate;
      };
      user_article_interactions: {
        Row: UserArticleInteractionRow;
        Insert: UserArticleInteractionInsert;
        Update: UserArticleInteractionUpdate;
      };
    };
    Views: {
      user_feed: {
        Row: UserFeedView;
      };
      team_stats: {
        Row: TeamStatsView;
      };
    };
    Functions: {
      get_personalized_feed: {
        Args: {
          user_id: string;
          limit_count?: number;
          offset_count?: number;
        };
        Returns: PersonalizedFeedItem[];
      };
      update_user_preferences: {
        Args: {
          user_id: string;
          preferences: UserPreferencesJson;
        };
        Returns: UserPreferencesRow;
      };
    };
    Enums: {
      content_frequency: 'minimal' | 'standard' | 'comprehensive';
      news_category: 'injuries' | 'trades' | 'roster' | 'general' | 'scores' | 'analysis';
      interaction_type: 'view' | 'like' | 'share' | 'save' | 'hide';
    };
  };
}

// Table Row Types
export interface UserRow {
  id: string;
  clerk_user_id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserInsert {
  id?: string;
  clerk_user_id: string;
  email: string;
  display_name?: string | null;
  avatar_url?: string | null;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UserUpdate {
  clerk_user_id?: string;
  email?: string;
  display_name?: string | null;
  avatar_url?: string | null;
  is_active?: boolean;
  updated_at?: string;
}

export interface UserSportRow {
  id: string;
  user_id: string;
  sport_id: string;
  rank: number;
  created_at: string;
  updated_at: string;
}

export interface UserSportInsert {
  id?: string;
  user_id: string;
  sport_id: string;
  rank: number;
  created_at?: string;
  updated_at?: string;
}

export interface UserSportUpdate {
  sport_id?: string;
  rank?: number;
  updated_at?: string;
}

export interface UserTeamRow {
  id: string;
  user_id: string;
  team_id: string;
  affinity_score: number;
  created_at: string;
  updated_at: string;
}

export interface UserTeamInsert {
  id?: string;
  user_id: string;
  team_id: string;
  affinity_score?: number;
  created_at?: string;
  updated_at?: string;
}

export interface UserTeamUpdate {
  team_id?: string;
  affinity_score?: number;
  updated_at?: string;
}

export interface UserPreferencesRow {
  id: string;
  user_id: string;
  news_types: NewsTypePreference[];
  notifications: NotificationSettings;
  content_frequency: Database['public']['Enums']['content_frequency'];
  created_at: string;
  updated_at: string;
}

export interface UserPreferencesInsert {
  id?: string;
  user_id: string;
  news_types: NewsTypePreference[];
  notifications: NotificationSettings;
  content_frequency: Database['public']['Enums']['content_frequency'];
  created_at?: string;
  updated_at?: string;
}

export interface UserPreferencesUpdate {
  news_types?: NewsTypePreference[];
  notifications?: NotificationSettings;
  content_frequency?: Database['public']['Enums']['content_frequency'];
  updated_at?: string;
}

export interface SportRow {
  id: string;
  name: string;
  slug: string;
  has_teams: boolean;
  icon: string | null;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface SportInsert {
  id?: string;
  name: string;
  slug: string;
  has_teams?: boolean;
  icon?: string | null;
  is_active?: boolean;
  display_order?: number;
  created_at?: string;
  updated_at?: string;
}

export interface SportUpdate {
  name?: string;
  slug?: string;
  has_teams?: boolean;
  icon?: string | null;
  is_active?: boolean;
  display_order?: number;
  updated_at?: string;
}

export interface LeagueRow {
  id: string;
  name: string;
  slug: string;
  sport_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LeagueInsert {
  id?: string;
  name: string;
  slug: string;
  sport_id: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface LeagueUpdate {
  name?: string;
  slug?: string;
  sport_id?: string;
  is_active?: boolean;
  updated_at?: string;
}

export interface TeamRow {
  id: string;
  name: string;
  market: string;
  slug: string;
  sport_id: string;
  league_id: string;
  abbreviation: string;
  logo_url: string | null;
  primary_color: string | null;
  secondary_color: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TeamInsert {
  id?: string;
  name: string;
  market: string;
  slug: string;
  sport_id: string;
  league_id: string;
  abbreviation: string;
  logo_url?: string | null;
  primary_color?: string | null;
  secondary_color?: string | null;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface TeamUpdate {
  name?: string;
  market?: string;
  slug?: string;
  sport_id?: string;
  league_id?: string;
  abbreviation?: string;
  logo_url?: string | null;
  primary_color?: string | null;
  secondary_color?: string | null;
  is_active?: boolean;
  updated_at?: string;
}

export interface ArticleRow {
  id: string;
  title: string;
  summary: string | null;
  content: string;
  source: string;
  author: string | null;
  published_at: string;
  category: Database['public']['Enums']['news_category'];
  priority: number;
  image_url: string | null;
  external_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ArticleInsert {
  id?: string;
  title: string;
  summary?: string | null;
  content: string;
  source: string;
  author?: string | null;
  published_at: string;
  category: Database['public']['Enums']['news_category'];
  priority?: number;
  image_url?: string | null;
  external_url?: string | null;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ArticleUpdate {
  title?: string;
  summary?: string | null;
  content?: string;
  source?: string;
  author?: string | null;
  published_at?: string;
  category?: Database['public']['Enums']['news_category'];
  priority?: number;
  image_url?: string | null;
  external_url?: string | null;
  is_active?: boolean;
  updated_at?: string;
}

export interface ArticleTeamRow {
  id: string;
  article_id: string;
  team_id: string;
  relevance_score: number;
  created_at: string;
}

export interface ArticleTeamInsert {
  id?: string;
  article_id: string;
  team_id: string;
  relevance_score?: number;
  created_at?: string;
}

export interface ArticleTeamUpdate {
  relevance_score?: number;
}

export interface ArticleSportRow {
  id: string;
  article_id: string;
  sport_id: string;
  relevance_score: number;
  created_at: string;
}

export interface ArticleSportInsert {
  id?: string;
  article_id: string;
  sport_id: string;
  relevance_score?: number;
  created_at?: string;
}

export interface ArticleSportUpdate {
  relevance_score?: number;
}

export interface UserArticleInteractionRow {
  id: string;
  user_id: string;
  article_id: string;
  interaction_type: Database['public']['Enums']['interaction_type'];
  created_at: string;
}

export interface UserArticleInteractionInsert {
  id?: string;
  user_id: string;
  article_id: string;
  interaction_type: Database['public']['Enums']['interaction_type'];
  created_at?: string;
}

export interface UserArticleInteractionUpdate {
  interaction_type?: Database['public']['Enums']['interaction_type'];
}

// View Types
export interface UserFeedView {
  article_id: string;
  title: string;
  summary: string | null;
  content: string;
  source: string;
  author: string | null;
  published_at: string;
  category: Database['public']['Enums']['news_category'];
  priority: number;
  image_url: string | null;
  external_url: string | null;
  teams: string[];
  sports: string[];
  relevance_score: number;
  user_interaction: Database['public']['Enums']['interaction_type'] | null;
}

export interface TeamStatsView {
  team_id: string;
  team_name: string;
  market: string;
  league_name: string;
  sport_name: string;
  follower_count: number;
  recent_articles: number;
  avg_priority: number;
}

// JSON Types for Complex Fields
export interface NewsTypePreference {
  type: Database['public']['Enums']['news_category'];
  enabled: boolean;
  priority: number;
}

export interface NotificationSettings {
  push: boolean;
  email: boolean;
  game_reminders: boolean;
  news_alerts: boolean;
  score_updates: boolean;
}

export interface UserPreferencesJson {
  news_types: NewsTypePreference[];
  notifications: NotificationSettings;
  content_frequency: Database['public']['Enums']['content_frequency'];
}

// Function Return Types
export interface PersonalizedFeedItem {
  article_id: string;
  title: string;
  summary: string | null;
  source: string;
  author: string | null;
  published_at: string;
  category: Database['public']['Enums']['news_category'];
  image_url: string | null;
  external_url: string | null;
  teams: { id: string; name: string; market: string }[];
  sports: { id: string; name: string }[];
  relevance_score: number;
  priority_score: number;
}

// RLS Policy Helpers
export type RLSContext = {
  user_id: string;
  clerk_user_id: string;
  is_admin?: boolean;
};

// Migration Types
export interface MigrationResult {
  success: boolean;
  migrated_records: number;
  conflicts: string[];
  rollback_data?: any;
}

export interface LocalStorageMigration {
  local_data: {
    sports: Array<{ sportId: string; name: string; rank: number; hasTeams: boolean }>;
    teams: Array<{ teamId: string; name: string; sportId: string; league: string; affinityScore: number }>;
    preferences: UserPreferencesJson;
  };
  last_modified: string;
  conflicts?: string[];
}

// Utility Types
export type DatabaseRow<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row'];
export type DatabaseInsert<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Insert'];
export type DatabaseUpdate<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Update'];

// Export the main Database type for Supabase client
export type { Database as SupabaseDatabase };