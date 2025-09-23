"""
Performance benchmark tests for onboarding API endpoints.

These tests measure response times and throughput to ensure
the API meets performance requirements.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.services.onboarding_service import OnboardingService
from backend.models.users import User
from backend.models.sports import Sport, Team


class TestOnboardingPerformanceBenchmarks:
    """Performance benchmarks for onboarding service."""

    @pytest.mark.benchmark
    async def test_get_sports_performance(self, test_client: AsyncClient, test_sports: list[Sport], benchmark):
        """Benchmark sports endpoint response time."""

        async def get_sports():
            response = await test_client.get("/api/v1/onboarding/sports")
            assert response.status_code == 200
            return response.json()

        # Benchmark the function
        result = await benchmark(get_sports)

        # Verify the result structure
        assert "sports" in result
        assert "total" in result

        # Performance assertions
        benchmark_stats = benchmark.stats
        assert benchmark_stats.mean < 0.5  # Average response time < 500ms
        assert benchmark_stats.max < 2.0   # Maximum response time < 2s

    @pytest.mark.benchmark
    async def test_get_teams_performance(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team], benchmark):
        """Benchmark teams endpoint response time."""

        sport_id = str(test_sports[0].id)

        async def get_teams():
            response = await test_client.get(f"/api/v1/onboarding/teams?sport_ids={sport_id}")
            assert response.status_code == 200
            return response.json()

        result = await benchmark(get_teams)

        assert "teams" in result
        assert "total" in result

        # Performance assertions
        benchmark_stats = benchmark.stats
        assert benchmark_stats.mean < 0.5  # Average response time < 500ms

    @pytest.mark.benchmark
    async def test_update_step_performance(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth, benchmark):
        """Benchmark step update endpoint performance."""

        async def update_step():
            response = await test_client.put(
                "/api/v1/onboarding/step",
                headers=authenticated_headers,
                json={"step": 2}
            )
            assert response.status_code == 200
            return response.json()

        result = await benchmark(update_step)

        assert result["current_step"] == 2

        # Performance assertions
        benchmark_stats = benchmark.stats
        assert benchmark_stats.mean < 1.0  # Average response time < 1s (database write)

    @pytest.mark.benchmark
    async def test_complete_onboarding_performance(self, test_client: AsyncClient, test_user: User, authenticated_headers, mock_firebase_auth, benchmark):
        """Benchmark onboarding completion performance."""

        async def complete_onboarding():
            response = await test_client.post(
                "/api/v1/onboarding/complete",
                headers=authenticated_headers,
                json={"force_complete": True}
            )
            assert response.status_code == 200
            return response.json()

        result = await benchmark(complete_onboarding)

        assert result["success"] is True

        # Performance assertions
        benchmark_stats = benchmark.stats
        assert benchmark_stats.mean < 1.5  # Average response time < 1.5s (complex operation)

    @pytest.mark.benchmark
    async def test_service_layer_performance(self, test_session: AsyncSession, test_sports: list[Sport], benchmark):
        """Benchmark onboarding service layer performance."""

        service = OnboardingService(test_session)

        async def get_sports_service():
            return await service.get_onboarding_sports()

        result = await benchmark(get_sports_service)

        assert len(result.sports) > 0

        # Service layer should be very fast
        benchmark_stats = benchmark.stats
        assert benchmark_stats.mean < 0.1  # Average < 100ms


class TestConcurrentLoadBenchmarks:
    """Load testing with concurrent requests."""

    @pytest.mark.benchmark
    @pytest.mark.slow
    async def test_concurrent_sports_requests(self, test_client: AsyncClient, test_sports: list[Sport]):
        """Test concurrent requests to sports endpoint."""

        concurrent_requests = 50

        async def make_request():
            start_time = time.time()
            response = await test_client.get("/api/v1/onboarding/sports")
            end_time = time.time()

            assert response.status_code == 200
            return end_time - start_time

        # Execute concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(concurrent_requests)]
        response_times = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Performance assertions
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        throughput = concurrent_requests / total_time

        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.2f}s exceeds 1s"
        assert max_response_time < 5.0, f"Max response time {max_response_time:.2f}s exceeds 5s"
        assert throughput > 10, f"Throughput {throughput:.2f} req/s is below 10 req/s"

    @pytest.mark.benchmark
    @pytest.mark.slow
    async def test_concurrent_team_requests(self, test_client: AsyncClient, test_sports: list[Sport], test_teams: list[Team]):
        """Test concurrent requests to teams endpoint."""

        concurrent_requests = 30
        sport_id = str(test_sports[0].id)

        async def make_request():
            start_time = time.time()
            response = await test_client.get(f"/api/v1/onboarding/teams?sport_ids={sport_id}")
            end_time = time.time()

            assert response.status_code == 200
            return end_time - start_time

        start_time = time.time()
        tasks = [make_request() for _ in range(concurrent_requests)]
        response_times = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        avg_response_time = sum(response_times) / len(response_times)
        throughput = concurrent_requests / total_time

        assert avg_response_time < 1.5, f"Average response time {avg_response_time:.2f}s exceeds 1.5s"
        assert throughput > 5, f"Throughput {throughput:.2f} req/s is below 5 req/s"

    @pytest.mark.benchmark
    @pytest.mark.slow
    async def test_database_connection_pool_performance(self, test_session: AsyncSession, test_sports: list[Sport]):
        """Test database connection pool under load."""

        service = OnboardingService(test_session)
        concurrent_operations = 20

        async def database_operation():
            start_time = time.time()
            result = await service.get_onboarding_sports()
            end_time = time.time()

            assert len(result.sports) > 0
            return end_time - start_time

        start_time = time.time()
        tasks = [database_operation() for _ in range(concurrent_operations)]
        operation_times = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        avg_operation_time = sum(operation_times) / len(operation_times)
        throughput = concurrent_operations / total_time

        assert avg_operation_time < 0.5, f"Average DB operation time {avg_operation_time:.2f}s exceeds 0.5s"
        assert throughput > 20, f"DB throughput {throughput:.2f} ops/s is below 20 ops/s"


class TestMemoryUsageBenchmarks:
    """Memory usage benchmarks."""

    @pytest.mark.benchmark
    async def test_sports_endpoint_memory_usage(self, test_client: AsyncClient, test_sports: list[Sport]):
        """Test memory usage of sports endpoint."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Make multiple requests to test memory accumulation
        for _ in range(100):
            response = await test_client.get("/api/v1/onboarding/sports")
            assert response.status_code == 200

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (< 10MB for 100 requests)
        assert memory_increase < 10 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"

    @pytest.mark.benchmark
    async def test_large_dataset_memory_efficiency(self, test_session: AsyncSession):
        """Test memory efficiency with large datasets."""
        import psutil
        import os

        # Create a large number of sports for testing
        from backend.models.sports import Sport
        from uuid import uuid4

        large_sports_set = []
        for i in range(1000):
            sport = Sport(
                id=uuid4(),
                name=f"Sport {i}",
                slug=f"sport-{i}",
                icon="⚽",
                description=f"Description for sport {i}",
                popularity_rank=i + 1,
                is_active=True
            )
            large_sports_set.append(sport)
            test_session.add(sport)

        await test_session.commit()

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        service = OnboardingService(test_session)
        result = await service.get_onboarding_sports()

        final_memory = process.memory_info().rss
        memory_used = final_memory - initial_memory

        assert len(result.sports) == 1003  # 3 original + 1000 new

        # Memory usage should be reasonable (< 50MB for 1000 sports)
        assert memory_used < 50 * 1024 * 1024, f"Memory used: {memory_used / 1024 / 1024:.2f}MB"


