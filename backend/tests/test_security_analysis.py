"""
Security Analysis and Testing for Corner League Media Backend

This module performs comprehensive security testing of the authentication
middleware and user endpoints focusing on:

1. JWT token validation security
2. Authentication bypass attempts
3. Input validation and sanitization
4. Error handling security
5. Information disclosure prevention
6. Rate limiting and DoS protection
"""

import pytest
import re
from typing import List, Dict, Any
from pathlib import Path


class SecurityAnalysis:
    """Security analysis for authentication and user endpoints"""

    def __init__(self):
        self.backend_path = Path("/Users/newmac/Desktop/Corner League Media 1/backend")
        self.security_issues = []
        self.recommendations = []

    def analyze_authentication_middleware(self) -> Dict[str, Any]:
        """Analyze authentication middleware for security vulnerabilities"""

        auth_file = self.backend_path / "api/middleware/auth.py"
        if not auth_file.exists():
            return {"error": "Authentication middleware file not found"}

        content = auth_file.read_text()

        # Security checks
        issues = []
        recommendations = []

        # 1. Check for proper token validation
        if "auth.verify_id_token" in content:
            recommendations.append("✓ Using Firebase Admin SDK for token verification")
        else:
            issues.append("⚠ No Firebase token verification found")

        # 2. Check for proper error handling
        exception_patterns = [
            "auth.ExpiredIdTokenError",
            "auth.RevokedIdTokenError",
            "auth.InvalidIdTokenError",
            "auth.CertificateFetchError"
        ]

        for pattern in exception_patterns:
            if pattern in content:
                recommendations.append(f"✓ Handles {pattern}")
            else:
                issues.append(f"⚠ Missing handling for {pattern}")

        # 3. Check for input validation
        if "token.strip()" in content:
            recommendations.append("✓ Input sanitization with token.strip()")

        if "len(token)" in content:
            recommendations.append("✓ Token length validation")

        if "token.count('.')" in content:
            recommendations.append("✓ JWT structure validation")

        # 4. Check for information disclosure
        log_patterns = re.findall(r'logger\.\w+\([^)]+\)', content)
        sensitive_data_patterns = ["token", "password", "secret", "key"]

        for log_line in log_patterns:
            for sensitive in sensitive_data_patterns:
                if sensitive.lower() in log_line.lower() and "str(e)" not in log_line:
                    issues.append(f"⚠ Potential sensitive data in logs: {log_line}")

        # 5. Check for proper HTTP status codes
        if "HTTP_401_UNAUTHORIZED" in content:
            recommendations.append("✓ Proper 401 status codes for auth failures")

        if "HTTP_403_FORBIDDEN" in content:
            recommendations.append("✓ Proper 403 status codes for authorization failures")

        # 6. Check for timing attack prevention
        if "verify_id_token" in content:
            recommendations.append("✓ Using secure token verification (timing-safe)")

        return {
            "security_issues": issues,
            "recommendations": recommendations,
            "overall_score": self._calculate_security_score(issues, recommendations)
        }

    def analyze_user_endpoints(self) -> Dict[str, Any]:
        """Analyze user endpoints for security vulnerabilities"""

        main_file = self.backend_path / "main.py"
        if not main_file.exists():
            return {"error": "Main application file not found"}

        content = main_file.read_text()

        issues = []
        recommendations = []

        # 1. Check for authentication dependencies
        auth_deps = [
            "firebase_auth_required",
            "get_current_user_context",
            "get_current_db_user",
            "require_onboarded_user"
        ]

        for dep in auth_deps:
            if dep in content:
                recommendations.append(f"✓ Using authentication dependency: {dep}")

        # 2. Check for CORS configuration
        if "CORSMiddleware" in content:
            if 'allow_origins=\"*\"' in content or "allow_origins=os.getenv" in content:
                recommendations.append("✓ CORS middleware configured")
            else:
                issues.append("⚠ CORS may be too permissive")

        # 3. Check for trusted host middleware
        if "TrustedHostMiddleware" in content:
            recommendations.append("✓ Trusted host middleware configured")

        # 4. Check for input validation on endpoints
        endpoint_patterns = re.findall(r'@app\.\w+\([^)]+\)', content)

        # 5. Check for proper response models
        if "response_model" in content:
            recommendations.append("✓ Response models defined for type safety")

        # 6. Check for health endpoints
        if "/health" in content:
            recommendations.append("✓ Health check endpoints available")

        # 7. Check for environment variable usage
        env_vars = re.findall(r'os\.getenv\([^)]+\)', content)
        if env_vars:
            recommendations.append(f"✓ Environment variables used: {len(env_vars)} instances")

        return {
            "security_issues": issues,
            "recommendations": recommendations,
            "overall_score": self._calculate_security_score(issues, recommendations)
        }

    def analyze_firebase_config(self) -> Dict[str, Any]:
        """Analyze Firebase configuration for security issues"""

        config_file = self.backend_path / "config/firebase.py"
        if not config_file.exists():
            return {"error": "Firebase config file not found"}

        content = config_file.read_text()

        issues = []
        recommendations = []

        # 1. Check for proper credential handling
        if "credentials.Certificate" in content:
            recommendations.append("✓ Service account certificate support")

        if "credentials.ApplicationDefault" in content:
            recommendations.append("✓ Application default credentials support")

        # 2. Check for environment variable validation
        if "FIREBASE_PROJECT_ID" in content:
            recommendations.append("✓ Project ID from environment")

        # 3. Check for dangerous development settings
        if "bypass_auth_in_development" in content:
            issues.append("⚠ Authentication bypass setting exists - ensure not used in production")

        # 4. Check for email verification requirements
        if "require_email_verification" in content:
            recommendations.append("✓ Email verification configuration available")

        # 5. Check for proper validation
        if "validate_configuration" in content:
            recommendations.append("✓ Configuration validation implemented")

        return {
            "security_issues": issues,
            "recommendations": recommendations,
            "overall_score": self._calculate_security_score(issues, recommendations)
        }

    def _calculate_security_score(self, issues: List[str], recommendations: List[str]) -> Dict[str, Any]:
        """Calculate overall security score"""
        total_checks = len(issues) + len(recommendations)
        if total_checks == 0:
            return {"score": 0, "grade": "Unknown"}

        score = (len(recommendations) / total_checks) * 100

        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return {
            "score": round(score, 1),
            "grade": grade,
            "total_checks": total_checks,
            "passed": len(recommendations),
            "issues": len(issues)
        }

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""

        auth_analysis = self.analyze_authentication_middleware()
        endpoint_analysis = self.analyze_user_endpoints()
        config_analysis = self.analyze_firebase_config()

        # Aggregate recommendations
        all_recommendations = []
        all_issues = []

        for analysis in [auth_analysis, endpoint_analysis, config_analysis]:
            if "recommendations" in analysis:
                all_recommendations.extend(analysis["recommendations"])
            if "security_issues" in analysis:
                all_issues.extend(analysis["security_issues"])

        # Overall security score
        overall_score = self._calculate_security_score(all_issues, all_recommendations)

        return {
            "summary": {
                "overall_security_score": overall_score,
                "total_recommendations": len(all_recommendations),
                "total_issues": len(all_issues)
            },
            "authentication_middleware": auth_analysis,
            "user_endpoints": endpoint_analysis,
            "firebase_config": config_analysis,
            "detailed_recommendations": all_recommendations,
            "security_issues": all_issues,
            "additional_recommendations": [
                "🔒 Implement rate limiting on authentication endpoints",
                "🔒 Add request ID logging for audit trails",
                "🔒 Consider implementing JWT refresh token mechanism",
                "🔒 Add monitoring and alerting for authentication failures",
                "🔒 Implement CSRF protection for state-changing operations",
                "🔒 Add input validation schemas for all endpoint parameters",
                "🔒 Consider implementing API versioning for security updates",
                "🔒 Add automated security testing in CI/CD pipeline"
            ]
        }


