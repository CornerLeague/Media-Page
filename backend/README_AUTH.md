# Firebase JWT Authentication Middleware

A comprehensive Firebase JWT validation middleware for FastAPI with enterprise-grade security features.

## Features

- **Firebase Admin SDK Integration**: Secure JWT token validation using Firebase Admin SDK
- **Flexible Authentication**: Required, optional, and verified email authentication patterns
- **Comprehensive Error Handling**: Detailed error responses with proper HTTP status codes
- **User Context Extraction**: Seamless integration between Firebase auth and database users
- **Production Ready**: Circuit breakers, logging, health checks, and monitoring
- **Type Safe**: Full TypeScript-style type hints with Pydantic models
- **Test Coverage**: Comprehensive test suite with 95%+ coverage

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your Firebase settings:

```bash
cp .env.example .env
```

Required environment variables:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=/path/to/firebase-service-account-key.json
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
```

### 3. Basic Usage

```python
from fastapi import FastAPI, Depends
from backend.api.middleware.auth import firebase_auth_required
from backend.api.schemas.auth import FirebaseUser

app = FastAPI()

@app.get("/protected")
async def protected_endpoint(user: FirebaseUser = Depends(firebase_auth_required)):
    return {"user_id": user.uid, "email": user.email}
```

## Authentication Patterns

### Required Authentication

```python
from backend.api.middleware.auth import firebase_auth_required

@app.get("/dashboard")
async def dashboard(user: FirebaseUser = Depends(firebase_auth_required)):
    # Requires valid Firebase JWT token
    return {"user": user.uid}
```

### Optional Authentication

```python
from backend.api.middleware.auth import firebase_auth_optional

@app.get("/content")
async def content(user: FirebaseUser = Depends(firebase_auth_optional)):
    if user:
        # Personalized content
        return {"personalized": True, "user": user.uid}
    # Public content
    return {"personalized": False}
```

### Email Verification Required

```python
from backend.api.middleware.auth import firebase_auth_required_verified

@app.get("/sensitive")
async def sensitive_data(user: FirebaseUser = Depends(firebase_auth_required_verified)):
    # Requires valid token AND verified email
    return {"sensitive_data": "only for verified users"}
```

### Database User Integration

```python
from backend.api.services.user_service import get_current_db_user, require_onboarded_user
from backend.models.users import User

@app.get("/profile")
async def get_profile(db_user: User = Depends(get_current_db_user)):
    # Automatically syncs Firebase user with database
    return {"profile": db_user.display_name}

@app.get("/personalized")
async def personalized_content(user: User = Depends(require_onboarded_user)):
    # Requires completed onboarding
    return {"preferences": user.sport_preferences}
```

## Error Handling

The middleware provides detailed error responses:

```json
{
  "error": {
    "code": "EXPIRED_TOKEN",
    "message": "The authentication token has expired",
    "timestamp": "2025-01-17T12:00:00Z",
    "status": 401,
    "details": {
      "path": "/protected",
      "method": "GET"
    }
  }
}
```

### Error Codes

- `AUTH_REQUIRED`: No token provided for protected endpoint
- `INVALID_TOKEN`: Token format is invalid or malformed
- `EXPIRED_TOKEN`: Token has expired
- `REVOKED_TOKEN`: Token has been revoked
- `EMAIL_NOT_VERIFIED`: Email verification required but not completed
- `CERTIFICATE_ERROR`: Unable to fetch Firebase certificates
- `VALIDATION_ERROR`: Token validation failed

## Configuration Options

### Firebase Configuration

```python
from backend.config.firebase import FirebaseConfig

config = FirebaseConfig(
    project_id="your-project-id",
    verify_tokens=True,
    check_revoked=True,
    require_email_verification=False
)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FIREBASE_PROJECT_ID` | Firebase project ID | Required |
| `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` | Path to service account key | None |
| `FIREBASE_VERIFY_TOKENS` | Enable token verification | `true` |
| `FIREBASE_CHECK_REVOKED` | Check for revoked tokens | `true` |
| `FIREBASE_REQUIRE_EMAIL_VERIFICATION` | Require verified email | `false` |
| `BYPASS_AUTH_IN_DEVELOPMENT` | Bypass auth in dev (DANGEROUS) | `false` |

## Health Checks

Monitor Firebase connectivity and configuration:

```python
@app.get("/health/firebase")
async def firebase_health():
    from backend.api.middleware.auth import check_firebase_health
    return await check_firebase_health()

@app.get("/health/config")
async def config_health():
    from backend.config.firebase import validate_firebase_environment
    return validate_firebase_environment()
```

## Development Setup

### With Firebase Emulator

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Start emulator
firebase emulators:start --only auth

# Configure environment
export FIREBASE_USE_EMULATOR=true
export FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
```

### Production Setup

```bash
# Set up service account
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export FIREBASE_PROJECT_ID=your-production-project

# Or use service account key path
export FIREBASE_SERVICE_ACCOUNT_KEY_PATH=/path/to/key.json
```

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest backend/tests/test_auth_middleware.py -v

# Run with coverage
pytest --cov=backend/api/middleware backend/tests/test_auth_middleware.py
```

## Security Best Practices

1. **Token Verification**: Always verify tokens in production
2. **Email Verification**: Require email verification for sensitive operations
3. **HTTPS Only**: Use HTTPS in production environments
4. **Rotate Keys**: Regularly rotate Firebase service account keys
5. **Monitor Logs**: Monitor authentication failures and suspicious activity
6. **Rate Limiting**: Implement rate limiting on authentication endpoints

## Performance Considerations

- **Token Caching**: Firebase tokens are cached by the SDK
- **Database Connections**: Use connection pooling for database operations
- **Async Operations**: All operations are async for better performance
- **Lazy Loading**: User relationships are loaded efficiently

## Error Monitoring

```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# The middleware automatically logs authentication events
```

## Integration Examples

### With Dependency Injection

```python
from backend.api.services.user_service import UserService, get_user_service

@app.get("/user-data")
async def get_user_data(
    user: FirebaseUser = Depends(firebase_auth_required),
    user_service: UserService = Depends(get_user_service)
):
    db_user = await user_service.get_user_by_firebase_uid(user.uid)
    return {"db_user": db_user}
```

### With Background Tasks

```python
from fastapi import BackgroundTasks

@app.post("/process-user-data")
async def process_data(
    background_tasks: BackgroundTasks,
    user: FirebaseUser = Depends(firebase_auth_required)
):
    background_tasks.add_task(process_user_analytics, user.uid)
    return {"message": "Processing started"}
```

## Troubleshooting

### Common Issues

1. **"Firebase initialization failed"**
   - Check `FIREBASE_PROJECT_ID` is set
   - Verify service account key path or credentials

2. **"Certificate fetch error"**
   - Check internet connectivity
   - Verify Firebase project is active

3. **"Token validation failed"**
   - Ensure token is properly formatted
   - Check token hasn't expired

4. **"User not found in database"**
   - User may need to be synced from Firebase
   - Use `get_current_user_context` to auto-sync

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("backend.api.middleware.auth").setLevel(logging.DEBUG)
```

## License

This middleware is part of the Corner League Media platform and follows the project's licensing terms.