# Docker Instructions - ESG Geospatial Data Inspector

## Prerequisites

- Docker installed and running
- Docker Compose (usually included with Docker Desktop)
- `.env` file with your API keys configured

## Step-by-Step Instructions

### 1. Prepare Environment File

Ensure you have a `.env` file in the project root with all required API keys:

```bash
# .env file
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
STREAMLIT_SERVER_PORT=8080
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

**Note**: The `.env` file is automatically loaded by Docker Compose.

### 2. Build and Run with Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

**Access the application**: Open your browser to `http://localhost:8080`

### 3. Alternative: Docker Only (Without Docker Compose)

#### Build the Docker image:
```bash
docker build -t stac-esg-app .
```

#### Run the container:
```bash
docker run -p 8080:8080 --env-file .env stac-esg-app
```

Or with interactive mode:
```bash
docker run -it -p 8080:8080 --env-file .env stac-esg-app
```

### 4. Common Docker Commands

```bash
# View running containers
docker ps

# Stop a running container
docker stop stac-esg-app

# Remove the container
docker rm stac-esg-app

# View container logs
docker logs stac-esg-app

# Access container shell (for debugging)
docker exec -it stac-esg-app /bin/bash
```

### 5. Troubleshooting

**Port already in use?**
```bash
# Change port in docker-compose.yml or use a different port
docker run -p 8081:8080 --env-file .env stac-esg-app
```

**Environment variables not working?**
```bash
# Verify .env file exists and has correct values
cat .env

# Check if variables are loaded in container
docker exec stac-esg-app env | grep API
```

**Container won't start?**
```bash
# View detailed logs
docker-compose logs -f

# Rebuild from scratch (no cache)
docker-compose build --no-cache
docker-compose up
```

**Need to rebuild after code changes?**
```bash
# Stop container
docker-compose down

# Rebuild and restart
docker-compose up --build
```

## Quick Start Summary

```bash
# 1. Ensure .env file exists with API keys
# 2. Run this command:
docker-compose up --build

# 3. Open browser to http://localhost:8080
```

That's it! 🚀

