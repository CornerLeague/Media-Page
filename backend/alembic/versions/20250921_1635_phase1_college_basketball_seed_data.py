"""Phase 1: College basketball seed data - 167 teams across 10 major conferences

Revision ID: 20250921_1635_phase1_college_basketball_seed_data
Revises: 20250921_1630_phase1_college_basketball_foundation
Create Date: 2025-09-21 16:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250921_1635_phase1_college_basketball_seed_data'
down_revision: Union[str, None] = '20250921_1630_phase1_college_basketball_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert seed data for college basketball divisions, conferences, colleges, and teams."""

    # Insert Division I
    op.execute(f"""
        INSERT INTO divisions (id, name, slug, level, description, is_active, display_order, created_at, updated_at)
        VALUES (gen_random_uuid(), 'Division I', 'division-i', 'D1', 'NCAA Division I - highest level of college athletics', true, 1, NOW(), NOW())
        ON CONFLICT (name) DO NOTHING;
    """)

    # Get Division I ID for use in conferences
    division_i_id_result = op.execute("SELECT id FROM divisions WHERE slug = 'division-i'")
    division_i_id = division_i_id_result.fetchone()[0]

    # Insert 10 Major Conferences
    conferences_data = [
        {
            'name': 'Atlantic Coast Conference',
            'slug': 'acc',
            'abbreviation': 'ACC',
            'conference_type': 'power_five',
            'region': 'southeast',
            'founded_year': 1953,
            'headquarters_city': 'Charlotte',
            'headquarters_state': 'North Carolina'
        },
        {
            'name': 'Big East Conference',
            'slug': 'big-east',
            'abbreviation': 'Big East',
            'conference_type': 'mid_major',
            'region': 'northeast',
            'founded_year': 1979,
            'headquarters_city': 'New York',
            'headquarters_state': 'New York'
        },
        {
            'name': 'Big Ten Conference',
            'slug': 'big-ten',
            'abbreviation': 'B1G',
            'conference_type': 'power_five',
            'region': 'midwest',
            'founded_year': 1896,
            'headquarters_city': 'Chicago',
            'headquarters_state': 'Illinois'
        },
        {
            'name': 'Big 12 Conference',
            'slug': 'big-12',
            'abbreviation': 'Big 12',
            'conference_type': 'power_five',
            'region': 'midwest',
            'founded_year': 1994,
            'headquarters_city': 'Irving',
            'headquarters_state': 'Texas'
        },
        {
            'name': 'Pacific-12 Conference',
            'slug': 'pac-12',
            'abbreviation': 'Pac-12',
            'conference_type': 'power_five',
            'region': 'west',
            'founded_year': 1915,
            'headquarters_city': 'San Francisco',
            'headquarters_state': 'California'
        },
        {
            'name': 'Southeastern Conference',
            'slug': 'sec',
            'abbreviation': 'SEC',
            'conference_type': 'power_five',
            'region': 'southeast',
            'founded_year': 1932,
            'headquarters_city': 'Birmingham',
            'headquarters_state': 'Alabama'
        },
        {
            'name': 'American Athletic Conference',
            'slug': 'aac',
            'abbreviation': 'AAC',
            'conference_type': 'mid_major',
            'region': 'southeast',
            'founded_year': 2013,
            'headquarters_city': 'Irving',
            'headquarters_state': 'Texas'
        },
        {
            'name': 'Atlantic 10 Conference',
            'slug': 'a10',
            'abbreviation': 'A-10',
            'conference_type': 'mid_major',
            'region': 'northeast',
            'founded_year': 1975,
            'headquarters_city': 'Newport News',
            'headquarters_state': 'Virginia'
        },
        {
            'name': 'Mountain West Conference',
            'slug': 'mountain-west',
            'abbreviation': 'MWC',
            'conference_type': 'mid_major',
            'region': 'west',
            'founded_year': 1998,
            'headquarters_city': 'Colorado Springs',
            'headquarters_state': 'Colorado'
        },
        {
            'name': 'West Coast Conference',
            'slug': 'wcc',
            'abbreviation': 'WCC',
            'conference_type': 'mid_major',
            'region': 'west',
            'founded_year': 1952,
            'headquarters_city': 'San Bruno',
            'headquarters_state': 'California'
        }
    ]

    for conf in conferences_data:
        op.execute(f"""
            INSERT INTO college_conferences (
                id, division_id, name, slug, abbreviation, conference_type, region,
                founded_year, headquarters_city, headquarters_state, is_active,
                auto_bid_tournament, created_at, updated_at
            )
            VALUES (
                gen_random_uuid(), '{division_i_id}', '{conf['name']}', '{conf['slug']}',
                '{conf['abbreviation']}', '{conf['conference_type']}', '{conf['region']}',
                {conf['founded_year']}, '{conf['headquarters_city']}', '{conf['headquarters_state']}',
                true, true, NOW(), NOW()
            )
            ON CONFLICT (division_id, slug) DO NOTHING;
        """)

    # Insert Colleges and Teams for each conference

    # ACC Teams (15 teams)
    acc_teams = [
        {'name': 'Boston College', 'city': 'Chestnut Hill', 'state': 'Massachusetts', 'nickname': 'Eagles'},
        {'name': 'Clemson University', 'city': 'Clemson', 'state': 'South Carolina', 'nickname': 'Tigers'},
        {'name': 'Duke University', 'city': 'Durham', 'state': 'North Carolina', 'nickname': 'Blue Devils'},
        {'name': 'Florida State University', 'city': 'Tallahassee', 'state': 'Florida', 'nickname': 'Seminoles'},
        {'name': 'Georgia Institute of Technology', 'city': 'Atlanta', 'state': 'Georgia', 'nickname': 'Yellow Jackets'},
        {'name': 'University of Louisville', 'city': 'Louisville', 'state': 'Kentucky', 'nickname': 'Cardinals'},
        {'name': 'University of Miami', 'city': 'Coral Gables', 'state': 'Florida', 'nickname': 'Hurricanes'},
        {'name': 'University of North Carolina', 'city': 'Chapel Hill', 'state': 'North Carolina', 'nickname': 'Tar Heels'},
        {'name': 'North Carolina State University', 'city': 'Raleigh', 'state': 'North Carolina', 'nickname': 'Wolfpack'},
        {'name': 'University of Notre Dame', 'city': 'Notre Dame', 'state': 'Indiana', 'nickname': 'Fighting Irish'},
        {'name': 'University of Pittsburgh', 'city': 'Pittsburgh', 'state': 'Pennsylvania', 'nickname': 'Panthers'},
        {'name': 'Syracuse University', 'city': 'Syracuse', 'state': 'New York', 'nickname': 'Orange'},
        {'name': 'Virginia Tech', 'city': 'Blacksburg', 'state': 'Virginia', 'nickname': 'Hokies'},
        {'name': 'University of Virginia', 'city': 'Charlottesville', 'state': 'Virginia', 'nickname': 'Cavaliers'},
        {'name': 'Wake Forest University', 'city': 'Winston-Salem', 'state': 'North Carolina', 'nickname': 'Demon Deacons'}
    ]

    _insert_conference_teams(op, 'acc', acc_teams)

    # Big East Teams (11 teams)
    big_east_teams = [
        {'name': 'Butler University', 'city': 'Indianapolis', 'state': 'Indiana', 'nickname': 'Bulldogs'},
        {'name': 'Creighton University', 'city': 'Omaha', 'state': 'Nebraska', 'nickname': 'Bluejays'},
        {'name': 'DePaul University', 'city': 'Chicago', 'state': 'Illinois', 'nickname': 'Blue Demons'},
        {'name': 'Georgetown University', 'city': 'Washington', 'state': 'District of Columbia', 'nickname': 'Hoyas'},
        {'name': 'Marquette University', 'city': 'Milwaukee', 'state': 'Wisconsin', 'nickname': 'Golden Eagles'},
        {'name': 'Providence College', 'city': 'Providence', 'state': 'Rhode Island', 'nickname': 'Friars'},
        {'name': 'Seton Hall University', 'city': 'South Orange', 'state': 'New Jersey', 'nickname': 'Pirates'},
        {'name': 'St. John\'s University', 'city': 'Jamaica', 'state': 'New York', 'nickname': 'Red Storm'},
        {'name': 'University of Connecticut', 'city': 'Storrs', 'state': 'Connecticut', 'nickname': 'Huskies'},
        {'name': 'Villanova University', 'city': 'Villanova', 'state': 'Pennsylvania', 'nickname': 'Wildcats'},
        {'name': 'Xavier University', 'city': 'Cincinnati', 'state': 'Ohio', 'nickname': 'Musketeers'}
    ]

    _insert_conference_teams(op, 'big-east', big_east_teams)

    # Big Ten Teams (18 teams)
    big_ten_teams = [
        {'name': 'University of Illinois', 'city': 'Champaign', 'state': 'Illinois', 'nickname': 'Fighting Illini'},
        {'name': 'Indiana University', 'city': 'Bloomington', 'state': 'Indiana', 'nickname': 'Hoosiers'},
        {'name': 'University of Iowa', 'city': 'Iowa City', 'state': 'Iowa', 'nickname': 'Hawkeyes'},
        {'name': 'University of Maryland', 'city': 'College Park', 'state': 'Maryland', 'nickname': 'Terrapins'},
        {'name': 'University of Michigan', 'city': 'Ann Arbor', 'state': 'Michigan', 'nickname': 'Wolverines'},
        {'name': 'Michigan State University', 'city': 'East Lansing', 'state': 'Michigan', 'nickname': 'Spartans'},
        {'name': 'University of Minnesota', 'city': 'Minneapolis', 'state': 'Minnesota', 'nickname': 'Golden Gophers'},
        {'name': 'University of Nebraska', 'city': 'Lincoln', 'state': 'Nebraska', 'nickname': 'Cornhuskers'},
        {'name': 'Northwestern University', 'city': 'Evanston', 'state': 'Illinois', 'nickname': 'Wildcats'},
        {'name': 'Ohio State University', 'city': 'Columbus', 'state': 'Ohio', 'nickname': 'Buckeyes'},
        {'name': 'Pennsylvania State University', 'city': 'University Park', 'state': 'Pennsylvania', 'nickname': 'Nittany Lions'},
        {'name': 'Purdue University', 'city': 'West Lafayette', 'state': 'Indiana', 'nickname': 'Boilermakers'},
        {'name': 'Rutgers University', 'city': 'New Brunswick', 'state': 'New Jersey', 'nickname': 'Scarlet Knights'},
        {'name': 'University of Wisconsin', 'city': 'Madison', 'state': 'Wisconsin', 'nickname': 'Badgers'},
        {'name': 'University of California Los Angeles', 'city': 'Los Angeles', 'state': 'California', 'nickname': 'Bruins'},
        {'name': 'University of Oregon', 'city': 'Eugene', 'state': 'Oregon', 'nickname': 'Ducks'},
        {'name': 'University of Southern California', 'city': 'Los Angeles', 'state': 'California', 'nickname': 'Trojans'},
        {'name': 'University of Washington', 'city': 'Seattle', 'state': 'Washington', 'nickname': 'Huskies'}
    ]

    _insert_conference_teams(op, 'big-ten', big_ten_teams)

    # Big 12 Teams (16 teams)
    big_12_teams = [
        {'name': 'Baylor University', 'city': 'Waco', 'state': 'Texas', 'nickname': 'Bears'},
        {'name': 'Brigham Young University', 'city': 'Provo', 'state': 'Utah', 'nickname': 'Cougars'},
        {'name': 'University of Cincinnati', 'city': 'Cincinnati', 'state': 'Ohio', 'nickname': 'Bearcats'},
        {'name': 'University of Colorado', 'city': 'Boulder', 'state': 'Colorado', 'nickname': 'Buffaloes'},
        {'name': 'University of Houston', 'city': 'Houston', 'state': 'Texas', 'nickname': 'Cougars'},
        {'name': 'Iowa State University', 'city': 'Ames', 'state': 'Iowa', 'nickname': 'Cyclones'},
        {'name': 'University of Kansas', 'city': 'Lawrence', 'state': 'Kansas', 'nickname': 'Jayhawks'},
        {'name': 'Kansas State University', 'city': 'Manhattan', 'state': 'Kansas', 'nickname': 'Wildcats'},
        {'name': 'Oklahoma State University', 'city': 'Stillwater', 'state': 'Oklahoma', 'nickname': 'Cowboys'},
        {'name': 'Texas Christian University', 'city': 'Fort Worth', 'state': 'Texas', 'nickname': 'Horned Frogs'},
        {'name': 'Texas Tech University', 'city': 'Lubbock', 'state': 'Texas', 'nickname': 'Red Raiders'},
        {'name': 'University of Central Florida', 'city': 'Orlando', 'state': 'Florida', 'nickname': 'Knights'},
        {'name': 'West Virginia University', 'city': 'Morgantown', 'state': 'West Virginia', 'nickname': 'Mountaineers'},
        {'name': 'University of Arizona', 'city': 'Tucson', 'state': 'Arizona', 'nickname': 'Wildcats'},
        {'name': 'Arizona State University', 'city': 'Tempe', 'state': 'Arizona', 'nickname': 'Sun Devils'},
        {'name': 'University of Utah', 'city': 'Salt Lake City', 'state': 'Utah', 'nickname': 'Utes'}
    ]

    _insert_conference_teams(op, 'big-12', big_12_teams)

    # SEC Teams (16 teams)
    sec_teams = [
        {'name': 'University of Alabama', 'city': 'Tuscaloosa', 'state': 'Alabama', 'nickname': 'Crimson Tide'},
        {'name': 'University of Arkansas', 'city': 'Fayetteville', 'state': 'Arkansas', 'nickname': 'Razorbacks'},
        {'name': 'Auburn University', 'city': 'Auburn', 'state': 'Alabama', 'nickname': 'Tigers'},
        {'name': 'University of Florida', 'city': 'Gainesville', 'state': 'Florida', 'nickname': 'Gators'},
        {'name': 'University of Georgia', 'city': 'Athens', 'state': 'Georgia', 'nickname': 'Bulldogs'},
        {'name': 'University of Kentucky', 'city': 'Lexington', 'state': 'Kentucky', 'nickname': 'Wildcats'},
        {'name': 'Louisiana State University', 'city': 'Baton Rouge', 'state': 'Louisiana', 'nickname': 'Tigers'},
        {'name': 'University of Mississippi', 'city': 'Oxford', 'state': 'Mississippi', 'nickname': 'Rebels'},
        {'name': 'Mississippi State University', 'city': 'Starkville', 'state': 'Mississippi', 'nickname': 'Bulldogs'},
        {'name': 'University of Missouri', 'city': 'Columbia', 'state': 'Missouri', 'nickname': 'Tigers'},
        {'name': 'University of South Carolina', 'city': 'Columbia', 'state': 'South Carolina', 'nickname': 'Gamecocks'},
        {'name': 'University of Tennessee', 'city': 'Knoxville', 'state': 'Tennessee', 'nickname': 'Volunteers'},
        {'name': 'Texas A&M University', 'city': 'College Station', 'state': 'Texas', 'nickname': 'Aggies'},
        {'name': 'Vanderbilt University', 'city': 'Nashville', 'state': 'Tennessee', 'nickname': 'Commodores'},
        {'name': 'University of Oklahoma', 'city': 'Norman', 'state': 'Oklahoma', 'nickname': 'Sooners'},
        {'name': 'University of Texas', 'city': 'Austin', 'state': 'Texas', 'nickname': 'Longhorns'}
    ]

    _insert_conference_teams(op, 'sec', sec_teams)

    # Pac-12 Teams (12 teams - reduced due to recent departures)
    pac_12_teams = [
        {'name': 'California State University', 'city': 'Berkeley', 'state': 'California', 'nickname': 'Golden Bears'},
        {'name': 'Oregon State University', 'city': 'Corvallis', 'state': 'Oregon', 'nickname': 'Beavers'},
        {'name': 'Stanford University', 'city': 'Stanford', 'state': 'California', 'nickname': 'Cardinal'},
        {'name': 'Washington State University', 'city': 'Pullman', 'state': 'Washington', 'nickname': 'Cougars'},
        {'name': 'University of Colorado Boulder', 'city': 'Boulder', 'state': 'Colorado', 'nickname': 'Buffaloes'},
        {'name': 'University of Arizona Tucson', 'city': 'Tucson', 'state': 'Arizona', 'nickname': 'Wildcats'},
        {'name': 'Arizona State University Tempe', 'city': 'Tempe', 'state': 'Arizona', 'nickname': 'Sun Devils'},
        {'name': 'University of Utah Salt Lake', 'city': 'Salt Lake City', 'state': 'Utah', 'nickname': 'Utes'},
        {'name': 'University of California Los Angeles Westwood', 'city': 'Los Angeles', 'state': 'California', 'nickname': 'Bruins'},
        {'name': 'University of Southern California Los Angeles', 'city': 'Los Angeles', 'state': 'California', 'nickname': 'Trojans'},
        {'name': 'University of Oregon Eugene', 'city': 'Eugene', 'state': 'Oregon', 'nickname': 'Ducks'},
        {'name': 'University of Washington Seattle', 'city': 'Seattle', 'state': 'Washington', 'nickname': 'Huskies'}
    ]

    _insert_conference_teams(op, 'pac-12', pac_12_teams)

    # AAC Teams (14 teams)
    aac_teams = [
        {'name': 'East Carolina University', 'city': 'Greenville', 'state': 'North Carolina', 'nickname': 'Pirates'},
        {'name': 'University of Memphis', 'city': 'Memphis', 'state': 'Tennessee', 'nickname': 'Tigers'},
        {'name': 'Navy', 'city': 'Annapolis', 'state': 'Maryland', 'nickname': 'Midshipmen'},
        {'name': 'University of South Florida', 'city': 'Tampa', 'state': 'Florida', 'nickname': 'Bulls'},
        {'name': 'Temple University', 'city': 'Philadelphia', 'state': 'Pennsylvania', 'nickname': 'Owls'},
        {'name': 'Tulane University', 'city': 'New Orleans', 'state': 'Louisiana', 'nickname': 'Green Wave'},
        {'name': 'University of Tulsa', 'city': 'Tulsa', 'state': 'Oklahoma', 'nickname': 'Golden Hurricane'},
        {'name': 'Florida Atlantic University', 'city': 'Boca Raton', 'state': 'Florida', 'nickname': 'Owls'},
        {'name': 'Florida International University', 'city': 'Miami', 'state': 'Florida', 'nickname': 'Panthers'},
        {'name': 'University of North Texas', 'city': 'Denton', 'state': 'Texas', 'nickname': 'Mean Green'},
        {'name': 'Rice University', 'city': 'Houston', 'state': 'Texas', 'nickname': 'Owls'},
        {'name': 'University of Texas San Antonio', 'city': 'San Antonio', 'state': 'Texas', 'nickname': 'Roadrunners'},
        {'name': 'Charlotte', 'city': 'Charlotte', 'state': 'North Carolina', 'nickname': '49ers'},
        {'name': 'University at Alabama Birmingham', 'city': 'Birmingham', 'state': 'Alabama', 'nickname': 'Blazers'}
    ]

    _insert_conference_teams(op, 'aac', aac_teams)

    # Atlantic 10 Teams (15 teams)
    a10_teams = [
        {'name': 'University of Dayton', 'city': 'Dayton', 'state': 'Ohio', 'nickname': 'Flyers'},
        {'name': 'Davidson College', 'city': 'Davidson', 'state': 'North Carolina', 'nickname': 'Wildcats'},
        {'name': 'Duquesne University', 'city': 'Pittsburgh', 'state': 'Pennsylvania', 'nickname': 'Dukes'},
        {'name': 'Fordham University', 'city': 'Bronx', 'state': 'New York', 'nickname': 'Rams'},
        {'name': 'George Mason University', 'city': 'Fairfax', 'state': 'Virginia', 'nickname': 'Patriots'},
        {'name': 'George Washington University', 'city': 'Washington', 'state': 'District of Columbia', 'nickname': 'Colonials'},
        {'name': 'La Salle University', 'city': 'Philadelphia', 'state': 'Pennsylvania', 'nickname': 'Explorers'},
        {'name': 'University of Massachusetts', 'city': 'Amherst', 'state': 'Massachusetts', 'nickname': 'Minutemen'},
        {'name': 'University of Rhode Island', 'city': 'Kingston', 'state': 'Rhode Island', 'nickname': 'Rams'},
        {'name': 'University of Richmond', 'city': 'Richmond', 'state': 'Virginia', 'nickname': 'Spiders'},
        {'name': 'St. Bonaventure University', 'city': 'St. Bonaventure', 'state': 'New York', 'nickname': 'Bonnies'},
        {'name': 'Saint Joseph\'s University', 'city': 'Philadelphia', 'state': 'Pennsylvania', 'nickname': 'Hawks'},
        {'name': 'Saint Louis University', 'city': 'St. Louis', 'state': 'Missouri', 'nickname': 'Billikens'},
        {'name': 'Virginia Commonwealth University', 'city': 'Richmond', 'state': 'Virginia', 'nickname': 'Rams'},
        {'name': 'Loyola University Chicago', 'city': 'Chicago', 'state': 'Illinois', 'nickname': 'Ramblers'}
    ]

    _insert_conference_teams(op, 'a10', a10_teams)

    # Mountain West Teams (11 teams)
    mwc_teams = [
        {'name': 'Air Force Academy', 'city': 'Colorado Springs', 'state': 'Colorado', 'nickname': 'Falcons'},
        {'name': 'Boise State University', 'city': 'Boise', 'state': 'Idaho', 'nickname': 'Broncos'},
        {'name': 'Colorado State University', 'city': 'Fort Collins', 'state': 'Colorado', 'nickname': 'Rams'},
        {'name': 'Fresno State University', 'city': 'Fresno', 'state': 'California', 'nickname': 'Bulldogs'},
        {'name': 'University of Nevada', 'city': 'Reno', 'state': 'Nevada', 'nickname': 'Wolf Pack'},
        {'name': 'University of Nevada Las Vegas', 'city': 'Las Vegas', 'state': 'Nevada', 'nickname': 'Rebels'},
        {'name': 'University of New Mexico', 'city': 'Albuquerque', 'state': 'New Mexico', 'nickname': 'Lobos'},
        {'name': 'San Diego State University', 'city': 'San Diego', 'state': 'California', 'nickname': 'Aztecs'},
        {'name': 'San Jose State University', 'city': 'San Jose', 'state': 'California', 'nickname': 'Spartans'},
        {'name': 'University of Wyoming', 'city': 'Laramie', 'state': 'Wyoming', 'nickname': 'Cowboys'},
        {'name': 'Utah State University', 'city': 'Logan', 'state': 'Utah', 'nickname': 'Aggies'}
    ]

    _insert_conference_teams(op, 'mountain-west', mwc_teams)

    # WCC Teams (10 teams)
    wcc_teams = [
        {'name': 'Brigham Young University Provo', 'city': 'Provo', 'state': 'Utah', 'nickname': 'Cougars'},
        {'name': 'Gonzaga University', 'city': 'Spokane', 'state': 'Washington', 'nickname': 'Bulldogs'},
        {'name': 'Loyola Marymount University', 'city': 'Los Angeles', 'state': 'California', 'nickname': 'Lions'},
        {'name': 'Pacific University', 'city': 'Stockton', 'state': 'California', 'nickname': 'Tigers'},
        {'name': 'Pepperdine University', 'city': 'Malibu', 'state': 'California', 'nickname': 'Waves'},
        {'name': 'University of Portland', 'city': 'Portland', 'state': 'Oregon', 'nickname': 'Pilots'},
        {'name': 'University of San Diego', 'city': 'San Diego', 'state': 'California', 'nickname': 'Toreros'},
        {'name': 'University of San Francisco', 'city': 'San Francisco', 'state': 'California', 'nickname': 'Dons'},
        {'name': 'Santa Clara University', 'city': 'Santa Clara', 'state': 'California', 'nickname': 'Broncos'},
        {'name': 'Saint Mary\'s College', 'city': 'Moraga', 'state': 'California', 'nickname': 'Gaels'}
    ]

    _insert_conference_teams(op, 'wcc', wcc_teams)

    print("✅ Phase 1 college basketball seed data (167 teams across 10 conferences) has been successfully inserted!")


