"""
Typed API client for Corner League Media Backend

This module provides a fully typed Python client for the backend API,
with support for enhanced search functionality, caching, and error handling.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel, ValidationError

# Import the schemas for type safety
try:
    from backend.api.schemas.sports import (
        TeamsPaginatedResponse,
        EnhancedTeamsPaginatedResponse,
        SearchSuggestionsResponse,
        TeamSearchParams,
        SportResponse,
        LeagueResponse
    )
except ImportError:
    # Fallback schemas for standalone usage
    from typing import Any
    TeamsPaginatedResponse = Dict[str, Any]
    EnhancedTeamsPaginatedResponse = Dict[str, Any]
    SearchSuggestionsResponse = Dict[str, Any]
    TeamSearchParams = Dict[str, Any]
    SportResponse = Dict[str, Any]
    LeagueResponse = Dict[str, Any]


class ApiClientError(Exception):
    """Base exception for API client errors"""
    pass


class ApiClientTimeoutError(ApiClientError):
    """Raised when API request times out"""
    pass


class ApiClientValidationError(ApiClientError):
    """Raised when API response validation fails"""
    pass


class SearchCache:
    """Simple in-memory cache for search results"""

    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key from endpoint and parameters"""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
        return f"{endpoint}?{param_str}"

    def get(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached result if still valid"""
        key = self._get_cache_key(endpoint, params)
        if key in self.cache:
            cached_item = self.cache[key]
            if datetime.utcnow() < cached_item['expires']:
                return cached_item['data']
            else:
                del self.cache[key]
        return None

    def set(self, endpoint: str, params: Dict[str, Any], data: Any) -> None:
        """Cache the result with TTL"""
        key = self._get_cache_key(endpoint, params)
        self.cache[key] = {
            'data': data,
            'expires': datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
        }

    def clear(self) -> None:
        """Clear all cached results"""
        self.cache.clear()


class CornerLeagueApiClient:
    """
    Typed API client for Corner League Media Backend

    Features:
    - Fully typed methods with Pydantic validation
    - Request caching for performance
    - Exponential backoff retry logic
    - Comprehensive error handling
    - Search debouncing support
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8001",
        timeout: float = 30.0,
        cache_ttl: int = 300,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache = SearchCache(ttl_seconds=cache_ttl)

        # Create async HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )

        # Debouncing support
        self._last_search_task: Optional[asyncio.Task] = None
        self._search_debounce_delay = 0.3  # 300ms

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling
        """
        url = f"{self.base_url}{endpoint}"

        # Filter out None and empty string values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None and v != ""}

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt == self.max_retries:
                    raise ApiClientTimeoutError(f"Request to {endpoint} timed out after {self.max_retries} retries")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500 or attempt == self.max_retries:
                    # Don't retry client errors or if we've exhausted retries
                    error_detail = "Unknown error"
                    try:
                        error_data = e.response.json()
                        error_detail = error_data.get('detail', error_data.get('message', str(e)))
                    except:
                        error_detail = str(e)
                    raise ApiClientError(f"API error ({e.response.status_code}): {error_detail}")
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                if attempt == self.max_retries:
                    raise ApiClientError(f"Unexpected error: {str(e)}")
                await asyncio.sleep(2 ** attempt)

    # Team Search Methods

    async def search_teams(
        self,
        query: Optional[str] = None,
        sport_id: Optional[UUID] = None,
        league_id: Optional[UUID] = None,
        market: Optional[str] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True
    ) -> TeamsPaginatedResponse:
        """
        Search teams with basic pagination

        Args:
            query: Search query for team name or market
            sport_id: Filter by sport UUID
            league_id: Filter by league UUID
            market: Filter by market/city
            is_active: Filter by active status
            page: Page number (1-indexed)
            page_size: Number of items per page
            use_cache: Whether to use cached results

        Returns:
            Paginated team search results
        """
        params = {
            "query": query,
            "sport_id": str(sport_id) if sport_id else None,
            "league_id": str(league_id) if league_id else None,
            "market": market,
            "is_active": is_active,
            "page": page,
            "page_size": page_size
        }

        # Check cache first
        if use_cache:
            cached_result = self.cache.get("/api/teams/search", params)
            if cached_result:
                if hasattr(TeamsPaginatedResponse, 'model_validate') and not isinstance(TeamsPaginatedResponse, type(Dict)):
                    return TeamsPaginatedResponse(**cached_result)
                else:
                    return cached_result

        # Make API request
        data = await self._request("GET", "/api/teams/search", params=params)

        # Validate and parse response
        try:
            if hasattr(TeamsPaginatedResponse, 'model_validate') and not isinstance(TeamsPaginatedResponse, type(Dict)):
                result = TeamsPaginatedResponse(**data)
            else:
                result = data  # Fallback to raw dict
        except (ValidationError, TypeError) as e:
            raise ApiClientValidationError(f"Invalid response format: {str(e)}")

        # Cache the result
        if use_cache:
            self.cache.set("/api/teams/search", params, data)

        return result

    async def search_teams_enhanced(
        self,
        query: Optional[str] = None,
        sport_id: Optional[UUID] = None,
        league_id: Optional[UUID] = None,
        market: Optional[str] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20,
        use_cache: bool = True
    ) -> EnhancedTeamsPaginatedResponse:
        """
        Enhanced team search with highlighting, relevance scoring, and metadata

        Args:
            query: Search query for team name or market
            sport_id: Filter by sport UUID
            league_id: Filter by league UUID
            market: Filter by market/city
            is_active: Filter by active status
            page: Page number (1-indexed)
            page_size: Number of items per page
            use_cache: Whether to use cached results

        Returns:
            Enhanced paginated team search results with metadata
        """
        params = {
            "query": query,
            "sport_id": str(sport_id) if sport_id else None,
            "league_id": str(league_id) if league_id else None,
            "market": market,
            "is_active": is_active,
            "page": page,
            "page_size": page_size
        }

        # Check cache first
        if use_cache:
            cached_result = self.cache.get("/api/teams/search-enhanced", params)
            if cached_result:
                if hasattr(EnhancedTeamsPaginatedResponse, 'model_validate') and not isinstance(EnhancedTeamsPaginatedResponse, type(Dict)):
                    return EnhancedTeamsPaginatedResponse(**cached_result)
                else:
                    return cached_result

        # Make API request
        data = await self._request("GET", "/api/teams/search-enhanced", params=params)

        # Validate and parse response
        try:
            if hasattr(EnhancedTeamsPaginatedResponse, 'model_validate') and not isinstance(EnhancedTeamsPaginatedResponse, type(Dict)):
                result = EnhancedTeamsPaginatedResponse(**data)
            else:
                result = data  # Fallback to raw dict
        except (ValidationError, TypeError) as e:
            raise ApiClientValidationError(f"Invalid response format: {str(e)}")

        # Cache the result
        if use_cache:
            self.cache.set("/api/teams/search-enhanced", params, data)

        return result

    async def get_search_suggestions(
        self,
        query: str,
        limit: int = 10,
        use_cache: bool = True
    ) -> SearchSuggestionsResponse:
        """
        Get search suggestions/autocomplete for team search

        Args:
            query: Search query (minimum 1 character)
            limit: Maximum number of suggestions (1-20)
            use_cache: Whether to use cached results

        Returns:
            Search suggestions with preview teams
        """
        if len(query) < 1:
            raise ValueError("Query must be at least 1 character long")

        params = {"query": query, "limit": limit}

        # Check cache first
        if use_cache:
            cached_result = self.cache.get("/api/teams/search-suggestions", params)
            if cached_result:
                if hasattr(SearchSuggestionsResponse, 'model_validate') and not isinstance(SearchSuggestionsResponse, type(Dict)):
                    return SearchSuggestionsResponse(**cached_result)
                else:
                    return cached_result

        # Make API request
        data = await self._request("GET", "/api/teams/search-suggestions", params=params)

        # Validate and parse response
        try:
            if hasattr(SearchSuggestionsResponse, 'model_validate') and not isinstance(SearchSuggestionsResponse, type(Dict)):
                result = SearchSuggestionsResponse(**data)
            else:
                result = data  # Fallback to raw dict
        except (ValidationError, TypeError) as e:
            raise ApiClientValidationError(f"Invalid response format: {str(e)}")

        # Cache the result
        if use_cache:
            self.cache.set("/api/teams/search-suggestions", params, data)

        return result

    async def search_teams_debounced(
        self,
        query: Optional[str],
        **kwargs
    ) -> Optional[EnhancedTeamsPaginatedResponse]:
        """
        Debounced team search - cancels previous search if called again quickly

        Args:
            query: Search query
            **kwargs: Other search parameters

        Returns:
            Search results or None if cancelled by newer search
        """
        # Cancel previous search task if it exists
        if self._last_search_task and not self._last_search_task.done():
            self._last_search_task.cancel()

        # Create new search task with debounce delay
        async def debounced_search():
            await asyncio.sleep(self._search_debounce_delay)
            return await self.search_teams_enhanced(query=query, **kwargs)

        self._last_search_task = asyncio.create_task(debounced_search())

        try:
            return await self._last_search_task
        except asyncio.CancelledError:
            return None

    # Sports and Leagues Methods

    async def get_sports(
        self,
        include_leagues: bool = False,
        include_inactive: bool = False,
        use_cache: bool = True
    ) -> List[SportResponse]:
        """
        Get all sports

        Args:
            include_leagues: Whether to include leagues for each sport
            include_inactive: Whether to include inactive sports
            use_cache: Whether to use cached results

        Returns:
            List of sports
        """
        params = {
            "include_leagues": include_leagues,
            "include_inactive": include_inactive
        }

        # Check cache first
        if use_cache:
            cached_result = self.cache.get("/api/sports", params)
            if cached_result:
                if hasattr(SportResponse, 'model_validate') and not isinstance(SportResponse, type(Dict)):
                    return [SportResponse(**sport) for sport in cached_result]
                else:
                    return cached_result

        # Make API request
        data = await self._request("GET", "/api/sports", params=params)

        # Validate and parse response
        try:
            if hasattr(SportResponse, 'model_validate') and not isinstance(SportResponse, type(Dict)):
                result = [SportResponse(**sport) for sport in data]
            else:
                result = data  # Fallback to raw list
        except (ValidationError, TypeError) as e:
            raise ApiClientValidationError(f"Invalid response format: {str(e)}")

        # Cache the result
        if use_cache:
            self.cache.set("/api/sports", params, data)

        return result

    # Utility Methods

    def clear_cache(self) -> None:
        """Clear all cached API results"""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cached_items": len(self.cache.cache),
            "cache_ttl_seconds": self.cache.ttl_seconds
        }


# Convenience functions for synchronous usage

def create_client(**kwargs) -> CornerLeagueApiClient:
    """Create a new API client instance"""
    return CornerLeagueApiClient(**kwargs)


async def quick_search(query: str, **kwargs) -> EnhancedTeamsPaginatedResponse:
    """Quick team search with automatic client management"""
    async with create_client() as client:
        return await client.search_teams_enhanced(query=query, **kwargs)


async def quick_suggestions(query: str, **kwargs) -> SearchSuggestionsResponse:
    """Quick search suggestions with automatic client management"""
    async with create_client() as client:
        return await client.get_search_suggestions(query=query, **kwargs)


# Example usage
if __name__ == "__main__":
    async def example_usage():
        """Example of how to use the API client"""

        # Create client
        async with create_client() as client:
            # Enhanced search with highlighting
            results = await client.search_teams_enhanced(query="Chicago")
            print(f"Found {results.total} teams in {results.search_metadata.response_time_ms:.1f}ms")

            for team in results.items[:3]:
                print(f"- {team.display_name} (relevance: {team.relevance_score})")
                for match in team.search_matches:
                    print(f"  {match.field}: {match.highlighted}")

            # Get search suggestions
            suggestions = await client.get_search_suggestions("Chi")
            print(f"\nSuggestions for 'Chi':")
            for suggestion in suggestions.suggestions[:5]:
                print(f"- {suggestion.suggestion} ({suggestion.type}) - {suggestion.team_count} teams")

    # Run example
    asyncio.run(example_usage())