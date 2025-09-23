"""Add indexes, triggers, and utility functions

Revision ID: 003_indexes_and_triggers
Revises: 002_players_and_experiences
Create Date: 2025-01-17 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_indexes_and_triggers'
down_revision: Union[str, None] = '002_players_and_experiences'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes, triggers, and utility functions."""

    # Create performance indexes
    # User-related indexes
    op.create_index('idx_users_clerk_id', 'users', ['clerk_user_id'])
    op.create_index('idx_users_active', 'users', ['is_active', 'last_active_at'])
    op.create_index('idx_user_sport_prefs_user_rank', 'user_sport_preferences', ['user_id', 'rank'])
    op.create_index('idx_user_team_prefs_user_affinity', 'user_team_preferences', ['user_id', 'affinity_score'], postgresql_order_by=['user_id', 'affinity_score DESC'])

    # Sports/Teams indexes
    op.create_index('idx_teams_sport_league', 'teams', ['sport_id', 'league_id'])
    op.create_index('idx_teams_active', 'teams', ['is_active'])
    op.create_index('idx_leagues_sport', 'leagues', ['sport_id'])

    # Games indexes
    op.create_index('idx_games_teams', 'games', ['home_team_id', 'away_team_id'])
    op.create_index('idx_games_scheduled', 'games', ['scheduled_at'])
    op.create_index('idx_games_status', 'games', ['status'])
    op.create_index('idx_games_sport_league', 'games', ['sport_id', 'league_id'])
    op.create_index('idx_game_events_game_time', 'game_events', ['game_id', 'event_time'])

    # Content indexes
    op.create_index('idx_articles_published', 'articles', ['published_at'], postgresql_order_by=['published_at DESC'])
    op.create_index('idx_articles_category', 'articles', ['category'])
    op.create_index('idx_articles_active', 'articles', ['is_active'])
    op.create_index('idx_articles_source', 'articles', ['source'])
    op.create_index('idx_article_sports_relevance', 'article_sports', ['sport_id', 'relevance_score'], postgresql_order_by=['sport_id', 'relevance_score DESC'])
    op.create_index('idx_article_teams_relevance', 'article_teams', ['team_id', 'relevance_score'], postgresql_order_by=['team_id', 'relevance_score DESC'])

    # Feed processing indexes
    op.create_index('idx_feed_snapshots_url_hash', 'feed_snapshots', ['url_hash'])
    op.create_index('idx_feed_snapshots_content_hash', 'feed_snapshots', ['content_hash'])
    op.create_index('idx_feed_snapshots_status', 'feed_snapshots', ['status'])
    op.create_index('idx_feed_sources_active', 'feed_sources', ['is_active', 'last_fetched_at'])

    # Full-text search indexes (GIN indexes for PostgreSQL)
    op.create_index('idx_articles_search_vector', 'articles', ['search_vector'], postgresql_using='gin')
    op.create_index('idx_articles_title_trgm', 'articles', ['title'], postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'})

    # Analytics indexes
    op.create_index('idx_user_interactions_user_type', 'user_interactions', ['user_id', 'interaction_type'])
    op.create_index('idx_user_interactions_entity', 'user_interactions', ['entity_type', 'entity_id'])
    op.create_index('idx_content_performance_date', 'content_performance', ['date_recorded', 'content_type'])

    # Ticket and experience indexes
    op.create_index('idx_ticket_deals_team_game', 'ticket_deals', ['team_id', 'game_id'])
    op.create_index('idx_ticket_deals_score', 'ticket_deals', ['deal_score'], postgresql_order_by=['deal_score DESC'])
    op.create_index('idx_fan_experiences_team_time', 'fan_experiences', ['team_id', 'start_time'])
    op.create_index('idx_fan_experiences_type', 'fan_experiences', ['experience_type'])

    # Create triggers for updated_at columns
    trigger_tables = [
        'sports', 'leagues', 'teams', 'users', 'user_sport_preferences',
        'user_team_preferences', 'user_news_preferences', 'user_notification_settings',
        'games', 'articles', 'players', 'depth_chart_entries', 'ticket_deals',
        'fan_experiences', 'feed_sources'
    ]

    for table in trigger_tables:
        op.execute(f"""
            CREATE TRIGGER set_updated_at_{table}
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """)

    # Create search vector update trigger for articles
    op.execute("""
        CREATE OR REPLACE FUNCTION update_article_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                                setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
                                setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER update_article_search_vector_trigger
        BEFORE INSERT OR UPDATE ON articles
        FOR EACH ROW EXECUTE FUNCTION update_article_search_vector();
    """)

    # Create utility functions
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_deal_score(
            price DECIMAL,
            average_price DECIMAL,
            market_demand DECIMAL DEFAULT 0.5
        ) RETURNS DECIMAL AS $$
        BEGIN
            -- Simple deal score calculation: lower price = higher score
            -- With market demand adjustment
            RETURN GREATEST(0, LEAST(1, (1 - (price / NULLIF(average_price, 0))) * (1 + market_demand)));
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION get_user_primary_team(user_uuid UUID)
        RETURNS UUID AS $$
        DECLARE
            primary_team_id UUID;
        BEGIN
            SELECT team_id INTO primary_team_id
            FROM user_team_preferences
            WHERE user_id = user_uuid
            ORDER BY affinity_score DESC
            LIMIT 1;

            RETURN primary_team_id;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION get_personalized_articles(
            user_uuid UUID,
            limit_count INTEGER DEFAULT 20
        ) RETURNS TABLE (
            article_id UUID,
            title VARCHAR,
            summary TEXT,
            published_at TIMESTAMP WITH TIME ZONE,
            relevance_score DECIMAL
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT DISTINCT
                a.id,
                a.title,
                a.summary,
                a.published_at,
                GREATEST(
                    COALESCE(ast.relevance_score, 0) * usp.rank::DECIMAL / 10,
                    COALESCE(at.relevance_score, 0) * utp.affinity_score
                ) as relevance_score
            FROM articles a
            LEFT JOIN article_sports ast ON a.id = ast.article_id
            LEFT JOIN user_sport_preferences usp ON ast.sport_id = usp.sport_id AND usp.user_id = user_uuid
            LEFT JOIN article_teams at ON a.id = at.article_id
            LEFT JOIN user_team_preferences utp ON at.team_id = utp.team_id AND utp.user_id = user_uuid
            WHERE a.is_active = true
            AND (usp.user_id IS NOT NULL OR utp.user_id IS NOT NULL)
            ORDER BY relevance_score DESC, a.published_at DESC
            LIMIT limit_count;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Remove indexes, triggers, and utility functions."""

    # Drop utility functions
    op.execute('DROP FUNCTION IF EXISTS get_personalized_articles(UUID, INTEGER)')
    op.execute('DROP FUNCTION IF EXISTS get_user_primary_team(UUID)')
    op.execute('DROP FUNCTION IF EXISTS calculate_deal_score(DECIMAL, DECIMAL, DECIMAL)')

    # Drop search vector trigger and function
    op.execute('DROP TRIGGER IF EXISTS update_article_search_vector_trigger ON articles')
    op.execute('DROP FUNCTION IF EXISTS update_article_search_vector()')

    # Drop updated_at triggers
    trigger_tables = [
        'sports', 'leagues', 'teams', 'users', 'user_sport_preferences',
        'user_team_preferences', 'user_news_preferences', 'user_notification_settings',
        'games', 'articles', 'players', 'depth_chart_entries', 'ticket_deals',
        'fan_experiences', 'feed_sources'
    ]

    for table in trigger_tables:
        op.execute(f'DROP TRIGGER IF EXISTS set_updated_at_{table} ON {table}')

    # Drop indexes (in reverse order)
    op.drop_index('idx_fan_experiences_type')
    op.drop_index('idx_fan_experiences_team_time')
    op.drop_index('idx_ticket_deals_score')
    op.drop_index('idx_ticket_deals_team_game')
    op.drop_index('idx_content_performance_date')
    op.drop_index('idx_user_interactions_entity')
    op.drop_index('idx_user_interactions_user_type')
    op.drop_index('idx_articles_title_trgm')
    op.drop_index('idx_articles_search_vector')
    op.drop_index('idx_feed_sources_active')
    op.drop_index('idx_feed_snapshots_status')
    op.drop_index('idx_feed_snapshots_content_hash')
    op.drop_index('idx_feed_snapshots_url_hash')
    op.drop_index('idx_article_teams_relevance')
    op.drop_index('idx_article_sports_relevance')
    op.drop_index('idx_articles_source')
    op.drop_index('idx_articles_active')
    op.drop_index('idx_articles_category')
    op.drop_index('idx_articles_published')
    op.drop_index('idx_game_events_game_time')
    op.drop_index('idx_games_sport_league')
    op.drop_index('idx_games_status')
    op.drop_index('idx_games_scheduled')
    op.drop_index('idx_games_teams')
    op.drop_index('idx_leagues_sport')
    op.drop_index('idx_teams_active')
    op.drop_index('idx_teams_sport_league')
    op.drop_index('idx_user_team_prefs_user_affinity')
    op.drop_index('idx_user_sport_prefs_user_rank')
    op.drop_index('idx_users_active')
    op.drop_index('idx_users_clerk_id')