"""Phase 2: Academic framework - years, seasons, and conference membership tracking

Revision ID: 20250921_1700_phase2_academic_framework
Revises: 20250921_1635_phase1_college_basketball_seed_data
Create Date: 2025-09-21 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250921_1700_phase2_academic_framework'
down_revision: Union[str, None] = '20250921_1635_phase1_college_basketball_seed_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Phase 2 academic framework schema."""

    # Create enum types for Phase 2
    season_type_enum = postgresql.ENUM(
        'regular_season', 'conference_tournament', 'postseason', 'ncaa_tournament',
        'nit', 'cbi', 'cit', 'exhibition', 'preseason',
        name='seasontype'
    )
    season_type_enum.create(op.get_bind())

    semester_type_enum = postgresql.ENUM(
        'fall', 'spring', 'summer', 'winter',
        name='semestertype'
    )
    semester_type_enum.create(op.get_bind())

    academic_year_status_enum = postgresql.ENUM(
        'current', 'future', 'past', 'active',
        name='academicyearstatus'
    )
    academic_year_status_enum.create(op.get_bind())

    conference_membership_type_enum = postgresql.ENUM(
        'full_member', 'associate_member', 'affiliate_member', 'provisional_member',
        name='conferencemembershiptype'
    )
    conference_membership_type_enum.create(op.get_bind())

    # Create academic_years table
    op.create_table('academic_years',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('start_year', sa.Integer(), nullable=False),
        sa.Column('end_year', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', academic_year_status_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )

    # Create indexes for academic_years
    op.create_index('idx_academic_years_start_year', 'academic_years', ['start_year'])
    op.create_index('idx_academic_years_status', 'academic_years', ['status'])
    op.create_index('idx_academic_years_dates', 'academic_years', ['start_date', 'end_date'])
    op.create_index('idx_academic_years_slug', 'academic_years', ['slug'])

    # Create seasons table
    op.create_table('seasons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=150), nullable=False),
        sa.Column('season_type', season_type_enum, nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('max_regular_season_games', sa.Integer(), nullable=True),
        sa.Column('conference_tournament_start', sa.Date(), nullable=True),
        sa.Column('selection_sunday', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('academic_year_id', 'slug', name='uq_seasons_academic_year_slug'),
        sa.UniqueConstraint('academic_year_id', 'season_type', name='uq_seasons_academic_year_type')
    )

    # Create indexes for seasons
    op.create_index('idx_seasons_academic_year_id', 'seasons', ['academic_year_id'])
    op.create_index('idx_seasons_type', 'seasons', ['season_type'])
    op.create_index('idx_seasons_dates', 'seasons', ['start_date', 'end_date'])
    op.create_index('idx_seasons_slug', 'seasons', ['slug'])
    op.create_index('idx_seasons_current', 'seasons', ['is_current'])

    # Create conference_memberships table
    op.create_table('conference_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('college_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('membership_type', conference_membership_type_enum, nullable=False),
        sa.Column('status', postgresql.ENUM(name='conferencestatus'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('announced_date', sa.Date(), nullable=True),
        sa.Column('is_primary_sport', sa.Boolean(), nullable=False, default=True),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'college_id', 'conference_id', 'academic_year_id', 'sport_id',
            name='uq_conference_memberships_college_conference_year_sport'
        )
    )

    # Create indexes for conference_memberships
    op.create_index('idx_conference_memberships_college_id', 'conference_memberships', ['college_id'])
    op.create_index('idx_conference_memberships_conference_id', 'conference_memberships', ['conference_id'])
    op.create_index('idx_conference_memberships_academic_year_id', 'conference_memberships', ['academic_year_id'])
    op.create_index('idx_conference_memberships_status', 'conference_memberships', ['status'])
    op.create_index('idx_conference_memberships_dates', 'conference_memberships', ['start_date', 'end_date'])
    op.create_index('idx_conference_memberships_primary_sport', 'conference_memberships', ['is_primary_sport'])

    # Create season_configurations table
    op.create_table('season_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('setting_key', sa.String(length=100), nullable=False),
        sa.Column('setting_value', sa.Text(), nullable=False),
        sa.Column('setting_type', sa.String(length=50), nullable=False, default='string'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'season_id', 'conference_id', 'setting_key',
            name='uq_season_configurations_season_conference_key'
        )
    )

    # Create indexes for season_configurations
    op.create_index('idx_season_configurations_season_id', 'season_configurations', ['season_id'])
    op.create_index('idx_season_configurations_conference_id', 'season_configurations', ['conference_id'])
    op.create_index('idx_season_configurations_key', 'season_configurations', ['setting_key'])
    op.create_index('idx_season_configurations_active', 'season_configurations', ['is_active'])

    print("✅ Phase 2 academic framework schema has been created!")


def downgrade() -> None:
    """Remove Phase 2 academic framework schema."""

    # Drop tables in reverse order
    op.drop_table('season_configurations')
    op.drop_table('conference_memberships')
    op.drop_table('seasons')
    op.drop_table('academic_years')

    # Drop enum types
    season_type_enum = postgresql.ENUM(name='seasontype')
    season_type_enum.drop(op.get_bind())

    semester_type_enum = postgresql.ENUM(name='semestertype')
    semester_type_enum.drop(op.get_bind())

    academic_year_status_enum = postgresql.ENUM(name='academicyearstatus')
    academic_year_status_enum.drop(op.get_bind())

    conference_membership_type_enum = postgresql.ENUM(name='conferencemembershiptype')
    conference_membership_type_enum.drop(op.get_bind())

    print("✅ Phase 2 academic framework schema has been removed!")