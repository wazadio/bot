#!/bin/bash

# Docker management script for KK Telegram Bot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_warning "Please copy .env.example to .env and fill in your configuration:"
    echo "cp .env.example .env"
    exit 1
fi

case "${1:-help}" in
    build)
        print_status "Building Docker image..."
        docker-compose build --no-cache
        ;;
    up)
        print_status "Starting services..."
        docker-compose up -d
        print_status "Services started. Use 'docker-compose logs -f telegram-bot' to view logs."
        ;;
    down)
        print_status "Stopping services..."
        docker-compose down
        ;;
    restart)
        print_status "Restarting services..."
        docker-compose restart
        ;;
    logs)
        print_status "Showing logs..."
        docker-compose logs -f "${2:-telegram-bot}"
        ;;
    status)
        print_status "Service status:"
        docker-compose ps
        ;;
    shell)
        print_status "Opening shell in telegram-bot container..."
        docker-compose exec telegram-bot /bin/bash
        ;;
    redis)
        print_status "Starting Redis Commander (available at http://localhost:8081)..."
        docker-compose --profile tools up -d redis-commander
        ;;
    clean)
        print_warning "Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        ;;
    help|*)
        echo "KK Telegram Bot Docker Management Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  build     Build the Docker image"
        echo "  up        Start all services"
        echo "  down      Stop all services"
        echo "  restart   Restart all services"
        echo "  logs      Show logs (optional: specify service name)"
        echo "  status    Show service status"
        echo "  shell     Open bash shell in telegram-bot container"
        echo "  redis     Start Redis Commander web interface"
        echo "  clean     Clean up Docker resources"
        echo "  help      Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 up                    # Start all services"
        echo "  $0 logs                  # Show telegram-bot logs"
        echo "  $0 logs redis            # Show redis logs"
        echo "  $0 shell                 # Open shell in telegram-bot container"
        ;;
esac
