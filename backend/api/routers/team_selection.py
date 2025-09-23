"""
Team selection API router with all sports, leagues, teams, and preferences endpoints
"""

import logging
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session
from backend.api.middleware.auth import firebase_auth_optional
from backend.api.services.user_service import get_current_db_user, AuthenticatedUserContext, get_current_user_context
from backend.api.services.team_selection_service import TeamSelectionService
from backend.api.schemas.sports import (
    SportResponse,
    SportWithLeagues,
    LeagueResponse,
    LeagueWithTeams,
    TeamResponse,
    TeamSearchParams,
    UserTeamPreferencesUpdate,
    UserTeamPreferencesResponse,
    SportsPaginatedResponse,
    LeaguesPaginatedResponse,
    TeamsPaginatedResponse,
    EnhancedTeamsPaginatedResponse,
    SearchSuggestionsResponse
)
from backend.models.users import User

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["Team Selection"])


# Dependency to get team selection service
async def get_team_selection_service(db: AsyncSession = Depends(get_async_session)) -> TeamSelectionService:
    """Dependency to get TeamSelectionService instance"""
    return TeamSelectionService(db)


@router.get(
    "/sports",
    response_model=List[Union[SportResponse, SportWithLeagues]],
    summary="Get all sports",
    description="Retrieve all available sports with optional league inclusion"
)
async def get_sports(
    include_leagues: bool = Query(False, description="Include leagues for each sport"),
    include_inactive: bool = Query(False, description="Include inactive sports"),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> List[Union[SportResponse, SportWithLeagues]]:
    """
    Get all available sports

    - **include_leagues**: Whether to include leagues for each sport
    - **include_inactive**: Whether to include inactive sports

    Returns a list of sports with their basic information and optionally their leagues.
    """
    logger.info(f"Getting sports: include_leagues={include_leagues}, include_inactive={include_inactive}")

    sports = await team_service.get_sports(
        include_leagues=include_leagues,
        include_inactive=include_inactive
    )

    logger.info(f"Retrieved {len(sports)} sports")
    return sports


@router.get(
    "/sports/{sport_id}/leagues",
    response_model=List[Union[LeagueResponse, LeagueWithTeams]],
    summary="Get leagues for a sport",
    description="Retrieve all leagues for a specific sport with optional team inclusion"
)
async def get_sport_leagues(
    sport_id: UUID,
    include_teams: bool = Query(False, description="Include teams for each league"),
    include_inactive: bool = Query(False, description="Include inactive leagues"),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> List[Union[LeagueResponse, LeagueWithTeams]]:
    """
    Get leagues for a specific sport

    - **sport_id**: UUID of the sport
    - **include_teams**: Whether to include teams for each league
    - **include_inactive**: Whether to include inactive leagues

    Returns a list of leagues for the specified sport.
    """
    logger.info(f"Getting leagues for sport {sport_id}: include_teams={include_teams}, include_inactive={include_inactive}")

    leagues = await team_service.get_sport_leagues(
        sport_id=sport_id,
        include_teams=include_teams,
        include_inactive=include_inactive
    )

    logger.info(f"Retrieved {len(leagues)} leagues for sport {sport_id}")
    return leagues


@router.get(
    "/leagues/{league_id}/teams",
    response_model=TeamsPaginatedResponse,
    summary="Get teams for a league",
    description="Retrieve all teams for a specific league with pagination"
)
async def get_league_teams(
    league_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    include_inactive: bool = Query(False, description="Include inactive teams"),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> TeamsPaginatedResponse:
    """
    Get teams for a specific league

    - **league_id**: UUID of the league
    - **page**: Page number (1-indexed)
    - **page_size**: Number of items per page (max 100)
    - **include_inactive**: Whether to include inactive teams

    Returns a paginated list of teams for the specified league.
    """
    logger.info(f"Getting teams for league {league_id}: page={page}, page_size={page_size}, include_inactive={include_inactive}")

    teams = await team_service.get_league_teams(
        league_id=league_id,
        page=page,
        page_size=page_size,
        include_inactive=include_inactive
    )

    logger.info(f"Retrieved {len(teams.items)} teams for league {league_id} (page {page})")
    return teams


@router.get(
    "/teams/search",
    response_model=TeamsPaginatedResponse,
    summary="Search teams",
    description="Search teams by name, market, sport, or league with pagination"
)
async def search_teams(
    query: Optional[str] = Query(None, description="Search query for team name or market"),
    sport_id: Optional[UUID] = Query(None, description="Filter by sport ID"),
    league_id: Optional[UUID] = Query(None, description="Filter by league ID"),
    market: Optional[str] = Query(None, description="Filter by market/city"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> TeamsPaginatedResponse:
    """
    Search teams with various filters

    - **query**: Search query for team name or market
    - **sport_id**: Filter by sport UUID
    - **league_id**: Filter by league UUID
    - **market**: Filter by market/city name
    - **is_active**: Filter by active status
    - **page**: Page number (1-indexed)
    - **page_size**: Number of items per page (max 100)

    Returns a paginated list of teams matching the search criteria.
    """
    logger.info(f"Searching teams: query='{query}', sport_id={sport_id}, league_id={league_id}, market='{market}', is_active={is_active}, page={page}, page_size={page_size}")

    search_params = TeamSearchParams(
        query=query,
        sport_id=sport_id,
        league_id=league_id,
        market=market,
        is_active=is_active,
        page=page,
        page_size=page_size
    )

    teams = await team_service.search_teams(search_params)

    logger.info(f"Found {teams.total} total teams, returning {len(teams.items)} for page {page}")
    return teams


@router.get(
    "/teams/search-enhanced",
    response_model=EnhancedTeamsPaginatedResponse,
    summary="Enhanced team search with metadata and highlighting",
    description="Enhanced search teams with performance metrics, search highlighting, and relevance scoring"
)
async def search_teams_enhanced(
    query: Optional[str] = Query(None, description="Search query for team name or market"),
    sport_id: Optional[UUID] = Query(None, description="Filter by sport ID"),
    league_id: Optional[UUID] = Query(None, description="Filter by league ID"),
    market: Optional[str] = Query(None, description="Filter by market/city"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> EnhancedTeamsPaginatedResponse:
    """
    Enhanced search teams with advanced features

    **Features:**
    - **Search highlighting**: Shows which fields matched your query
    - **Relevance scoring**: Results ranked by relevance to your search
    - **Performance metrics**: Response time and search metadata
    - **Enhanced filtering**: Supports abbreviations and partial matches

    **Search supports:**
    - Team names (e.g., "Bears", "Lakers", "Patriots")
    - Market/city names (e.g., "Chicago", "Los Angeles")
    - Abbreviations (e.g., "CHI", "LAL", "NE")
    - Partial matches (e.g., "Chi" finds Chicago teams)

    **Filters:**
    - **query**: Search query for team name or market
    - **sport_id**: Filter by sport UUID
    - **league_id**: Filter by league UUID
    - **market**: Filter by market/city name
    - **is_active**: Filter by active status
    - **page**: Page number (1-indexed)
    - **page_size**: Number of items per page (max 100)

    **Returns:**
    - Teams with search highlighting
    - Relevance scores for ranking
    - Performance metrics (response time)
    - Applied filters information
    """
    logger.info(f"Enhanced team search: query='{query}', sport_id={sport_id}, league_id={league_id}, market='{market}', is_active={is_active}, page={page}, page_size={page_size}")

    search_params = TeamSearchParams(
        query=query,
        sport_id=sport_id,
        league_id=league_id,
        market=market,
        is_active=is_active,
        page=page,
        page_size=page_size
    )

    teams = await team_service.search_teams_enhanced(search_params)

    logger.info(f"Enhanced search completed: {teams.search_metadata.total_matches} matches in {teams.search_metadata.response_time_ms:.2f}ms")
    return teams


@router.get(
    "/teams/search-suggestions",
    response_model=SearchSuggestionsResponse,
    summary="Get search suggestions for team autocomplete",
    description="Get search suggestions and autocomplete options for team search queries"
)
async def get_team_search_suggestions(
    query: str = Query(..., min_length=1, description="Search query (minimum 1 character)"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> SearchSuggestionsResponse:
    """
    Get search suggestions for team autocomplete

    **Purpose:**
    Provides intelligent autocomplete suggestions for team search queries to improve
    user experience and help users discover teams more easily.

    **Features:**
    - **Team name suggestions**: Suggests team names that start with your query
    - **Market/city suggestions**: Suggests cities/markets that start with your query
    - **Abbreviation suggestions**: Suggests team abbreviations that start with your query
    - **Team count**: Shows how many teams match each suggestion
    - **Preview teams**: Shows sample team names for each suggestion

    **Examples:**
    - Query "Chi" → suggests "Chicago" (market), "Chiefs" (team name), "CHI" (abbreviation)
    - Query "L" → suggests "Los Angeles" (market), "Lakers" (team name), "LAL" (abbreviation)
    - Query "Pat" → suggests "Patriots" (team name)

    **Parameters:**
    - **query**: Search query (minimum 1 character)
    - **limit**: Maximum number of suggestions (1-20, default 10)

    **Returns:**
    - Ranked suggestions by relevance (team count and alphabetical)
    - Team count for each suggestion
    - Preview of matching teams
    - Response time for performance monitoring
    """
    logger.info(f"Getting search suggestions for query: '{query}' (limit: {limit})")

    suggestions = await team_service.get_search_suggestions(query, limit)

    logger.info(f"Returned {len(suggestions.suggestions)} suggestions in {suggestions.response_time_ms:.2f}ms")
    return suggestions


@router.get(
    "/user/team-preferences",
    response_model=UserTeamPreferencesResponse,
    summary="Get user team preferences",
    description="Get current user's team preferences with team details"
)
async def get_user_team_preferences(
    db_user: User = Depends(get_current_db_user),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> UserTeamPreferencesResponse:
    """
    Get current user's team preferences

    **Requires**: Valid Firebase JWT token

    Returns the user's team preferences with full team details including:
    - Team name, market, and display name
    - Team logo URL and colors
    - Sport and league information
    - User's affinity score for each team
    """
    logger.info(f"Getting team preferences for user {db_user.id}")

    preferences = await team_service.get_user_team_preferences(db_user)

    logger.info(f"Retrieved {preferences.total_count} team preferences for user {db_user.id}")
    return preferences


@router.post(
    "/user/team-preferences",
    response_model=UserTeamPreferencesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set user team preferences",
    description="Set/update user's team preferences (replaces all existing preferences)"
)
async def set_user_team_preferences(
    preferences_update: UserTeamPreferencesUpdate,
    db_user: User = Depends(get_current_db_user),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> UserTeamPreferencesResponse:
    """
    Set or update user's team preferences

    **Requires**: Valid Firebase JWT token

    This endpoint replaces all existing team preferences with the provided list.
    Each preference includes:
    - **team_id**: UUID of the team
    - **affinity_score**: User's preference score (0.0-1.0)
    - **is_active**: Whether this preference is active

    All team IDs must be valid and unique within the request.
    """
    logger.info(f"Setting team preferences for user {db_user.id}: {len(preferences_update.preferences)} preferences")

    preferences = await team_service.update_user_team_preferences(db_user, preferences_update)

    logger.info(f"Updated team preferences for user {db_user.id}: {preferences.total_count} preferences set")
    return preferences


@router.put(
    "/user/team-preferences",
    response_model=UserTeamPreferencesResponse,
    summary="Update user team preferences",
    description="Update user's team preferences (replaces all existing preferences)"
)
async def update_user_team_preferences(
    preferences_update: UserTeamPreferencesUpdate,
    db_user: User = Depends(get_current_db_user),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> UserTeamPreferencesResponse:
    """
    Update user's team preferences

    **Requires**: Valid Firebase JWT token

    This endpoint replaces all existing team preferences with the provided list.
    Same functionality as POST endpoint - use either depending on your preference.
    """
    logger.info(f"Updating team preferences for user {db_user.id}: {len(preferences_update.preferences)} preferences")

    preferences = await team_service.update_user_team_preferences(db_user, preferences_update)

    logger.info(f"Updated team preferences for user {db_user.id}: {preferences.total_count} preferences set")
    return preferences


@router.delete(
    "/user/team-preferences/{team_id}",
    summary="Remove team preference",
    description="Remove a specific team preference for the current user"
)
async def remove_user_team_preference(
    team_id: UUID,
    db_user: User = Depends(get_current_db_user),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> Dict[str, Any]:
    """
    Remove a specific team preference

    **Requires**: Valid Firebase JWT token

    - **team_id**: UUID of the team to remove from preferences

    Returns a success message if the preference was found and removed.
    """
    logger.info(f"Removing team preference for user {db_user.id}, team {team_id}")

    result = await team_service.remove_user_team_preference(db_user, team_id)

    logger.info(f"Removed team preference for user {db_user.id}, team {team_id}")
    return result


# Optional endpoints with authentication
@router.get(
    "/public/sports",
    response_model=List[Union[SportResponse, SportWithLeagues]],
    summary="Get sports (public with optional personalization)",
    description="Public endpoint to get sports with optional personalization if authenticated"
)
async def get_public_sports(
    include_leagues: bool = Query(False, description="Include leagues for each sport"),
    include_inactive: bool = Query(False, description="Include inactive sports"),
    user_context: Optional[AuthenticatedUserContext] = Depends(get_current_user_context),
    team_service: TeamSelectionService = Depends(get_team_selection_service)
) -> List[Union[SportResponse, SportWithLeagues]]:
    """
    Get all available sports (public endpoint with optional personalization)

    **Optional**: Firebase JWT token for personalization

    - **include_leagues**: Whether to include leagues for each sport
    - **include_inactive**: Whether to include inactive sports

    If authenticated, this could be enhanced to include user-specific data like
    preferred sports highlighted or ordered by user preferences.
    """
    logger.info(f"Getting public sports: include_leagues={include_leagues}, include_inactive={include_inactive}, authenticated={user_context is not None}")

    sports = await team_service.get_sports(
        include_leagues=include_leagues,
        include_inactive=include_inactive
    )

    # Future enhancement: personalize response based on user preferences
    if user_context and user_context.db_user:
        logger.info(f"Personalizing sports response for user {user_context.db_user.id}")
        # Could add logic to highlight user's preferred sports, reorder by preference, etc.

    logger.info(f"Retrieved {len(sports)} sports (public endpoint)")
    return sports