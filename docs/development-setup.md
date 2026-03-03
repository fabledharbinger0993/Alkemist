# Development Setup Guide

**For developers who want to build & improve Alkemist.**

If you just want to USE Alkemist, see [Getting Started](getting-started.md) instead.

---

## Prerequisites

Make sure you have these installed:

- **Git** ([git-scm.com](https://git-scm.com))
- **Docker** ([docker.com](https://docker.com))
- **Node.js 18+** ([nodejs.org](https://nodejs.org) — LTS version)
- **Python 3.12+** ([python.org](https://python.org))

**Verify everything:**

```bash
git --version          # Should show: git version 2.x
docker --version       # Should show: Docker version 24.x
node --version         # Should show: v18.x or higher
python3 --version      # Should show: Python 3.12.x
```

Don't see versions? Go to [Hold My Hand](hold-my-hand.md) to install.

---

## Part 1: Backend Development (Python)

### Step 1: Clone the repo

```bash
git clone https://github.com/yourname/Alkemist.git
cd Alkemist
```

### Step 2: Set up Python environment

```bash
cd alkemist-server
pip install poetry
poetry install
```

**You should see:**

```
Successfully installed 47 packages
```

### Step 3: Run tests (make sure everything works)

```bash
poetry run pytest -v
```

**You should see:**

```
======================== 73 passed in 2.87s ========================
```

All tests passing = everything is working! ✅

### Step 4: Start the backend server

```bash
poetry run uvicorn main:app --reload --port 8000
```

**You should see:**

```
Uvicorn running on http://127.0.0.1:8000
```

**Leave this running.** Open a new terminal for the frontend.

---

## Part 2: Frontend Development (React)

### Step 1: Open a new terminal

**Keep the backend running from above. In a new terminal:**

```bash
cd Alkemist/alkemist-client
```

### Step 2: Install dependencies

```bash
npm install
```

**You should see:**

```
added 668 packages
```

### Step 3: Check for TypeScript errors

```bash
npm run type-check
```

**Should say:**

```
✓ Compiled successfully
```

### Step 4: Check code style

```bash
npm run lint
```

**Should say:**

```
✔ ESLint check passed
```

### Step 5: Start frontend dev server

```bash
npm run dev
```

**You should see:**

```
  ▲ Next.js 15.0.0
  - Local: http://localhost:3000
```

### Step 6: Open <http://localhost:3000>

You should see Alkemist with both frontend AND backend working! 🎉

---

## Part 3: Database & Services (Optional)

If you want vector search or Telegram features:

```bash
# In a new terminal:
docker compose up -d chromadb

# For Telegram bot, see OPENCLAW_OLLAMA_SETUP.md
```

---

## Making Changes

### Backend

1. Edit a file in `alkemist-server/`
2. The server auto-reloads (you'll see changes in terminal)
3. Run tests: `poetry run pytest -v`

### Frontend

1. Edit a file in `alkemist-client/`
2. Browser auto-refreshes (you'll see changes immediately)
3. Check TypeScript: `npm run type-check`

---

## Before You Submit Code

Run this validation checklist:

### Backend

```bash
cd alkemist-server

# Run all tests
poetry run pytest -v

# Check code quality (if linting is set up)
poetry run pytest --cov=.
```

All tests must pass! ✅

### Frontend

```bash
cd alkemist-client

# Type check
npm run type-check

# Lint
npm run lint

# Run tests
npm test
```

All checks must pass! ✅

### Both

```bash
# Make sure everything still runs
# Backend should still be running
# Frontend should still load at http://localhost:3000
```

---

## Testing Locally

### Test a specific feature

**Backend:**

```bash
cd alkemist-server
poetry run pytest tests/test_routers.py -v
```

**Frontend:**

```bash
cd alkemist-client
npm test -- --testPathPattern="api.test"
```

### Clear cache and restart

```bash
# Remove node modules
cd alkemist-client
rm -rf node_modules package-lock.json
npm install

# Reset Python env
cd alkemist-server
poetry env remove python3.12
poetry install
```

---

## Debugging

### Backend

Add Python print statements or use the debugger:

```python
import pdb; pdb.set_trace()  # Pauses execution here
```

Or use VS Code's Python debugger (see `.vscode/launch.json`).

### Frontend

Use browser DevTools:

- Press `F12` in your browser
- Go to **Console** tab to see errors
- Use `console.log()` in code

### Check logs

```bash
# Backend logs
docker compose logs -f backend

# Frontend logs
# Check browser console (F12)

# All services
docker compose logs -f
```

---

## Project Structure

```
Alkemist/
├── alkemist-server/        (Python FastAPI backend)
│   ├── main.py             (App entry point)
│   ├── models/             (Database, schemas)
│   ├── routers/            (API endpoints)
│   ├── ai/                 (Logic Ladder reasoning)
│   ├── execution/          (Docker execution)
│   ├── tests/              (Test suite)
│   └── pyproject.toml      (Dependencies)
│
├── alkemist-client/        (React/Next.js frontend)
│   ├── app/                (Next.js pages)
│   ├── components/         (React components)
│   ├── lib/                (Utilities)
│   ├── __tests__/          (Tests)
│   └── package.json        (Dependencies)
│
├── docs/                   (Documentation)
└── docker-compose.yml      (Services config)
```

---

## Code Standards

### Python

- Type annotations: `def foo(x: str) -> int:`
- Async for FastAPI: `async def get_data():`
- Docstrings for functions: `"""Do something."""`

### TypeScript/React

- Functional components only
- Type props: `interface Props { name: string }`
- Tailwind CSS for styling

### Commits

```bash
git add .
git commit -m "Feature: Add support for Python 3.13"
git push origin main
```

Clear, present-tense messages. ✅

---

## Continuous Development

Keep these running:

**Terminal 1 (Backend):**

```bash
cd alkemist-server
poetry run uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**

```bash
cd alkemist-client
npm run dev
```

**Terminal 3 (Tests):**

```bash
cd alkemist-server
poetry run pytest --watch  # Reruns on file changes
```

Edit code → See changes live! 🔄

---

## Need Help?

- 📖 Check [how it works](how-it-works.md)
- 📖 Check [architecture](architecture.md)
- 💬 Ask on [GitHub Discussions](https://github.com/yourname/Alkemist/discussions)
- 🐛 Report bugs on [GitHub Issues](https://github.com/yourname/Alkemist/issues)

---

**Happy developing!** 🚀
