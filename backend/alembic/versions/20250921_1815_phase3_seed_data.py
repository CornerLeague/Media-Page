"""Phase 3: Seed Data - Venues, Tournaments, and Sample Games

Revision ID: 20250921_1815_phase3_seed_data
Revises: 20250921_1800_phase3_competition_structure
Create Date: 2025-09-21 18:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '20250921_1815_phase3_seed_data'
down_revision: Union[str, None] = '20250921_1800_phase3_competition_structure'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert seed data for Phase 3 competition structure."""

    # Insert major college basketball venues
    venues_data = [
        # Duke - Cameron Indoor Stadium
        {
            'name': 'Cameron Indoor Stadium',
            'slug': 'cameron-indoor-stadium',
            'venue_type': 'arena',
            'city': 'Durham',
            'state': 'North Carolina',
            'capacity': 9314,
            'opened_year': 1940,
            'college_name': 'Duke University',
            'is_neutral_site': False,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # UNC - Dean Smith Center
        {
            'name': 'Dean Smith Center',
            'slug': 'dean-smith-center',
            'venue_type': 'arena',
            'city': 'Chapel Hill',
            'state': 'North Carolina',
            'capacity': 21750,
            'opened_year': 1986,
            'college_name': 'University of North Carolina',
            'is_neutral_site': False,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # Kentucky - Rupp Arena
        {
            'name': 'Rupp Arena',
            'slug': 'rupp-arena',
            'venue_type': 'arena',
            'city': 'Lexington',
            'state': 'Kentucky',
            'capacity': 20545,
            'opened_year': 1976,
            'college_name': 'University of Kentucky',
            'is_neutral_site': False,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # Kansas - Allen Fieldhouse
        {
            'name': 'Allen Fieldhouse',
            'slug': 'allen-fieldhouse',
            'venue_type': 'field_house',
            'city': 'Lawrence',
            'state': 'Kansas',
            'capacity': 16300,
            'opened_year': 1955,
            'college_name': 'University of Kansas',
            'is_neutral_site': False,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # Villanova - Finneran Pavilion
        {
            'name': 'Finneran Pavilion',
            'slug': 'finneran-pavilion',
            'venue_type': 'pavilion',
            'city': 'Villanova',
            'state': 'Pennsylvania',
            'capacity': 6500,
            'opened_year': 1986,
            'college_name': 'Villanova University',
            'is_neutral_site': False,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # Gonzaga - McCarthey Athletic Center
        {
            'name': 'McCarthey Athletic Center',
            'slug': 'mccarthey-athletic-center',
            'venue_type': 'center',
            'city': 'Spokane',
            'state': 'Washington',
            'capacity': 6000,
            'opened_year': 2004,
            'college_name': 'Gonzaga University',
            'is_neutral_site': False,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # Neutral sites for tournaments
        # T-Mobile Center (Kansas City)
        {
            'name': 'T-Mobile Center',
            'slug': 't-mobile-center',
            'venue_type': 'arena',
            'city': 'Kansas City',
            'state': 'Missouri',
            'capacity': 19500,
            'opened_year': 2007,
            'college_name': None,
            'is_neutral_site': True,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # State Farm Stadium (Phoenix)
        {
            'name': 'State Farm Stadium',
            'slug': 'state-farm-stadium',
            'venue_type': 'stadium',
            'city': 'Glendale',
            'state': 'Arizona',
            'capacity': 63400,
            'opened_year': 2006,
            'college_name': None,
            'is_neutral_site': True,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # Madison Square Garden
        {
            'name': 'Madison Square Garden',
            'slug': 'madison-square-garden',
            'venue_type': 'arena',
            'city': 'New York',
            'state': 'New York',
            'capacity': 20789,
            'opened_year': 1968,
            'college_name': None,
            'is_neutral_site': True,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        },
        # Alamodome (San Antonio)
        {
            'name': 'Alamodome',
            'slug': 'alamodome',
            'venue_type': 'dome',
            'city': 'San Antonio',
            'state': 'Texas',
            'capacity': 65000,
            'opened_year': 1993,
            'college_name': None,
            'is_neutral_site': True,
            'court_dimensions': '94x50 feet',
            'surface_type': 'hardwood'
        }
    ]

    # Insert venues
    for venue in venues_data:
        college_id_query = ""
        if venue['college_name']:
            college_id_query = f"""
                (SELECT id FROM colleges WHERE name = '{venue['college_name']}' LIMIT 1)
            """
        else:
            college_id_query = "NULL"

        op.execute(text(f"""
            INSERT INTO venues (
                name, slug, venue_type, city, state, capacity, opened_year,
                college_id, is_neutral_site, court_dimensions, surface_type,
                created_at, updated_at
            ) VALUES (
                '{venue['name']}',
                '{venue['slug']}',
                '{venue['venue_type']}',
                '{venue['city']}',
                '{venue['state']}',
                {venue['capacity']},
                {venue['opened_year']},
                {college_id_query},
                {venue['is_neutral_site']},
                '{venue['court_dimensions']}',
                '{venue['surface_type']}',
                NOW(),
                NOW()
            ) ON CONFLICT (slug) DO NOTHING;
        """))

    # Get the current academic year for tournament creation
    op.execute(text("""
        INSERT INTO tournaments (
            academic_year_id, name, slug, short_name, tournament_type, format, status,
            total_teams, total_rounds, start_date, end_date, selection_date,
            auto_bid_eligible, has_bracket, description,
            created_at, updated_at
        ) VALUES (
            (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1),
            'NCAA Division I Men''s Basketball Tournament',
            'ncaa-tournament-2025',
            'March Madness',
            'ncaa_tournament',
            'single_elimination',
            'scheduled',
            68,
            6,
            '2025-03-21',
            '2025-04-07',
            '2025-03-16',
            true,
            true,
            'The premier college basketball tournament featuring 68 teams competing for the national championship.',
            NOW(),
            NOW()
        ) ON CONFLICT DO NOTHING;
    """))

    # Insert ACC Tournament
    op.execute(text("""
        INSERT INTO tournaments (
            academic_year_id, conference_id, name, slug, short_name, tournament_type, format, status,
            total_teams, total_rounds, start_date, end_date,
            auto_bid_eligible, has_bracket, description,
            created_at, updated_at
        ) VALUES (
            (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1),
            (SELECT id FROM college_conferences WHERE abbreviation = 'ACC' LIMIT 1),
            'ACC Men''s Basketball Tournament',
            'acc-tournament-2025',
            'ACC Tournament',
            'conference_tournament',
            'single_elimination',
            'scheduled',
            15,
            4,
            '2025-03-11',
            '2025-03-16',
            true,
            true,
            'The Atlantic Coast Conference basketball tournament determining the automatic bid to the NCAA Tournament.',
            NOW(),
            NOW()
        ) ON CONFLICT DO NOTHING;
    """));

    # Insert Big Ten Tournament
    op.execute(text("""
        INSERT INTO tournaments (
            academic_year_id, conference_id, name, slug, short_name, tournament_type, format, status,
            total_teams, total_rounds, start_date, end_date,
            auto_bid_eligible, has_bracket, description,
            created_at, updated_at
        ) VALUES (
            (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1),
            (SELECT id FROM college_conferences WHERE abbreviation = 'B1G' LIMIT 1),
            'Big Ten Men''s Basketball Tournament',
            'big-ten-tournament-2025',
            'Big Ten Tournament',
            'conference_tournament',
            'single_elimination',
            'scheduled',
            14,
            4,
            '2025-03-12',
            '2025-03-17',
            true,
            true,
            'The Big Ten Conference basketball tournament.',
            NOW(),
            NOW()
        ) ON CONFLICT DO NOTHING;
    """));

    # Insert SEC Tournament
    op.execute(text("""
        INSERT INTO tournaments (
            academic_year_id, conference_id, name, slug, short_name, tournament_type, format, status,
            total_teams, total_rounds, start_date, end_date,
            auto_bid_eligible, has_bracket, description,
            created_at, updated_at
        ) VALUES (
            (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1),
            (SELECT id FROM college_conferences WHERE abbreviation = 'SEC' LIMIT 1),
            'SEC Men''s Basketball Tournament',
            'sec-tournament-2025',
            'SEC Tournament',
            'conference_tournament',
            'single_elimination',
            'scheduled',
            14,
            4,
            '2025-03-12',
            '2025-03-16',
            true,
            true,
            'The Southeastern Conference basketball tournament.',
            NOW(),
            NOW()
        ) ON CONFLICT DO NOTHING;
    """));

    # Insert Maui Invitational (Holiday Tournament)
    op.execute(text("""
        INSERT INTO tournaments (
            academic_year_id, name, slug, short_name, tournament_type, format, status,
            total_teams, total_rounds, start_date, end_date,
            auto_bid_eligible, has_bracket, description,
            created_at, updated_at
        ) VALUES (
            (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1),
            'Maui Invitational',
            'maui-invitational-2024',
            'Maui Invitational',
            'holiday_tournament',
            'single_elimination',
            'completed',
            8,
            3,
            '2024-11-25',
            '2024-11-27',
            false,
            true,
            'Premier early-season tournament held in Maui, Hawaii.',
            NOW(),
            NOW()
        ) ON CONFLICT DO NOTHING;
    """));

    # Insert NIT Tournament
    op.execute(text("""
        INSERT INTO tournaments (
            academic_year_id, name, slug, short_name, tournament_type, format, status,
            total_teams, total_rounds, start_date, end_date,
            auto_bid_eligible, has_bracket, description,
            created_at, updated_at
        ) VALUES (
            (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1),
            'National Invitation Tournament',
            'nit-2025',
            'NIT',
            'nit',
            'single_elimination',
            'scheduled',
            32,
            5,
            '2025-03-19',
            '2025-04-03',
            false,
            true,
            'Postseason tournament for teams not selected to the NCAA Tournament.',
            NOW(),
            NOW()
        ) ON CONFLICT DO NOTHING;
    """));

    # Associate venues with tournaments
    # NCAA Tournament venues (multiple venues)
    tournament_venues_data = [
        ('ncaa-tournament-2025', 't-mobile-center', 'First Round, Second Round', False),
        ('ncaa-tournament-2025', 'madison-square-garden', 'Regional Semifinals, Regional Finals', False),
        ('ncaa-tournament-2025', 'state-farm-stadium', 'Final Four, Championship', True),
        ('acc-tournament-2025', 't-mobile-center', 'All Rounds', True),
        ('big-ten-tournament-2025', 'madison-square-garden', 'All Rounds', True),
        ('sec-tournament-2025', 't-mobile-center', 'All Rounds', True),
        ('nit-2025', 'madison-square-garden', 'Semifinals, Championship', True),
    ]

    for tournament_slug, venue_slug, rounds, is_primary in tournament_venues_data:
        op.execute(text(f"""
            INSERT INTO tournament_venues (
                tournament_id, venue_id, rounds_hosted, is_primary_venue, created_at, updated_at
            ) VALUES (
                (SELECT id FROM tournaments WHERE slug = '{tournament_slug}' LIMIT 1),
                (SELECT id FROM venues WHERE slug = '{venue_slug}' LIMIT 1),
                '{rounds}',
                {is_primary},
                NOW(),
                NOW()
            ) ON CONFLICT DO NOTHING;
        """))

    # Insert some sample college games for the current season
    sample_games_data = [
        # Duke vs UNC rivalry game
        {
            'home_team': 'Duke University',
            'away_team': 'University of North Carolina',
            'venue_slug': 'cameron-indoor-stadium',
            'scheduled_at': '2025-02-08 21:00:00',
            'game_type': 'regular_season',
            'is_conference_game': True,
            'importance': 'critical',
            'tv_coverage': 'ESPN'
        },
        # UNC vs Duke return game
        {
            'home_team': 'University of North Carolina',
            'away_team': 'Duke University',
            'venue_slug': 'dean-smith-center',
            'scheduled_at': '2025-03-01 18:00:00',
            'game_type': 'regular_season',
            'is_conference_game': True,
            'importance': 'critical',
            'tv_coverage': 'CBS'
        },
        # Kentucky vs Kansas neutral site game
        {
            'home_team': 'University of Kentucky',
            'away_team': 'University of Kansas',
            'venue_slug': 'madison-square-garden',
            'scheduled_at': '2024-12-21 19:00:00',
            'game_type': 'regular_season',
            'is_conference_game': False,
            'importance': 'high',
            'home_court_advantage': 'neutral',
            'tv_coverage': 'FOX'
        },
        # Villanova vs Gonzaga
        {
            'home_team': 'Villanova University',
            'away_team': 'Gonzaga University',
            'venue_slug': 'finneran-pavilion',
            'scheduled_at': '2024-11-30 15:00:00',
            'game_type': 'regular_season',
            'is_conference_game': False,
            'importance': 'high',
            'tv_coverage': 'CBS Sports Network'
        }
    ]

    for game in sample_games_data:
        home_court_advantage = game.get('home_court_advantage', 'home')
        op.execute(text(f"""
            INSERT INTO college_games (
                academic_year_id, season_id, home_team_id, away_team_id, venue_id,
                scheduled_at, game_type, is_conference_game, importance,
                home_court_advantage, tv_coverage, created_at, updated_at
            ) VALUES (
                (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1),
                (SELECT id FROM seasons WHERE season_type = 'regular_season'
                 AND academic_year_id = (SELECT id FROM academic_years WHERE name = '2024-25' LIMIT 1) LIMIT 1),
                (SELECT ct.id FROM college_teams ct
                 JOIN colleges c ON ct.college_id = c.id
                 WHERE c.name = '{game['home_team']}' LIMIT 1),
                (SELECT ct.id FROM college_teams ct
                 JOIN colleges c ON ct.college_id = c.id
                 WHERE c.name = '{game['away_team']}' LIMIT 1),
                (SELECT id FROM venues WHERE slug = '{game['venue_slug']}' LIMIT 1),
                '{game['scheduled_at']}',
                '{game['game_type']}',
                {game['is_conference_game']},
                '{game['importance']}',
                '{home_court_advantage}',
                '{game['tv_coverage']}',
                NOW(),
                NOW()
            ) ON CONFLICT DO NOTHING;
        """))


def downgrade() -> None:
    """Remove Phase 3 seed data."""

    # Remove sample games
    op.execute(text("DELETE FROM college_games WHERE created_at >= '2025-09-21'"))

    # Remove tournament venues
    op.execute(text("DELETE FROM tournament_venues WHERE created_at >= '2025-09-21'"))

    # Remove tournaments
    op.execute(text("DELETE FROM tournaments WHERE created_at >= '2025-09-21'"))

    # Remove venues
    op.execute(text("DELETE FROM venues WHERE created_at >= '2025-09-21'"))