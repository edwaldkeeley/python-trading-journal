#!/bin/bash

# Development script for Trading Journal Backend
# This script sets up the development environment with hot reloading

echo "🚀 Starting Trading Journal Backend Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping development environment..."
    docker-compose -f docker-compose.dev.yml down
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "📦 Building development containers..."
docker-compose -f docker-compose.dev.yml build

echo "🔄 Starting services with hot reloading..."
docker-compose -f docker-compose.dev.yml up

# Keep script running
wait
