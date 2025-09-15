# Corner League Media - Docker Development Environment

A comprehensive Docker-based development environment for the Corner League Media sports platform with full observability, development tools, and production-ready configuration patterns.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop 4.0+ with Compose V2
- 8GB+ RAM available for Docker
- 10GB+ free disk space

### Basic Setup
```bash
# 1. Clone and enter project directory
cd "Corner League Media"

# 2. Start core services only
./dev-start.sh

# 3. Start with development tools
./dev-start.sh --tools

# 4. Start with full monitoring stack
./dev-start.sh --all --logs
```

### Core Services Access
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (postgres/postgres)
- **Redis Cache**: localhost:6379

## 📋 Architecture Overview

### Core Stack
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│────│  FastAPI Backend│────│   PostgreSQL    │
│   (Port 8080)   │    │   (Port 8000)   │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Port 6379)   │
                    └─────────────────┘
```

### Service Dependencies
- **Frontend** → Backend (health check dependent)
- **Backend** → PostgreSQL + Redis (health check dependent)
- **PostgreSQL** → Independent (first to start)
- **Redis** → Independent (starts with PostgreSQL)

### Network Configuration
- **Network**: `corner-league-network` (172.20.0.0/16)
- **Bridge**: Docker bridge with custom subnet
- **Service Discovery**: Automatic via Docker DNS

## 🛠️ Development Tools (--tools profile)

### Database Administration
- **Adminer**: http://localhost:8081
  - Server: `postgres`
  - Username: `postgres`
  - Password: `postgres`
  - Database: `sportsdb`

### Redis Administration
- **Redis Commander**: http://localhost:8082
  - Username: `admin`
  - Password: `admin` (configurable via .env)

### Email Testing
- **MailHog**: http://localhost:8025
  - SMTP: localhost:1025
  - Captures all outbound emails for testing

## 📊 Monitoring & Observability (--monitoring profile)

### Metrics & Dashboards
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin` (configurable via .env)
  - Dashboards: Pre-configured for application metrics

- **Prometheus**: http://localhost:9090
  - Metrics collection from all services
  - Backend metrics on `/metrics` endpoint

### Distributed Tracing
- **Jaeger**: http://localhost:16686
  - Full request tracing across services
  - Performance analysis and debugging

### OpenTelemetry Collector
- **OTLP gRPC**: localhost:4317
- **OTLP HTTP**: localhost:4318
- **Metrics Export**: localhost:8889
- **Health Check**: localhost:13133

## 💾 Storage Services (--storage profile)

### Object Storage
- **MinIO**: http://localhost:9000
  - Console: http://localhost:9001
  - Access Key: `admin`
  - Secret Key: `minioadmin`
  - S3-compatible API for file storage

## 🔧 Development Workflow

### Starting Services
```bash
# Core services only (fastest startup)
./dev-start.sh

# With development tools
./dev-start.sh --tools

# With monitoring stack
./dev-start.sh --monitoring

# With object storage
./dev-start.sh --storage

# Everything (full development environment)
./dev-start.sh --all

# Start and show logs immediately
./dev-start.sh --all --logs
```

### Managing Services
```bash
# View real-time logs
./dev-logs.sh

# Check service health
./scripts/health-check.sh

# Quick health check
./scripts/health-check.sh --quick

# Restart specific service
docker compose restart backend

# Stop all services
./dev-stop.sh

# Restart everything
./dev-restart.sh
```

### Development Commands
```bash
# Backend shell access
./dev-shell.sh backend

# Database shell
./dev-shell.sh postgres

# Frontend shell
./dev-shell.sh frontend

# Redis CLI
./dev-shell.sh redis

# Build only backend
docker compose build backend

# View service status
docker compose ps

# Follow logs for specific service
docker compose logs -f backend
```

## 🗂️ Volume Management

### Persistent Data
- **postgres_data**: Database storage
- **redis_data**: Redis persistence
- **grafana_data**: Grafana dashboards and config
- **prometheus_data**: Metrics storage

### Performance Caches
- **backend_cache**: Python package cache
- **node_modules_cache**: Node.js dependencies
- **vite_cache**: Vite build cache

### Cache Management
```bash
# Clear all caches (nuclear option)
docker compose down -v

# Clear specific cache
docker volume rm corner-league-media_backend_cache

# View volume usage
docker system df
```

