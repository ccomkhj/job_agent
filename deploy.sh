#!/bin/bash

# Job Agent Deployment Script

set -e

echo "🚀 Starting Job Agent deployment..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OPENROUTER_API_KEY"
    echo "You can copy from production.env and fill in your API key"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed!"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build and start the application
echo "🏗️  Building and starting containers..."
if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check if services are running
if curl -f http://localhost/health &> /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

if curl -f http://localhost/ &> /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "🌐 Application is running at: http://localhost"
echo "📊 Backend API at: http://localhost/api"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"