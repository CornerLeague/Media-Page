#!/bin/bash

# =================================================================
# Corner League Media - Stop Development Environment
# =================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "==================================================================="
echo -e "${BLUE}Corner League Media - Stopping Development Environment${NC}"
echo "==================================================================="

print_status "Stopping all services..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml down

if [ "$1" = "--clean" ] || [ "$1" = "-c" ]; then
    print_warning "Removing volumes and cleaning up..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
    docker system prune -f
    print_success "Environment cleaned"
fi

print_success "Development environment stopped"

echo ""
echo "To start again, run: ./dev-start.sh"
echo "To clean everything, run: $0 --clean"
echo ""