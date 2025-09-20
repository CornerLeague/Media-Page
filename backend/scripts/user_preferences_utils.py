#!/usr/bin/env python3
"""
User Preferences Utility Script

This script provides utilities for managing and querying user preferences
in the Corner League Media sports platform.

Usage examples:
    python user_preferences_utils.py --check-schema
    python user_preferences_utils.py --analyze-user firebase_uid_here
    python user_preferences_utils.py --bulk-import-teams teams.csv
"""

import asyncio
import csv
import sys
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from uuid import UUID

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path so we can import models
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.users import User, UserSportPreference, UserTeamPreference, UserNewsPreference
from models.sports import Sport, Team


class UserPreferencesManager:
    """Manager class for user preferences operations."""

    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def check_schema_integrity(self) -> Dict[str, bool]:
        """Check if all user preference tables exist and are properly configured."""
        async with self.session_factory() as session:
            checks = {}

            # Check if tables exist
            table_checks = [
                "user_sport_preferences",
                "user_team_preferences",
                "user_news_preferences",
                "user_notification_settings"
            ]

            for table in table_checks:
                result = await session.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table}'
                    );
                """))
                checks[f"{table}_exists"] = result.scalar()

            # Check foreign key constraints
            constraint_query = """
                SELECT constraint_name, table_name
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_name IN ('user_sport_preferences', 'user_team_preferences', 'user_news_preferences')
            """
            result = await session.execute(text(constraint_query))
            fk_constraints = result.fetchall()
            checks["foreign_key_constraints"] = len(fk_constraints) >= 6  # Expected minimum

            # Check indexes
            index_query = """
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE tablename IN ('user_sport_preferences', 'user_team_preferences')
                AND indexname LIKE 'idx_%'
            """
            result = await session.execute(text(index_query))
            indexes = result.fetchall()
            checks["performance_indexes"] = len(indexes) >= 4  # Expected minimum

            return checks

    async def analyze_user_preferences(self, firebase_uid: str) -> Dict[str, any]:
        """Analyze a user's preferences and return detailed information."""
        async with self.session_factory() as session:
            # Get user
            user_result = await session.execute(
                text("SELECT id, display_name, email FROM users WHERE firebase_uid = :uid"),
                {"uid": firebase_uid}
            )
            user_row = user_result.fetchone()

            if not user_row:
                return {"error": f"User with firebase_uid {firebase_uid} not found"}

            user_id = user_row[0]
            analysis = {
                "user_id": str(user_id),
                "display_name": user_row[1],
                "email": user_row[2]
            }

            # Get sport preferences with sport names
            sport_prefs_query = """
                SELECT s.name, usp.rank, usp.is_active, usp.created_at
                FROM user_sport_preferences usp
                JOIN sports s ON usp.sport_id = s.id
                WHERE usp.user_id = :user_id
                ORDER BY usp.rank
            """
            result = await session.execute(text(sport_prefs_query), {"user_id": user_id})
            analysis["sport_preferences"] = [
                {
                    "sport": row[0],
                    "rank": row[1],
                    "is_active": row[2],
                    "created_at": row[3].isoformat() if row[3] else None
                }
                for row in result.fetchall()
            ]

            # Get team preferences with team names
            team_prefs_query = """
                SELECT t.name, t.market, utp.affinity_score, utp.is_active, utp.created_at
                FROM user_team_preferences utp
                JOIN teams t ON utp.team_id = t.id
                WHERE utp.user_id = :user_id
                ORDER BY utp.affinity_score DESC
            """
            result = await session.execute(text(team_prefs_query), {"user_id": user_id})
            analysis["team_preferences"] = [
                {
                    "team": f"{row[1]} {row[0]}",  # Market + Name
                    "affinity_score": float(row[2]),
                    "is_active": row[3],
                    "created_at": row[4].isoformat() if row[4] else None
                }
                for row in result.fetchall()
            ]

            # Get news preferences
            news_prefs_query = """
                SELECT news_type, enabled, priority
                FROM user_news_preferences
                WHERE user_id = :user_id
                ORDER BY priority DESC
            """
            result = await session.execute(text(news_prefs_query), {"user_id": user_id})
            analysis["news_preferences"] = [
                {
                    "news_type": row[0],
                    "enabled": row[1],
                    "priority": row[2]
                }
                for row in result.fetchall()
            ]

            return analysis

    async def get_popular_teams_by_sport(self, sport_name: str, limit: int = 10) -> List[Dict]:
        """Get most followed teams for a specific sport."""
        async with self.session_factory() as session:
            query = """
                SELECT
                    t.name,
                    t.market,
                    COUNT(utp.user_id) as follower_count,
                    AVG(utp.affinity_score) as avg_affinity
                FROM teams t
                JOIN sports s ON t.sport_id = s.id
                LEFT JOIN user_team_preferences utp ON t.id = utp.team_id AND utp.is_active = true
                WHERE s.name = :sport_name
                GROUP BY t.id, t.name, t.market
                ORDER BY follower_count DESC, avg_affinity DESC
                LIMIT :limit
            """
            result = await session.execute(text(query), {"sport_name": sport_name, "limit": limit})

            return [
                {
                    "team": f"{row[1]} {row[0]}",
                    "follower_count": row[2],
                    "avg_affinity": float(row[3]) if row[3] else 0.0
                }
                for row in result.fetchall()
            ]

    async def create_user_sport_preference(
        self,
        firebase_uid: str,
        sport_name: str,
        rank: int
    ) -> bool:
        """Create or update a user's sport preference."""
        async with self.session_factory() as session:
            try:
                # Get user ID and sport ID
                user_result = await session.execute(
                    text("SELECT id FROM users WHERE firebase_uid = :uid"),
                    {"uid": firebase_uid}
                )
                user_id = user_result.scalar()

                sport_result = await session.execute(
                    text("SELECT id FROM sports WHERE name = :name"),
                    {"name": sport_name}
                )
                sport_id = sport_result.scalar()

                if not user_id or not sport_id:
                    return False

                # Insert or update preference
                upsert_query = """
                    INSERT INTO user_sport_preferences (user_id, sport_id, rank, is_active)
                    VALUES (:user_id, :sport_id, :rank, true)
                    ON CONFLICT (user_id, sport_id)
                    DO UPDATE SET rank = :rank, is_active = true, updated_at = NOW()
                """
                await session.execute(text(upsert_query), {
                    "user_id": user_id,
                    "sport_id": sport_id,
                    "rank": rank
                })
                await session.commit()
                return True

            except Exception as e:
                await session.rollback()
                print(f"Error creating sport preference: {e}")
                return False

    async def create_user_team_preference(
        self,
        firebase_uid: str,
        team_name: str,
        market: str,
        affinity_score: float = 0.5
    ) -> bool:
        """Create or update a user's team preference."""
        async with self.session_factory() as session:
            try:
                # Get user ID and team ID
                user_result = await session.execute(
                    text("SELECT id FROM users WHERE firebase_uid = :uid"),
                    {"uid": firebase_uid}
                )
                user_id = user_result.scalar()

                team_result = await session.execute(
                    text("SELECT id FROM teams WHERE name = :name AND market = :market"),
                    {"name": team_name, "market": market}
                )
                team_id = team_result.scalar()

                if not user_id or not team_id:
                    return False

                # Insert or update preference
                upsert_query = """
                    INSERT INTO user_team_preferences (user_id, team_id, affinity_score, is_active)
                    VALUES (:user_id, :team_id, :affinity_score, true)
                    ON CONFLICT (user_id, team_id)
                    DO UPDATE SET affinity_score = :affinity_score, is_active = true, updated_at = NOW()
                """
                await session.execute(text(upsert_query), {
                    "user_id": user_id,
                    "team_id": team_id,
                    "affinity_score": Decimal(str(affinity_score))
                })
                await session.commit()
                return True

            except Exception as e:
                await session.rollback()
                print(f"Error creating team preference: {e}")
                return False

    async def get_personalized_content_preview(self, firebase_uid: str, limit: int = 5) -> List[Dict]:
        """Get a preview of personalized content for a user."""
        async with self.session_factory() as session:
            # Get user ID
            user_result = await session.execute(
                text("SELECT id FROM users WHERE firebase_uid = :uid"),
                {"uid": firebase_uid}
            )
            user_id = user_result.scalar()

            if not user_id:
                return []

            # Use the existing personalized articles function
            query = """
                SELECT * FROM get_personalized_articles(:user_id, :limit)
            """
            result = await session.execute(text(query), {
                "user_id": user_id,
                "limit": limit
            })

            return [
                {
                    "article_id": str(row[0]),
                    "title": row[1],
                    "summary": row[2],
                    "published_at": row[3].isoformat() if row[3] else None,
                    "relevance_score": float(row[4]) if row[4] else 0.0
                }
                for row in result.fetchall()
            ]

    async def close(self):
        """Close the database connection."""
        await self.engine.dispose()


