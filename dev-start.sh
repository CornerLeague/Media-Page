#!/bin/bash

# =================================================================
# Corner League Media - Development Environment Startup Script
# =================================================================
# This script starts the complete development environment
# =================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Created .env file from template"
            print_warning "Please review and update .env file with your configuration"
        else
            print_error ".env.example file not found. Cannot create .env file."
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/grafana
    print_success "Directories created"
}

# Function to stop existing containers
stop_existing() {
    print_status "Stopping any existing containers..."
    docker compose down --remove-orphans || true
    print_success "Existing containers stopped"
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    docker compose build --pull
    print_success "Images built successfully"
}

# Function to start services
start_services() {
    local with_tools=${1:-false}
    local with_monitoring=${2:-false}
    local with_storage=${3:-false}

    print_status "Starting development services..."

    # Build profiles array
    profiles=()
    if [ "$with_tools" = true ]; then
        profiles+=(--profile tools)
        print_status "Including development tools profile"
    fi
    if [ "$with_monitoring" = true ]; then
        profiles+=(--profile monitoring)
        print_status "Including monitoring profile"
    fi
    if [ "$with_storage" = true ]; then
        profiles+=(--profile storage)
        print_status "Including storage profile"
    fi

    # Start core services first
    print_status "Starting database and cache services..."
    docker compose up -d postgres redis

    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10

    # Start backend
    print_status "Starting backend service..."
    docker compose up -d backend

    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    sleep 15

    # Start frontend
    print_status "Starting frontend service..."
    docker compose up -d frontend

    # Start optional services with profiles
    if [ ${#profiles[@]} -gt 0 ]; then
        print_status "Starting optional services..."
        docker compose "${profiles[@]}" up -d
    fi

    # Start nginx last
    print_status "Starting reverse proxy..."
    docker compose up -d nginx

    print_success "All services started"
}

# Function to wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."

    # List of services to check
    services=("postgres" "redis" "backend" "frontend")

    for service in "${services[@]}"; do
        print_status "Checking health of $service..."
        timeout=60
        while [ $timeout -gt 0 ]; do
            if docker compose ps | grep -q "$service.*healthy\|$service.*running"; then
                print_success "$service is ready"
                break
            fi
            sleep 2
            ((timeout-=2))
        done

        if [ $timeout -le 0 ]; then
            print_warning "$service may not be fully ready yet"
        fi
    done
}

# Function to display service URLs
show_services() {
    echo ""
    echo "==================================================================="
    echo -e "${GREEN}Corner League Media - Development Environment${NC}"
    echo "==================================================================="
    echo ""
    echo "🚀 Services are starting up! Give them a moment to initialize..."
    echo ""
    echo "📱 Application:"
    echo "   Frontend:     http://localhost:8080"
    echo "   Backend API:  http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo ""
    echo "🛠️  Development Tools:"
    echo "   Database:     http://localhost:8081 (Adminer)"
    echo "   Redis:        http://localhost:8082 (Redis Commander)"
    echo ""
    echo "🌐 Unified Access (via Nginx):"
    echo "   Main App:     http://localhost"
    echo "   API:          http://localhost/api/"
    echo "   Tools:        http://tools.corner-league.local"
    echo ""
    echo "📊 Monitoring (optional):"
    echo "   Grafana:      http://localhost:3000"
    echo "   Prometheus:   http://localhost:9090"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   View logs:    ./dev-logs.sh"
    echo "   Stop all:     ./dev-stop.sh"
    echo "   Restart:      ./dev-restart.sh"
    echo "   Shell access: ./dev-shell.sh [service]"
    echo ""
    echo "==================================================================="
}

# Function to show logs
show_logs() {
    echo ""
    print_status "Showing recent logs..."
    docker compose logs --tail=50
    echo ""
    print_status "To follow logs in real-time, run: ./dev-logs.sh"
}

# Function to parse command line arguments
parse_arguments() {
    local with_tools=false
    local with_monitoring=false
    local with_storage=false
    local show_logs=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --tools|-t)
                with_tools=true
                shift
                ;;
            --monitoring|-m)
                with_monitoring=true
                shift
                ;;
            --storage|-s)
                with_storage=true
                shift
                ;;
            --all|-a)
                with_tools=true
                with_monitoring=true
                with_storage=true
                shift
                ;;
            --logs|-l)
                show_logs=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo "$with_tools $with_monitoring $with_storage $show_logs"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --tools, -t       Start with development tools (Adminer, Redis Commander)"
    echo "  --monitoring, -m  Start with monitoring stack (Grafana, Prometheus, Jaeger)"
    echo "  --storage, -s     Start with storage services (MinIO)"
    echo "  --all, -a         Start with all optional services"
    echo "  --logs, -l        Show logs after startup"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start core services only"
    echo "  $0 --tools           # Start with development tools"
    echo "  $0 --monitoring      # Start with monitoring stack"
    echo "  $0 --all --logs      # Start everything and show logs"
}

# Main execution
main() {
    echo "==================================================================="
    echo -e "${BLUE}Corner League Media - Development Environment Setup${NC}"
    echo "==================================================================="
    echo ""

    # Parse command line arguments
    read with_tools with_monitoring with_storage show_logs_flag <<< $(parse_arguments "$@")

    # Pre-flight checks
    check_docker
    check_env_file
    create_directories

    # Setup and start
    stop_existing
    build_images
    start_services "$with_tools" "$with_monitoring" "$with_storage"
    wait_for_services

    # Show status
    show_services

    # Optional: show logs
    if [ "$show_logs_flag" = "true" ]; then
        show_logs
    fi

    echo ""
    print_success "Development environment is ready!"
    print_status "Run './dev-logs.sh' to view logs or './dev-stop.sh' to stop all services"
    print_status "Run './scripts/health-check.sh' to verify all services are healthy"
    echo ""
}

# Handle script arguments
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    show_help
    exit 0
else
    main "$@"
fi