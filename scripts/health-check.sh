#!/bin/bash

# Docwheech Health Check Script
# Checks the health of all services

set -e

echo "🏥 Docwheech Health Check"
echo "========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        return 1
    fi
}

# Function to check Docker container status
check_container() {
    local container=$1
    
    echo -n "Checking container $container... "
    
    if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Not Running${NC}"
        return 1
    fi
}

# Check Docker containers
echo "🐳 Docker Containers:"
check_container "docwheech_postgres"
check_container "docwheech_redis"
check_container "docwheech_backend"
check_container "docwheech_frontend"

echo ""

# Check service endpoints
echo "🌐 Service Endpoints:"
check_service "Backend API" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:3000"
check_service "API Documentation" "http://localhost:8000/docs"

echo ""

# Check database connectivity
echo "🗄️  Database Connectivity:"
echo -n "Checking PostgreSQL connection... "
if docker-compose exec -T postgres pg_isready -U docwheech_user -d docwheech > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected${NC}"
else
    echo -e "${RED}❌ Connection Failed${NC}"
fi

# Check Redis connectivity
echo -n "Checking Redis connection... "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected${NC}"
else
    echo -e "${RED}❌ Connection Failed${NC}"
fi

echo ""
echo "🏥 Health check complete!"
