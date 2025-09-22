"""Phase 1: College basketball foundation schema

Revision ID: 20250921_1630_phase1_college_basketball_foundation
Revises: 20250920_0002_seed_college_soccer_teams
Create Date: 2025-09-21 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250921_1630_phase1_college_basketball_foundation'
down_revision: Union[str, None] = '20250920_0002_seed_college_soccer_teams'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Phase 1 college basketball foundation schema."""

    # Create enum types for college-specific enums
    division_level_enum = postgresql.ENUM(
        'D1', 'D2', 'D3', 'NAIA', 'NJCAA',
        name='divisionlevel'
    )
    division_level_enum.create(op.get_bind())

    conference_type_enum = postgresql.ENUM(
        'power_five', 'mid_major', 'low_major', 'independent',
        name='conferencetype'
    )
    conference_type_enum.create(op.get_bind())

    college_type_enum = postgresql.ENUM(
        'public', 'private', 'religious', 'military', 'community',
        name='collegetype'
    )
    college_type_enum.create(op.get_bind())

    region_enum = postgresql.ENUM(
        'northeast', 'southeast', 'midwest', 'southwest', 'west', 'northwest',
        name='region'
    )
    region_enum.create(op.get_bind())

    conference_status_enum = postgresql.ENUM(
        'active', 'departing', 'joining', 'former',
        name='conferencestatus'
    )
    conference_status_enum.create(op.get_bind())

    # Create divisions table
    op.create_table('divisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('level', division_level_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )

    # Create indexes for divisions
    op.create_index('idx_divisions_level', 'divisions', ['level'])
    op.create_index('idx_divisions_slug', 'divisions', ['slug'])
    op.create_index('idx_divisions_display_order', 'divisions', ['display_order'])

    # Create college_conferences table
    op.create_table('college_conferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('division_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('slug', sa.String(length=150), nullable=False),
        sa.Column('abbreviation', sa.String(length=10), nullable=True),
        sa.Column('conference_type', conference_type_enum, nullable=False),
        sa.Column('region', region_enum, nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('headquarters_city', sa.String(length=100), nullable=True),
        sa.Column('headquarters_state', sa.String(length=50), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('secondary_color', sa.String(length=7), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('tournament_format', sa.String(length=100), nullable=True),
        sa.Column('auto_bid_tournament', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['division_id'], ['divisions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('division_id', 'slug', name='uq_college_conferences_division_slug')
    )

    # Create indexes for college_conferences
    op.create_index('idx_college_conferences_division_id', 'college_conferences', ['division_id'])
    op.create_index('idx_college_conferences_slug', 'college_conferences', ['slug'])
    op.create_index('idx_college_conferences_abbreviation', 'college_conferences', ['abbreviation'])
    op.create_index('idx_college_conferences_type_region', 'college_conferences', ['conference_type', 'region'])

    # Create colleges table
    op.create_table('colleges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('short_name', sa.String(length=100), nullable=True),
        sa.Column('abbreviation', sa.String(length=10), nullable=True),
        sa.Column('college_type', college_type_enum, nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('country', sa.String(length=3), nullable=False, default='USA'),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('enrollment', sa.Integer(), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('athletics_website_url', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('secondary_color', sa.String(length=7), nullable=True),
        sa.Column('mascot', sa.String(length=100), nullable=True),
        sa.Column('nickname', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('arena_name', sa.String(length=200), nullable=True),
        sa.Column('arena_capacity', sa.Integer(), nullable=True),
        sa.Column('head_coach', sa.String(length=100), nullable=True),
        sa.Column('coach_since_year', sa.Integer(), nullable=True),
        sa.Column('ncaa_championships', sa.Integer(), nullable=False, default=0),
        sa.Column('final_four_appearances', sa.Integer(), nullable=False, default=0),
        sa.Column('ncaa_tournament_appearances', sa.Integer(), nullable=False, default=0),
        sa.Column('conference_championships', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conference_id'], ['college_conferences.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conference_id', 'slug', name='uq_colleges_conference_slug')
    )

    # Create indexes for colleges
    op.create_index('idx_colleges_conference_id', 'colleges', ['conference_id'])
    op.create_index('idx_colleges_slug', 'colleges', ['slug'])
    op.create_index('idx_colleges_state_city', 'colleges', ['state', 'city'])
    op.create_index('idx_colleges_name_search', 'colleges', ['name'])
    op.create_index('idx_colleges_nickname', 'colleges', ['nickname'])

    # Create college_teams table
    op.create_table('college_teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('college_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('abbreviation', sa.String(length=10), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('current_record_wins', sa.Integer(), nullable=False, default=0),
        sa.Column('current_record_losses', sa.Integer(), nullable=False, default=0),
        sa.Column('conference_record_wins', sa.Integer(), nullable=False, default=0),
        sa.Column('conference_record_losses', sa.Integer(), nullable=False, default=0),
        sa.Column('ap_poll_rank', sa.Integer(), nullable=True),
        sa.Column('coaches_poll_rank', sa.Integer(), nullable=True),
        sa.Column('net_ranking', sa.Integer(), nullable=True),
        sa.Column('kenpom_ranking', sa.Integer(), nullable=True),
        sa.Column('rpi_ranking', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('college_id', 'sport_id', name='uq_college_teams_college_sport'),
        sa.UniqueConstraint('slug', name='uq_college_teams_slug')
    )

    # Create indexes for college_teams
    op.create_index('idx_college_teams_college_id', 'college_teams', ['college_id'])
    op.create_index('idx_college_teams_sport_id', 'college_teams', ['sport_id'])
    op.create_index('idx_college_teams_slug', 'college_teams', ['slug'])
    op.create_index('idx_college_teams_external_id', 'college_teams', ['external_id'])
    op.create_index('idx_college_teams_rankings', 'college_teams', ['ap_poll_rank', 'coaches_poll_rank'])

    print("✅ Phase 1 college basketball foundation schema has been created!")


def downgrade() -> None:
    """Remove Phase 1 college basketball foundation schema."""

    # Drop tables in reverse order
    op.drop_table('college_teams')
    op.drop_table('colleges')
    op.drop_table('college_conferences')
    op.drop_table('divisions')

    # Drop enum types
    division_level_enum = postgresql.ENUM(name='divisionlevel')
    division_level_enum.drop(op.get_bind())

    conference_type_enum = postgresql.ENUM(name='conferencetype')
    conference_type_enum.drop(op.get_bind())

    college_type_enum = postgresql.ENUM(name='collegetype')
    college_type_enum.drop(op.get_bind())

    region_enum = postgresql.ENUM(name='region')
    region_enum.drop(op.get_bind())

    conference_status_enum = postgresql.ENUM(name='conferencestatus')
    conference_status_enum.drop(op.get_bind())

    print("✅ Phase 1 college basketball foundation schema has been removed!")