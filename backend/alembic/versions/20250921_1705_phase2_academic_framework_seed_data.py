"""Phase 2: Academic framework seed data - populate academic years and seasons

Revision ID: 20250921_1705_phase2_academic_framework_seed_data
Revises: 20250921_1700_phase2_academic_framework
Create Date: 2025-09-21 17:05:00.000000

"""
from typing import Sequence, Union
import uuid
from datetime import date

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250921_1705_phase2_academic_framework_seed_data'
down_revision: Union[str, None] = '20250921_1700_phase2_academic_framework'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Populate Phase 2 academic framework with seed data."""

    # Define table references
    academic_years_table = table('academic_years',
        column('id', postgresql.UUID),
        column('name', sa.String),
        column('slug', sa.String),
        column('start_year', sa.Integer),
        column('end_year', sa.Integer),
        column('start_date', sa.Date),
        column('end_date', sa.Date),
        column('status', sa.String),
        column('is_active', sa.Boolean),
        column('description', sa.Text),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )

    seasons_table = table('seasons',
        column('id', postgresql.UUID),
        column('academic_year_id', postgresql.UUID),
        column('name', sa.String),
        column('slug', sa.String),
        column('season_type', sa.String),
        column('start_date', sa.Date),
        column('end_date', sa.Date),
        column('is_active', sa.Boolean),
        column('is_current', sa.Boolean),
        column('description', sa.Text),
        column('max_regular_season_games', sa.Integer),
        column('conference_tournament_start', sa.Date),
        column('selection_sunday', sa.Date),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )

    season_configurations_table = table('season_configurations',
        column('id', postgresql.UUID),
        column('season_id', postgresql.UUID),
        column('conference_id', postgresql.UUID),
        column('setting_key', sa.String),
        column('setting_value', sa.Text),
        column('setting_type', sa.String),
        column('description', sa.Text),
        column('is_active', sa.Boolean),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )

    # Get current timestamp
    now = sa.text('NOW()')

    # Academic Years Data (2022-23 through 2027-28)
    academic_years_data = [
        {
            'id': uuid.uuid4(),
            'name': '2022-23',
            'slug': '2022-23',
            'start_year': 2022,
            'end_year': 2023,
            'start_date': date(2022, 7, 1),
            'end_date': date(2023, 6, 30),
            'status': 'past',
            'is_active': True,
            'description': 'Academic year 2022-2023 - Historical data for reference',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'name': '2023-24',
            'slug': '2023-24',
            'start_year': 2023,
            'end_year': 2024,
            'start_date': date(2023, 7, 1),
            'end_date': date(2024, 6, 30),
            'status': 'past',
            'is_active': True,
            'description': 'Academic year 2023-2024 - Previous season data',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'name': '2024-25',
            'slug': '2024-25',
            'start_year': 2024,
            'end_year': 2025,
            'start_date': date(2024, 7, 1),
            'end_date': date(2025, 6, 30),
            'status': 'current',
            'is_active': True,
            'description': 'Academic year 2024-2025 - Current active season',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'name': '2025-26',
            'slug': '2025-26',
            'start_year': 2025,
            'end_year': 2026,
            'start_date': date(2025, 7, 1),
            'end_date': date(2026, 6, 30),
            'status': 'future',
            'is_active': True,
            'description': 'Academic year 2025-2026 - Future planning',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'name': '2026-27',
            'slug': '2026-27',
            'start_year': 2026,
            'end_year': 2027,
            'start_date': date(2026, 7, 1),
            'end_date': date(2027, 6, 30),
            'status': 'future',
            'is_active': True,
            'description': 'Academic year 2026-2027 - Future planning',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'name': '2027-28',
            'slug': '2027-28',
            'start_year': 2027,
            'end_year': 2028,
            'start_date': date(2027, 7, 1),
            'end_date': date(2028, 6, 30),
            'status': 'future',
            'is_active': True,
            'description': 'Academic year 2027-2028 - Long-term planning',
            'created_at': now,
            'updated_at': now
        }
    ]

    # Insert academic years
    op.bulk_insert(academic_years_table, academic_years_data)

    # Store academic year IDs for seasons
    ay_2022_23_id = academic_years_data[0]['id']
    ay_2023_24_id = academic_years_data[1]['id']
    ay_2024_25_id = academic_years_data[2]['id']
    ay_2025_26_id = academic_years_data[3]['id']
    ay_2026_27_id = academic_years_data[4]['id']
    ay_2027_28_id = academic_years_data[5]['id']

    # Seasons Data for each academic year
    seasons_data = []

    # 2022-23 Seasons (Past)
    seasons_data.extend([
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2022_23_id,
            'name': 'Preseason 2022-23',
            'slug': 'preseason-2022-23',
            'season_type': 'preseason',
            'start_date': date(2022, 10, 1),
            'end_date': date(2022, 11, 6),
            'is_active': True,
            'is_current': False,
            'description': 'Preseason games and exhibitions for 2022-23',
            'max_regular_season_games': None,
            'conference_tournament_start': None,
            'selection_sunday': None,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2022_23_id,
            'name': 'Regular Season 2022-23',
            'slug': 'regular-season-2022-23',
            'season_type': 'regular_season',
            'start_date': date(2022, 11, 7),
            'end_date': date(2023, 3, 5),
            'is_active': True,
            'is_current': False,
            'description': 'Regular season games for 2022-23',
            'max_regular_season_games': 31,
            'conference_tournament_start': date(2023, 3, 6),
            'selection_sunday': date(2023, 3, 12),
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2022_23_id,
            'name': 'Conference Tournaments 2022-23',
            'slug': 'conference-tournaments-2022-23',
            'season_type': 'conference_tournament',
            'start_date': date(2023, 3, 6),
            'end_date': date(2023, 3, 19),
            'is_active': True,
            'is_current': False,
            'description': 'Conference tournament week for 2022-23',
            'max_regular_season_games': None,
            'conference_tournament_start': date(2023, 3, 6),
            'selection_sunday': date(2023, 3, 12),
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2022_23_id,
            'name': 'NCAA Tournament 2022-23',
            'slug': 'ncaa-tournament-2022-23',
            'season_type': 'ncaa_tournament',
            'start_date': date(2023, 3, 14),
            'end_date': date(2023, 4, 3),
            'is_active': True,
            'is_current': False,
            'description': 'March Madness 2023',
            'max_regular_season_games': None,
            'conference_tournament_start': None,
            'selection_sunday': date(2023, 3, 12),
            'created_at': now,
            'updated_at': now
        }
    ])

    # 2023-24 Seasons (Past)
    seasons_data.extend([
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2023_24_id,
            'name': 'Preseason 2023-24',
            'slug': 'preseason-2023-24',
            'season_type': 'preseason',
            'start_date': date(2023, 10, 1),
            'end_date': date(2023, 11, 5),
            'is_active': True,
            'is_current': False,
            'description': 'Preseason games and exhibitions for 2023-24',
            'max_regular_season_games': None,
            'conference_tournament_start': None,
            'selection_sunday': None,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2023_24_id,
            'name': 'Regular Season 2023-24',
            'slug': 'regular-season-2023-24',
            'season_type': 'regular_season',
            'start_date': date(2023, 11, 6),
            'end_date': date(2024, 3, 3),
            'is_active': True,
            'is_current': False,
            'description': 'Regular season games for 2023-24',
            'max_regular_season_games': 31,
            'conference_tournament_start': date(2024, 3, 4),
            'selection_sunday': date(2024, 3, 17),
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2023_24_id,
            'name': 'Conference Tournaments 2023-24',
            'slug': 'conference-tournaments-2023-24',
            'season_type': 'conference_tournament',
            'start_date': date(2024, 3, 4),
            'end_date': date(2024, 3, 17),
            'is_active': True,
            'is_current': False,
            'description': 'Conference tournament week for 2023-24',
            'max_regular_season_games': None,
            'conference_tournament_start': date(2024, 3, 4),
            'selection_sunday': date(2024, 3, 17),
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2023_24_id,
            'name': 'NCAA Tournament 2023-24',
            'slug': 'ncaa-tournament-2023-24',
            'season_type': 'ncaa_tournament',
            'start_date': date(2024, 3, 19),
            'end_date': date(2024, 4, 8),
            'is_active': True,
            'is_current': False,
            'description': 'March Madness 2024',
            'max_regular_season_games': None,
            'conference_tournament_start': None,
            'selection_sunday': date(2024, 3, 17),
            'created_at': now,
            'updated_at': now
        }
    ])

    # 2024-25 Seasons (Current)
    current_regular_season_id = uuid.uuid4()
    seasons_data.extend([
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2024_25_id,
            'name': 'Preseason 2024-25',
            'slug': 'preseason-2024-25',
            'season_type': 'preseason',
            'start_date': date(2024, 10, 1),
            'end_date': date(2024, 11, 3),
            'is_active': True,
            'is_current': False,
            'description': 'Preseason games and exhibitions for 2024-25',
            'max_regular_season_games': None,
            'conference_tournament_start': None,
            'selection_sunday': None,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': current_regular_season_id,
            'academic_year_id': ay_2024_25_id,
            'name': 'Regular Season 2024-25',
            'slug': 'regular-season-2024-25',
            'season_type': 'regular_season',
            'start_date': date(2024, 11, 4),
            'end_date': date(2025, 3, 9),
            'is_active': True,
            'is_current': True,  # This is the current active season
            'description': 'Regular season games for 2024-25 - Current active season',
            'max_regular_season_games': 31,
            'conference_tournament_start': date(2025, 3, 10),
            'selection_sunday': date(2025, 3, 16),
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2024_25_id,
            'name': 'Conference Tournaments 2024-25',
            'slug': 'conference-tournaments-2024-25',
            'season_type': 'conference_tournament',
            'start_date': date(2025, 3, 10),
            'end_date': date(2025, 3, 16),
            'is_active': True,
            'is_current': False,
            'description': 'Conference tournament week for 2024-25',
            'max_regular_season_games': None,
            'conference_tournament_start': date(2025, 3, 10),
            'selection_sunday': date(2025, 3, 16),
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2024_25_id,
            'name': 'NCAA Tournament 2024-25',
            'slug': 'ncaa-tournament-2024-25',
            'season_type': 'ncaa_tournament',
            'start_date': date(2025, 3, 18),
            'end_date': date(2025, 4, 7),
            'is_active': True,
            'is_current': False,
            'description': 'March Madness 2025',
            'max_regular_season_games': None,
            'conference_tournament_start': None,
            'selection_sunday': date(2025, 3, 16),
            'created_at': now,
            'updated_at': now
        }
    ])

    # 2025-26 Seasons (Future)
    seasons_data.extend([
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2025_26_id,
            'name': 'Regular Season 2025-26',
            'slug': 'regular-season-2025-26',
            'season_type': 'regular_season',
            'start_date': date(2025, 11, 10),
            'end_date': date(2026, 3, 8),
            'is_active': True,
            'is_current': False,
            'description': 'Regular season games for 2025-26',
            'max_regular_season_games': 31,
            'conference_tournament_start': date(2026, 3, 9),
            'selection_sunday': date(2026, 3, 15),
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'academic_year_id': ay_2025_26_id,
            'name': 'NCAA Tournament 2025-26',
            'slug': 'ncaa-tournament-2025-26',
            'season_type': 'ncaa_tournament',
            'start_date': date(2026, 3, 17),
            'end_date': date(2026, 4, 6),
            'is_active': True,
            'is_current': False,
            'description': 'March Madness 2026',
            'max_regular_season_games': None,
            'conference_tournament_start': None,
            'selection_sunday': date(2026, 3, 15),
            'created_at': now,
            'updated_at': now
        }
    ])

    # Insert seasons
    op.bulk_insert(seasons_table, seasons_data)

    # Sample Season Configurations
    season_config_data = [
        {
            'id': uuid.uuid4(),
            'season_id': current_regular_season_id,
            'conference_id': None,  # Global setting
            'setting_key': 'max_overtime_periods',
            'setting_value': '5',
            'setting_type': 'integer',
            'description': 'Maximum number of overtime periods before declaring a tie',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'season_id': current_regular_season_id,
            'conference_id': None,  # Global setting
            'setting_key': 'shot_clock_seconds',
            'setting_value': '30',
            'setting_type': 'integer',
            'description': 'Shot clock duration in seconds',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'season_id': current_regular_season_id,
            'conference_id': None,  # Global setting
            'setting_key': 'transfer_portal_windows',
            'setting_value': '{"spring": {"start": "2025-03-18", "end": "2025-05-11"}, "fall": {"start": "2024-12-09", "end": "2024-12-28"}}',
            'setting_type': 'json',
            'description': 'NCAA Transfer Portal windows for the season',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'season_id': current_regular_season_id,
            'conference_id': None,  # Global setting
            'setting_key': 'tournament_selection_criteria',
            'setting_value': '{"net_ranking_weight": 0.4, "quad_wins_weight": 0.3, "strength_of_schedule_weight": 0.2, "record_weight": 0.1}',
            'setting_type': 'json',
            'description': 'NCAA Tournament selection criteria weights',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
    ]

    # Insert season configurations
    op.bulk_insert(season_configurations_table, season_config_data)

    print("✅ Phase 2 academic framework seed data has been inserted!")
    print(f"   • Created {len(academic_years_data)} academic years (2022-23 through 2027-28)")
    print(f"   • Created {len(seasons_data)} seasons across all academic years")
    print(f"   • Created {len(season_config_data)} season configuration settings")
    print("   • Set 2024-25 Regular Season as the current active season")


def downgrade() -> None:
    """Remove Phase 2 academic framework seed data."""

    # Clear all tables (foreign key constraints will handle proper ordering)
    op.execute("DELETE FROM season_configurations")
    op.execute("DELETE FROM conference_memberships")
    op.execute("DELETE FROM seasons")
    op.execute("DELETE FROM academic_years")

    print("✅ Phase 2 academic framework seed data has been removed!")