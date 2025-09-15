# Corner League Media - FastAPI Backend Setup

## 🚀 Quick Start

I've created a comprehensive FastAPI backend for your Corner League Media sports platform. Here's how to get it running:

### Option 1: Automated Start (Recommended)
```bash
python start_backend.py
```
This script will:
- Check if Redis is running
- Start Redis with Docker if needed
- Launch the FastAPI server

### Option 2: Manual Start
```bash
# 1. Start Redis
docker run -d --name redis-cornerleague -p 6379:6379 redis:7-alpine

# 2. Start the API
cd app
python start.py
```

## 📋 What's Been Created

### Complete Backend Structure
```
/app/
├── api/                 # API routes and dependencies
│   ├── deps.py         # Authentication dependencies
│   ├── main.py         # FastAPI application
│   └── routes/         # API route modules
│       ├── health.py   # Health check endpoints
│       ├── auth.py     # Authentication endpoints
│       ├── users.py    # User management
│       └── teams.py    # Team management
├── core/               # Core configuration and utilities
│   ├── config.py       # Settings and configuration
│   ├── security.py     # Clerk JWT validation
│   └── middleware.py   # Custom middleware
├── models/             # Pydantic models
│   ├── base.py         # Base model classes
│   ├── user.py         # User models
│   └── team.py         # Team models
├── services/           # Business logic services
│   ├── auth_service.py # Authentication service
│   ├── redis_service.py# Redis operations
│   └── user_service.py # User management
└── requirements.txt    # Python dependencies
```

## 🔧 Key Features Implemented

### ✅ Authentication & Security
- **Clerk JWT Integration**: Complete token validation with JWKS
- **Security Middleware**: Headers, CORS, request size limits
- **Authentication Dependencies**: Reusable auth decorators
- **Development Mode**: Works without Clerk keys for testing

### ✅ API Endpoints
- **Health Checks**: `/health`, `/health/detailed`, `/health/redis`
- **Authentication**: `/api/v1/auth/me`, `/auth/refresh`, `/auth/logout`
- **User Management**: `/api/v1/users/me`, `/users/me/preferences`, `/users/me/teams`
- **Team Data**: `/api/v1/teams`, `/teams/{id}/dashboard`, `/teams/{id}/summary`

### ✅ Data Management
- **Pydantic Models**: Type-safe data validation
- **Redis Integration**: Caching and session management
- **Mock Data**: Ready-to-use sample teams and users
- **Error Handling**: Comprehensive error responses

### ✅ Production Ready
- **OpenAPI Documentation**: Auto-generated at `/docs`
- **CORS Configuration**: Ready for frontend integration
- **Environment Variables**: Flexible configuration
- **Docker Support**: docker-compose.yml included
- **Logging & Monitoring**: Request/response logging

## 🌐 API Documentation

Once running, visit:
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔗 Frontend Integration

The API is configured for your React frontend:
```javascript
// Frontend API client example
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Get current user
const response = await fetch(`${API_BASE_URL}/auth/me`, {
  headers: {
    'Authorization': `Bearer ${clerkToken}`,
    'Content-Type': 'application/json'
  }
});
```

## 📝 Environment Setup

Copy the example environment file:
```bash
cd app
cp .env.example .env
```

Key variables to configure:
- `CLERK_SECRET_KEY`: Your Clerk secret key
- `REDIS_URL`: Redis connection string
- `FRONTEND_URL`: Your React app URL (default: http://localhost:8080)

## 🧪 Testing

Run the test suite:
```bash
python test_api.py
```

## 📊 Sample API Calls

### Get Teams
```bash
curl http://localhost:8000/api/v1/teams
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Team Dashboard (requires auth)
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/teams/team_1/dashboard
```

## 🔄 Next Steps

1. **Start the backend**: `python start_backend.py`
2. **Test endpoints**: Visit http://localhost:8000/docs
3. **Integrate with frontend**: Update API_URL in your React app
4. **Add Clerk keys**: For full authentication functionality
5. **Customize teams**: Replace mock data with real team data

## 🎯 Ready for Integration

The backend is immediately compatible with your existing React frontend and includes:
- All endpoint schemas ready for OpenAPI code generation
- CORS configured for your frontend port (8080)
- Mock data for immediate testing
- Comprehensive error handling
- Production-ready architecture

Your sports platform backend is ready to power real-time team data, user preferences, and AI-generated summaries! 🏈🏀⚾