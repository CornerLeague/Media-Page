"""College Football Phase 2: Play-by-Play and Advanced Statistics

Revision ID: college_football_phase2
Revises: 20250920_0001_seed_sports_leagues_teams
Create Date: 2025-09-21 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'college_football_phase2'
down_revision = '20250920_0001_seed_sports_leagues_teams'
branch_labels = None
depends_on = None

def upgrade():
    """Create College Football Phase 2 tables for play-by-play and advanced statistics"""

    # =============================================================================
    # Create new enums for Phase 2
    # =============================================================================

    # Play result enum
    play_result_enum = postgresql.ENUM(
        'gain', 'loss', 'no_gain', 'touchdown', 'fumble', 'interception',
        'incomplete', 'sack', 'safety', 'turnover_on_downs', 'penalty',
        'field_goal_good', 'field_goal_missed', 'extra_point_good', 'extra_point_missed',
        'blocked_kick', 'punt', 'punt_blocked', 'punt_downed', 'punt_fair_catch',
        'punt_touchback', 'punt_out_of_bounds', 'kickoff', 'kickoff_touchback',
        'kickoff_out_of_bounds', 'onside_kick_recovered', 'onside_kick_failed',
        name='playresult'
    )
    play_result_enum.create(op.get_bind())

    # Drive result enum
    drive_result_enum = postgresql.ENUM(
        'touchdown', 'field_goal', 'missed_field_goal', 'punt', 'fumble_lost',
        'interception', 'turnover_on_downs', 'safety', 'end_of_half', 'end_of_game',
        'downs', 'blocked_punt', 'blocked_field_goal',
        name='driveresult'
    )
    drive_result_enum.create(op.get_bind())

    # Field position enum
    field_position_enum = postgresql.ENUM(
        'own_endzone', 'own_territory', 'midfield', 'opponent_territory',
        'red_zone', 'goal_line',
        name='fieldposition'
    )
    field_position_enum.create(op.get_bind())

    # Down type enum
    down_type_enum = postgresql.ENUM(
        'first_down', 'second_short', 'second_medium', 'second_long',
        'third_short', 'third_medium', 'third_long', 'fourth_down',
        name='downtype'
    )
    down_type_enum.create(op.get_bind())

    # Play direction enum
    play_direction_enum = postgresql.ENUM(
        'left', 'right', 'center', 'outside_left', 'outside_right',
        'up_the_middle', 'deep_left', 'deep_right', 'deep_middle',
        'short_left', 'short_right', 'short_middle',
        name='playdirection'
    )
    play_direction_enum.create(op.get_bind())

    # Pass length enum
    pass_length_enum = postgresql.ENUM(
        'screen', 'short', 'medium', 'deep', 'bomb',
        name='passlength'
    )
    pass_length_enum.create(op.get_bind())

    # Rush type enum
    rush_type_enum = postgresql.ENUM(
        'inside_run', 'outside_run', 'draw', 'power_run', 'sweep',
        'reverse', 'option', 'qb_sneak', 'qb_scramble', 'designed_qb_run', 'wildcat',
        name='rushtype'
    )
    rush_type_enum.create(op.get_bind())

    # Defensive play type enum
    defensive_play_type_enum = postgresql.ENUM(
        'base_defense', 'blitz', 'coverage', 'prevent', 'goal_line',
        'punt_block', 'field_goal_block', 'return_formation',
        name='defensiveplaytype'
    )
    defensive_play_type_enum.create(op.get_bind())

    # Penalty type enum
    penalty_type_enum = postgresql.ENUM(
        'false_start', 'holding_offense', 'illegal_formation', 'illegal_motion',
        'delay_of_game', 'intentional_grounding', 'illegal_forward_pass',
        'offensive_pass_interference', 'unsportsmanlike_conduct_offense',
        'offside', 'encroachment', 'neutral_zone_infraction', 'holding_defense',
        'illegal_contact', 'pass_interference', 'roughing_the_passer',
        'roughing_the_kicker', 'targeting', 'unsportsmanlike_conduct_defense',
        'illegal_block_above_waist', 'illegal_block_below_waist', 'clipping',
        'block_in_back', 'kickoff_out_of_bounds', 'personal_foul',
        'unnecessary_roughness', 'facemask', 'horse_collar', 'illegal_substitution',
        'too_many_men',
        name='penaltytype'
    )
    penalty_type_enum.create(op.get_bind())

    # Advanced metric type enum
    advanced_metric_type_enum = postgresql.ENUM(
        'epa', 'wpa', 'success_rate', 'explosive_play_rate', 'stuff_rate',
        'yards_per_play', 'points_per_drive', 'plays_per_drive', 'time_per_drive',
        'third_down_conversion', 'red_zone_efficiency', 'goal_line_efficiency',
        'two_minute_efficiency', 'average_field_position', 'field_position_advantage',
        'defensive_dvoa', 'havoc_rate', 'pressure_rate', 'field_goal_efficiency',
        'punt_efficiency', 'return_efficiency',
        name='advancedmetrictype'
    )
    advanced_metric_type_enum.create(op.get_bind())

    # Game situation enum
    game_situation_enum = postgresql.ENUM(
        'early_game', 'middle_game', 'late_game', 'overtime',
        'close_game', 'blowout', 'garbage_time', 'winning', 'losing', 'tied',
        'high_leverage', 'low_leverage',
        name='gamesituation'
    )
    game_situation_enum.create(op.get_bind())

    # =============================================================================
    # Create Drive Data table
    # =============================================================================

    op.create_table('football_drive_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Game context
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drive_number', sa.Integer(), nullable=False),
        sa.Column('offense_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('defense_team_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Drive timing
        sa.Column('start_quarter', sa.Integer(), nullable=False),
        sa.Column('end_quarter', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('drive_duration_seconds', sa.Integer(), nullable=True),

        # Field position
        sa.Column('start_yard_line', sa.Integer(), nullable=False),
        sa.Column('end_yard_line', sa.Integer(), nullable=False),
        sa.Column('start_field_position', field_position_enum, nullable=False),

        # Drive statistics
        sa.Column('total_plays', sa.Integer(), nullable=False, default=0),
        sa.Column('total_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_plays', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_plays', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('penalty_yards', sa.Integer(), nullable=False, default=0),

        # Drive outcome
        sa.Column('drive_result', drive_result_enum, nullable=False),
        sa.Column('points_scored', sa.Integer(), nullable=False, default=0),

        # Down tracking
        sa.Column('first_downs_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('third_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('third_down_conversions', sa.Integer(), nullable=False, default=0),
        sa.Column('fourth_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('fourth_down_conversions', sa.Integer(), nullable=False, default=0),

        # Situational context
        sa.Column('is_red_zone_drive', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_goal_line_drive', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_short_field', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_two_minute_drive', sa.Boolean(), nullable=False, default=False),

        # Game situation
        sa.Column('score_differential_start', sa.Integer(), nullable=False),
        sa.Column('score_differential_end', sa.Integer(), nullable=False),
        sa.Column('game_situation_start', game_situation_enum, nullable=True),

        # Advanced metrics
        sa.Column('expected_points_start', sa.Numeric(6, 3), nullable=True),
        sa.Column('expected_points_end', sa.Numeric(6, 3), nullable=True),
        sa.Column('expected_points_added', sa.Numeric(6, 3), nullable=True),
        sa.Column('win_probability_start', sa.Numeric(5, 4), nullable=True),
        sa.Column('win_probability_end', sa.Numeric(5, 4), nullable=True),
        sa.Column('win_probability_added', sa.Numeric(6, 4), nullable=True),

        # Efficiency metrics
        sa.Column('yards_per_play', sa.Numeric(4, 2), nullable=True),
        sa.Column('success_rate', sa.Numeric(4, 3), nullable=True),
        sa.Column('explosive_play_count', sa.Integer(), nullable=False, default=0),
        sa.Column('stuff_count', sa.Integer(), nullable=False, default=0),

        # Turnover and penalty tracking
        sa.Column('turnovers', sa.Integer(), nullable=False, default=0),
        sa.Column('penalties', sa.Integer(), nullable=False, default=0),

        # External references
        sa.Column('external_drive_id', sa.String(100), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['offense_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['defense_team_id'], ['football_teams.id'], ondelete='CASCADE'),
    )

    # =============================================================================
    # Create Play-by-Play table
    # =============================================================================

    op.create_table('football_play_by_play',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Game context
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drive_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('play_number', sa.Integer(), nullable=False),
        sa.Column('drive_play_number', sa.Integer(), nullable=True),

        # Team context
        sa.Column('offense_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('defense_team_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Game timing
        sa.Column('quarter', sa.Integer(), nullable=False),
        sa.Column('time_remaining', sa.Time(), nullable=True),
        sa.Column('game_clock_seconds', sa.Integer(), nullable=True),

        # Down and distance
        sa.Column('down', sa.Integer(), nullable=False),
        sa.Column('distance', sa.Integer(), nullable=False),
        sa.Column('down_type', down_type_enum, nullable=False),

        # Field position
        sa.Column('yard_line', sa.Integer(), nullable=False),
        sa.Column('yard_line_side', sa.String(10), nullable=False),
        sa.Column('field_position', field_position_enum, nullable=False),

        # Play details
        sa.Column('play_type', postgresql.ENUM(name='footballplaytype'), nullable=False),
        sa.Column('play_description', sa.Text(), nullable=False),
        sa.Column('play_result', play_result_enum, nullable=False),

        # Yardage and movement
        sa.Column('yards_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('yards_to_endzone_start', sa.Integer(), nullable=False),
        sa.Column('yards_to_endzone_end', sa.Integer(), nullable=False),

        # Play direction and location
        sa.Column('play_direction', play_direction_enum, nullable=True),
        sa.Column('gap_location', sa.String(50), nullable=True),

        # Passing play details
        sa.Column('is_pass', sa.Boolean(), nullable=False, default=False),
        sa.Column('pass_length', pass_length_enum, nullable=True),
        sa.Column('air_yards', sa.Integer(), nullable=True),
        sa.Column('yards_after_catch', sa.Integer(), nullable=True),
        sa.Column('is_completion', sa.Boolean(), nullable=True),

        # Rushing play details
        sa.Column('is_rush', sa.Boolean(), nullable=False, default=False),
        sa.Column('rush_type', rush_type_enum, nullable=True),

        # Special teams details
        sa.Column('is_special_teams', sa.Boolean(), nullable=False, default=False),

        # Player involvement
        sa.Column('primary_player_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('secondary_player_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Scoring
        sa.Column('is_touchdown', sa.Boolean(), nullable=False, default=False),
        sa.Column('points_scored', sa.Integer(), nullable=False, default=0),

        # Turnover information
        sa.Column('is_turnover', sa.Boolean(), nullable=False, default=False),
        sa.Column('turnover_type', sa.String(50), nullable=True),

        # Penalty information
        sa.Column('is_penalty', sa.Boolean(), nullable=False, default=False),
        sa.Column('penalty_type', penalty_type_enum, nullable=True),
        sa.Column('penalty_yards', sa.Integer(), nullable=True),
        sa.Column('penalty_team_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Formation and strategy
        sa.Column('offensive_formation', postgresql.ENUM(name='footballformation'), nullable=True),
        sa.Column('defensive_formation', postgresql.ENUM(name='footballformation'), nullable=True),
        sa.Column('defensive_play_type', defensive_play_type_enum, nullable=True),

        # Game situation context
        sa.Column('game_situation', game_situation_enum, nullable=True),
        sa.Column('score_differential', sa.Integer(), nullable=False, default=0),

        # Advanced context
        sa.Column('is_red_zone', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_goal_line', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_two_minute_warning', sa.Boolean(), nullable=False, default=False),

        # Expected points and win probability
        sa.Column('expected_points_before', sa.Numeric(6, 3), nullable=True),
        sa.Column('expected_points_after', sa.Numeric(6, 3), nullable=True),
        sa.Column('expected_points_added', sa.Numeric(6, 3), nullable=True),
        sa.Column('win_probability_before', sa.Numeric(5, 4), nullable=True),
        sa.Column('win_probability_after', sa.Numeric(5, 4), nullable=True),
        sa.Column('win_probability_added', sa.Numeric(6, 4), nullable=True),

        # Success metrics
        sa.Column('is_successful_play', sa.Boolean(), nullable=True),
        sa.Column('is_explosive_play', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_stuff', sa.Boolean(), nullable=False, default=False),

        # External references
        sa.Column('external_play_id', sa.String(100), nullable=True),
        sa.Column('pbp_data_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['drive_id'], ['football_drive_data.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['offense_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['defense_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['primary_player_id'], ['football_players.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['secondary_player_id'], ['football_players.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['penalty_team_id'], ['football_teams.id'], ondelete='SET NULL'),
    )

    # =============================================================================
    # Create Player Statistics table
    # =============================================================================

    op.create_table('football_player_statistics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Player and context
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Statistical context
        sa.Column('statistic_type', postgresql.ENUM(name='statistictype'), nullable=False),
        sa.Column('position_group', postgresql.ENUM(name='footballpositiongroup'), nullable=False),
        sa.Column('games_played', sa.Integer(), nullable=False, default=0),
        sa.Column('games_started', sa.Integer(), nullable=False, default=0),

        # Passing statistics (QB)
        sa.Column('passing_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_completions', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_interceptions', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_sacks', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_sack_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_longest', sa.Integer(), nullable=False, default=0),
        sa.Column('qbr', sa.Numeric(5, 2), nullable=True),

        # Rushing statistics
        sa.Column('rushing_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_longest', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_fumbles', sa.Integer(), nullable=False, default=0),

        # Receiving statistics
        sa.Column('receiving_targets', sa.Integer(), nullable=False, default=0),
        sa.Column('receiving_receptions', sa.Integer(), nullable=False, default=0),
        sa.Column('receiving_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('receiving_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('receiving_longest', sa.Integer(), nullable=False, default=0),
        sa.Column('receiving_fumbles', sa.Integer(), nullable=False, default=0),
        sa.Column('yards_after_catch', sa.Integer(), nullable=False, default=0),
        sa.Column('drops', sa.Integer(), nullable=False, default=0),

        # Defensive statistics
        sa.Column('tackles_total', sa.Integer(), nullable=False, default=0),
        sa.Column('tackles_solo', sa.Integer(), nullable=False, default=0),
        sa.Column('tackles_assisted', sa.Integer(), nullable=False, default=0),
        sa.Column('tackles_for_loss', sa.Integer(), nullable=False, default=0),
        sa.Column('tackles_for_loss_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('sacks', sa.Numeric(4, 1), nullable=False, default=0),
        sa.Column('sack_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('quarterback_hits', sa.Integer(), nullable=False, default=0),
        sa.Column('quarterback_hurries', sa.Integer(), nullable=False, default=0),

        # Pass defense
        sa.Column('passes_defended', sa.Integer(), nullable=False, default=0),
        sa.Column('interceptions', sa.Integer(), nullable=False, default=0),
        sa.Column('interception_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('interception_touchdowns', sa.Integer(), nullable=False, default=0),

        # Fumble recovery
        sa.Column('fumbles_recovered', sa.Integer(), nullable=False, default=0),
        sa.Column('fumble_return_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('fumble_return_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('fumbles_forced', sa.Integer(), nullable=False, default=0),

        # Special teams statistics
        sa.Column('field_goal_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('field_goals_made', sa.Integer(), nullable=False, default=0),
        sa.Column('field_goal_longest', sa.Integer(), nullable=False, default=0),
        sa.Column('extra_point_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('extra_points_made', sa.Integer(), nullable=False, default=0),

        # Punting statistics
        sa.Column('punts', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_longest', sa.Integer(), nullable=False, default=0),
        sa.Column('punts_inside_20', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_touchbacks', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_fair_catches', sa.Integer(), nullable=False, default=0),

        # Return statistics
        sa.Column('punt_returns', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_return_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_return_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_return_longest', sa.Integer(), nullable=False, default=0),
        sa.Column('kickoff_returns', sa.Integer(), nullable=False, default=0),
        sa.Column('kickoff_return_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('kickoff_return_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('kickoff_return_longest', sa.Integer(), nullable=False, default=0),

        # Offensive line statistics
        sa.Column('pass_blocking_snaps', sa.Integer(), nullable=False, default=0),
        sa.Column('sacks_allowed', sa.Integer(), nullable=False, default=0),
        sa.Column('quarterback_hits_allowed', sa.Integer(), nullable=False, default=0),
        sa.Column('hurries_allowed', sa.Integer(), nullable=False, default=0),

        # Penalty statistics
        sa.Column('penalties', sa.Integer(), nullable=False, default=0),
        sa.Column('penalty_yards', sa.Integer(), nullable=False, default=0),

        # Snap counts and usage
        sa.Column('offensive_snaps', sa.Integer(), nullable=False, default=0),
        sa.Column('defensive_snaps', sa.Integer(), nullable=False, default=0),
        sa.Column('special_teams_snaps', sa.Integer(), nullable=False, default=0),

        # Advanced metrics
        sa.Column('player_efficiency_rating', sa.Numeric(6, 3), nullable=True),
        sa.Column('pro_football_focus_grade', sa.Numeric(5, 2), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['player_id'], ['football_players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
    )

    # =============================================================================
    # Create Team Statistics table
    # =============================================================================

    op.create_table('football_team_statistics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Team and context
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('opponent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Statistical context
        sa.Column('statistic_type', postgresql.ENUM(name='statistictype'), nullable=False),
        sa.Column('is_home_team', sa.Boolean(), nullable=True),
        sa.Column('games_played', sa.Integer(), nullable=False, default=0),

        # Scoring
        sa.Column('points_for', sa.Integer(), nullable=False, default=0),
        sa.Column('points_against', sa.Integer(), nullable=False, default=0),
        sa.Column('touchdowns_total', sa.Integer(), nullable=False, default=0),
        sa.Column('field_goals_made', sa.Integer(), nullable=False, default=0),
        sa.Column('field_goals_attempted', sa.Integer(), nullable=False, default=0),
        sa.Column('extra_points_made', sa.Integer(), nullable=False, default=0),
        sa.Column('extra_points_attempted', sa.Integer(), nullable=False, default=0),
        sa.Column('safeties', sa.Integer(), nullable=False, default=0),

        # Offensive statistics
        sa.Column('total_plays', sa.Integer(), nullable=False, default=0),
        sa.Column('total_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('first_downs', sa.Integer(), nullable=False, default=0),
        sa.Column('first_downs_passing', sa.Integer(), nullable=False, default=0),
        sa.Column('first_downs_rushing', sa.Integer(), nullable=False, default=0),
        sa.Column('first_downs_penalty', sa.Integer(), nullable=False, default=0),

        # Passing offense
        sa.Column('passing_completions', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_interceptions', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_longest', sa.Integer(), nullable=False, default=0),
        sa.Column('sacks_allowed', sa.Integer(), nullable=False, default=0),
        sa.Column('sack_yards_lost', sa.Integer(), nullable=False, default=0),

        # Rushing offense
        sa.Column('rushing_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_longest', sa.Integer(), nullable=False, default=0),

        # Defensive statistics
        sa.Column('defensive_plays', sa.Integer(), nullable=False, default=0),
        sa.Column('defensive_yards_allowed', sa.Integer(), nullable=False, default=0),
        sa.Column('passing_yards_allowed', sa.Integer(), nullable=False, default=0),
        sa.Column('rushing_yards_allowed', sa.Integer(), nullable=False, default=0),
        sa.Column('sacks_recorded', sa.Integer(), nullable=False, default=0),
        sa.Column('sack_yards_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('tackles_for_loss', sa.Integer(), nullable=False, default=0),
        sa.Column('tackles_for_loss_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('interceptions_made', sa.Integer(), nullable=False, default=0),
        sa.Column('interception_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('fumbles_recovered', sa.Integer(), nullable=False, default=0),
        sa.Column('fumble_return_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('fumbles_forced', sa.Integer(), nullable=False, default=0),
        sa.Column('passes_defended', sa.Integer(), nullable=False, default=0),

        # Turnover statistics
        sa.Column('turnovers_gained', sa.Integer(), nullable=False, default=0),
        sa.Column('turnovers_lost', sa.Integer(), nullable=False, default=0),
        sa.Column('fumbles_lost', sa.Integer(), nullable=False, default=0),

        # Special teams
        sa.Column('punt_return_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('punt_return_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('kickoff_return_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('kickoff_return_touchdowns', sa.Integer(), nullable=False, default=0),

        # Down and distance
        sa.Column('third_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('third_down_conversions', sa.Integer(), nullable=False, default=0),
        sa.Column('fourth_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('fourth_down_conversions', sa.Integer(), nullable=False, default=0),

        # Red zone efficiency
        sa.Column('red_zone_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('red_zone_scores', sa.Integer(), nullable=False, default=0),
        sa.Column('red_zone_touchdowns', sa.Integer(), nullable=False, default=0),

        # Penalties
        sa.Column('penalties', sa.Integer(), nullable=False, default=0),
        sa.Column('penalty_yards', sa.Integer(), nullable=False, default=0),

        # Time of possession
        sa.Column('time_of_possession_seconds', sa.Integer(), nullable=True),

        # Drives
        sa.Column('total_drives', sa.Integer(), nullable=False, default=0),
        sa.Column('scoring_drives', sa.Integer(), nullable=False, default=0),
        sa.Column('touchdown_drives', sa.Integer(), nullable=False, default=0),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['opponent_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
    )

    # =============================================================================
    # Create Advanced Metrics table
    # =============================================================================

    op.create_table('football_advanced_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Context
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Metric identification
        sa.Column('metric_type', advanced_metric_type_enum, nullable=False),
        sa.Column('metric_category', postgresql.ENUM(name='statisticcategory'), nullable=False),
        sa.Column('position_group', postgresql.ENUM(name='footballpositiongroup'), nullable=True),

        # Situational context
        sa.Column('situation_filter', sa.String(100), nullable=True),
        sa.Column('opponent_strength', sa.String(50), nullable=True),

        # Core metric values
        sa.Column('metric_value', sa.Numeric(10, 6), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=False, default=0),
        sa.Column('confidence_interval_lower', sa.Numeric(10, 6), nullable=True),
        sa.Column('confidence_interval_upper', sa.Numeric(10, 6), nullable=True),

        # Expected Points metrics
        sa.Column('expected_points_added', sa.Numeric(8, 4), nullable=True),
        sa.Column('expected_points_per_play', sa.Numeric(6, 4), nullable=True),

        # Win Probability metrics
        sa.Column('win_probability_added', sa.Numeric(8, 6), nullable=True),
        sa.Column('win_probability_per_play', sa.Numeric(6, 6), nullable=True),

        # Success rate metrics
        sa.Column('success_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('explosive_play_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('stuff_rate', sa.Numeric(5, 4), nullable=True),

        # Efficiency metrics
        sa.Column('yards_per_play', sa.Numeric(5, 2), nullable=True),
        sa.Column('points_per_drive', sa.Numeric(5, 3), nullable=True),
        sa.Column('plays_per_drive', sa.Numeric(5, 2), nullable=True),
        sa.Column('seconds_per_drive', sa.Numeric(6, 2), nullable=True),

        # Down and distance efficiency
        sa.Column('first_down_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('third_down_conversion_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('fourth_down_conversion_rate', sa.Numeric(5, 4), nullable=True),

        # Red zone and goal line
        sa.Column('red_zone_efficiency', sa.Numeric(5, 4), nullable=True),
        sa.Column('red_zone_touchdown_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('goal_line_efficiency', sa.Numeric(5, 4), nullable=True),

        # Two-minute drill
        sa.Column('two_minute_efficiency', sa.Numeric(5, 4), nullable=True),

        # Field position metrics
        sa.Column('average_field_position', sa.Numeric(4, 1), nullable=True),
        sa.Column('field_position_advantage', sa.Numeric(5, 2), nullable=True),

        # Pressure and pass rush metrics
        sa.Column('pressure_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('sack_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('quarterback_hit_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('hurry_rate', sa.Numeric(5, 4), nullable=True),

        # Coverage metrics
        sa.Column('completion_percentage_allowed', sa.Numeric(5, 4), nullable=True),
        sa.Column('yards_per_target_allowed', sa.Numeric(5, 2), nullable=True),
        sa.Column('passer_rating_allowed', sa.Numeric(5, 2), nullable=True),

        # HAVOC rate
        sa.Column('havoc_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('tackles_for_loss_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('forced_fumble_rate', sa.Numeric(5, 4), nullable=True),

        # DVOA-style metrics
        sa.Column('dvoa_offensive', sa.Numeric(6, 3), nullable=True),
        sa.Column('dvoa_defensive', sa.Numeric(6, 3), nullable=True),

        # Special teams efficiency
        sa.Column('field_goal_efficiency', sa.Numeric(5, 4), nullable=True),
        sa.Column('punt_efficiency', sa.Numeric(5, 2), nullable=True),
        sa.Column('return_efficiency', sa.Numeric(5, 2), nullable=True),
        sa.Column('punt_coverage_efficiency', sa.Numeric(5, 2), nullable=True),
        sa.Column('kickoff_coverage_efficiency', sa.Numeric(5, 2), nullable=True),

        # Relative performance
        sa.Column('percentile_rank', sa.Numeric(5, 2), nullable=True),
        sa.Column('z_score', sa.Numeric(6, 3), nullable=True),
        sa.Column('grade', sa.String(5), nullable=True),

        # Time-based context
        sa.Column('calculation_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),

        # Metadata
        sa.Column('calculation_method', sa.String(100), nullable=True),
        sa.Column('data_source', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['football_players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
    )

    # =============================================================================
    # Create Game Statistics table
    # =============================================================================

    op.create_table('football_game_statistics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Game context
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('home_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('away_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Game outcome
        sa.Column('home_score', sa.Integer(), nullable=False),
        sa.Column('away_score', sa.Integer(), nullable=False),
        sa.Column('winner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('margin_of_victory', sa.Integer(), nullable=False),

        # Game flow and timing
        sa.Column('total_plays', sa.Integer(), nullable=False, default=0),
        sa.Column('game_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('overtime_periods', sa.Integer(), nullable=False, default=0),

        # Scoring breakdown
        sa.Column('home_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('away_touchdowns', sa.Integer(), nullable=False, default=0),
        sa.Column('home_field_goals', sa.Integer(), nullable=False, default=0),
        sa.Column('away_field_goals', sa.Integer(), nullable=False, default=0),
        sa.Column('home_safeties', sa.Integer(), nullable=False, default=0),
        sa.Column('away_safeties', sa.Integer(), nullable=False, default=0),

        # Total yardage
        sa.Column('home_total_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('away_total_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('home_passing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('away_passing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('home_rushing_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('away_rushing_yards', sa.Integer(), nullable=False, default=0),

        # First downs
        sa.Column('home_first_downs', sa.Integer(), nullable=False, default=0),
        sa.Column('away_first_downs', sa.Integer(), nullable=False, default=0),

        # Third down efficiency
        sa.Column('home_third_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('home_third_down_conversions', sa.Integer(), nullable=False, default=0),
        sa.Column('away_third_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('away_third_down_conversions', sa.Integer(), nullable=False, default=0),

        # Fourth down efficiency
        sa.Column('home_fourth_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('home_fourth_down_conversions', sa.Integer(), nullable=False, default=0),
        sa.Column('away_fourth_down_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('away_fourth_down_conversions', sa.Integer(), nullable=False, default=0),

        # Red zone efficiency
        sa.Column('home_red_zone_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('home_red_zone_scores', sa.Integer(), nullable=False, default=0),
        sa.Column('away_red_zone_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('away_red_zone_scores', sa.Integer(), nullable=False, default=0),

        # Turnovers
        sa.Column('home_turnovers', sa.Integer(), nullable=False, default=0),
        sa.Column('away_turnovers', sa.Integer(), nullable=False, default=0),
        sa.Column('home_interceptions_thrown', sa.Integer(), nullable=False, default=0),
        sa.Column('away_interceptions_thrown', sa.Integer(), nullable=False, default=0),
        sa.Column('home_fumbles_lost', sa.Integer(), nullable=False, default=0),
        sa.Column('away_fumbles_lost', sa.Integer(), nullable=False, default=0),

        # Penalties
        sa.Column('home_penalties', sa.Integer(), nullable=False, default=0),
        sa.Column('home_penalty_yards', sa.Integer(), nullable=False, default=0),
        sa.Column('away_penalties', sa.Integer(), nullable=False, default=0),
        sa.Column('away_penalty_yards', sa.Integer(), nullable=False, default=0),

        # Time of possession
        sa.Column('home_time_of_possession_seconds', sa.Integer(), nullable=True),
        sa.Column('away_time_of_possession_seconds', sa.Integer(), nullable=True),

        # Drives
        sa.Column('home_total_drives', sa.Integer(), nullable=False, default=0),
        sa.Column('away_total_drives', sa.Integer(), nullable=False, default=0),
        sa.Column('home_scoring_drives', sa.Integer(), nullable=False, default=0),
        sa.Column('away_scoring_drives', sa.Integer(), nullable=False, default=0),

        # Sacks
        sa.Column('home_sacks_recorded', sa.Integer(), nullable=False, default=0),
        sa.Column('away_sacks_recorded', sa.Integer(), nullable=False, default=0),
        sa.Column('home_sacks_allowed', sa.Integer(), nullable=False, default=0),
        sa.Column('away_sacks_allowed', sa.Integer(), nullable=False, default=0),

        # Advanced metrics
        sa.Column('home_expected_points_added', sa.Numeric(8, 4), nullable=True),
        sa.Column('away_expected_points_added', sa.Numeric(8, 4), nullable=True),
        sa.Column('home_success_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('away_success_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('home_explosive_plays', sa.Integer(), nullable=False, default=0),
        sa.Column('away_explosive_plays', sa.Integer(), nullable=False, default=0),

        # Game context and significance
        sa.Column('game_importance', sa.String(50), nullable=True),
        sa.Column('playoff_implications', sa.Boolean(), nullable=True),
        sa.Column('rivalry_game', sa.Boolean(), nullable=False, default=False),
        sa.Column('conference_game', sa.Boolean(), nullable=False, default=False),

        # Weather impact
        sa.Column('weather_impact', sa.String(50), nullable=True),

        # Data completeness
        sa.Column('play_by_play_complete', sa.Boolean(), nullable=False, default=False),
        sa.Column('advanced_stats_complete', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_stats_update', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_id'], ['football_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['home_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['away_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['winner_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
    )

    # =============================================================================
    # Create indexes for all tables
    # =============================================================================

    # Drive Data indexes
    op.create_index('idx_football_drives_game_id', 'football_drive_data', ['game_id'])
    op.create_index('idx_football_drives_offense_team_id', 'football_drive_data', ['offense_team_id'])
    op.create_index('idx_football_drives_defense_team_id', 'football_drive_data', ['defense_team_id'])
    op.create_index('idx_football_drives_drive_number', 'football_drive_data', ['drive_number'])
    op.create_index('idx_football_drives_result', 'football_drive_data', ['drive_result'])
    op.create_index('idx_football_drives_quarter', 'football_drive_data', ['start_quarter', 'end_quarter'])
    op.create_index('idx_football_drives_field_position', 'football_drive_data', ['start_field_position'])
    op.create_index('idx_football_drives_points', 'football_drive_data', ['points_scored'])
    op.create_index('idx_football_drives_situational', 'football_drive_data', ['is_red_zone_drive', 'is_two_minute_drive'])
    op.create_index('idx_football_drives_game_team_drive', 'football_drive_data', ['game_id', 'offense_team_id', 'drive_number'])
    op.create_index('idx_football_drives_external_id', 'football_drive_data', ['external_drive_id'])

    # Play-by-Play indexes
    op.create_index('idx_football_pbp_game_id', 'football_play_by_play', ['game_id'])
    op.create_index('idx_football_pbp_drive_id', 'football_play_by_play', ['drive_id'])
    op.create_index('idx_football_pbp_offense_team_id', 'football_play_by_play', ['offense_team_id'])
    op.create_index('idx_football_pbp_defense_team_id', 'football_play_by_play', ['defense_team_id'])
    op.create_index('idx_football_pbp_play_number', 'football_play_by_play', ['play_number'])
    op.create_index('idx_football_pbp_quarter', 'football_play_by_play', ['quarter'])
    op.create_index('idx_football_pbp_down', 'football_play_by_play', ['down'])
    op.create_index('idx_football_pbp_down_type', 'football_play_by_play', ['down_type'])
    op.create_index('idx_football_pbp_field_position', 'football_play_by_play', ['field_position'])
    op.create_index('idx_football_pbp_play_type', 'football_play_by_play', ['play_type'])
    op.create_index('idx_football_pbp_play_result', 'football_play_by_play', ['play_result'])
    op.create_index('idx_football_pbp_is_pass', 'football_play_by_play', ['is_pass'])
    op.create_index('idx_football_pbp_is_rush', 'football_play_by_play', ['is_rush'])
    op.create_index('idx_football_pbp_is_special_teams', 'football_play_by_play', ['is_special_teams'])
    op.create_index('idx_football_pbp_is_touchdown', 'football_play_by_play', ['is_touchdown'])
    op.create_index('idx_football_pbp_is_turnover', 'football_play_by_play', ['is_turnover'])
    op.create_index('idx_football_pbp_is_penalty', 'football_play_by_play', ['is_penalty'])
    op.create_index('idx_football_pbp_primary_player_id', 'football_play_by_play', ['primary_player_id'])
    op.create_index('idx_football_pbp_game_play', 'football_play_by_play', ['game_id', 'play_number'])
    op.create_index('idx_football_pbp_game_quarter', 'football_play_by_play', ['game_id', 'quarter'])
    op.create_index('idx_football_pbp_external_id', 'football_play_by_play', ['external_play_id'])
    op.create_index('idx_football_pbp_situational', 'football_play_by_play', ['down', 'distance', 'field_position'])
    op.create_index('idx_football_pbp_analytics', 'football_play_by_play', ['is_successful_play', 'is_explosive_play', 'is_stuff'])

    # Player Statistics indexes
    op.create_index('idx_football_player_stats_player_id', 'football_player_statistics', ['player_id'])
    op.create_index('idx_football_player_stats_game_id', 'football_player_statistics', ['game_id'])
    op.create_index('idx_football_player_stats_team_id', 'football_player_statistics', ['team_id'])
    op.create_index('idx_football_player_stats_season_id', 'football_player_statistics', ['season_id'])
    op.create_index('idx_football_player_stats_type', 'football_player_statistics', ['statistic_type'])
    op.create_index('idx_football_player_stats_position', 'football_player_statistics', ['position_group'])
    op.create_index('idx_football_player_stats_player_season', 'football_player_statistics', ['player_id', 'season_id'])
    op.create_index('idx_football_player_stats_player_game', 'football_player_statistics', ['player_id', 'game_id'])
    op.create_index('idx_football_player_stats_team_season', 'football_player_statistics', ['team_id', 'season_id'])
    op.create_index('idx_football_player_stats_passing', 'football_player_statistics', ['passing_yards', 'passing_touchdowns'])
    op.create_index('idx_football_player_stats_rushing', 'football_player_statistics', ['rushing_yards', 'rushing_touchdowns'])
    op.create_index('idx_football_player_stats_receiving', 'football_player_statistics', ['receiving_yards', 'receiving_touchdowns'])
    op.create_index('idx_football_player_stats_defense', 'football_player_statistics', ['tackles_total', 'sacks', 'interceptions'])

    # Team Statistics indexes
    op.create_index('idx_football_team_stats_team_id', 'football_team_statistics', ['team_id'])
    op.create_index('idx_football_team_stats_opponent_id', 'football_team_statistics', ['opponent_id'])
    op.create_index('idx_football_team_stats_game_id', 'football_team_statistics', ['game_id'])
    op.create_index('idx_football_team_stats_season_id', 'football_team_statistics', ['season_id'])
    op.create_index('idx_football_team_stats_type', 'football_team_statistics', ['statistic_type'])
    op.create_index('idx_football_team_stats_team_season', 'football_team_statistics', ['team_id', 'season_id'])
    op.create_index('idx_football_team_stats_team_game', 'football_team_statistics', ['team_id', 'game_id'])
    op.create_index('idx_football_team_stats_offensive', 'football_team_statistics', ['total_yards', 'points_for'])
    op.create_index('idx_football_team_stats_defensive', 'football_team_statistics', ['defensive_yards_allowed', 'points_against'])

    # Advanced Metrics indexes
    op.create_index('idx_football_adv_metrics_team_id', 'football_advanced_metrics', ['team_id'])
    op.create_index('idx_football_adv_metrics_player_id', 'football_advanced_metrics', ['player_id'])
    op.create_index('idx_football_adv_metrics_game_id', 'football_advanced_metrics', ['game_id'])
    op.create_index('idx_football_adv_metrics_season_id', 'football_advanced_metrics', ['season_id'])
    op.create_index('idx_football_adv_metrics_type', 'football_advanced_metrics', ['metric_type'])
    op.create_index('idx_football_adv_metrics_category', 'football_advanced_metrics', ['metric_category'])
    op.create_index('idx_football_adv_metrics_position', 'football_advanced_metrics', ['position_group'])
    op.create_index('idx_football_adv_metrics_situation', 'football_advanced_metrics', ['situation_filter'])
    op.create_index('idx_football_adv_metrics_team_season', 'football_advanced_metrics', ['team_id', 'season_id'])
    op.create_index('idx_football_adv_metrics_player_season', 'football_advanced_metrics', ['player_id', 'season_id'])
    op.create_index('idx_football_adv_metrics_calculation_date', 'football_advanced_metrics', ['calculation_date'])
    op.create_index('idx_football_adv_metrics_value', 'football_advanced_metrics', ['metric_value'])
    op.create_index('idx_football_adv_metrics_percentile', 'football_advanced_metrics', ['percentile_rank'])

    # Game Statistics indexes
    op.create_index('idx_football_game_stats_game_id', 'football_game_statistics', ['game_id'])
    op.create_index('idx_football_game_stats_home_team_id', 'football_game_statistics', ['home_team_id'])
    op.create_index('idx_football_game_stats_away_team_id', 'football_game_statistics', ['away_team_id'])
    op.create_index('idx_football_game_stats_season_id', 'football_game_statistics', ['season_id'])
    op.create_index('idx_football_game_stats_winner_id', 'football_game_statistics', ['winner_id'])
    op.create_index('idx_football_game_stats_scores', 'football_game_statistics', ['home_score', 'away_score'])
    op.create_index('idx_football_game_stats_margin', 'football_game_statistics', ['margin_of_victory'])
    op.create_index('idx_football_game_stats_rivalry', 'football_game_statistics', ['rivalry_game'])
    op.create_index('idx_football_game_stats_conference', 'football_game_statistics', ['conference_game'])
    op.create_index('idx_football_game_stats_teams', 'football_game_statistics', ['home_team_id', 'away_team_id'])
    op.create_index('idx_football_game_stats_season_teams', 'football_game_statistics', ['season_id', 'home_team_id', 'away_team_id'])

    # =============================================================================
    # Create unique constraints
    # =============================================================================

    op.create_unique_constraint('uq_football_drives_game_team_number', 'football_drive_data', ['game_id', 'offense_team_id', 'drive_number'])
    op.create_unique_constraint('uq_football_pbp_game_play_number', 'football_play_by_play', ['game_id', 'play_number'])
    op.create_unique_constraint('uq_football_player_stats_player_game_type', 'football_player_statistics', ['player_id', 'game_id', 'statistic_type'])
    op.create_unique_constraint('uq_football_player_stats_player_season_type', 'football_player_statistics', ['player_id', 'season_id', 'statistic_type'])
    op.create_unique_constraint('uq_football_team_stats_team_game_type', 'football_team_statistics', ['team_id', 'game_id', 'statistic_type'])
    op.create_unique_constraint('uq_football_team_stats_team_season_type', 'football_team_statistics', ['team_id', 'season_id', 'statistic_type'])
    op.create_unique_constraint('uq_football_adv_metrics_context_type', 'football_advanced_metrics', ['team_id', 'player_id', 'game_id', 'season_id', 'metric_type', 'situation_filter'])
    op.create_unique_constraint('uq_football_game_stats_game', 'football_game_statistics', ['game_id'])


def downgrade():
    """Drop College Football Phase 2 tables and enums"""

    # Drop indexes first (they'll be dropped with tables, but explicit for clarity)
    op.drop_table('football_game_statistics')
    op.drop_table('football_advanced_metrics')
    op.drop_table('football_team_statistics')
    op.drop_table('football_player_statistics')
    op.drop_table('football_play_by_play')
    op.drop_table('football_drive_data')

    # Drop enums
    postgresql.ENUM(name='gamesituation').drop(op.get_bind())
    postgresql.ENUM(name='advancedmetrictype').drop(op.get_bind())
    postgresql.ENUM(name='penaltytype').drop(op.get_bind())
    postgresql.ENUM(name='defensiveplaytype').drop(op.get_bind())
    postgresql.ENUM(name='rushtype').drop(op.get_bind())
    postgresql.ENUM(name='passlength').drop(op.get_bind())
    postgresql.ENUM(name='playdirection').drop(op.get_bind())
    postgresql.ENUM(name='downtype').drop(op.get_bind())
    postgresql.ENUM(name='fieldposition').drop(op.get_bind())
    postgresql.ENUM(name='driveresult').drop(op.get_bind())
    postgresql.ENUM(name='playresult').drop(op.get_bind())