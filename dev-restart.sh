#!/bin/bash

# =================================================================
# Corner League Media - Restart Development Environment
# =================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE=${1:-}

echo "==================================================================="
echo -e "${BLUE}Corner League Media - Restart Development Environment${NC}"
echo "==================================================================="

if [ -n "$SERVICE" ]; then
    echo -e "${BLUE}[INFO]${NC} Restarting service: $SERVICE"
    docker compose -f docker-compose.yml -f docker-compose.dev.yml restart "$SERVICE"
    echo -e "${GREEN}[SUCCESS]${NC} Service $SERVICE restarted"
else
    echo -e "${BLUE}[INFO]${NC} Restarting all services..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml restart
    echo -e "${GREEN}[SUCCESS]${NC} All services restarted"
fi

echo ""
echo "To view logs: ./dev-logs.sh"
echo "To view specific service logs: ./dev-logs.sh <service-name>"
echo ""