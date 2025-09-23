"""
Team selection service for handling sports, leagues, teams, and user preferences
"""

import logging
import time
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, delete
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status

from backend.models.sports import Sport, League, Team, TeamLeagueMembership
from backend.models.users import User, UserTeamPreference
from backend.api.schemas.sports import (
    SportResponse,
    SportWithLeagues,
    LeagueResponse,
    LeagueWithTeams,
    TeamResponse,
    TeamSearchParams,
    UserTeamPreferenceCreate,
    UserTeamPreferenceResponse,
    UserTeamPreferencesUpdate,
    UserTeamPreferencesResponse,
    SportsPaginatedResponse,
    LeaguesPaginatedResponse,
    TeamsPaginatedResponse,
    LeagueInfo,
    EnhancedTeamResponse,
    EnhancedTeamsPaginatedResponse,
    SearchMetadata,
    SearchMatchInfo,
    TeamSearchSuggestion,
    SearchSuggestionsResponse
)
from backend.api.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)


class TeamSelectionService:
    """Service for team selection-related operations"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def _get_team_leagues_info(self, team: Team) -> List[LeagueInfo]:
        """Get all league information for a team (internal helper method)"""
        leagues_info = []

        # If the team has league_memberships loaded, use them
        if hasattr(team, 'league_memberships') and team.league_memberships:
            for index, membership in enumerate(team.league_memberships):
                if membership.is_active and membership.league:
                    league_info = LeagueInfo(
                        id=membership.league.id,
                        name=membership.league.name,
                        slug=membership.league.slug,
                        country_code=getattr(membership.league, 'country_code', None),
                        league_level=getattr(membership.league, 'league_level', None),
                        competition_type=getattr(membership.league, 'competition_type', None),
                        is_primary=(index == 0),  # First active membership is primary
                        season_start_year=membership.season_start_year,
                        position_last_season=membership.position_last_season
                    )
                    leagues_info.append(league_info)
        else:
            # Fallback: query league memberships separately
            try:
                memberships_query = (
                    select(TeamLeagueMembership)
                    .options(selectinload(TeamLeagueMembership.league))
                    .where(
                        and_(
                            TeamLeagueMembership.team_id == team.id,
                            TeamLeagueMembership.is_active == True
                        )
                    )
                )
                result = await self.db.execute(memberships_query)
                memberships = result.scalars().all()

                for index, membership in enumerate(memberships):
                    if membership.league:
                        league_info = LeagueInfo(
                            id=membership.league.id,
                            name=membership.league.name,
                            slug=membership.league.slug,
                            country_code=getattr(membership.league, 'country_code', None),
                            league_level=getattr(membership.league, 'league_level', None),
                            competition_type=getattr(membership.league, 'competition_type', None),
                            is_primary=(index == 0),  # First active membership is primary
                            season_start_year=membership.season_start_year,
                            position_last_season=membership.position_last_season
                        )
                        leagues_info.append(league_info)
            except Exception as e:
                logger.warning(f"Failed to fetch league memberships for team {team.id}: {str(e)}")

        return leagues_info

    def _highlight_search_term(self, text: str, search_term: str) -> str:
        """Highlight search term in text with HTML tags"""
        if not text or not search_term:
            return text

        # Case-insensitive highlighting
        import re
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        return pattern.sub(f'<mark>\\g<0></mark>', text)

    def _get_search_matches(self, team: Team, search_query: Optional[str]) -> List[SearchMatchInfo]:
        """Get information about which fields matched the search query"""
        matches = []
        if not search_query:
            return matches

        search_term = search_query.lower()

        # Check team name
        if team.name and search_term in team.name.lower():
            matches.append(SearchMatchInfo(
                field="name",
                value=team.name,
                highlighted=self._highlight_search_term(team.name, search_query)
            ))

        # Check market/city
        if team.market and search_term in team.market.lower():
            matches.append(SearchMatchInfo(
                field="market",
                value=team.market,
                highlighted=self._highlight_search_term(team.market, search_query)
            ))

        # Check abbreviation
        if team.abbreviation and search_term in team.abbreviation.lower():
            matches.append(SearchMatchInfo(
                field="abbreviation",
                value=team.abbreviation,
                highlighted=self._highlight_search_term(team.abbreviation, search_query)
            ))

        # Check display name
        display_name = team.display_name
        if display_name and search_term in display_name.lower():
            matches.append(SearchMatchInfo(
                field="display_name",
                value=display_name,
                highlighted=self._highlight_search_term(display_name, search_query)
            ))

        return matches

    def _calculate_relevance_score(self, team: Team, search_query: Optional[str]) -> float:
        """Calculate relevance score for search results"""
        if not search_query:
            return 1.0

        search_term = search_query.lower()
        score = 0.0

        # Exact name match gets highest score
        if team.name and team.name.lower() == search_term:
            score += 10.0
        elif team.name and team.name.lower().startswith(search_term):
            score += 8.0
        elif team.name and search_term in team.name.lower():
            score += 5.0

        # Market match
        if team.market and team.market.lower() == search_term:
            score += 8.0
        elif team.market and team.market.lower().startswith(search_term):
            score += 6.0
        elif team.market and search_term in team.market.lower():
            score += 3.0

        # Abbreviation match
        if team.abbreviation and team.abbreviation.lower() == search_term:
            score += 9.0
        elif team.abbreviation and search_term in team.abbreviation.lower():
            score += 7.0

        # Display name match
        display_name = team.display_name
        if display_name and display_name.lower() == search_term:
            score += 9.5
        elif display_name and display_name.lower().startswith(search_term):
            score += 7.0
        elif display_name and search_term in display_name.lower():
            score += 4.0

        return score

    def _get_primary_league_name(self, team: Team) -> Optional[str]:
        """Get primary league name for a team"""
        if not team or not hasattr(team, 'league_memberships') or not team.league_memberships:
            return None

        # Find first active membership
        for membership in team.league_memberships:
            if membership.is_active and membership.league:
                return membership.league.name

        return None

    def _create_team_response(self, team: Team, leagues_info: Optional[List[LeagueInfo]] = None) -> TeamResponse:
        """Create a TeamResponse with enhanced multi-league support"""
        if leagues_info is None:
            leagues_info = []

        # Determine primary league from leagues_info
        primary_league = None
        primary_league_id = None
        league_name = None

        if leagues_info:
            # Find primary league (first one marked as primary, or first active one)
            primary_league = next((league for league in leagues_info if league.is_primary), leagues_info[0])
            primary_league_id = primary_league.id if primary_league else None
            league_name = primary_league.name if primary_league else None

        return TeamResponse(
            id=team.id,
            sport_id=team.sport_id,
            league_id=primary_league_id,  # Use primary league from memberships
            name=team.name,
            market=team.market,
            slug=team.slug,
            abbreviation=team.abbreviation,
            logo_url=team.logo_url,
            primary_color=team.primary_color,
            secondary_color=team.secondary_color,
            is_active=team.is_active,
            external_id=team.external_id,
            # Enhanced metadata from Phase 2
            official_name=getattr(team, 'official_name', None),
            short_name=getattr(team, 'short_name', None),
            country_code=getattr(team, 'country_code', None),
            founding_year=getattr(team, 'founding_year', None),
            # Computed fields
            sport_name=team.sport.name if team.sport else None,
            league_name=league_name,  # Use primary league name
            display_name=team.display_name,
            computed_short_name=getattr(team, 'computed_short_name', team.name),
            computed_official_name=getattr(team, 'computed_official_name', team.display_name),
            leagues=leagues_info
        )

    async def get_sports(
        self,
        include_leagues: bool = False,
        include_inactive: bool = False
    ) -> List[SportResponse | SportWithLeagues]:
        """
        Get all sports with optional league inclusion

        Args:
            include_leagues: Whether to include leagues for each sport
            include_inactive: Whether to include inactive sports

        Returns:
            List of sports with optional league data

        Raises:
            HTTPException: If database operation fails
        """
        try:
            # Build query
            query = select(Sport)

            if include_leagues:
                query = query.options(selectinload(Sport.leagues))

            if not include_inactive:
                query = query.where(Sport.is_active == True)

            query = query.order_by(Sport.display_order, Sport.name)

            # Execute query
            result = await self.db.execute(query)
            sports = result.scalars().all()

            # Convert to response schemas
            if include_leagues:
                return [
                    SportWithLeagues(
                        id=sport.id,
                        name=sport.name,
                        slug=sport.slug,
                        has_teams=sport.has_teams,
                        icon=sport.icon,
                        is_active=sport.is_active,
                        display_order=sport.display_order,
                        leagues_count=len(sport.leagues),
                        leagues=[
                            LeagueResponse(
                                id=league.id,
                                sport_id=league.sport_id,
                                name=league.name,
                                slug=league.slug,
                                abbreviation=league.abbreviation,
                                is_active=league.is_active,
                                season_start_month=league.season_start_month,
                                season_end_month=league.season_end_month,
                                # Enhanced metadata from Phase 2
                                country_code=getattr(league, 'country_code', None),
                                league_level=getattr(league, 'league_level', 1),
                                competition_type=getattr(league, 'competition_type', 'league'),
                                sport_name=sport.name,
                                teams_count=None  # Would need additional query
                            )
                            for league in sport.leagues
                            if include_inactive or league.is_active
                        ]
                    )
                    for sport in sports
                ]
            else:
                return [
                    SportResponse(
                        id=sport.id,
                        name=sport.name,
                        slug=sport.slug,
                        has_teams=sport.has_teams,
                        icon=sport.icon,
                        is_active=sport.is_active,
                        display_order=sport.display_order,
                        leagues_count=None  # Would need additional query
                    )
                    for sport in sports
                ]

        except Exception as e:
            logger.error(f"Error getting sports: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve sports"
            )

    async def get_sport_leagues(
        self,
        sport_id: UUID,
        include_teams: bool = False,
        include_inactive: bool = False
    ) -> List[LeagueResponse | LeagueWithTeams]:
        """
        Get leagues for a specific sport

        Args:
            sport_id: Sport UUID
            include_teams: Whether to include teams for each league
            include_inactive: Whether to include inactive leagues

        Returns:
            List of leagues with optional team data

        Raises:
            HTTPException: If sport not found or database operation fails
        """
        try:
            # Verify sport exists
            sport_result = await self.db.execute(
                select(Sport).where(Sport.id == sport_id)
            )
            sport = sport_result.scalar_one_or_none()

            if not sport:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sport with ID {sport_id} not found"
                )

            # Build query
            query = select(League).where(League.sport_id == sport_id)

            if include_teams:
                query = query.options(selectinload(League.teams))

            if not include_inactive:
                query = query.where(League.is_active == True)

            query = query.order_by(League.name)

            # Execute query
            result = await self.db.execute(query)
            leagues = result.scalars().all()

            # Convert to response schemas
            if include_teams:
                return [
                    LeagueWithTeams(
                        id=league.id,
                        sport_id=league.sport_id,
                        name=league.name,
                        slug=league.slug,
                        abbreviation=league.abbreviation,
                        is_active=league.is_active,
                        season_start_month=league.season_start_month,
                        season_end_month=league.season_end_month,
                        sport_name=sport.name,
                        teams_count=len(league.teams),
                        teams=[
                            TeamResponse(
                                id=team.id,
                                sport_id=team.sport_id,
                                league_id=team.league_id,
                                name=team.name,
                                market=team.market,
                                slug=team.slug,
                                abbreviation=team.abbreviation,
                                logo_url=team.logo_url,
                                primary_color=team.primary_color,
                                secondary_color=team.secondary_color,
                                is_active=team.is_active,
                                external_id=team.external_id,
                                sport_name=sport.name,
                                league_name=league.name,
                                display_name=team.display_name,
                                short_name=team.short_name
                            )
                            for team in league.teams
                            if include_inactive or team.is_active
                        ]
                    )
                    for league in leagues
                ]
            else:
                return [
                    LeagueResponse(
                        id=league.id,
                        sport_id=league.sport_id,
                        name=league.name,
                        slug=league.slug,
                        abbreviation=league.abbreviation,
                        is_active=league.is_active,
                        season_start_month=league.season_start_month,
                        season_end_month=league.season_end_month,
                        # Enhanced metadata from Phase 2
                        country_code=getattr(league, 'country_code', None),
                        league_level=getattr(league, 'league_level', 1),
                        competition_type=getattr(league, 'competition_type', 'league'),
                        sport_name=sport.name,
                        teams_count=None  # Would need additional query
                    )
                    for league in leagues
                ]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting leagues for sport {sport_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve leagues"
            )

    async def get_league_teams(
        self,
        league_id: UUID,
        page: int = 1,
        page_size: int = 20,
        include_inactive: bool = False
    ) -> TeamsPaginatedResponse:
        """
        Get teams for a specific league with pagination

        Args:
            league_id: League UUID
            page: Page number (1-indexed)
            page_size: Number of items per page
            include_inactive: Whether to include inactive teams

        Returns:
            Paginated list of teams

        Raises:
            HTTPException: If league not found or database operation fails
        """
        try:
            # Verify league exists and get related data
            league_result = await self.db.execute(
                select(League)
                .options(selectinload(League.sport))
                .where(League.id == league_id)
            )
            league = league_result.scalar_one_or_none()

            if not league:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League with ID {league_id} not found"
                )

            # Build base query with league memberships
            base_query = select(Team).options(
                selectinload(Team.sport),
                selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            ).join(TeamLeagueMembership).where(
                TeamLeagueMembership.league_id == league_id,
                TeamLeagueMembership.is_active == True
            )

            if not include_inactive:
                base_query = base_query.where(Team.is_active == True)

            # Get total count
            count_query = select(func.count()).select_from(base_query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Get paginated results
            offset = (page - 1) * page_size
            query = base_query.order_by(Team.market, Team.name).offset(offset).limit(page_size)

            result = await self.db.execute(query)
            teams = result.scalars().all()

            # Convert to response schemas with multi-league support
            team_responses = []
            for team in teams:
                leagues_info = await self._get_team_leagues_info(team)
                team_response = self._create_team_response(team, leagues_info)
                team_responses.append(team_response)

            return PaginatedResponse.create(
                items=team_responses,
                total=total,
                page=page,
                page_size=page_size
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting teams for league {league_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve teams"
            )

    async def search_teams(self, search_params: TeamSearchParams) -> TeamsPaginatedResponse:
        """
        Search teams with various filters and pagination

        Args:
            search_params: Search parameters and filters

        Returns:
            Paginated list of matching teams

        Raises:
            HTTPException: If database operation fails
        """
        try:
            # Build base query with joins for sport and league memberships
            query = select(Team).options(
                selectinload(Team.sport),
                selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            )

            # Apply filters
            if search_params.query:
                search_term = f"%{search_params.query.lower()}%"
                query = query.where(
                    or_(
                        func.lower(Team.name).like(search_term),
                        func.lower(Team.market).like(search_term),
                        func.lower(func.concat(Team.market, ' ', Team.name)).like(search_term)
                    )
                )

            if search_params.sport_id:
                query = query.where(Team.sport_id == search_params.sport_id)

            if search_params.league_id:
                # Join with league memberships to filter by league
                query = query.join(TeamLeagueMembership).where(
                    TeamLeagueMembership.league_id == search_params.league_id,
                    TeamLeagueMembership.is_active == True
                )

            if search_params.market:
                query = query.where(func.lower(Team.market).like(f"%{search_params.market.lower()}%"))

            if search_params.is_active is not None:
                query = query.where(Team.is_active == search_params.is_active)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply pagination and ordering
            offset = (search_params.page - 1) * search_params.page_size
            query = query.order_by(Team.market, Team.name).offset(offset).limit(search_params.page_size)

            # Execute query
            result = await self.db.execute(query)
            teams = result.scalars().all()

            # Convert to response schemas with multi-league support
            team_responses = []
            for team in teams:
                leagues_info = await self._get_team_leagues_info(team)
                team_response = self._create_team_response(team, leagues_info)
                team_responses.append(team_response)

            return PaginatedResponse.create(
                items=team_responses,
                total=total,
                page=search_params.page,
                page_size=search_params.page_size
            )

        except Exception as e:
            logger.error(f"Error searching teams: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search teams"
            )

    async def search_teams_enhanced(self, search_params: TeamSearchParams) -> EnhancedTeamsPaginatedResponse:
        """
        Enhanced search teams with metadata, highlighting, and performance tracking

        Args:
            search_params: Search parameters and filters

        Returns:
            Enhanced paginated list of matching teams with search metadata

        Raises:
            HTTPException: If database operation fails
        """
        start_time = time.time()

        try:
            # Build base query with comprehensive joins
            query = select(Team).options(
                selectinload(Team.sport),
                selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            )

            filters_applied = {}

            # Apply filters
            if search_params.query:
                search_term = f"%{search_params.query.lower()}%"
                query = query.where(
                    or_(
                        func.lower(Team.name).like(search_term),
                        func.lower(Team.market).like(search_term),
                        func.lower(Team.abbreviation).like(search_term),
                        func.lower(func.concat(Team.market, ' ', Team.name)).like(search_term)
                    )
                )
                filters_applied["query"] = search_params.query

            if search_params.sport_id:
                query = query.where(Team.sport_id == search_params.sport_id)
                filters_applied["sport_id"] = str(search_params.sport_id)

            if search_params.league_id:
                # Join with league memberships to filter by league
                query = query.join(TeamLeagueMembership).where(
                    TeamLeagueMembership.league_id == search_params.league_id,
                    TeamLeagueMembership.is_active == True
                )
                filters_applied["league_id"] = str(search_params.league_id)

            if search_params.market:
                query = query.where(func.lower(Team.market).like(f"%{search_params.market.lower()}%"))
                filters_applied["market"] = search_params.market

            if search_params.is_active is not None:
                query = query.where(Team.is_active == search_params.is_active)
                filters_applied["is_active"] = search_params.is_active

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply pagination and ordering
            offset = (search_params.page - 1) * search_params.page_size
            query = query.order_by(Team.market, Team.name).offset(offset).limit(search_params.page_size)

            # Execute query
            result = await self.db.execute(query)
            teams = result.scalars().all()

            # Convert to enhanced response schemas
            enhanced_teams = []
            for team in teams:
                # Get league information
                leagues_info = await self._get_team_leagues_info(team)

                # Create base team response
                team_response = self._create_team_response(team, leagues_info)

                # Get search highlighting and relevance
                search_matches = self._get_search_matches(team, search_params.query)
                relevance_score = self._calculate_relevance_score(team, search_params.query)

                # Create enhanced response
                enhanced_team = EnhancedTeamResponse(
                    **team_response.model_dump(),
                    search_matches=search_matches,
                    relevance_score=relevance_score
                )
                enhanced_teams.append(enhanced_team)

            # Sort by relevance if there's a search query
            if search_params.query:
                enhanced_teams.sort(key=lambda t: t.relevance_score or 0, reverse=True)

            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000

            # Create search metadata
            search_metadata = SearchMetadata(
                query=search_params.query,
                total_matches=total,
                response_time_ms=response_time_ms,
                filters_applied=filters_applied,
                timestamp=datetime.utcnow()
            )

            # Create enhanced paginated response
            return EnhancedTeamsPaginatedResponse(
                items=enhanced_teams,
                total=total,
                page=search_params.page,
                page_size=search_params.page_size,
                has_next=(search_params.page * search_params.page_size) < total,
                has_previous=search_params.page > 1,
                search_metadata=search_metadata
            )

        except Exception as e:
            logger.error(f"Error in enhanced team search: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search teams"
            )

    async def get_search_suggestions(self, query: str, limit: int = 10) -> SearchSuggestionsResponse:
        """
        Get search suggestions/autocomplete for team search

        Args:
            query: Partial search query
            limit: Maximum number of suggestions to return

        Returns:
            Search suggestions with preview teams

        Raises:
            HTTPException: If database operation fails
        """
        start_time = time.time()

        try:
            suggestions = []

            if len(query) < 1:
                # For very short queries, return empty suggestions
                return SearchSuggestionsResponse(
                    query=query,
                    suggestions=[],
                    response_time_ms=(time.time() - start_time) * 1000
                )

            query_lower = query.lower()

            # Get team name suggestions
            name_query = select(Team.name, func.count().label('count')).where(
                and_(
                    func.lower(Team.name).like(f'{query_lower}%'),
                    Team.is_active == True
                )
            ).group_by(Team.name).order_by(func.count().desc(), Team.name).limit(limit)

            name_result = await self.db.execute(name_query)
            name_suggestions = name_result.all()

            for name, count in name_suggestions:
                # Get preview teams for this name
                preview_query = select(Team.name, Team.market).where(
                    and_(
                        func.lower(Team.name).like(f'{query_lower}%'),
                        Team.is_active == True
                    )
                ).limit(3)

                preview_result = await self.db.execute(preview_query)
                preview_teams = [f"{row[1]} {row[0]}" for row in preview_result.all()]

                suggestions.append(TeamSearchSuggestion(
                    suggestion=name,
                    type="team_name",
                    team_count=count,
                    preview_teams=preview_teams
                ))

            # Get market suggestions
            market_query = select(Team.market, func.count().label('count')).where(
                and_(
                    func.lower(Team.market).like(f'{query_lower}%'),
                    Team.is_active == True
                )
            ).group_by(Team.market).order_by(func.count().desc(), Team.market).limit(limit)

            market_result = await self.db.execute(market_query)
            market_suggestions = market_result.all()

            for market, count in market_suggestions:
                # Get preview teams for this market
                preview_query = select(Team.name, Team.market).where(
                    and_(
                        func.lower(Team.market).like(f'{query_lower}%'),
                        Team.is_active == True
                    )
                ).limit(3)

                preview_result = await self.db.execute(preview_query)
                preview_teams = [f"{row[1]} {row[0]}" for row in preview_result.all()]

                suggestions.append(TeamSearchSuggestion(
                    suggestion=market,
                    type="market",
                    team_count=count,
                    preview_teams=preview_teams
                ))

            # Get abbreviation suggestions
            abbrev_query = select(Team.abbreviation, func.count().label('count')).where(
                and_(
                    Team.abbreviation.isnot(None),
                    func.lower(Team.abbreviation).like(f'{query_lower}%'),
                    Team.is_active == True
                )
            ).group_by(Team.abbreviation).order_by(func.count().desc(), Team.abbreviation).limit(limit)

            abbrev_result = await self.db.execute(abbrev_query)
            abbrev_suggestions = abbrev_result.all()

            for abbreviation, count in abbrev_suggestions:
                # Get preview teams for this abbreviation
                preview_query = select(Team.name, Team.market).where(
                    and_(
                        func.lower(Team.abbreviation).like(f'{query_lower}%'),
                        Team.is_active == True
                    )
                ).limit(3)

                preview_result = await self.db.execute(preview_query)
                preview_teams = [f"{row[1]} {row[0]}" for row in preview_result.all()]

                suggestions.append(TeamSearchSuggestion(
                    suggestion=abbreviation,
                    type="abbreviation",
                    team_count=count,
                    preview_teams=preview_teams
                ))

            # Sort suggestions by relevance (team count desc, then alphabetically)
            suggestions.sort(key=lambda s: (-s.team_count, s.suggestion))

            # Limit total suggestions
            suggestions = suggestions[:limit]

            response_time_ms = (time.time() - start_time) * 1000

            return SearchSuggestionsResponse(
                query=query,
                suggestions=suggestions,
                response_time_ms=response_time_ms
            )

        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get search suggestions"
            )

    async def get_user_team_preferences(self, user: User) -> UserTeamPreferencesResponse:
        """
        Get user's team preferences

        Args:
            user: User model

        Returns:
            User's team preferences with team details

        Raises:
            HTTPException: If database operation fails
        """
        try:
            # Get user's team preferences with related team, sport, and league memberships data
            query = select(UserTeamPreference).options(
                selectinload(UserTeamPreference.team).selectinload(Team.sport),
                selectinload(UserTeamPreference.team).selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            ).where(
                UserTeamPreference.user_id == user.id,
                UserTeamPreference.is_active == True
            ).order_by(UserTeamPreference.affinity_score.desc())

            result = await self.db.execute(query)
            preferences = result.scalars().all()

            # Convert to response schemas
            preference_responses = [
                UserTeamPreferenceResponse(
                    id=pref.id,
                    team_id=pref.team_id,
                    affinity_score=float(pref.affinity_score),
                    is_active=pref.is_active,
                    created_at=pref.created_at,
                    updated_at=pref.updated_at,
                    team_name=pref.team.name if pref.team else None,
                    team_market=pref.team.market if pref.team else None,
                    team_display_name=pref.team.display_name if pref.team else None,
                    team_logo_url=pref.team.logo_url if pref.team else None,
                    sport_name=pref.team.sport.name if pref.team and pref.team.sport else None,
                    league_name=self._get_primary_league_name(pref.team) if pref.team else None
                )
                for pref in preferences
            ]

            return UserTeamPreferencesResponse(
                preferences=preference_responses,
                total_count=len(preference_responses)
            )

        except Exception as e:
            logger.error(f"Error getting user team preferences for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve team preferences"
            )

    async def update_user_team_preferences(
        self,
        user: User,
        preferences_update: UserTeamPreferencesUpdate
    ) -> UserTeamPreferencesResponse:
        """
        Update user's team preferences (replace all)

        Args:
            user: User model
            preferences_update: New team preferences

        Returns:
            Updated team preferences

        Raises:
            HTTPException: If validation or database operation fails
        """
        try:
            # Validate input
            if not preferences_update.preferences:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one team preference must be provided"
                )

            # Validate team IDs are unique and teams exist
            team_ids = set()
            for pref in preferences_update.preferences:
                if pref.team_id in team_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Duplicate team_id {pref.team_id} found in preferences"
                    )
                team_ids.add(pref.team_id)

            # Validate all teams exist
            teams_query = select(Team).where(Team.id.in_(team_ids))
            teams_result = await self.db.execute(teams_query)
            existing_teams = {team.id for team in teams_result.scalars().all()}

            missing_teams = team_ids - existing_teams
            if missing_teams:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Teams not found: {list(missing_teams)}"
                )

            # Delete existing team preferences
            await self.db.execute(
                delete(UserTeamPreference).where(UserTeamPreference.user_id == user.id)
            )

            # Create new team preferences
            new_preferences = []
            for pref_data in preferences_update.preferences:
                new_pref = UserTeamPreference(
                    user_id=user.id,
                    team_id=pref_data.team_id,
                    affinity_score=Decimal(str(pref_data.affinity_score)),
                    is_active=pref_data.is_active
                )
                new_preferences.append(new_pref)
                self.db.add(new_pref)

            await self.db.commit()

            # Refresh to get related data and return updated preferences
            return await self.get_user_team_preferences(user)

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating team preferences for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update team preferences"
            )

    async def remove_user_team_preference(self, user: User, team_id: UUID) -> Dict[str, Any]:
        """
        Remove a specific team preference for user

        Args:
            user: User model
            team_id: Team UUID to remove

        Returns:
            Success message

        Raises:
            HTTPException: If preference not found or database operation fails
        """
        try:
            # Check if preference exists
            preference_query = select(UserTeamPreference).where(
                and_(
                    UserTeamPreference.user_id == user.id,
                    UserTeamPreference.team_id == team_id
                )
            )
            result = await self.db.execute(preference_query)
            preference = result.scalar_one_or_none()

            if not preference:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team preference for team {team_id} not found"
                )

            # Delete the preference
            await self.db.execute(
                delete(UserTeamPreference).where(
                    and_(
                        UserTeamPreference.user_id == user.id,
                        UserTeamPreference.team_id == team_id
                    )
                )
            )

            await self.db.commit()

            return {
                "message": f"Team preference for team {team_id} removed successfully",
                "team_id": str(team_id)
            }

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error removing team preference for user {user.id}, team {team_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove team preference"
            )