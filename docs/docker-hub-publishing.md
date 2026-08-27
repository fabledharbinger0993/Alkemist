# Publishing Alkemist to Docker Hub

> ⚙️ **For Project Maintainers Only** — This guide is for publishing official Alkemist images.

This guide walks you through publishing Alkemist's backend and frontend to Docker Hub for easy deployment.

## Prerequisites

1. **Docker Desktop** installed and running
2. **Docker Hub account** (free) — [signup here](https://hub.docker.com/signup)
3. **Logged in to Docker CLI:**
   ```bash
   docker login
   ```

## Step 1: Set Up Your Docker Hub Namespace

1. Go to [Docker Hub](https://hub.docker.com)
2. Log in and note your **username** (e.g., `myusername`)
3. Create a public repository:
   - Click "Create Repository"
   - Name: `alkemist-server`
   - Description: "Alkemist Backend — Local AI-native IDE"
   - Visibility: **Public**
   - Click "Create"
4. Repeat for `alkemist-client`

You'll now have:
- `docker.io/myusername/alkemist-server`
- `docker.io/myusername/alkemist-client`

## Step 2: Build Docker Images Locally

```bash
cd /workspaces/Alkemist

# Build backend image
docker build -t alkemist-server:latest ./alkemist-server

# Build frontend image
docker build -t alkemist-client:latest ./alkemist-client

# Verify builds
docker images | grep alkemist
```

## Step 3: Tag Images for Docker Hub

Replace `myusername` with your actual Docker Hub username:

```bash
# Tag backend
docker tag alkemist-server:latest myusername/alkemist-server:latest
docker tag alkemist-server:latest myusername/alkemist-server:0.1.0

# Tag frontend
docker tag alkemist-client:latest myusername/alkemist-client:latest
docker tag alkemist-client:latest myusername/alkemist-client:0.1.0
```

## Step 4: Push to Docker Hub

```bash
# Push backend
docker push myusername/alkemist-server:latest
docker push myusername/alkemist-server:0.1.0

# Push frontend
docker push myusername/alkemist-client:latest
docker push myusername/alkemist-client:0.1.0
```

Monitor the upload (usually 2-5 minutes per image).

## Step 5: Verify on Docker Hub

1. Go to [Docker Hub](https://hub.docker.com)
2. Click on your username (top right)
3. You should see:
   - `alkemist-server` with tags `latest` and `0.1.0`
   - `alkemist-client` with tags `latest` and `0.1.0`

---

## Step 6: Update docker-compose.yml for Public Use

Replace the `build` sections with public image references:

```yaml
# alkemist-server service
backend:
  image: myusername/alkemist-server:latest   # <-- Change this
  # ... rest of config
```

Or keep both — Docker Compose will use remote images if local build doesn't exist.

---

## Usage (After Publishing)

Anyone can now deploy Alkemist with just:

```bash
git clone https://github.com/fabledharbinger0993/Alkemist.git
cd Alkemist

# Deploy with docker-compose (uses public images)
docker compose up -d

# Or specify your Docker Hub namespace
docker compose up -d --build  # Uses local Dockerfiles

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Ollama: http://localhost:11434
# ChromaDB: http://localhost:8001
```

Verify:
```bash
docker compose ps
```

---

## Automation: GitHub Actions (Optional)

Create [`.github/workflows/docker-publish.yml`](../.github/workflows/docker-publish.yml) to auto-push on release:

```yaml
name: Publish to Docker Hub

on:
  push:
    tags:
      - v*

jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASS }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./alkemist-server
          push: true
          tags: |
            ${{ secrets.DOCKER_USER }}/alkemist-server:latest
            ${{ secrets.DOCKER_USER }}/alkemist-server:${{ github.ref_name }}
      
      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./alkemist-client
          push: true
          tags: |
            ${{ secrets.DOCKER_USER }}/alkemist-client:latest
            ${{ secrets.DOCKER_USER }}/alkemist-client:${{ github.ref_name }}
```

Then add secrets in GitHub:
- `DOCKER_USER` = your Docker Hub username
- `DOCKER_PASS` = your Docker Hub password/token

Push a tag and GitHub automatically publishes to Docker Hub! 🚀

---

## Troubleshooting

### Image won't build
```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker build -t alkemist-server:latest ./alkemist-server
```

### Authentication failed
```bash
# Log out and re-login
docker logout
docker login

# Verify credentials
cat ~/.docker/config.json
```

### Push is slow
- Check internet connection
- Push during off-peak hours
- Use `.dockerignore` to reduce image size (already included)

---

## Next Steps

- ✅ Dockerfiles created
- ✅ Images built and pushed
- ⏭️ Update main [README.md](../README.md) with Docker Hub instructions
- ⏭️ Add to GitHub marketplace (optional)
- ⏭️ Set up CI/CD for auto-publish (GitHub Actions)
