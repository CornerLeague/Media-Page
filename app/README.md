# Corner League Media API

A comprehensive FastAPI backend for the Corner League Media sports platform, providing authentication, team management, and real-time sports data integration.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic OpenAPI documentation
- **Clerk Authentication**: JWT token validation and user management
- **Redis Integration**: Caching and job queue management
- **Team Management**: Comprehensive team data and statistics
- **User Preferences**: Personalized user settings and team favorites
- **Health Monitoring**: Comprehensive health checks and monitoring
- **CORS Support**: Configured for frontend integration
- **Production Ready**: Security headers, rate limiting, and error handling

## Quick Start

### Prerequisites

- Python 3.11+
- Redis Server
- Clerk account (for authentication)

### Local Development

1. **Install Dependencies**
   ```bash
   cd app
   pip install -r requirements.txt
   ```

2. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Redis**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:7-alpine

   # Or using local Redis
   redis-server
   ```

4. **Start the API**
   ```bash
   python start.py
   ```

The API will be available at `http://localhost:8000`

### Using Docker

1. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

This will start both the API and Redis services.

## API Documentation

With the server running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/v1/openapi.json`

## Environment Configuration

Key environment variables:

```bash
# Required
CLERK_SECRET_KEY=your_clerk_secret_key
REDIS_URL=redis://localhost:6379

# Optional
DEBUG=true
PORT=8000
FRONTEND_URL=http://localhost:8080
```

See `.env.example` for complete configuration options.

## API Endpoints

### Health & Monitoring
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with dependencies
- `GET /health/redis` - Redis connection status

### Authentication
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh session
- `POST /api/v1/auth/logout` - Logout user

### User Management
- `GET /api/v1/users/me` - Get user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/me/preferences` - Get user preferences
- `PUT /api/v1/users/me/preferences` - Update preferences
- `GET /api/v1/users/me/teams` - Get favorite teams
- `POST /api/v1/users/me/teams` - Add favorite team
- `DELETE /api/v1/users/me/teams/{team_id}` - Remove favorite team

### Team Management
- `GET /api/v1/teams` - List teams with filtering
- `GET /api/v1/teams/{team_id}` - Get team details
- `GET /api/v1/teams/{team_id}/dashboard` - Team dashboard data
- `GET /api/v1/teams/{team_id}/news` - Team news
- `GET /api/v1/teams/{team_id}/summary` - AI-generated team summary
- `GET /api/v1/teams/{team_id}/stats` - Team statistics
- `GET /api/v1/teams/popular` - Popular teams

## Authentication

The API uses Clerk JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Frontend Integration

The API is configured to work with the React frontend running on `http://localhost:8080`. CORS is properly configured for seamless integration.

## Development

### Project Structure

```
app/
├── api/                 # API routes and dependencies
│   ├── deps.py         # Authentication dependencies
│   ├── main.py         # FastAPI application
│   └── routes/         # API route modules
├── core/               # Core configuration and utilities
│   ├── config.py       # Settings and configuration
│   ├── security.py     # Authentication and JWT validation
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

### Adding New Features

1. **Create Pydantic models** in `models/`
2. **Add business logic** in `services/`
3. **Create API routes** in `api/routes/`
4. **Update dependencies** if needed in `api/deps.py`
5. **Include routes** in `api/main.py`

## Testing

The API includes comprehensive error handling and logging. Monitor the application logs for debugging.

## Production Deployment

1. **Set environment variables** for production
2. **Use a production Redis instance**
3. **Configure proper CORS origins**
4. **Set up monitoring and logging**
5. **Use a reverse proxy** (nginx, etc.)

## Security

The API includes:
- JWT token validation
- CORS protection
- Security headers
- Request size limits
- Rate limiting (configured)
- Input validation

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the health endpoints for system status
3. Check application logs for error details