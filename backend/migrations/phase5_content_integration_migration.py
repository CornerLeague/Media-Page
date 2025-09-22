"""
Phase 5: College Basketball Content Integration Migration
Creates content classification system, injury reports, recruiting news, and coaching updates

This migration integrates with the existing content pipeline and extends it with
college basketball-specific features while maintaining compatibility.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

logger = logging.getLogger(__name__)


class Phase5ContentIntegrationMigration:
    """
    Phase 5 migration implementing college basketball content integration.

    Creates:
    - Enhanced content classification system
    - Injury report tracking
    - Recruiting news management
    - Coaching change tracking
    - Multi-team content relationships
    - Enhanced content categorization
    """

    def __init__(self):
        self.migration_name = "Phase 5: Content Integration"
        self.version = "20250921_2000_phase5_content_integration"

    async def upgrade(self, session: AsyncSession) -> None:
        """
        Apply Phase 5 content integration schema changes
        """
        logger.info(f"Starting {self.migration_name} upgrade...")

        try:
            # Create enum types first
            await self._create_enum_types(session)

            # Create core content tables
            await self._create_content_tables(session)

            # Create content relationship tables
            await self._create_relationship_tables(session)

            # Create content classification tables
            await self._create_classification_tables(session)

            # Create indexes for performance
            await self._create_indexes(session)

            # Create triggers for search vectors
            await self._create_search_triggers(session)

            await session.commit()
            logger.info(f"{self.migration_name} upgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.migration_name} upgrade: {str(e)}")
            raise

    async def downgrade(self, session: AsyncSession) -> None:
        """
        Rollback Phase 5 content integration schema changes
        """
        logger.info(f"Starting {self.migration_name} downgrade...")

        try:
            # Drop tables in reverse dependency order
            await self._drop_content_tables(session)

            # Drop enum types
            await self._drop_enum_types(session)

            await session.commit()
            logger.info(f"{self.migration_name} downgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.migration_name} downgrade: {str(e)}")
            raise

    async def _create_enum_types(self, session: AsyncSession) -> None:
        """Create custom enum types for content integration"""
        logger.info("Creating enum types...")

        enum_definitions = [
            """
            CREATE TYPE college_content_type AS ENUM (
                'game_preview', 'game_recap', 'injury_report', 'recruiting_news',
                'transfer_portal', 'coaching_news', 'conference_news', 'tournament_news',
                'ranking_news', 'academic_news', 'suspension_news', 'eligibility_news',
                'depth_chart', 'season_outlook', 'bracket_analysis', 'recruiting_commit',
                'recruiting_decommit', 'recruiting_visit', 'coach_hire', 'coach_fire',
                'coach_extension', 'facility_news', 'alumni_news'
            )
            """,
            """
            CREATE TYPE injury_type AS ENUM (
                'ankle', 'knee', 'foot', 'back', 'shoulder', 'hand', 'wrist',
                'hip', 'concussion', 'illness', 'personal', 'other'
            )
            """,
            """
            CREATE TYPE injury_severity AS ENUM (
                'minor', 'moderate', 'major', 'season_ending', 'career_ending'
            )
            """,
            """
            CREATE TYPE recruiting_event_type AS ENUM (
                'commit', 'decommit', 'visit', 'offer', 'contact', 'evaluation',
                'transfer_entry', 'transfer_commitment', 'transfer_withdrawal'
            )
            """,
            """
            CREATE TYPE coaching_change_type AS ENUM (
                'hire', 'fire', 'resignation', 'retirement', 'extension',
                'promotion', 'demotion', 'suspension', 'reinstatement'
            )
            """
        ]

        for enum_sql in enum_definitions:
            await session.execute(text(enum_sql))

    async def _create_content_tables(self, session: AsyncSession) -> None:
        """Create core content tables"""
        logger.info("Creating content tables...")

        # College Content Table
        college_content_sql = """
        CREATE TABLE college_content (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            article_id UUID REFERENCES articles(id) ON DELETE CASCADE,

            -- Content identification
            title VARCHAR(500) NOT NULL,
            summary TEXT,
            content TEXT,

            -- College basketball specific classification
            content_type college_content_type NOT NULL,

            -- Team associations
            primary_team_id UUID REFERENCES college_teams(id) ON DELETE CASCADE,
            secondary_team_id UUID REFERENCES college_teams(id) ON DELETE CASCADE,

            -- Player association
            primary_player_id UUID REFERENCES players(id) ON DELETE CASCADE,

            -- Content metadata
            author VARCHAR(255),
            source VARCHAR(255) NOT NULL,
            published_at TIMESTAMPTZ NOT NULL,
            url VARCHAR(1000),
            image_url VARCHAR(1000),

            -- Content analysis
            word_count INTEGER CHECK (word_count >= 0),
            reading_time_minutes INTEGER CHECK (reading_time_minutes >= 0),
            sentiment_score NUMERIC(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
            relevance_score NUMERIC(3,2) DEFAULT 0.5 NOT NULL CHECK (relevance_score >= 0 AND relevance_score <= 1),
            engagement_score NUMERIC(10,2) CHECK (engagement_score >= 0),

            -- Search and categorization
            search_vector TSVECTOR,
            tags TEXT[],
            mentioned_players TEXT[],
            mentioned_coaches TEXT[],

            -- Metadata
            external_id VARCHAR(255),
            metadata JSONB,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            is_featured BOOLEAN DEFAULT FALSE NOT NULL,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
        """

        # Injury Reports Table
        injury_reports_sql = """
        CREATE TABLE injury_reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Player and team
            player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            team_id UUID NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,

            -- Injury details
            injury_type injury_type NOT NULL,
            injury_description TEXT NOT NULL,
            severity injury_severity NOT NULL,

            -- Timeline
            injury_date DATE NOT NULL,
            reported_date DATE DEFAULT CURRENT_DATE NOT NULL,
            expected_return_date DATE,
            actual_return_date DATE,

            -- Status tracking
            current_status player_eligibility_status DEFAULT 'injured' NOT NULL,
            games_missed INTEGER DEFAULT 0 NOT NULL CHECK (games_missed >= 0),

            -- Additional details
            requires_surgery BOOLEAN DEFAULT FALSE NOT NULL,
            surgery_date DATE,
            recovery_notes TEXT,

            -- Content association
            content_id UUID REFERENCES college_content(id) ON DELETE SET NULL,

            -- Medical metadata
            medical_metadata JSONB,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

            -- Constraints
            UNIQUE (player_id, injury_date, injury_type)
        )
        """

        # Recruiting News Table
        recruiting_news_sql = """
        CREATE TABLE recruiting_news (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Recruit information
            recruit_name VARCHAR(200) NOT NULL,
            recruit_position player_position,
            recruit_height VARCHAR(10),
            recruit_weight INTEGER,

            -- Academic information
            high_school VARCHAR(200),
            hometown VARCHAR(100),
            home_state VARCHAR(50),
            recruiting_class INTEGER,

            -- Event details
            event_type recruiting_event_type NOT NULL,
            team_id UUID REFERENCES college_teams(id) ON DELETE CASCADE,
            previous_team_id UUID REFERENCES college_teams(id) ON DELETE CASCADE,
            event_date DATE NOT NULL,

            -- Ratings and rankings
            rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5),
            national_ranking INTEGER,
            position_ranking INTEGER,
            state_ranking INTEGER,

            -- Additional details
            scholarship_type VARCHAR(50),
            commitment_level VARCHAR(50),
            other_offers TEXT[],
            visit_details JSONB,

            -- Content association
            content_id UUID REFERENCES college_content(id) ON DELETE SET NULL,

            -- Transfer portal specific
            is_transfer BOOLEAN DEFAULT FALSE NOT NULL,
            transfer_reason TEXT,
            eligibility_remaining INTEGER,

            -- Source and verification
            source VARCHAR(255) NOT NULL,
            verified BOOLEAN DEFAULT FALSE NOT NULL,
            metadata JSONB,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
        """

        # Coaching News Table
        coaching_news_sql = """
        CREATE TABLE coaching_news (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Coach information
            coach_name VARCHAR(200) NOT NULL,
            position_title VARCHAR(100) NOT NULL,
            team_id UUID NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,

            -- Change details
            change_type coaching_change_type NOT NULL,
            effective_date DATE NOT NULL,
            announced_date DATE DEFAULT CURRENT_DATE NOT NULL,

            -- Previous/new positions
            previous_position VARCHAR(200),
            new_position VARCHAR(200),

            -- Contract details
            contract_years INTEGER CHECK (contract_years >= 0),
            salary_amount NUMERIC(12,2) CHECK (salary_amount >= 0),
            contract_details JSONB,

            -- Background
            coaching_background TEXT,
            playing_background TEXT,

            -- Reason and impact
            reason TEXT,
            team_record VARCHAR(20),
            tenure_years INTEGER,

            -- Content association
            content_id UUID REFERENCES college_content(id) ON DELETE SET NULL,

            -- Source and verification
            source VARCHAR(255) NOT NULL,
            verified BOOLEAN DEFAULT FALSE NOT NULL,
            metadata JSONB,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
        """

        tables = [
            college_content_sql,
            injury_reports_sql,
            recruiting_news_sql,
            coaching_news_sql
        ]

        for table_sql in tables:
            await session.execute(text(table_sql))

    async def _create_relationship_tables(self, session: AsyncSession) -> None:
        """Create content relationship tables"""
        logger.info("Creating relationship tables...")

        # Content Team Associations Table
        content_team_associations_sql = """
        CREATE TABLE content_team_associations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content_id UUID NOT NULL REFERENCES college_content(id) ON DELETE CASCADE,
            team_id UUID NOT NULL REFERENCES college_teams(id) ON DELETE CASCADE,
            relevance_score NUMERIC(3,2) DEFAULT 0.5 NOT NULL CHECK (relevance_score >= 0 AND relevance_score <= 1),
            association_type VARCHAR(50) DEFAULT 'general',
            mentioned_players TEXT[],
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

            UNIQUE (content_id, team_id)
        )
        """

        await session.execute(text(content_team_associations_sql))

    async def _create_classification_tables(self, session: AsyncSession) -> None:
        """Create content classification tables"""
        logger.info("Creating classification tables...")

        # Content Classifications Table
        content_classifications_sql = """
        CREATE TABLE content_classifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content_id UUID NOT NULL REFERENCES college_content(id) ON DELETE CASCADE,
            classification_type VARCHAR(50) NOT NULL,
            classification_value VARCHAR(100) NOT NULL,
            confidence_score NUMERIC(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
            classifier_model VARCHAR(100) NOT NULL,
            classification_metadata JSONB,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

            UNIQUE (content_id, classification_type)
        )
        """

        await session.execute(text(content_classifications_sql))

    async def _create_indexes(self, session: AsyncSession) -> None:
        """Create performance indexes"""
        logger.info("Creating indexes...")

        indexes = [
            # College Content indexes
            "CREATE INDEX idx_college_content_teams ON college_content(primary_team_id, secondary_team_id)",
            "CREATE INDEX idx_college_content_players ON college_content(primary_player_id)",
            "CREATE INDEX idx_college_content_type_date ON college_content(content_type, published_at)",
            "CREATE INDEX idx_college_content_search_vector ON college_content USING gin(search_vector)",
            "CREATE INDEX idx_college_content_title_trgm ON college_content USING gin(title gin_trgm_ops)",
            "CREATE INDEX idx_college_content_active ON college_content(is_active, published_at)",
            "CREATE INDEX idx_college_content_featured ON college_content(is_featured, published_at)",

            # Injury Reports indexes
            "CREATE INDEX idx_injury_reports_player ON injury_reports(player_id)",
            "CREATE INDEX idx_injury_reports_team ON injury_reports(team_id)",
            "CREATE INDEX idx_injury_reports_status ON injury_reports(current_status)",
            "CREATE INDEX idx_injury_reports_date ON injury_reports(injury_date)",
            "CREATE INDEX idx_injury_reports_severity ON injury_reports(severity, is_active)",
            "CREATE INDEX idx_injury_reports_active ON injury_reports(is_active, reported_date)",

            # Recruiting News indexes
            "CREATE INDEX idx_recruiting_news_recruit ON recruiting_news(recruit_name)",
            "CREATE INDEX idx_recruiting_news_team ON recruiting_news(team_id)",
            "CREATE INDEX idx_recruiting_news_event_type ON recruiting_news(event_type)",
            "CREATE INDEX idx_recruiting_news_date ON recruiting_news(event_date)",
            "CREATE INDEX idx_recruiting_news_class ON recruiting_news(recruiting_class)",
            "CREATE INDEX idx_recruiting_news_transfer ON recruiting_news(is_transfer, event_type)",
            "CREATE INDEX idx_recruiting_news_verified ON recruiting_news(verified, event_date)",

            # Coaching News indexes
            "CREATE INDEX idx_coaching_news_coach ON coaching_news(coach_name)",
            "CREATE INDEX idx_coaching_news_team ON coaching_news(team_id)",
            "CREATE INDEX idx_coaching_news_change_type ON coaching_news(change_type)",
            "CREATE INDEX idx_coaching_news_date ON coaching_news(effective_date)",
            "CREATE INDEX idx_coaching_news_verified ON coaching_news(verified, announced_date)",

            # Content Team Associations indexes
            "CREATE INDEX idx_content_team_assoc_content ON content_team_associations(content_id)",
            "CREATE INDEX idx_content_team_assoc_team ON content_team_associations(team_id)",
            "CREATE INDEX idx_content_team_assoc_relevance ON content_team_associations(relevance_score)",

            # Content Classifications indexes
            "CREATE INDEX idx_content_class_content ON content_classifications(content_id)",
            "CREATE INDEX idx_content_class_type ON content_classifications(classification_type)",
            "CREATE INDEX idx_content_class_confidence ON content_classifications(confidence_score)",
        ]

        for index_sql in indexes:
            await session.execute(text(index_sql))

    async def _create_search_triggers(self, session: AsyncSession) -> None:
        """Create triggers for maintaining search vectors"""
        logger.info("Creating search triggers...")

        # Function to update search vectors
        search_function_sql = """
        CREATE OR REPLACE FUNCTION update_college_content_search_vector()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(NEW.author, '')), 'D') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.mentioned_players, ' '), '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.mentioned_coaches, ' '), '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'C');

            NEW.updated_at := NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """

        # Trigger for college content
        search_trigger_sql = """
        CREATE TRIGGER trigger_update_college_content_search_vector
            BEFORE INSERT OR UPDATE ON college_content
            FOR EACH ROW
            EXECUTE FUNCTION update_college_content_search_vector();
        """

        await session.execute(text(search_function_sql))
        await session.execute(text(search_trigger_sql))

        # Update timestamp triggers
        timestamp_triggers = [
            """
            CREATE TRIGGER trigger_update_college_content_timestamp
                BEFORE UPDATE ON college_content
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            CREATE TRIGGER trigger_update_injury_reports_timestamp
                BEFORE UPDATE ON injury_reports
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            CREATE TRIGGER trigger_update_recruiting_news_timestamp
                BEFORE UPDATE ON recruiting_news
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            CREATE TRIGGER trigger_update_coaching_news_timestamp
                BEFORE UPDATE ON coaching_news
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            CREATE TRIGGER trigger_update_content_classifications_timestamp
                BEFORE UPDATE ON content_classifications
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """
        ]

        for trigger_sql in timestamp_triggers:
            await session.execute(text(trigger_sql))

    async def _drop_content_tables(self, session: AsyncSession) -> None:
        """Drop content tables in reverse dependency order"""
        logger.info("Dropping content tables...")

        tables_to_drop = [
            "content_classifications",
            "content_team_associations",
            "coaching_news",
            "recruiting_news",
            "injury_reports",
            "college_content"
        ]

        # Drop triggers first
        triggers_to_drop = [
            "trigger_update_college_content_search_vector",
            "trigger_update_college_content_timestamp",
            "trigger_update_injury_reports_timestamp",
            "trigger_update_recruiting_news_timestamp",
            "trigger_update_coaching_news_timestamp",
            "trigger_update_content_classifications_timestamp"
        ]

        for trigger in triggers_to_drop:
            await session.execute(text(f"DROP TRIGGER IF EXISTS {trigger} ON college_content CASCADE"))
            await session.execute(text(f"DROP TRIGGER IF EXISTS {trigger} ON injury_reports CASCADE"))
            await session.execute(text(f"DROP TRIGGER IF EXISTS {trigger} ON recruiting_news CASCADE"))
            await session.execute(text(f"DROP TRIGGER IF EXISTS {trigger} ON coaching_news CASCADE"))
            await session.execute(text(f"DROP TRIGGER IF EXISTS {trigger} ON content_classifications CASCADE"))

        # Drop function
        await session.execute(text("DROP FUNCTION IF EXISTS update_college_content_search_vector() CASCADE"))

        # Drop tables
        for table in tables_to_drop:
            await session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))

    async def _drop_enum_types(self, session: AsyncSession) -> None:
        """Drop custom enum types"""
        logger.info("Dropping enum types...")

        enum_types = [
            "coaching_change_type",
            "recruiting_event_type",
            "injury_severity",
            "injury_type",
            "college_content_type"
        ]

        for enum_type in enum_types:
            await session.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))


async def run_migration():
    """Run the Phase 5 Content Integration migration"""
    migration = Phase5ContentIntegrationMigration()

    async with get_async_session() as session:
        await migration.upgrade(session)
        print("Phase 5 Content Integration migration completed successfully!")


async def run_rollback():
    """Rollback the Phase 5 Content Integration migration"""
    migration = Phase5ContentIntegrationMigration()

    async with get_async_session() as session:
        await migration.downgrade(session)
        print("Phase 5 Content Integration rollback completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(run_rollback())
    else:
        asyncio.run(run_migration())