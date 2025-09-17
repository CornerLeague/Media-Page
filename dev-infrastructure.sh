#!/bin/bash

# =================================================================
# Corner League Media - Infrastructure Management Script
# =================================================================
# Comprehensive Docker Compose infrastructure management
# with support for different service profiles and environments
# =================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.docker"
PROJECT_NAME="corner-league-media"

# =================================================================
# UTILITY FUNCTIONS
# =================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    log_success "Dependencies check passed"
}

check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.docker.example" ]; then
            log_warning "No $ENV_FILE found. Copying from .env.docker.example"
            cp .env.docker.example "$ENV_FILE"
            log_info "Please edit $ENV_FILE with your configuration"
        else
            log_error "No environment file found. Please create $ENV_FILE"
            exit 1
        fi
    fi
}

wait_for_health() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=1

    log_info "Waiting for $service to be healthy..."

    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps "$service" | grep -q "healthy"; then
            log_success "$service is healthy"
            return 0
        fi

        echo -n "."
        sleep 2
        ((attempt++))
    done

    log_error "$service did not become healthy within $((max_attempts * 2)) seconds"
    return 1
}

show_service_status() {
    log_info "Service Status:"
    docker-compose ps
    echo ""

    log_info "Service Health Checks:"
    for service in postgres redis backend frontend; do
        if docker-compose ps "$service" | grep -q "Up"; then
            health=$(docker-compose ps "$service" | awk '{print $5}' | tail -n 1)
            echo "  $service: $health"
        else
            echo "  $service: Not running"
        fi
    done
    echo ""
}

show_service_urls() {
    log_info "Service URLs:"
    echo "  Frontend:          http://localhost:8080"
    echo "  Backend API:       http://localhost:8000"
    echo "  Backend Docs:      http://localhost:8000/docs"
    echo "  Backend Health:    http://localhost:8000/health"
    echo "  Nginx Proxy:       http://localhost"
    echo ""
    echo "  Database (Postgres): localhost:5432"
    echo "  Cache (Redis):       localhost:6379"
    echo ""
    echo "Development Tools (with --dev-tools):"
    echo "  Adminer (DB):      http://localhost:8081"
    echo "  Redis Commander:   http://localhost:8082"
    echo ""
    echo "Monitoring (with --monitoring):"
    echo "  Grafana:           http://localhost:3000"
    echo "  Prometheus:        http://localhost:9090"
    echo ""
    echo "Observability (with --observability):"
    echo "  Jaeger UI:         http://localhost:16686"
    echo "  OTEL Collector:    http://localhost:8888"
    echo ""
}

# =================================================================
# MAIN COMMANDS
# =================================================================

start_infrastructure() {
    local profiles=""
    local wait_for_health_checks=true
    local detached=true

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --monitoring)
                profiles="$profiles,monitoring"
                shift
                ;;
            --observability)
                profiles="$profiles,observability"
                shift
                ;;
            --dev-tools)
                profiles="$profiles,dev-tools"
                shift
                ;;
            --full)
                profiles="$profiles,monitoring,observability,dev-tools"
                shift
                ;;
            --no-wait)
                wait_for_health_checks=false
                shift
                ;;
            --foreground)
                detached=false
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Remove leading comma if present
    profiles=${profiles#,}

    check_dependencies
    check_env_file

    log_info "Starting Corner League Media infrastructure..."

    if [ -n "$profiles" ]; then
        log_info "Using profiles: $profiles"
        export COMPOSE_PROFILES="$profiles"
    fi

    # Start services
    if [ "$detached" = true ]; then
        docker-compose --env-file "$ENV_FILE" up -d
    else
        docker-compose --env-file "$ENV_FILE" up
        return 0
    fi

    # Wait for core services to be healthy
    if [ "$wait_for_health_checks" = true ]; then
        log_info "Waiting for core services to be healthy..."
        wait_for_health postgres 30
        wait_for_health redis 20
        wait_for_health backend 60
        wait_for_health frontend 60

        # Wait for optional services if enabled
        if [[ "$profiles" == *"observability"* ]]; then
            wait_for_health jaeger 30
            wait_for_health otel-collector 30
        fi
    fi

    show_service_status
    show_service_urls

    log_success "Infrastructure started successfully!"
}

