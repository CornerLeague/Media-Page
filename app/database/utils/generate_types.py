"""Generate TypeScript types from SQLAlchemy models."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Add the database models to the path
sys.path.append(str(Path(__file__).parent.parent))

from models import *
from models.enums import *
from sqlalchemy import inspect
from sqlalchemy.sql.sqltypes import DateTime, Boolean, Integer, String, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

# TypeScript type mappings
TYPE_MAPPING = {
    'UUID': 'string',
    'String': 'string',
    'Text': 'string',
    'Integer': 'number',
    'Numeric': 'number',
    'Boolean': 'boolean',
    'DateTime': 'string',  # ISO string
    'TIMESTAMP': 'string',  # ISO string
    'JSONB': 'Record<string, any>',
    'ARRAY': 'Array',
    'TSVector': 'string',  # Full-text search vector
}

# Enum type mappings
ENUM_MAPPING = {
    'UserRole': ['user', 'admin', 'moderator'],
    'UserStatus': ['active', 'inactive', 'suspended'],
    'TeamStatus': ['active', 'inactive', 'archived'],
    'Sport': ['nfl', 'nba', 'mlb', 'nhl', 'mls', 'college_football', 'college_basketball'],
    'League': ['NFL', 'NBA', 'MLB', 'NHL', 'MLS', 'NCAA_FB', 'NCAA_BB'],
    'ArticleStatus': ['draft', 'published', 'archived', 'deleted'],
    'ContentCategory': ['news', 'analysis', 'opinion', 'rumors', 'injury_report', 'trade', 'draft', 'game_recap'],
    'GameStatus': ['scheduled', 'live', 'completed', 'postponed', 'cancelled'],
    'IngestionStatus': ['success', 'duplicate', 'error', 'skip'],
    'ArticleClassificationCategory': ['injury', 'roster', 'trade', 'general', 'depth_chart', 'game_recap', 'analysis', 'rumors'],
    'AgentType': ['scores', 'news', 'depth_chart', 'tickets', 'experiences', 'planner', 'content_classification'],
    'RunStatus': ['pending', 'running', 'completed', 'failed', 'cancelled'],
    'JobType': ['scrape_news', 'scrape_scores', 'scrape_depth_chart', 'scrape_tickets', 'scrape_experiences', 'classify_content'],
    'ExperienceType': ['watch_party', 'meetup', 'bar_event', 'community_event', 'fan_fest', 'tailgate'],
    'SeatQuality': ['premium', 'good', 'average', 'poor'],
}


def get_typescript_type(column) -> str:
    """Convert SQLAlchemy column type to TypeScript type."""
    column_type = str(column.type)

    # Handle UUID type
    if 'UUID' in column_type:
        return 'string'

    # Handle ARRAY types
    if 'ARRAY' in column_type:
        if 'UUID' in column_type:
            return 'string[]'
        elif 'TEXT' in column_type or 'VARCHAR' in column_type:
            return 'string[]'
        else:
            return 'any[]'

    # Handle JSONB
    if 'JSONB' in column_type:
        return 'Record<string, any>'

    # Handle Numeric/DECIMAL
    if 'NUMERIC' in column_type or 'DECIMAL' in column_type:
        return 'number'

    # Handle Enums
    if hasattr(column.type, 'name') and column.type.name in ENUM_MAPPING:
        enum_values = ENUM_MAPPING[column.type.name]
        return ' | '.join([f"'{value}'" for value in enum_values])

    # Handle basic types
    if isinstance(column.type, (DateTime,)):
        return 'string'
    elif isinstance(column.type, Boolean):
        return 'boolean'
    elif isinstance(column.type, (Integer,)):
        return 'number'
    elif isinstance(column.type, (String, Text)):
        return 'string'
    elif isinstance(column.type, Numeric):
        return 'number'

    # Fallback
    return 'any'


def generate_enum_types() -> str:
    """Generate TypeScript enum types."""
    enums = []

    for enum_name, values in ENUM_MAPPING.items():
        enum_values = '\n'.join([f"  {value.upper().replace('-', '_')} = '{value}'," for value in values])
        enums.append(f"""export enum {enum_name} {{
{enum_values}
}}

