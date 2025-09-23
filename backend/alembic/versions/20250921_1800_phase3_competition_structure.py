"""Phase 3: Competition Structure - Venues, Tournaments, and Game Management

Revision ID: 20250921_1800_phase3_competition_structure
Revises: 20250921_1705_phase2_academic_framework_seed_data
Create Date: 2025-09-21 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250921_1800_phase3_competition_structure'
down_revision: Union[str, None] = '20250921_1705_phase2_academic_framework_seed_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Phase 3 competition structure tables."""

    # Create venue_type enum
    venue_type_enum = sa.Enum(
        'arena', 'gymnasium', 'stadium', 'field_house', 'pavilion', 'center', 'dome', 'neutral_site',
        name='venuetype'
    )
    venue_type_enum.create(op.get_bind())

    # Create tournament_type enum
    tournament_type_enum = sa.Enum(
        'ncaa_tournament', 'conference_tournament', 'nit', 'cbi', 'cit', 'preseason',
        'regular_season', 'invitational', 'holiday_tournament', 'exempt_tournament',
        name='tournamenttype'
    )
    tournament_type_enum.create(op.get_bind())

    # Create tournament_status enum
    tournament_status_enum = sa.Enum(
        'scheduled', 'in_progress', 'completed', 'cancelled', 'postponed',
        name='tournamentstatus'
    )
    tournament_status_enum.create(op.get_bind())

    # Create tournament_format enum
    tournament_format_enum = sa.Enum(
        'single_elimination', 'double_elimination', 'round_robin', 'swiss', 'pool_play', 'stepped_bracket',
        name='tournamentformat'
    )
    tournament_format_enum.create(op.get_bind())

    # Create game_type enum
    game_type_enum = sa.Enum(
        'regular_season', 'conference_tournament', 'ncaa_tournament', 'nit', 'cbi', 'cit',
        'exhibition', 'scrimmage', 'invitational', 'holiday_tournament', 'postseason',
        name='gametype'
    )
    game_type_enum.create(op.get_bind())

    # Create bracket_region enum
    bracket_region_enum = sa.Enum(
        'east', 'west', 'south', 'midwest',
        name='bracketregion'
    )
    bracket_region_enum.create(op.get_bind())

    # Create game_importance enum
    game_importance_enum = sa.Enum(
        'low', 'medium', 'high', 'critical', 'championship',
        name='gameimportance'
    )
    game_importance_enum.create(op.get_bind())

    # Create home_court_advantage enum
    home_court_advantage_enum = sa.Enum(
        'home', 'away', 'neutral',
        name='homecourtadvantage'
    )
    home_court_advantage_enum.create(op.get_bind())

    # Create venues table
    op.create_table(
        'venues',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('venue_type', venue_type_enum, nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('country', sa.String(length=3), nullable=False, server_default='USA'),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('opened_year', sa.Integer(), nullable=True),
        sa.Column('surface_type', sa.String(length=50), nullable=True, server_default='hardwood'),
        sa.Column('college_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_neutral_site', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('court_dimensions', sa.String(length=100), nullable=True),
        sa.Column('elevation_feet', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Create tournaments table
    op.create_table(
        'tournaments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('short_name', sa.String(length=100), nullable=True),
        sa.Column('tournament_type', tournament_type_enum, nullable=False),
        sa.Column('format', tournament_format_enum, nullable=False, server_default='single_elimination'),
        sa.Column('status', tournament_status_enum, nullable=False, server_default='scheduled'),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('total_teams', sa.Integer(), nullable=True),
        sa.Column('total_rounds', sa.Integer(), nullable=True),
        sa.Column('current_round', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('selection_date', sa.Date(), nullable=True),
        sa.Column('auto_bid_eligible', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_bracket', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('champion_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('runner_up_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rules', sa.Text(), nullable=True),
        sa.Column('prize_money', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['champion_team_id'], ['college_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['runner_up_team_id'], ['college_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('academic_year_id', 'slug', name='uq_tournaments_academic_year_slug')
    )

    # Create tournament_brackets table
    op.create_table(
        'tournament_brackets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=True),
        sa.Column('region', bracket_region_enum, nullable=True),
        sa.Column('round_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('eliminated_round', sa.Integer(), nullable=True),
        sa.Column('automatic_bid', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('at_large_bid', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('selection_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['college_teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tournament_id', 'team_id', name='uq_tournament_brackets_tournament_team'),
        sa.UniqueConstraint('tournament_id', 'region', 'seed', name='uq_tournament_brackets_tournament_region_seed')
    )

    # Create college_games table
    op.create_table(
        'college_games',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('base_game_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('venue_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('game_type', game_type_enum, nullable=False, server_default='regular_season'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'LIVE', 'FINAL', 'POSTPONED', 'CANCELLED', name='gamestatus'), nullable=False, server_default='SCHEDULED'),
        sa.Column('period', sa.Integer(), nullable=True),
        sa.Column('time_remaining', sa.String(length=20), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('away_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('home_score_halftime', sa.Integer(), nullable=True),
        sa.Column('away_score_halftime', sa.Integer(), nullable=True),
        sa.Column('number_of_overtimes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('importance', game_importance_enum, nullable=False, server_default='medium'),
        sa.Column('home_court_advantage', home_court_advantage_enum, nullable=False, server_default='home'),
        sa.Column('is_conference_game', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tv_coverage', sa.String(length=100), nullable=True),
        sa.Column('attendance', sa.Integer(), nullable=True),
        sa.Column('sellout', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('temperature_fahrenheit', sa.Integer(), nullable=True),
        sa.Column('weather_conditions', sa.String(length=100), nullable=True),
        sa.Column('referees', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('espn_game_id', sa.String(length=100), nullable=True),
        sa.Column('ncaa_game_id', sa.String(length=100), nullable=True),
        sa.Column('total_fouls_home', sa.Integer(), nullable=True),
        sa.Column('total_fouls_away', sa.Integer(), nullable=True),
        sa.Column('total_timeouts_home', sa.Integer(), nullable=True),
        sa.Column('total_timeouts_away', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('game_recap', sa.Text(), nullable=True),
        sa.Column('upset_alert', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('margin_of_victory', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['base_game_id'], ['games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['home_team_id'], ['college_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['away_team_id'], ['college_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('home_team_id', 'away_team_id', 'scheduled_at', name='uq_college_games_teams_time')
    )

    # Create tournament_games table
    op.create_table(
        'tournament_games',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('round_name', sa.String(length=100), nullable=True),
        sa.Column('region', bracket_region_enum, nullable=True),
        sa.Column('game_number', sa.Integer(), nullable=True),
        sa.Column('winner_advances_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('loser_advances_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('importance', game_importance_enum, nullable=False, server_default='medium'),
        sa.Column('is_championship', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_semifinal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tv_coverage', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['college_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['winner_advances_to'], ['tournament_games.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['loser_advances_to'], ['tournament_games.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tournament_id', 'game_id', name='uq_tournament_games_tournament_game')
    )

    # Create tournament_venues table
    op.create_table(
        'tournament_venues',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('venue_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rounds_hosted', sa.String(length=200), nullable=True),
        sa.Column('is_primary_venue', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('capacity_used', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tournament_id', 'venue_id', name='uq_tournament_venues_tournament_venue')
    )

    # Create indexes for venues
    op.create_index('idx_venues_slug', 'venues', ['slug'])
    op.create_index('idx_venues_college_id', 'venues', ['college_id'])
    op.create_index('idx_venues_location', 'venues', ['state', 'city'])
    op.create_index('idx_venues_type', 'venues', ['venue_type'])
    op.create_index('idx_venues_neutral_site', 'venues', ['is_neutral_site'])
    op.create_index('idx_venues_capacity', 'venues', ['capacity'])
    op.create_index('idx_venues_external_id', 'venues', ['external_id'])

    # Create indexes for tournaments
    op.create_index('idx_tournaments_academic_year_id', 'tournaments', ['academic_year_id'])
    op.create_index('idx_tournaments_season_id', 'tournaments', ['season_id'])
    op.create_index('idx_tournaments_conference_id', 'tournaments', ['conference_id'])
    op.create_index('idx_tournaments_slug', 'tournaments', ['slug'])
    op.create_index('idx_tournaments_type', 'tournaments', ['tournament_type'])
    op.create_index('idx_tournaments_status', 'tournaments', ['status'])
    op.create_index('idx_tournaments_dates', 'tournaments', ['start_date', 'end_date'])
    op.create_index('idx_tournaments_current_round', 'tournaments', ['current_round'])

    # Create indexes for tournament_brackets
    op.create_index('idx_tournament_brackets_tournament_id', 'tournament_brackets', ['tournament_id'])
    op.create_index('idx_tournament_brackets_team_id', 'tournament_brackets', ['team_id'])
    op.create_index('idx_tournament_brackets_seed', 'tournament_brackets', ['seed'])
    op.create_index('idx_tournament_brackets_region', 'tournament_brackets', ['region'])
    op.create_index('idx_tournament_brackets_round', 'tournament_brackets', ['round_number'])
    op.create_index('idx_tournament_brackets_position', 'tournament_brackets', ['position'])
    op.create_index('idx_tournament_brackets_active', 'tournament_brackets', ['is_active'])

    # Create indexes for college_games
    op.create_index('idx_college_games_academic_year_id', 'college_games', ['academic_year_id'])
    op.create_index('idx_college_games_season_id', 'college_games', ['season_id'])
    op.create_index('idx_college_games_home_team_id', 'college_games', ['home_team_id'])
    op.create_index('idx_college_games_away_team_id', 'college_games', ['away_team_id'])
    op.create_index('idx_college_games_venue_id', 'college_games', ['venue_id'])
    op.create_index('idx_college_games_conference_id', 'college_games', ['conference_id'])
    op.create_index('idx_college_games_scheduled_at', 'college_games', ['scheduled_at'])
    op.create_index('idx_college_games_status', 'college_games', ['status'])
    op.create_index('idx_college_games_game_type', 'college_games', ['game_type'])
    op.create_index('idx_college_games_conference_game', 'college_games', ['is_conference_game'])
    op.create_index('idx_college_games_importance', 'college_games', ['importance'])
    op.create_index('idx_college_games_teams', 'college_games', ['home_team_id', 'away_team_id'])
    op.create_index('idx_college_games_external_id', 'college_games', ['external_id'])
    op.create_index('idx_college_games_espn_id', 'college_games', ['espn_game_id'])
    op.create_index('idx_college_games_ncaa_id', 'college_games', ['ncaa_game_id'])

    # Create indexes for tournament_games
    op.create_index('idx_tournament_games_tournament_id', 'tournament_games', ['tournament_id'])
    op.create_index('idx_tournament_games_game_id', 'tournament_games', ['game_id'])
    op.create_index('idx_tournament_games_round', 'tournament_games', ['round_number'])
    op.create_index('idx_tournament_games_region', 'tournament_games', ['region'])
    op.create_index('idx_tournament_games_championship', 'tournament_games', ['is_championship'])
    op.create_index('idx_tournament_games_importance', 'tournament_games', ['importance'])

    # Create indexes for tournament_venues
    op.create_index('idx_tournament_venues_tournament_id', 'tournament_venues', ['tournament_id'])
    op.create_index('idx_tournament_venues_venue_id', 'tournament_venues', ['venue_id'])
    op.create_index('idx_tournament_venues_primary', 'tournament_venues', ['is_primary_venue'])


def downgrade() -> None:
    """Drop Phase 3 competition structure tables and enums."""

    # Drop indexes first
    op.drop_index('idx_tournament_venues_primary', table_name='tournament_venues')
    op.drop_index('idx_tournament_venues_venue_id', table_name='tournament_venues')
    op.drop_index('idx_tournament_venues_tournament_id', table_name='tournament_venues')

    op.drop_index('idx_tournament_games_importance', table_name='tournament_games')
    op.drop_index('idx_tournament_games_championship', table_name='tournament_games')
    op.drop_index('idx_tournament_games_region', table_name='tournament_games')
    op.drop_index('idx_tournament_games_round', table_name='tournament_games')
    op.drop_index('idx_tournament_games_game_id', table_name='tournament_games')
    op.drop_index('idx_tournament_games_tournament_id', table_name='tournament_games')

    op.drop_index('idx_college_games_ncaa_id', table_name='college_games')
    op.drop_index('idx_college_games_espn_id', table_name='college_games')
    op.drop_index('idx_college_games_external_id', table_name='college_games')
    op.drop_index('idx_college_games_teams', table_name='college_games')
    op.drop_index('idx_college_games_importance', table_name='college_games')
    op.drop_index('idx_college_games_conference_game', table_name='college_games')
    op.drop_index('idx_college_games_game_type', table_name='college_games')
    op.drop_index('idx_college_games_status', table_name='college_games')
    op.drop_index('idx_college_games_scheduled_at', table_name='college_games')
    op.drop_index('idx_college_games_conference_id', table_name='college_games')
    op.drop_index('idx_college_games_venue_id', table_name='college_games')
    op.drop_index('idx_college_games_away_team_id', table_name='college_games')
    op.drop_index('idx_college_games_home_team_id', table_name='college_games')
    op.drop_index('idx_college_games_season_id', table_name='college_games')
    op.drop_index('idx_college_games_academic_year_id', table_name='college_games')

    op.drop_index('idx_tournament_brackets_active', table_name='tournament_brackets')
    op.drop_index('idx_tournament_brackets_position', table_name='tournament_brackets')
    op.drop_index('idx_tournament_brackets_round', table_name='tournament_brackets')
    op.drop_index('idx_tournament_brackets_region', table_name='tournament_brackets')
    op.drop_index('idx_tournament_brackets_seed', table_name='tournament_brackets')
    op.drop_index('idx_tournament_brackets_team_id', table_name='tournament_brackets')
    op.drop_index('idx_tournament_brackets_tournament_id', table_name='tournament_brackets')

    op.drop_index('idx_tournaments_current_round', table_name='tournaments')
    op.drop_index('idx_tournaments_dates', table_name='tournaments')
    op.drop_index('idx_tournaments_status', table_name='tournaments')
    op.drop_index('idx_tournaments_type', table_name='tournaments')
    op.drop_index('idx_tournaments_slug', table_name='tournaments')
    op.drop_index('idx_tournaments_conference_id', table_name='tournaments')
    op.drop_index('idx_tournaments_season_id', table_name='tournaments')
    op.drop_index('idx_tournaments_academic_year_id', table_name='tournaments')

    op.drop_index('idx_venues_external_id', table_name='venues')
    op.drop_index('idx_venues_capacity', table_name='venues')
    op.drop_index('idx_venues_neutral_site', table_name='venues')
    op.drop_index('idx_venues_type', table_name='venues')
    op.drop_index('idx_venues_location', table_name='venues')
    op.drop_index('idx_venues_college_id', table_name='venues')
    op.drop_index('idx_venues_slug', table_name='venues')

    # Drop tables (in reverse dependency order)
    op.drop_table('tournament_venues')
    op.drop_table('tournament_games')
    op.drop_table('college_games')
    op.drop_table('tournament_brackets')
    op.drop_table('tournaments')
    op.drop_table('venues')

    # Drop enums
    sa.Enum(name='homecourtadvantage').drop(op.get_bind())
    sa.Enum(name='gameimportance').drop(op.get_bind())
    sa.Enum(name='bracketregion').drop(op.get_bind())
    sa.Enum(name='gametype').drop(op.get_bind())
    sa.Enum(name='tournamentformat').drop(op.get_bind())
    sa.Enum(name='tournamentstatus').drop(op.get_bind())
    sa.Enum(name='tournamenttype').drop(op.get_bind())
    sa.Enum(name='venuetype').drop(op.get_bind())