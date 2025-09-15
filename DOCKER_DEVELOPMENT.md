# Corner League Media - Docker Development Environment

Complete Docker-based development environment for the Corner League Media sports platform.

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Update .env with your configuration
# (especially Clerk authentication keys)

# 3. Start development environment
./dev-start.sh

# 4. Access the application
open http://localhost:8080
```

## Architecture Overview

The development environment consists of the following services:

### Core Services
- **PostgreSQL** (port 5432): Primary database with full sports schema
- **Redis** (port 6379): Caching and session storage
- **FastAPI Backend** (port 8000): Python API with Clerk authentication
- **React Frontend** (port 8080): Vite development server with hot reload
- **Nginx** (port 80): Reverse proxy for unified access

### Development Tools
- **Adminer** (port 8081): Database administration interface
- **Redis Commander** (port 8082): Redis management interface

### Monitoring Stack (Optional)
- **Grafana** (port 3000): Monitoring dashboards
- **Prometheus** (port 9090): Metrics collection

## Service URLs

| Service | Local URL | Docker URL | Description |
|---------|-----------|------------|-------------|
| Frontend | http://localhost:8080 | http://frontend:8080 | React app with Vite |
| Backend API | http://localhost:8000 | http://backend:8000 | FastAPI with docs |
| Database | localhost:5432 | postgres:5432 | PostgreSQL |
| Redis | localhost:6379 | redis:6379 | Redis cache |
| Adminer | http://localhost:8081 | http://adminer:8080 | DB admin |
| Redis UI | http://localhost:8082 | http://redis-commander:8081 | Redis admin |
| Nginx | http://localhost | http://nginx:80 | Reverse proxy |

## Management Scripts

### Start Environment
```bash
./dev-start.sh           # Start all services
./dev-start.sh --logs    # Start and show logs
```

### Stop Environment
```bash
./dev-stop.sh            # Stop all services
./dev-stop.sh --clean    # Stop and remove volumes
```

### View Logs
```bash
./dev-logs.sh            # Follow all service logs
./dev-logs.sh backend    # Follow specific service logs
./dev-logs.sh frontend   # Follow frontend logs
```

### Restart Services
```bash
./dev-restart.sh         # Restart all services
./dev-restart.sh backend # Restart specific service
```

### Access Service Shells
```bash
./dev-shell.sh backend   # Access backend Python shell
./dev-shell.sh frontend  # Access frontend Node.js shell
./dev-shell.sh postgres  # Access PostgreSQL shell
./dev-shell.sh redis     # Access Redis CLI
```

## Environment Configuration

### Required Environment Variables

Copy `.env.example` to `.env` and configure:

#### Clerk Authentication (Required)
```bash
CLERK_PUBLISHABLE_KEY=pk_test_your-key-here
CLERK_SECRET_KEY=sk_test_your-key-here
CLERK_ISSUER=https://your-domain.clerk.accounts.dev
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-key-here
```

#### Database Configuration
```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/sportsdb
REDIS_URL=redis://redis:6379/0
```

#### API Configuration
```bash
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here
VITE_API_URL=http://localhost:8000
```

### Optional Configuration

#### AI Services
```bash
DEEPSEEK_API_KEY=your-deepseek-key
OPENAI_API_KEY=your-openai-key
```

#### Monitoring
```bash
GRAFANA_PASSWORD=your-grafana-password
```

## Development Workflow

### 1. Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd corner-league-media

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Start development environment
./dev-start.sh
```

### 2. Daily Development
```bash
# Start environment (if not running)
./dev-start.sh

# View logs during development
./dev-logs.sh

# Access backend shell for debugging
./dev-shell.sh backend

# Restart service after configuration changes
./dev-restart.sh backend
```

### 3. Database Operations
```bash
# Access PostgreSQL shell
./dev-shell.sh postgres

# View database through Adminer
open http://localhost:8081
```

### 4. Frontend Development
- Frontend runs on port 8080 with hot reload
- Changes to React files automatically trigger rebuilds
- Vite HMR provides instant feedback

