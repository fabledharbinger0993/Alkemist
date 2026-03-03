# Quick Reference — Copy-Paste Commands

> 👤 **For All Users & Developers** — All commands you need in one place.

All commands you need, in one place. No explanations, just copy & paste.

---

## First Time Setup

### Windows (Command Prompt)

```powershell
# Download
cd Desktop
git clone https://github.com/yourname/Alkemist.git
cd Alkemist

# Start
docker compose up -d

# Check if running
docker compose ps

# Open browser: http://localhost:3000
```

### Mac/Linux (Terminal)

```bash
# Download
cd ~
git clone https://github.com/yourname/Alkemist.git
cd Alkemist

# Start
docker compose up -d

# Check if running
docker compose ps

# Open browser: http://localhost:3000
```

---

## Backend Development

```bash
# Setup
cd alkemist-server
pip install poetry
poetry install

# Run tests
poetry run pytest -v

# Start dev server
poetry run uvicorn main:app --reload --port 8000

# Run specific test
poetry run pytest tests/test_routers.py -v

# Check coverage
poetry run pytest --cov=. --cov-report=html
```

---

## Frontend Development

```bash
# Setup
cd alkemist-client
npm install

# Check TypeScript
npm run type-check

# Check code style
npm run lint

# Run tests
npm test

# Start dev server
npm run dev

# Build for production
npm run build
```

---

## Docker Commands

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down

# View status
docker compose ps

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend
docker compose logs -f frontend

# Restart
docker compose restart

# Delete everything & start fresh
docker compose down -v
docker compose up -d

# Build locally
docker build -t alkemist-server:latest ./alkemist-server
docker build -t alkemist-client:latest ./alkemist-client

# Test build
docker build -t alkemist-server:test ./alkemist-server --no-cache
```

---

## Git Commands

```bash
# Clone
git clone https://github.com/yourname/Alkemist.git

# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Feature: your description here"

# Push to GitHub
git push origin main

# Create new branch
git checkout -b feature/your-feature

# Switch branches
git checkout main

# View history
git log --oneline
```

---

## Troubleshooting

### Port Already in Use

#### Windows
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID 1234 /F

# Or check other ports
netstat -ano | findstr :8000
netstat -ano | findstr :11434
```

#### Mac/Linux
```bash
# Find process using port 3000
lsof -i :3000

# Kill process (replace PID)
kill -9 1234

# Or check other ports
lsof -i :8000
lsof -i :11434
```

### Docker Issues

```bash
# Docker not running? Start it manually
docker run hello-world

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a

# Check Docker info
docker info
```

### Node.js Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall node_modules
rm -rf node_modules package-lock.json
npm install

# Update npm
npm install -g npm@latest
```

### Python Issues

```bash
# Clear poetry cache
poetry cache clear . --all

# Reinstall environment
poetry env remove python3.12
poetry install

# Check Python version
python3 --version

# Check poetry version
poetry --version
```

---

## Validation (Before Submitting Code)

```bash
# Backend validation
cd alkemist-server
poetry run pytest -v
poetry run pytest --cov=.

# Frontend validation
cd alkemist-client
npm run type-check
npm run lint
npm test

# Both
npm run build
```

---

## Useful URLs

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **Ollama:** http://localhost:11434
- **ChromaDB:** http://localhost:8001
- **GitHub:** https://github.com/yourname/Alkemist
- **Docker Hub:** https://hub.docker.com/r/yourname/alkemist-server

---

## Environment Variables

### Backend (.env in alkemist-server/)
```
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_HOST=localhost
CHROMA_PORT=8001
```

### Frontend (.env.local in alkemist-client/)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Common Workflows

### "I made changes, now what?"

```bash
# Backend
cd alkemist-server
poetry run pytest -v               # Make sure tests pass
git add .
git commit -m "Fix: describe change"
git push origin main

# Frontend
cd alkemist-client
npm run type-check && npm run lint # Check for errors
npm test                           # Run tests
git add .
git commit -m "Feature: describe change"
git push origin main
```

### "I want to add a new language"

Edit: `alkemist-server/execution/docker_manager.py`

```python
LANGUAGE_IMAGES = {
    "kotlin": "eclipse-temurin:21-jdk",  # Add this line
    # ... rest
}

LANGUAGE_COMMANDS = {
    "kotlin": ["sh", "-c", "kotlinc main.kt && java -cp . MainKt"],  # Add this line
    # ... rest
}
```

Then test:
```bash
cd alkemist-server
poetry run pytest tests/test_docker_manager.py -v
```

### "I want to update the README"

Edit: `README.md` or any file in `docs/`

```bash
git add README.md
git commit -m "Docs: clarify setup instructions"
git push origin main
```

No tests needed for docs! 📝

---

**Need more help?** See [Getting Started](getting-started.md) or ask on [GitHub Discussions](https://github.com/yourname/Alkemist/discussions).
