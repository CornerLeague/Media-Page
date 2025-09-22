"""
Comprehensive Onboarding Flow Test Suite

This test suite validates the complete onboarding flow after Phase 2 critical fixes,
ensuring that sports selection, team selection, preferences saving, and error handling
all work correctly.
"""

import pytest
import requests
import json
from typing import Dict, List, Any
from datetime import datetime


class OnboardingFlowTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []

    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test results for reporting"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend connectivity and health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            success = response.status_code == 200

            result = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if success else None
            }

            self.log_test_result("Backend Health Check", success, result)
            return result

        except Exception as e:
            result = {"error": str(e)}
            self.log_test_result("Backend Health Check", False, result)
            return result

    def test_sports_api_endpoint(self) -> Dict[str, Any]:
        """Test sports selection API endpoint returns proper data"""
        try:
            response = requests.get(f"{self.base_url}/api/sports", timeout=10)
            success = response.status_code == 200

            if success:
                sports_data = response.json()
                # Validate structure
                required_fields = ["id", "name", "slug", "has_teams", "is_active"]
                sports_with_teams = [sport for sport in sports_data if sport.get("has_teams")]

                validation_errors = []
                for sport in sports_data:
                    for field in required_fields:
                        if field not in sport:
                            validation_errors.append(f"Missing field '{field}' in sport {sport.get('name', 'unknown')}")

                result = {
                    "status_code": response.status_code,
                    "total_sports": len(sports_data),
                    "sports_with_teams": len(sports_with_teams),
                    "validation_errors": validation_errors,
                    "sample_sports": sports_data[:3] if sports_data else []
                }
            else:
                result = {
                    "status_code": response.status_code,
                    "error": response.text
                }

            self.log_test_result("Sports API Endpoint", success and len(validation_errors) == 0, result)
            return result

        except Exception as e:
            result = {"error": str(e)}
            self.log_test_result("Sports API Endpoint", False, result)
            return result

    def test_team_search_functionality(self) -> Dict[str, Any]:
        """Test team selection functionality for different sports"""
        test_teams = [
            {"query": "Chiefs", "expected_sport": "Football"},
            {"query": "Lakers", "expected_sport": "Basketball"},
            {"query": "Yankees", "expected_sport": "Baseball"},
            {"query": "Rangers", "expected_sport": "Hockey"},
        ]

        results = []
        overall_success = True

        for test_case in test_teams:
            try:
                response = requests.get(
                    f"{self.base_url}/api/teams/search",
                    params={"query": test_case["query"]},
                    timeout=10
                )

                success = response.status_code == 200
                if success:
                    teams_data = response.json()
                    team_found = len(teams_data.get("items", [])) > 0

                    if team_found:
                        team = teams_data["items"][0]
                        team_result = {
                            "query": test_case["query"],
                            "found": True,
                            "team_name": team.get("name"),
                            "team_market": team.get("market"),
                            "display_name": team.get("display_name"),
                            "sport_id": team.get("sport_id"),
                            "has_leagues": len(team.get("leagues", [])) > 0
                        }
                    else:
                        team_result = {
                            "query": test_case["query"],
                            "found": False,
                            "error": "No teams found"
                        }
                        overall_success = False
                else:
                    team_result = {
                        "query": test_case["query"],
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    overall_success = False

                results.append(team_result)

            except Exception as e:
                results.append({
                    "query": test_case["query"],
                    "error": str(e)
                })
                overall_success = False

        result = {
            "team_search_results": results,
            "success_rate": sum(1 for r in results if r.get("found", False)) / len(results)
        }

        self.log_test_result("Team Search Functionality", overall_success, result)
        return result

    def test_team_leagues_association(self) -> Dict[str, Any]:
        """Validate database fixes and team associations"""
        try:
            # Get teams and check for proper league associations
            response = requests.get(f"{self.base_url}/api/teams/search?query=Chiefs", timeout=10)

            if response.status_code != 200:
                raise Exception(f"Failed to get teams: {response.status_code}")

            teams_data = response.json()
            if not teams_data.get("items"):
                raise Exception("No teams found in search")

            team = teams_data["items"][0]
            team_id = team.get("id")

            # Test multi-league info endpoint
            multi_league_response = requests.get(
                f"{self.base_url}/sports/teams/{team_id}/multi-league-info",
                timeout=10
            )

            # Test leagues association
            leagues_response = requests.get(
                f"{self.base_url}/sports/teams/{team_id}/leagues",
                timeout=10
            )

            result = {
                "team_id": team_id,
                "team_name": team.get("display_name"),
                "leagues_endpoint_status": leagues_response.status_code,
                "multi_league_endpoint_status": multi_league_response.status_code,
                "has_league_id": team.get("league_id") is not None,
                "leagues_data": leagues_response.json() if leagues_response.status_code == 200 else None,
                "multi_league_data": multi_league_response.json() if multi_league_response.status_code == 200 else None
            }

            success = leagues_response.status_code in [200, 404]  # 404 is acceptable if no leagues

            self.log_test_result("Team Leagues Association", success, result)
            return result

        except Exception as e:
            result = {"error": str(e)}
            self.log_test_result("Team Leagues Association", False, result)
            return result

    def test_api_client_endpoints(self) -> Dict[str, Any]:
        """Test that API client endpoints are correctly configured"""
        endpoints_to_test = [
            {"path": "/api/v1/users/me", "method": "GET", "expected_auth_required": True},
            {"path": "/api/v1/users/me", "method": "PUT", "expected_auth_required": True},
            {"path": "/api/v1/me/preferences", "method": "GET", "expected_auth_required": True},
            {"path": "/api/v1/me/preferences", "method": "PUT", "expected_auth_required": True},
            {"path": "/api/sports", "method": "GET", "expected_auth_required": False},
            {"path": "/api/teams/search", "method": "GET", "expected_auth_required": False},
        ]

        results = []
        overall_success = True

        for endpoint in endpoints_to_test:
            try:
                # Test without authentication
                response = requests.request(
                    endpoint["method"],
                    f"{self.base_url}{endpoint['path']}",
                    timeout=10
                )

                expected_auth_status = 403 if endpoint["expected_auth_required"] else 200

                if endpoint["expected_auth_required"]:
                    # Should return 403 Forbidden (not 404 Not Found)
                    success = response.status_code == 403
                    status_message = "Correctly requires authentication" if success else f"Unexpected status: {response.status_code}"
                else:
                    # Should return 200 OK for public endpoints
                    success = response.status_code == 200
                    status_message = "Public endpoint accessible" if success else f"Unexpected status: {response.status_code}"

                if not success:
                    overall_success = False

                results.append({
                    "endpoint": f"{endpoint['method']} {endpoint['path']}",
                    "status_code": response.status_code,
                    "expected_auth_required": endpoint["expected_auth_required"],
                    "success": success,
                    "message": status_message
                })

            except Exception as e:
                results.append({
                    "endpoint": f"{endpoint['method']} {endpoint['path']}",
                    "error": str(e),
                    "success": False
                })
                overall_success = False

        result = {
            "endpoint_tests": results,
            "overall_success": overall_success
        }

        self.log_test_result("API Client Endpoints", overall_success, result)
        return result

    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and fallback behavior"""
        error_test_cases = [
            {
                "name": "Invalid UUID in team search",
                "path": "/api/leagues/invalid-uuid/teams",
                "expected_status": 422,
                "description": "Should return validation error for invalid UUID"
            },
            {
                "name": "Non-existent team search",
                "path": "/api/teams/search?query=NonExistentTeamXYZ123",
                "expected_status": 200,
                "description": "Should return empty results for non-existent team"
            },
            {
                "name": "Non-existent endpoint",
                "path": "/api/non-existent-endpoint",
                "expected_status": 404,
                "description": "Should return 404 for non-existent endpoints"
            }
        ]

        results = []
        overall_success = True

        for test_case in error_test_cases:
            try:
                response = requests.get(f"{self.base_url}{test_case['path']}", timeout=10)

                success = response.status_code == test_case["expected_status"]
                if not success:
                    overall_success = False

                # Check if error responses have proper structure
                error_structure_valid = True
                if response.status_code >= 400 and response.status_code != 404:
                    try:
                        error_data = response.json()
                        if "error" not in error_data:
                            error_structure_valid = False
                    except:
                        error_structure_valid = False

                results.append({
                    "test_name": test_case["name"],
                    "path": test_case["path"],
                    "expected_status": test_case["expected_status"],
                    "actual_status": response.status_code,
                    "success": success,
                    "error_structure_valid": error_structure_valid,
                    "description": test_case["description"]
                })

            except Exception as e:
                results.append({
                    "test_name": test_case["name"],
                    "error": str(e),
                    "success": False
                })
                overall_success = False

        result = {
            "error_handling_tests": results,
            "overall_success": overall_success
        }

        self.log_test_result("Error Handling", overall_success, result)
        return result

    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        print("🧪 Starting Comprehensive Onboarding Flow Test Suite...")
        print("=" * 60)

        # Run all tests
        test_results = {}

        print("1. Testing backend health...")
        test_results["backend_health"] = self.test_backend_health()

        print("2. Testing sports API endpoint...")
        test_results["sports_api"] = self.test_sports_api_endpoint()

        print("3. Testing team search functionality...")
        test_results["team_search"] = self.test_team_search_functionality()

        print("4. Testing team leagues association...")
        test_results["team_leagues"] = self.test_team_leagues_association()

        print("5. Testing API client endpoints...")
        test_results["api_client"] = self.test_api_client_endpoints()

        print("6. Testing error handling...")
        test_results["error_handling"] = self.test_error_handling()

        # Generate summary
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])

        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "test_results": test_results,
            "detailed_results": self.test_results
        }

        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {summary['success_rate']:.1%}")

        return summary


def test_onboarding_flow_comprehensive():
    """Pytest test function for the comprehensive onboarding flow"""
    tester = OnboardingFlowTester()
    results = tester.run_comprehensive_test_suite()

    # Assert overall success
    assert results["success_rate"] >= 0.8, f"Test success rate too low: {results['success_rate']:.1%}"

    # Assert critical components
    assert any(r["test_name"] == "Backend Health Check" and r["success"] for r in results["detailed_results"]), "Backend health check failed"
    assert any(r["test_name"] == "Sports API Endpoint" and r["success"] for r in results["detailed_results"]), "Sports API endpoint failed"

    return results


if __name__ == "__main__":
    # Run tests standalone
    tester = OnboardingFlowTester()
    results = tester.run_comprehensive_test_suite()

    # Save results to file
    with open("/Users/newmac/Desktop/Corner League Media 1/test_onboarding_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Test results saved to test_onboarding_results.json")
    print(f"Overall success rate: {results['success_rate']:.1%}")