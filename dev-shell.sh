#!/bin/bash

# =================================================================
# Corner League Media - Access Service Shell
# =================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SERVICE=${1:-backend}
SHELL_CMD=${2:-bash}

echo "==================================================================="
echo -e "${BLUE}Corner League Media - Service Shell Access${NC}"
echo "==================================================================="

# Check if service is running
if ! docker compose -f docker-compose.yml -f docker-compose.dev.yml ps | grep -q "$SERVICE.*running"; then
    echo -e "${RED}[ERROR]${NC} Service '$SERVICE' is not running"
    echo ""
    echo "Available running services:"
    docker compose -f docker-compose.yml -f docker-compose.dev.yml ps --services --filter "status=running"
    echo ""
    echo "Start services with: ./dev-start.sh"
    exit 1
fi

echo -e "${GREEN}[INFO]${NC} Accessing shell for service: $SERVICE"
echo -e "${GREEN}[INFO]${NC} Shell command: $SHELL_CMD"
echo ""

# Special handling for different services
case "$SERVICE" in
    "backend")
        echo "🐍 Python Backend Shell"
        echo "Available commands: python, pip, pytest, black, isort"
        echo "Working directory: /app"
        ;;
    "frontend")
        echo "📦 Node.js Frontend Shell"
        echo "Available commands: npm, yarn, node"
        echo "Working directory: /app"
        ;;
    "postgres")
        echo "🐘 PostgreSQL Database Shell"
        echo "Available commands: psql, pg_dump, pg_restore"
        SHELL_CMD="psql -U postgres -d sportsdb"
        ;;
    "redis")
        echo "⚡ Redis Shell"
        echo "Available commands: redis-cli"
        SHELL_CMD="redis-cli"
        ;;
esac

echo ""
echo "Type 'exit' to return to host shell"
echo "==================================================================="

# Execute shell in container
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec "$SERVICE" $SHELL_CMD