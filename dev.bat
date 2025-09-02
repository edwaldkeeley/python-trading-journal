@echo off
echo 🚀 Starting Trading Journal Backend Development Environment...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

echo 📦 Building development containers...
docker-compose -f docker-compose.dev.yml build

echo 🔄 Starting services with hot reloading...
echo.
echo 💡 The backend will automatically reload when you make code changes!
echo 💡 Press Ctrl+C to stop the development environment
echo.

docker-compose -f docker-compose.dev.yml up

pause
