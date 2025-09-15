#!/bin/bash

# =================================================================
# Corner League Media - Health Check Script
# =================================================================
# Comprehensive health check for all services in the development stack
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
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to check if a service is running
check_service_running() {
    local service_name=$1
    if docker compose ps | grep -q "$service_name.*running"; then
        return 0
    else
        return 1
    fi
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local service_name=$2
    local timeout=${3:-10}

    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check HTTP endpoint with expected response
check_http_with_response() {
    local url=$1
    local expected=$2
    local service_name=$3
    local timeout=${4:-10}

    response=$(curl -s --max-time $timeout "$url" 2>/dev/null || echo "")
    if echo "$response" | grep -q "$expected"; then
        return 0
    else
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    print_status "Checking PostgreSQL database..."

    if check_service_running "postgres"; then
        print_success "PostgreSQL container is running"

        # Check database connectivity
        if docker exec corner-league-postgres pg_isready -U postgres -d sportsdb > /dev/null 2>&1; then
            print_success "PostgreSQL database is accessible"
        else
            print_error "PostgreSQL database is not responding"
            return 1
        fi
    else
        print_error "PostgreSQL container is not running"
        return 1
    fi
}

# Function to check Redis
check_redis() {
    print_status "Checking Redis cache..."

    if check_service_running "redis"; then
        print_success "Redis container is running"

        # Check Redis connectivity
        if docker exec corner-league-redis redis-cli ping | grep -q "PONG"; then
            print_success "Redis is responding to ping"
        else
            print_error "Redis is not responding"
            return 1
        fi
    else
        print_error "Redis container is not running"
        return 1
    fi
}

# Function to check backend API
check_backend() {
    print_status "Checking FastAPI backend..."

    if check_service_running "backend"; then
        print_success "Backend container is running"

        # Check health endpoint
        if check_http_with_response "http://localhost:8000/health" "healthy" "backend" 15; then
            print_success "Backend health endpoint is responding"
        else
            print_error "Backend health endpoint is not responding"
            return 1
        fi

        # Check API documentation
        if check_http_endpoint "http://localhost:8000/docs" "backend-docs" 10; then
            print_success "Backend API documentation is accessible"
        else
            print_warning "Backend API documentation may not be accessible"
        fi
    else
        print_error "Backend container is not running"
        return 1
    fi
}

# Function to check frontend
check_frontend() {
    print_status "Checking React frontend..."

    if check_service_running "frontend"; then
        print_success "Frontend container is running"

        # Check frontend accessibility
        if check_http_endpoint "http://localhost:8080" "frontend" 15; then
            print_success "Frontend is accessible"
        else
            print_error "Frontend is not accessible"
            return 1
        fi
    else
        print_error "Frontend container is not running"
        return 1
    fi
}

# Function to check development tools
check_dev_tools() {
    print_status "Checking development tools..."

    # Check Adminer
    if check_service_running "adminer"; then
        if check_http_endpoint "http://localhost:8081" "adminer" 10; then
            print_success "Adminer (Database UI) is accessible"
        else
            print_warning "Adminer is running but not accessible"
        fi
    else
        print_warning "Adminer is not running (use profile: tools)"
    fi

    # Check Redis Commander
    if check_service_running "redis-commander"; then
        if check_http_endpoint "http://localhost:8082" "redis-commander" 10; then
            print_success "Redis Commander is accessible"
        else
            print_warning "Redis Commander is running but not accessible"
        fi
    else
        print_warning "Redis Commander is not running (use profile: tools)"
    fi
}

# Function to check monitoring stack
check_monitoring() {
    print_status "Checking monitoring stack..."

    # Check Grafana
    if check_service_running "grafana"; then
        if check_http_endpoint "http://localhost:3000" "grafana" 10; then
            print_success "Grafana is accessible"
        else
            print_warning "Grafana is running but not accessible"
        fi
    else
        print_warning "Grafana is not running (use profile: monitoring)"
    fi

    # Check Prometheus
    if check_service_running "prometheus"; then
        if check_http_endpoint "http://localhost:9090" "prometheus" 10; then
            print_success "Prometheus is accessible"
        else
            print_warning "Prometheus is running but not accessible"
        fi
    else
        print_warning "Prometheus is not running (use profile: monitoring)"
    fi

    # Check Jaeger
    if check_service_running "jaeger"; then
        if check_http_endpoint "http://localhost:16686" "jaeger" 10; then
            print_success "Jaeger UI is accessible"
        else
            print_warning "Jaeger is running but not accessible"
        fi
    else
        print_warning "Jaeger is not running (use profile: monitoring)"
    fi
}

# Function to check overall system health
check_system_health() {
    print_status "Checking system resources..."

    # Check Docker daemon
    if docker info > /dev/null 2>&1; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not accessible"
        return 1
    fi

    # Check disk space
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 90 ]; then
        print_success "Disk space is adequate (${disk_usage}% used)"
    else
        print_warning "Disk space is getting low (${disk_usage}% used)"
    fi

    # Check memory usage (if available)
    if command -v free > /dev/null; then
        memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ "$memory_usage" -lt 90 ]; then
            print_success "Memory usage is acceptable (${memory_usage}% used)"
        else
            print_warning "Memory usage is high (${memory_usage}% used)"
        fi
    fi
}

# Function to display service summary
display_summary() {
    echo ""
    echo "==================================================================="
    echo -e "${BLUE}Service Access Summary${NC}"
    echo "==================================================================="
    echo ""
    echo "🌐 Core Application:"
    echo "   Frontend:         http://localhost:8080"
    echo "   Backend API:      http://localhost:8000"
    echo "   API Docs:         http://localhost:8000/docs"
    echo ""
    echo "🛠️  Development Tools:"
    echo "   Database Admin:   http://localhost:8081"
    echo "   Redis Admin:      http://localhost:8082"
    echo "   Email Testing:    http://localhost:8025 (if running)"
    echo ""
    echo "📊 Monitoring & Observability:"
    echo "   Grafana:          http://localhost:3000"
    echo "   Prometheus:       http://localhost:9090"
    echo "   Jaeger Tracing:   http://localhost:16686"
    echo ""
    echo "🔧 Service Commands:"
    echo "   Start tools:      docker compose --profile tools up -d"
    echo "   Start monitoring: docker compose --profile monitoring up -d"
    echo "   View logs:        ./dev-logs.sh"
    echo "   Stop all:         ./dev-stop.sh"
    echo ""
}

# Main execution
main() {
    echo "==================================================================="
    echo -e "${BLUE}Corner League Media - Health Check${NC}"
    echo "==================================================================="
    echo ""

    # Track overall health
    overall_health=0

    # Check core services
    check_system_health || ((overall_health++))
    echo ""

    check_database || ((overall_health++))
    echo ""

    check_redis || ((overall_health++))
    echo ""

    check_backend || ((overall_health++))
    echo ""

    check_frontend || ((overall_health++))
    echo ""

    # Check optional services
    check_dev_tools
    echo ""

    check_monitoring
    echo ""

    # Display summary
    display_summary

    # Final status
    if [ $overall_health -eq 0 ]; then
        print_success "All core services are healthy!"
        echo ""
        exit 0
    else
        print_error "Some services have issues. Check the output above for details."
        echo ""
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--quick|-q] [--help|-h]"
        echo ""
        echo "Options:"
        echo "  --quick, -q   Quick check (core services only)"
        echo "  --help, -h    Show this help message"
        exit 0
        ;;
    --quick|-q)
        # Quick check mode (core services only)
        check_database && check_redis && check_backend && check_frontend
        ;;
    *)
        main "$@"
        ;;
esac