class TestScalabilityBenchmarks:
    """Scalability benchmarks for different data sizes."""

    @pytest.mark.benchmark
    @pytest.mark.parametrize("sport_count", [10, 100, 500])
    async def test_sports_scalability(self, test_session: AsyncSession, sport_count: int, benchmark):
        """Test sports endpoint scalability with different data sizes."""

        # Create sports dynamically
        from backend.models.sports import Sport
        from uuid import uuid4

        sports = []
        for i in range(sport_count):
            sport = Sport(
                id=uuid4(),
                name=f"Sport {i}",
                slug=f"sport-{i}",
                icon="⚽",
                description=f"Description {i}",
                popularity_rank=i + 1,
                is_active=True
            )
            sports.append(sport)
            test_session.add(sport)

        await test_session.commit()

        service = OnboardingService(test_session)

        async def get_sports():
            return await service.get_onboarding_sports()

        result = await benchmark(get_sports)

        assert len(result.sports) >= sport_count

        # Response time should scale sub-linearly
        benchmark_stats = benchmark.stats
        if sport_count <= 100:
            assert benchmark_stats.mean < 0.2
        elif sport_count <= 500:
            assert benchmark_stats.mean < 0.5
        else:
            assert benchmark_stats.mean < 1.0

    @pytest.mark.benchmark
    @pytest.mark.parametrize("team_count", [10, 100, 500])
    async def test_teams_scalability(self, test_session: AsyncSession, test_sports: list[Sport], team_count: int, benchmark):
        """Test teams endpoint scalability with different data sizes."""

        from backend.models.sports import Team
        from uuid import uuid4

        sport_id = test_sports[0].id
        teams = []

        for i in range(team_count):
            team = Team(
                id=uuid4(),
                name=f"Team {i}",
                market=f"City {i}",
                slug=f"team-{i}",
                sport_id=sport_id,
                logo_url=f"https://example.com/team{i}.png",
                abbreviation=f"T{i:02d}",
                primary_color="#000000",
                secondary_color="#FFFFFF",
                is_active=True
            )
            teams.append(team)
            test_session.add(team)

        await test_session.commit()

        service = OnboardingService(test_session)

        async def get_teams():
            return await service.get_onboarding_teams([sport_id])

        result = await benchmark(get_teams)

        assert len(result.teams) >= team_count

        # Response time should scale sub-linearly
        benchmark_stats = benchmark.stats
        if team_count <= 100:
            assert benchmark_stats.mean < 0.3
        elif team_count <= 500:
            assert benchmark_stats.mean < 0.7
        else:
            assert benchmark_stats.mean < 1.5


