"""Load team seed data into the database."""

import json
import os
from pathlib import Path
from typing import List, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Team
from ..models.enums import Sport, League, TeamStatus
from ..database import get_session


def load_teams_from_json(file_path: Path) -> List[Dict]:
    """Load team data from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_team_from_data(team_data: Dict) -> Team:
    """Create a Team instance from dictionary data."""
    return Team(
        name=team_data['name'],
        city=team_data.get('city'),
        abbreviation=team_data['abbreviation'],
        sport=Sport(team_data['sport']),
        league=League(team_data['league']),
        conference=team_data.get('conference'),
        division=team_data.get('division'),
        logo_url=team_data.get('logo_url'),
        primary_color=team_data.get('primary_color'),
        secondary_color=team_data.get('secondary_color'),
        status=TeamStatus.ACTIVE
    )


def team_exists(session: Session, name: str, league: str) -> bool:
    """Check if team already exists in database."""
    result = session.execute(
        select(Team).where(
            Team.name == name,
            Team.league == League(league)
        )
    ).first()
    return result is not None


def load_teams_for_sport(session: Session, sport: str, force: bool = False) -> int:
    """Load teams for a specific sport."""
    seed_dir = Path(__file__).parent
    file_path = seed_dir / f"teams_{sport}.json"

    if not file_path.exists():
        print(f"Warning: Team data file not found: {file_path}")
        return 0

    team_data = load_teams_from_json(file_path)
    loaded_count = 0

    for data in team_data:
        # Check if team already exists
        if not force and team_exists(session, data['name'], data['league']):
            print(f"Team already exists: {data['city']} {data['name']} ({data['abbreviation']})")
            continue

        try:
            team = create_team_from_data(data)
            session.add(team)
            loaded_count += 1
            print(f"Added team: {team.city} {team.name} ({team.abbreviation})")

        except Exception as e:
            print(f"Error creating team {data['name']}: {e}")
            continue

    return loaded_count


def load_all_teams(force: bool = False) -> Dict[str, int]:
    """Load all team data into the database."""
    sports = ['nfl', 'nba', 'mlb', 'nhl']
    results = {}

    with get_session() as session:
        for sport in sports:
            print(f"\nLoading {sport.upper()} teams...")
            count = load_teams_for_sport(session, sport, force)
            results[sport] = count
            print(f"Loaded {count} {sport.upper()} teams")

        # Commit all changes
        session.commit()
        print(f"\nDatabase transaction committed successfully")

    return results


def verify_team_data() -> Dict[str, int]:
    """Verify loaded team data and return counts by sport."""
    with get_session() as session:
        counts = {}
        for sport in Sport:
            count = session.execute(
                select(Team).where(Team.sport == sport)
            ).fetchall()
            counts[sport.value] = len(count)

        return counts


def main():
    """Main function to load team seed data."""
    print("Loading team seed data...")

    # Load all teams
    results = load_all_teams(force=False)

    # Print summary
    print("\n" + "="*50)
    print("TEAM LOADING SUMMARY")
    print("="*50)

    total_loaded = sum(results.values())
    for sport, count in results.items():
        print(f"{sport.upper()}: {count} teams loaded")

    print(f"\nTotal teams loaded: {total_loaded}")

    # Verify data
    print("\nVerifying database...")
    verification = verify_team_data()

    print("\nTeams in database by sport:")
    total_in_db = sum(verification.values())
    for sport, count in verification.items():
        print(f"{sport.upper()}: {count} teams")

    print(f"\nTotal teams in database: {total_in_db}")

    if total_in_db > 0:
        print("\n✅ Team seed data loaded successfully!")
    else:
        print("\n❌ No teams found in database")


if __name__ == "__main__":
    main()