## 🔒 Environment Configuration

### Required Environment Variables
```bash
# Copy template and customize
cp .env.example .env

# Edit configuration
vim .env
```

### Key Configuration Sections
1. **Database**: PostgreSQL connection settings
2. **Redis**: Cache configuration
3. **Clerk Auth**: Authentication provider settings
4. **AI Services**: DeepSeek/OpenAI API keys
5. **CORS**: Cross-origin request settings
6. **Monitoring**: Observability configuration

## 🚨 Health Monitoring

### Automatic Health Checks
All services include built-in health checks:

- **PostgreSQL**: `pg_isready` every 10s
- **Redis**: `redis-cli ping` every 10s
- **Backend**: HTTP `/health` endpoint every 30s
- **Frontend**: HTTP connectivity check every 30s

### Manual Health Verification
```bash
# Comprehensive health check
./scripts/health-check.sh

# Quick core services check
./scripts/health-check.sh --quick

# Check specific service
docker compose exec backend curl -f http://localhost:8000/health
```

## 🎯 Performance Optimization

### Development Performance
- **Hot Reload**: Both frontend and backend support live reloading
- **Layer Caching**: Optimized Dockerfile layers for fast rebuilds
- **Volume Caching**: Persistent caches for dependencies
- **Parallel Startup**: Services start in optimal dependency order

### Resource Limits
- **Redis Memory**: 256MB with LRU eviction
- **PostgreSQL**: Optimized for development workload
- **Container Memory**: No hard limits (relies on Docker Desktop)

### Build Optimization
```bash
# Build with no cache (clean build)
docker compose build --no-cache

# Pull latest base images
docker compose build --pull

# Build specific service only
docker compose build backend
```

## 🔍 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker daemon
docker info

# Check available resources
docker system df
docker system prune

# Reset to clean state
./dev-stop.sh
docker compose down -v
./dev-start.sh
```

#### Backend/Frontend Connection Issues
```bash
# Verify network connectivity
docker compose exec frontend curl -f http://backend:8000/health

# Check CORS configuration
grep ALLOWED_ORIGIN .env

# Verify environment variables
docker compose exec backend env | grep DATABASE_URL
```

#### Database Connection Problems
```bash
# Check PostgreSQL health
docker compose exec postgres pg_isready -U postgres

# View database logs
docker compose logs postgres

# Connect to database directly
docker compose exec postgres psql -U postgres -d sportsdb
```

#### Performance Issues
```bash
# Check container resource usage
docker stats

# Clear caches
docker system prune

# Restart specific service
docker compose restart backend
```

### Log Analysis
```bash
# All services logs
docker compose logs

# Specific service logs
docker compose logs backend

# Follow logs with timestamps
docker compose logs -f -t backend

# Filter logs by level
docker compose logs backend | grep ERROR
```

## 🌐 Production Considerations

### Security Notes
- Default passwords are for development only
- SSL/TLS disabled for local development
- Debug mode enabled for detailed error messages
- All ports exposed for development access

### Configuration Differences
- **Environment**: Set `ENVIRONMENT=production`
- **Debug**: Set `DEBUG=false`
- **Database**: Use production-grade PostgreSQL
- **Redis**: Configure persistence and clustering
- **Secrets**: Use proper secret management
- **Monitoring**: Configure external monitoring services

### Deployment Patterns
This development environment provides a foundation for:
- **Docker Swarm**: Multi-node orchestration
- **Kubernetes**: Cloud-native deployment
- **Cloud Services**: AWS ECS, Google Cloud Run, etc.
- **CI/CD**: GitHub Actions, GitLab CI integration

## 📚 Additional Resources

### Documentation
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Development](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

### Monitoring & Observability
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry](https://opentelemetry.io/docs/)

### Development Tools
- [Adminer Documentation](https://www.adminer.org/)
- [Redis Commander](https://joeferner.github.io/redis-commander/)
- [MinIO Documentation](https://docs.min.io/)

---

## 🤝 Contributing

When adding new services or modifying the Docker configuration:

1. **Update docker-compose.yml** for core services
2. **Use docker-compose.override.yml** for development-only services
3. **Add appropriate profiles** for optional services
4. **Include health checks** for all services
5. **Update documentation** and scripts
6. **Test complete stack startup** with `./scripts/health-check.sh`

This ensures a consistent, reliable development experience for all team members.