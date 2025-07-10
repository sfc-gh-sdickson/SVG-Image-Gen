#!/bin/bash

# State API Server Deployment Script
# Supports multiple deployment modes for SiS compatibility

set -e

# Configuration
API_PORT=${API_PORT:-8000}
DASHBOARD_PORT=${DASHBOARD_PORT:-80}
CONTAINER_NAME="svg-state-api"
IMAGE_NAME="svg-state-api:latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

# Deploy using Docker Compose (recommended)
deploy_compose() {
    log_info "Deploying State API Server using Docker Compose..."

    cd docker/state-api

    # Build and start services
    docker-compose up -d --build

    log_info "State API Server deployed successfully!"
    log_info "API available at: http://localhost:${API_PORT}"
    log_info "Dashboard available at: http://localhost:${DASHBOARD_PORT}"
    log_info "Health check: http://localhost:${API_PORT}/health"

    cd ../..
}

# Deploy using Docker only
deploy_docker() {
    log_info "Deploying State API Server using Docker..."

    # Build image
    docker build -f docker/state-api/Dockerfile -t ${IMAGE_NAME} .

    # Stop existing container if running
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true

    # Run container
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${API_PORT}:8000 \
        -e PYTHONPATH=/app \
        -e LOG_LEVEL=INFO \
        --restart unless-stopped \
        ${IMAGE_NAME}

    log_info "State API Server deployed successfully!"
    log_info "API available at: http://localhost:${API_PORT}"
    log_info "Health check: http://localhost:${API_PORT}/health"
}

# Deploy locally (development)
deploy_local() {
    log_info "Starting State API Server locally..."

    # Check if port is available
    if lsof -Pi :${API_PORT} -sTCP:LISTEN -t >/dev/null ; then
        log_warn "Port ${API_PORT} is already in use. Stopping existing process..."
        lsof -ti:${API_PORT} | xargs kill -9
    fi

    # Start server
    python start_state_api.py &
    SERVER_PID=$!

    # Wait for server to start
    sleep 3

    # Check if server is running
    if curl -f http://localhost:${API_PORT}/health >/dev/null 2>&1; then
        log_info "State API Server started successfully!"
        log_info "API available at: http://localhost:${API_PORT}"
        log_info "Dashboard available at: http://localhost:${API_PORT}"
        log_info "Health check: http://localhost:${API_PORT}/health"
        log_info "Server PID: ${SERVER_PID}"
        log_info "To stop: kill ${SERVER_PID}"
    else
        log_error "Failed to start State API Server"
        exit 1
    fi
}

# Deploy to Snowflake (placeholder for future implementation)
deploy_snowflake() {
    log_warn "Snowflake deployment not yet implemented"
    log_info "For Snowflake deployment, consider:"
    log_info "1. Using Snowflake's container services"
    log_info "2. Using external container registry"
    log_info "3. Using lightweight serverless functions"
}

# Stop services
stop_services() {
    log_info "Stopping State API Server..."

    # Try Docker Compose first
    if [ -f "docker/state-api/docker-compose.yml" ]; then
        cd docker/state-api
        docker-compose down 2>/dev/null || true
        cd ../..
    fi

    # Try Docker container
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true

    # Try local process
    if lsof -Pi :${API_PORT} -sTCP:LISTEN -t >/dev/null ; then
        lsof -ti:${API_PORT} | xargs kill -9
    fi

    log_info "State API Server stopped"
}

# Show status
show_status() {
    log_info "Checking State API Server status..."

    # Check Docker Compose
    if [ -f "docker/state-api/docker-compose.yml" ]; then
        cd docker/state-api
        docker-compose ps
        cd ../..
    fi

    # Check Docker container
    docker ps --filter name=${CONTAINER_NAME} 2>/dev/null || true

    # Check local process
    if lsof -Pi :${API_PORT} -sTCP:LISTEN -t >/dev/null ; then
        log_info "Local server running on port ${API_PORT}"
    fi

    # Test health endpoint
    if curl -f http://localhost:${API_PORT}/health >/dev/null 2>&1; then
        log_info "Health check: OK"
    else
        log_warn "Health check: FAILED"
    fi
}

# Show logs
show_logs() {
    log_info "Showing State API Server logs..."

    # Try Docker Compose logs
    if [ -f "docker/state-api/docker-compose.yml" ]; then
        cd docker/state-api
        docker-compose logs -f state-api
        cd ../..
        return
    fi

    # Try Docker container logs
    if docker ps --filter name=${CONTAINER_NAME} --format "{{.Names}}" | grep -q ${CONTAINER_NAME}; then
        docker logs -f ${CONTAINER_NAME}
        return
    fi

    log_warn "No running State API Server found"
}

# Main script
case "${1:-help}" in
    "compose")
        check_docker_compose
        deploy_compose
        ;;
    "docker")
        check_docker
        deploy_docker
        ;;
    "local")
        deploy_local
        ;;
    "snowflake")
        deploy_snowflake
        ;;
    "stop")
        stop_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "help"|*)
        echo "State API Server Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  compose    - Deploy using Docker Compose (recommended)"
        echo "  docker     - Deploy using Docker only"
        echo "  local      - Deploy locally for development"
        echo "  snowflake  - Deploy to Snowflake (placeholder)"
        echo "  stop       - Stop all services"
        echo "  status     - Show service status"
        echo "  logs       - Show service logs"
        echo "  help       - Show this help"
        echo ""
        echo "Environment variables:"
        echo "  API_PORT        - API server port (default: 8000)"
        echo "  DASHBOARD_PORT  - Dashboard port (default: 80)"
        echo ""
        echo "Examples:"
        echo "  $0 compose                    # Deploy with Docker Compose"
        echo "  $0 local                      # Deploy locally"
        echo "  API_PORT=9000 $0 docker      # Deploy with custom port"
        ;;
esac