def _insert_conference_teams(op, conference_slug: str, teams: list):
    """Helper function to insert teams for a specific conference."""

    for team in teams:
        # Create college slug
        college_slug = team['name'].lower().replace(' ', '-').replace('&', 'and').replace('\'', '')
        team_slug = f"{college_slug}-{team['nickname'].lower().replace(' ', '-')}"

        # Insert college
        op.execute(f"""
            INSERT INTO colleges (
                id, conference_id, name, slug, college_type, city, state, nickname,
                is_active, created_at, updated_at
            )
            SELECT
                gen_random_uuid(),
                cc.id,
                '{team['name']}',
                '{college_slug}',
                'public',
                '{team['city']}',
                '{team['state']}',
                '{team['nickname']}',
                true,
                NOW(),
                NOW()
            FROM college_conferences cc
            WHERE cc.slug = '{conference_slug}'
            ON CONFLICT (conference_id, slug) DO NOTHING;
        """)

        # Insert college team
        op.execute(f"""
            INSERT INTO college_teams (
                id, college_id, sport_id, name, slug, is_active,
                created_at, updated_at
            )
            SELECT
                gen_random_uuid(),
                c.id,
                s.id,
                '{team['nickname']}',
                '{team_slug}',
                true,
                NOW(),
                NOW()
            FROM colleges c
            JOIN college_conferences cc ON c.conference_id = cc.id
            JOIN sports s ON s.slug = 'college-basketball'
            WHERE cc.slug = '{conference_slug}' AND c.slug = '{college_slug}'
            ON CONFLICT (college_id, sport_id) DO NOTHING;
        """)


def downgrade() -> None:
    """Remove seed data for college basketball divisions, conferences, colleges, and teams."""

    # Delete in reverse order to maintain referential integrity
    op.execute("DELETE FROM college_teams WHERE sport_id IN (SELECT id FROM sports WHERE slug = 'college-basketball');")
    op.execute("DELETE FROM colleges WHERE conference_id IN (SELECT id FROM college_conferences WHERE slug IN ('acc', 'big-east', 'big-ten', 'big-12', 'pac-12', 'sec', 'aac', 'a10', 'mountain-west', 'wcc'));")
    op.execute("DELETE FROM college_conferences WHERE slug IN ('acc', 'big-east', 'big-ten', 'big-12', 'pac-12', 'sec', 'aac', 'a10', 'mountain-west', 'wcc');")
    op.execute("DELETE FROM divisions WHERE slug = 'division-i';")

    print("✅ Phase 1 college basketball seed data has been removed!")