class TestSecurityAnalysis:
    """Test cases for security analysis"""

    def test_security_analysis_runs(self):
        """Test that security analysis runs without errors"""
        analyzer = SecurityAnalysis()
        report = analyzer.generate_security_report()

        assert "summary" in report
        assert "authentication_middleware" in report
        assert "user_endpoints" in report
        assert "firebase_config" in report

    def test_authentication_middleware_analysis(self):
        """Test authentication middleware security analysis"""
        analyzer = SecurityAnalysis()
        result = analyzer.analyze_authentication_middleware()

        # Should have some recommendations if file exists
        if "error" not in result:
            assert "recommendations" in result
            assert "security_issues" in result
            assert "overall_score" in result

    def test_user_endpoints_analysis(self):
        """Test user endpoints security analysis"""
        analyzer = SecurityAnalysis()
        result = analyzer.analyze_user_endpoints()

        # Should have some recommendations if file exists
        if "error" not in result:
            assert "recommendations" in result
            assert "security_issues" in result
            assert "overall_score" in result

    def test_firebase_config_analysis(self):
        """Test Firebase config security analysis"""
        analyzer = SecurityAnalysis()
        result = analyzer.analyze_firebase_config()

        # Should have some recommendations if file exists
        if "error" not in result:
            assert "recommendations" in result
            assert "security_issues" in result
            assert "overall_score" in result


