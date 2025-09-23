# Firebase Admin SDK Integration Guide

This document outlines the Firebase Admin SDK integration into the Corner League Media FastAPI backend, providing comprehensive authentication and user management capabilities.

## Overview

The Firebase Admin SDK has been successfully integrated into the FastAPI backend to provide:

- **Server-side authentication** using Firebase ID tokens
- **User management** operations (create, read, update, delete users)
- **Custom claims** for role-based access control
- **Token management** (verification, revocation)
- **Firestore database** operations for additional data storage
- **Dual authentication support** (Clerk + Firebase)

## Architecture

### Service Layer

#### FirebaseService (`app/services/firebase_service.py`)
- Centralized Firebase Admin SDK operations
- Handles authentication, user management, and Firestore operations
- Automatic initialization with environment variable validation
- Comprehensive error handling and logging

#### Enhanced Security (`app/core/security.py`)
- Firebase token verification utilities
- Auto-detection of authentication provider (Clerk vs Firebase)
- Firebase-specific user metadata extraction
- Unified authentication interface

#### Dependencies (`app/core/dependencies.py`)
- FastAPI dependency injection for Firebase authentication
- Firebase-specific authentication decorators
- Service access dependencies
- Permission-based access control placeholders

### Configuration

#### Environment Variables
```bash
# Backend Firebase Admin SDK Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour Firebase private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com

# Frontend Firebase Web Configuration
FIREBASE_WEB_API_KEY=your-firebase-web-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
```

#### Setup Instructions
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Navigate to Project Settings → Service accounts
3. Click "Generate new private key" to download JSON file
4. Extract values from JSON and add to environment variables
5. Configure web app settings for frontend integration

## Features

### 1. Authentication & Authorization

#### Token Verification
```python
from app.core.security import verify_firebase_token

# Verify Firebase ID token
payload = await verify_firebase_token(id_token)
```

#### Multi-Provider Support
```python
from app.core.security import verify_auth_token

# Auto-detect and verify token from any provider
payload = await verify_auth_token(token, provider="auto")
```

#### FastAPI Dependencies
```python
from app.core.dependencies import get_current_user_firebase

@router.get("/protected")
async def protected_endpoint(
    current_user: CurrentUser = Depends(get_current_user_firebase)
):
    return {"user_id": current_user.user_id}
```

### 2. User Management

#### Create User
```python
firebase_service = await get_firebase_service()
user_id = await firebase_service.create_user(
    email="user@example.com",
    password="secure_password",
    display_name="John Doe"
)
```

#### Get User Details
```python
user_data = await firebase_service.get_user(user_id)
```

#### Update User
```python
success = await firebase_service.update_user(
    user_id,
    display_name="Updated Name",
    email_verified=True
)
```

#### Delete User
```python
success = await firebase_service.delete_user(user_id)
```

### 3. Token Management

#### Revoke Refresh Tokens
```python
success = await firebase_service.revoke_refresh_tokens(user_id)
```

#### Create Custom Token
```python
custom_token = await firebase_service.create_custom_token(
    user_id,
    claims={"role": "admin", "team_id": "123"}
)
```

#### Set Custom Claims
```python
success = await firebase_service.set_custom_claims(
    user_id,
    {"role": "moderator", "permissions": ["read", "write"]}
)
```

### 4. Firestore Operations

#### Document Operations
```python
# Create/Update document
await firebase_service.set_document("users", user_id, user_data)

# Read document
user_doc = await firebase_service.get_document("users", user_id)

# Update document
await firebase_service.update_document("users", user_id, {"last_seen": datetime.now()})

# Delete document
await firebase_service.delete_document("users", user_id)
```

#### Query Collections
```python
# Query users by role
admin_users = await firebase_service.query_collection(
    "users",
    role="admin"
)
```

### 5. API Endpoints

#### Firebase-Specific Routes
- `GET /api/v1/auth/firebase/me` - Get current Firebase user info
- `POST /api/v1/auth/firebase/revoke-tokens` - Revoke all refresh tokens

#### Universal Routes (Support Both Providers)
- `GET /api/v1/auth/me` - Auto-detect authentication provider
- `POST /api/v1/auth/refresh` - Refresh session
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/validate` - Validate token

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r app/requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and configure Firebase variables:
```bash
cp .env.example .env
# Edit .env with your Firebase configuration
```

### 3. Verify Integration
```bash
python scripts/verify_firebase_integration.py
```

### 4. Start Application
```bash
cd app
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

