#!/bin/bash

# Docwheech MVP Setup Script
echo "🚀 Setting up Docwheech MVP..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy environment file
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update .env file with your actual configuration values"
fi

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p backend/uploads

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose build
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys and configuration"
echo "2. Run 'docker-compose up' to start all services"
echo "3. Visit http://localhost:3000 for the frontend"
echo "4. Visit http://localhost:8000/docs for the API documentation"
