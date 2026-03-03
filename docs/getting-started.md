# Getting Started with Alkemist

Complete step-by-step guide to running Alkemist on your computer.

**Time required:** 5-10 minutes (assuming you have Git and Docker installed)

---

## Before You Start

**Do you have these installed?**

```bash
git --version      # Should show: git version 2.x
docker --version   # Should show: Docker version 24.x
```

**Don't see version numbers?** Go to [Hold My Hand](hold-my-hand.md) first to install.

Otherwise, continue below. ↓

---

## Setup: Docker (Easiest — 3 Steps)

This is the best way. Takes ~5 minutes.

### Step 1: Download Alkemist

Open your Terminal/PowerShell and copy-paste this:

#### Windows (Command Prompt)
```powershell
cd Desktop
git clone https://github.com/yourname/Alkemist.git
cd Alkemist
```

#### Mac/Linux (Terminal)
```bash
cd ~
git clone https://github.com/yourname/Alkemist.git
cd Alkemist
```

**What you should see:**
```
Cloning into 'Alkemist'...
remote: Enumerating objects...
```

Then the prompt returns. ✅

---

### Step 2: Start Alkemist

Copy-paste this command:

```bash
docker compose up -d
```

**What you'll see:**
```
[+] Running 4/4
 ✔ Container alkemist-chromadb   Created    1.2s
 ✔ Container alkemist-backend    Created    2.1s
 ✔ Container alkemist-frontend   Created    1.8s
 ✔ Network alkemist_alkemist     Created    0.5s
```

(Taking a few moments is normal.)

---

### Step 3: Open in Browser

**Check if everything is running:**
```bash
docker compose ps
```

**You should see:**
```
NAME                    STATUS
alkemist-backend        Up 2 minutes
alkemist-frontend       Up 2 minutes
alkemist-chromadb       Up 2 minutes
```

**Open your browser and go to:** 
```
http://localhost:3000
```

**You should see:** Alkemist web IDE with a code editor on the left! 🎉

---

## That's It!

You're running Alkemist. Start using it:

1. **Create a project** — Click "New Project"
2. **Write code** — Use the editor
3. **Get AI help** — Click the chat icon
4. **Run code** — Click "Run"

---

## Useful Commands

### Check Status
```bash
docker compose ps
```

### View Logs (for troubleshooting)
```bash
docker compose logs -f
```

### Stop Everything
```bash
docker compose down
```

### Restart
```bash
docker compose down
docker compose up -d
```

### Delete Everything & Start Fresh
```bash
docker compose down -v
docker compose up -d
```

---

## Setup: Manual (Advanced)

**Only do this if Docker doesn't work for you.**

### Prerequisites

Make sure you have:
- Git
- Docker (for sandboxing code) — optional but recommended
- Node.js 18+ ([nodejs.org](https://nodejs.org))
- Python 3.12+ ([python.org](https://www.python.org))

### Step 1: Download Alkemist

```bash
cd ~
git clone https://github.com/yourname/Alkemist.git
cd Alkemist
```

### Step 2: Start Backend

**Open Terminal/PowerShell #1:**

#### Windows
```powershell
cd Alkemist\alkemist-server
pip install poetry
poetry install
poetry run uvicorn main:app --reload --port 8000
```

#### Mac/Linux
```bash
cd Alkemist/alkemist-server
pip install poetry
poetry install
poetry run uvicorn main:app --reload --port 8000
```

**You should see:**
```
Uvicorn running on http://127.0.0.1:8000
```

✅ Leave this running, open a new terminal.

### Step 3: Start Frontend

**Open Terminal/PowerShell #2:**

#### Windows
```powershell
cd Alkemist\alkemist-client
npm install
npm run dev
```

#### Mac/Linux
```bash
cd Alkemist/alkemist-client
npm install
npm run dev
```

**You should see:**
```
  ▲ Next.js 15.x
  - Local: http://localhost:3000
```

### Step 4: Open Browser

Go to: **http://localhost:3000**

You should see Alkemist! ✅

---

## Troubleshooting

### "Port 3000 already in use"

**On Windows:**
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**On Mac/Linux:**
```bash
lsof -i :3000
kill -9 <PID>
```

Then try again: `npm run dev`

### "Port 8000 already in use"

**On Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**On Mac/Linux:**
```bash
lsof -i :8000
kill -9 <PID>
```

Then try again: `poetry run uvicorn main:app --reload --port 8000`

### "Docker daemon not running"

**Fix:**
1. Open Docker Desktop
2. Wait 30 seconds for it to start
3. Try again: `docker compose ps`

### "Module not found: poetry"

Be in the `alkemist-server` directory first:
```bash
cd alkemist-server
pip install poetry
poetry install
```

### "npm: command not found"

Node.js didn't install correctly. Go to [Hold My Hand](hold-my-hand.md) and reinstall Node.js.

### "Cannot find module 'next'"

You skipped `npm install`. Run:
```bash
cd alkemist-client
npm install
```

### "Test failed" or "Type errors"

Make sure you're in the right directory:
- Backend: `cd alkemist-server`
- Frontend: `cd alkemist-client`

Then try the validation commands:
```bash
# Backend
poetry run pytest -v

# Frontend
npm run type-check
```

---

## Next Steps

- 📖 Read [How Alkemist Works](how-it-works.md)
- 🤝 Check [Contributing](../CONTRIBUTING.md) to help develop
- 🏗️ See [Architecture](architecture.md) for technical details
- 🐛 Found a bug? [Report it](https://github.com/yourname/Alkemist/issues)

---

**Welcome to Alkemist!** 🚀

If you get stuck, ask on [GitHub Discussions](https://github.com/yourname/Alkemist/discussions) — we're here to help!
