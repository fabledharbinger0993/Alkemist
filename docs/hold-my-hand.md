# 🤝 Hold My Hand — System Prep Guide

**For people who haven't set up development tools before.**

Don't worry. This page walks you through installing everything you need. It takes ~30 minutes total.

---

## What You Need to Install

You'll install 3 things:
1. **Git** — For downloading Alkemist
2. **Docker** — For running Alkemist (easiest way)
3. (Optional) **Node.js + Python** — If you want to develop Alkemist itself

---

## Step 1: Download Git

Git is how you'll download Alkemist.

### Windows

1. Go to [git-scm.com](https://git-scm.com)
2. Click the **Windows** link (big button)
3. Download will start automatically
4. Open the file and click through (all defaults are fine)
5. Click **Finish**

**Verify it worked:**
```bash
git --version
```
You should see: `git version 2.x.x`

### Mac

1. Open **Terminal** (press Cmd + Space, type "terminal", press Enter)
2. Copy & paste this:
   ```bash
   xcode-select --install
   ```
3. Click **Install** when asked
4. Wait ~10 minutes for installation

**Verify it worked:**
```bash
git --version
```
You should see: `git version 2.x.x`

### Linux (Ubuntu/Debian)

1. Open **Terminal**
2. Copy & paste this:
   ```bash
   sudo apt update
   sudo apt install git
   ```
3. Press Enter, type your password if asked

**Verify it worked:**
```bash
git --version
```
You should see: `git version 2.x.x`

---

## Step 2: Download Docker

Docker is how Alkemist runs (much easier than manual setup).

### Windows & Mac

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Click **Download** (big blue button)
3. Choose your OS (Windows or Mac)
4. Open the downloaded file
5. Click through the installer (all defaults are fine)
6. **Restart your computer** when prompted
7. Open Docker Desktop from your Applications/Start Menu

**Verify it worked:**
- Docker Desktop should be running (you'll see the whale icon 🐋)
- Open Terminal/PowerShell, then copy & paste:
  ```bash
  docker --version
  ```
  You should see: `Docker version 24.x.x`

### Linux

1. Open **Terminal**
2. Copy & paste this:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```
3. Type your password if asked
4. **Log out and log back in** (or restart your computer)

**Verify it worked:**
```bash
docker --version
```
You should see: `Docker version 24.x.x`

---

## Step 3 (Optional): Download Node.js + Python

**Only do this if you want to develop Alkemist yourself.**  
(If you just want to USE Alkemist, skip this.)

### Node.js

1. Go to [nodejs.org](https://nodejs.org)
2. Click **LTS** (green button, left side)
3. Download and open the file
4. Click through installer (all defaults fine)
5. **Restart your computer**

**Verify it worked:**
```bash
node --version
npm --version
```
You should see version numbers.

### Python

#### Windows
1. Go to [python.org](https://www.python.org)
2. Click **Download** (yellow button)
3. Open the file
4. **⚠️ IMPORTANT:** Check the box "Add Python to PATH" (bottom of window)
5. Click **Install Now**
6. **Restart your computer**

#### Mac
1. Go to [python.org](https://www.python.org)
2. Click **Download**
3. Open the file, click through installer
4. **Restart your computer**

#### Linux
```bash
sudo apt update
sudo apt install python3.12 python3-pip
```

**Verify it worked:**
```bash
python3 --version
```
You should see: `Python 3.12.x`

---

## You're Ready! 🎉

Now go to [Getting Started](getting-started.md) and follow the steps to run Alkemist.

---

## Troubleshooting

### "command not found: git"
- You didn't restart your computer after installing
- **Fix:** Restart your computer, try again

### "Docker: command not found"
- Docker Desktop isn't running
- **Fix:** Open Docker Desktop, wait for it to start, try again

### "docker: Cannot connect to Docker daemon"
- Docker isn't running
- **Fix:** Open Docker Desktop and wait 30 seconds

### On Windows: "PowerShell: command not recognized"
- Use Command Prompt instead of PowerShell
- **Fix:** Press `Win + R`, type `cmd`, press Enter

---

**Stuck?** Ask on [GitHub Discussions](https://github.com/yourname/Alkemist/discussions) — we'll help! 🙌