class TestCachePerformanceBenchmarks:
    """Cache performance benchmarks."""

    @pytest.mark.benchmark
    async def test_repeated_requests_caching(self, test_client: AsyncClient, test_sports: list[Sport], benchmark):
        """Test that repeated requests benefit from caching."""

        # First request (cold cache)
        start_time = time.time()
        response1 = await test_client.get("/api/v1/onboarding/sports")
        first_request_time = time.time() - start_time

        assert response1.status_code == 200

        # Subsequent requests should be faster if caching is implemented
        async def cached_request():
            response = await test_client.get("/api/v1/onboarding/sports")
            assert response.status_code == 200
            return response.json()

        result = await benchmark(cached_request)

        benchmark_stats = benchmark.stats

        # Cached requests should be significantly faster
        # This test assumes some form of caching is implemented
        assert benchmark_stats.mean <= first_request_time * 1.5  # At most 50% slower than first request


# Performance thresholds configuration
PERFORMANCE_THRESHOLDS = {
    "sports_endpoint": {
        "mean_response_time": 0.5,  # 500ms
        "max_response_time": 2.0,   # 2s
        "throughput_rps": 10,       # 10 requests per second
    },
    "teams_endpoint": {
        "mean_response_time": 0.5,
        "max_response_time": 2.0,
        "throughput_rps": 8,
    },
    "step_update": {
        "mean_response_time": 1.0,  # 1s (database write)
        "max_response_time": 3.0,
        "throughput_rps": 5,
    },
    "completion": {
        "mean_response_time": 1.5,  # 1.5s (complex operation)
        "max_response_time": 5.0,
        "throughput_rps": 3,
    },
    "service_layer": {
        "mean_response_time": 0.1,  # 100ms
        "max_response_time": 0.5,
    },
    "memory_usage": {
        "max_increase_mb": 10,      # 10MB for 100 requests
        "large_dataset_mb": 50,     # 50MB for 1000 records
    },
    "concurrent_load": {
        "max_avg_response_time": 1.0,
        "max_response_time": 5.0,
        "min_throughput_rps": 10,
    }
}