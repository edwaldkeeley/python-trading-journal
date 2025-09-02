# Development Setup with Hot Reloading

This setup provides automatic backend reloading when you make code changes, so you don't need to manually restart containers.

## 🚀 Quick Start

### Windows
```bash
# Double-click or run:
dev.bat
```

### Linux/Mac
```bash
# Make executable and run:
chmod +x dev.sh
./dev.sh
```

### Manual Docker Compose
```bash
# Build and start development environment
docker-compose -f docker-compose.dev.yml up --build
```

## 🔥 Hot Reloading Features

- **Automatic Restart**: Backend restarts automatically when you save code changes
- **File Watching**: Monitors all Python files in the `/app` directory
- **Fast Reloads**: Uses uvicorn's built-in reloader for quick restarts
- **Debug Logging**: Enhanced logging for development debugging

## 📁 File Structure

```
backend/
├── docker-compose.dev.yml    # Development compose file
├── Dockerfile.dev            # Development Dockerfile
├── dev.bat                   # Windows startup script
├── dev.sh                    # Linux/Mac startup script
└── .dockerignore            # Optimized build context
```

## ⚙️ Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Hot Reloading | ✅ Yes | ❌ No |
| Debug Logging | ✅ Yes | ❌ No |
| Volume Mounts | ✅ Yes | ❌ No |
| Source Code | Live Mounted | Copied into Image |
| Performance | Optimized for Dev | Optimized for Prod |

## 🔧 Configuration

### Environment Variables
- `ENVIRONMENT=development` - Enables development mode
- `LOG_LEVEL=DEBUG` - Detailed logging
- `RUN_MIGRATIONS_ON_STARTUP=true` - Auto-run migrations

### Volume Mounts
- `.:/app` - Live code mounting
- `/app/__pycache__` - Exclude Python cache
- `/app/.pytest_cache` - Exclude test cache

## 🚨 Troubleshooting

### Backend Not Reloading
1. Check if `--reload` flag is in the command
2. Verify volume mount is working: `docker-compose -f docker-compose.dev.yml exec web ls -la /app`
3. Check logs: `docker-compose -f docker-compose.dev.yml logs web`

### Permission Issues
1. Ensure Docker has access to your project directory
2. Check file ownership: `ls -la`
3. Restart Docker Desktop if on Windows/Mac

### Port Conflicts
1. Stop any existing containers: `docker-compose down`
2. Check if ports 8000 or 5432 are in use
3. Use different ports in docker-compose.dev.yml if needed

## 📝 Development Workflow

1. **Start Development Environment**
   ```bash
   ./dev.sh  # or dev.bat on Windows
   ```

2. **Make Code Changes**
   - Edit any Python file in the `app/` directory
   - Save the file
   - Backend automatically restarts

3. **View Logs**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f web
   ```

4. **Stop Environment**
   - Press `Ctrl+C` in the terminal
   - Or run: `docker-compose -f docker-compose.dev.yml down`

## 🎯 Benefits

- **Faster Development**: No more manual container restarts
- **Better Debugging**: Enhanced logging and error messages
- **Consistent Environment**: Same setup across team members
- **Production Parity**: Development environment matches production
- **Easy Setup**: One command to start everything

## 🔄 Migration from Old Setup

If you were using the old `docker-compose.yml`:

1. **Stop old containers**:
   ```bash
   docker-compose down
   ```

2. **Start new development environment**:
   ```bash
   ./dev.sh  # or dev.bat
   ```

3. **Your existing data will be preserved** (PostgreSQL volume)

The new setup is backward compatible and will work with your existing database and code!
