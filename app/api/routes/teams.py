"""Team management routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from ..deps import get_current_active_user, get_optional_current_user, get_redis
from ...models.user import CurrentUser
from ...models.team import (
    TeamResponse, TeamListResponse, TeamSearchFilters, TeamStats,
    TeamStatsResponse, Sport, League, TeamStatus
)
from ...models.base import BaseResponse, PaginatedResponse
from ...services.redis_service import RedisService

router = APIRouter()


class TeamDetailResponse(BaseResponse):
    """Team detail response model."""

    team: TeamResponse


class TeamSummaryResponse(BaseResponse):
    """Team summary response for dashboard."""

    teams: List[TeamResponse]
    user_favorites: List[str]
    total_favorites: int


# Mock data for teams (replace with database in production)
MOCK_TEAMS = [
    {
        "id": "team_1",
        "name": "Los Angeles Lakers",
        "city": "Los Angeles",
        "abbreviation": "LAL",
        "sport": "nba",
        "league": "NBA",
        "logo_url": "https://example.com/lakers.png",
        "primary_color": "#552583",
        "secondary_color": "#FDB927",
        "conference": "Western",
        "division": "Pacific",
        "status": "active",
        "follower_count": 15420,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "team_2",
        "name": "New England Patriots",
        "city": "Foxborough",
        "abbreviation": "NE",
        "sport": "nfl",
        "league": "NFL",
        "logo_url": "https://example.com/patriots.png",
        "primary_color": "#002244",
        "secondary_color": "#C60C30",
        "conference": "AFC",
        "division": "East",
        "status": "active",
        "follower_count": 22150,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "team_3",
        "name": "New York Yankees",
        "city": "New York",
        "abbreviation": "NYY",
        "sport": "mlb",
        "league": "MLB",
        "logo_url": "https://example.com/yankees.png",
        "primary_color": "#132448",
        "secondary_color": "#C4CED4",
        "conference": "American League",
        "division": "East",
        "status": "active",
        "follower_count": 18900,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]


@router.get(
    "/",
    response_model=List[TeamResponse],
    status_code=status.HTTP_200_OK,
    summary="Get teams",
    description="Get list of teams with optional filtering"
)
async def get_teams(
    sport: Optional[Sport] = Query(None, description="Filter by sport"),
    league: Optional[League] = Query(None, description="Filter by league"),
    search: Optional[str] = Query(None, description="Search team name or city"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    redis_service: RedisService = Depends(get_redis)
):
    """
    Get teams with optional filtering.

    Supports filtering by:
    - Sport type (NBA, NFL, MLB, etc.)
    - League
    - Search query (team name or city)
    - Pagination
    """
    try:
        # Check cache first
        cache_key = f"teams:list:{sport}:{league}:{search}:{page}:{page_size}"
        cached_teams = await redis_service.get_json(cache_key)

        if cached_teams:
            return [TeamResponse(**team) for team in cached_teams]

        # Filter teams (mock implementation)
        filtered_teams = MOCK_TEAMS.copy()

        if sport:
            filtered_teams = [t for t in filtered_teams if t["sport"] == sport.value]

        if league:
            filtered_teams = [t for t in filtered_teams if t["league"] == league.value]

        if search:
            search_lower = search.lower()
            filtered_teams = [
                t for t in filtered_teams
                if search_lower in t["name"].lower() or search_lower in t.get("city", "").lower()
            ]

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_teams = filtered_teams[start_idx:end_idx]

        # Cache results
        await redis_service.set_json(cache_key, paginated_teams, expire=300)  # 5 minutes

        return [TeamResponse(**team) for team in paginated_teams]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve teams: {str(e)}"
        )


@router.get(
    "/{team_id}",
    response_model=TeamDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get team by ID",
    description="Get detailed information about a specific team"
)
async def get_team_by_id(
    team_id: str,
    redis_service: RedisService = Depends(get_redis)
):
    """
    Get team by ID.

    Returns detailed information about a specific team including:
    - Team profile data
    - Statistics
    - Current season information
    """
    try:
        # Check cache first
        cached_team = await redis_service.get_team_data(team_id)

        if cached_team:
            return TeamDetailResponse(
                success=True,
                message="Team retrieved successfully",
                team=TeamResponse(**cached_team)
            )

        # Find team in mock data
        team_data = next((t for t in MOCK_TEAMS if t["id"] == team_id), None)

        if not team_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        # Cache team data
        await redis_service.cache_team_data(team_id, team_data)

        return TeamDetailResponse(
            success=True,
            message="Team retrieved successfully",
            team=TeamResponse(**team_data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team: {str(e)}"
        )


@router.get(
    "/{team_id}/dashboard",
    response_model=TeamDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get team dashboard data",
    description="Get team data optimized for dashboard display"
)
async def get_team_dashboard(
    team_id: str,
    current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
    redis_service: RedisService = Depends(get_redis)
):
    """
    Get team dashboard data.

    Returns team information optimized for dashboard display:
    - Team profile
    - Recent performance
    - Upcoming games
    - Fan engagement metrics
    """
    try:
        # Get team data
        team_response = await get_team_by_id(team_id, redis_service)

        # Add user-specific data if authenticated
        if current_user:
            # TODO: Add user-specific team data like follow status
            pass

        return team_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team dashboard: {str(e)}"
        )


@router.get(
    "/{team_id}/news",
    status_code=status.HTTP_200_OK,
    summary="Get team news",
    description="Get latest news and updates for a specific team"
)
async def get_team_news(
    team_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of news items"),
    redis_service: RedisService = Depends(get_redis)
):
    """
    Get team news.

    Returns latest news articles and updates for the specified team.
    """
    try:
        # Check cache first
        cache_key = f"team_news:{team_id}:{limit}"
        cached_news = await redis_service.get_json(cache_key)

        if cached_news:
            return {
                "success": True,
                "message": "Team news retrieved successfully",
                "news": cached_news
            }

        # Mock news data
        mock_news = [
            {
                "id": f"news_{team_id}_1",
                "title": "Team Update: Latest Performance Analysis",
                "summary": "Comprehensive analysis of recent team performance and upcoming strategies.",
                "published_at": "2024-01-15T10:00:00Z",
                "source": "ESPN",
                "url": "https://example.com/news/1"
            },
            {
                "id": f"news_{team_id}_2",
                "title": "Player Spotlight: Key Performances This Season",
                "summary": "Highlighting standout player performances and statistics from this season.",
                "published_at": "2024-01-14T15:30:00Z",
                "source": "Sports Illustrated",
                "url": "https://example.com/news/2"
            }
        ]

        # Cache news data
        await redis_service.set_json(cache_key, mock_news, expire=600)  # 10 minutes

        return {
            "success": True,
            "message": "Team news retrieved successfully",
            "news": mock_news[:limit]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team news: {str(e)}"
        )


@router.get(
    "/{team_id}/summary",
    status_code=status.HTTP_200_OK,
    summary="Get team AI summary",
    description="Get AI-generated summary of team performance and news"
)
async def get_team_summary(
    team_id: str,
    current_user: CurrentUser = Depends(get_current_active_user),
    redis_service: RedisService = Depends(get_redis)
):
    """
    Get team AI summary.

    Returns an AI-generated summary of:
    - Recent team performance
    - Key news and updates
    - Upcoming games and events
    - Fan sentiment analysis
    """
    try:
        # Check cache first
        cache_key = f"team_summary:{team_id}"
        cached_summary = await redis_service.get_json(cache_key)

        if cached_summary:
            return {
                "success": True,
                "message": "Team summary retrieved successfully",
                "summary": cached_summary
            }

        # Get team data for summary generation
        team_response = await get_team_by_id(team_id, redis_service)
        team = team_response.team

        # Mock AI summary (replace with actual AI service)
        mock_summary = {
            "team_id": team_id,
            "team_name": team.name,
            "generated_at": "2024-01-15T12:00:00Z",
            "summary": f"The {team.name} have shown strong performance this season with a solid roster and strategic gameplay. Recent analysis indicates positive fan engagement and competitive standings in the {team.conference} {team.division} division.",
            "key_points": [
                "Strong defensive performance in recent games",
                "High fan engagement and attendance",
                "Positive team chemistry and leadership",
                "Strategic acquisitions showing impact"
            ],
            "performance_score": 85,
            "fan_sentiment": "positive",
            "next_game": "2024-01-20T19:00:00Z"
        }

        # Cache summary
        await redis_service.set_json(cache_key, mock_summary, expire=1800)  # 30 minutes

        return {
            "success": True,
            "message": "Team summary generated successfully",
            "summary": mock_summary
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate team summary: {str(e)}"
        )


@router.get(
    "/{team_id}/stats",
    response_model=TeamStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get team statistics",
    description="Get current season statistics for a team"
)
async def get_team_stats(
    team_id: str,
    season: str = Query("2024", description="Season year"),
    redis_service: RedisService = Depends(get_redis)
):
    """
    Get team statistics.

    Returns comprehensive statistics for the specified team and season.
    """
    try:
        # Check cache first
        cache_key = f"team_stats:{team_id}:{season}"
        cached_stats = await redis_service.get_json(cache_key)

        if cached_stats:
            return TeamStatsResponse(**cached_stats)

        # Get team data
        team_response = await get_team_by_id(team_id, redis_service)
        team = team_response.team

        # Mock stats data
        mock_stats = {
            "team_id": team_id,
            "team_name": team.name,
            "team_abbreviation": team.abbreviation,
            "stats": {
                "wins": 45,
                "losses": 20,
                "ties": 0,
                "points_for": 2156.5,
                "points_against": 1998.2,
                "win_percentage": 0.692,
                "season": season
            }
        }

        # Cache stats
        await redis_service.set_json(cache_key, mock_stats, expire=3600)  # 1 hour

        return TeamStatsResponse(**mock_stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team stats: {str(e)}"
        )


@router.get(
    "/popular",
    response_model=List[TeamResponse],
    status_code=status.HTTP_200_OK,
    summary="Get popular teams",
    description="Get list of most popular teams by follower count"
)
async def get_popular_teams(
    limit: int = Query(10, ge=1, le=50, description="Number of teams to return"),
    sport: Optional[Sport] = Query(None, description="Filter by sport"),
    redis_service: RedisService = Depends(get_redis)
):
    """
    Get popular teams.

    Returns teams sorted by popularity (follower count).
    """
    try:
        # Check cache first
        cache_key = f"popular_teams:{limit}:{sport}"
        cached_teams = await redis_service.get_json(cache_key)

        if cached_teams:
            return [TeamResponse(**team) for team in cached_teams]

        # Filter and sort teams
        teams = MOCK_TEAMS.copy()

        if sport:
            teams = [t for t in teams if t["sport"] == sport.value]

        # Sort by follower count
        teams.sort(key=lambda x: x["follower_count"], reverse=True)
        popular_teams = teams[:limit]

        # Cache results
        await redis_service.set_json(cache_key, popular_teams, expire=1800)  # 30 minutes

        return [TeamResponse(**team) for team in popular_teams]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve popular teams: {str(e)}"
        )