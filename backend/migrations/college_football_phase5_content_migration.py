"""
College Football Phase 5: Content Integration Migration
Creates football-specific content classification system, injury reports, recruiting news,
coaching updates, depth charts, game previews, and bowl content management

This migration extends the existing content pipeline with football-specific features
while maintaining compatibility with the basketball content infrastructure.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

logger = logging.getLogger(__name__)


class CollegeFootballPhase5ContentMigration:
    """
    College Football Phase 5 migration implementing football content integration.

    Creates:
    - Football-specific content classification system
    - Football injury report tracking with depth chart implications
    - Football recruiting news management
    - Football coaching change tracking
    - Football depth chart update tracking
    - Football game preview system
    - Football bowl and playoff news management
    - Enhanced content categorization for football complexity
    """

    def __init__(self):
        self.migration_name = "College Football Phase 5: Content Integration"
        self.version = "20250921_2200_college_football_phase5_content"

    async def upgrade(self, session: AsyncSession) -> None:
        """
        Apply College Football Phase 5 content integration schema changes
        """
        logger.info(f"Starting {self.migration_name} upgrade...")

        try:
            # Create enum types first
            await self._create_enum_types(session)

            # Create core football content tables
            await self._create_football_content_tables(session)

            # Create football content feature tables
            await self._create_football_feature_tables(session)

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
        Rollback College Football Phase 5 content integration schema changes
        """
        logger.info(f"Starting {self.migration_name} downgrade...")

        try:
            # Drop tables in reverse dependency order
            await self._drop_football_content_tables(session)

            # Drop enum types
            await self._drop_enum_types(session)

            await session.commit()
            logger.info(f"{self.migration_name} downgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.migration_name} downgrade: {str(e)}")
            raise

    async def _create_enum_types(self, session: AsyncSession) -> None:
        """Create custom enum types for football content integration"""
        logger.info("Creating football content enum types...")

        enum_definitions = [
            """
            CREATE TYPE football_content_type AS ENUM (
                'game_preview', 'game_recap', 'game_highlights', 'pregame_analysis', 'postgame_analysis',
                'injury_report', 'injury_update', 'return_from_injury', 'medical_clearance', 'surgery_news',
                'recruiting_news', 'recruiting_commit', 'recruiting_decommit', 'recruiting_visit',
                'recruiting_ranking', 'recruiting_class_update', 'signing_day_news',
                'transfer_portal_entry', 'transfer_commitment', 'transfer_portal_news', 'transfer_portal_update',
                'coaching_news', 'coach_hire', 'coach_fire', 'coach_resignation', 'coach_contract', 'coaching_staff_update',
                'depth_chart_update', 'depth_chart_release', 'position_battle', 'roster_move', 'starting_lineup_change',
                'bowl_selection', 'bowl_news', 'bowl_preview', 'bowl_recap', 'playoff_news', 'playoff_selection', 'playoff_ranking',
                'conference_news', 'conference_realignment', 'season_outlook', 'season_preview', 'season_recap',
                'ranking_news', 'poll_update', 'award_news', 'honors_announcement',
                'academic_news', 'suspension_news', 'eligibility_news', 'dismissal_news',
                'nil_news', 'nil_deal_announcement', 'compliance_news', 'violation_news',
                'facility_news', 'facility_upgrade', 'program_announcement',
                'press_conference', 'interview', 'feature_story', 'breaking_news'
            )
            """,
            """
            CREATE TYPE football_injury_type AS ENUM (
                'concussion', 'neck_injury', 'head_injury',
                'shoulder_injury', 'arm_injury', 'elbow_injury', 'wrist_injury', 'hand_injury', 'finger_injury',
                'rib_injury', 'chest_injury', 'back_injury', 'abdominal_injury', 'core_injury', 'spine_injury',
                'hip_injury', 'groin_injury', 'thigh_injury', 'hamstring_injury', 'quadriceps_injury',
                'knee_injury', 'shin_injury', 'calf_injury', 'ankle_injury', 'foot_injury', 'toe_injury',
                'acl_tear', 'mcl_tear', 'meniscus_tear', 'achilles_injury', 'turf_toe',
                'illness', 'undisclosed', 'other'
            )
            """,
            """
            CREATE TYPE football_injury_severity AS ENUM (
                'minor', 'moderate', 'major', 'severe', 'season_ending', 'career_ending'
            )
            """,
            """
            CREATE TYPE football_depth_chart_status AS ENUM (
                'starter', 'backup', 'third_string', 'fourth_string', 'special_teams',
                'redshirt', 'injured_reserve', 'suspended', 'dismissed', 'transfer_portal'
            )
            """,
            """
            CREATE TYPE football_coaching_change_type AS ENUM (
                'hire', 'promotion', 'lateral_move', 'fire', 'resignation', 'retirement', 'mutual_separation',
                'contract_extension', 'contract_renewal', 'salary_increase',
                'role_change', 'additional_duties', 'leave_of_absence', 'suspension'
            )
            """,
            """
            CREATE TYPE football_recruiting_event_type AS ENUM (
                'commit', 'decommit', 'recommit', 'flip',
                'transfer_entry', 'transfer_commitment', 'transfer_withdrawal',
                'official_visit', 'unofficial_visit', 'junior_day_visit', 'camp_visit',
                'offer_extended', 'offer_accepted', 'offer_declined', 'offer_rescinded',
                'signed_loi', 'enrolled', 'ranking_update', 'star_rating_change'
            )
            """,
            """
            CREATE TYPE football_bowl_news_type AS ENUM (
                'bowl_selection', 'bowl_announcement', 'bowl_preview', 'bowl_prediction', 'bowl_matchup_analysis',
                'bowl_ticket_info', 'bowl_travel_info', 'bowl_history', 'bowl_tradition',
                'playoff_selection', 'playoff_ranking', 'playoff_seeding', 'playoff_schedule', 'championship_news'
            )
            """
        ]

        for enum_def in enum_definitions:
            await session.execute(text(enum_def))

    async def _create_football_content_tables(self, session: AsyncSession) -> None:
        """Create core football content tables"""
        logger.info("Creating football content tables...")

        # Main football content table
        football_content_table = """
        CREATE TABLE football_content (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            college_content_id UUID REFERENCES college_content(id) ON DELETE CASCADE,

            -- Content identification
            title VARCHAR(500) NOT NULL,
            summary TEXT,
            content TEXT,

            -- Football-specific classification
            content_type football_content_type NOT NULL,

            -- Team associations
            primary_team_id UUID REFERENCES football_teams(id) ON DELETE CASCADE,
            secondary_team_id UUID REFERENCES football_teams(id) ON DELETE CASCADE,

            -- Player association
            primary_player_id UUID REFERENCES football_players(id) ON DELETE CASCADE,

            -- Game associations
            game_id UUID REFERENCES football_games(id) ON DELETE CASCADE,
            bowl_game_id UUID REFERENCES bowl_games(id) ON DELETE CASCADE,

            -- Content metadata
            author VARCHAR(255),
            source VARCHAR(255) NOT NULL,
            published_at TIMESTAMPTZ NOT NULL,
            url VARCHAR(1000),
            image_url VARCHAR(1000),

            -- Content analysis
            word_count INTEGER CHECK (word_count >= 0),
            reading_time_minutes INTEGER CHECK (reading_time_minutes >= 0),
            sentiment_score NUMERIC(3,2),
            relevance_score NUMERIC(3,2) DEFAULT 0.5 NOT NULL CHECK (relevance_score >= 0 AND relevance_score <= 1),
            engagement_score NUMERIC(10,2) CHECK (engagement_score >= 0),

            -- Football-specific content details
            position_groups_mentioned TEXT[],
            recruiting_class_year INTEGER,
            coaching_position_mentioned VARCHAR(100),
            injury_status_impact VARCHAR(100),

            -- Search and categorization
            search_vector TSVECTOR,
            tags TEXT[],
            mentioned_players TEXT[],
            mentioned_coaches TEXT[],
            mentioned_recruits TEXT[],

            -- Metadata
            external_id VARCHAR(255),
            content_metadata JSONB,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            is_featured BOOLEAN DEFAULT FALSE NOT NULL,
            is_breaking_news BOOLEAN DEFAULT FALSE NOT NULL,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
        """
        await session.execute(text(football_content_table))

    async def _create_football_feature_tables(self, session: AsyncSession) -> None:
        """Create football-specific feature tables"""
        logger.info("Creating football feature tables...")

        # Football injury reports table
        injury_reports_table = """
        CREATE TABLE football_injury_reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Player and team
            player_id UUID NOT NULL REFERENCES football_players(id) ON DELETE CASCADE,
            team_id UUID NOT NULL REFERENCES football_teams(id) ON DELETE CASCADE,

            -- Position impact
            position_affected football_position NOT NULL,
            position_group_affected football_position_group NOT NULL,

            -- Injury details
            injury_type football_injury_type NOT NULL,
            injury_description TEXT NOT NULL,
            severity football_injury_severity NOT NULL,

            -- Timeline
            injury_date DATE NOT NULL,
            reported_date DATE DEFAULT CURRENT_DATE NOT NULL,
            expected_return_date DATE,
            actual_return_date DATE,

            -- Status tracking
            current_status player_eligibility_status DEFAULT 'injured' NOT NULL,
            depth_chart_status football_depth_chart_status DEFAULT 'injured_reserve' NOT NULL,
            games_missed INTEGER DEFAULT 0 NOT NULL CHECK (games_missed >= 0),
            practices_missed INTEGER,

            -- Football-specific details
            requires_surgery BOOLEAN DEFAULT FALSE NOT NULL,
            surgery_date DATE,
            is_contact_injury BOOLEAN DEFAULT FALSE NOT NULL,
            occurred_during_game BOOLEAN DEFAULT TRUE NOT NULL,

            -- Impact assessment
            replacement_player_id UUID REFERENCES football_players(id) ON DELETE SET NULL,
            depth_chart_impact TEXT,
            recruiting_impact TEXT,

            -- Recovery tracking
            recovery_notes TEXT,
            recovery_milestones JSONB,

            -- Content association
            content_id UUID REFERENCES football_content(id) ON DELETE SET NULL,

            -- Medical metadata
            medical_metadata JSONB,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

            CONSTRAINT uq_football_player_injury_date_type UNIQUE (player_id, injury_date, injury_type)
        )
        """
        await session.execute(text(injury_reports_table))

        # Football recruiting news table
        recruiting_news_table = """
        CREATE TABLE football_recruiting_news (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Recruit information
            recruit_name VARCHAR(200) NOT NULL,
            recruit_position football_position NOT NULL,
            recruit_position_group football_position_group NOT NULL,
            recruit_height VARCHAR(10),
            recruit_weight INTEGER,
            forty_yard_dash_time NUMERIC(3,2),

            -- Academic information
            high_school VARCHAR(200),
            hometown VARCHAR(100),
            home_state VARCHAR(50),
            recruiting_class INTEGER NOT NULL,

            -- Event details
            event_type football_recruiting_event_type NOT NULL,
            team_id UUID REFERENCES football_teams(id) ON DELETE CASCADE,
            previous_team_id UUID REFERENCES football_teams(id) ON DELETE CASCADE,
            event_date DATE NOT NULL,

            -- Ratings and rankings
            star_rating INTEGER CHECK (star_rating >= 2 AND star_rating <= 5),
            composite_rating NUMERIC(4,3),
            national_ranking INTEGER,
            position_ranking INTEGER,
            state_ranking INTEGER,

            -- Football-specific metrics
            projected_impact VARCHAR(50),
            nfl_projection VARCHAR(50),

            -- Additional details
            scholarship_type VARCHAR(50),
            commitment_level VARCHAR(50),
            other_offers TEXT[],
            top_schools TEXT[],
            visit_details JSONB,

            -- Content association
            content_id UUID REFERENCES football_content(id) ON DELETE SET NULL,

            -- Transfer portal specific
            is_transfer BOOLEAN DEFAULT FALSE NOT NULL,
            transfer_reason TEXT,
            eligibility_remaining INTEGER,
            has_redshirt_available BOOLEAN DEFAULT TRUE NOT NULL,

            -- Decision factors
            decision_factors TEXT[],
            family_influence TEXT,

            -- Source and verification
            source VARCHAR(255) NOT NULL,
            verified BOOLEAN DEFAULT FALSE NOT NULL,
            recruiting_metadata JSONB,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
        """
        await session.execute(text(recruiting_news_table))

        # Football coaching news table
        coaching_news_table = """
        CREATE TABLE football_coaching_news (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Coach information
            coach_name VARCHAR(200) NOT NULL,
            position_title VARCHAR(100) NOT NULL,
            coaching_position coaching_position NOT NULL,
            coaching_level coaching_level NOT NULL,
            team_id UUID NOT NULL REFERENCES football_teams(id) ON DELETE CASCADE,

            -- Change details
            change_type football_coaching_change_type NOT NULL,
            effective_date DATE NOT NULL,
            announced_date DATE DEFAULT CURRENT_DATE NOT NULL,

            -- Previous/new positions
            previous_position VARCHAR(200),
            previous_team VARCHAR(200),
            new_position VARCHAR(200),
            new_team VARCHAR(200),

            -- Contract details
            contract_years INTEGER CHECK (contract_years >= 0),
            salary_amount NUMERIC(12,2) CHECK (salary_amount >= 0),
            total_contract_value NUMERIC(15,2),
            buyout_amount NUMERIC(12,2),
            contract_details JSONB,

            -- Background
            coaching_background TEXT,
            playing_background TEXT,
            education_background TEXT,

            -- Specializations
            recruiting_areas TEXT[],
            position_groups_coached TEXT[],
            specialties TEXT[],

            -- Reason and impact
            reason TEXT,
            team_record VARCHAR(20),
            tenure_years INTEGER,
            recruiting_impact TEXT,

            -- Performance metrics
            wins_losses_record VARCHAR(20),
            bowl_record VARCHAR(20),
            recruiting_success TEXT,

            -- Content association
            content_id UUID REFERENCES football_content(id) ON DELETE SET NULL,

            -- Source and verification
            source VARCHAR(255) NOT NULL,
            verified BOOLEAN DEFAULT FALSE NOT NULL,
            coaching_metadata JSONB,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
        """
        await session.execute(text(coaching_news_table))

        # Football depth chart updates table
        depth_chart_updates_table = """
        CREATE TABLE football_depth_chart_updates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Team and player
            team_id UUID NOT NULL REFERENCES football_teams(id) ON DELETE CASCADE,
            player_id UUID NOT NULL REFERENCES football_players(id) ON DELETE CASCADE,

            -- Position details
            position football_position NOT NULL,
            position_group football_position_group NOT NULL,

            -- Depth chart status
            depth_chart_status football_depth_chart_status NOT NULL,
            previous_status football_depth_chart_status,
            depth_order INTEGER,
            previous_depth_order INTEGER,

            -- Update details
            update_date DATE DEFAULT CURRENT_DATE NOT NULL,
            update_type VARCHAR(50) NOT NULL,
            reason TEXT,

            -- Position battle details
            is_position_battle BOOLEAN DEFAULT FALSE NOT NULL,
            competing_players TEXT[],
            battle_status VARCHAR(100),

            -- Performance impact
            expected_playing_time VARCHAR(50),
            impact_on_gameplan TEXT,

            -- Special circumstances
            is_injury_related BOOLEAN DEFAULT FALSE NOT NULL,
            is_disciplinary BOOLEAN DEFAULT FALSE NOT NULL,
            is_academic_related BOOLEAN DEFAULT FALSE NOT NULL,
            is_performance_based BOOLEAN DEFAULT FALSE NOT NULL,

            -- Timeline expectations
            expected_duration VARCHAR(100),
            review_date DATE,

            -- Content association
            content_id UUID REFERENCES football_content(id) ON DELETE SET NULL,

            -- Metadata
            update_metadata JSONB,
            is_official BOOLEAN DEFAULT TRUE NOT NULL,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

            CONSTRAINT uq_football_depth_chart_update UNIQUE (team_id, player_id, position, update_date)
        )
        """
        await session.execute(text(depth_chart_updates_table))

        # Football game previews table
        game_previews_table = """
        CREATE TABLE football_game_previews (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Game reference
            game_id UUID NOT NULL REFERENCES football_games(id) ON DELETE CASCADE,
            home_team_id UUID NOT NULL REFERENCES football_teams(id) ON DELETE CASCADE,
            away_team_id UUID NOT NULL REFERENCES football_teams(id) ON DELETE CASCADE,

            -- Game details
            game_date TIMESTAMPTZ NOT NULL,
            venue VARCHAR(200),
            tv_coverage VARCHAR(100),

            -- Betting and predictions
            point_spread NUMERIC(4,1),
            over_under NUMERIC(4,1),
            predicted_winner UUID REFERENCES football_teams(id) ON DELETE SET NULL,
            confidence_level VARCHAR(50),

            -- Matchup analysis
            key_matchups TEXT[],
            home_team_strengths TEXT[],
            home_team_weaknesses TEXT[],
            away_team_strengths TEXT[],
            away_team_weaknesses TEXT[],

            -- Weather and conditions
            weather_forecast VARCHAR(200),
            field_conditions VARCHAR(100),

            -- Storylines
            major_storylines TEXT[],
            players_to_watch TEXT[],
            injury_concerns TEXT[],

            -- Historical context
            series_record VARCHAR(20),
            recent_meetings JSONB,

            -- Stakes and implications
            conference_implications TEXT,
            playoff_implications TEXT,
            bowl_implications TEXT,
            ranking_implications TEXT,

            -- Content association
            content_id UUID NOT NULL REFERENCES football_content(id) ON DELETE CASCADE,

            -- Metadata
            preview_metadata JSONB,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

            CONSTRAINT uq_football_game_preview UNIQUE (game_id, content_id)
        )
        """
        await session.execute(text(game_previews_table))

        # Football bowl news table
        bowl_news_table = """
        CREATE TABLE football_bowl_news (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Team and bowl
            team_id UUID NOT NULL REFERENCES football_teams(id) ON DELETE CASCADE,
            bowl_game_id UUID REFERENCES bowl_games(id) ON DELETE CASCADE,
            opponent_team_id UUID REFERENCES football_teams(id) ON DELETE CASCADE,

            -- News details
            news_type football_bowl_news_type NOT NULL,
            announcement_date DATE DEFAULT CURRENT_DATE NOT NULL,

            -- Selection details
            bowl_tier bowl_tier,
            selection_reason TEXT,
            final_record VARCHAR(20),
            conference_record VARCHAR(20),

            -- Playoff details
            playoff_round playoff_round,
            playoff_seed INTEGER,
            ranking_at_selection INTEGER,

            -- Bowl game details
            bowl_location VARCHAR(200),
            bowl_date DATE,
            bowl_payout NUMERIC(12,2),

            -- Historical context
            last_bowl_appearance VARCHAR(100),
            bowl_history JSONB,

            -- Ticket and travel info
            ticket_information JSONB,
            travel_details JSONB,

            -- Preparation details
            opt_outs TEXT[],
            key_storylines TEXT[],
            coaching_changes TEXT[],

            -- Content association
            content_id UUID REFERENCES football_content(id) ON DELETE SET NULL,

            -- Source and verification
            source VARCHAR(255) NOT NULL,
            verified BOOLEAN DEFAULT FALSE NOT NULL,
            bowl_metadata JSONB,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
        )
        """
        await session.execute(text(bowl_news_table))

    async def _create_indexes(self, session: AsyncSession) -> None:
        """Create indexes for performance optimization"""
        logger.info("Creating indexes for football content tables...")

        indexes = [
            # Football content indexes
            "CREATE INDEX idx_football_content_teams ON football_content(primary_team_id, secondary_team_id)",
            "CREATE INDEX idx_football_content_players ON football_content(primary_player_id)",
            "CREATE INDEX idx_football_content_type_date ON football_content(content_type, published_at)",
            "CREATE INDEX idx_football_content_search_vector ON football_content USING GIN(search_vector)",
            "CREATE INDEX idx_football_content_title_trgm ON football_content USING GIN(title gin_trgm_ops)",
            "CREATE INDEX idx_football_content_game ON football_content(game_id)",
            "CREATE INDEX idx_football_content_bowl ON football_content(bowl_game_id)",

            # Injury reports indexes
            "CREATE INDEX idx_football_injury_reports_player ON football_injury_reports(player_id)",
            "CREATE INDEX idx_football_injury_reports_team ON football_injury_reports(team_id)",
            "CREATE INDEX idx_football_injury_reports_status ON football_injury_reports(current_status)",
            "CREATE INDEX idx_football_injury_reports_date ON football_injury_reports(injury_date)",
            "CREATE INDEX idx_football_injury_reports_position ON football_injury_reports(position_affected)",

            # Recruiting news indexes
            "CREATE INDEX idx_football_recruiting_news_recruit ON football_recruiting_news(recruit_name)",
            "CREATE INDEX idx_football_recruiting_news_team ON football_recruiting_news(team_id)",
            "CREATE INDEX idx_football_recruiting_news_event_type ON football_recruiting_news(event_type)",
            "CREATE INDEX idx_football_recruiting_news_date ON football_recruiting_news(event_date)",
            "CREATE INDEX idx_football_recruiting_news_class ON football_recruiting_news(recruiting_class)",
            "CREATE INDEX idx_football_recruiting_news_position ON football_recruiting_news(recruit_position)",

            # Coaching news indexes
            "CREATE INDEX idx_football_coaching_news_coach ON football_coaching_news(coach_name)",
            "CREATE INDEX idx_football_coaching_news_team ON football_coaching_news(team_id)",
            "CREATE INDEX idx_football_coaching_news_change_type ON football_coaching_news(change_type)",
            "CREATE INDEX idx_football_coaching_news_date ON football_coaching_news(effective_date)",
            "CREATE INDEX idx_football_coaching_news_position ON football_coaching_news(position_title)",

            # Depth chart updates indexes
            "CREATE INDEX idx_football_depth_chart_team ON football_depth_chart_updates(team_id)",
            "CREATE INDEX idx_football_depth_chart_player ON football_depth_chart_updates(player_id)",
            "CREATE INDEX idx_football_depth_chart_position ON football_depth_chart_updates(position)",
            "CREATE INDEX idx_football_depth_chart_date ON football_depth_chart_updates(update_date)",
            "CREATE INDEX idx_football_depth_chart_status ON football_depth_chart_updates(depth_chart_status)",

            # Game previews indexes
            "CREATE INDEX idx_football_game_previews_game ON football_game_previews(game_id)",
            "CREATE INDEX idx_football_game_previews_home_team ON football_game_previews(home_team_id)",
            "CREATE INDEX idx_football_game_previews_away_team ON football_game_previews(away_team_id)",
            "CREATE INDEX idx_football_game_previews_date ON football_game_previews(game_date)",

            # Bowl news indexes
            "CREATE INDEX idx_football_bowl_news_team ON football_bowl_news(team_id)",
            "CREATE INDEX idx_football_bowl_news_bowl ON football_bowl_news(bowl_game_id)",
            "CREATE INDEX idx_football_bowl_news_type ON football_bowl_news(news_type)",
            "CREATE INDEX idx_football_bowl_news_date ON football_bowl_news(announcement_date)"
        ]

        for index in indexes:
            await session.execute(text(index))

    async def _create_search_triggers(self, session: AsyncSession) -> None:
        """Create triggers for automatic search vector updates"""
        logger.info("Creating search vector triggers...")

        # Function to update search vectors for football content
        search_function = """
        CREATE OR REPLACE FUNCTION update_football_content_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.mentioned_players, ' '), '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.mentioned_coaches, ' '), '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.mentioned_recruits, ' '), '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        await session.execute(text(search_function))

        # Trigger for football content
        search_trigger = """
        CREATE TRIGGER update_football_content_search_vector_trigger
            BEFORE INSERT OR UPDATE ON football_content
            FOR EACH ROW EXECUTE FUNCTION update_football_content_search_vector();
        """
        await session.execute(text(search_trigger))

        # Update trigger for timestamps
        update_trigger_function = """
        CREATE OR REPLACE FUNCTION update_football_content_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        await session.execute(text(update_trigger_function))

        # Apply update triggers to all tables
        tables = [
            'football_content',
            'football_injury_reports',
            'football_recruiting_news',
            'football_coaching_news',
            'football_depth_chart_updates',
            'football_game_previews',
            'football_bowl_news'
        ]

        for table in tables:
            trigger = f"""
            CREATE TRIGGER update_{table}_timestamp_trigger
                BEFORE UPDATE ON {table}
                FOR EACH ROW EXECUTE FUNCTION update_football_content_timestamp();
            """
            await session.execute(text(trigger))

    async def _drop_football_content_tables(self, session: AsyncSession) -> None:
        """Drop football content tables in reverse dependency order"""
        logger.info("Dropping football content tables...")

        tables = [
            'football_bowl_news',
            'football_game_previews',
            'football_depth_chart_updates',
            'football_coaching_news',
            'football_recruiting_news',
            'football_injury_reports',
            'football_content'
        ]

        for table in tables:
            await session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))

    async def _drop_enum_types(self, session: AsyncSession) -> None:
        """Drop custom enum types"""
        logger.info("Dropping football content enum types...")

        enums = [
            'football_bowl_news_type',
            'football_recruiting_event_type',
            'football_coaching_change_type',
            'football_depth_chart_status',
            'football_injury_severity',
            'football_injury_type',
            'football_content_type'
        ]

        for enum_type in enums:
            await session.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))


async def run_migration():
    """Run the College Football Phase 5 content migration"""
    migration = CollegeFootballPhase5ContentMigration()

    async for session in get_async_session():
        try:
            await migration.upgrade(session)
            logger.info("College Football Phase 5 content migration completed successfully")
            break
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise


async def run_rollback():
    """Rollback the College Football Phase 5 content migration"""
    migration = CollegeFootballPhase5ContentMigration()

    async for session in get_async_session():
        try:
            await migration.downgrade(session)
            logger.info("College Football Phase 5 content migration rollback completed successfully")
            break
        except Exception as e:
            logger.error(f"Migration rollback failed: {str(e)}")
            raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(run_rollback())
    else:
        asyncio.run(run_migration())