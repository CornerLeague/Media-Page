"""College Football Phase 4: Recruiting and Transfer Portal Integration

Revision ID: college_football_phase4
Revises: 20250921_2035
Create Date: 2025-09-21 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'college_football_phase4'
down_revision = '20250921_2035'
branch_labels = None
depends_on = None


def upgrade():
    # Add new enums for Phase 4
    op.execute("CREATE TYPE recruitingstarrating AS ENUM ('2_star', '3_star', '4_star', '5_star')")
    op.execute("CREATE TYPE recruitingstatus AS ENUM ('initial_contact', 'showing_interest', 'offered', 'visiting', 'committed', 'signed', 'enrolled', 'decommitted', 'lost_to_competitor')")
    op.execute("CREATE TYPE commitmentstatus AS ENUM ('uncommitted', 'soft_commit', 'committed', 'signed', 'decommitted', 'enrolled')")
    op.execute("CREATE TYPE visittype AS ENUM ('unofficial', 'official', 'junior_day', 'camp_visit', 'game_day')")
    op.execute("CREATE TYPE transferreason AS ENUM ('playing_time', 'coaching_change', 'academic_reasons', 'family_reasons', 'scheme_fit', 'development_opportunities', 'disciplinary', 'medical', 'personal', 'graduate_transfer', 'other')")
    op.execute("CREATE TYPE transferstatus AS ENUM ('in_portal', 'committed', 'signed', 'enrolled', 'returned_to_original', 'withdrawn', 'dismissed')")
    op.execute("CREATE TYPE eligibilitytype AS ENUM ('academic', 'athletic', 'transfer', 'ncaa_clearinghouse', 'medical', 'disciplinary')")
    op.execute("CREATE TYPE coachingposition AS ENUM ('head_coach', 'offensive_coordinator', 'defensive_coordinator', 'special_teams_coordinator', 'quarterbacks_coach', 'running_backs_coach', 'wide_receivers_coach', 'tight_ends_coach', 'offensive_line_coach', 'defensive_line_coach', 'linebackers_coach', 'defensive_backs_coach', 'safeties_coach', 'cornerbacks_coach', 'recruiting_coordinator', 'strength_conditioning', 'quality_control', 'graduate_assistant', 'analyst')")
    op.execute("CREATE TYPE coachinglevel AS ENUM ('head_coach', 'coordinator', 'position_coach', 'assistant_coach', 'graduate_assistant', 'quality_control', 'analyst', 'support_staff')")
    op.execute("CREATE TYPE contractstatus AS ENUM ('active', 'expired', 'terminated', 'resigned', 'retired', 'suspended', 'on_leave')")
    op.execute("CREATE TYPE nildealtype AS ENUM ('endorsement', 'social_media', 'appearance', 'autograph_session', 'camp_instruction', 'merchandise', 'licensing', 'content_creation', 'promotional', 'collective', 'other')")
    op.execute("CREATE TYPE nilcategory AS ENUM ('traditional_advertising', 'social_media_promotion', 'personal_appearances', 'camps_and_lessons', 'autographs_memorabilia', 'merchandise_sales', 'content_creation', 'charity_work', 'business_ventures', 'collective_payments')")
    op.execute("CREATE TYPE compliancestatus AS ENUM ('pending_review', 'approved', 'conditionally_approved', 'denied', 'under_review', 'requires_modification', 'violation_suspected')")
    op.execute("CREATE TYPE portalentryreason AS ENUM ('lack_of_playing_time', 'coaching_staff_change', 'scheme_change', 'closer_to_home', 'academic_program', 'graduate_school', 'injury_concerns', 'team_culture', 'development_opportunity', 'disciplinary_issues', 'family_emergency', 'better_fit', 'conference_move', 'nfl_preparation')")
    op.execute("CREATE TYPE recruitingperiod AS ENUM ('contact_period', 'evaluation_period', 'quiet_period', 'dead_period')")
    op.execute("CREATE TYPE signingperiod AS ENUM ('early_signing_period', 'regular_signing_period', 'late_signing_period')")

    # Create football_recruiting_classes table
    op.create_table('football_recruiting_classes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('class_year', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('early_signing_period_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('regular_signing_period_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('late_period_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('full_scholarships_used', sa.Integer(), nullable=False, default=0),
        sa.Column('partial_scholarships_used', sa.Numeric(precision=5, scale=3), nullable=False, default=0),
        sa.Column('total_scholarship_count', sa.Numeric(precision=5, scale=3), nullable=False, default=0),
        sa.Column('offensive_line_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('quarterback_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('running_back_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('wide_receiver_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('tight_end_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('defensive_line_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('linebacker_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('defensive_back_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('special_teams_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('in_state_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('out_of_state_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('international_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('transfer_additions', sa.Integer(), nullable=False, default=0),
        sa.Column('graduate_transfer_additions', sa.Integer(), nullable=False, default=0),
        sa.Column('national_ranking', sa.Integer(), nullable=True),
        sa.Column('conference_ranking', sa.Integer(), nullable=True),
        sa.Column('class_rating', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('average_star_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('five_star_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('four_star_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('three_star_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('two_star_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('unrated_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('top_100_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('top_300_commits', sa.Integer(), nullable=False, default=0),
        sa.Column('is_complete', sa.Boolean(), nullable=False, default=False),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('early_enrollees', sa.Integer(), nullable=False, default=0),
        sa.Column('decommitments', sa.Integer(), nullable=False, default=0),
        sa.Column('signings_not_qualified', sa.Integer(), nullable=False, default=0),
        sa.Column('class_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'class_year', name='uq_football_recruiting_classes_team_year')
    )

    # Create indexes for football_recruiting_classes
    op.create_index('idx_football_recruiting_classes_team_id', 'football_recruiting_classes', ['team_id'])
    op.create_index('idx_football_recruiting_classes_academic_year_id', 'football_recruiting_classes', ['academic_year_id'])
    op.create_index('idx_football_recruiting_classes_class_year', 'football_recruiting_classes', ['class_year'])
    op.create_index('idx_football_recruiting_classes_team_year', 'football_recruiting_classes', ['team_id', 'class_year'])
    op.create_index('idx_football_recruiting_classes_ranking', 'football_recruiting_classes', ['national_ranking'])
    op.create_index('idx_football_recruiting_classes_complete', 'football_recruiting_classes', ['is_complete'])

    # Create football_recruits table
    op.create_table('football_recruits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recruiting_class_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('high_school', sa.String(length=200), nullable=False),
        sa.Column('high_school_city', sa.String(length=100), nullable=False),
        sa.Column('high_school_state', sa.String(length=50), nullable=False),
        sa.Column('high_school_country', sa.String(length=50), nullable=False, default='USA'),
        sa.Column('graduation_year', sa.Integer(), nullable=False),
        sa.Column('primary_position', sa.Enum('QB', 'RB', 'FB', 'WR', 'TE', 'OL', 'C', 'G', 'T', 'DL', 'DE', 'DT', 'NT', 'LB', 'ILB', 'OLB', 'DB', 'CB', 'S', 'FS', 'SS', 'K', 'P', 'LS', 'KR', 'PR', 'ATH', name='footballposition'), nullable=False),
        sa.Column('secondary_position', sa.Enum('QB', 'RB', 'FB', 'WR', 'TE', 'OL', 'C', 'G', 'T', 'DL', 'DE', 'DT', 'NT', 'LB', 'ILB', 'OLB', 'DB', 'CB', 'S', 'FS', 'SS', 'K', 'P', 'LS', 'KR', 'PR', 'ATH', name='footballposition'), nullable=True),
        sa.Column('position_group', sa.Enum('OFFENSE', 'DEFENSE', 'SPECIAL_TEAMS', 'QUARTERBACK', 'RUNNING_BACK', 'OFFENSIVE_LINE', 'RECEIVER', 'TIGHT_END', 'DEFENSIVE_LINE', 'LINEBACKER', 'DEFENSIVE_BACK', 'KICKER', 'PUNTER', name='footballpositiongroup'), nullable=False),
        sa.Column('height_inches', sa.Integer(), nullable=True),
        sa.Column('weight_pounds', sa.Integer(), nullable=True),
        sa.Column('forty_yard_dash', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('bench_press', sa.Integer(), nullable=True),
        sa.Column('vertical_jump', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('composite_rating', sa.Numeric(precision=6, scale=4), nullable=True),
        sa.Column('star_rating', postgresql.ENUM('2_star', '3_star', '4_star', '5_star', name='recruitingstarrating'), nullable=True),
        sa.Column('national_ranking', sa.Integer(), nullable=True),
        sa.Column('position_ranking', sa.Integer(), nullable=True),
        sa.Column('state_ranking', sa.Integer(), nullable=True),
        sa.Column('commitment_status', postgresql.ENUM('uncommitted', 'soft_commit', 'committed', 'signed', 'decommitted', 'enrolled', name='commitmentstatus'), nullable=False, default='uncommitted'),
        sa.Column('committed_to_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('commitment_date', sa.Date(), nullable=True),
        sa.Column('signing_date', sa.Date(), nullable=True),
        sa.Column('enrollment_date', sa.Date(), nullable=True),
        sa.Column('is_early_enrollee', sa.Boolean(), nullable=False, default=False),
        sa.Column('early_enrollment_date', sa.Date(), nullable=True),
        sa.Column('decommitment_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_decommitment_date', sa.Date(), nullable=True),
        sa.Column('academic_eligibility_status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('clearinghouse_status', sa.String(length=50), nullable=True),
        sa.Column('core_gpa', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('sat_score', sa.Integer(), nullable=True),
        sa.Column('act_score', sa.Integer(), nullable=True),
        sa.Column('scholarship_offered', sa.Boolean(), nullable=False, default=False),
        sa.Column('scholarship_type', sa.Enum('FULL_SCHOLARSHIP', 'PARTIAL_SCHOLARSHIP', 'WALK_ON', 'PREFERRED_WALK_ON', name='scholarshiptype'), nullable=True),
        sa.Column('scholarship_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('total_offers', sa.Integer(), nullable=False, default=0),
        sa.Column('top_schools', sa.Text(), nullable=True),
        sa.Column('first_contact_date', sa.Date(), nullable=True),
        sa.Column('first_offer_date', sa.Date(), nullable=True),
        sa.Column('official_visit_date', sa.Date(), nullable=True),
        sa.Column('official_visits_taken', sa.Integer(), nullable=False, default=0),
        sa.Column('unofficial_visits_taken', sa.Integer(), nullable=False, default=0),
        sa.Column('parent_contact', sa.Text(), nullable=True),
        sa.Column('family_notes', sa.Text(), nullable=True),
        sa.Column('twitter_handle', sa.String(length=100), nullable=True),
        sa.Column('instagram_handle', sa.String(length=100), nullable=True),
        sa.Column('hudl_profile', sa.String(length=500), nullable=True),
        sa.Column('highlight_film_url', sa.String(length=500), nullable=True),
        sa.Column('recruiting_notes', sa.Text(), nullable=True),
        sa.Column('character_concerns', sa.Text(), nullable=True),
        sa.Column('injury_history', sa.Text(), nullable=True),
        sa.Column('rivals_id', sa.String(length=100), nullable=True),
        sa.Column('two_four_seven_id', sa.String(length=100), nullable=True),
        sa.Column('espn_id', sa.String(length=100), nullable=True),
        sa.Column('on3_id', sa.String(length=100), nullable=True),
        sa.Column('is_active_recruit', sa.Boolean(), nullable=False, default=True),
        sa.Column('recruiting_priority', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['committed_to_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recruiting_class_id'], ['football_recruiting_classes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for football_recruits
    op.create_index('idx_football_recruits_recruiting_class_id', 'football_recruits', ['recruiting_class_id'])
    op.create_index('idx_football_recruits_full_name', 'football_recruits', ['full_name'])
    op.create_index('idx_football_recruits_last_name', 'football_recruits', ['last_name'])
    op.create_index('idx_football_recruits_graduation_year', 'football_recruits', ['graduation_year'])
    op.create_index('idx_football_recruits_position', 'football_recruits', ['primary_position'])
    op.create_index('idx_football_recruits_position_group', 'football_recruits', ['position_group'])
    op.create_index('idx_football_recruits_state', 'football_recruits', ['high_school_state'])
    op.create_index('idx_football_recruits_commitment', 'football_recruits', ['commitment_status'])
    op.create_index('idx_football_recruits_committed_team', 'football_recruits', ['committed_to_team_id'])
    op.create_index('idx_football_recruits_star_rating', 'football_recruits', ['star_rating'])
    op.create_index('idx_football_recruits_rankings', 'football_recruits', ['national_ranking', 'position_ranking'])
    op.create_index('idx_football_recruits_active', 'football_recruits', ['is_active_recruit'])
    op.create_index('idx_football_recruits_graduation_position', 'football_recruits', ['graduation_year', 'position_group'])

    # Create football_recruiting_offers table
    op.create_table('football_recruiting_offers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recruit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('offer_date', sa.Date(), nullable=False),
        sa.Column('scholarship_type', sa.Enum('FULL_SCHOLARSHIP', 'PARTIAL_SCHOLARSHIP', 'WALK_ON', 'PREFERRED_WALK_ON', name='scholarshiptype'), nullable=False),
        sa.Column('scholarship_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('response_date', sa.Date(), nullable=True),
        sa.Column('response_status', sa.String(length=50), nullable=True),
        sa.Column('recruiting_coach', sa.String(length=200), nullable=True),
        sa.Column('offer_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['recruit_id'], ['football_recruits.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recruit_id', 'team_id', 'offer_date', name='uq_football_recruiting_offers')
    )

    # Create indexes for football_recruiting_offers
    op.create_index('idx_football_recruiting_offers_recruit_id', 'football_recruiting_offers', ['recruit_id'])
    op.create_index('idx_football_recruiting_offers_team_id', 'football_recruiting_offers', ['team_id'])
    op.create_index('idx_football_recruiting_offers_date', 'football_recruiting_offers', ['offer_date'])
    op.create_index('idx_football_recruiting_offers_active', 'football_recruiting_offers', ['is_active'])

    # Create football_recruiting_visits table
    op.create_table('football_recruiting_visits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recruit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('visit_date', sa.Date(), nullable=False),
        sa.Column('visit_type', postgresql.ENUM('unofficial', 'official', 'junior_day', 'camp_visit', 'game_day', name='visittype'), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('host_player', sa.String(length=200), nullable=True),
        sa.Column('primary_coach_contact', sa.String(length=200), nullable=True),
        sa.Column('attended_practice', sa.Boolean(), nullable=False, default=False),
        sa.Column('attended_game', sa.Boolean(), nullable=False, default=False),
        sa.Column('game_attended', sa.String(length=200), nullable=True),
        sa.Column('met_with_academics', sa.Boolean(), nullable=False, default=False),
        sa.Column('campus_tour', sa.Boolean(), nullable=False, default=False),
        sa.Column('family_members_attended', sa.Text(), nullable=True),
        sa.Column('family_accommodation', sa.String(length=200), nullable=True),
        sa.Column('visit_rating', sa.Integer(), nullable=True),
        sa.Column('positive_feedback', sa.Text(), nullable=True),
        sa.Column('concerns_noted', sa.Text(), nullable=True),
        sa.Column('follow_up_planned', sa.Boolean(), nullable=False, default=False),
        sa.Column('visit_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['recruit_id'], ['football_recruits.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recruit_id', 'team_id', 'visit_date', name='uq_football_recruiting_visits')
    )

    # Create indexes for football_recruiting_visits
    op.create_index('idx_football_recruiting_visits_recruit_id', 'football_recruiting_visits', ['recruit_id'])
    op.create_index('idx_football_recruiting_visits_team_id', 'football_recruiting_visits', ['team_id'])
    op.create_index('idx_football_recruiting_visits_date', 'football_recruiting_visits', ['visit_date'])
    op.create_index('idx_football_recruiting_visits_type', 'football_recruiting_visits', ['visit_type'])

    # Create football_transfer_portal_entries table
    op.create_table('football_transfer_portal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('previous_team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('previous_college_name', sa.String(length=200), nullable=False),
        sa.Column('portal_entry_date', sa.Date(), nullable=False),
        sa.Column('portal_entry_reason', postgresql.ENUM('lack_of_playing_time', 'coaching_staff_change', 'scheme_change', 'closer_to_home', 'academic_program', 'graduate_school', 'injury_concerns', 'team_culture', 'development_opportunity', 'disciplinary_issues', 'family_emergency', 'better_fit', 'conference_move', 'nfl_preparation', name='portalentryreason'), nullable=False),
        sa.Column('is_graduate_transfer', sa.Boolean(), nullable=False, default=False),
        sa.Column('primary_position', sa.Enum('QB', 'RB', 'FB', 'WR', 'TE', 'OL', 'C', 'G', 'T', 'DL', 'DE', 'DT', 'NT', 'LB', 'ILB', 'OLB', 'DB', 'CB', 'S', 'FS', 'SS', 'K', 'P', 'LS', 'KR', 'PR', 'ATH', name='footballposition'), nullable=False),
        sa.Column('position_group', sa.Enum('OFFENSE', 'DEFENSE', 'SPECIAL_TEAMS', 'QUARTERBACK', 'RUNNING_BACK', 'OFFENSIVE_LINE', 'RECEIVER', 'TIGHT_END', 'DEFENSIVE_LINE', 'LINEBACKER', 'DEFENSIVE_BACK', 'KICKER', 'PUNTER', name='footballpositiongroup'), nullable=False),
        sa.Column('current_class', sa.Enum('FRESHMAN', 'SOPHOMORE', 'JUNIOR', 'SENIOR', 'GRADUATE', 'REDSHIRT_FRESHMAN', 'REDSHIRT_SOPHOMORE', 'REDSHIRT_JUNIOR', 'REDSHIRT_SENIOR', name='playerclass'), nullable=False),
        sa.Column('years_of_eligibility_remaining', sa.Integer(), nullable=False),
        sa.Column('height_inches', sa.Integer(), nullable=True),
        sa.Column('weight_pounds', sa.Integer(), nullable=True),
        sa.Column('previous_college_stats', sa.Text(), nullable=True),
        sa.Column('games_played_previous', sa.Integer(), nullable=True),
        sa.Column('years_at_previous_school', sa.Integer(), nullable=False),
        sa.Column('new_team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('commitment_date', sa.Date(), nullable=True),
        sa.Column('enrollment_date', sa.Date(), nullable=True),
        sa.Column('transfer_status', postgresql.ENUM('in_portal', 'committed', 'signed', 'enrolled', 'returned_to_original', 'withdrawn', 'dismissed', name='transferstatus'), nullable=False, default='in_portal'),
        sa.Column('immediate_eligibility', sa.Boolean(), nullable=False, default=False),
        sa.Column('waiver_filed', sa.Boolean(), nullable=False, default=False),
        sa.Column('waiver_status', sa.String(length=50), nullable=True),
        sa.Column('sit_out_required', sa.Boolean(), nullable=False, default=True),
        sa.Column('academic_standing', sa.String(length=50), nullable=True),
        sa.Column('gpa', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('degree_progress', sa.String(length=100), nullable=True),
        sa.Column('graduation_date', sa.Date(), nullable=True),
        sa.Column('scholarship_status', sa.String(length=50), nullable=True),
        sa.Column('scholarship_type', sa.Enum('FULL_SCHOLARSHIP', 'PARTIAL_SCHOLARSHIP', 'WALK_ON', 'PREFERRED_WALK_ON', name='scholarshiptype'), nullable=True),
        sa.Column('transfer_reason_detail', sa.Text(), nullable=True),
        sa.Column('coaching_change_factor', sa.Boolean(), nullable=False, default=False),
        sa.Column('playing_time_factor', sa.Boolean(), nullable=False, default=False),
        sa.Column('academic_factor', sa.Boolean(), nullable=False, default=False),
        sa.Column('family_factor', sa.Boolean(), nullable=False, default=False),
        sa.Column('portal_window_type', sa.String(length=50), nullable=True),
        sa.Column('deadline_date', sa.Date(), nullable=True),
        sa.Column('receiving_interest_from', sa.Text(), nullable=True),
        sa.Column('official_visits_scheduled', sa.Integer(), nullable=False, default=0),
        sa.Column('offers_received', sa.Integer(), nullable=False, default=0),
        sa.Column('social_media_announcement', sa.Text(), nullable=True),
        sa.Column('twitter_handle', sa.String(length=100), nullable=True),
        sa.Column('final_destination', sa.String(length=200), nullable=True),
        sa.Column('portal_outcome', sa.String(length=50), nullable=True),
        sa.Column('portal_exit_date', sa.Date(), nullable=True),
        sa.Column('transfer_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['new_team_id'], ['football_teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['player_id'], ['football_players.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['previous_team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for football_transfer_portal_entries
    op.create_index('idx_football_transfer_portal_player_id', 'football_transfer_portal_entries', ['player_id'])
    op.create_index('idx_football_transfer_portal_previous_team', 'football_transfer_portal_entries', ['previous_team_id'])
    op.create_index('idx_football_transfer_portal_new_team', 'football_transfer_portal_entries', ['new_team_id'])
    op.create_index('idx_football_transfer_portal_entry_date', 'football_transfer_portal_entries', ['portal_entry_date'])
    op.create_index('idx_football_transfer_portal_status', 'football_transfer_portal_entries', ['transfer_status'])
    op.create_index('idx_football_transfer_portal_position', 'football_transfer_portal_entries', ['primary_position'])
    op.create_index('idx_football_transfer_portal_grad', 'football_transfer_portal_entries', ['is_graduate_transfer'])
    op.create_index('idx_football_transfer_portal_eligibility', 'football_transfer_portal_entries', ['immediate_eligibility'])
    op.create_index('idx_football_transfer_portal_full_name', 'football_transfer_portal_entries', ['full_name'])

    # Create football_coaching_staff table
    op.create_table('football_coaching_staff',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('coaching_position', postgresql.ENUM('head_coach', 'offensive_coordinator', 'defensive_coordinator', 'special_teams_coordinator', 'quarterbacks_coach', 'running_backs_coach', 'wide_receivers_coach', 'tight_ends_coach', 'offensive_line_coach', 'defensive_line_coach', 'linebackers_coach', 'defensive_backs_coach', 'safeties_coach', 'cornerbacks_coach', 'recruiting_coordinator', 'strength_conditioning', 'quality_control', 'graduate_assistant', 'analyst', name='coachingposition'), nullable=False),
        sa.Column('coaching_level', postgresql.ENUM('head_coach', 'coordinator', 'position_coach', 'assistant_coach', 'graduate_assistant', 'quality_control', 'analyst', 'support_staff', name='coachinglevel'), nullable=False),
        sa.Column('position_group_responsibility', sa.Enum('OFFENSE', 'DEFENSE', 'SPECIAL_TEAMS', 'QUARTERBACK', 'RUNNING_BACK', 'OFFENSIVE_LINE', 'RECEIVER', 'TIGHT_END', 'DEFENSIVE_LINE', 'LINEBACKER', 'DEFENSIVE_BACK', 'KICKER', 'PUNTER', name='footballpositiongroup'), nullable=True),
        sa.Column('additional_responsibilities', sa.Text(), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('contract_end_date', sa.Date(), nullable=True),
        sa.Column('contract_status', postgresql.ENUM('active', 'expired', 'terminated', 'resigned', 'retired', 'suspended', 'on_leave', name='contractstatus'), nullable=False, default='active'),
        sa.Column('annual_salary', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('contract_length_years', sa.Integer(), nullable=True),
        sa.Column('buyout_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('performance_bonuses', sa.Text(), nullable=True),
        sa.Column('recruiting_bonuses', sa.Text(), nullable=True),
        sa.Column('previous_positions', sa.Text(), nullable=True),
        sa.Column('college_coaching_years', sa.Integer(), nullable=True),
        sa.Column('nfl_coaching_years', sa.Integer(), nullable=True),
        sa.Column('high_school_coaching_years', sa.Integer(), nullable=True),
        sa.Column('alma_mater', sa.String(length=200), nullable=True),
        sa.Column('degree', sa.String(length=100), nullable=True),
        sa.Column('playing_background', sa.Text(), nullable=True),
        sa.Column('primary_recruiting_region', sa.String(length=200), nullable=True),
        sa.Column('recruiting_states', sa.Text(), nullable=True),
        sa.Column('high_school_contacts', sa.Text(), nullable=True),
        sa.Column('recruiting_specialties', sa.Text(), nullable=True),
        sa.Column('recruiting_rating', sa.Integer(), nullable=True),
        sa.Column('coaching_rating', sa.Integer(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('hometown', sa.String(length=100), nullable=True),
        sa.Column('family_info', sa.Text(), nullable=True),
        sa.Column('twitter_handle', sa.String(length=100), nullable=True),
        sa.Column('linkedin_profile', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('termination_reason', sa.String(length=200), nullable=True),
        sa.Column('coaching_notes', sa.Text(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('areas_for_improvement', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['football_teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'coaching_position', 'academic_year_id', name='uq_football_coaching_staff_team_position_year')
    )

    # Create indexes for football_coaching_staff
    op.create_index('idx_football_coaching_staff_team_id', 'football_coaching_staff', ['team_id'])
    op.create_index('idx_football_coaching_staff_academic_year_id', 'football_coaching_staff', ['academic_year_id'])
    op.create_index('idx_football_coaching_staff_full_name', 'football_coaching_staff', ['full_name'])
    op.create_index('idx_football_coaching_staff_position', 'football_coaching_staff', ['coaching_position'])
    op.create_index('idx_football_coaching_staff_level', 'football_coaching_staff', ['coaching_level'])
    op.create_index('idx_football_coaching_staff_active', 'football_coaching_staff', ['is_active'])
    op.create_index('idx_football_coaching_staff_contract', 'football_coaching_staff', ['contract_status'])
    op.create_index('idx_football_coaching_staff_team_year', 'football_coaching_staff', ['team_id', 'academic_year_id'])

    # Create football_nil_deals table
    op.create_table('football_nil_deals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deal_name', sa.String(length=200), nullable=False),
        sa.Column('deal_type', postgresql.ENUM('endorsement', 'social_media', 'appearance', 'autograph_session', 'camp_instruction', 'merchandise', 'licensing', 'content_creation', 'promotional', 'collective', 'other', name='nildealtype'), nullable=False),
        sa.Column('nil_category', postgresql.ENUM('traditional_advertising', 'social_media_promotion', 'personal_appearances', 'camps_and_lessons', 'autographs_memorabilia', 'merchandise_sales', 'content_creation', 'charity_work', 'business_ventures', 'collective_payments', name='nilcategory'), nullable=False),
        sa.Column('partner_name', sa.String(length=200), nullable=False),
        sa.Column('partner_type', sa.String(length=100), nullable=False),
        sa.Column('partner_location', sa.String(length=200), nullable=True),
        sa.Column('deal_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('payment_structure', sa.String(length=100), nullable=True),
        sa.Column('payment_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('payment_frequency', sa.String(length=50), nullable=True),
        sa.Column('deal_date', sa.Date(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('deal_duration_months', sa.Integer(), nullable=True),
        sa.Column('required_activities', sa.Text(), nullable=True),
        sa.Column('social_media_requirements', sa.Text(), nullable=True),
        sa.Column('appearance_requirements', sa.Text(), nullable=True),
        sa.Column('content_creation_requirements', sa.Text(), nullable=True),
        sa.Column('exclusivity_clauses', sa.Text(), nullable=True),
        sa.Column('engagement_metrics', sa.Text(), nullable=True),
        sa.Column('performance_bonuses', sa.Text(), nullable=True),
        sa.Column('success_metrics', sa.Text(), nullable=True),
        sa.Column('compliance_status', postgresql.ENUM('pending_review', 'approved', 'conditionally_approved', 'denied', 'under_review', 'requires_modification', 'violation_suspected', name='compliancestatus'), nullable=False, default='pending_review'),
        sa.Column('school_approval_required', sa.Boolean(), nullable=False, default=True),
        sa.Column('school_approval_date', sa.Date(), nullable=True),
        sa.Column('ncaa_reporting_required', sa.Boolean(), nullable=False, default=True),
        sa.Column('reporting_date', sa.Date(), nullable=True),
        sa.Column('nil_collective_involved', sa.Boolean(), nullable=False, default=False),
        sa.Column('collective_name', sa.String(length=200), nullable=True),
        sa.Column('booster_involvement', sa.Boolean(), nullable=False, default=False),
        sa.Column('deal_status', sa.String(length=50), nullable=False, default='active'),
        sa.Column('completed_successfully', sa.Boolean(), nullable=True),
        sa.Column('early_termination', sa.Boolean(), nullable=False, default=False),
        sa.Column('termination_reason', sa.Text(), nullable=True),
        sa.Column('deal_description', sa.Text(), nullable=True),
        sa.Column('public_announcement', sa.Boolean(), nullable=False, default=False),
        sa.Column('announcement_date', sa.Date(), nullable=True),
        sa.Column('media_coverage', sa.Text(), nullable=True),
        sa.Column('deal_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['football_players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for football_nil_deals
    op.create_index('idx_football_nil_deals_player_id', 'football_nil_deals', ['player_id'])
    op.create_index('idx_football_nil_deals_deal_date', 'football_nil_deals', ['deal_date'])
    op.create_index('idx_football_nil_deals_deal_type', 'football_nil_deals', ['deal_type'])
    op.create_index('idx_football_nil_deals_category', 'football_nil_deals', ['nil_category'])
    op.create_index('idx_football_nil_deals_partner', 'football_nil_deals', ['partner_name'])
    op.create_index('idx_football_nil_deals_value', 'football_nil_deals', ['deal_value'])
    op.create_index('idx_football_nil_deals_status', 'football_nil_deals', ['deal_status'])
    op.create_index('idx_football_nil_deals_compliance', 'football_nil_deals', ['compliance_status'])
    op.create_index('idx_football_nil_deals_collective', 'football_nil_deals', ['nil_collective_involved'])

    # Create football_eligibility_tracking table
    op.create_table('football_eligibility_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('eligibility_period', sa.String(length=50), nullable=False),
        sa.Column('eligibility_type', postgresql.ENUM('academic', 'athletic', 'transfer', 'ncaa_clearinghouse', 'medical', 'disciplinary', name='eligibilitytype'), nullable=False),
        sa.Column('overall_gpa', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('semester_gpa', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('credit_hours_completed', sa.Integer(), nullable=True),
        sa.Column('credit_hours_current_semester', sa.Integer(), nullable=True),
        sa.Column('degree_progress_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('academic_standing', sa.String(length=50), nullable=False),
        sa.Column('academic_probation', sa.Boolean(), nullable=False, default=False),
        sa.Column('academic_suspension', sa.Boolean(), nullable=False, default=False),
        sa.Column('athletic_eligibility_status', sa.Enum('ELIGIBLE', 'SUSPENDED', 'INJURED', 'MEDICALLY_DISQUALIFIED', 'ACADEMICALLY_INELIGIBLE', 'TRANSFER_PENDING', 'REDSHIRT', 'DISMISSED', name='playereligibilitystatus'), nullable=False, default='ELIGIBLE'),
        sa.Column('years_of_eligibility_used', sa.Integer(), nullable=False, default=0),
        sa.Column('years_of_eligibility_remaining', sa.Integer(), nullable=False, default=4),
        sa.Column('forty_percent_rule_met', sa.Boolean(), nullable=False, default=False),
        sa.Column('sixty_percent_rule_met', sa.Boolean(), nullable=False, default=False),
        sa.Column('eighty_percent_rule_met', sa.Boolean(), nullable=False, default=False),
        sa.Column('transfer_eligibility_status', sa.String(length=50), nullable=True),
        sa.Column('transfer_waiver_status', sa.String(length=50), nullable=True),
        sa.Column('immediate_eligibility_granted', sa.Boolean(), nullable=False, default=False),
        sa.Column('disciplinary_action', sa.Boolean(), nullable=False, default=False),
        sa.Column('suspension_status', sa.Boolean(), nullable=False, default=False),
        sa.Column('suspension_games_remaining', sa.Integer(), nullable=True),
        sa.Column('medical_clearance', sa.Boolean(), nullable=False, default=True),
        sa.Column('injury_status', sa.String(length=200), nullable=True),
        sa.Column('medical_redshirt_eligible', sa.Boolean(), nullable=False, default=False),
        sa.Column('compliance_review_date', sa.Date(), nullable=True),
        sa.Column('compliance_officer_notes', sa.Text(), nullable=True),
        sa.Column('ncaa_clearinghouse_status', sa.String(length=50), nullable=True),
        sa.Column('academic_support_needed', sa.Boolean(), nullable=False, default=False),
        sa.Column('tutoring_hours_weekly', sa.Integer(), nullable=True),
        sa.Column('study_hall_hours_weekly', sa.Integer(), nullable=True),
        sa.Column('last_eligibility_check', sa.Date(), nullable=True),
        sa.Column('next_eligibility_review', sa.Date(), nullable=True),
        sa.Column('eligibility_notes', sa.Text(), nullable=True),
        sa.Column('academic_alerts', sa.Text(), nullable=True),
        sa.Column('compliance_alerts', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['football_players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_id', 'academic_year_id', 'eligibility_period', 'eligibility_type', name='uq_football_eligibility_player_year_period_type')
    )

    # Create indexes for football_eligibility_tracking
    op.create_index('idx_football_eligibility_player_id', 'football_eligibility_tracking', ['player_id'])
    op.create_index('idx_football_eligibility_academic_year_id', 'football_eligibility_tracking', ['academic_year_id'])
    op.create_index('idx_football_eligibility_period', 'football_eligibility_tracking', ['eligibility_period'])
    op.create_index('idx_football_eligibility_type', 'football_eligibility_tracking', ['eligibility_type'])
    op.create_index('idx_football_eligibility_athletic_status', 'football_eligibility_tracking', ['athletic_eligibility_status'])
    op.create_index('idx_football_eligibility_academic_standing', 'football_eligibility_tracking', ['academic_standing'])
    op.create_index('idx_football_eligibility_player_year', 'football_eligibility_tracking', ['player_id', 'academic_year_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('football_eligibility_tracking')
    op.drop_table('football_nil_deals')
    op.drop_table('football_coaching_staff')
    op.drop_table('football_transfer_portal_entries')
    op.drop_table('football_recruiting_visits')
    op.drop_table('football_recruiting_offers')
    op.drop_table('football_recruits')
    op.drop_table('football_recruiting_classes')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS recruitingstarrating")
    op.execute("DROP TYPE IF EXISTS recruitingstatus")
    op.execute("DROP TYPE IF EXISTS commitmentstatus")
    op.execute("DROP TYPE IF EXISTS visittype")
    op.execute("DROP TYPE IF EXISTS transferreason")
    op.execute("DROP TYPE IF EXISTS transferstatus")
    op.execute("DROP TYPE IF EXISTS eligibilitytype")
    op.execute("DROP TYPE IF EXISTS coachingposition")
    op.execute("DROP TYPE IF EXISTS coachinglevel")
    op.execute("DROP TYPE IF EXISTS contractstatus")
    op.execute("DROP TYPE IF EXISTS nildealtype")
    op.execute("DROP TYPE IF EXISTS nilcategory")
    op.execute("DROP TYPE IF EXISTS compliancestatus")
    op.execute("DROP TYPE IF EXISTS portalentryreason")
    op.execute("DROP TYPE IF EXISTS recruitingperiod")
    op.execute("DROP TYPE IF EXISTS signingperiod")