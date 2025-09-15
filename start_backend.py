#!/usr/bin/env python3
"""Quick start script for Corner League Media API backend."""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_redis():
    """Check if Redis is running."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis is running")
        return True
    except Exception as e:
        print(f"✗ Redis is not running: {str(e)}")
        return False

def start_redis():
    """Start Redis if not running."""
    print("Starting Redis with Docker...")
    try:
        subprocess.run([
            "docker", "run", "-d", "--name", "redis-cornerleague",
            "-p", "6379:6379", "redis:7-alpine"
        ], check=True, capture_output=True)
        print("✓ Redis started successfully")
        time.sleep(2)  # Wait for Redis to start
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to start Redis with Docker")
        print("Please install Docker or start Redis manually:")
        print("  brew install redis && redis-server")
        return False

def start_api():
    """Start the FastAPI server."""
    app_dir = Path(__file__).parent / "app"
    os.chdir(app_dir)

    print("Starting Corner League Media API...")
    print("=" * 50)
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 50)

    try:
        subprocess.run([sys.executable, "start.py"], check=True)
    except KeyboardInterrupt:
        print("\nAPI stopped by user")
    except Exception as e:
        print(f"Failed to start API: {str(e)}")

def main():
    """Main function."""
    print("Corner League Media API - Quick Start")
    print("=" * 40)

    # Check if Redis is running
    if not check_redis():
        if not start_redis():
            return 1

        # Check again after starting
        if not check_redis():
            return 1

    # Start the API
    start_api()
    return 0

if __name__ == "__main__":
    sys.exit(main())