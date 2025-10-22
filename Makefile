# Docwheech MVP Makefile
# Provides convenient commands for Docker management

.PHONY: help build up down logs shell-backend shell-frontend shell-db clean test

# Default target
help:
	@echo "Docwheech MVP - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make setup     - Initial project setup"
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start all services in development mode"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Show logs for all services"
	@echo ""
	@echo "Database:"
	@echo "  make db-shell  - Connect to PostgreSQL shell"
	@echo "  make db-reset  - Reset database (WARNING: destroys data)"
	@echo "  make migrate   - Run database migrations"
	@echo ""
	@echo "Development Shells:"
	@echo "  make shell-backend  - Open backend container shell"
	@echo "  make shell-frontend - Open frontend container shell"
	@echo "  make shell-redis    - Open Redis CLI"
	@echo ""
	@echo "Testing:"
	@echo "  make test      - Run all tests"
	@echo "  make test-backend - Run backend tests"
	@echo "  make test-frontend - Run frontend tests"
	@echo ""
	@echo "Production:"
	@echo "  make prod-build - Build for production"
	@echo "  make prod-up    - Start production services"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean     - Clean up Docker resources"
	@echo "  make clean-all - Clean up everything (including volumes)"

# Development commands
setup:
	@echo "🚀 Setting up Docwheech MVP..."
	@if [ ! -f .env ]; then cp env.example .env; echo "⚠️  Please update .env file with your configuration"; fi
	@mkdir -p logs backend/uploads
	@echo "✅ Setup complete!"

build:
	@echo "🔨 Building Docker images..."
	docker-compose build

up:
	@echo "🚀 Starting development environment..."
	docker-compose up -d

down:
	@echo "🛑 Stopping all services..."
	docker-compose down

restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart

logs:
	docker-compose logs -f

# Database commands
db-shell:
	@echo "🗄️  Connecting to PostgreSQL..."
	docker-compose exec postgres psql -U docwheech_user -d docwheech

db-reset:
	@echo "⚠️  Resetting database (this will destroy all data)..."
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	docker-compose up -d postgres redis
	@echo "✅ Database reset complete!"

migrate:
	@echo "📊 Running database migrations..."
	docker-compose exec backend alembic upgrade head

# Shell access
shell-backend:
	@echo "🐍 Opening backend shell..."
	docker-compose exec backend /bin/bash

shell-frontend:
	@echo "⚛️  Opening frontend shell..."
	docker-compose exec frontend /bin/sh

shell-redis:
	@echo "🔴 Opening Redis CLI..."
	docker-compose exec redis redis-cli

# Testing
test:
	@echo "🧪 Running all tests..."
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

test-backend:
	@echo "🧪 Running backend tests..."
	docker-compose exec backend pytest

test-frontend:
	@echo "🧪 Running frontend tests..."
	docker-compose exec frontend npm test

# Production commands
prod-build:
	@echo "🏭 Building production images..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	@echo "🏭 Starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Maintenance
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down
	docker system prune -f

clean-all:
	@echo "🧹 Cleaning up everything (including volumes)..."
	@echo "⚠️  This will destroy all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v --remove-orphans
	docker system prune -af
	docker volume prune -f

# Quick development workflow
dev: setup build up
	@echo "🎉 Development environment ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