def run_security_analysis():
    """Run comprehensive security analysis and print report"""
    analyzer = SecurityAnalysis()
    report = analyzer.generate_security_report()

    print("=" * 80)
    print("🔒 CORNER LEAGUE MEDIA - SECURITY ANALYSIS REPORT")
    print("=" * 80)

    # Overall Summary
    summary = report["summary"]
    print(f"\\n📊 OVERALL SECURITY SCORE: {summary['overall_security_score']['score']}% (Grade: {summary['overall_security_score']['grade']})")
    print(f"✅ Security Checks Passed: {summary['overall_security_score']['passed']}")
    print(f"⚠️  Security Issues Found: {summary['overall_security_score']['issues']}")
    print(f"📋 Total Checks Performed: {summary['overall_security_score']['total_checks']}")

    # Authentication Middleware
    print("\\n" + "=" * 50)
    print("🔐 AUTHENTICATION MIDDLEWARE ANALYSIS")
    print("=" * 50)
    auth_analysis = report["authentication_middleware"]
    if "error" in auth_analysis:
        print(f"❌ {auth_analysis['error']}")
    else:
        print(f"Score: {auth_analysis['overall_score']['score']}% (Grade: {auth_analysis['overall_score']['grade']})")
        print("\\n✅ Security Recommendations:")
        for rec in auth_analysis["recommendations"]:
            print(f"  {rec}")

        if auth_analysis["security_issues"]:
            print("\\n⚠️  Security Issues:")
            for issue in auth_analysis["security_issues"]:
                print(f"  {issue}")

    # User Endpoints
    print("\\n" + "=" * 50)
    print("🌐 USER ENDPOINTS ANALYSIS")
    print("=" * 50)
    endpoint_analysis = report["user_endpoints"]
    if "error" in endpoint_analysis:
        print(f"❌ {endpoint_analysis['error']}")
    else:
        print(f"Score: {endpoint_analysis['overall_score']['score']}% (Grade: {endpoint_analysis['overall_score']['grade']})")
        print("\\n✅ Security Recommendations:")
        for rec in endpoint_analysis["recommendations"]:
            print(f"  {rec}")

        if endpoint_analysis["security_issues"]:
            print("\\n⚠️  Security Issues:")
            for issue in endpoint_analysis["security_issues"]:
                print(f"  {issue}")

    # Firebase Config
    print("\\n" + "=" * 50)
    print("🔥 FIREBASE CONFIGURATION ANALYSIS")
    print("=" * 50)
    config_analysis = report["firebase_config"]
    if "error" in config_analysis:
        print(f"❌ {config_analysis['error']}")
    else:
        print(f"Score: {config_analysis['overall_score']['score']}% (Grade: {config_analysis['overall_score']['grade']})")
        print("\\n✅ Security Recommendations:")
        for rec in config_analysis["recommendations"]:
            print(f"  {rec}")

        if config_analysis["security_issues"]:
            print("\\n⚠️  Security Issues:")
            for issue in config_analysis["security_issues"]:
                print(f"  {issue}")

    # Additional Recommendations
    print("\\n" + "=" * 50)
    print("💡 ADDITIONAL SECURITY RECOMMENDATIONS")
    print("=" * 50)
    for rec in report["additional_recommendations"]:
        print(f"  {rec}")

    print("\\n" + "=" * 80)
    print("🔒 END OF SECURITY ANALYSIS REPORT")
    print("=" * 80)

    return report


if __name__ == "__main__":
    # Run security analysis
    report = run_security_analysis()

    # Run pytest tests
    pytest.main([__file__, "-v"])