stop_infrastructure() {
    log_info "Stopping Corner League Media infrastructure..."
    docker-compose --env-file "$ENV_FILE" down
    log_success "Infrastructure stopped"
}

restart_infrastructure() {
    log_info "Restarting Corner League Media infrastructure..."
    stop_infrastructure
    sleep 2
    start_infrastructure "$@"
}

clean_infrastructure() {
    log_warning "This will remove all containers, networks, and volumes"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up infrastructure..."
        docker-compose --env-file "$ENV_FILE" down -v --remove-orphans
        docker system prune -f
        log_success "Infrastructure cleaned up"
    else
        log_info "Cleanup cancelled"
    fi
}

show_logs() {
    local service=${1:-}
    local follow=${2:-}

    if [ -n "$service" ]; then
        if [ "$follow" = "--follow" ] || [ "$follow" = "-f" ]; then
            docker-compose --env-file "$ENV_FILE" logs -f "$service"
        else
            docker-compose --env-file "$ENV_FILE" logs --tail=50 "$service"
        fi
    else
        docker-compose --env-file "$ENV_FILE" logs --tail=20
    fi
}

show_status() {
    show_service_status
    show_service_urls
}

run_health_checks() {
    log_info "Running comprehensive health checks..."

    # Core services health checks
    local services=("postgres" "redis" "backend" "frontend")
    local healthy=0
    local total=${#services[@]}

    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "healthy"; then
            log_success "$service: Healthy"
            ((healthy++))
        elif docker-compose ps "$service" | grep -q "Up"; then
            log_warning "$service: Running but no health check"
        else
            log_error "$service: Not running"
        fi
    done

    # API endpoint checks
    log_info "Checking API endpoints..."

    if curl -sf http://localhost:8000/health > /dev/null; then
        log_success "Backend API: Responsive"
        ((healthy++))
    else
        log_error "Backend API: Not responding"
    fi

    if curl -sf http://localhost:8080 > /dev/null; then
        log_success "Frontend: Responsive"
        ((healthy++))
    else
        log_error "Frontend: Not responding"
    fi

    log_info "Health check summary: $healthy/$(($total + 2)) services healthy"

    if [ $healthy -eq $(($total + 2)) ]; then
        log_success "All services are healthy!"
        return 0
    else
        log_warning "Some services are not healthy"
        return 1
    fi
}

show_help() {
    echo "Corner League Media Infrastructure Management"
    echo ""
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start           Start the infrastructure"
    echo "  stop            Stop the infrastructure"
    echo "  restart         Restart the infrastructure"
    echo "  status          Show service status and URLs"
    echo "  logs [service]  Show logs (optionally for specific service)"
    echo "  health          Run comprehensive health checks"
    echo "  clean           Clean up all containers and volumes"
    echo "  help            Show this help message"
    echo ""
    echo "Start Options:"
    echo "  --monitoring        Include Grafana and Prometheus"
    echo "  --observability     Include Jaeger and OpenTelemetry"
    echo "  --dev-tools         Include Adminer and Redis Commander"
    echo "  --full              Include all optional services"
    echo "  --no-wait           Don't wait for health checks"
    echo "  --foreground        Run in foreground (don't detach)"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start core services only"
    echo "  $0 start --full             # Start all services"
    echo "  $0 start --dev-tools        # Start with development tools"
    echo "  $0 logs backend             # Show backend logs"
    echo "  $0 logs backend --follow    # Follow backend logs"
    echo ""
}

# =================================================================
# MAIN EXECUTION
# =================================================================

# Check if running in project directory
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "docker-compose.yml not found. Please run from project root."
    exit 1
fi

# Parse command
case "${1:-}" in
    start)
        shift
        start_infrastructure "$@"
        ;;
    stop)
        stop_infrastructure
        ;;
    restart)
        shift
        restart_infrastructure "$@"
        ;;
    status)
        show_status
        ;;
    logs)
        shift
        show_logs "$@"
        ;;
    health)
        run_health_checks
        ;;
    clean)
        clean_infrastructure
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        log_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac