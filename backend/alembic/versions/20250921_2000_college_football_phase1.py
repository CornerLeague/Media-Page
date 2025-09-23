"""College Football Phase 1: Foundation Tables

Revision ID: 20250921_2000_college_football_phase1
Revises: 20250921_1815_phase3_seed_data
Create Date: 2025-09-21 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250921_2000_college_football_phase1'
down_revision: Union[str, None] = '20250921_1815_phase3_seed_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create college football Phase 1 tables"""

    # Create football-specific enums
    football_position_enum = postgresql.ENUM(
        'quarterback', 'running_back', 'fullback', 'wide_receiver', 'tight_end',
        'left_tackle', 'left_guard', 'center', 'right_guard', 'right_tackle',
        'defensive_end', 'defensive_tackle', 'nose_tackle', 'outside_linebacker',
        'middle_linebacker', 'inside_linebacker', 'cornerback', 'safety',
        'free_safety', 'strong_safety', 'kicker', 'punter', 'long_snapper',
        'return_specialist', 'offensive_line', 'defensive_line', 'linebacker',
        'defensive_back',
        name='footballposition',
        create_type=False
    )
    football_position_enum.create(op.get_bind(), checkfirst=True)

    football_position_group_enum = postgresql.ENUM(
        'quarterback', 'running_back', 'wide_receiver', 'tight_end',
        'offensive_line', 'defensive_line', 'linebacker', 'defensive_back',
        'special_teams',
        name='footballpositiongroup',
        create_type=False
    )
    football_position_group_enum.create(op.get_bind(), checkfirst=True)

    football_play_type_enum = postgresql.ENUM(
        'rush', 'pass', 'option', 'play_action', 'screen', 'draw', 'wildcat',
        'punt', 'field_goal', 'extra_point', 'kickoff', 'punt_return',
        'kickoff_return', 'fake_punt', 'fake_field_goal', 'onside_kick',
        'blitz', 'coverage', 'run_defense', 'penalty', 'timeout',
        'kneel_down', 'spike', 'two_point_conversion',
        name='footballplaytype',
        create_type=False
    )
    football_play_type_enum.create(op.get_bind(), checkfirst=True)

    football_game_context_enum = postgresql.ENUM(
        'first_down', 'second_down', 'third_down', 'fourth_down',
        'red_zone', 'goal_line', 'two_minute_warning', 'overtime',
        'garbage_time', 'clutch_time', 'goal_to_go', 'short_yardage',
        'long_yardage',
        name='footballgamecontext',
        create_type=False
    )
    football_game_context_enum.create(op.get_bind(), checkfirst=True)

    football_weather_condition_enum = postgresql.ENUM(
        'clear', 'partly_cloudy', 'cloudy', 'light_rain', 'heavy_rain',
        'light_snow', 'heavy_snow', 'wind', 'fog', 'cold', 'hot',
        'humid', 'dome', 'unknown',
        name='footballweathercondition',
        create_type=False
    )
    football_weather_condition_enum.create(op.get_bind(), checkfirst=True)

    football_formation_enum = postgresql.ENUM(
        'i_formation', 'shotgun', 'pistol', 'wildcat', 'spread',
        'pro_set', 'single_back', 'empty_backfield', 'jumbo',
        '4_3', '3_4', '4_2_5', '3_3_5', '6_1', '5_2',
        'goal_line_defense', 'prevent', 'dime', 'quarter',
        name='footballformation',
        create_type=False
    )
    football_formation_enum.create(op.get_bind(), checkfirst=True)

    bowl_game_type_enum = postgresql.ENUM(
        'college_football_playoff', 'new_years_six', 'major_bowl',
        'minor_bowl', 'conference_championship', 'national_championship',
        name='bowlgametype',
        create_type=False
    )
    bowl_game_type_enum.create(op.get_bind(), checkfirst=True)

    football_season_type_enum = postgresql.ENUM(
        'regular_season', 'conference_championship', 'bowl_season',
        'playoff', 'spring_practice', 'fall_practice', 'recruiting',
        'transfer_portal',
        name='footballseasontype',
        create_type=False
    )
    football_season_type_enum.create(op.get_bind(), checkfirst=True)

    recruiting_class_enum = postgresql.ENUM(
        'freshman', 'redshirt_freshman', 'transfer', 'graduate_transfer',
        'juco_transfer',
        name='recruitingclass',
        create_type=False
    )
    recruiting_class_enum.create(op.get_bind(), checkfirst=True)

    scholarship_type_enum = postgresql.ENUM(
        'full_scholarship', 'partial_scholarship', 'walk_on',
        'preferred_walk_on', 'grey_shirt', 'blue_shirt',
        name='scholarshiptype',
        create_type=False
    )
    scholarship_type_enum.create(op.get_bind(), checkfirst=True)

    football_ranking_system_enum = postgresql.ENUM(
        'ap_poll', 'coaches_poll', 'cfp_ranking', 'bcs', 'sagarin',
        'massey', 'fpi', 'sp_plus', 'pff', 'recruiting_ranking',
        name='footballrankingsystem',
        create_type=False
    )
    football_ranking_system_enum.create(op.get_bind(), checkfirst=True)

    # Create football_teams table
    op.create_table(
        'football_teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('college_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stadium_name', sa.String(length=200), nullable=True),
        sa.Column('stadium_capacity', sa.Integer(), nullable=True),
        sa.Column('field_type', sa.String(length=50), nullable=True),
        sa.Column('head_coach', sa.String(length=100), nullable=True),
        sa.Column('offensive_coordinator', sa.String(length=100), nullable=True),
        sa.Column('defensive_coordinator', sa.String(length=100), nullable=True),
        sa.Column('coach_since_year', sa.Integer(), nullable=True),
        sa.Column('national_championships', sa.Integer(), nullable=False, default=0),
        sa.Column('bowl_appearances', sa.Integer(), nullable=False, default=0),
        sa.Column('bowl_wins', sa.Integer(), nullable=False, default=0),
        sa.Column('playoff_appearances', sa.Integer(), nullable=False, default=0),
        sa.Column('current_record_wins', sa.Integer(), nullable=False, default=0),
        sa.Column('current_record_losses', sa.Integer(), nullable=False, default=0),
        sa.Column('conference_record_wins', sa.Integer(), nullable=False, default=0),
        sa.Column('conference_record_losses', sa.Integer(), nullable=False, default=0),
        sa.Column('ap_poll_rank', sa.Integer(), nullable=True),
        sa.Column('coaches_poll_rank', sa.Integer(), nullable=True),
        sa.Column('cfp_ranking', sa.Integer(), nullable=True),
        sa.Column('offensive_scheme', sa.String(length=100), nullable=True),
        sa.Column('defensive_scheme', sa.String(length=100), nullable=True),
        sa.Column('scholarship_count', sa.Integer(), nullable=False, default=85),
        sa.Column('roster_size', sa.Integer(), nullable=False, default=0),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('espn_team_id', sa.String(length=100), nullable=True),
        sa.Column('cfb_data_id', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['college_team_id'], ['college_teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('college_team_id', name='uq_football_teams_college_team')
    )

    # Create indexes for football_teams
    op.create_index('idx_football_teams_college_team_id', 'football_teams', ['college_team_id'])
    op.create_index('idx_football_teams_external_id', 'football_teams', ['external_id'])
    op.create_index('idx_football_teams_espn_id', 'football_teams', ['espn_team_id'])
    op.create_index('idx_football_teams_cfb_data_id', 'football_teams', ['cfb_data_id'])
    op.create_index('idx_football_teams_rankings', 'football_teams', ['ap_poll_rank', 'coaches_poll_rank', 'cfp_ranking'])
    op.create_index('idx_football_teams_active', 'football_teams', ['is_active'])

    # Create football_players table
    op.create_table(
        'football_players',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('jersey_number', sa.Integer(), nullable=True),
        sa.Column('primary_position', football_position_enum, nullable=False),
        sa.Column('secondary_position', football_position_enum, nullable=True),
        sa.Column('position_group', football_position_group_enum, nullable=False),
        sa.Column('height_inches', sa.Integer(), nullable=True),
        sa.Column('weight_pounds', sa.Integer(), nullable=True),
        sa.Column('forty_yard_dash', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('bench_press', sa.Integer(), nullable=True),
        sa.Column('vertical_jump', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('hometown', sa.String(length=100), nullable=True),
        sa.Column('home_state', sa.String(length=50), nullable=True),
        sa.Column('home_country', sa.String(length=50), nullable=True, default='USA'),
        sa.Column('high_school', sa.String(length=200), nullable=True),
        sa.Column('junior_college', sa.String(length=200), nullable=True),
        sa.Column('previous_college', sa.String(length=200), nullable=True),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_class', sa.Enum('FRESHMAN', 'SOPHOMORE', 'JUNIOR', 'SENIOR', 'GRADUATE', 'REDSHIRT_FRESHMAN', 'REDSHIRT_SOPHOMORE', 'REDSHIRT_JUNIOR', 'REDSHIRT_SENIOR', name='playerclass'), nullable=False),
        sa.Column('eligibility_status', sa.Enum('ELIGIBLE', 'INELIGIBLE', 'REDSHIRT', 'MEDICAL_REDSHIRT', 'TRANSFER_PORTAL', 'GRADUATE_TRANSFER', 'SUSPENDED', 'INJURED', name='playereligibilitystatus'), nullable=False, default='ELIGIBLE'),
        sa.Column('years_of_eligibility_remaining', sa.Integer(), nullable=False, default=4),
        sa.Column('scholarship_type', scholarship_type_enum, nullable=False, default='walk_on'),
        sa.Column('scholarship_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('is_transfer', sa.Boolean(), nullable=False, default=False),
        sa.Column('transfer_from_college_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('transfer_year', sa.Integer(), nullable=True),
        sa.Column('is_juco_transfer', sa.Boolean(), nullable=False, default=False),
        sa.Column('recruiting_class_year', sa.Integer(), nullable=True),
        sa.Column('recruiting_stars', sa.Integer(), nullable=True),
        sa.Column('recruiting_rank_national', sa.Integer(), nullable=True),
        sa.Column('recruiting_rank_position', sa.Integer(), nullable=True),
        sa.Column('recruiting_rank_state', sa.Integer(), nullable=True),
        sa.Column('nfl_draft_eligible', sa.Boolean(), nullable=False, default=False),
        sa.Column('nfl_draft_year', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('espn_player_id', sa.String(length=100), nullable=True),
        sa.Column('cfb_data_id', sa.String(length=100), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('injury_status', sa.String(length=200), nullable=True),
        sa.Column('is_suspended', sa.Boolean(), nullable=False, default=False),
        sa.Column('suspension_details', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transfer_from_college_id'], ['colleges.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'jersey_number', 'academic_year_id', name='uq_football_players_team_jersey_year')
    )

    # Create indexes for football_players
    op.create_index('idx_football_players_team_id', 'football_players', ['team_id'])
    op.create_index('idx_football_players_academic_year_id', 'football_players', ['academic_year_id'])
    op.create_index('idx_football_players_full_name', 'football_players', ['full_name'])
    op.create_index('idx_football_players_last_name', 'football_players', ['last_name'])
    op.create_index('idx_football_players_jersey_number', 'football_players', ['jersey_number'])
    op.create_index('idx_football_players_position', 'football_players', ['primary_position'])
    op.create_index('idx_football_players_position_group', 'football_players', ['position_group'])
    op.create_index('idx_football_players_class', 'football_players', ['player_class'])
    op.create_index('idx_football_players_eligibility', 'football_players', ['eligibility_status'])
    op.create_index('idx_football_players_scholarship', 'football_players', ['scholarship_type'])
    op.create_index('idx_football_players_transfer', 'football_players', ['is_transfer'])
    op.create_index('idx_football_players_active', 'football_players', ['is_active'])
    op.create_index('idx_football_players_external_id', 'football_players', ['external_id'])
    op.create_index('idx_football_players_espn_id', 'football_players', ['espn_player_id'])
    op.create_index('idx_football_players_cfb_data_id', 'football_players', ['cfb_data_id'])
    op.create_index('idx_football_players_team_jersey', 'football_players', ['team_id', 'jersey_number'])

    # Create football_games table
    op.create_table(
        'football_games',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('game_date', sa.Date(), nullable=False),
        sa.Column('kickoff_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('week_number', sa.Integer(), nullable=True),
        sa.Column('season_type', football_season_type_enum, nullable=False, default='regular_season'),
        sa.Column('bowl_game_type', bowl_game_type_enum, nullable=True),
        sa.Column('bowl_name', sa.String(length=200), nullable=True),
        sa.Column('is_conference_game', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_rivalry_game', sa.Boolean(), nullable=False, default=False),
        sa.Column('rivalry_name', sa.String(length=200), nullable=True),
        sa.Column('venue_name', sa.String(length=200), nullable=True),
        sa.Column('venue_city', sa.String(length=100), nullable=True),
        sa.Column('venue_state', sa.String(length=50), nullable=True),
        sa.Column('is_neutral_site', sa.Boolean(), nullable=False, default=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'LIVE', 'FINAL', 'POSTPONED', 'CANCELLED', name='gamestatus'), nullable=False, default='SCHEDULED'),
        sa.Column('home_team_score', sa.Integer(), nullable=True),
        sa.Column('away_team_score', sa.Integer(), nullable=True),
        sa.Column('weather_condition', football_weather_condition_enum, nullable=True),
        sa.Column('temperature', sa.Integer(), nullable=True),
        sa.Column('wind_speed', sa.Integer(), nullable=True),
        sa.Column('precipitation', sa.String(length=100), nullable=True),
        sa.Column('attendance', sa.Integer(), nullable=True),
        sa.Column('tv_network', sa.String(length=100), nullable=True),
        sa.Column('broadcast_time', sa.String(length=50), nullable=True),
        sa.Column('game_importance', sa.String(length=50), nullable=True),
        sa.Column('playoff_implications', sa.Text(), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('espn_game_id', sa.String(length=100), nullable=True),
        sa.Column('cfb_data_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['home_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['away_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('home_team_id', 'away_team_id', 'game_date', name='uq_football_games_teams_date')
    )

    # Create indexes for football_games
    op.create_index('idx_football_games_home_team_id', 'football_games', ['home_team_id'])
    op.create_index('idx_football_games_away_team_id', 'football_games', ['away_team_id'])
    op.create_index('idx_football_games_academic_year_id', 'football_games', ['academic_year_id'])
    op.create_index('idx_football_games_season_id', 'football_games', ['season_id'])
    op.create_index('idx_football_games_date', 'football_games', ['game_date'])
    op.create_index('idx_football_games_week', 'football_games', ['week_number'])
    op.create_index('idx_football_games_status', 'football_games', ['status'])
    op.create_index('idx_football_games_season_type', 'football_games', ['season_type'])
    op.create_index('idx_football_games_conference', 'football_games', ['is_conference_game'])
    op.create_index('idx_football_games_bowl', 'football_games', ['bowl_game_type'])
    op.create_index('idx_football_games_external_id', 'football_games', ['external_id'])
    op.create_index('idx_football_games_espn_id', 'football_games', ['espn_game_id'])
    op.create_index('idx_football_games_cfb_data_id', 'football_games', ['cfb_data_id'])
    op.create_index('idx_football_games_teams', 'football_games', ['home_team_id', 'away_team_id'])
    op.create_index('idx_football_games_date_teams', 'football_games', ['game_date', 'home_team_id', 'away_team_id'])

    # Create football_rosters table
    op.create_table(
        'football_rosters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('roster_status', sa.String(length=50), nullable=False, default='active'),
        sa.Column('position_group', football_position_group_enum, nullable=False),
        sa.Column('depth_order', sa.Integer(), nullable=False, default=1),
        sa.Column('is_starter', sa.Boolean(), nullable=False, default=False),
        sa.Column('special_teams_roles', sa.Text(), nullable=True),
        sa.Column('is_captain', sa.Boolean(), nullable=False, default=False),
        sa.Column('scholarship_type', scholarship_type_enum, nullable=False, default='walk_on'),
        sa.Column('scholarship_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('scholarship_count', sa.Numeric(precision=4, scale=3), nullable=False, default=0),
        sa.Column('academic_standing', sa.String(length=50), nullable=True),
        sa.Column('gpa', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('is_academically_eligible', sa.Boolean(), nullable=False, default=True),
        sa.Column('roster_added_date', sa.Date(), nullable=True),
        sa.Column('last_status_change', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['football_players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'player_id', 'academic_year_id', name='uq_football_rosters_team_player_year')
    )

    # Create indexes for football_rosters
    op.create_index('idx_football_rosters_team_id', 'football_rosters', ['team_id'])
    op.create_index('idx_football_rosters_player_id', 'football_rosters', ['player_id'])
    op.create_index('idx_football_rosters_academic_year_id', 'football_rosters', ['academic_year_id'])
    op.create_index('idx_football_rosters_active', 'football_rosters', ['is_active'])
    op.create_index('idx_football_rosters_position_group', 'football_rosters', ['position_group'])
    op.create_index('idx_football_rosters_depth', 'football_rosters', ['position_group', 'depth_order'])
    op.create_index('idx_football_rosters_starters', 'football_rosters', ['is_starter'])
    op.create_index('idx_football_rosters_scholarship', 'football_rosters', ['scholarship_type'])
    op.create_index('idx_football_rosters_team_year', 'football_rosters', ['team_id', 'academic_year_id'])

    # Create football_seasons table
    op.create_table(
        'football_seasons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('regular_season_weeks', sa.Integer(), nullable=False, default=12),
        sa.Column('conference_championship_week', sa.Integer(), nullable=True),
        sa.Column('bowl_selection_date', sa.Date(), nullable=True),
        sa.Column('playoff_selection_date', sa.Date(), nullable=True),
        sa.Column('national_championship_date', sa.Date(), nullable=True),
        sa.Column('transfer_portal_open_date', sa.Date(), nullable=True),
        sa.Column('transfer_portal_close_date', sa.Date(), nullable=True),
        sa.Column('early_signing_period_start', sa.Date(), nullable=True),
        sa.Column('early_signing_period_end', sa.Date(), nullable=True),
        sa.Column('regular_signing_period_start', sa.Date(), nullable=True),
        sa.Column('spring_practice_start', sa.Date(), nullable=True),
        sa.Column('spring_game_date', sa.Date(), nullable=True),
        sa.Column('fall_practice_start', sa.Date(), nullable=True),
        sa.Column('scholarship_limit', sa.Integer(), nullable=False, default=85),
        sa.Column('roster_limit', sa.Integer(), nullable=True),
        sa.Column('total_bowl_games', sa.Integer(), nullable=True),
        sa.Column('bowl_eligibility_requirement', sa.String(length=100), nullable=True),
        sa.Column('playoff_teams', sa.Integer(), nullable=True),
        sa.Column('playoff_format', sa.Text(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('season_id', name='uq_football_seasons_season')
    )

    # Create indexes for football_seasons
    op.create_index('idx_football_seasons_season_id', 'football_seasons', ['season_id'])
    op.create_index('idx_football_seasons_current', 'football_seasons', ['is_current'])
    op.create_index('idx_football_seasons_bowl_selection', 'football_seasons', ['bowl_selection_date'])
    op.create_index('idx_football_seasons_playoff_selection', 'football_seasons', ['playoff_selection_date'])

    # Create updated_at triggers for all tables
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add triggers for updated_at
    for table_name in ['football_teams', 'football_players', 'football_games', 'football_rosters', 'football_seasons']:
        op.execute(f"""
            CREATE TRIGGER update_{table_name}_updated_at
                BEFORE UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    """Drop college football Phase 1 tables"""

    # Drop triggers
    for table_name in ['football_teams', 'football_players', 'football_games', 'football_rosters', 'football_seasons']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table_name}_updated_at ON {table_name};")

    # Drop tables in reverse order
    op.drop_table('football_seasons')
    op.drop_table('football_rosters')
    op.drop_table('football_games')
    op.drop_table('football_players')
    op.drop_table('football_teams')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS footballrankingsystem;")
    op.execute("DROP TYPE IF EXISTS scholarshiptype;")
    op.execute("DROP TYPE IF EXISTS recruitingclass;")
    op.execute("DROP TYPE IF EXISTS footballseasontype;")
    op.execute("DROP TYPE IF EXISTS bowlgametype;")
    op.execute("DROP TYPE IF EXISTS footballformation;")
    op.execute("DROP TYPE IF EXISTS footballweathercondition;")
    op.execute("DROP TYPE IF EXISTS footballgamecontext;")
    op.execute("DROP TYPE IF EXISTS footballplaytype;")
    op.execute("DROP TYPE IF EXISTS footballpositiongroup;")
    op.execute("DROP TYPE IF EXISTS footballposition;")