export type {enum_name}Type = {' | '.join([f"'{value}'" for value in values])};
""")

    return '\n'.join(enums)


def generate_interface_for_model(model_class) -> str:
    """Generate TypeScript interface for a SQLAlchemy model."""
    class_name = model_class.__name__
    table_name = model_class.__tablename__

    # Get column information
    inspector = inspect(model_class)
    columns = inspector.columns

    # Generate interface properties
    properties = []

    for column in columns:
        column_name = column.name
        ts_type = get_typescript_type(column)
        is_optional = column.nullable or column.default is not None

        # Add JSDoc comment if available
        comment = getattr(column, 'doc', None) or getattr(column, 'comment', None)
        if comment:
            properties.append(f"  /** {comment} */")

        optional_marker = '?' if is_optional else ''
        properties.append(f"  {column_name}{optional_marker}: {ts_type};")

    properties_str = '\n'.join(properties)

    return f"""/**
 * {class_name} database model
 * Table: {table_name}
 */
export interface {class_name} {{
{properties_str}
}}

/**
 * {class_name} creation payload (excludes auto-generated fields)
 */
export interface Create{class_name} extends Omit<{class_name}, 'id' | 'created_at' | 'updated_at'> {{}}

/**
 * {class_name} update payload (all fields optional except id)
 */
export interface Update{class_name} extends Partial<Omit<{class_name}, 'id'>> {{
  id: string;
}}
"""


def generate_api_types() -> str:
    """Generate API-specific TypeScript types."""
    return """
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
"""


def generate_all_types() -> str:
    """Generate all TypeScript types."""
    header = f"""/**
 * TypeScript types generated from SQLAlchemy models
 * Generated on: {datetime.now().isoformat()}
 *
 * This file is auto-generated. Do not edit manually.
 * To regenerate, run: python app/database/utils/generate_types.py
 */

// ===== ENUMS =====

"""

    # Generate enums
    enums = generate_enum_types()

    # Generate model interfaces
    models = []
    model_classes = [
        User, UserTeam, UserPreferenceHistory,
        Team, TeamStats,
        Article, ArticleClassification, ArticleEntity,
        Game, Score,
        FeedSource, IngestionLog,
        SearchAnalytics,
        Sport, UserSportPref,
        DepthChart,
        TicketDeal,
        Experience,
        AgentRun, ScrapeJob,
    ]

    for model_class in model_classes:
        try:
            interface = generate_interface_for_model(model_class)
            models.append(interface)
        except Exception as e:
            print(f"Error generating interface for {model_class.__name__}: {e}")

    model_interfaces = '\n\n'.join(models)

    # Generate API types
    api_types = generate_api_types()

    return f"""{header}
{enums}

// ===== DATABASE MODELS =====

{model_interfaces}

{api_types}
"""


def write_types_file(output_path: Path, content: str) -> None:
    """Write TypeScript types to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"TypeScript types written to: {output_path}")


def main():
    """Main function to generate TypeScript types."""
    # Determine output path
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent  # Go up to project root

    # Check if we're in the React project structure
    react_src = project_root / "src"
    if react_src.exists():
        # React project - put types in src/lib/types/
        output_path = react_src / "lib" / "types" / "database.ts"
    else:
        # Default - put in database/schemas/
        output_path = current_dir.parent / "schemas" / "database.types.ts"

    try:
        content = generate_all_types()
        write_types_file(output_path, content)

        print(f"✅ Successfully generated TypeScript types!")
        print(f"📁 Output: {output_path}")
        print(f"📊 Generated types for {len([User, Team, Article, Game, Score, Sport, DepthChart, TicketDeal, Experience, AgentRun, ScrapeJob])} models")

    except Exception as e:
        print(f"❌ Error generating TypeScript types: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()