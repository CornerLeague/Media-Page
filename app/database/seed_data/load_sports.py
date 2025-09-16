"""Load sports data into the database."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..models import Sport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sports_from_json(file_path: Path) -> List[Dict[str, Any]]:
    """Load sports data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sports_data = json.load(f)
        logger.info(f"Loaded {len(sports_data)} sports from {file_path}")
        return sports_data
    except FileNotFoundError:
        logger.error(f"Sports file not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return []


def create_or_update_sport(session: Session, sport_data: Dict[str, Any]) -> Sport:
    """Create or update a sport record."""
    sport_id = sport_data["id"]

    # Check if sport exists
    existing_sport = session.query(Sport).filter(Sport.id == sport_id).first()

    if existing_sport:
        # Update existing sport
        existing_sport.name = sport_data["name"]
        existing_sport.display_name = sport_data["display_name"]
        existing_sport.has_teams = sport_data["has_teams"]
        existing_sport.season_structure = sport_data.get("season_structure")
        sport = existing_sport
        logger.info(f"Updated existing sport: {sport_id}")
    else:
        # Create new sport
        sport = Sport(
            id=sport_id,
            name=sport_data["name"],
            display_name=sport_data["display_name"],
            has_teams=sport_data["has_teams"],
            season_structure=sport_data.get("season_structure")
        )
        session.add(sport)
        logger.info(f"Created new sport: {sport_id}")

    return sport


def load_sports(session: Session, sports_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Load all sports into the database."""
    results = {"created": 0, "updated": 0, "errors": 0}

    for sport_data in sports_data:
        try:
            existing_sport = session.query(Sport).filter(
                Sport.id == sport_data["id"]
            ).first()

            if existing_sport:
                create_or_update_sport(session, sport_data)
                results["updated"] += 1
            else:
                create_or_update_sport(session, sport_data)
                results["created"] += 1

        except IntegrityError as e:
            logger.error(f"Integrity error for sport {sport_data.get('id', 'unknown')}: {e}")
            results["errors"] += 1
            session.rollback()
        except Exception as e:
            logger.error(f"Error processing sport {sport_data.get('id', 'unknown')}: {e}")
            results["errors"] += 1
            session.rollback()

    return results


def load_all_sports() -> Dict[str, int]:
    """Load all sports from JSON files."""
    current_dir = Path(__file__).parent
    sports_file = current_dir / "sports.json"

    sports_data = load_sports_from_json(sports_file)
    if not sports_data:
        logger.error("No sports data loaded")
        return {"created": 0, "updated": 0, "errors": 1}

    with get_session() as session:
        try:
            results = load_sports(session, sports_data)
            session.commit()

            total_processed = results["created"] + results["updated"]
            logger.info(f"Sports loading completed: {total_processed} processed, "
                       f"{results['created']} created, {results['updated']} updated, "
                       f"{results['errors']} errors")

            return results

        except Exception as e:
            logger.error(f"Error during sports loading: {e}")
            session.rollback()
            return {"created": 0, "updated": 0, "errors": 1}


def get_sport_by_id(sport_id: str) -> Sport:
    """Get a sport by ID."""
    with get_session() as session:
        return session.query(Sport).filter(Sport.id == sport_id).first()


def list_all_sports() -> List[Sport]:
    """List all sports."""
    with get_session() as session:
        return session.query(Sport).order_by(Sport.display_name).all()


if __name__ == "__main__":
    """Run sports loading as a script."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        sports = list_all_sports()
        print(f"Found {len(sports)} sports:")
        for sport in sports:
            print(f"  {sport.id}: {sport.display_name}")
    else:
        results = load_all_sports()
        print(f"Sports loading results: {results}")