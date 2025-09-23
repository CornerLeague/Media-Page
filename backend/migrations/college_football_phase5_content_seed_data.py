"""
College Football Phase 5: Content Integration Seed Data
Comprehensive sample data for college football content types

This migration populates the Football Phase 5 content system with realistic sample data
including injury reports, recruiting news, coaching changes, depth chart updates,
game previews, bowl news, and various football-specific content types.
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


class CollegeFootballPhase5ContentSeedData:
    """
    Seed data for College Football Phase 5 content integration models.

    Creates realistic sample data for:
    - College football content across various types
    - Football injury reports with depth chart implications
    - Football recruiting news and transfer portal activity
    - Football coaching changes and staff updates
    - Football depth chart updates and position battles
    - Football game previews and analysis
    - Football bowl and playoff news
    """

    def __init__(self):
        self.migration_name = "College Football Phase 5: Content Integration Seed Data"
        self.version = "20250921_2215_college_football_phase5_content_seed_data"

        # Cache for IDs we'll need to reference
        self.team_ids = {}
        self.player_ids = {}
        self.game_ids = {}
        self.bowl_game_ids = {}
        self.content_ids = {}

        # Current date for relative timing
        self.today = date.today()

    async def upgrade(self, session: AsyncSession) -> None:
        """Apply College Football Phase 5 content seed data"""
        logger.info(f"Starting {self.migration_name} upgrade...")

        try:
            # Load existing data IDs for references
            await self._load_reference_ids(session)

            # Create sample football content across various types
            await self._create_sample_football_content(session)

            # Create football injury reports
            await self._create_football_injury_reports(session)

            # Create football recruiting news
            await self._create_football_recruiting_news(session)

            # Create football coaching news
            await self._create_football_coaching_news(session)

            # Create football depth chart updates
            await self._create_football_depth_chart_updates(session)

            # Create football game previews
            await self._create_football_game_previews(session)

            # Create football bowl news
            await self._create_football_bowl_news(session)

            await session.commit()
            logger.info(f"{self.migration_name} upgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.migration_name} upgrade: {str(e)}")
            raise

    async def downgrade(self, session: AsyncSession) -> None:
        """Remove College Football Phase 5 content seed data"""
        logger.info(f"Starting {self.migration_name} downgrade...")

        try:
            # Delete in reverse dependency order
            await session.execute(text("DELETE FROM football_bowl_news"))
            await session.execute(text("DELETE FROM football_game_previews"))
            await session.execute(text("DELETE FROM football_depth_chart_updates"))
            await session.execute(text("DELETE FROM football_coaching_news"))
            await session.execute(text("DELETE FROM football_recruiting_news"))
            await session.execute(text("DELETE FROM football_injury_reports"))
            await session.execute(text("DELETE FROM football_content"))

            await session.commit()
            logger.info(f"{self.migration_name} downgrade completed successfully")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in {self.migration_name} downgrade: {str(e)}")
            raise

    async def _load_reference_ids(self, session: AsyncSession) -> None:
        """Load existing entity IDs for foreign key references"""
        logger.info("Loading reference IDs...")

        # Load football team IDs
        team_result = await session.execute(text("""
            SELECT ft.id, ct.name
            FROM football_teams ft
            JOIN college_teams ct ON ft.college_team_id = ct.id
            LIMIT 20
        """))
        for row in team_result:
            self.team_ids[row.name] = row.id

        # Load football player IDs
        player_result = await session.execute(text("""
            SELECT fp.id, fp.first_name, fp.last_name, fp.position
            FROM football_players fp
            LIMIT 50
        """))
        for row in player_result:
            full_name = f"{row.first_name} {row.last_name}"
            self.player_ids[full_name] = {
                'id': row.id,
                'position': row.position
            }

        # Load football game IDs
        game_result = await session.execute(text("""
            SELECT id, home_team_id, away_team_id, game_date
            FROM football_games
            WHERE game_date >= CURRENT_DATE - INTERVAL '30 days'
            LIMIT 10
        """))
        for row in game_result:
            self.game_ids[str(row.id)] = {
                'id': row.id,
                'home_team_id': row.home_team_id,
                'away_team_id': row.away_team_id,
                'game_date': row.game_date
            }

        # Load bowl game IDs
        bowl_result = await session.execute(text("""
            SELECT id, name, game_date
            FROM bowl_games
            WHERE game_date >= CURRENT_DATE
            LIMIT 10
        """))
        for row in bowl_result:
            self.bowl_game_ids[row.name] = row.id

        logger.info(f"Loaded {len(self.team_ids)} teams, {len(self.player_ids)} players, "
                   f"{len(self.game_ids)} games, {len(self.bowl_game_ids)} bowl games")

    async def _create_sample_football_content(self, session: AsyncSession) -> None:
        """Create diverse football content samples"""
        logger.info("Creating sample football content...")

        # Get some team IDs for content
        team_names = list(self.team_ids.keys())[:10]

        content_samples = [
            # Game content
            {
                'title': 'Alabama vs Georgia: SEC Championship Game Preview',
                'summary': 'Two powerhouse programs clash for the SEC title with playoff implications.',
                'content': 'The SEC Championship Game features two of college football\'s most storied programs...',
                'content_type': 'game_preview',
                'primary_team_id': self.team_ids.get('Alabama Crimson Tide'),
                'secondary_team_id': self.team_ids.get('Georgia Bulldogs'),
                'tags': ['SEC Championship', 'College Football Playoff', 'rivalry'],
                'mentioned_coaches': ['Nick Saban', 'Kirby Smart']
            },
            {
                'title': 'Ohio State Dominates Michigan in The Game',
                'summary': 'Buckeyes cruise to victory in latest edition of college football\'s greatest rivalry.',
                'content': 'Ohio State put on a dominant performance against Michigan in The Game...',
                'content_type': 'game_recap',
                'primary_team_id': self.team_ids.get('Ohio State Buckeyes'),
                'secondary_team_id': self.team_ids.get('Michigan Wolverines'),
                'tags': ['The Game', 'rivalry', 'Big Ten'],
                'mentioned_players': ['C.J. Stroud', 'J.J. McCarthy']
            },

            # Injury content
            {
                'title': 'Star Quarterback Out 4-6 Weeks with Shoulder Injury',
                'summary': 'Starting QB suffered shoulder injury in practice, backup to take over.',
                'content': 'The team announced that their starting quarterback will miss 4-6 weeks...',
                'content_type': 'injury_report',
                'primary_team_id': self.team_ids.get(team_names[0]) if team_names else None,
                'tags': ['injury', 'quarterback', 'depth chart'],
                'injury_status_impact': 'Starting quarterback role affected'
            },

            # Recruiting content
            {
                'title': '5-Star QB Commits to Texas During Official Visit',
                'summary': 'Top quarterback prospect announces commitment to Longhorns.',
                'content': 'In a surprise move during his official visit, five-star quarterback...',
                'content_type': 'recruiting_commit',
                'primary_team_id': self.team_ids.get('Texas Longhorns'),
                'recruiting_class_year': 2025,
                'tags': ['recruiting', 'commitment', '5-star', 'quarterback'],
                'mentioned_recruits': ['Arch Manning']
            },

            # Transfer portal content
            {
                'title': 'Starting Running Back Enters Transfer Portal',
                'summary': 'Senior RB seeking new opportunity after coaching change.',
                'content': 'Following the recent coaching staff changes, the team\'s leading rusher...',
                'content_type': 'transfer_portal_entry',
                'primary_team_id': self.team_ids.get(team_names[1]) if len(team_names) > 1 else None,
                'tags': ['transfer portal', 'running back', 'coaching change'],
                'position_groups_mentioned': ['running_back']
            },

            # Coaching content
            {
                'title': 'Former NFL Coordinator Named New Offensive Coordinator',
                'summary': 'Program hires experienced coordinator to lead explosive offense.',
                'content': 'The university announced the hiring of a former NFL coordinator...',
                'content_type': 'coach_hire',
                'primary_team_id': self.team_ids.get(team_names[2]) if len(team_names) > 2 else None,
                'coaching_position_mentioned': 'offensive_coordinator',
                'tags': ['coaching hire', 'offensive coordinator', 'NFL experience']
            },

            # Depth chart content
            {
                'title': 'Freshman WR Moves Up to Starting Role',
                'summary': 'Young receiver earns starting position after strong fall camp.',
                'content': 'Following an impressive fall camp, the freshman wide receiver...',
                'content_type': 'depth_chart_update',
                'primary_team_id': self.team_ids.get(team_names[3]) if len(team_names) > 3 else None,
                'position_groups_mentioned': ['wide_receiver'],
                'tags': ['depth chart', 'freshman', 'wide receiver', 'promotion']
            },

            # Bowl content
            {
                'title': 'Rose Bowl Matchup Set: Wisconsin vs Oregon',
                'summary': 'Big Ten and Pac-12 champions to meet in the Granddaddy of Them All.',
                'content': 'The Rose Bowl Committee announced the matchup for this year\'s game...',
                'content_type': 'bowl_selection',
                'primary_team_id': self.team_ids.get('Wisconsin Badgers'),
                'secondary_team_id': self.team_ids.get('Oregon Ducks'),
                'tags': ['Rose Bowl', 'Big Ten', 'Pac-12', 'tradition']
            },

            # Conference content
            {
                'title': 'Big 12 Expansion: Four New Teams Join Conference',
                'summary': 'Conference announces major expansion with Colorado, Arizona schools.',
                'content': 'In a major realignment move, the Big 12 announced the addition...',
                'content_type': 'conference_realignment',
                'tags': ['Big 12', 'conference realignment', 'expansion']
            },

            # Rankings content
            {
                'title': 'College Football Playoff Rankings: Georgia Jumps to #1',
                'summary': 'Bulldogs move to top spot after dominant win over ranked opponent.',
                'content': 'The College Football Playoff committee released its latest rankings...',
                'content_type': 'playoff_ranking',
                'primary_team_id': self.team_ids.get('Georgia Bulldogs'),
                'tags': ['CFP rankings', 'playoff', 'poll update']
            }
        ]

        # Insert content
        for i, content in enumerate(content_samples):
            content_id = uuid4()
            self.content_ids[content['title']] = content_id

            await session.execute(text("""
                INSERT INTO football_content (
                    id, title, summary, content, content_type, primary_team_id, secondary_team_id,
                    source, published_at, author, tags, mentioned_players, mentioned_coaches,
                    mentioned_recruits, recruiting_class_year, coaching_position_mentioned,
                    injury_status_impact, position_groups_mentioned, relevance_score,
                    word_count, reading_time_minutes, is_featured, is_breaking_news
                ) VALUES (
                    :id, :title, :summary, :content, :content_type, :primary_team_id, :secondary_team_id,
                    :source, :published_at, :author, :tags, :mentioned_players, :mentioned_coaches,
                    :mentioned_recruits, :recruiting_class_year, :coaching_position_mentioned,
                    :injury_status_impact, :position_groups_mentioned, :relevance_score,
                    :word_count, :reading_time_minutes, :is_featured, :is_breaking_news
                )
            """), {
                'id': content_id,
                'title': content['title'],
                'summary': content['summary'],
                'content': content['content'],
                'content_type': content['content_type'],
                'primary_team_id': content.get('primary_team_id'),
                'secondary_team_id': content.get('secondary_team_id'),
                'source': 'ESPN',
                'published_at': datetime.now() - timedelta(days=i),
                'author': f'Reporter {i+1}',
                'tags': content.get('tags', []),
                'mentioned_players': content.get('mentioned_players', []),
                'mentioned_coaches': content.get('mentioned_coaches', []),
                'mentioned_recruits': content.get('mentioned_recruits', []),
                'recruiting_class_year': content.get('recruiting_class_year'),
                'coaching_position_mentioned': content.get('coaching_position_mentioned'),
                'injury_status_impact': content.get('injury_status_impact'),
                'position_groups_mentioned': content.get('position_groups_mentioned', []),
                'relevance_score': Decimal('0.8'),
                'word_count': 500 + (i * 50),
                'reading_time_minutes': 3 + i,
                'is_featured': i < 3,
                'is_breaking_news': i < 2
            })

    async def _create_football_injury_reports(self, session: AsyncSession) -> None:
        """Create football injury reports"""
        logger.info("Creating football injury reports...")

        if not self.player_ids or not self.team_ids:
            logger.warning("No players or teams found, skipping injury reports")
            return

        player_names = list(self.player_ids.keys())[:10]
        team_names = list(self.team_ids.keys())[:5]

        injury_reports = [
            {
                'player_name': player_names[0] if player_names else 'John Smith',
                'team_name': team_names[0] if team_names else 'Default Team',
                'position_affected': 'quarterback',
                'position_group_affected': 'quarterback',
                'injury_type': 'shoulder_injury',
                'severity': 'moderate',
                'injury_description': 'AC joint sprain in throwing shoulder',
                'injury_date': self.today - timedelta(days=5),
                'expected_return_date': self.today + timedelta(days=21),
                'requires_surgery': False,
                'is_contact_injury': True,
                'depth_chart_impact': 'Backup quarterback will start for 3 weeks'
            },
            {
                'player_name': player_names[1] if len(player_names) > 1 else 'Mike Johnson',
                'team_name': team_names[1] if len(team_names) > 1 else 'Default Team',
                'position_affected': 'running_back',
                'position_group_affected': 'running_back',
                'injury_type': 'knee_injury',
                'severity': 'major',
                'injury_description': 'MCL tear requiring 8-10 weeks recovery',
                'injury_date': self.today - timedelta(days=10),
                'expected_return_date': self.today + timedelta(days=60),
                'requires_surgery': False,
                'is_contact_injury': True,
                'depth_chart_impact': 'Committee approach at RB position'
            },
            {
                'player_name': player_names[2] if len(player_names) > 2 else 'Tom Wilson',
                'team_name': team_names[2] if len(team_names) > 2 else 'Default Team',
                'position_affected': 'wide_receiver',
                'position_group_affected': 'wide_receiver',
                'injury_type': 'hamstring_injury',
                'severity': 'minor',
                'injury_description': 'Grade 1 hamstring strain',
                'injury_date': self.today - timedelta(days=3),
                'expected_return_date': self.today + timedelta(days=14),
                'requires_surgery': False,
                'is_contact_injury': False,
                'depth_chart_impact': 'Limited impact, next man up approach'
            }
        ]

        for report in injury_reports:
            player_id = self.player_ids.get(report['player_name'], {}).get('id')
            team_id = self.team_ids.get(report['team_name'])

            if player_id and team_id:
                await session.execute(text("""
                    INSERT INTO football_injury_reports (
                        id, player_id, team_id, position_affected, position_group_affected,
                        injury_type, injury_description, severity, injury_date, expected_return_date,
                        current_status, depth_chart_status, requires_surgery, is_contact_injury,
                        occurred_during_game, depth_chart_impact
                    ) VALUES (
                        :id, :player_id, :team_id, :position_affected, :position_group_affected,
                        :injury_type, :injury_description, :severity, :injury_date, :expected_return_date,
                        :current_status, :depth_chart_status, :requires_surgery, :is_contact_injury,
                        :occurred_during_game, :depth_chart_impact
                    )
                """), {
                    'id': uuid4(),
                    'player_id': player_id,
                    'team_id': team_id,
                    'position_affected': report['position_affected'],
                    'position_group_affected': report['position_group_affected'],
                    'injury_type': report['injury_type'],
                    'injury_description': report['injury_description'],
                    'severity': report['severity'],
                    'injury_date': report['injury_date'],
                    'expected_return_date': report['expected_return_date'],
                    'current_status': 'injured',
                    'depth_chart_status': 'injured_reserve',
                    'requires_surgery': report['requires_surgery'],
                    'is_contact_injury': report['is_contact_injury'],
                    'occurred_during_game': True,
                    'depth_chart_impact': report['depth_chart_impact']
                })

    async def _create_football_recruiting_news(self, session: AsyncSession) -> None:
        """Create football recruiting news"""
        logger.info("Creating football recruiting news...")

        if not self.team_ids:
            logger.warning("No teams found, skipping recruiting news")
            return

        team_names = list(self.team_ids.keys())[:8]

        recruiting_news = [
            {
                'recruit_name': 'Dylan Raiola',
                'recruit_position': 'quarterback',
                'recruit_position_group': 'quarterback',
                'recruit_height': '6-3',
                'recruit_weight': 220,
                'high_school': 'Burleson High School',
                'hometown': 'Burleson',
                'home_state': 'Texas',
                'recruiting_class': 2024,
                'event_type': 'commit',
                'team_name': team_names[0] if team_names else None,
                'star_rating': 5,
                'national_ranking': 15,
                'position_ranking': 2,
                'projected_impact': 'immediate'
            },
            {
                'recruit_name': 'Caleb Downs',
                'recruit_position': 'safety',
                'recruit_position_group': 'defensive_back',
                'recruit_height': '6-0',
                'recruit_weight': 185,
                'high_school': 'Hoschton High School',
                'hometown': 'Hoschton',
                'home_state': 'Georgia',
                'recruiting_class': 2024,
                'event_type': 'transfer_commitment',
                'team_name': team_names[1] if len(team_names) > 1 else None,
                'star_rating': 5,
                'national_ranking': 8,
                'position_ranking': 1,
                'projected_impact': 'immediate',
                'is_transfer': True
            },
            {
                'recruit_name': 'Jerrick Gibson',
                'recruit_position': 'wide_receiver',
                'recruit_position_group': 'wide_receiver',
                'recruit_height': '6-1',
                'recruit_weight': 175,
                'high_school': 'St. Frances Academy',
                'hometown': 'Baltimore',
                'home_state': 'Maryland',
                'recruiting_class': 2025,
                'event_type': 'official_visit',
                'team_name': team_names[2] if len(team_names) > 2 else None,
                'star_rating': 4,
                'national_ranking': 85,
                'position_ranking': 12,
                'projected_impact': 'year 2'
            }
        ]

        for news in recruiting_news:
            team_id = self.team_ids.get(news['team_name']) if news['team_name'] else None

            if team_id:
                await session.execute(text("""
                    INSERT INTO football_recruiting_news (
                        id, recruit_name, recruit_position, recruit_position_group,
                        recruit_height, recruit_weight, high_school, hometown, home_state,
                        recruiting_class, event_type, team_id, event_date, star_rating,
                        national_ranking, position_ranking, projected_impact, is_transfer,
                        source, verified
                    ) VALUES (
                        :id, :recruit_name, :recruit_position, :recruit_position_group,
                        :recruit_height, :recruit_weight, :high_school, :hometown, :home_state,
                        :recruiting_class, :event_type, :team_id, :event_date, :star_rating,
                        :national_ranking, :position_ranking, :projected_impact, :is_transfer,
                        :source, :verified
                    )
                """), {
                    'id': uuid4(),
                    'recruit_name': news['recruit_name'],
                    'recruit_position': news['recruit_position'],
                    'recruit_position_group': news['recruit_position_group'],
                    'recruit_height': news.get('recruit_height'),
                    'recruit_weight': news.get('recruit_weight'),
                    'high_school': news.get('high_school'),
                    'hometown': news.get('hometown'),
                    'home_state': news.get('home_state'),
                    'recruiting_class': news['recruiting_class'],
                    'event_type': news['event_type'],
                    'team_id': team_id,
                    'event_date': self.today - timedelta(days=2),
                    'star_rating': news.get('star_rating'),
                    'national_ranking': news.get('national_ranking'),
                    'position_ranking': news.get('position_ranking'),
                    'projected_impact': news.get('projected_impact'),
                    'is_transfer': news.get('is_transfer', False),
                    'source': '247Sports',
                    'verified': True
                })

    async def _create_football_coaching_news(self, session: AsyncSession) -> None:
        """Create football coaching news"""
        logger.info("Creating football coaching news...")

        if not self.team_ids:
            logger.warning("No teams found, skipping coaching news")
            return

        team_names = list(self.team_ids.keys())[:5]

        coaching_news = [
            {
                'coach_name': 'Ryan Day',
                'position_title': 'Head Coach',
                'coaching_position': 'head_coach',
                'coaching_level': 'head_coach',
                'team_name': team_names[0] if team_names else None,
                'change_type': 'contract_extension',
                'effective_date': self.today + timedelta(days=30),
                'contract_years': 6,
                'salary_amount': Decimal('9500000'),
                'reason': 'Strong program performance and playoff appearances'
            },
            {
                'coach_name': 'Todd Monken',
                'position_title': 'Offensive Coordinator',
                'coaching_position': 'offensive_coordinator',
                'coaching_level': 'coordinator',
                'team_name': team_names[1] if len(team_names) > 1 else None,
                'change_type': 'hire',
                'effective_date': self.today - timedelta(days=60),
                'previous_position': 'Offensive Coordinator at Georgia',
                'contract_years': 3,
                'salary_amount': Decimal('1800000'),
                'reason': 'Brings innovative offensive schemes'
            },
            {
                'coach_name': 'Alex Grinch',
                'position_title': 'Defensive Coordinator',
                'coaching_position': 'defensive_coordinator',
                'coaching_level': 'coordinator',
                'team_name': team_names[2] if len(team_names) > 2 else None,
                'change_type': 'fire',
                'effective_date': self.today - timedelta(days=10),
                'tenure_years': 2,
                'reason': 'Poor defensive performance this season'
            }
        ]

        for news in coaching_news:
            team_id = self.team_ids.get(news['team_name']) if news['team_name'] else None

            if team_id:
                await session.execute(text("""
                    INSERT INTO football_coaching_news (
                        id, coach_name, position_title, coaching_position, coaching_level,
                        team_id, change_type, effective_date, contract_years, salary_amount,
                        previous_position, tenure_years, reason, source, verified
                    ) VALUES (
                        :id, :coach_name, :position_title, :coaching_position, :coaching_level,
                        :team_id, :change_type, :effective_date, :contract_years, :salary_amount,
                        :previous_position, :tenure_years, :reason, :source, :verified
                    )
                """), {
                    'id': uuid4(),
                    'coach_name': news['coach_name'],
                    'position_title': news['position_title'],
                    'coaching_position': news['coaching_position'],
                    'coaching_level': news['coaching_level'],
                    'team_id': team_id,
                    'change_type': news['change_type'],
                    'effective_date': news['effective_date'],
                    'contract_years': news.get('contract_years'),
                    'salary_amount': news.get('salary_amount'),
                    'previous_position': news.get('previous_position'),
                    'tenure_years': news.get('tenure_years'),
                    'reason': news.get('reason'),
                    'source': 'The Athletic',
                    'verified': True
                })

    async def _create_football_depth_chart_updates(self, session: AsyncSession) -> None:
        """Create football depth chart updates"""
        logger.info("Creating football depth chart updates...")

        if not self.player_ids or not self.team_ids:
            logger.warning("No players or teams found, skipping depth chart updates")
            return

        player_names = list(self.player_ids.keys())[:8]
        team_names = list(self.team_ids.keys())[:4]

        depth_chart_updates = [
            {
                'player_name': player_names[0] if player_names else 'John Doe',
                'team_name': team_names[0] if team_names else 'Default Team',
                'position': 'quarterback',
                'position_group': 'quarterback',
                'depth_chart_status': 'starter',
                'previous_status': 'backup',
                'depth_order': 1,
                'previous_depth_order': 2,
                'update_type': 'promotion',
                'reason': 'Outstanding fall camp performance',
                'is_position_battle': True
            },
            {
                'player_name': player_names[1] if len(player_names) > 1 else 'Mike Smith',
                'team_name': team_names[1] if len(team_names) > 1 else 'Default Team',
                'position': 'running_back',
                'position_group': 'running_back',
                'depth_chart_status': 'backup',
                'previous_status': 'third_string',
                'depth_order': 2,
                'previous_depth_order': 3,
                'update_type': 'promotion',
                'reason': 'Injury to starter moved him up depth chart',
                'is_injury_related': True
            }
        ]

        for update in depth_chart_updates:
            player_id = self.player_ids.get(update['player_name'], {}).get('id')
            team_id = self.team_ids.get(update['team_name'])

            if player_id and team_id:
                await session.execute(text("""
                    INSERT INTO football_depth_chart_updates (
                        id, team_id, player_id, position, position_group,
                        depth_chart_status, previous_status, depth_order, previous_depth_order,
                        update_type, reason, is_position_battle, is_injury_related
                    ) VALUES (
                        :id, :team_id, :player_id, :position, :position_group,
                        :depth_chart_status, :previous_status, :depth_order, :previous_depth_order,
                        :update_type, :reason, :is_position_battle, :is_injury_related
                    )
                """), {
                    'id': uuid4(),
                    'team_id': team_id,
                    'player_id': player_id,
                    'position': update['position'],
                    'position_group': update['position_group'],
                    'depth_chart_status': update['depth_chart_status'],
                    'previous_status': update.get('previous_status'),
                    'depth_order': update.get('depth_order'),
                    'previous_depth_order': update.get('previous_depth_order'),
                    'update_type': update['update_type'],
                    'reason': update.get('reason'),
                    'is_position_battle': update.get('is_position_battle', False),
                    'is_injury_related': update.get('is_injury_related', False)
                })

    async def _create_football_game_previews(self, session: AsyncSession) -> None:
        """Create football game previews"""
        logger.info("Creating football game previews...")

        if not self.game_ids or not self.content_ids:
            logger.warning("No games or content found, skipping game previews")
            return

        game_list = list(self.game_ids.values())[:3]
        content_list = list(self.content_ids.values())[:3]

        for i, game in enumerate(game_list):
            if i < len(content_list):
                await session.execute(text("""
                    INSERT INTO football_game_previews (
                        id, game_id, home_team_id, away_team_id, game_date,
                        venue, point_spread, over_under, content_id,
                        key_matchups, major_storylines, players_to_watch
                    ) VALUES (
                        :id, :game_id, :home_team_id, :away_team_id, :game_date,
                        :venue, :point_spread, :over_under, :content_id,
                        :key_matchups, :major_storylines, :players_to_watch
                    )
                """), {
                    'id': uuid4(),
                    'game_id': game['id'],
                    'home_team_id': game['home_team_id'],
                    'away_team_id': game['away_team_id'],
                    'game_date': game['game_date'],
                    'venue': 'Memorial Stadium',
                    'point_spread': Decimal('-7.5'),
                    'over_under': Decimal('52.5'),
                    'content_id': content_list[i],
                    'key_matchups': ['O-Line vs D-Line', 'QB vs Secondary'],
                    'major_storylines': ['Rivalry renewed', 'Playoff implications'],
                    'players_to_watch': ['Star QB', 'Elite WR', 'Shutdown CB']
                })

    async def _create_football_bowl_news(self, session: AsyncSession) -> None:
        """Create football bowl news"""
        logger.info("Creating football bowl news...")

        if not self.team_ids or not self.bowl_game_ids:
            logger.warning("No teams or bowl games found, skipping bowl news")
            return

        team_names = list(self.team_ids.keys())[:4]
        bowl_names = list(self.bowl_game_ids.keys())[:2]

        bowl_news = [
            {
                'team_name': team_names[0] if team_names else None,
                'bowl_name': bowl_names[0] if bowl_names else None,
                'news_type': 'bowl_selection',
                'bowl_tier': 'major',
                'final_record': '10-2',
                'conference_record': '7-1',
                'selection_reason': 'Strong season performance and quality wins'
            },
            {
                'team_name': team_names[1] if len(team_names) > 1 else None,
                'news_type': 'playoff_selection',
                'playoff_seed': 3,
                'ranking_at_selection': 3,
                'final_record': '12-1',
                'conference_record': '8-1'
            }
        ]

        for news in bowl_news:
            team_id = self.team_ids.get(news['team_name']) if news['team_name'] else None
            bowl_id = self.bowl_game_ids.get(news['bowl_name']) if news.get('bowl_name') else None

            if team_id:
                await session.execute(text("""
                    INSERT INTO football_bowl_news (
                        id, team_id, bowl_game_id, news_type, bowl_tier,
                        final_record, conference_record, playoff_seed, ranking_at_selection,
                        selection_reason, source, verified
                    ) VALUES (
                        :id, :team_id, :bowl_game_id, :news_type, :bowl_tier,
                        :final_record, :conference_record, :playoff_seed, :ranking_at_selection,
                        :selection_reason, :source, :verified
                    )
                """), {
                    'id': uuid4(),
                    'team_id': team_id,
                    'bowl_game_id': bowl_id,
                    'news_type': news['news_type'],
                    'bowl_tier': news.get('bowl_tier'),
                    'final_record': news.get('final_record'),
                    'conference_record': news.get('conference_record'),
                    'playoff_seed': news.get('playoff_seed'),
                    'ranking_at_selection': news.get('ranking_at_selection'),
                    'selection_reason': news.get('selection_reason'),
                    'source': 'ESPN',
                    'verified': True
                })


async def run_seed_data():
    """Run the College Football Phase 5 content seed data"""
    seed_data = CollegeFootballPhase5ContentSeedData()

    async for session in get_async_session():
        try:
            await seed_data.upgrade(session)
            logger.info("College Football Phase 5 content seed data completed successfully")
            break
        except Exception as e:
            logger.error(f"Seed data failed: {str(e)}")
            raise


async def run_seed_rollback():
    """Rollback the College Football Phase 5 content seed data"""
    seed_data = CollegeFootballPhase5ContentSeedData()

    async for session in get_async_session():
        try:
            await seed_data.downgrade(session)
            logger.info("College Football Phase 5 content seed data rollback completed successfully")
            break
        except Exception as e:
            logger.error(f"Seed data rollback failed: {str(e)}")
            raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(run_seed_rollback())
    else:
        asyncio.run(run_seed_data())