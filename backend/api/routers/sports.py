"""
Enhanced Sports API Router with Multi-League Support
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session
from backend.api.services.sports_service import SportsService
from backend.api.schemas.sports import (
    MultiLeagueTeamResponse,
    MultiLeagueTeamsPaginatedResponse,
    LeagueInfo,
    SoccerTeamFilters,
    TeamLeagueMembershipResponse
)
from backend.api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/sports", tags=["sports"])


async def get_sports_service(db: AsyncSession = Depends(get_async_session)) -> SportsService:
    """Dependency to get SportsService instance"""
    return SportsService(db)


@router.get("/teams/{team_id}/leagues", response_model=List[LeagueInfo])
async def get_team_leagues(
    team_id: UUID,
    sports_service: SportsService = Depends(get_sports_service)
) -> List[LeagueInfo]:
    """
    Get all leagues for a specific team

    Returns all active league memberships for the specified team,
    including information about league level, competition type, and membership details.
    """
    try:
        leagues = await sports_service.get_team_leagues(team_id)
        if not leagues:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found or has no league memberships"
            )
        return leagues
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving team leagues: {str(e)}"
        )


@router.get("/leagues/{league_id}/teams", response_model=List[MultiLeagueTeamResponse])
async def get_league_teams(
    league_id: UUID,
    include_inactive: bool = Query(False, description="Include inactive team memberships"),
    sports_service: SportsService = Depends(get_sports_service)
) -> List[MultiLeagueTeamResponse]:
    """
    Get all teams for a specific league

    Returns all teams that have memberships in the specified league,
    with complete multi-league information for each team.
    """
    try:
        teams = await sports_service.get_league_teams(league_id, include_inactive)
        return teams
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving league teams: {str(e)}"
        )


@router.get("/teams/multi-league", response_model=List[MultiLeagueTeamResponse])
async def get_multi_league_teams(
    sport_id: Optional[UUID] = Query(None, description="Filter by sport ID (defaults to soccer)"),
    sports_service: SportsService = Depends(get_sports_service)
) -> List[MultiLeagueTeamResponse]:
    """
    Get teams that participate in multiple leagues

    Returns teams that have active memberships in more than one league,
    particularly useful for finding teams in both domestic and international competitions.
    """
    try:
        teams = await sports_service.get_multi_league_teams(sport_id)
        return teams
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving multi-league teams: {str(e)}"
        )


@router.get("/soccer/teams", response_model=MultiLeagueTeamsPaginatedResponse)
async def get_soccer_teams(
    league_ids: Optional[List[UUID]] = Query(None, description="Filter by league IDs"),
    country_codes: Optional[List[str]] = Query(None, description="Filter by country codes"),
    competition_types: Optional[List[str]] = Query(None, description="Filter by competition types"),
    league_levels: Optional[List[int]] = Query(None, description="Filter by league levels"),
    multi_league_only: bool = Query(False, description="Show only multi-league teams"),
    founding_year_min: Optional[int] = Query(None, description="Minimum founding year"),
    founding_year_max: Optional[int] = Query(None, description="Maximum founding year"),
    query: Optional[str] = Query(None, description="Search query for team names"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sports_service: SportsService = Depends(get_sports_service)
) -> MultiLeagueTeamsPaginatedResponse:
    """
    Get soccer teams with advanced filtering and multi-league support

    Provides comprehensive filtering options for soccer teams including:
    - League membership filtering
    - Geographic filtering (country codes)
    - Competition type filtering (domestic, international, cup)
    - Multi-league team identification
    - Full-text search capabilities
    - Pagination support

    Example use cases:
    - Find all teams in UEFA Champions League: competition_types=["international"]
    - Find Spanish teams in multiple leagues: country_codes=["ES"], multi_league_only=true
    - Search for Real Madrid: query="Real Madrid"
    """
    try:
        filters = SoccerTeamFilters(
            league_ids=league_ids,
            country_codes=country_codes,
            competition_types=competition_types,
            league_levels=league_levels,
            multi_league_only=multi_league_only,
            founding_year_min=founding_year_min,
            founding_year_max=founding_year_max,
            query=query,
            page=page,
            page_size=page_size
        )

        teams, total_count = await sports_service.get_teams_with_multi_league_info(filters)

        return MultiLeagueTeamsPaginatedResponse(
            items=teams,
            total=total_count,
            page=page,
            page_size=page_size,
            pages=(total_count + page_size - 1) // page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving soccer teams: {str(e)}"
        )


@router.get("/soccer/leagues", response_model=List[Dict[str, Any]])
async def get_soccer_leagues(
    sports_service: SportsService = Depends(get_sports_service)
) -> List[Dict[str, Any]]:
    """
    Get all soccer leagues with team counts

    Returns comprehensive information about all active soccer leagues including:
    - Basic league information (name, slug, country)
    - League classification (level, competition type)
    - Team counts (total teams, current teams)

    Useful for:
    - League selection interfaces
    - Statistical dashboards
    - League comparison views
    """
    try:
        leagues = await sports_service.get_soccer_leagues_with_team_counts()
        return leagues
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving soccer leagues: {str(e)}"
        )


@router.get("/teams/{team_id}/multi-league-info", response_model=MultiLeagueTeamResponse)
async def get_team_multi_league_info(
    team_id: UUID,
    sports_service: SportsService = Depends(get_sports_service)
) -> MultiLeagueTeamResponse:
    """
    Get comprehensive multi-league information for a specific team

    Returns detailed information about a team including:
    - All league memberships (current and historical)
    - Primary league designation
    - Multi-league status
    - Enhanced team metadata

    Particularly useful for team detail pages and comprehensive team profiles.
    """
    try:
        # Create a filter for this specific team
        filters = SoccerTeamFilters(page=1, page_size=1)

        # Get teams with multi-league info but filter in the service layer
        # This is a bit of a workaround - in a real implementation, you'd want
        # a specific service method for getting a single team
        from sqlalchemy import select
        from backend.models.sports import Team
        from sqlalchemy.orm import selectinload
        from backend.models.sports import TeamLeagueMembership

        # Get the team directly
        db = sports_service.db
        result = await db.execute(
            select(Team)
            .options(
                selectinload(Team.sport),
                selectinload(Team.league_memberships).selectinload(TeamLeagueMembership.league)
            )
            .where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found"
            )

        # Get league information
        leagues_info = await sports_service._get_team_leagues_info(team)

        if not leagues_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} has no active league memberships"
            )

        # Determine primary league using new logic
        primary_league_info = sports_service._determine_primary_league(leagues_info)

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

        return team_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving team information: {str(e)}"
        )


# Health check endpoint for the sports service
@router.get("/health")
async def sports_health_check(
    sports_service: SportsService = Depends(get_sports_service)
) -> Dict[str, Any]:
    """
    Health check for the sports service

    Validates database connectivity and basic service functionality.
    """
    try:
        # Try to get soccer sport ID as a basic connectivity test
        soccer_sport_id = await sports_service.get_soccer_sport_id()

        return {
            "status": "healthy",
            "service": "sports-api",
            "soccer_sport_available": soccer_sport_id is not None,
            "soccer_sport_id": str(soccer_sport_id) if soccer_sport_id else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Sports service health check failed: {str(e)}"
        )