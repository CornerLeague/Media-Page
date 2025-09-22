"""Seed sports, leagues, and teams data

Revision ID: 20250920_0001_seed_sports_leagues_teams
Revises: 20250919_2100_optimize_user_preferences
Create Date: 2025-09-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250920_0001_seed_sports_leagues_teams'
down_revision: Union[str, None] = '20250919_2100_optimize_user_preferences'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert seed data for sports, leagues, and teams."""

    # Insert Sports
    sports_data = [
        {
            'name': 'Football',
            'slug': 'football',
            'has_teams': True,
            'is_active': True,
            'display_order': 1
        },
        {
            'name': 'Basketball',
            'slug': 'basketball',
            'has_teams': True,
            'is_active': True,
            'display_order': 2
        },
        {
            'name': 'Baseball',
            'slug': 'baseball',
            'has_teams': True,
            'is_active': True,
            'display_order': 3
        },
        {
            'name': 'Hockey',
            'slug': 'hockey',
            'has_teams': True,
            'is_active': True,
            'display_order': 4
        },
        {
            'name': 'Soccer',
            'slug': 'soccer',
            'has_teams': True,
            'is_active': True,
            'display_order': 5
        },
        {
            'name': 'College Football',
            'slug': 'college-football',
            'has_teams': True,
            'is_active': True,
            'display_order': 6
        },
        {
            'name': 'College Basketball',
            'slug': 'college-basketball',
            'has_teams': True,
            'is_active': True,
            'display_order': 7
        }
    ]

    for sport in sports_data:
        op.execute(f"""
            INSERT INTO sports (name, slug, has_teams, is_active, display_order, created_at, updated_at)
            VALUES ('{sport['name']}', '{sport['slug']}', {sport['has_teams']}, {sport['is_active']}, {sport['display_order']}, NOW(), NOW())
            ON CONFLICT (name) DO NOTHING;
        """)

    # Insert Leagues
    leagues_data = [
        # NFL
        {
            'sport_slug': 'football',
            'name': 'National Football League',
            'slug': 'nfl',
            'abbreviation': 'NFL',
            'season_start_month': 9,
            'season_end_month': 2
        },
        # NBA
        {
            'sport_slug': 'basketball',
            'name': 'National Basketball Association',
            'slug': 'nba',
            'abbreviation': 'NBA',
            'season_start_month': 10,
            'season_end_month': 6
        },
        # MLB
        {
            'sport_slug': 'baseball',
            'name': 'Major League Baseball',
            'slug': 'mlb',
            'abbreviation': 'MLB',
            'season_start_month': 3,
            'season_end_month': 10
        },
        # NHL
        {
            'sport_slug': 'hockey',
            'name': 'National Hockey League',
            'slug': 'nhl',
            'abbreviation': 'NHL',
            'season_start_month': 10,
            'season_end_month': 6
        },
        # Premier League
        {
            'sport_slug': 'soccer',
            'name': 'Premier League',
            'slug': 'premier-league',
            'abbreviation': 'EPL',
            'season_start_month': 8,
            'season_end_month': 5
        },
        # UEFA Champions League
        {
            'sport_slug': 'soccer',
            'name': 'UEFA Champions League',
            'slug': 'uefa-champions-league',
            'abbreviation': 'UCL',
            'season_start_month': 9,
            'season_end_month': 6
        },
        # Major League Soccer
        {
            'sport_slug': 'soccer',
            'name': 'Major League Soccer',
            'slug': 'mls',
            'abbreviation': 'MLS',
            'season_start_month': 2,
            'season_end_month': 11
        },
        # La Liga
        {
            'sport_slug': 'soccer',
            'name': 'La Liga',
            'slug': 'la-liga',
            'abbreviation': 'LaLiga',
            'season_start_month': 8,
            'season_end_month': 5
        },
        # Bundesliga
        {
            'sport_slug': 'soccer',
            'name': 'Bundesliga',
            'slug': 'bundesliga',
            'abbreviation': 'BL',
            'season_start_month': 8,
            'season_end_month': 5
        },
        # Serie A
        {
            'sport_slug': 'soccer',
            'name': 'Serie A',
            'slug': 'serie-a',
            'abbreviation': 'SA',
            'season_start_month': 8,
            'season_end_month': 5
        },
        # College Football Conferences
        {
            'sport_slug': 'college-football',
            'name': 'Southeastern Conference',
            'slug': 'sec',
            'abbreviation': 'SEC',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Big Ten Conference',
            'slug': 'big-ten',
            'abbreviation': 'B1G',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Big 12 Conference',
            'slug': 'big-12',
            'abbreviation': 'Big12',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Atlantic Coast Conference',
            'slug': 'acc',
            'abbreviation': 'ACC',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'American Athletic Conference',
            'slug': 'aac',
            'abbreviation': 'AAC',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Conference USA',
            'slug': 'cusa',
            'abbreviation': 'C-USA',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Mid-American Conference',
            'slug': 'mac',
            'abbreviation': 'MAC',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Mountain West Conference',
            'slug': 'mwc',
            'abbreviation': 'MWC',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Sun Belt Conference',
            'slug': 'sun-belt',
            'abbreviation': 'SBC',
            'season_start_month': 8,
            'season_end_month': 1
        },
        {
            'sport_slug': 'college-football',
            'name': 'Ivy League',
            'slug': 'ivy-league',
            'abbreviation': 'Ivy',
            'season_start_month': 9,
            'season_end_month': 11
        },
        {
            'sport_slug': 'college-football',
            'name': 'FBS Independents',
            'slug': 'fbs-independents',
            'abbreviation': 'IND',
            'season_start_month': 8,
            'season_end_month': 1
        },
        # College Basketball Conferences
        {
            'sport_slug': 'college-basketball',
            'name': 'Southeastern Conference',
            'slug': 'sec-basketball',
            'abbreviation': 'SEC',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'Big Ten Conference',
            'slug': 'big-ten-basketball',
            'abbreviation': 'B1G',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'Big 12 Conference',
            'slug': 'big-12-basketball',
            'abbreviation': 'Big12',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'Atlantic Coast Conference',
            'slug': 'acc-basketball',
            'abbreviation': 'ACC',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'Mountain West Conference',
            'slug': 'mwc-basketball',
            'abbreviation': 'MWC',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'West Coast Conference',
            'slug': 'wcc',
            'abbreviation': 'WCC',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'Conference USA',
            'slug': 'cusa-basketball',
            'abbreviation': 'C-USA',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'Mid-American Conference',
            'slug': 'mac-basketball',
            'abbreviation': 'MAC',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'American Athletic Conference',
            'slug': 'aac-basketball',
            'abbreviation': 'AAC',
            'season_start_month': 11,
            'season_end_month': 3
        },
        {
            'sport_slug': 'college-basketball',
            'name': 'Sun Belt Conference',
            'slug': 'sun-belt-basketball',
            'abbreviation': 'SBC',
            'season_start_month': 11,
            'season_end_month': 3
        }
    ]

    for league in leagues_data:
        op.execute(f"""
            INSERT INTO leagues (sport_id, name, slug, abbreviation, season_start_month, season_end_month, is_active, created_at, updated_at)
            SELECT s.id, '{league['name']}', '{league['slug']}', '{league['abbreviation']}', {league['season_start_month']}, {league['season_end_month']}, true, NOW(), NOW()
            FROM sports s
            WHERE s.slug = '{league['sport_slug']}'
            ON CONFLICT (sport_id, slug) DO NOTHING;
        """)

    # Insert NFL Teams
    nfl_teams = [
        # AFC North
        {'name': 'Ravens', 'market': 'Baltimore', 'abbreviation': 'BAL'},
        {'name': 'Bengals', 'market': 'Cincinnati', 'abbreviation': 'CIN'},
        {'name': 'Browns', 'market': 'Cleveland', 'abbreviation': 'CLE'},
        {'name': 'Steelers', 'market': 'Pittsburgh', 'abbreviation': 'PIT'},
        # AFC East
        {'name': 'Bills', 'market': 'Buffalo', 'abbreviation': 'BUF'},
        {'name': 'Dolphins', 'market': 'Miami', 'abbreviation': 'MIA'},
        {'name': 'Patriots', 'market': 'New England', 'abbreviation': 'NE'},
        {'name': 'Jets', 'market': 'New York', 'abbreviation': 'NYJ'},
        # AFC South
        {'name': 'Texans', 'market': 'Houston', 'abbreviation': 'HOU'},
        {'name': 'Colts', 'market': 'Indianapolis', 'abbreviation': 'IND'},
        {'name': 'Jaguars', 'market': 'Jacksonville', 'abbreviation': 'JAX'},
        {'name': 'Titans', 'market': 'Tennessee', 'abbreviation': 'TEN'},
        # AFC West
        {'name': 'Broncos', 'market': 'Denver', 'abbreviation': 'DEN'},
        {'name': 'Chiefs', 'market': 'Kansas City', 'abbreviation': 'KC'},
        {'name': 'Raiders', 'market': 'Las Vegas', 'abbreviation': 'LV'},
        {'name': 'Chargers', 'market': 'Los Angeles', 'abbreviation': 'LAC'},
        # NFC North
        {'name': 'Bears', 'market': 'Chicago', 'abbreviation': 'CHI'},
        {'name': 'Lions', 'market': 'Detroit', 'abbreviation': 'DET'},
        {'name': 'Packers', 'market': 'Green Bay', 'abbreviation': 'GB'},
        {'name': 'Vikings', 'market': 'Minnesota', 'abbreviation': 'MIN'},
        # NFC East
        {'name': 'Cowboys', 'market': 'Dallas', 'abbreviation': 'DAL'},
        {'name': 'Giants', 'market': 'New York', 'abbreviation': 'NYG'},
        {'name': 'Eagles', 'market': 'Philadelphia', 'abbreviation': 'PHI'},
        {'name': 'Commanders', 'market': 'Washington', 'abbreviation': 'WAS'},
        # NFC South
        {'name': 'Falcons', 'market': 'Atlanta', 'abbreviation': 'ATL'},
        {'name': 'Panthers', 'market': 'Carolina', 'abbreviation': 'CAR'},
        {'name': 'Saints', 'market': 'New Orleans', 'abbreviation': 'NO'},
        {'name': 'Buccaneers', 'market': 'Tampa Bay', 'abbreviation': 'TB'},
        # NFC West
        {'name': 'Cardinals', 'market': 'Arizona', 'abbreviation': 'ARI'},
        {'name': 'Rams', 'market': 'Los Angeles', 'abbreviation': 'LAR'},
        {'name': '49ers', 'market': 'San Francisco', 'abbreviation': 'SF'},
        {'name': 'Seahawks', 'market': 'Seattle', 'abbreviation': 'SEA'}
    ]

    for team in nfl_teams:
        slug = f"{team['market'].lower().replace(' ', '-')}-{team['name'].lower().replace(' ', '-')}"
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{team['name']}', '{team['market']}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'football' AND l.slug = 'nfl'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # Insert NBA Teams
    nba_teams = [
        # Eastern Conference Atlantic
        {'name': 'Celtics', 'market': 'Boston', 'abbreviation': 'BOS'},
        {'name': 'Nets', 'market': 'Brooklyn', 'abbreviation': 'BKN'},
        {'name': 'Knicks', 'market': 'New York', 'abbreviation': 'NYK'},
        {'name': '76ers', 'market': 'Philadelphia', 'abbreviation': 'PHI'},
        {'name': 'Raptors', 'market': 'Toronto', 'abbreviation': 'TOR'},
        # Eastern Conference Central
        {'name': 'Bulls', 'market': 'Chicago', 'abbreviation': 'CHI'},
        {'name': 'Cavaliers', 'market': 'Cleveland', 'abbreviation': 'CLE'},
        {'name': 'Pistons', 'market': 'Detroit', 'abbreviation': 'DET'},
        {'name': 'Pacers', 'market': 'Indiana', 'abbreviation': 'IND'},
        {'name': 'Bucks', 'market': 'Milwaukee', 'abbreviation': 'MIL'},
        # Eastern Conference Southeast
        {'name': 'Hawks', 'market': 'Atlanta', 'abbreviation': 'ATL'},
        {'name': 'Hornets', 'market': 'Charlotte', 'abbreviation': 'CHA'},
        {'name': 'Heat', 'market': 'Miami', 'abbreviation': 'MIA'},
        {'name': 'Magic', 'market': 'Orlando', 'abbreviation': 'ORL'},
        {'name': 'Wizards', 'market': 'Washington', 'abbreviation': 'WAS'},
        # Western Conference Southwest
        {'name': 'Mavericks', 'market': 'Dallas', 'abbreviation': 'DAL'},
        {'name': 'Rockets', 'market': 'Houston', 'abbreviation': 'HOU'},
        {'name': 'Grizzlies', 'market': 'Memphis', 'abbreviation': 'MEM'},
        {'name': 'Pelicans', 'market': 'New Orleans', 'abbreviation': 'NOP'},
        {'name': 'Spurs', 'market': 'San Antonio', 'abbreviation': 'SA'},
        # Western Conference Northwest
        {'name': 'Nuggets', 'market': 'Denver', 'abbreviation': 'DEN'},
        {'name': 'Timberwolves', 'market': 'Minnesota', 'abbreviation': 'MIN'},
        {'name': 'Thunder', 'market': 'Oklahoma City', 'abbreviation': 'OKC'},
        {'name': 'Trail Blazers', 'market': 'Portland', 'abbreviation': 'POR'},
        {'name': 'Jazz', 'market': 'Utah', 'abbreviation': 'UTA'},
        # Western Conference Pacific
        {'name': 'Warriors', 'market': 'Golden State', 'abbreviation': 'GSW'},
        {'name': 'Clippers', 'market': 'Los Angeles', 'abbreviation': 'LAC'},
        {'name': 'Lakers', 'market': 'Los Angeles', 'abbreviation': 'LAL'},
        {'name': 'Suns', 'market': 'Phoenix', 'abbreviation': 'PHX'},
        {'name': 'Kings', 'market': 'Sacramento', 'abbreviation': 'SAC'}
    ]

    for team in nba_teams:
        slug = f"{team['market'].lower().replace(' ', '-')}-{team['name'].lower().replace(' ', '-')}"
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{team['name']}', '{team['market']}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'basketball' AND l.slug = 'nba'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # Insert MLB Teams
    mlb_teams = [
        # American League East
        {'name': 'Orioles', 'market': 'Baltimore', 'abbreviation': 'BAL'},
        {'name': 'Red Sox', 'market': 'Boston', 'abbreviation': 'BOS'},
        {'name': 'Yankees', 'market': 'New York', 'abbreviation': 'NYY'},
        {'name': 'Rays', 'market': 'Tampa Bay', 'abbreviation': 'TB'},
        {'name': 'Blue Jays', 'market': 'Toronto', 'abbreviation': 'TOR'},
        # American League Central
        {'name': 'White Sox', 'market': 'Chicago', 'abbreviation': 'CWS'},
        {'name': 'Guardians', 'market': 'Cleveland', 'abbreviation': 'CLE'},
        {'name': 'Tigers', 'market': 'Detroit', 'abbreviation': 'DET'},
        {'name': 'Royals', 'market': 'Kansas City', 'abbreviation': 'KC'},
        {'name': 'Twins', 'market': 'Minnesota', 'abbreviation': 'MIN'},
        # American League West
        {'name': 'Athletics', 'market': 'Oakland', 'abbreviation': 'OAK'},
        {'name': 'Astros', 'market': 'Houston', 'abbreviation': 'HOU'},
        {'name': 'Angels', 'market': 'Los Angeles', 'abbreviation': 'LAA'},
        {'name': 'Mariners', 'market': 'Seattle', 'abbreviation': 'SEA'},
        {'name': 'Rangers', 'market': 'Texas', 'abbreviation': 'TEX'},
        # National League East
        {'name': 'Braves', 'market': 'Atlanta', 'abbreviation': 'ATL'},
        {'name': 'Marlins', 'market': 'Miami', 'abbreviation': 'MIA'},
        {'name': 'Mets', 'market': 'New York', 'abbreviation': 'NYM'},
        {'name': 'Phillies', 'market': 'Philadelphia', 'abbreviation': 'PHI'},
        {'name': 'Nationals', 'market': 'Washington', 'abbreviation': 'WAS'},
        # National League Central
        {'name': 'Cubs', 'market': 'Chicago', 'abbreviation': 'CHC'},
        {'name': 'Reds', 'market': 'Cincinnati', 'abbreviation': 'CIN'},
        {'name': 'Brewers', 'market': 'Milwaukee', 'abbreviation': 'MIL'},
        {'name': 'Pirates', 'market': 'Pittsburgh', 'abbreviation': 'PIT'},
        {'name': 'Cardinals', 'market': 'St. Louis', 'abbreviation': 'STL'},
        # National League West
        {'name': 'Diamondbacks', 'market': 'Arizona', 'abbreviation': 'ARI'},
        {'name': 'Rockies', 'market': 'Colorado', 'abbreviation': 'COL'},
        {'name': 'Dodgers', 'market': 'Los Angeles', 'abbreviation': 'LAD'},
        {'name': 'Padres', 'market': 'San Diego', 'abbreviation': 'SD'},
        {'name': 'Giants', 'market': 'San Francisco', 'abbreviation': 'SF'}
    ]

    for team in mlb_teams:
        slug = f"{team['market'].lower().replace(' ', '-')}-{team['name'].lower().replace(' ', '-')}"
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{team['name']}', '{team['market']}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'baseball' AND l.slug = 'mlb'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    # Insert NHL Teams
    nhl_teams = [
        # Atlantic Division
        {'name': 'Bruins', 'market': 'Boston', 'abbreviation': 'BOS'},
        {'name': 'Sabres', 'market': 'Buffalo', 'abbreviation': 'BUF'},
        {'name': 'Red Wings', 'market': 'Detroit', 'abbreviation': 'DET'},
        {'name': 'Panthers', 'market': 'Florida', 'abbreviation': 'FLA'},
        {'name': 'Canadiens', 'market': 'Montreal', 'abbreviation': 'MTL'},
        {'name': 'Senators', 'market': 'Ottawa', 'abbreviation': 'OTT'},
        {'name': 'Lightning', 'market': 'Tampa Bay', 'abbreviation': 'TB'},
        {'name': 'Maple Leafs', 'market': 'Toronto', 'abbreviation': 'TOR'},
        # Metropolitan Division
        {'name': 'Hurricanes', 'market': 'Carolina', 'abbreviation': 'CAR'},
        {'name': 'Blue Jackets', 'market': 'Columbus', 'abbreviation': 'CBJ'},
        {'name': 'Devils', 'market': 'New Jersey', 'abbreviation': 'NJD'},
        {'name': 'Islanders', 'market': 'New York', 'abbreviation': 'NYI'},
        {'name': 'Rangers', 'market': 'New York', 'abbreviation': 'NYR'},
        {'name': 'Flyers', 'market': 'Philadelphia', 'abbreviation': 'PHI'},
        {'name': 'Penguins', 'market': 'Pittsburgh', 'abbreviation': 'PIT'},
        {'name': 'Capitals', 'market': 'Washington', 'abbreviation': 'WAS'},
        # Central Division
        {'name': 'Blackhawks', 'market': 'Chicago', 'abbreviation': 'CHI'},
        {'name': 'Avalanche', 'market': 'Colorado', 'abbreviation': 'COL'},
        {'name': 'Stars', 'market': 'Dallas', 'abbreviation': 'DAL'},
        {'name': 'Wild', 'market': 'Minnesota', 'abbreviation': 'MIN'},
        {'name': 'Predators', 'market': 'Nashville', 'abbreviation': 'NSH'},
        {'name': 'Blues', 'market': 'St. Louis', 'abbreviation': 'STL'},
        {'name': 'Utah Hockey Club', 'market': 'Utah', 'abbreviation': 'UTA'},
        {'name': 'Jets', 'market': 'Winnipeg', 'abbreviation': 'WPG'},
        # Pacific Division
        {'name': 'Ducks', 'market': 'Anaheim', 'abbreviation': 'ANA'},
        {'name': 'Flames', 'market': 'Calgary', 'abbreviation': 'CGY'},
        {'name': 'Oilers', 'market': 'Edmonton', 'abbreviation': 'EDM'},
        {'name': 'Kings', 'market': 'Los Angeles', 'abbreviation': 'LAK'},
        {'name': 'Sharks', 'market': 'San Jose', 'abbreviation': 'SJS'},
        {'name': 'Kraken', 'market': 'Seattle', 'abbreviation': 'SEA'},
        {'name': 'Canucks', 'market': 'Vancouver', 'abbreviation': 'VAN'},
        {'name': 'Golden Knights', 'market': 'Vegas', 'abbreviation': 'VGK'}
    ]

    for team in nhl_teams:
        slug = f"{team['market'].lower().replace(' ', '-')}-{team['name'].lower().replace(' ', '-')}"
        op.execute(f"""
            INSERT INTO teams (sport_id, league_id, name, market, slug, abbreviation, is_active, created_at, updated_at)
            SELECT s.id, l.id, '{team['name']}', '{team['market']}', '{slug}', '{team['abbreviation']}', true, NOW(), NOW()
            FROM sports s
            JOIN leagues l ON l.sport_id = s.id
            WHERE s.slug = 'hockey' AND l.slug = 'nhl'
            ON CONFLICT (league_id, slug) DO NOTHING;
        """)

    print("✅ Sports, leagues, and teams seed data has been successfully inserted!")


