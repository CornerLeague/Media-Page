"""
Sports service layer for multi-league team operations
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from backend.models.sports import Sport, League, Team, TeamLeagueMembership
from backend.api.schemas.sports import (
    LeagueInfo,
    MultiLeagueTeamResponse,
    TeamLeagueMembershipResponse,
    SoccerTeamFilters
)


class SportsService:
    """Service for sports, leagues, and teams operations with multi-league support"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_soccer_sport_id(self) -> Optional[UUID]:
        """Get the UUID for soccer/football sport"""
        result = await self.db.execute(
            select(Sport.id).where(Sport.slug == "soccer")
        )
        sport = result.scalar_one_or_none()
        return sport

    async def get_teams_with_multi_league_info(
        self,
        filters: SoccerTeamFilters,
        sport_id: Optional[UUID] = None
    ) -> Tuple[List[MultiLeagueTeamResponse], int]:
        """
        Get teams with comprehensive multi-league information

        Returns:
            Tuple of (teams_list, total_count)
        """
        if not sport_id:
            sport_id = await self.get_soccer_sport_id()
            if not sport_id:
                return [], 0

        # Build base query with joins
        query = (
            select(Team)
            .options(
                selectinload(Team.sport),
                selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            )
            .where(Team.sport_id == sport_id)
        )

        # Apply filters
        conditions = []

        if filters.league_ids:
            # Teams that have memberships in any of the specified leagues
            subquery = select(TeamLeagueMembership.team_id).where(
                and_(
                    TeamLeagueMembership.league_id.in_(filters.league_ids),
                    TeamLeagueMembership.is_active == True
                )
            )
            conditions.append(Team.id.in_(subquery))

        if filters.country_codes:
            conditions.append(Team.country_code.in_(filters.country_codes))

        if filters.founding_year_min:
            conditions.append(Team.founding_year >= filters.founding_year_min)

        if filters.founding_year_max:
            conditions.append(Team.founding_year <= filters.founding_year_max)

        if filters.query:
            search_pattern = f"%{filters.query}%"
            conditions.append(
                or_(
                    Team.name.ilike(search_pattern),
                    Team.official_name.ilike(search_pattern),
                    Team.short_name.ilike(search_pattern),
                    Team.market.ilike(search_pattern)
                )
            )

        if filters.multi_league_only:
            # Teams with more than one active league membership
            multi_league_subquery = (
                select(TeamLeagueMembership.team_id)
                .where(TeamLeagueMembership.is_active == True)
                .group_by(TeamLeagueMembership.team_id)
                .having(func.count(TeamLeagueMembership.league_id) > 1)
            )
            conditions.append(Team.id.in_(multi_league_subquery))

        if filters.competition_types or filters.league_levels:
            # Filter by league characteristics
            league_conditions = []
            if filters.competition_types:
                league_conditions.append(League.competition_type.in_(filters.competition_types))
            if filters.league_levels:
                league_conditions.append(League.league_level.in_(filters.league_levels))

            if league_conditions:
                league_filter_subquery = (
                    select(TeamLeagueMembership.team_id)
                    .join(League)
                    .where(
                        and_(
                            TeamLeagueMembership.is_active == True,
                            *league_conditions
                        )
                    )
                )
                conditions.append(Team.id.in_(league_filter_subquery))

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.db.execute(count_query)
        total_count = total_count_result.scalar()

        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Execute query
        result = await self.db.execute(query)
        teams = result.scalars().all()

        # Convert to response format
        team_responses = []
        for team in teams:
            leagues_info = await self._get_team_leagues_info(team)

            # Determine primary league using new logic (no longer dependent on legacy league_id)
            primary_league_info = self._determine_primary_league(leagues_info)

            if primary_league_info is None:
                continue  # Skip teams without league information

            team_response = MultiLeagueTeamResponse(
                id=team.id,
                name=team.name,
                market=team.market,
                slug=team.slug,
                display_name=team.display_name,
                official_name=team.official_name,
                short_name=team.short_name,
                computed_short_name=team.computed_short_name,
                country_code=team.country_code,
                founding_year=team.founding_year,
                logo_url=team.logo_url,
                primary_color=team.primary_color,
                secondary_color=team.secondary_color,
                sport_name=team.sport.name if team.sport else "Soccer",
                primary_league=primary_league_info,
                all_leagues=leagues_info,
                is_multi_league=len(leagues_info) > 1
            )
            team_responses.append(team_response)

        return team_responses, total_count

    async def _get_team_leagues_info(self, team: Team) -> List[LeagueInfo]:
        """Get all league information for a team"""
        leagues_info = []

        for membership in team.league_memberships:
            if membership.is_active and membership.league:
                league_info = LeagueInfo(
                    id=membership.league.id,
                    name=membership.league.name,
                    slug=membership.league.slug,
                    country_code=membership.league.country_code,
                    league_level=membership.league.league_level,
                    competition_type=membership.league.competition_type,
                    is_primary=False,  # Will be set by _determine_primary_league
                    season_start_year=membership.season_start_year,
                    position_last_season=membership.position_last_season
                )
                leagues_info.append(league_info)

        return leagues_info

    def _determine_primary_league(self, leagues_info: List[LeagueInfo]) -> Optional[LeagueInfo]:
        """
        Determine the primary league for a team using intelligent heuristics

        Priority order:
        1. Domestic leagues (league_level 1, competition_type 'league')
        2. Earliest membership (longest history)
        3. Highest league level (lower number = higher tier)
        4. First alphabetically (fallback)
        """
        if not leagues_info:
            return None

        if len(leagues_info) == 1:
            # Mark the only league as primary
            leagues_info[0].is_primary = True
            return leagues_info[0]

        # Sort by priority criteria
        def league_priority(league: LeagueInfo) -> tuple:
            # Priority: (is_domestic, earliest_season, league_level, name)
            is_domestic = (league.competition_type == 'league' and league.league_level == 1)
            return (
                not is_domestic,  # False (domestic) sorts before True (non-domestic)
                league.season_start_year,  # Earlier seasons first
                league.league_level,  # Lower level number = higher tier
                league.name  # Alphabetical fallback
            )

        sorted_leagues = sorted(leagues_info, key=league_priority)
        primary = sorted_leagues[0]

        # Mark the primary league
        for league in leagues_info:
            league.is_primary = (league.id == primary.id)

        return primary

    async def get_team_leagues(self, team_id: UUID) -> List[LeagueInfo]:
        """Get all leagues for a specific team"""
        result = await self.db.execute(
            select(Team)
            .options(
                selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            )
            .where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            return []

        return await self._get_team_leagues_info(team)

    async def get_league_teams(
        self,
        league_id: UUID,
        include_inactive: bool = False
    ) -> List[MultiLeagueTeamResponse]:
        """Get all teams for a specific league"""
        # Build query for teams in this league
        membership_query = (
            select(TeamLeagueMembership)
            .options(
                selectinload(TeamLeagueMembership.team).selectinload(Team.sport),
                selectinload(TeamLeagueMembership.league)
            )
            .where(TeamLeagueMembership.league_id == league_id)
        )

        if not include_inactive:
            membership_query = membership_query.where(TeamLeagueMembership.is_active == True)

        result = await self.db.execute(membership_query)
        memberships = result.scalars().all()

        # Convert to team responses
        team_responses = []
        for membership in memberships:
            team = membership.team
            if not team:
                continue

            # Get all leagues for this team
            leagues_info = await self._get_team_leagues_info(team)

            # Determine primary league using new logic
            primary_league_info = self._determine_primary_league(leagues_info)

            if primary_league_info is None:
                continue

            team_response = MultiLeagueTeamResponse(
                id=team.id,
                name=team.name,
                market=team.market,
                slug=team.slug,
                display_name=team.display_name,
                official_name=team.official_name,
                short_name=team.short_name,
                computed_short_name=team.computed_short_name,
                country_code=team.country_code,
                founding_year=team.founding_year,
                logo_url=team.logo_url,
                primary_color=team.primary_color,
                secondary_color=team.secondary_color,
                sport_name=team.sport.name if team.sport else "Soccer",
                primary_league=primary_league_info,
                all_leagues=leagues_info,
                is_multi_league=len(leagues_info) > 1
            )
            team_responses.append(team_response)

        return team_responses

    async def get_multi_league_teams(self, sport_id: Optional[UUID] = None) -> List[MultiLeagueTeamResponse]:
        """Get teams that participate in multiple leagues"""
        if not sport_id:
            sport_id = await self.get_soccer_sport_id()
            if not sport_id:
                return []

        # Find teams with multiple active league memberships
        multi_league_query = text("""
            SELECT team_id
            FROM team_league_memberships tlm
            JOIN teams t ON tlm.team_id = t.id
            WHERE t.sport_id = :sport_id
            AND tlm.is_active = 1
            GROUP BY team_id
            HAVING COUNT(league_id) > 1
        """)

        result = await self.db.execute(multi_league_query, {"sport_id": str(sport_id)})
        multi_league_team_ids = [row[0] for row in result.fetchall()]

        if not multi_league_team_ids:
            return []

        # Get full team information
        teams_query = (
            select(Team)
            .options(
                selectinload(Team.sport),
                selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            )
            .where(Team.id.in_(multi_league_team_ids))
        )

        result = await self.db.execute(teams_query)
        teams = result.scalars().all()

        # Convert to response format
        team_responses = []
        for team in teams:
            leagues_info = await self._get_team_leagues_info(team)

            # Determine primary league using new logic
            primary_league_info = self._determine_primary_league(leagues_info)

            if primary_league_info is None:
                continue

            team_response = MultiLeagueTeamResponse(
                id=team.id,
                name=team.name,
                market=team.market,
                slug=team.slug,
                display_name=team.display_name,
                official_name=team.official_name,
                short_name=team.short_name,
                computed_short_name=team.computed_short_name,
                country_code=team.country_code,
                founding_year=team.founding_year,
                logo_url=team.logo_url,
                primary_color=team.primary_color,
                secondary_color=team.secondary_color,
                sport_name=team.sport.name if team.sport else "Soccer",
                primary_league=primary_league_info,
                all_leagues=leagues_info,
                is_multi_league=True  # By definition, these are multi-league teams
            )
            team_responses.append(team_response)

        return team_responses

    async def get_soccer_leagues_with_team_counts(self) -> List[Dict[str, Any]]:
        """Get all soccer leagues with team counts"""
        sport_id = await self.get_soccer_sport_id()
        if not sport_id:
            return []

        query = text("""
            SELECT
                l.id,
                l.name,
                l.slug,
                l.country_code,
                l.league_level,
                l.competition_type,
                l.abbreviation,
                COUNT(DISTINCT tlm.team_id) as team_count,
                COUNT(DISTINCT CASE WHEN tlm.season_end_year IS NULL THEN tlm.team_id END) as current_teams
            FROM leagues l
            LEFT JOIN team_league_memberships tlm ON l.id = tlm.league_id AND tlm.is_active = 1
            WHERE l.sport_id = :sport_id AND l.is_active = 1
            GROUP BY l.id, l.name, l.slug, l.country_code, l.league_level, l.competition_type, l.abbreviation
            ORDER BY l.league_level, l.name
        """)

        result = await self.db.execute(query, {"sport_id": str(sport_id)})

        leagues = []
        for row in result.fetchall():
            league_data = {
                "id": row[0],
                "name": row[1],
                "slug": row[2],
                "country_code": row[3],
                "league_level": row[4],
                "competition_type": row[5],
                "abbreviation": row[6],
                "team_count": row[7],
                "current_teams": row[8]
            }
            leagues.append(league_data)

        return leagues