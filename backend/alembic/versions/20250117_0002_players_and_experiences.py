"""Add players, tickets, experiences, and analytics tables

Revision ID: 002_players_and_experiences
Revises: 001_initial_schema
Create Date: 2025-01-17 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_players_and_experiences'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add remaining tables for players, tickets, experiences, and analytics."""

    # Create AI summaries table
    op.create_table('ai_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE')),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE')),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('summary_type', sa.String(50), server_default='daily'),
        sa.Column('source_article_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('confidence_score', sa.Numeric(3, 2)),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create players table
    op.create_table('players',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('jersey_number', sa.Integer()),
        sa.Column('position', sa.String(50)),
        sa.Column('experience_years', sa.Integer()),
        sa.Column('height', sa.String(10)),
        sa.Column('weight', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('external_id', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create depth chart entries table
    op.create_table('depth_chart_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('position', sa.String(50), nullable=False),
        sa.Column('depth_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('week', sa.Integer()),
        sa.Column('season', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('team_id', 'player_id', 'position', 'week', 'season', name='uq_depth_chart_entry'),
        sa.CheckConstraint('depth_order > 0', name='check_valid_depth_order'),
    )

    # Create ticket providers table
    op.create_table('ticket_providers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('website', sa.String(500)),
        sa.Column('api_endpoint', sa.String(500)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create ticket deals table
    op.create_table('ticket_deals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ticket_providers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('games.id', ondelete='CASCADE')),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE')),
        sa.Column('section', sa.String(50), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.Integer()),
        sa.Column('deal_score', sa.Numeric(3, 2), nullable=False, server_default='0.5'),
        sa.Column('external_url', sa.String(1000)),
        sa.Column('external_id', sa.String(255)),
        sa.Column('valid_until', sa.DateTime(timezone=True)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('price >= 0', name='check_valid_price'),
        sa.CheckConstraint('quantity > 0', name='check_valid_quantity'),
        sa.CheckConstraint('deal_score >= 0 AND deal_score <= 1', name='check_valid_deal_score'),
    )

    # Create fan experiences table
    op.create_table('fan_experiences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE')),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('games.id', ondelete='CASCADE')),
        sa.Column('sport_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sports.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('experience_type', postgresql.ENUM(name='experience_type'), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('location', sa.String(500)),
        sa.Column('organizer', sa.String(255)),
        sa.Column('max_attendees', sa.Integer()),
        sa.Column('current_attendees', sa.Integer(), server_default='0'),
        sa.Column('price', sa.Numeric(10, 2)),
        sa.Column('external_url', sa.String(1000)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('current_attendees <= max_attendees', name='check_valid_attendee_count'),
        sa.CheckConstraint('price >= 0', name='check_valid_experience_price'),
    )

    # Create user experience registrations table
    op.create_table('user_experience_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('experience_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fan_experiences.id', ondelete='CASCADE'), nullable=False),
        sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.String(20), server_default='registered'),
        sa.UniqueConstraint('user_id', 'experience_id', name='uq_user_experience'),
    )

    # Create user interactions table
    op.create_table('user_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create content performance table
    op.create_table('content_performance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_value', sa.Numeric(15, 4), nullable=False),
        sa.Column('date_recorded', sa.Date(), server_default=sa.func.current_date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('content_type', 'content_id', 'metric_name', 'date_recorded', name='uq_content_metric_date'),
    )


def downgrade() -> None:
    """Remove players, tickets, experiences, and analytics tables."""

    # Drop tables in reverse order
    op.drop_table('content_performance')
    op.drop_table('user_interactions')
    op.drop_table('user_experience_registrations')
    op.drop_table('fan_experiences')
    op.drop_table('ticket_deals')
    op.drop_table('ticket_providers')
    op.drop_table('depth_chart_entries')
    op.drop_table('players')
    op.drop_table('ai_summaries')