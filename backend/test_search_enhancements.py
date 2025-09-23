#!/usr/bin/env python3
"""
Comprehensive performance testing and validation for Phase 2A search enhancements

This script tests all the enhanced search functionality including:
- Basic search endpoint performance
- Enhanced search with metadata and highlighting
- Search suggestions/autocomplete
- API client functionality
- Edge cases and error handling
"""

import asyncio
import statistics
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass
import httpx

from api_client import create_client


@dataclass
class PerformanceResult:
    """Performance test result"""
    test_name: str
    response_times: List[float]
    success_count: int
    error_count: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    throughput: float  # requests per second


class SearchEnhancementTester:
    """Comprehensive tester for search enhancements"""

    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url
        self.results: List[PerformanceResult] = []

    async def test_basic_search_performance(self, iterations: int = 50) -> PerformanceResult:
        """Test basic search endpoint performance"""
        print(f"Testing basic search performance ({iterations} iterations)...")

        response_times = []
        success_count = 0
        error_count = 0

        test_queries = ["Chicago", "Lakers", "Patriots", "Chi", "L", "New York"]

        async with httpx.AsyncClient() as client:
            start_time = time.time()

            for i in range(iterations):
                query = test_queries[i % len(test_queries)]

                try:
                    request_start = time.time()
                    response = await client.get(
                        f"{self.base_url}/api/teams/search",
                        params={"query": query},
                        timeout=5.0
                    )
                    request_end = time.time()

                    if response.status_code == 200:
                        success_count += 1
                        response_times.append((request_end - request_start) * 1000)  # Convert to ms
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    print(f"Error in iteration {i}: {str(e)}")

            total_time = time.time() - start_time

        result = PerformanceResult(
            test_name="Basic Search",
            response_times=response_times,
            success_count=success_count,
            error_count=error_count,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 10 else 0,
            throughput=success_count / total_time if total_time > 0 else 0
        )

        self.results.append(result)
        return result

    async def test_enhanced_search_performance(self, iterations: int = 30) -> PerformanceResult:
        """Test enhanced search endpoint performance"""
        print(f"Testing enhanced search performance ({iterations} iterations)...")

        response_times = []
        success_count = 0
        error_count = 0

        test_queries = ["Chicago", "Lakers", "CHI", "New", "Patriots"]

        async with httpx.AsyncClient() as client:
            start_time = time.time()

            for i in range(iterations):
                query = test_queries[i % len(test_queries)]

                try:
                    request_start = time.time()
                    response = await client.get(
                        f"{self.base_url}/api/teams/search-enhanced",
                        params={"query": query},
                        timeout=10.0
                    )
                    request_end = time.time()

                    if response.status_code == 200:
                        success_count += 1
                        response_times.append((request_end - request_start) * 1000)

                        # Validate response structure
                        data = response.json()
                        assert "search_metadata" in data, "Missing search_metadata"
                        assert "items" in data, "Missing items"

                        if data["items"]:
                            item = data["items"][0]
                            assert "search_matches" in item, "Missing search_matches"
                            assert "relevance_score" in item, "Missing relevance_score"
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    print(f"Error in enhanced search iteration {i}: {str(e)}")

            total_time = time.time() - start_time

        result = PerformanceResult(
            test_name="Enhanced Search",
            response_times=response_times,
            success_count=success_count,
            error_count=error_count,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 10 else 0,
            throughput=success_count / total_time if total_time > 0 else 0
        )

        self.results.append(result)
        return result

    async def test_search_suggestions_performance(self, iterations: int = 40) -> PerformanceResult:
        """Test search suggestions endpoint performance"""
        print(f"Testing search suggestions performance ({iterations} iterations)...")

        response_times = []
        success_count = 0
        error_count = 0

        test_queries = ["C", "Ch", "Chi", "L", "La", "N", "Ne", "P", "Pa", "Pat"]

        async with httpx.AsyncClient() as client:
            start_time = time.time()

            for i in range(iterations):
                query = test_queries[i % len(test_queries)]

                try:
                    request_start = time.time()
                    response = await client.get(
                        f"{self.base_url}/api/teams/search-suggestions",
                        params={"query": query},
                        timeout=5.0
                    )
                    request_end = time.time()

                    if response.status_code == 200:
                        success_count += 1
                        response_times.append((request_end - request_start) * 1000)

                        # Validate response structure
                        data = response.json()
                        assert "suggestions" in data, "Missing suggestions"
                        assert "response_time_ms" in data, "Missing response_time_ms"

                        if data["suggestions"]:
                            suggestion = data["suggestions"][0]
                            assert "suggestion" in suggestion, "Missing suggestion text"
                            assert "type" in suggestion, "Missing suggestion type"
                            assert "team_count" in suggestion, "Missing team_count"
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    print(f"Error in suggestions iteration {i}: {str(e)}")

            total_time = time.time() - start_time

        result = PerformanceResult(
            test_name="Search Suggestions",
            response_times=response_times,
            success_count=success_count,
            error_count=error_count,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 10 else 0,
            throughput=success_count / total_time if total_time > 0 else 0
        )

        self.results.append(result)
        return result

    async def test_api_client_functionality(self) -> None:
        """Test API client functionality and features"""
        print("Testing API client functionality...")

        async with create_client() as client:
            # Test enhanced search
            print("  - Testing enhanced search...")
            results = await client.search_teams_enhanced(query="Chicago")
            assert results["total"] > 0, "No results found for Chicago"
            assert "search_metadata" in results, "Missing search metadata"

            # Test search highlighting
            if results["items"]:
                team = results["items"][0]
                assert "search_matches" in team, "Missing search matches"
                assert "relevance_score" in team, "Missing relevance score"

            # Test search suggestions
            print("  - Testing search suggestions...")
            suggestions = await client.get_search_suggestions("Chi")
            assert len(suggestions["suggestions"]) > 0, "No suggestions found"

            # Test caching
            print("  - Testing caching...")
            start_time = time.time()
            cached_results = await client.search_teams_enhanced(query="Chicago")
            cached_time = time.time() - start_time

            # Second call should be faster due to caching
            assert cached_time < 0.1, f"Cached request too slow: {cached_time:.3f}s"

            # Test debounced search
            print("  - Testing debounced search...")
            debounced_result = await client.search_teams_debounced("Lakers")
            assert debounced_result is not None, "Debounced search failed"

            print("  ✅ API client tests passed!")

    async def test_edge_cases(self) -> None:
        """Test edge cases and error handling"""
        print("Testing edge cases...")

        async with httpx.AsyncClient() as client:
            # Test empty query
            print("  - Testing empty query...")
            response = await client.get(f"{self.base_url}/api/teams/search")
            assert response.status_code == 200, "Empty query should work"

            # Test very long query
            print("  - Testing long query...")
            long_query = "a" * 100
            response = await client.get(
                f"{self.base_url}/api/teams/search",
                params={"query": long_query}
            )
            assert response.status_code == 200, "Long query should work"

            # Test special characters
            print("  - Testing special characters...")
            special_query = "Chicago's & Bears!"
            response = await client.get(
                f"{self.base_url}/api/teams/search",
                params={"query": special_query}
            )
            assert response.status_code == 200, "Special characters should work"

            # Test invalid UUIDs
            print("  - Testing invalid UUID...")
            response = await client.get(
                f"{self.base_url}/api/teams/search",
                params={"sport_id": "invalid-uuid"}
            )
            assert response.status_code == 422, "Invalid UUID should return 422"

            # Test suggestions with too short query
            print("  - Testing short suggestions query...")
            response = await client.get(
                f"{self.base_url}/api/teams/search-suggestions",
                params={"query": ""}
            )
            assert response.status_code == 422, "Empty suggestions query should return 422"

            print("  ✅ Edge case tests passed!")

    async def test_load_performance(self, concurrent_requests: int = 20) -> None:
        """Test performance under load"""
        print(f"Testing load performance ({concurrent_requests} concurrent requests)...")

        async def make_request(client: httpx.AsyncClient, query: str) -> float:
            start_time = time.time()
            response = await client.get(
                f"{self.base_url}/api/teams/search-enhanced",
                params={"query": query}
            )
            end_time = time.time()

            if response.status_code != 200:
                raise Exception(f"Request failed with status {response.status_code}")

            return (end_time - start_time) * 1000

        queries = ["Chicago", "Lakers", "Patriots", "CHI", "LAL"] * (concurrent_requests // 5 + 1)
        queries = queries[:concurrent_requests]

        async with httpx.AsyncClient() as client:
            start_time = time.time()

            tasks = [make_request(client, query) for query in queries]
            response_times = await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start_time

        # Filter out exceptions
        valid_times = [t for t in response_times if isinstance(t, float)]
        error_count = len(response_times) - len(valid_times)

        if valid_times:
            avg_time = statistics.mean(valid_times)
            max_time = max(valid_times)
            throughput = len(valid_times) / total_time

            print(f"  Load test results:")
            print(f"    Successful requests: {len(valid_times)}")
            print(f"    Failed requests: {error_count}")
            print(f"    Average response time: {avg_time:.1f}ms")
            print(f"    Max response time: {max_time:.1f}ms")
            print(f"    Throughput: {throughput:.1f} req/s")

            # Assert performance requirements
            assert avg_time < 500, f"Average response time too high: {avg_time:.1f}ms"
            assert error_count == 0, f"Too many errors: {error_count}"

            print("  ✅ Load test passed!")

    def print_performance_summary(self) -> None:
        """Print comprehensive performance summary"""
        print("\n" + "="*80)
        print("PERFORMANCE SUMMARY")
        print("="*80)

        for result in self.results:
            print(f"\n{result.test_name}:")
            print(f"  Success Rate: {result.success_count}/{result.success_count + result.error_count} "
                  f"({100 * result.success_count / (result.success_count + result.error_count):.1f}%)")
            print(f"  Average Response Time: {result.avg_response_time:.1f}ms")
            print(f"  P95 Response Time: {result.p95_response_time:.1f}ms")
            print(f"  Min/Max Response Time: {result.min_response_time:.1f}ms / {result.max_response_time:.1f}ms")
            print(f"  Throughput: {result.throughput:.1f} req/s")

        print("\n" + "="*80)
        print("QUALITY GATES")
        print("="*80)

        all_passed = True

        # Check performance requirements
        for result in self.results:
            if result.test_name == "Basic Search":
                target = 200  # ms
                if result.p95_response_time > target:
                    print(f"❌ Basic Search P95 ({result.p95_response_time:.1f}ms) > {target}ms")
                    all_passed = False
                else:
                    print(f"✅ Basic Search P95 ({result.p95_response_time:.1f}ms) ≤ {target}ms")

            elif result.test_name == "Enhanced Search":
                target = 400  # ms (higher due to additional processing)
                if result.p95_response_time > target:
                    print(f"❌ Enhanced Search P95 ({result.p95_response_time:.1f}ms) > {target}ms")
                    all_passed = False
                else:
                    print(f"✅ Enhanced Search P95 ({result.p95_response_time:.1f}ms) ≤ {target}ms")

            elif result.test_name == "Search Suggestions":
                target = 100  # ms (should be very fast)
                if result.p95_response_time > target:
                    print(f"❌ Search Suggestions P95 ({result.p95_response_time:.1f}ms) > {target}ms")
                    all_passed = False
                else:
                    print(f"✅ Search Suggestions P95 ({result.p95_response_time:.1f}ms) ≤ {target}ms")

        print(f"\n{'✅ ALL QUALITY GATES PASSED!' if all_passed else '❌ SOME QUALITY GATES FAILED!'}")

    async def run_all_tests(self) -> None:
        """Run all performance tests"""
        print("Starting comprehensive search enhancement tests...")
        print("="*80)

        try:
            # Performance tests
            await self.test_basic_search_performance()
            await self.test_enhanced_search_performance()
            await self.test_search_suggestions_performance()

            # Functionality tests
            await self.test_api_client_functionality()
            await self.test_edge_cases()
            await self.test_load_performance()

            # Print summary
            self.print_performance_summary()

            print("\n🎉 All tests completed successfully!")

        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            raise


async def main():
    """Main test runner"""
    tester = SearchEnhancementTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())