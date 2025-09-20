#!/bin/bash

# =================================================================
# Corner League Media - Infrastructure Setup Script
# =================================================================
# First-time setup for development infrastructure
# This script prepares the environment and validates the setup
# =================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_header() {
    echo "================================================================="
    echo "      Corner League Media - Infrastructure Setup"
    echo "================================================================="
    echo ""
}

check_requirements() {
    log_info "Checking system requirements..."

    local missing_deps=()

    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("Docker")
    else
        if ! docker version &> /dev/null; then
            log_error "Docker is installed but not running"
            exit 1
        fi
        log_success "Docker: $(docker --version)"
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_deps+=("Docker Compose")
    else
        if command -v docker-compose &> /dev/null; then
            log_success "Docker Compose: $(docker-compose --version)"
        else
            log_success "Docker Compose: $(docker compose version)"
        fi
    fi

    # Check curl
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi

    # Check Node.js (for frontend development)
    if ! command -v node &> /dev/null; then
        log_warning "Node.js not found (optional for local frontend development)"
    else
        log_success "Node.js: $(node --version)"
    fi

    # Check Python (for backend development)
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_warning "Python not found (optional for local backend development)"
    else
        if command -v python3 &> /dev/null; then
            log_success "Python: $(python3 --version)"
        else
            log_success "Python: $(python --version)"
        fi
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        echo ""
        echo "Please install the missing dependencies and run this script again."
        exit 1
    fi

    log_success "All requirements satisfied"
}

setup_environment() {
    log_info "Setting up environment configuration..."

    # Create .env.docker from template if it doesn't exist
    if [ ! -f ".env.docker" ]; then
        if [ -f ".env.docker.example" ]; then
            cp .env.docker.example .env.docker
            log_success "Created .env.docker from template"
        else
            log_error ".env.docker.example template not found"
            exit 1
        fi
    else
        log_info ".env.docker already exists"
    fi

    # Create directories for persistent data
    log_info "Creating data directories..."
    mkdir -p data/{postgres,redis,grafana,prometheus,jaeger}
    mkdir -p logs
    mkdir -p backups

    log_success "Environment setup complete"
}

validate_configuration() {
    log_info "Validating Docker Compose configuration..."

    # Validate docker-compose.yml
    if docker-compose config &> /dev/null; then
        log_success "Docker Compose configuration is valid"
    else
        log_error "Docker Compose configuration is invalid"
        docker-compose config
        exit 1
    fi

    # Check required files
    local required_files=(
        "docker-compose.yml"
        ".env.docker"
        "app/Dockerfile.dev"
        "otel/otel-collector.yml"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "Found: $file"
        else
            log_error "Missing required file: $file"
            exit 1
        fi
    done
}

check_port_availability() {
    log_info "Checking port availability..."

    local ports=(5432 6379 8000 8080 3000 9090 16686)
    local used_ports=()

    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            used_ports+=($port)
        fi
    done

    if [ ${#used_ports[@]} -ne 0 ]; then
        log_warning "The following ports are already in use:"
        for port in "${used_ports[@]}"; do
            echo "  - Port $port: $(lsof -Pi :$port -sTCP:LISTEN -P -n | head -2 | tail -1)"
        done
        echo ""
        echo "You may need to stop conflicting services or change port mappings in docker-compose.yml"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "All required ports are available"
    fi
}

pull_docker_images() {
    log_info "Pulling Docker images (this may take a while)..."

    # Pull core images
    docker-compose pull postgres redis

    # Build backend image
    if [ -f "app/Dockerfile.dev" ]; then
        log_info "Building backend development image..."
        docker-compose build backend
    fi

    log_success "Docker images ready"
}

test_infrastructure() {
    log_info "Testing infrastructure startup..."

    # Start core services
    log_info "Starting core services (postgres, redis, backend)..."
    docker-compose --env-file .env.docker up -d postgres redis

    # Wait for database
    log_info "Waiting for database to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose --env-file .env.docker exec -T postgres pg_isready -U postgres &> /dev/null; then
            log_success "Database is ready"
            break
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        log_error "Database failed to start within $((max_attempts * 2)) seconds"
        docker-compose --env-file .env.docker logs postgres
        exit 1
    fi

    # Wait for Redis
    log_info "Waiting for Redis to be ready..."
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose --env-file .env.docker exec -T redis redis-cli ping &> /dev/null; then
            log_success "Redis is ready"
            break
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        log_error "Redis failed to start within $((max_attempts * 2)) seconds"
        docker-compose --env-file .env.docker logs redis
        exit 1
    fi

    # Clean up test
    log_info "Cleaning up test containers..."
    docker-compose --env-file .env.docker down

    log_success "Infrastructure test completed successfully"
}

show_next_steps() {
    echo ""
    echo "================================================================="
    echo "                    Setup Complete!"
    echo "================================================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Review and customize .env.docker configuration:"
    echo "   - Set up Clerk authentication keys"
    echo "   - Configure AI API keys (DeepSeek/OpenAI)"
    echo "   - Adjust database passwords"
    echo ""
    echo "2. Start the infrastructure:"
    echo "   ./dev-infrastructure.sh start                 # Core services only"
    echo "   ./dev-infrastructure.sh start --dev-tools     # With admin tools"
    echo "   ./dev-infrastructure.sh start --full          # All services"
    echo ""
    echo "3. Check service status:"
    echo "   ./dev-infrastructure.sh status"
    echo "   ./dev-infrastructure.sh health"
    echo ""
    echo "4. View logs:"
    echo "   ./dev-infrastructure.sh logs                  # All services"
    echo "   ./dev-infrastructure.sh logs backend          # Specific service"
    echo ""
    echo "5. Access services:"
    echo "   Frontend:     http://localhost:8080"
    echo "   Backend API:  http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo ""
    echo "For help: ./dev-infrastructure.sh help"
    echo ""
}

# =================================================================
# MAIN EXECUTION
# =================================================================

print_header

# Check if running in project directory
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml not found. Please run from project root."
    exit 1
fi

# Run setup steps
check_requirements
setup_environment
validate_configuration
check_port_availability
pull_docker_images
test_infrastructure

show_next_steps

log_success "Infrastructure setup completed successfully!"