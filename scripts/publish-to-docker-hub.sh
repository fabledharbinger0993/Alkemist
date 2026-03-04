#!/bin/bash
# Alkemist Docker Hub Publish Script
# Usage: ./scripts/publish-to-docker-hub.sh <docker-username> <version>
# Example: ./scripts/publish-to-docker-hub.sh myusername 0.1.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Docker Hub username required${NC}"
    echo "Usage: $0 <docker-username> [version]"
    echo "Example: $0 myusername 0.1.0"
    exit 1
fi

DOCKER_USER=$1
VERSION=${2:-latest}

echo -e "${YELLOW}📦 Alkemist Docker Hub Publisher${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Username: ${GREEN}$DOCKER_USER${NC}"
echo -e "Version:  ${GREEN}$VERSION${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
    exit 1
fi

# Verify Docker login
if ! docker config view > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not logged into Docker Hub. Running 'docker login'...${NC}"
    docker login
fi

# Build backend
echo -e "\n${YELLOW}🔨 Building backend image...${NC}"
docker build -t alkemist-server:$VERSION ./alkemist-server
docker tag alkemist-server:$VERSION $DOCKER_USER/alkemist-server:$VERSION

if [ "$VERSION" != "latest" ]; then
    docker tag alkemist-server:$VERSION $DOCKER_USER/alkemist-server:latest
fi

# Build frontend
echo -e "\n${YELLOW}🔨 Building frontend image...${NC}"
docker build -t alkemist-client:$VERSION ./alkemist-client
docker tag alkemist-client:$VERSION $DOCKER_USER/alkemist-client:$VERSION

if [ "$VERSION" != "latest" ]; then
    docker tag alkemist-client:$VERSION $DOCKER_USER/alkemist-client:latest
fi

# Push backend
echo -e "\n${YELLOW}📤 Pushing backend to Docker Hub...${NC}"
docker push $DOCKER_USER/alkemist-server:$VERSION
if [ "$VERSION" != "latest" ]; then
    docker push $DOCKER_USER/alkemist-server:latest
fi

# Push frontend
echo -e "\n${YELLOW}📤 Pushing frontend to Docker Hub...${NC}"
docker push $DOCKER_USER/alkemist-client:$VERSION
if [ "$VERSION" != "latest" ]; then
    docker push $DOCKER_USER/alkemist-client:latest
fi

# Clean up
echo -e "\n${YELLOW}🧹 Cleaning up local images...${NC}"
docker rmi alkemist-server:$VERSION alkemist-client:$VERSION
docker rmi $DOCKER_USER/alkemist-server:$VERSION $DOCKER_USER/alkemist-client:$VERSION 2>/dev/null || true

echo -e "\n${GREEN}✅ Successfully published to Docker Hub!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Backend:  ${GREEN}https://hub.docker.com/r/$DOCKER_USER/alkemist-server${NC}"
echo -e "Frontend: ${GREEN}https://hub.docker.com/r/$DOCKER_USER/alkemist-client${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next: Update docker-compose.yml to use your images:"
echo "  image: $DOCKER_USER/alkemist-server:$VERSION"
echo "  image: $DOCKER_USER/alkemist-client:$VERSION"
