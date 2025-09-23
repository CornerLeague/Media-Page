# Corner League Media - Infrastructure Setup Guide

## Overview

This guide provides comprehensive instructions for setting up and managing the complete development infrastructure for Corner League Media, a modern sports platform with React frontend, FastAPI backend, and full observability stack.

## Quick Start

### 1. Initial Setup

```bash
# Run the setup script
./setup-infrastructure.sh

# Start core services
./dev-infrastructure.sh start

# Or start with all tools
./dev-infrastructure.sh start --full
```

### 2. Access Services

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Architecture Overview

### Core Services

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| Frontend | 8080 | React/Vite dev server | HTTP 200 |
| Backend | 8000 | FastAPI application | `/health` endpoint |
| PostgreSQL | 5432 | Primary database | `pg_isready` |
| Redis | 6379 | Cache and sessions | `redis-cli ping` |
| Nginx | 80/443 | Reverse proxy | Config test |

### Optional Services (Profiles)

#### Development Tools (`--dev-tools`)
| Service | Port | Description |
|---------|------|-------------|
| Adminer | 8081 | Database administration |
| Redis Commander | 8082 | Redis management UI |

#### Monitoring (`--monitoring`)
| Service | Port | Description |
|---------|------|-------------|
| Grafana | 3000 | Dashboards and visualization |
| Prometheus | 9090 | Metrics collection |

#### Observability (`--observability`)
| Service | Port | Description |
|---------|------|-------------|
| Jaeger | 16686 | Distributed tracing UI |
| OTEL Collector | 4317/4318 | Telemetry collection |

## Environment Configuration

### File Structure

```
.env                    # Local development (existing)
.env.docker             # Docker environment (copy from .env.docker.example)
.env.docker.example     # Template for Docker setup
```

### Key Configuration Areas

#### Database Configuration
```bash
# PostgreSQL (Docker internal networking)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/sportsdb
POSTGRES_DB=sportsdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

#### Redis Configuration
```bash
# Redis (Docker internal networking)
REDIS_URL=redis://redis:6379/0
REDIS_MAX_MEMORY=256mb
REDIS_MAXMEMORY_POLICY=allkeys-lru
```

#### API Configuration
```bash
# API settings
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGIN=http://localhost:8080,http://localhost:3000,http://localhost
```

#### OpenTelemetry Configuration
```bash
# OTEL endpoints (Docker service names)
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
OTEL_SERVICE_NAME=corner-league-media
OTEL_SERVICE_VERSION=1.0.0
```

## Management Scripts

### Infrastructure Management (`dev-infrastructure.sh`)

#### Basic Commands
```bash
# Start core services
./dev-infrastructure.sh start

# Start with profiles
./dev-infrastructure.sh start --dev-tools
./dev-infrastructure.sh start --monitoring
./dev-infrastructure.sh start --observability
./dev-infrastructure.sh start --full

# Stop services
./dev-infrastructure.sh stop

# Restart services
./dev-infrastructure.sh restart

# Show status
./dev-infrastructure.sh status

# Run health checks
./dev-infrastructure.sh health
```

#### Logging and Debugging
```bash
# View all logs
./dev-infrastructure.sh logs

# View specific service logs
./dev-infrastructure.sh logs backend
./dev-infrastructure.sh logs postgres

# Follow logs in real-time
./dev-infrastructure.sh logs backend --follow
```

#### Cleanup
```bash
# Clean up all containers and volumes
./dev-infrastructure.sh clean
```

### First-time Setup (`setup-infrastructure.sh`)

```bash
# Run comprehensive setup
./setup-infrastructure.sh
```

This script:
- Checks system requirements
- Sets up environment files
- Creates data directories
- Validates configuration
- Tests port availability
- Pulls Docker images
- Runs infrastructure test

## Service Dependencies

### Startup Order

1. **Infrastructure Layer**
   - PostgreSQL
   - Redis

2. **Application Layer**
   - Backend (depends on DB and Redis)
   - Frontend (depends on Backend)

3. **Proxy Layer**
   - Nginx (depends on Frontend and Backend)

4. **Observability Layer** (optional)
   - Jaeger
   - OTEL Collector (depends on Jaeger)
   - Prometheus
   - Grafana

5. **Development Tools** (optional)
   - Adminer (depends on PostgreSQL)
   - Redis Commander (depends on Redis)

### Health Check Strategy

All services implement comprehensive health checks:
- **Database**: `pg_isready` command
- **Redis**: `redis-cli ping` command
- **Backend**: HTTP health endpoint
- **Frontend**: HTTP availability check
- **Jaeger**: UI endpoint availability
- **OTEL Collector**: Health check endpoint

## Data Persistence

### Volume Mappings

```yaml
volumes:
  postgres_data:        # Database data
  redis_data:          # Redis persistence
  grafana_data:        # Grafana dashboards/settings
  prometheus_data:     # Metrics storage
  jaeger_data:         # Trace storage
  backend_cache:       # Python cache
  node_modules_cache:  # Frontend dependencies
  vite_cache:          # Build cache
```

### Data Directories

Local directories for development:
```
data/
├── postgres/        # Database files
├── redis/          # Redis snapshots
├── grafana/        # Grafana data
├── prometheus/     # Metrics data
└── jaeger/         # Trace data

