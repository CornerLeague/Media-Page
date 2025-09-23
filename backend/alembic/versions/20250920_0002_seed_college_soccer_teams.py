"""Seed college and soccer teams data

Revision ID: 20250920_0002_seed_college_soccer_teams
Revises: 20250920_0001_seed_sports_leagues_teams
Create Date: 2025-09-20 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250920_0002_seed_college_soccer_teams'
down_revision: Union[str, None] = '20250920_0001_seed_sports_leagues_teams'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert seed data for college and soccer teams."""

    # College Football Teams - SEC
    sec_football_teams = [
        {'name': 'Crimson Tide', 'market': 'Alabama', 'abbreviation': 'ALA'},
        {'name': 'Razorbacks', 'market': 'Arkansas', 'abbreviation': 'ARK'},
        {'name': 'Tigers', 'market': 'Auburn', 'abbreviation': 'AUB'},
        {'name': 'Gators', 'market': 'Florida', 'abbreviation': 'FLA'},
        {'name': 'Bulldogs', 'market': 'Georgia', 'abbreviation': 'UGA'},
        {'name': 'Wildcats', 'market': 'Kentucky', 'abbreviation': 'UK'},
        {'name': 'Tigers', 'market': 'LSU', 'abbreviation': 'LSU'},
        {'name': 'Rebels', 'market': 'Ole Miss', 'abbreviation': 'OM'},
        {'name': 'Bulldogs', 'market': 'Mississippi State', 'abbreviation': 'MSST'},
        {'name': 'Tigers', 'market': 'Missouri', 'abbreviation': 'MIZ'},
        {'name': 'Sooners', 'market': 'Oklahoma', 'abbreviation': 'OU'},
        {'name': 'Gamecocks', 'market': 'South Carolina', 'abbreviation': 'SC'},
        {'name': 'Volunteers', 'market': 'Tennessee', 'abbreviation': 'TENN'},
        {'name': 'Longhorns', 'market': 'Texas', 'abbreviation': 'TEX'},
        {'name': 'Aggies', 'market': 'Texas A&M', 'abbreviation': 'A&M'},
        {'name': 'Commodores', 'market': 'Vanderbilt', 'abbreviation': 'VANDY'}
    ]

    for team in sec_football_teams:
        slug = f"{team['market'].lower().replace(' ', '-').replace('&', 'and')}-{team['name'].lower().replace(' ', '-')}"
        market_escaped = team['market'].replace("'", "''")
        name_escaped = team['name'].replace("'", "''")
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{name_escaped}', '{market_escaped}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'college-football' AND l.slug = 'sec'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # College Football Teams - Big Ten
    big_ten_football_teams = [
        {'name': 'Fighting Illini', 'market': 'Illinois', 'abbreviation': 'ILL'},
        {'name': 'Hoosiers', 'market': 'Indiana', 'abbreviation': 'IND'},
        {'name': 'Hawkeyes', 'market': 'Iowa', 'abbreviation': 'IOWA'},
        {'name': 'Terrapins', 'market': 'Maryland', 'abbreviation': 'MD'},
        {'name': 'Wolverines', 'market': 'Michigan', 'abbreviation': 'MICH'},
        {'name': 'Spartans', 'market': 'Michigan State', 'abbreviation': 'MSU'},
        {'name': 'Golden Gophers', 'market': 'Minnesota', 'abbreviation': 'MINN'},
        {'name': 'Cornhuskers', 'market': 'Nebraska', 'abbreviation': 'NEB'},
        {'name': 'Wildcats', 'market': 'Northwestern', 'abbreviation': 'NW'},
        {'name': 'Buckeyes', 'market': 'Ohio State', 'abbreviation': 'OSU'},
        {'name': 'Ducks', 'market': 'Oregon', 'abbreviation': 'ORE'},
        {'name': 'Nittany Lions', 'market': 'Penn State', 'abbreviation': 'PSU'},
        {'name': 'Boilermakers', 'market': 'Purdue', 'abbreviation': 'PUR'},
        {'name': 'Scarlet Knights', 'market': 'Rutgers', 'abbreviation': 'RUT'},
        {'name': 'Bruins', 'market': 'UCLA', 'abbreviation': 'UCLA'},
        {'name': 'Trojans', 'market': 'USC', 'abbreviation': 'USC'},
        {'name': 'Huskies', 'market': 'Washington', 'abbreviation': 'UW'},
        {'name': 'Badgers', 'market': 'Wisconsin', 'abbreviation': 'WIS'}
    ]

    for team in big_ten_football_teams:
        slug = f"{team['market'].lower().replace(' ', '-')}-{team['name'].lower().replace(' ', '-')}"
        market_escaped = team['market'].replace("'", "''")
        name_escaped = team['name'].replace("'", "''")
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{name_escaped}', '{market_escaped}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'college-football' AND l.slug = 'big-ten'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # College Football Teams - Big 12
    big_12_football_teams = [
        {'name': 'Wildcats', 'market': 'Arizona', 'abbreviation': 'ARIZ'},
        {'name': 'Sun Devils', 'market': 'Arizona State', 'abbreviation': 'ASU'},
        {'name': 'Bears', 'market': 'Baylor', 'abbreviation': 'BAY'},
        {'name': 'Cougars', 'market': 'BYU', 'abbreviation': 'BYU'},
        {'name': 'Knights', 'market': 'UCF', 'abbreviation': 'UCF'},
        {'name': 'Bearcats', 'market': 'Cincinnati', 'abbreviation': 'CIN'},
        {'name': 'Buffaloes', 'market': 'Colorado', 'abbreviation': 'COL'},
        {'name': 'Cougars', 'market': 'Houston', 'abbreviation': 'HOU'},
        {'name': 'Cyclones', 'market': 'Iowa State', 'abbreviation': 'ISU'},
        {'name': 'Jayhawks', 'market': 'Kansas', 'abbreviation': 'KU'},
        {'name': 'Wildcats', 'market': 'Kansas State', 'abbreviation': 'KSU'},
        {'name': 'Cowboys', 'market': 'Oklahoma State', 'abbreviation': 'OKST'},
        {'name': 'Horned Frogs', 'market': 'TCU', 'abbreviation': 'TCU'},
        {'name': 'Red Raiders', 'market': 'Texas Tech', 'abbreviation': 'TTU'},
        {'name': 'Utes', 'market': 'Utah', 'abbreviation': 'UTAH'},
        {'name': 'Mountaineers', 'market': 'West Virginia', 'abbreviation': 'WVU'}
    ]

    for team in big_12_football_teams:
        slug = f"{team['market'].lower().replace(' ', '-')}-{team['name'].lower().replace(' ', '-')}"
        market_escaped = team['market'].replace("'", "''")
        name_escaped = team['name'].replace("'", "''")
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{name_escaped}', '{market_escaped}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'college-football' AND l.slug = 'big-12'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # College Football Teams - ACC
    acc_football_teams = [
        {'name': 'Eagles', 'market': 'Boston College', 'abbreviation': 'BC'},
        {'name': 'Golden Bears', 'market': 'California', 'abbreviation': 'CAL'},
        {'name': 'Tigers', 'market': 'Clemson', 'abbreviation': 'CLEM'},
        {'name': 'Blue Devils', 'market': 'Duke', 'abbreviation': 'DUKE'},
        {'name': 'Seminoles', 'market': 'Florida State', 'abbreviation': 'FSU'},
        {'name': 'Yellow Jackets', 'market': 'Georgia Tech', 'abbreviation': 'GT'},
        {'name': 'Cardinals', 'market': 'Louisville', 'abbreviation': 'LOU'},
        {'name': 'Hurricanes', 'market': 'Miami', 'abbreviation': 'MIA'},
        {'name': 'Tar Heels', 'market': 'North Carolina', 'abbreviation': 'UNC'},
        {'name': 'Wolfpack', 'market': 'NC State', 'abbreviation': 'NCST'},
        {'name': 'Fighting Irish', 'market': 'Notre Dame', 'abbreviation': 'ND'},
        {'name': 'Panthers', 'market': 'Pittsburgh', 'abbreviation': 'PITT'},
        {'name': 'Mustangs', 'market': 'SMU', 'abbreviation': 'SMU'},
        {'name': 'Cardinal', 'market': 'Stanford', 'abbreviation': 'STAN'},
        {'name': 'Orange', 'market': 'Syracuse', 'abbreviation': 'SYR'},
        {'name': 'Cavaliers', 'market': 'Virginia', 'abbreviation': 'UVA'},
        {'name': 'Hokies', 'market': 'Virginia Tech', 'abbreviation': 'VT'},
        {'name': 'Demon Deacons', 'market': 'Wake Forest', 'abbreviation': 'WAKE'}
    ]

    for team in acc_football_teams:
        slug = f"{team['market'].lower().replace(' ', '-')}-{team['name'].lower().replace(' ', '-')}"
        market_escaped = team['market'].replace("'", "''")
        name_escaped = team['name'].replace("'", "''")
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{name_escaped}', '{market_escaped}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'college-football' AND l.slug = 'acc'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # Premier League Teams
    premier_league_teams = [
        {'name': 'Arsenal', 'market': 'Arsenal', 'abbreviation': 'ARS'},
        {'name': 'Aston Villa', 'market': 'Aston Villa', 'abbreviation': 'AVL'},
        {'name': 'AFC Bournemouth', 'market': 'Bournemouth', 'abbreviation': 'BOU'},
        {'name': 'Brentford', 'market': 'Brentford', 'abbreviation': 'BRE'},
        {'name': 'Brighton & Hove Albion', 'market': 'Brighton', 'abbreviation': 'BHA'},
        {'name': 'Chelsea', 'market': 'Chelsea', 'abbreviation': 'CHE'},
        {'name': 'Crystal Palace', 'market': 'Crystal Palace', 'abbreviation': 'CRY'},
        {'name': 'Everton', 'market': 'Everton', 'abbreviation': 'EVE'},
        {'name': 'Fulham', 'market': 'Fulham', 'abbreviation': 'FUL'},
        {'name': 'Liverpool', 'market': 'Liverpool', 'abbreviation': 'LIV'},
        {'name': 'Luton Town', 'market': 'Luton Town', 'abbreviation': 'LUT'},
        {'name': 'Manchester City', 'market': 'Manchester City', 'abbreviation': 'MCI'},
        {'name': 'Manchester United', 'market': 'Manchester United', 'abbreviation': 'MUN'},
        {'name': 'Newcastle United', 'market': 'Newcastle United', 'abbreviation': 'NEW'},
        {'name': 'Nottingham Forest', 'market': 'Nottingham Forest', 'abbreviation': 'NFO'},
        {'name': 'Sheffield United', 'market': 'Sheffield United', 'abbreviation': 'SHU'},
        {'name': 'Tottenham Hotspur', 'market': 'Tottenham', 'abbreviation': 'TOT'},
        {'name': 'West Ham United', 'market': 'West Ham', 'abbreviation': 'WHU'},
        {'name': 'Wolverhampton Wanderers', 'market': 'Wolves', 'abbreviation': 'WOL'},
        {'name': 'Leicester City', 'market': 'Leicester City', 'abbreviation': 'LEI'}
    ]

    for team in premier_league_teams:
        slug = f"{team['market'].lower().replace(' ', '-').replace('&', 'and')}-{team['name'].lower().replace(' ', '-').replace('&', 'and')}"
        market_escaped = team['market'].replace("'", "''")
        name_escaped = team['name'].replace("'", "''")
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{name_escaped}', '{market_escaped}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'soccer' AND l.slug = 'premier-league'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # Major League Soccer Teams
    mls_teams = [
        {'name': 'Atlanta United FC', 'market': 'Atlanta', 'abbreviation': 'ATL'},
        {'name': 'Austin FC', 'market': 'Austin', 'abbreviation': 'AUS'},
        {'name': 'Charlotte FC', 'market': 'Charlotte', 'abbreviation': 'CLT'},
        {'name': 'Chicago Fire FC', 'market': 'Chicago', 'abbreviation': 'CHI'},
        {'name': 'FC Cincinnati', 'market': 'Cincinnati', 'abbreviation': 'CIN'},
        {'name': 'Colorado Rapids', 'market': 'Colorado', 'abbreviation': 'COL'},
        {'name': 'Columbus Crew', 'market': 'Columbus', 'abbreviation': 'CLB'},
        {'name': 'FC Dallas', 'market': 'Dallas', 'abbreviation': 'DAL'},
        {'name': 'D.C. United', 'market': 'D.C.', 'abbreviation': 'DC'},
        {'name': 'Houston Dynamo FC', 'market': 'Houston', 'abbreviation': 'HOU'},
        {'name': 'Inter Miami CF', 'market': 'Inter Miami', 'abbreviation': 'MIA'},
        {'name': 'LA Galaxy', 'market': 'LA Galaxy', 'abbreviation': 'LAG'},
        {'name': 'Los Angeles FC', 'market': 'LAFC', 'abbreviation': 'LAFC'},
        {'name': 'Minnesota United FC', 'market': 'Minnesota', 'abbreviation': 'MIN'},
        {'name': 'CF Montréal', 'market': 'Montreal', 'abbreviation': 'MTL'},
        {'name': 'Nashville SC', 'market': 'Nashville', 'abbreviation': 'NSH'},
        {'name': 'New England Revolution', 'market': 'New England', 'abbreviation': 'NE'},
        {'name': 'New York City FC', 'market': 'NYC', 'abbreviation': 'NYC'},
        {'name': 'New York Red Bulls', 'market': 'NY Red Bulls', 'abbreviation': 'NYRB'},
        {'name': 'Orlando City SC', 'market': 'Orlando', 'abbreviation': 'ORL'},
        {'name': 'Philadelphia Union', 'market': 'Philadelphia', 'abbreviation': 'PHI'},
        {'name': 'Portland Timbers', 'market': 'Portland', 'abbreviation': 'POR'},
        {'name': 'Real Salt Lake', 'market': 'Real Salt Lake', 'abbreviation': 'RSL'},
        {'name': 'San Jose Earthquakes', 'market': 'San Jose', 'abbreviation': 'SJ'},
        {'name': 'Seattle Sounders FC', 'market': 'Seattle', 'abbreviation': 'SEA'},
        {'name': 'Sporting Kansas City', 'market': 'Sporting KC', 'abbreviation': 'SKC'},
        {'name': 'Toronto FC', 'market': 'Toronto', 'abbreviation': 'TOR'},
        {'name': 'Vancouver Whitecaps FC', 'market': 'Vancouver', 'abbreviation': 'VAN'}
    ]

    for team in mls_teams:
        slug = f"{team['market'].lower().replace(' ', '-').replace('.', '')}-{team['name'].lower().replace(' ', '-').replace('.', '')}"
        market_escaped = team['market'].replace("'", "''")
        name_escaped = team['name'].replace("'", "''")
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{name_escaped}', '{market_escaped}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'soccer' AND l.slug = 'mls'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # Sample of College Basketball Teams - SEC
    sec_basketball_teams = [
        {'name': 'Crimson Tide', 'market': 'Alabama', 'abbreviation': 'ALA'},
        {'name': 'Razorbacks', 'market': 'Arkansas', 'abbreviation': 'ARK'},
        {'name': 'Tigers', 'market': 'Auburn', 'abbreviation': 'AUB'},
        {'name': 'Gators', 'market': 'Florida', 'abbreviation': 'FLA'},
        {'name': 'Bulldogs', 'market': 'Georgia', 'abbreviation': 'UGA'},
        {'name': 'Wildcats', 'market': 'Kentucky', 'abbreviation': 'UK'},
        {'name': 'Tigers', 'market': 'LSU', 'abbreviation': 'LSU'},
        {'name': 'Bulldogs', 'market': 'Mississippi State', 'abbreviation': 'MSST'},
        {'name': 'Tigers', 'market': 'Missouri', 'abbreviation': 'MIZ'},
        {'name': 'Rebels', 'market': 'Ole Miss', 'abbreviation': 'OM'},
        {'name': 'Sooners', 'market': 'Oklahoma', 'abbreviation': 'OU'},
        {'name': 'Gamecocks', 'market': 'South Carolina', 'abbreviation': 'SC'},
        {'name': 'Volunteers', 'market': 'Tennessee', 'abbreviation': 'TENN'},
        {'name': 'Longhorns', 'market': 'Texas', 'abbreviation': 'TEX'},
        {'name': 'Aggies', 'market': 'Texas A&M', 'abbreviation': 'A&M'},
        {'name': 'Commodores', 'market': 'Vanderbilt', 'abbreviation': 'VANDY'}
    ]

    for team in sec_basketball_teams:
        slug = f"{team['market'].lower().replace(' ', '-').replace('&', 'and')}-{team['name'].lower().replace(' ', '-')}-basketball"
        market_escaped = team['market'].replace("'", "''")
        name_escaped = team['name'].replace("'", "''")
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{name_escaped}', '{market_escaped}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'college-basketball' AND l.slug = 'sec-basketball'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    print("✅ College and soccer teams seed data has been successfully inserted!")


def downgrade() -> None:
    """Remove seed data for college and soccer teams."""

    # Delete college and soccer teams
    op.execute("""
        DELETE FROM teams WHERE league_id IN (
            SELECT id FROM leagues WHERE slug IN (
                'sec', 'big-ten', 'big-12', 'acc', 'premier-league', 'mls', 'sec-basketball'
            )
        );
    """)

    print("✅ College and soccer teams seed data has been removed!")