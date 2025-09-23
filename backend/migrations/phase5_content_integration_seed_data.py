"""
Phase 5: College Basketball Content Integration Seed Data
Comprehensive sample data for college basketball content types

This migration populates the Phase 5 content system with realistic sample data
including injury reports, recruiting news, coaching changes, and various content types.
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

logger = logging.getLogger(__name__)


class Phase5ContentSeedData:
    """
    Seed data for Phase 5 content integration models.

    Creates realistic sample data for:
    - College basketball content across various types
    - Injury reports for players
    - Recruiting news and transfer portal activity
    - Coaching changes and staff updates
    - Content classification examples
    """

    def __init__(self):
        self.migration_name = "Phase 5: Content Integration Seed Data"
        self.version = "20250921_2015_phase5_content_seed_data"

        # Cache for IDs we'll need to reference
        self.team_ids = {}
        self.player_ids = {}
        self.content_ids = {}

    async def upgrade(self, session: AsyncSession) -> None:
        """Apply Phase 5 content seed data"""
        logger.info(f"Starting {self.migration_name} upgrade...")

        try:
            # Load existing data IDs for references
            await self._load_reference_ids(session)

            # Create sample content across various types
            await self._create_sample_content(session)

            # Create injury reports
            await self._create_injury_reports(session)

            # Create recruiting news
            await self._create_recruiting_news(session)

            # Create coaching news
            await self._create_coaching_news(session)

            # Create content team associations
            await self._create_content_team_associations(session)

            # Create content classifications
            await self._create_content_classifications(session)

            await session.commit()
            logger.info(f"{self.migration_name} upgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.migration_name} upgrade: {str(e)}")
            raise

    async def downgrade(self, session: AsyncSession) -> None:
        """Remove Phase 5 content seed data"""
        logger.info(f"Starting {self.migration_name} downgrade...")

        try:
            # Delete in reverse dependency order
            await session.execute(text("DELETE FROM content_classifications"))
            await session.execute(text("DELETE FROM content_team_associations"))
            await session.execute(text("DELETE FROM coaching_news"))
            await session.execute(text("DELETE FROM recruiting_news"))
            await session.execute(text("DELETE FROM injury_reports"))
            await session.execute(text("DELETE FROM college_content"))

            await session.commit()
            logger.info(f"{self.migration_name} downgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.migration_name} downgrade: {str(e)}")
            raise

    async def _load_reference_ids(self, session: AsyncSession) -> None:
        """Load existing team and player IDs for references"""
        logger.info("Loading reference IDs...")

        # Load team IDs
        team_result = await session.execute(
            text("SELECT id, name FROM college_teams ORDER BY name LIMIT 20")
        )
        for row in team_result:
            self.team_ids[row.name] = row.id

        # Load player IDs
        player_result = await session.execute(
            text("SELECT id, full_name, team_id FROM players ORDER BY full_name LIMIT 50")
        )
        for row in player_result:
            self.player_ids[row.full_name] = {"id": row.id, "team_id": row.team_id}

        logger.info(f"Loaded {len(self.team_ids)} teams and {len(self.player_ids)} players")

    async def _create_sample_content(self, session: AsyncSession) -> None:
        """Create diverse college basketball content examples"""
        logger.info("Creating sample college basketball content...")

        # Get team IDs for content creation
        team_names = list(self.team_ids.keys())
        if len(team_names) < 2:
            logger.warning("Not enough teams loaded for comprehensive content examples")
            return

        content_examples = [
            # Game Preview
            {
                "title": f"{team_names[0]} vs {team_names[1]}: Big Conference Showdown Preview",
                "content_type": "game_preview",
                "summary": f"Two top-ranked teams clash in what could be the game of the year. {team_names[0]} brings their high-powered offense against {team_names[1]}'s stifling defense.",
                "content": f"The stage is set for an epic battle as {team_names[0]} travels to face {team_names[1]} in a contest that could shake up the conference standings. This matchup features contrasting styles that should make for compelling basketball.\n\n{team_names[0]} enters the game averaging 82.5 points per game, led by their dynamic backcourt. Their fast-paced offense has been nearly unstoppable this season.\n\n{team_names[1]}, meanwhile, has built their success on defensive intensity, allowing just 65.2 points per game. Their ability to control tempo will be crucial.\n\nKey matchups to watch include the battle in the paint and which team can establish their preferred pace early.",
                "primary_team_id": self.team_ids[team_names[0]],
                "secondary_team_id": self.team_ids[team_names[1]],
                "tags": ["preview", "conference", "rankings"],
                "word_count": 145,
                "reading_time_minutes": 1,
                "relevance_score": "0.95"
            },
            # Injury Report
            {
                "title": f"{team_names[0]} Star Player Questionable for Upcoming Games",
                "content_type": "injury_report",
                "summary": "Team's leading scorer dealing with ankle injury, status unclear for weekend games.",
                "content": f"The {team_names[0]} basketball program received concerning news today as their leading scorer is dealing with an ankle injury sustained in practice. The injury occurred during a routine drill and the player immediately sought medical attention.\n\nCoach Smith provided an update: 'We're taking a cautious approach with his recovery. His health is our top priority, and we won't rush him back before he's 100% ready.'\n\nThe player has been averaging 18.5 points and 6.2 rebounds per game this season and is considered crucial to the team's championship aspirations.",
                "primary_team_id": self.team_ids[team_names[0]],
                "tags": ["injury", "basketball", "player-health"],
                "word_count": 98,
                "reading_time_minutes": 1,
                "relevance_score": "0.88"
            },
            # Recruiting Commit
            {
                "title": f"Five-Star Recruit Commits to {team_names[1]} Basketball Program",
                "content_type": "recruiting_commit",
                "summary": "Top-ranked point guard chooses program after official visit, strengthening future outlook.",
                "content": f"In a major recruiting victory, {team_names[1]} has secured a commitment from five-star point guard Marcus Johnson, one of the top prospects in the class of 2025.\n\nJohnson, who stands 6'2\" and hails from Chicago, chose the program over offers from several other prestigious universities. His decision came after an official visit last weekend where he was impressed by the coaching staff's development plan.\n\n'The culture and family atmosphere really stood out to me,' Johnson said. 'Coach Williams showed me exactly how I can contribute and grow as a player.'\n\nJohnson is ranked as the #8 overall prospect in his class and the #2 point guard nationally by major recruiting services.",
                "primary_team_id": self.team_ids[team_names[1]],
                "tags": ["recruiting", "commitment", "five-star", "point-guard"],
                "word_count": 132,
                "reading_time_minutes": 1,
                "relevance_score": "0.92"
            },
            # Transfer Portal
            {
                "title": f"Former {team_names[0]} Forward Enters Transfer Portal",
                "content_type": "transfer_portal",
                "summary": "Junior forward seeks new opportunity after limited playing time this season.",
                "content": f"Junior forward Alex Thompson has entered the NCAA transfer portal, announcing his departure from {team_names[0]} after two seasons with the program.\n\nThompson, a 6'8\" forward from Atlanta, appeared in 28 games this season but saw his minutes decrease as the coaching staff opted for different lineup combinations. He averaged 5.2 points and 3.8 rebounds per game.\n\n'I want to thank Coach Davis and the entire program for the opportunity,' Thompson said in a statement. 'After discussions with my family and coaches, I feel it's best to explore new opportunities where I can contribute more significantly.'\n\nThompson has two years of eligibility remaining and is expected to draw interest from multiple programs seeking frontcourt depth.",
                "primary_team_id": self.team_ids[team_names[0]],
                "tags": ["transfer-portal", "forward", "eligibility"],
                "word_count": 118,
                "reading_time_minutes": 1,
                "relevance_score": "0.85"
            },
            # Coaching News
            {
                "title": f"{team_names[1]} Extends Head Coach Contract Through 2030",
                "content_type": "coach_extension",
                "summary": "Successful coach receives contract extension after leading team to consecutive tournament appearances.",
                "content": f"{team_names[1]} has announced a contract extension for head coach Sarah Williams that will keep her with the program through the 2030 season.\n\nWilliams, who is in her fifth season leading the program, has compiled a 98-47 record and guided the team to three consecutive NCAA tournament appearances, including a Sweet 16 run last season.\n\n'Coach Williams has transformed our program into a consistent contender,' said Athletic Director John Martinez. 'Her commitment to developing student-athletes both on and off the court aligns perfectly with our institutional values.'\n\nThe extension includes performance incentives and reinforces the university's commitment to maintaining championship-level basketball.",
                "primary_team_id": self.team_ids[team_names[1]],
                "tags": ["coaching", "contract", "extension", "success"],
                "word_count": 112,
                "reading_time_minutes": 1,
                "relevance_score": "0.90"
            },
            # Tournament Analysis
            {
                "title": "March Madness Bracket Predictions: Conference Tournament Impact",
                "content_type": "bracket_analysis",
                "summary": "Analyzing how conference tournament results could affect NCAA tournament seeding and at-large bids.",
                "content": "With conference tournaments underway, the NCAA tournament picture is becoming clearer, though several bubble teams still have work to do to secure their spots in the Big Dance.\n\nThe committee will be watching closely as automatic bids are claimed and at-large positions are finalized. Key storylines include potential bid thieves from mid-major conferences and power conference teams fighting for favorable seeding.\n\nTeams on the bubble must balance rest for key players with the need to impress the selection committee. Quality wins in conference tournaments can significantly boost a team's resume.\n\nExpect the final bracket to feature several surprising omissions and inclusions as teams make their final push for March Madness.",
                "tags": ["march-madness", "bracket", "tournament", "selection"],
                "word_count": 125,
                "reading_time_minutes": 1,
                "relevance_score": "0.87"
            },
            # Conference News
            {
                "title": "Conference Realignment: Impact on Basketball Schedules",
                "content_type": "conference_news",
                "summary": "New conference alignments create travel challenges and exciting new rivalries for basketball programs.",
                "content": "The latest wave of conference realignment continues to reshape college basketball, with programs adapting to new leagues and scheduling challenges.\n\nTravel costs and logistics have become major considerations as conferences now span greater geographic distances. Programs are investing in charter flights and adjusting practice schedules to accommodate longer road trips.\n\nDespite the challenges, coaches are excited about new matchups and recruiting opportunities. The expanded geographic footprint allows programs to recruit in new markets and build national brands.\n\nFans are already circling dates for inaugural conference matchups that will establish new traditions and rivalries in the evolving landscape of college basketball.",
                "tags": ["conference", "realignment", "travel", "scheduling"],
                "word_count": 108,
                "reading_time_minutes": 1,
                "relevance_score": "0.82"
            }
        ]

        for i, content_data in enumerate(content_examples):
            content_id = uuid4()
            self.content_ids[content_data["title"]] = content_id

            # Insert college content
            insert_sql = """
            INSERT INTO college_content (
                id, title, summary, content, content_type, primary_team_id, secondary_team_id,
                author, source, published_at, word_count, reading_time_minutes,
                relevance_score, tags, is_active, is_featured
            ) VALUES (
                :id, :title, :summary, :content, :content_type, :primary_team_id, :secondary_team_id,
                :author, :source, :published_at, :word_count, :reading_time_minutes,
                :relevance_score, :tags, :is_active, :is_featured
            )
            """

            await session.execute(text(insert_sql), {
                "id": content_id,
                "title": content_data["title"],
                "summary": content_data["summary"],
                "content": content_data["content"],
                "content_type": content_data["content_type"],
                "primary_team_id": content_data.get("primary_team_id"),
                "secondary_team_id": content_data.get("secondary_team_id"),
                "author": f"Staff Writer {i+1}",
                "source": "College Basketball Central",
                "published_at": datetime.now() - timedelta(days=i),
                "word_count": content_data["word_count"],
                "reading_time_minutes": content_data["reading_time_minutes"],
                "relevance_score": Decimal(content_data["relevance_score"]),
                "tags": content_data["tags"],
                "is_active": True,
                "is_featured": i < 2  # First two are featured
            })

    async def _create_injury_reports(self, session: AsyncSession) -> None:
        """Create sample injury reports"""
        logger.info("Creating injury reports...")

        if not self.player_ids:
            logger.warning("No players available for injury reports")
            return

        player_names = list(self.player_ids.keys())[:5]  # Take first 5 players

        injury_examples = [
            {
                "player_name": player_names[0],
                "injury_type": "ankle",
                "severity": "minor",
                "description": "Mild ankle sprain sustained during practice scrimmage",
                "injury_date": date.today() - timedelta(days=3),
                "expected_return": date.today() + timedelta(days=7),
                "current_status": "injured"
            },
            {
                "player_name": player_names[1],
                "injury_type": "knee",
                "severity": "moderate",
                "description": "MCL strain, no structural damage detected on MRI",
                "injury_date": date.today() - timedelta(days=14),
                "expected_return": date.today() + timedelta(days=21),
                "current_status": "injured"
            },
            {
                "player_name": player_names[2],
                "injury_type": "concussion",
                "severity": "major",
                "description": "Concussion protocol after collision during game",
                "injury_date": date.today() - timedelta(days=8),
                "expected_return": None,  # Unknown return date
                "current_status": "injured"
            }
        ]

        for injury_data in injury_examples:
            player_info = self.player_ids[injury_data["player_name"]]

            insert_sql = """
            INSERT INTO injury_reports (
                id, player_id, team_id, injury_type, injury_description, severity,
                injury_date, expected_return_date, current_status, games_missed
            ) VALUES (
                :id, :player_id, :team_id, :injury_type, :injury_description, :severity,
                :injury_date, :expected_return_date, :current_status, :games_missed
            )
            """

            await session.execute(text(insert_sql), {
                "id": uuid4(),
                "player_id": player_info["id"],
                "team_id": player_info["team_id"],
                "injury_type": injury_data["injury_type"],
                "injury_description": injury_data["description"],
                "severity": injury_data["severity"],
                "injury_date": injury_data["injury_date"],
                "expected_return_date": injury_data["expected_return"],
                "current_status": injury_data["current_status"],
                "games_missed": (date.today() - injury_data["injury_date"]).days // 3  # Approx games missed
            })

    async def _create_recruiting_news(self, session: AsyncSession) -> None:
        """Create sample recruiting news"""
        logger.info("Creating recruiting news...")

        if not self.team_ids:
            logger.warning("No teams available for recruiting news")
            return

        team_names = list(self.team_ids.keys())

        recruiting_examples = [
            {
                "recruit_name": "Marcus Johnson",
                "event_type": "commit",
                "team": team_names[0] if team_names else None,
                "position": "point_guard",
                "height": "6-2",
                "weight": 180,
                "hometown": "Chicago, IL",
                "high_school": "Lincoln Park High School",
                "rating": 5.0,
                "national_ranking": 8,
                "recruiting_class": 2025
            },
            {
                "recruit_name": "Sarah Williams",
                "event_type": "visit",
                "team": team_names[1] if len(team_names) > 1 else None,
                "position": "shooting_guard",
                "height": "5-9",
                "weight": 145,
                "hometown": "Atlanta, GA",
                "high_school": "Westside High School",
                "rating": 4.5,
                "national_ranking": 25,
                "recruiting_class": 2025
            },
            {
                "recruit_name": "Alex Thompson",
                "event_type": "transfer_entry",
                "team": None,  # Entering portal
                "previous_team": team_names[0] if team_names else None,
                "position": "power_forward",
                "height": "6-8",
                "weight": 225,
                "is_transfer": True,
                "eligibility_remaining": 2,
                "transfer_reason": "Seeking increased playing time and role"
            }
        ]

        for recruit_data in recruiting_examples:
            insert_sql = """
            INSERT INTO recruiting_news (
                id, recruit_name, event_type, team_id, previous_team_id, recruit_position,
                recruit_height, recruit_weight, hometown, high_school, rating, national_ranking,
                recruiting_class, is_transfer, eligibility_remaining, transfer_reason,
                event_date, source, verified
            ) VALUES (
                :id, :recruit_name, :event_type, :team_id, :previous_team_id, :recruit_position,
                :recruit_height, :recruit_weight, :hometown, :high_school, :rating, :national_ranking,
                :recruiting_class, :is_transfer, :eligibility_remaining, :transfer_reason,
                :event_date, :source, :verified
            )
            """

            await session.execute(text(insert_sql), {
                "id": uuid4(),
                "recruit_name": recruit_data["recruit_name"],
                "event_type": recruit_data["event_type"],
                "team_id": self.team_ids.get(recruit_data.get("team")) if recruit_data.get("team") else None,
                "previous_team_id": self.team_ids.get(recruit_data.get("previous_team")) if recruit_data.get("previous_team") else None,
                "recruit_position": recruit_data.get("position"),
                "recruit_height": recruit_data.get("height"),
                "recruit_weight": recruit_data.get("weight"),
                "hometown": recruit_data.get("hometown"),
                "high_school": recruit_data.get("high_school"),
                "rating": recruit_data.get("rating"),
                "national_ranking": recruit_data.get("national_ranking"),
                "recruiting_class": recruit_data.get("recruiting_class"),
                "is_transfer": recruit_data.get("is_transfer", False),
                "eligibility_remaining": recruit_data.get("eligibility_remaining"),
                "transfer_reason": recruit_data.get("transfer_reason"),
                "event_date": date.today() - timedelta(days=7),
                "source": "Recruiting Central",
                "verified": True
            })

    async def _create_coaching_news(self, session: AsyncSession) -> None:
        """Create sample coaching news"""
        logger.info("Creating coaching news...")

        if not self.team_ids:
            logger.warning("No teams available for coaching news")
            return

        team_names = list(self.team_ids.keys())

        coaching_examples = [
            {
                "coach_name": "Sarah Williams",
                "position_title": "Head Coach",
                "team": team_names[0] if team_names else None,
                "change_type": "extension",
                "contract_years": 5,
                "salary_amount": 750000,
                "coaching_background": "Former assistant coach at major conference program",
                "reason": "Successful program turnaround and consistent tournament appearances"
            },
            {
                "coach_name": "Mike Johnson",
                "position_title": "Assistant Coach",
                "team": team_names[1] if len(team_names) > 1 else None,
                "change_type": "hire",
                "previous_position": "Associate Head Coach at State University",
                "coaching_background": "15 years of coaching experience at various levels",
                "reason": "Expertise in player development and recruiting"
            },
            {
                "coach_name": "David Smith",
                "position_title": "Head Coach",
                "team": team_names[2] if len(team_names) > 2 else None,
                "change_type": "resignation",
                "tenure_years": 8,
                "team_record": "142-98",
                "reason": "Pursuing other opportunities in basketball"
            }
        ]

        for coaching_data in coaching_examples:
            insert_sql = """
            INSERT INTO coaching_news (
                id, coach_name, position_title, team_id, change_type, effective_date,
                previous_position, contract_years, salary_amount, coaching_background,
                reason, team_record, tenure_years, source, verified
            ) VALUES (
                :id, :coach_name, :position_title, :team_id, :change_type, :effective_date,
                :previous_position, :contract_years, :salary_amount, :coaching_background,
                :reason, :team_record, :tenure_years, :source, :verified
            )
            """

            await session.execute(text(insert_sql), {
                "id": uuid4(),
                "coach_name": coaching_data["coach_name"],
                "position_title": coaching_data["position_title"],
                "team_id": self.team_ids.get(coaching_data["team"]) if coaching_data.get("team") else None,
                "change_type": coaching_data["change_type"],
                "effective_date": date.today() + timedelta(days=30),
                "previous_position": coaching_data.get("previous_position"),
                "contract_years": coaching_data.get("contract_years"),
                "salary_amount": coaching_data.get("salary_amount"),
                "coaching_background": coaching_data.get("coaching_background"),
                "reason": coaching_data.get("reason"),
                "team_record": coaching_data.get("team_record"),
                "tenure_years": coaching_data.get("tenure_years"),
                "source": "Coaching News Network",
                "verified": True
            })

    async def _create_content_team_associations(self, session: AsyncSession) -> None:
        """Create content-team associations for multi-team content"""
        logger.info("Creating content-team associations...")

        if not self.content_ids or not self.team_ids:
            logger.warning("Missing content or team IDs for associations")
            return

        # Create associations for content that mentions multiple teams
        team_names = list(self.team_ids.keys())
        if len(team_names) >= 2:
            # Associate bracket analysis with multiple teams
            bracket_content_title = "March Madness Bracket Predictions: Conference Tournament Impact"
            if bracket_content_title in self.content_ids:
                for i, team_name in enumerate(team_names[:4]):  # Associate with 4 teams
                    insert_sql = """
                    INSERT INTO content_team_associations (
                        id, content_id, team_id, relevance_score, association_type
                    ) VALUES (
                        :id, :content_id, :team_id, :relevance_score, :association_type
                    )
                    """

                    await session.execute(text(insert_sql), {
                        "id": uuid4(),
                        "content_id": self.content_ids[bracket_content_title],
                        "team_id": self.team_ids[team_name],
                        "relevance_score": 0.8 - (i * 0.1),  # Decreasing relevance
                        "association_type": "mentioned"
                    })

    async def _create_content_classifications(self, session: AsyncSession) -> None:
        """Create content classifications for sample content"""
        logger.info("Creating content classifications...")

        if not self.content_ids:
            logger.warning("No content IDs available for classifications")
            return

        # Create classifications for a few content pieces
        classifications = [
            {
                "classification_type": "sentiment",
                "classification_value": "positive",
                "confidence_score": 0.85,
                "classifier_model": "sentiment_analyzer_v1"
            },
            {
                "classification_type": "urgency",
                "classification_value": "high",
                "confidence_score": 0.92,
                "classifier_model": "urgency_classifier_v1"
            },
            {
                "classification_type": "topic",
                "classification_value": "recruiting",
                "confidence_score": 0.96,
                "classifier_model": "topic_classifier_v1"
            }
        ]

        content_title = list(self.content_ids.keys())[0] if self.content_ids else None
        if content_title:
            for class_data in classifications:
                insert_sql = """
                INSERT INTO content_classifications (
                    id, content_id, classification_type, classification_value,
                    confidence_score, classifier_model
                ) VALUES (
                    :id, :content_id, :classification_type, :classification_value,
                    :confidence_score, :classifier_model
                )
                """

                await session.execute(text(insert_sql), {
                    "id": uuid4(),
                    "content_id": self.content_ids[content_title],
                    "classification_type": class_data["classification_type"],
                    "classification_value": class_data["classification_value"],
                    "confidence_score": class_data["confidence_score"],
                    "classifier_model": class_data["classifier_model"]
                })


async def run_seed_data():
    """Run the Phase 5 Content Integration seed data migration"""
    migration = Phase5ContentSeedData()

    async with get_async_session() as session:
        await migration.upgrade(session)
        print("Phase 5 Content Integration seed data migration completed successfully!")


async def run_rollback():
    """Rollback the Phase 5 Content Integration seed data migration"""
    migration = Phase5ContentSeedData()

    async with get_async_session() as session:
        await migration.downgrade(session)
        print("Phase 5 Content Integration seed data rollback completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(run_rollback())
    else:
        asyncio.run(run_seed_data())