### 5. Backend Development
- Backend runs with uvicorn in reload mode
- Python file changes automatically restart the server
- API documentation available at http://localhost:8000/docs

## Docker Compose Files

### docker-compose.yml
Main production-ready configuration with:
- Health checks for all services
- Proper networking and dependencies
- Volume persistence
- Security configurations

### docker-compose.dev.yml
Development overrides providing:
- Hot reload for all services
- Development tools (Adminer, Redis Commander)
- Debug logging
- Volume mounts for code changes

## Database Schema

The PostgreSQL database is automatically initialized with:

### Core Tables
- `users` - User accounts with Clerk integration
- `user_preferences` - User settings and team preferences
- `sports` - Sports leagues (NFL, NBA, MLB, etc.)
- `teams` - Team information and metadata
- `content_articles` - Sports news and content
- `content_sources` - News source information
- `games` - Game schedules and scores

### Indexes and Performance
- Full-text search indexes on content
- Team and sport relationship indexes
- User interaction tracking indexes
- Optimized query performance

### Sample Data
Development environment includes:
- Major sports leagues (NFL, NBA, MLB, NHL)
- Sample teams from each league
- Sample content articles
- Test user accounts

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker daemon
docker info

# Check for port conflicts
lsof -i :8080  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Clean and restart
./dev-stop.sh --clean
./dev-start.sh
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
./dev-logs.sh postgres

# Access database directly
./dev-shell.sh postgres

# Verify database exists
docker exec -it corner-league-postgres psql -U postgres -l
```

#### Backend API Issues
```bash
# Check backend logs
./dev-logs.sh backend

# Access backend shell
./dev-shell.sh backend

# Test API manually
curl http://localhost:8000/health
```

#### Frontend Build Issues
```bash
# Check frontend logs
./dev-logs.sh frontend

# Access frontend shell
./dev-shell.sh frontend

# Clear node modules and reinstall
docker exec -it corner-league-frontend sh -c "rm -rf node_modules && npm install"
```

### Performance Issues

#### Slow Startup
- Increase Docker memory allocation (4GB+ recommended)
- Use Docker volume instead of bind mounts for node_modules
- Ensure SSD storage for Docker volumes

#### Database Performance
- Increase shared_buffers in PostgreSQL configuration
- Monitor query performance through Adminer
- Use database indexes effectively

### Health Checks

All services include health checks:
```bash
# Check service health
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps

# View health check logs
docker inspect corner-league-backend --format='{{.State.Health}}'
```

## Security Considerations

### Development Environment
- Uses default passwords (change for production)
- Disables HTTPS (enable for production)
- Exposes internal ports (restrict for production)
- Includes debugging tools (remove for production)

### Production Deployment
- Use strong passwords and secrets
- Enable HTTPS with proper certificates
- Restrict network access
- Remove development tools
- Use production Docker targets

## Monitoring and Observability

### Grafana Dashboards
Access at http://localhost:3000 (when monitoring profile enabled):
- Application metrics
- Database performance
- Redis cache statistics
- System resource usage

### Prometheus Metrics
Access at http://localhost:9090:
- Service health metrics
- Custom application metrics
- Infrastructure monitoring

### Logging
- Structured JSON logging in production
- Centralized log aggregation
- Error tracking and alerting

## CI/CD Integration

### GitHub Actions
```yaml
# Example workflow for testing
- name: Start development environment
  run: ./dev-start.sh

- name: Run tests
  run: |
    ./dev-shell.sh backend python -m pytest
    ./dev-shell.sh frontend npm test
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Contributing

### Development Guidelines
1. Always use the Docker environment for development
2. Write tests for new features
3. Follow code formatting standards (Black for Python, Prettier for JS)
4. Update documentation for significant changes
5. Use feature branches and pull requests

### Code Quality
```bash
# Python formatting
./dev-shell.sh backend black .
./dev-shell.sh backend isort .

# Python testing
./dev-shell.sh backend pytest

# JavaScript formatting
./dev-shell.sh frontend npm run lint
./dev-shell.sh frontend npm run test
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Clerk Authentication](https://clerk.dev/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)