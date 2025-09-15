#!/bin/bash

# =================================================================
# Corner League Media - View Development Logs
# =================================================================

set -e

# Colors for output
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE=${1:-}

echo "==================================================================="
echo -e "${BLUE}Corner League Media - Development Logs${NC}"
echo "==================================================================="

if [ -n "$SERVICE" ]; then
    echo "Following logs for service: $SERVICE"
    echo "Press Ctrl+C to stop following logs"
    echo ""
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f "$SERVICE"
else
    echo "Following logs for all services"
    echo "Press Ctrl+C to stop following logs"
    echo ""
    echo "Available services:"
    echo "  backend, frontend, postgres, redis, nginx, adminer, redis-commander"
    echo ""
    echo "To view logs for a specific service: $0 <service-name>"
    echo ""
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
fi