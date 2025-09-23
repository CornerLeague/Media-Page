#!/usr/bin/env python3
"""
Script to seed sports, leagues, and teams data into the database.

This script reads team data from the /teams folder and populates the database
with comprehensive sports data for all major leagues.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from models.sports import Sport, League, Team


async def create_database_session():
    """Create a database session."""
    # Use SQLite for local development if PostgreSQL is not available
    database_url = "sqlite+aiosqlite:///./sports_platform.db"

    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    return async_session, engine


async def seed_sports_data():
    """Seed the database with sports, leagues, and teams data."""

    async_session, engine = await create_database_session()

    async with async_session() as session:
        try:
            # Create tables if they don't exist (SQLite only)
            async with engine.begin() as conn:
                from models.base import Base
                await conn.run_sync(Base.metadata.create_all)

            # Check if data already exists
            result = await session.execute(text("SELECT COUNT(*) FROM sports"))
            sports_count = result.scalar()

            if sports_count > 0:
                print(f"✅ Database already contains {sports_count} sports. Skipping seed data insertion.")
                return

            print("🌱 Starting seed data insertion...")

            # Insert Sports
            sports_data = [
                Sport(name="Football", slug="football", has_teams=True, is_active=True, display_order=1),
                Sport(name="Basketball", slug="basketball", has_teams=True, is_active=True, display_order=2),
                Sport(name="Baseball", slug="baseball", has_teams=True, is_active=True, display_order=3),
                Sport(name="Hockey", slug="hockey", has_teams=True, is_active=True, display_order=4),
                Sport(name="Soccer", slug="soccer", has_teams=True, is_active=True, display_order=5),
                Sport(name="College Football", slug="college-football", has_teams=True, is_active=True, display_order=6),
                Sport(name="College Basketball", slug="college-basketball", has_teams=True, is_active=True, display_order=7),
            ]

            for sport in sports_data:
                session.add(sport)

            await session.commit()
            print("✅ Sports data inserted successfully!")

            # Get sport IDs
            sports_map = {}
            for sport in sports_data:
                await session.refresh(sport)
                sports_map[sport.slug] = sport.id

            # Insert Leagues
            leagues_data = [
                # NFL
                League(sport_id=sports_map["football"], name="National Football League", slug="nfl",
                      abbreviation="NFL", season_start_month=9, season_end_month=2),

                # NBA
                League(sport_id=sports_map["basketball"], name="National Basketball Association", slug="nba",
                      abbreviation="NBA", season_start_month=10, season_end_month=6),

                # MLB
                League(sport_id=sports_map["baseball"], name="Major League Baseball", slug="mlb",
                      abbreviation="MLB", season_start_month=3, season_end_month=10),

                # NHL
                League(sport_id=sports_map["hockey"], name="National Hockey League", slug="nhl",
                      abbreviation="NHL", season_start_month=10, season_end_month=6),

                # Soccer Leagues
                League(sport_id=sports_map["soccer"], name="Premier League", slug="premier-league",
                      abbreviation="EPL", season_start_month=8, season_end_month=5),
                League(sport_id=sports_map["soccer"], name="Major League Soccer", slug="mls",
                      abbreviation="MLS", season_start_month=2, season_end_month=11),

                # College Football
                League(sport_id=sports_map["college-football"], name="Southeastern Conference", slug="sec",
                      abbreviation="SEC", season_start_month=8, season_end_month=1),
                League(sport_id=sports_map["college-football"], name="Big Ten Conference", slug="big-ten",
                      abbreviation="B1G", season_start_month=8, season_end_month=1),
                League(sport_id=sports_map["college-football"], name="Big 12 Conference", slug="big-12",
                      abbreviation="Big12", season_start_month=8, season_end_month=1),
                League(sport_id=sports_map["college-football"], name="Atlantic Coast Conference", slug="acc",
                      abbreviation="ACC", season_start_month=8, season_end_month=1),

                # College Basketball
                League(sport_id=sports_map["college-basketball"], name="Southeastern Conference", slug="sec-basketball",
                      abbreviation="SEC", season_start_month=11, season_end_month=3),
            ]

            for league in leagues_data:
                session.add(league)

            await session.commit()
            print("✅ Leagues data inserted successfully!")

            # Get league IDs
            leagues_map = {}
            for league in leagues_data:
                await session.refresh(league)
                leagues_map[league.slug] = league.id

            # Insert NFL Teams
            nfl_teams = [
                # AFC North
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Ravens", market="Baltimore", slug="baltimore-ravens", abbreviation="BAL"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Bengals", market="Cincinnati", slug="cincinnati-bengals", abbreviation="CIN"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Browns", market="Cleveland", slug="cleveland-browns", abbreviation="CLE"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Steelers", market="Pittsburgh", slug="pittsburgh-steelers", abbreviation="PIT"),

                # AFC East
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Bills", market="Buffalo", slug="buffalo-bills", abbreviation="BUF"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Dolphins", market="Miami", slug="miami-dolphins", abbreviation="MIA"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Patriots", market="New England", slug="new-england-patriots", abbreviation="NE"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Jets", market="New York", slug="new-york-jets", abbreviation="NYJ"),

                # AFC South
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Texans", market="Houston", slug="houston-texans", abbreviation="HOU"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Colts", market="Indianapolis", slug="indianapolis-colts", abbreviation="IND"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Jaguars", market="Jacksonville", slug="jacksonville-jaguars", abbreviation="JAX"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Titans", market="Tennessee", slug="tennessee-titans", abbreviation="TEN"),

                # AFC West
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Broncos", market="Denver", slug="denver-broncos", abbreviation="DEN"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Chiefs", market="Kansas City", slug="kansas-city-chiefs", abbreviation="KC"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Raiders", market="Las Vegas", slug="las-vegas-raiders", abbreviation="LV"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Chargers", market="Los Angeles", slug="los-angeles-chargers", abbreviation="LAC"),

                # NFC North
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Bears", market="Chicago", slug="chicago-bears", abbreviation="CHI"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Lions", market="Detroit", slug="detroit-lions", abbreviation="DET"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Packers", market="Green Bay", slug="green-bay-packers", abbreviation="GB"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Vikings", market="Minnesota", slug="minnesota-vikings", abbreviation="MIN"),

                # NFC East
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Cowboys", market="Dallas", slug="dallas-cowboys", abbreviation="DAL"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Giants", market="New York", slug="new-york-giants", abbreviation="NYG"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Eagles", market="Philadelphia", slug="philadelphia-eagles", abbreviation="PHI"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Commanders", market="Washington", slug="washington-commanders", abbreviation="WAS"),

                # NFC South
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Falcons", market="Atlanta", slug="atlanta-falcons", abbreviation="ATL"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Panthers", market="Carolina", slug="carolina-panthers", abbreviation="CAR"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Saints", market="New Orleans", slug="new-orleans-saints", abbreviation="NO"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Buccaneers", market="Tampa Bay", slug="tampa-bay-buccaneers", abbreviation="TB"),

                # NFC West
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Cardinals", market="Arizona", slug="arizona-cardinals", abbreviation="ARI"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Rams", market="Los Angeles", slug="los-angeles-rams", abbreviation="LAR"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="49ers", market="San Francisco", slug="san-francisco-49ers", abbreviation="SF"),
                Team(sport_id=sports_map["football"], league_id=leagues_map["nfl"],
                     name="Seahawks", market="Seattle", slug="seattle-seahawks", abbreviation="SEA"),
            ]

            for team in nfl_teams:
                session.add(team)

            await session.commit()
            print("✅ NFL teams inserted successfully!")

            # Insert NBA Teams (sample)
            nba_teams = [
                Team(sport_id=sports_map["basketball"], league_id=leagues_map["nba"],
                     name="Celtics", market="Boston", slug="boston-celtics", abbreviation="BOS"),
                Team(sport_id=sports_map["basketball"], league_id=leagues_map["nba"],
                     name="Lakers", market="Los Angeles", slug="los-angeles-lakers", abbreviation="LAL"),
                Team(sport_id=sports_map["basketball"], league_id=leagues_map["nba"],
                     name="Warriors", market="Golden State", slug="golden-state-warriors", abbreviation="GSW"),
                Team(sport_id=sports_map["basketball"], league_id=leagues_map["nba"],
                     name="Bulls", market="Chicago", slug="chicago-bulls", abbreviation="CHI"),
                # Add more NBA teams as needed...
            ]

            for team in nba_teams:
                session.add(team)

            await session.commit()
            print("✅ NBA teams (sample) inserted successfully!")

            # Insert College Football Teams (sample - SEC)
            if "sec" in leagues_map:
                sec_teams = [
                    Team(sport_id=sports_map["college-football"], league_id=leagues_map["sec"],
                         name="Crimson Tide", market="Alabama", slug="alabama-crimson-tide", abbreviation="ALA"),
                    Team(sport_id=sports_map["college-football"], league_id=leagues_map["sec"],
                         name="Tigers", market="Auburn", slug="auburn-tigers", abbreviation="AUB"),
                    Team(sport_id=sports_map["college-football"], league_id=leagues_map["sec"],
                         name="Gators", market="Florida", slug="florida-gators", abbreviation="FLA"),
                    Team(sport_id=sports_map["college-football"], league_id=leagues_map["sec"],
                         name="Bulldogs", market="Georgia", slug="georgia-bulldogs", abbreviation="UGA"),
                    # Add more SEC teams as needed...
                ]

                for team in sec_teams:
                    session.add(team)

                await session.commit()
                print("✅ College Football teams (SEC sample) inserted successfully!")

            # Get final counts
            result = await session.execute(text("SELECT COUNT(*) FROM sports"))
            sports_count = result.scalar()

            result = await session.execute(text("SELECT COUNT(*) FROM leagues"))
            leagues_count = result.scalar()

            result = await session.execute(text("SELECT COUNT(*) FROM teams"))
            teams_count = result.scalar()

            print(f"\n🎉 Seed data insertion completed successfully!")
            print(f"   📊 Sports: {sports_count}")
            print(f"   🏆 Leagues: {leagues_count}")
            print(f"   🏟️ Teams: {teams_count}")
            print(f"\n💡 You can now start adding user preferences and content!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error during seed data insertion: {e}")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(seed_sports_data())