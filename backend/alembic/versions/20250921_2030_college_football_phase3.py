"""College Football Phase 3: Postseason Structure (Bowl Games, CFP, Championships)

Revision ID: college_football_phase3
Revises: college_football_phase2
Create Date: 2025-09-21 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'college_football_phase3'
down_revision = 'college_football_phase2'
branch_labels = None
depends_on = None

def upgrade():
    """Create College Football Phase 3 tables for postseason structure"""

    # =============================================================================
    # Create new enums for Phase 3
    # =============================================================================

    # Bowl tier enum
    bowl_tier_enum = postgresql.ENUM(
        'cfp', 'new_years_six', 'major', 'regional', 'minor',
        name='bowltier'
    )
    bowl_tier_enum.create(op.get_bind())

    # Bowl selection criteria enum
    bowl_selection_criteria_enum = postgresql.ENUM(
        'cfp_semifinal', 'cfp_quarterfinal', 'conference_tie_in',
        'at_large_pool', 'group_of_five_access', 'regional_tie_in', 'open_selection',
        name='bowlselectioncriteria'
    )
    bowl_selection_criteria_enum.create(op.get_bind())

    # Playoff round enum
    playoff_round_enum = postgresql.ENUM(
        'first_round', 'quarterfinals', 'semifinals', 'championship',
        name='playoffround'
    )
    playoff_round_enum.create(op.get_bind())

    # CFP seed type enum
    cfp_seed_type_enum = postgresql.ENUM(
        'auto_qualifier', 'at_large',
        name='cfpseedtype'
    )
    cfp_seed_type_enum.create(op.get_bind())

    # Conference championship format enum
    conf_champ_format_enum = postgresql.ENUM(
        'championship_game', 'round_robin', 'division_winners', 'best_record', 'tiebreaker',
        name='conferencechampionshipformat'
    )
    conf_champ_format_enum.create(op.get_bind())

    # Rivalry type enum
    rivalry_type_enum = postgresql.ENUM(
        'conference', 'regional', 'national', 'trophy', 'cross_division', 'traditional',
        name='rivalrytype'
    )
    rivalry_type_enum.create(op.get_bind())

    # Trophy status enum
    trophy_status_enum = postgresql.ENUM(
        'active', 'retired', 'discontinued', 'disputed', 'missing',
        name='trophystatus'
    )
    trophy_status_enum.create(op.get_bind())

    # Postseason format enum
    postseason_format_enum = postgresql.ENUM(
        'single_elimination', 'double_elimination', 'round_robin',
        'pool_play', 'swiss_system', 'ladder',
        name='postseasonformat'
    )
    postseason_format_enum.create(op.get_bind())

    # Selection method enum
    selection_method_enum = postgresql.ENUM(
        'committee', 'automatic', 'ranking_based', 'conference_record',
        'overall_record', 'hybrid',
        name='selectionmethod'
    )
    selection_method_enum.create(op.get_bind())

    # Bracket position enum
    bracket_position_enum = postgresql.ENUM(
        'top_left', 'top_right', 'bottom_left', 'bottom_right', 'center', 'championship',
        name='bracketposition'
    )
    bracket_position_enum.create(op.get_bind())

    # =============================================================================
    # Bowl Games Tables
    # =============================================================================

    # Bowl games table
    op.create_table('bowl_games',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('sponsor_name', sa.String(length=200), nullable=True),
        sa.Column('full_name', sa.String(length=300), nullable=False),
        sa.Column('bowl_tier', bowl_tier_enum, nullable=False),
        sa.Column('is_cfp_bowl', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_new_years_six', sa.Boolean(), nullable=False, default=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('venue_name', sa.String(length=200), nullable=False),
        sa.Column('venue_capacity', sa.Integer(), nullable=True),
        sa.Column('typical_date', sa.String(length=100), nullable=True),
        sa.Column('kickoff_time', sa.String(length=50), nullable=True),
        sa.Column('selection_criteria', bowl_selection_criteria_enum, nullable=False),
        sa.Column('selection_order', sa.Integer(), nullable=True),
        sa.Column('min_wins_required', sa.Integer(), nullable=False, default=6),
        sa.Column('academic_requirements', sa.Text(), nullable=True),
        sa.Column('primary_conference_tie_ins', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('secondary_conference_tie_ins', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('at_large_eligible', sa.Boolean(), nullable=False, default=True),
        sa.Column('group_of_five_access', sa.Boolean(), nullable=False, default=False),
        sa.Column('total_payout', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('payout_per_team', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('payout_year', sa.Integer(), nullable=True),
        sa.Column('first_played', sa.Integer(), nullable=True),
        sa.Column('total_games_played', sa.Integer(), nullable=False, default=0),
        sa.Column('primary_tv_network', sa.String(length=100), nullable=True),
        sa.Column('broadcast_time_slot', sa.String(length=100), nullable=True),
        sa.Column('trophy_name', sa.String(length=200), nullable=True),
        sa.Column('is_tradition_bowl', sa.Boolean(), nullable=False, default=False),
        sa.Column('weather_type', sa.String(length=50), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Bowl tie-ins table
    op.create_table('bowl_tie_ins',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bowl_game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tie_in_type', sa.String(length=50), nullable=False),
        sa.Column('selection_priority', sa.Integer(), nullable=False),
        sa.Column('required_position', sa.String(length=100), nullable=True),
        sa.Column('min_conference_wins', sa.Integer(), nullable=True),
        sa.Column('max_losses_allowed', sa.Integer(), nullable=True),
        sa.Column('ranking_requirement', sa.String(length=200), nullable=True),
        sa.Column('contract_start_year', sa.Integer(), nullable=True),
        sa.Column('contract_end_year', sa.Integer(), nullable=True),
        sa.Column('is_automatic', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['bowl_game_id'], ['bowl_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bowl_game_id', 'conference_id', 'tie_in_type', name='uq_bowl_tie_ins_bowl_conf_type')
    )

    # Bowl selections table
    op.create_table('bowl_selections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bowl_game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team1_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('team2_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('selection_date', sa.Date(), nullable=True),
        sa.Column('announcement_date', sa.Date(), nullable=True),
        sa.Column('team1_selection_reason', sa.Text(), nullable=True),
        sa.Column('team2_selection_reason', sa.Text(), nullable=True),
        sa.Column('team1_record_wins', sa.Integer(), nullable=True),
        sa.Column('team1_record_losses', sa.Integer(), nullable=True),
        sa.Column('team2_record_wins', sa.Integer(), nullable=True),
        sa.Column('team2_record_losses', sa.Integer(), nullable=True),
        sa.Column('team1_cfp_ranking', sa.Integer(), nullable=True),
        sa.Column('team2_cfp_ranking', sa.Integer(), nullable=True),
        sa.Column('team1_ap_ranking', sa.Integer(), nullable=True),
        sa.Column('team2_ap_ranking', sa.Integer(), nullable=True),
        sa.Column('payout_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('is_confirmed', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_cancelled', sa.Boolean(), nullable=False, default=False),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bowl_game_id'], ['bowl_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team1_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team2_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('academic_year_id', 'bowl_game_id', name='uq_bowl_selections_year_bowl')
    )

    # =============================================================================
    # College Football Playoff Tables
    # =============================================================================

    # College Football Playoff table
    op.create_table('college_football_playoffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_teams', sa.Integer(), nullable=False, default=12),
        sa.Column('automatic_qualifiers', sa.Integer(), nullable=False, default=4),
        sa.Column('at_large_bids', sa.Integer(), nullable=False, default=8),
        sa.Column('selection_date', sa.Date(), nullable=True),
        sa.Column('bracket_release_date', sa.Date(), nullable=True),
        sa.Column('first_round_start', sa.Date(), nullable=True),
        sa.Column('championship_date', sa.Date(), nullable=True),
        sa.Column('current_round', sa.Integer(), nullable=False, default=0),
        sa.Column('total_rounds', sa.Integer(), nullable=False, default=4),
        sa.Column('is_complete', sa.Boolean(), nullable=False, default=False),
        sa.Column('champion_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('runner_up_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('selection_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['champion_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['runner_up_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('academic_year_id', name='uq_cfp_academic_year')
    )

    # CFP teams table
    op.create_table('cfp_teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('playoff_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=False),
        sa.Column('seed_type', cfp_seed_type_enum, nullable=False),
        sa.Column('conference_champion', sa.Boolean(), nullable=False, default=False),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('regular_season_wins', sa.Integer(), nullable=False),
        sa.Column('regular_season_losses', sa.Integer(), nullable=False),
        sa.Column('conference_wins', sa.Integer(), nullable=True),
        sa.Column('conference_losses', sa.Integer(), nullable=True),
        sa.Column('cfp_ranking', sa.Integer(), nullable=False),
        sa.Column('ap_ranking', sa.Integer(), nullable=True),
        sa.Column('current_round', sa.Integer(), nullable=False, default=1),
        sa.Column('is_eliminated', sa.Boolean(), nullable=False, default=False),
        sa.Column('elimination_round', sa.Integer(), nullable=True),
        sa.Column('selection_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['playoff_id'], ['college_football_playoffs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('playoff_id', 'team_id', name='uq_cfp_teams_playoff_team'),
        sa.UniqueConstraint('playoff_id', 'seed', name='uq_cfp_teams_playoff_seed')
    )

    # CFP games table
    op.create_table('cfp_games',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('playoff_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('playoff_round', playoff_round_enum, nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('game_number', sa.Integer(), nullable=True),
        sa.Column('bracket_position', bracket_position_enum, nullable=True),
        sa.Column('higher_seed', sa.Integer(), nullable=True),
        sa.Column('lower_seed', sa.Integer(), nullable=True),
        sa.Column('is_home_game', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_neutral_site', sa.Boolean(), nullable=False, default=True),
        sa.Column('host_bowl_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('winner_advances_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_championship', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_semifinal', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['playoff_id'], ['college_football_playoffs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['host_bowl_id'], ['bowl_games.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['winner_advances_to'], ['cfp_games.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('playoff_id', 'game_id', name='uq_cfp_games_playoff_game')
    )

    # =============================================================================
    # Conference Championship Tables
    # =============================================================================

    # Conference championships table
    op.create_table('conference_championships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('championship_format', conf_champ_format_enum, nullable=False),
        sa.Column('has_championship_game', sa.Boolean(), nullable=False, default=False),
        sa.Column('championship_game_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('game_date', sa.Date(), nullable=True),
        sa.Column('venue_name', sa.String(length=200), nullable=True),
        sa.Column('has_divisions', sa.Boolean(), nullable=False, default=False),
        sa.Column('division_structure', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('champion_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('runner_up_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tiebreaker_rules', sa.Text(), nullable=True),
        sa.Column('tiebreaker_applied', sa.Text(), nullable=True),
        sa.Column('cfp_automatic_qualifier', sa.Boolean(), nullable=False, default=False),
        sa.Column('cfp_ranking_requirement', sa.String(length=200), nullable=True),
        sa.Column('champion_record_wins', sa.Integer(), nullable=True),
        sa.Column('champion_record_losses', sa.Integer(), nullable=True),
        sa.Column('champion_conference_wins', sa.Integer(), nullable=True),
        sa.Column('champion_conference_losses', sa.Integer(), nullable=True),
        sa.Column('champion_cfp_ranking', sa.Integer(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('determination_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['championship_game_id'], ['football_games.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['champion_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['runner_up_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('academic_year_id', 'conference_id', name='uq_conf_champ_year_conference')
    )

    # =============================================================================
    # Rivalry Game Tables
    # =============================================================================

    # Rivalry games table
    op.create_table('rivalry_games',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('nickname', sa.String(length=200), nullable=True),
        sa.Column('team1_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team2_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rivalry_type', rivalry_type_enum, nullable=False),
        sa.Column('intensity_level', sa.Integer(), nullable=False, default=5),
        sa.Column('has_trophy', sa.Boolean(), nullable=False, default=False),
        sa.Column('trophy_name', sa.String(length=200), nullable=True),
        sa.Column('trophy_description', sa.Text(), nullable=True),
        sa.Column('trophy_holder_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('trophy_status', trophy_status_enum, nullable=True),
        sa.Column('first_meeting', sa.Integer(), nullable=True),
        sa.Column('total_meetings', sa.Integer(), nullable=False, default=0),
        sa.Column('team1_wins', sa.Integer(), nullable=False, default=0),
        sa.Column('team2_wins', sa.Integer(), nullable=False, default=0),
        sa.Column('ties', sa.Integer(), nullable=False, default=0),
        sa.Column('current_winner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('current_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('longest_streak_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('longest_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('is_annual', sa.Boolean(), nullable=False, default=True),
        sa.Column('typical_date', sa.String(length=100), nullable=True),
        sa.Column('alternates_venue', sa.Boolean(), nullable=False, default=True),
        sa.Column('neutral_site_games', sa.Boolean(), nullable=False, default=False),
        sa.Column('conference_implications', sa.Boolean(), nullable=False, default=False),
        sa.Column('playoff_implications', sa.Boolean(), nullable=False, default=False),
        sa.Column('recruiting_impact', sa.String(length=100), nullable=True),
        sa.Column('tv_tradition', sa.String(length=200), nullable=True),
        sa.Column('cultural_significance', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_played_year', sa.Integer(), nullable=True),
        sa.Column('hiatus_reason', sa.Text(), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['team1_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team2_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trophy_holder_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['current_winner_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['longest_streak_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('team1_id', 'team2_id', name='uq_rivalry_games_teams')
    )

    # Rivalry game history table
    op.create_table('rivalry_game_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rivalry_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_number', sa.Integer(), nullable=False),
        sa.Column('team1_record_before', sa.String(length=20), nullable=True),
        sa.Column('team2_record_before', sa.String(length=20), nullable=True),
        sa.Column('team1_ranking_before', sa.Integer(), nullable=True),
        sa.Column('team2_ranking_before', sa.Integer(), nullable=True),
        sa.Column('conference_implications', sa.Text(), nullable=True),
        sa.Column('playoff_implications', sa.Text(), nullable=True),
        sa.Column('trophy_on_line', sa.Boolean(), nullable=False, default=False),
        sa.Column('trophy_changed_hands', sa.Boolean(), nullable=False, default=False),
        sa.Column('winning_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('margin_of_victory', sa.Integer(), nullable=True),
        sa.Column('overtime_periods', sa.Integer(), nullable=True),
        sa.Column('notable_performances', sa.Text(), nullable=True),
        sa.Column('game_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rivalry_id'], ['rivalry_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['winning_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rivalry_id', 'game_id', name='uq_rivalry_history_rivalry_game'),
        sa.UniqueConstraint('rivalry_id', 'academic_year_id', name='uq_rivalry_history_rivalry_year')
    )

    # =============================================================================
    # Postseason Tournament Framework Table
    # =============================================================================

    # Postseason tournaments table
    op.create_table('postseason_tournaments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('sport_type', sa.String(length=50), nullable=False),
        sa.Column('postseason_format', postseason_format_enum, nullable=False),
        sa.Column('selection_method', selection_method_enum, nullable=False),
        sa.Column('total_participants', sa.Integer(), nullable=True),
        sa.Column('automatic_qualifiers', sa.Integer(), nullable=True),
        sa.Column('at_large_selections', sa.Integer(), nullable=True),
        sa.Column('selection_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('current_stage', sa.String(length=100), nullable=True),
        sa.Column('total_stages', sa.Integer(), nullable=True),
        sa.Column('selection_date', sa.Date(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('champion_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('runner_up_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_cancelled', sa.Boolean(), nullable=False, default=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['champion_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['runner_up_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('academic_year_id', 'slug', name='uq_postseason_tournaments_year_slug')
    )

    # =============================================================================
    # Create Indexes for Performance Optimization
    # =============================================================================

    # Bowl games indexes
    op.create_index('idx_bowl_games_slug', 'bowl_games', ['slug'])
    op.create_index('idx_bowl_games_tier', 'bowl_games', ['bowl_tier'])
    op.create_index('idx_bowl_games_cfp', 'bowl_games', ['is_cfp_bowl'])
    op.create_index('idx_bowl_games_ny6', 'bowl_games', ['is_new_years_six'])
    op.create_index('idx_bowl_games_location', 'bowl_games', ['state', 'city'])
    op.create_index('idx_bowl_games_selection_criteria', 'bowl_games', ['selection_criteria'])
    op.create_index('idx_bowl_games_selection_order', 'bowl_games', ['selection_order'])
    op.create_index('idx_bowl_games_active', 'bowl_games', ['is_active'])
    op.create_index('idx_bowl_games_tradition', 'bowl_games', ['is_tradition_bowl'])
    op.create_index('idx_bowl_games_external_id', 'bowl_games', ['external_id'])

    # Bowl tie-ins indexes
    op.create_index('idx_bowl_tie_ins_bowl_id', 'bowl_tie_ins', ['bowl_game_id'])
    op.create_index('idx_bowl_tie_ins_conference_id', 'bowl_tie_ins', ['conference_id'])
    op.create_index('idx_bowl_tie_ins_type', 'bowl_tie_ins', ['tie_in_type'])
    op.create_index('idx_bowl_tie_ins_priority', 'bowl_tie_ins', ['selection_priority'])
    op.create_index('idx_bowl_tie_ins_automatic', 'bowl_tie_ins', ['is_automatic'])

    # Bowl selections indexes
    op.create_index('idx_bowl_selections_academic_year_id', 'bowl_selections', ['academic_year_id'])
    op.create_index('idx_bowl_selections_bowl_game_id', 'bowl_selections', ['bowl_game_id'])
    op.create_index('idx_bowl_selections_team1_id', 'bowl_selections', ['team1_id'])
    op.create_index('idx_bowl_selections_team2_id', 'bowl_selections', ['team2_id'])
    op.create_index('idx_bowl_selections_game_id', 'bowl_selections', ['game_id'])
    op.create_index('idx_bowl_selections_selection_date', 'bowl_selections', ['selection_date'])
    op.create_index('idx_bowl_selections_confirmed', 'bowl_selections', ['is_confirmed'])
    op.create_index('idx_bowl_selections_cancelled', 'bowl_selections', ['is_cancelled'])

    # CFP indexes
    op.create_index('idx_cfp_academic_year_id', 'college_football_playoffs', ['academic_year_id'])
    op.create_index('idx_cfp_current_round', 'college_football_playoffs', ['current_round'])
    op.create_index('idx_cfp_complete', 'college_football_playoffs', ['is_complete'])
    op.create_index('idx_cfp_selection_date', 'college_football_playoffs', ['selection_date'])
    op.create_index('idx_cfp_external_id', 'college_football_playoffs', ['external_id'])

    # CFP teams indexes
    op.create_index('idx_cfp_teams_playoff_id', 'cfp_teams', ['playoff_id'])
    op.create_index('idx_cfp_teams_team_id', 'cfp_teams', ['team_id'])
    op.create_index('idx_cfp_teams_seed', 'cfp_teams', ['seed'])
    op.create_index('idx_cfp_teams_seed_type', 'cfp_teams', ['seed_type'])
    op.create_index('idx_cfp_teams_conference_champion', 'cfp_teams', ['conference_champion'])
    op.create_index('idx_cfp_teams_eliminated', 'cfp_teams', ['is_eliminated'])
    op.create_index('idx_cfp_teams_current_round', 'cfp_teams', ['current_round'])

    # CFP games indexes
    op.create_index('idx_cfp_games_playoff_id', 'cfp_games', ['playoff_id'])
    op.create_index('idx_cfp_games_game_id', 'cfp_games', ['game_id'])
    op.create_index('idx_cfp_games_round', 'cfp_games', ['playoff_round'])
    op.create_index('idx_cfp_games_round_number', 'cfp_games', ['round_number'])
    op.create_index('idx_cfp_games_championship', 'cfp_games', ['is_championship'])
    op.create_index('idx_cfp_games_semifinal', 'cfp_games', ['is_semifinal'])
    op.create_index('idx_cfp_games_host_bowl_id', 'cfp_games', ['host_bowl_id'])

    # Conference championships indexes
    op.create_index('idx_conf_champ_academic_year_id', 'conference_championships', ['academic_year_id'])
    op.create_index('idx_conf_champ_conference_id', 'conference_championships', ['conference_id'])
    op.create_index('idx_conf_champ_game_id', 'conference_championships', ['championship_game_id'])
    op.create_index('idx_conf_champ_format', 'conference_championships', ['championship_format'])
    op.create_index('idx_conf_champ_has_game', 'conference_championships', ['has_championship_game'])
    op.create_index('idx_conf_champ_cfp_auto', 'conference_championships', ['cfp_automatic_qualifier'])
    op.create_index('idx_conf_champ_completed', 'conference_championships', ['is_completed'])
    op.create_index('idx_conf_champ_date', 'conference_championships', ['game_date'])

    # Rivalry games indexes
    op.create_index('idx_rivalry_games_slug', 'rivalry_games', ['slug'])
    op.create_index('idx_rivalry_games_team1_id', 'rivalry_games', ['team1_id'])
    op.create_index('idx_rivalry_games_team2_id', 'rivalry_games', ['team2_id'])
    op.create_index('idx_rivalry_games_type', 'rivalry_games', ['rivalry_type'])
    op.create_index('idx_rivalry_games_intensity', 'rivalry_games', ['intensity_level'])
    op.create_index('idx_rivalry_games_trophy', 'rivalry_games', ['has_trophy'])
    op.create_index('idx_rivalry_games_active', 'rivalry_games', ['is_active'])
    op.create_index('idx_rivalry_games_annual', 'rivalry_games', ['is_annual'])
    op.create_index('idx_rivalry_games_external_id', 'rivalry_games', ['external_id'])

    # Rivalry game history indexes
    op.create_index('idx_rivalry_history_rivalry_id', 'rivalry_game_history', ['rivalry_id'])
    op.create_index('idx_rivalry_history_game_id', 'rivalry_game_history', ['game_id'])
    op.create_index('idx_rivalry_history_academic_year_id', 'rivalry_game_history', ['academic_year_id'])
    op.create_index('idx_rivalry_history_game_number', 'rivalry_game_history', ['game_number'])
    op.create_index('idx_rivalry_history_trophy', 'rivalry_game_history', ['trophy_on_line'])
    op.create_index('idx_rivalry_history_winning_team_id', 'rivalry_game_history', ['winning_team_id'])

    # Postseason tournaments indexes
    op.create_index('idx_postseason_tournaments_tournament_id', 'postseason_tournaments', ['tournament_id'])
    op.create_index('idx_postseason_tournaments_academic_year_id', 'postseason_tournaments', ['academic_year_id'])
    op.create_index('idx_postseason_tournaments_season_id', 'postseason_tournaments', ['season_id'])
    op.create_index('idx_postseason_tournaments_slug', 'postseason_tournaments', ['slug'])
    op.create_index('idx_postseason_tournaments_sport', 'postseason_tournaments', ['sport_type'])
    op.create_index('idx_postseason_tournaments_format', 'postseason_tournaments', ['postseason_format'])
    op.create_index('idx_postseason_tournaments_completed', 'postseason_tournaments', ['is_completed'])
    op.create_index('idx_postseason_tournaments_external_id', 'postseason_tournaments', ['external_id'])


def downgrade():
    """Drop College Football Phase 3 tables and enums"""

    # Drop tables in reverse dependency order
    op.drop_table('postseason_tournaments')
    op.drop_table('rivalry_game_history')
    op.drop_table('rivalry_games')
    op.drop_table('conference_championships')
    op.drop_table('cfp_games')
    op.drop_table('cfp_teams')
    op.drop_table('college_football_playoffs')
    op.drop_table('bowl_selections')
    op.drop_table('bowl_tie_ins')
    op.drop_table('bowl_games')

    # Drop enums
    postgresql.ENUM(name='bracketposition').drop(op.get_bind())
    postgresql.ENUM(name='selectionmethod').drop(op.get_bind())
    postgresql.ENUM(name='postseasonformat').drop(op.get_bind())
    postgresql.ENUM(name='trophystatus').drop(op.get_bind())
    postgresql.ENUM(name='rivalrytype').drop(op.get_bind())
    postgresql.ENUM(name='conferencechampionshipformat').drop(op.get_bind())
    postgresql.ENUM(name='cfpseedtype').drop(op.get_bind())
    postgresql.ENUM(name='playoffround').drop(op.get_bind())
    postgresql.ENUM(name='bowlselectioncriteria').drop(op.get_bind())
    postgresql.ENUM(name='bowltier').drop(op.get_bind())