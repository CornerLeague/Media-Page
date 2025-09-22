"""College Football Phase 1: Seed Data

Revision ID: 20250921_2015_college_football_seed_data
Revises: 20250921_2000_college_football_phase1
Create Date: 2025-09-21 20:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '20250921_2015_college_football_seed_data'
down_revision: Union[str, None] = '20250921_2000_college_football_phase1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create football teams for existing college basketball teams and add football-specific data"""

    # First, let's create a "college-football" sport in the sports table if it doesn't exist
    connection = op.get_bind()

    # Check if college-football sport exists, if not create it
    result = connection.execute(text("""
        SELECT id FROM sports WHERE slug = 'college-football'
    """))

    college_football_sport = result.fetchone()

    if not college_football_sport:
        # Create college-football sport
        connection.execute(text("""
            INSERT INTO sports (id, name, slug, description, is_active, display_order)
            VALUES (
                gen_random_uuid(),
                'College Football',
                'college-football',
                'NCAA College Football',
                true,
                2
            )
        """))

        # Get the newly created sport ID
        result = connection.execute(text("""
            SELECT id FROM sports WHERE slug = 'college-football'
        """))
        college_football_sport = result.fetchone()

    college_football_sport_id = college_football_sport[0]

    # Create college teams for football using existing colleges that have basketball teams
    # This will create the bridge between colleges and the football sport
    connection.execute(text(f"""
        INSERT INTO college_teams (
            id, college_id, sport_id, name, slug, abbreviation,
            is_active, created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            ct.college_id,
            '{college_football_sport_id}',
            ct.name,
            ct.slug || '-football',
            ct.abbreviation,
            true,
            now(),
            now()
        FROM college_teams ct
        WHERE ct.sport_id = (SELECT id FROM sports WHERE slug = 'college-basketball')
        AND NOT EXISTS (
            SELECT 1 FROM college_teams ct2
            WHERE ct2.college_id = ct.college_id
            AND ct2.sport_id = '{college_football_sport_id}'
        )
    """))

    # Now create football_teams for each college_team that represents football
    connection.execute(text(f"""
        INSERT INTO football_teams (
            id, college_team_id, is_active, created_at, updated_at,
            scholarship_count, roster_size
        )
        SELECT
            gen_random_uuid(),
            ct.id,
            true,
            now(),
            now(),
            85,
            105
        FROM college_teams ct
        WHERE ct.sport_id = '{college_football_sport_id}'
        AND NOT EXISTS (
            SELECT 1 FROM football_teams ft
            WHERE ft.college_team_id = ct.id
        )
    """))

    # Add football-specific data for major programs
    # Let's start with some notable football programs and their stadium information

    # SEC Teams
    football_team_data = [
        # SEC
        ('Alabama', 'Bryant-Denny Stadium', 101821, 'natural_grass', 'Kalen DeBoer', 2024, 18, 45, 32, 8),
        ('Georgia', 'Sanford Stadium', 92746, 'natural_grass', 'Kirby Smart', 2016, 4, 45, 32, 6),
        ('LSU', 'Tiger Stadium', 102321, 'natural_grass', 'Brian Kelly', 2022, 4, 35, 25, 4),
        ('Florida', 'Ben Hill Griffin Stadium', 88548, 'natural_grass', 'Billy Napier', 2022, 3, 40, 30, 2),
        ('Tennessee', 'Neyland Stadium', 102455, 'natural_grass', 'Josh Heupel', 2021, 6, 35, 25, 4),
        ('Auburn', 'Jordan-Hare Stadium', 87451, 'natural_grass', 'Hugh Freeze', 2023, 3, 30, 22, 2),
        ('Texas A&M', 'Kyle Field', 102733, 'natural_grass', 'Jimbo Fisher', 2018, 3, 25, 18, 1),
        ('Kentucky', 'Kroger Field', 61000, 'artificial_turf', 'Mark Stoops', 2013, 2, 20, 15, 1),
        ('South Carolina', 'Williams-Brice Stadium', 77559, 'natural_grass', 'Shane Beamer', 2021, 0, 15, 12, 0),
        ('Missouri', 'Faurot Field', 62621, 'artificial_turf', 'Eli Drinkwitz', 2020, 2, 20, 15, 2),
        ('Arkansas', 'Donald W. Reynolds Razorback Stadium', 76212, 'natural_grass', 'Sam Pittman', 2020, 1, 25, 18, 3),
        ('Mississippi State', 'Davis Wade Stadium', 60311, 'natural_grass', 'Jeff Lebby', 2024, 1, 20, 15, 2),
        ('Ole Miss', 'Vaught-Hemingway Stadium', 64038, 'artificial_turf', 'Lane Kiffin', 2020, 1, 20, 15, 2),
        ('Vanderbilt', 'FirstBank Stadium', 40350, 'artificial_turf', 'Clark Lea', 2021, 0, 5, 3, 0),
        ('Oklahoma', 'Gaylord Family Oklahoma Memorial Stadium', 86112, 'artificial_turf', 'Brent Venables', 2022, 7, 50, 37, 4),
        ('Texas', 'Darrell K Royal Stadium', 100119, 'artificial_turf', 'Steve Sarkisian', 2021, 4, 35, 25, 2),

        # Big Ten
        ('Ohio State', 'Ohio Stadium', 104944, 'natural_grass', 'Ryan Day', 2019, 8, 55, 42, 8),
        ('Michigan', 'Michigan Stadium', 107601, 'natural_grass', 'Jim Harbaugh', 2015, 11, 50, 38, 3),
        ('Penn State', 'Beaver Stadium', 106572, 'natural_grass', 'James Franklin', 2014, 2, 40, 30, 4),
        ('Wisconsin', 'Camp Randall Stadium', 80321, 'artificial_turf', 'Luke Fickell', 2023, 0, 35, 25, 3),
        ('Iowa', 'Kinnick Stadium', 69250, 'natural_grass', 'Kirk Ferentz', 1999, 1, 25, 18, 3),
        ('Nebraska', 'Memorial Stadium', 85458, 'artificial_turf', 'Matt Rhule', 2023, 5, 45, 35, 3),
        ('Michigan State', 'Spartan Stadium', 75005, 'natural_grass', 'Jonathan Smith', 2024, 6, 30, 22, 2),
        ('Minnesota', 'TCF Bank Stadium', 50805, 'artificial_turf', 'P.J. Fleck', 2017, 7, 20, 15, 1),
        ('Illinois', 'Memorial Stadium', 60670, 'artificial_turf', 'Bret Bielema', 2021, 5, 15, 12, 1),
        ('Indiana', 'Memorial Stadium', 52929, 'artificial_turf', 'Curt Cignetti', 2024, 0, 10, 8, 0),
        ('Purdue', 'Ross-Ade Stadium', 57236, 'natural_grass', 'Ryan Walters', 2023, 0, 10, 8, 0),
        ('Northwestern', 'Ryan Field', 47130, 'artificial_turf', 'David Braun', 2023, 0, 10, 8, 1),
        ('Maryland', 'SECU Stadium', 51802, 'natural_grass', 'Mike Locksley', 2019, 1, 10, 8, 1),
        ('Rutgers', 'SHI Stadium', 52454, 'artificial_turf', 'Greg Schiano', 2020, 1, 15, 12, 0),
        ('Oregon', 'Autzen Stadium', 54000, 'artificial_turf', 'Dan Lanning', 2022, 12, 35, 25, 2),
        ('Washington', 'Husky Stadium', 70138, 'artificial_turf', 'Jedd Fisch', 2024, 2, 25, 18, 1),
        ('USC', 'United Airlines Field at the Los Angeles Memorial Coliseum', 77500, 'natural_grass', 'Lincoln Riley', 2022, 11, 40, 30, 6),
        ('UCLA', 'Rose Bowl', 88565, 'natural_grass', 'DeShaun Foster', 2024, 1, 20, 15, 1),

        # ACC
        ('Clemson', 'Memorial Stadium', 81500, 'natural_grass', 'Dabo Swinney', 2008, 3, 35, 28, 6),
        ('Florida State', 'Doak Campbell Stadium', 79560, 'natural_grass', 'Mike Norvell', 2020, 3, 40, 30, 14),
        ('Miami', 'Hard Rock Stadium', 65326, 'natural_grass', 'Mario Cristobal', 2022, 5, 30, 22, 9),
        ('North Carolina', 'Kenan Stadium', 50500, 'natural_grass', 'Mack Brown', 2019, 2, 25, 18, 1),
        ('NC State', 'Carter-Finley Stadium', 57583, 'natural_grass', 'Dave Doeren', 2013, 2, 20, 15, 2),
        ('Duke', 'Wallace Wade Stadium', 40004, 'artificial_turf', 'Manny Diaz', 2024, 1, 15, 12, 1),
        ('Wake Forest', 'Truist Field', 31500, 'natural_grass', 'Dave Clawson', 2014, 0, 15, 12, 1),
        ('Virginia', 'Scott Stadium', 61500, 'artificial_turf', 'Tony Elliott', 2022, 1, 20, 15, 1),
        ('Virginia Tech', 'Lane Stadium', 65632, 'natural_grass', 'Brent Pry', 2022, 1, 25, 18, 3),
        ('Georgia Tech', 'Bobby Dodd Stadium', 55000, 'artificial_turf', 'Brent Key', 2022, 4, 20, 15, 1),
        ('Pittsburgh', 'Heinz Field', 68400, 'natural_grass', 'Pat Narduzzi', 2015, 1, 20, 15, 2),
        ('Louisville', 'Cardinal Stadium', 65000, 'artificial_turf', 'Jeff Brohm', 2023, 0, 15, 12, 1),
        ('Syracuse', 'JMA Wireless Dome', 49262, 'artificial_turf', 'Fran Brown', 2024, 1, 15, 12, 1),
        ('Boston College', 'Alumni Stadium', 44500, 'artificial_turf', 'Bill OBrien', 2024, 0, 10, 8, 0),
        ('California', 'California Memorial Stadium', 63000, 'artificial_turf', 'Justin Wilcox', 2017, 0, 15, 12, 1),
        ('Stanford', 'Stanford Stadium', 50424, 'natural_grass', 'Troy Taylor', 2023, 0, 20, 15, 2),
        ('SMU', 'Gerald J. Ford Stadium', 32000, 'artificial_turf', 'Rhett Lashlee', 2022, 0, 15, 12, 1),

        # Big 12
        ('Oklahoma State', 'Boone Pickens Stadium', 60218, 'artificial_turf', 'Mike Gundy', 2005, 1, 30, 22, 1),
        ('Kansas State', 'Bill Snyder Family Stadium', 50000, 'artificial_turf', 'Chris Klieman', 2019, 1, 25, 18, 2),
        ('Iowa State', 'Jack Trice Stadium', 61500, 'natural_grass', 'Matt Campbell', 2016, 0, 20, 15, 2),
        ('Kansas', 'David Booth Kansas Memorial Stadium', 47233, 'artificial_turf', 'Lance Leipold', 2021, 0, 10, 8, 0),
        ('Texas Tech', 'Jones AT&T Stadium', 60454, 'artificial_turf', 'Joey McGuire', 2022, 1, 20, 15, 1),
        ('TCU', 'Amon G. Carter Stadium', 50307, 'natural_grass', 'Sonny Dykes', 2022, 2, 25, 18, 1),
        ('Baylor', 'McLane Stadium', 45140, 'artificial_turf', 'Dave Aranda', 2020, 3, 20, 15, 2),
        ('West Virginia', 'Mountaineer Field', 60000, 'artificial_turf', 'Neal Brown', 2019, 0, 15, 12, 1),
        ('Cincinnati', 'Nippert Stadium', 40000, 'artificial_turf', 'Scott Satterfield', 2023, 0, 15, 12, 2),
        ('Houston', 'TDECU Stadium', 40000, 'artificial_turf', 'Willie Fritz', 2024, 1, 15, 12, 1),
        ('UCF', 'FBC Mortgage Stadium', 44206, 'artificial_turf', 'Gus Malzahn', 2021, 0, 15, 12, 1),
        ('Arizona', 'Arizona Stadium', 50782, 'natural_grass', 'Brent Brennan', 2024, 1, 20, 15, 1),
        ('Arizona State', 'Mountain America Stadium', 53599, 'natural_grass', 'Kenny Dillingham', 2023, 1, 20, 15, 2),
        ('Colorado', 'Folsom Field', 50183, 'natural_grass', 'Deion Sanders', 2023, 1, 25, 18, 1),
        ('Utah', 'Rice-Eccles Stadium', 51444, 'natural_grass', 'Kyle Whittingham', 2005, 2, 30, 22, 2),
        ('BYU', 'LaVell Edwards Stadium', 63470, 'natural_grass', 'Kalani Sitake', 2016, 1, 25, 18, 1),

        # Pac-12 Remaining and Others
        ('Washington State', 'Gesa Field', 32952, 'artificial_turf', 'Jake Dickert', 2021, 1, 15, 12, 1),
        ('Oregon State', 'Reser Stadium', 45674, 'artificial_turf', 'Jonathan Smith', 2018, 0, 15, 12, 1),

        # Group of 5 Notable Programs
        ('Boise State', 'Albertsons Stadium', 36387, 'artificial_turf', 'Spencer Danielson', 2024, 0, 20, 15, 4),
        ('Memphis', 'Simmons Bank Liberty Stadium', 58325, 'artificial_turf', 'Ryan Silverfield', 2020, 0, 15, 12, 1),
        ('Tulane', 'Yulman Stadium', 30000, 'artificial_turf', 'Jon Sumrall', 2024, 0, 15, 12, 2),
        ('Navy', 'Navy-Marine Corps Memorial Stadium', 34000, 'artificial_turf', 'Brian Newberry', 2024, 1, 20, 15, 2),
        ('Air Force', 'Falcon Stadium', 46692, 'artificial_turf', 'Troy Calhoun', 2007, 0, 15, 12, 1),
        ('Army', 'Michie Stadium', 38000, 'artificial_turf', 'Jeff Monken', 2014, 0, 10, 8, 3),
    ]

    # Update football teams with specific stadium and historical data
    for team_data in football_team_data:
        (college_name, stadium_name, capacity, field_type, coach, coach_year,
         championships, bowl_apps, bowl_wins, playoff_apps) = team_data

        # Update the football team with this data
        connection.execute(text(f"""
            UPDATE football_teams
            SET
                stadium_name = '{stadium_name}',
                stadium_capacity = {capacity},
                field_type = '{field_type}',
                head_coach = '{coach}',
                coach_since_year = {coach_year},
                national_championships = {championships},
                bowl_appearances = {bowl_apps},
                bowl_wins = {bowl_wins},
                playoff_appearances = {playoff_apps},
                updated_at = now()
            WHERE college_team_id IN (
                SELECT ct.id FROM college_teams ct
                JOIN colleges c ON ct.college_id = c.id
                WHERE c.name LIKE '%{college_name}%'
                AND ct.sport_id = '{college_football_sport_id}'
            )
        """))

    # Create a current academic year and football season if they don't exist
    current_year = 2024
    academic_year_name = f"{current_year}-{str(current_year + 1)[-2:]}"

    # Check if current academic year exists
    result = connection.execute(text(f"""
        SELECT id FROM academic_years WHERE name = '{academic_year_name}'
    """))

    academic_year = result.fetchone()

    if not academic_year:
        # Create current academic year
        connection.execute(text(f"""
            INSERT INTO academic_years (
                id, name, slug, start_year, end_year, start_date, end_date,
                status, is_active, created_at, updated_at
            )
            VALUES (
                gen_random_uuid(),
                '{academic_year_name}',
                '{academic_year_name.lower()}',
                {current_year},
                {current_year + 1},
                '{current_year}-08-15',
                '{current_year + 1}-05-15',
                'current',
                true,
                now(),
                now()
            )
        """))

        result = connection.execute(text(f"""
            SELECT id FROM academic_years WHERE name = '{academic_year_name}'
        """))
        academic_year = result.fetchone()

    academic_year_id = academic_year[0]

    # Create football season for the current academic year
    result = connection.execute(text(f"""
        SELECT s.id FROM seasons s
        WHERE s.academic_year_id = '{academic_year_id}'
        AND s.season_type = 'regular_season'
    """))

    season = result.fetchone()

    if not season:
        # Create regular season
        connection.execute(text(f"""
            INSERT INTO seasons (
                id, academic_year_id, name, slug, season_type,
                start_date, end_date, is_active, is_current,
                created_at, updated_at
            )
            VALUES (
                gen_random_uuid(),
                '{academic_year_id}',
                'Regular Season {academic_year_name}',
                'regular-season-{academic_year_name.lower()}',
                'regular_season',
                '{current_year}-08-24',
                '{current_year}-12-07',
                true,
                true,
                now(),
                now()
            )
        """))

        result = connection.execute(text(f"""
            SELECT s.id FROM seasons s
            WHERE s.academic_year_id = '{academic_year_id}'
            AND s.season_type = 'regular_season'
        """))
        season = result.fetchone()

    season_id = season[0]

    # Create football season configuration
    connection.execute(text(f"""
        INSERT INTO football_seasons (
            id, season_id, regular_season_weeks, conference_championship_week,
            bowl_selection_date, playoff_selection_date, national_championship_date,
            transfer_portal_open_date, transfer_portal_close_date,
            early_signing_period_start, early_signing_period_end,
            regular_signing_period_start, spring_practice_start,
            fall_practice_start, scholarship_limit, roster_limit,
            total_bowl_games, bowl_eligibility_requirement,
            playoff_teams, playoff_format, is_current,
            created_at, updated_at
        )
        VALUES (
            gen_random_uuid(),
            '{season_id}',
            12,
            13,
            '{current_year}-12-08',
            '{current_year}-12-08',
            '{current_year + 1}-01-20',
            '{current_year}-12-09',
            '{current_year}-12-28',
            '{current_year}-12-20',
            '{current_year}-12-22',
            '{current_year + 1}-02-07',
            '{current_year + 1}-03-01',
            '{current_year}-08-01',
            85,
            105,
            43,
            '6 wins',
            12,
            '12-team College Football Playoff with first round on campus',
            true,
            now(),
            now()
        )
        ON CONFLICT DO NOTHING
    """))

    print(f"✅ Football Phase 1 seed data completed!")
    print(f"   - Created football teams for existing colleges")
    print(f"   - Added stadium and historical data for major programs")
    print(f"   - Created {academic_year_name} academic year and football season")
    print(f"   - Ready for football player and game data")


def downgrade() -> None:
    """Remove football seed data"""

    connection = op.get_bind()

    # Remove football seasons
    connection.execute(text("DELETE FROM football_seasons"))

    # Remove football teams
    connection.execute(text("DELETE FROM football_teams"))

    # Remove college teams for football sport
    connection.execute(text("""
        DELETE FROM college_teams
        WHERE sport_id = (SELECT id FROM sports WHERE slug = 'college-football')
    """))

    # Remove college-football sport if it was created by this migration
    connection.execute(text("DELETE FROM sports WHERE slug = 'college-football'"))

    print("✅ Football Phase 1 seed data removed!")