logs/               # Application logs
backups/           # Database backups
```

## Development Workflow

### Daily Development

1. **Start Infrastructure**
   ```bash
   ./dev-infrastructure.sh start --dev-tools
   ```

2. **Check Status**
   ```bash
   ./dev-infrastructure.sh status
   ./dev-infrastructure.sh health
   ```

3. **Development Work**
   - Frontend: Auto-reload on changes (Vite HMR)
   - Backend: Auto-reload on changes (FastAPI with watchdog)
   - Database: Persistent data in volumes

4. **Debugging**
   ```bash
   # View logs
   ./dev-infrastructure.sh logs backend

   # Access tools
   open http://localhost:8081  # Adminer
   open http://localhost:8082  # Redis Commander
   ```

5. **End of Day**
   ```bash
   ./dev-infrastructure.sh stop
   ```

### Testing Setup

```bash
# Start with observability for testing
./dev-infrastructure.sh start --observability

# Access testing tools
open http://localhost:16686  # Jaeger tracing
open http://localhost:8888   # OTEL metrics
```

### Production Preparation

```bash
# Start full stack for production validation
./dev-infrastructure.sh start --full

# Access monitoring
open http://localhost:3000   # Grafana
open http://localhost:9090   # Prometheus
```

## Port Reference

### Core Services
- **8080**: Frontend (React/Vite)
- **8000**: Backend API (FastAPI)
- **5432**: PostgreSQL database
- **6379**: Redis cache
- **80/443**: Nginx reverse proxy

### Development Tools
- **8081**: Adminer (database admin)
- **8082**: Redis Commander

### Monitoring
- **3000**: Grafana dashboards
- **9090**: Prometheus metrics

### Observability
- **16686**: Jaeger UI
- **14268**: Jaeger collector HTTP
- **14250**: Jaeger collector gRPC
- **4317**: OTEL gRPC receiver
- **4318**: OTEL HTTP receiver
- **8888**: OTEL metrics endpoint

### Debug Ports
- **5678**: Backend Python debugger
- **24678**: Vite HMR (Hot Module Reload)

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using a port
lsof -i :8080

# Stop conflicting service
sudo kill -9 $(lsof -t -i:8080)
```

#### Service Won't Start
```bash
# Check service logs
./dev-infrastructure.sh logs [service-name]

# Check Docker status
docker ps -a

# Restart specific service
docker-compose restart [service-name]
```

#### Database Connection Issues
```bash
# Check database health
./dev-infrastructure.sh health

# Manual database check
docker-compose exec postgres pg_isready -U postgres

# View database logs
./dev-infrastructure.sh logs postgres
```

#### Memory Issues
```bash
# Check container resource usage
docker stats

# Clean up unused resources
docker system prune -f
```

### Health Check Commands

Manual health verification:

```bash
# Database
curl -f http://localhost:8000/health

# Frontend
curl -f http://localhost:8080

# Database direct
docker-compose exec postgres pg_isready -U postgres

# Redis direct
docker-compose exec redis redis-cli ping
```

### Log Analysis

```bash
# Application logs
./dev-infrastructure.sh logs backend | grep ERROR

# Database logs
./dev-infrastructure.sh logs postgres | grep ERROR

# All service errors
./dev-infrastructure.sh logs 2>&1 | grep -i error
```

## Security Notes

### Development Security

- All services run with development configurations
- Default passwords are used (change for production)
- CORS is configured for localhost
- SSL/TLS is disabled in development
- Debug modes are enabled

### Environment Variables

Sensitive configuration in `.env.docker`:
- Database passwords
- JWT secrets
- API keys (Clerk, DeepSeek, OpenAI)
- Proxy credentials

**Important**: Never commit `.env.docker` to version control.

## Performance Optimization

### Resource Limits

Services are configured with appropriate resource limits:
- PostgreSQL: 512MB memory limit
- Redis: 256MB memory limit
- Backend: 1GB memory limit
- Frontend: 512MB memory limit

### Caching Strategy

- Redis for application cache
- PostgreSQL connection pooling
- Frontend build caching (Vite)
- Docker layer caching

### Monitoring

With `--monitoring` profile:
- Grafana dashboards for service metrics
- Prometheus for metrics collection
- Custom dashboards for application performance

## Integration Points

### Frontend ↔ Backend
- API calls via `http://localhost:8000`
- CORS configured for development
- Real-time updates via WebSocket (planned)

### Backend ↔ Database
- PostgreSQL connection pooling
- Health checks and reconnection
- Migration support

### Backend ↔ Redis
- Session storage
- Application caching
- Job queues (planned)

### Observability Integration
- OpenTelemetry auto-instrumentation
- Distributed tracing via Jaeger
- Metrics collection via Prometheus
- Log aggregation (planned)

## Next Steps

After successful infrastructure setup:

1. **Authentication Integration**
   - Configure Clerk authentication keys
   - Test login/logout flows

2. **AI Services Integration**
   - Set up DeepSeek/OpenAI API keys
   - Test AI summarization features

3. **Real-time Features**
   - WebSocket implementation
   - Live sports data integration

4. **Production Preparation**
   - SSL/TLS configuration
   - Environment-specific configs
   - CI/CD pipeline integration

## Support

For issues with infrastructure setup:

1. Check logs: `./dev-infrastructure.sh logs`
2. Run health checks: `./dev-infrastructure.sh health`
3. Validate configuration: `docker compose config`
4. Review this documentation
5. Check Docker/system requirements

---

*This infrastructure supports the complete development lifecycle for Corner League Media, providing a production-like environment with full observability and development tools.*