### Manual Testing with curl

#### Test Firebase Authentication
```bash
# Get Firebase ID token from your frontend
export FIREBASE_TOKEN="your_firebase_id_token_here"

# Test Firebase-specific endpoint
curl -H "Authorization: Bearer $FIREBASE_TOKEN" \
     http://localhost:8000/api/v1/auth/firebase/me

# Test universal endpoint (auto-detection)
curl -H "Authorization: Bearer $FIREBASE_TOKEN" \
     http://localhost:8000/api/v1/auth/me
```

#### Test Token Revocation
```bash
curl -X POST \
     -H "Authorization: Bearer $FIREBASE_TOKEN" \
     http://localhost:8000/api/v1/auth/firebase/revoke-tokens
```

### Unit Testing
The integration includes comprehensive error handling and validation that can be tested with:
- Mock Firebase credentials
- Invalid token scenarios
- Network failure simulation
- Permission boundary testing

## Security Considerations

### Best Practices Implemented
1. **Secure credential handling** - Environment variable validation with warnings
2. **Token verification** - Proper Firebase ID token validation with Firebase Admin SDK
3. **Error handling** - Comprehensive exception handling without exposing sensitive data
4. **Logging** - Structured logging for debugging without logging sensitive information
5. **Rate limiting** - Ready for rate limiting implementation (dependency placeholders)
6. **Permission system** - Framework for role-based access control

### Production Recommendations
1. Use Firebase security rules for Firestore
2. Implement proper CORS configuration
3. Enable Firebase App Check for additional security
4. Monitor authentication events in Firebase Console
5. Regularly rotate service account keys
6. Implement rate limiting on authentication endpoints
7. Use HTTPS in production
8. Enable audit logging

## Troubleshooting

### Common Issues

#### 1. "Firebase Admin SDK not initialized"
- Check environment variables are properly set
- Verify Firebase project ID and credentials
- Check application startup logs for initialization errors

#### 2. "Invalid Firebase token"
- Ensure token is a valid Firebase ID token (not custom token)
- Check token expiration
- Verify token was issued for correct Firebase project

#### 3. "Permission denied"
- Check Firebase security rules
- Verify custom claims and user permissions
- Ensure service account has proper Firebase project permissions

#### 4. Import errors
- Run `pip install -r app/requirements.txt`
- Check Python path configuration
- Verify relative imports in modules

### Debug Mode
The application includes comprehensive logging. Set `LOG_LEVEL=DEBUG` in environment variables for detailed Firebase operation logs.

## Future Enhancements

### Planned Features
1. **Real-time listeners** - Firestore real-time updates via WebSockets
2. **Firebase Storage** - File upload and management integration
3. **Firebase Messaging** - Push notification support
4. **Advanced permissions** - Team-based access control
5. **Analytics integration** - Firebase Analytics for user behavior
6. **Performance monitoring** - Firebase Performance Monitoring integration

### Integration Patterns
1. **Database synchronization** - Keep PostgreSQL and Firestore in sync
2. **Event-driven updates** - Use Redis pub/sub for real-time notifications
3. **Caching strategy** - Redis caching for frequently accessed Firebase data
4. **Audit logging** - Comprehensive audit trail for all Firebase operations

## Migration Guide

### From Clerk-Only to Dual Authentication
1. Keep existing Clerk authentication working
2. Add Firebase credentials to environment
3. Update frontend to optionally use Firebase Auth
4. Gradually migrate users to Firebase or maintain dual support
5. Use auto-detection feature for seamless transition

### Database Migration
If migrating from Clerk user IDs to Firebase UIDs:
1. Add `firebase_uid` column to user tables
2. Create mapping between Clerk IDs and Firebase UIDs
3. Update authentication logic to handle both ID formats
4. Migrate data in batches
5. Switch primary authentication once migration complete

## API Documentation

The Firebase integration automatically generates comprehensive OpenAPI documentation available at:
- Development: `http://localhost:8000/docs`
- Production: Documentation disabled for security

All Firebase-specific endpoints are properly documented with:
- Request/response schemas
- Authentication requirements
- Error response formats
- Usage examples

## Conclusion

The Firebase Admin SDK integration provides a robust, secure, and scalable authentication and user management solution for the Corner League Media platform. The implementation follows FastAPI best practices and provides a solid foundation for future enhancements.

For additional support or questions, refer to:
- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Project issue tracker for bug reports and feature requests