def downgrade() -> None:
    """Remove seed data for sports, leagues, and teams."""

    # Delete teams
    op.execute("DELETE FROM teams WHERE league_id IN (SELECT id FROM leagues WHERE slug IN ('nfl', 'nba', 'mlb', 'nhl', 'premier-league', 'uefa-champions-league', 'mls', 'la-liga', 'bundesliga', 'serie-a', 'sec', 'big-ten', 'big-12', 'acc', 'aac', 'cusa', 'mac', 'mwc', 'sun-belt', 'ivy-league', 'fbs-independents', 'sec-basketball', 'big-ten-basketball', 'big-12-basketball', 'acc-basketball', 'mwc-basketball', 'wcc', 'cusa-basketball', 'mac-basketball', 'aac-basketball', 'sun-belt-basketball'));")

    # Delete leagues
    op.execute("DELETE FROM leagues WHERE slug IN ('nfl', 'nba', 'mlb', 'nhl', 'premier-league', 'uefa-champions-league', 'mls', 'la-liga', 'bundesliga', 'serie-a', 'sec', 'big-ten', 'big-12', 'acc', 'aac', 'cusa', 'mac', 'mwc', 'sun-belt', 'ivy-league', 'fbs-independents', 'sec-basketball', 'big-ten-basketball', 'big-12-basketball', 'acc-basketball', 'mwc-basketball', 'wcc', 'cusa-basketball', 'mac-basketball', 'aac-basketball', 'sun-belt-basketball');")

    # Delete sports
    op.execute("DELETE FROM sports WHERE slug IN ('football', 'basketball', 'baseball', 'hockey', 'soccer', 'college-football', 'college-basketball');")

    print("✅ Sports, leagues, and teams seed data has been removed!")