async def main():
    """Main CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description='User Preferences Management Utilities')
    parser.add_argument('--database-url', default='postgresql+asyncpg://postgres:password@localhost:5432/cornerleague')
    parser.add_argument('--check-schema', action='store_true', help='Check schema integrity')
    parser.add_argument('--analyze-user', help='Analyze user preferences by Firebase UID')
    parser.add_argument('--popular-teams', help='Get popular teams for sport')
    parser.add_argument('--personalized-content', help='Get personalized content preview for Firebase UID')

    args = parser.parse_args()

    manager = UserPreferencesManager(args.database_url)

    try:
        if args.check_schema:
            print("🔍 Checking schema integrity...")
            checks = await manager.check_schema_integrity()
            for check, result in checks.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {check}: {status}")

        elif args.analyze_user:
            print(f"👤 Analyzing user preferences for: {args.analyze_user}")
            analysis = await manager.analyze_user_preferences(args.analyze_user)
            if "error" in analysis:
                print(f"❌ {analysis['error']}")
            else:
                print(f"📧 Email: {analysis['email']}")
                print(f"👋 Display Name: {analysis['display_name']}")

                print(f"\n🏈 Sport Preferences ({len(analysis['sport_preferences'])}):")
                for pref in analysis['sport_preferences']:
                    active = "✅" if pref['is_active'] else "❌"
                    print(f"  {pref['rank']}. {pref['sport']} {active}")

                print(f"\n🏆 Team Preferences ({len(analysis['team_preferences'])}):")
                for pref in analysis['team_preferences']:
                    active = "✅" if pref['is_active'] else "❌"
                    print(f"  {pref['team']} (affinity: {pref['affinity_score']:.2f}) {active}")

                print(f"\n📰 News Preferences ({len(analysis['news_preferences'])}):")
                for pref in analysis['news_preferences']:
                    enabled = "✅" if pref['enabled'] else "❌"
                    print(f"  {pref['news_type']} (priority: {pref['priority']}) {enabled}")

        elif args.popular_teams:
            print(f"🔥 Popular teams for {args.popular_teams}:")
            teams = await manager.get_popular_teams_by_sport(args.popular_teams)
            for i, team in enumerate(teams, 1):
                print(f"  {i}. {team['team']} - {team['follower_count']} followers (avg affinity: {team['avg_affinity']:.2f})")

        elif args.personalized_content:
            print(f"📋 Personalized content for: {args.personalized_content}")
            content = await manager.get_personalized_content_preview(args.personalized_content)
            for i, article in enumerate(content, 1):
                print(f"  {i}. {article['title'][:60]}... (relevance: {article['relevance_score']:.2f})")

        else:
            parser.print_help()

    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())