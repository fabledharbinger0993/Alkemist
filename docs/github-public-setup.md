# Making Alkemist a Public GitHub Repository

> ⚙️ **For Project Maintainers Only** — This guide is for publishing the official Alkemist repo on GitHub.

This guide walks you through publishing Alkemist on GitHub as an open-source project.

## Prerequisites

1. **GitHub account** (free) — [signup here](https://github.com/signup)
2. **git** installed locally
3. **SSH key or Personal Access Token** configured for GitHub

## Setup Options

### Option A: Existing GitHub Repo (Easiest)

If you already have a GitHub repo (private and want to make public):

1. Go to **Settings → Visibility → Change visibility to Public**
2. Skip to "Step 3: Add Open Source Files" below

### Option B: New GitHub Repo

1. Go to [github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name:** `Alkemist`
   - **Description:** "The AI IDE for people who can't send their code to the cloud"
   - **Visibility:** `Public` ✅
   - **Add a README:** Uncheck (we have one)
   - **Add .gitignore:** Select `Python` (we'll customize it)
   - **Choose a license:** Select `MIT` ✅
   - Click **Create repository**

3. You'll see instructions like:
   ```bash
   git remote add origin https://github.com/yourname/Alkemist.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 1: Initialize & Push (if new repo)

```bash
cd /workspaces/Alkemist

# Verify you're on main branch
git branch -M main

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourname/Alkemist.git

# Push all commits and history
git push -u origin main
```

If you already have a remote:
```bash
git remote set-url origin https://github.com/yourname/Alkemist.git
git push -u origin main
```

---

## Step 2: Add/Update .gitignore

Create or update [`.gitignore`](../.gitignore) to exclude:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
.pytest_cache/
.coverage
htmlcov/

# Node.js
node_modules/
npm-debug.log
.next/
out/
.vercel/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Data
data/projects/
.claude/
```

---

## Step 3: Add Key Open Source Files

### Already included:
- ✅ `LICENSE` (MIT)
- ✅ `README.md` (enhanced with privacy positioning)
- ✅ `CONTRIBUTING.md` (contributor guide)
- ✅ `docs/positioning.md` (market strategy)

### Add if missing:

**`CODE_OF_CONDUCT.md` (optional but recommended)**
```markdown
# Code of Conduct

We're committed to providing a welcoming and collaborative environment.

## Standards
- Be respectful and inclusive
- Assume good intent
- Welcome diverse perspectives
- Report concerns to maintainers

See [Contributor Covenant](https://www.contributor-covenant.org) for details.
```

**`SECURITY.md` (for reporting vulnerabilities)**
```markdown
# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability, please email security@alkemist.dev 
instead of using the issue tracker.

**Do not disclose the vulnerability publicly until a fix is available.**

We will:
1. Confirm receipt within 48 hours
2. Provide timeline for fix
3. Release patch and credit you (if desired)
```

---

## Step 4: Configure GitHub Repository Settings

Go to your repo → **Settings** and configure:

### General
- ✅ Make repo **Public**
- ✅ Check "Discussions" (let people ask questions)
- ✅ Check "Sponsorships" (let people fund development)

### Access
- **Admin:** You only (or trusted maintainers)
- **Write:** None initially (you'll approve PRs)
- **Read:** Everyone (public repo)

### Collaborators & Teams (Optional)
- Add trusted maintainers as "Maintain" role
- They can merge PRs but not change settings

### Pages (Optional, for documentation)
- Source: `main` (or `docs/` folder)
- This auto-publishes a website from markdown

### Actions (for CI/CD)
- Workflows are ready (tests, Docker publish)
- Enable if you want auto-builds

---

## Step 5: Set Up GitHub Sponsorships (Optional but Important!)

1. Go to **Settings → Sponsor this project** (or click "Sponsor" button in repo)
2. Choose a sponsorship platform:
   - **GitHub Sponsors** (free, recommended for open source)
   - Ko-fi, Open Collective, etc.
3. Add sponsorship tiers:
   - $5/month — Early supporter
   - $25/month — Feature requests
   - $100/month — Priority support
4. Write a message explaining funding helps:
   - Keep project free
   - Hire contributors
   - Improve documentation

**Example:**
```markdown
# Support Alkemist

Help us build the #1 privacy-first AI IDE!

Your sponsorship helps us:
- 🚀 Ship new features faster
- 📚 Write better documentation
- 🛠️ Support more languages
- 🔒 Improve security & compliance

Every dollar counts. Thank you!
```

---

## Step 6: Add Topics (GitHub Searchability)

Go to repo **About** (top right, click gear icon):

Add topics:
- `ai` `ide` `local-llm` `privacy` `open-source`
- `llm` `python` `typescript` `langchain` `langraph`

This helps people discover Alkemist.

---

## Step 7: Enable Discussions (Community)

1. Go to **Settings → Features**
2. Check ✅ **Discussions**
3. Customize categories:
   - **Announcements** — News & releases
   - **General** — Chat & questions
   - **Feature requests** — Ideas
   - **Q&A** — Help & troubleshooting

Now people can ask questions without opening issues.

---

## Step 8: Create GitHub Issues for First Contributors

Create `good-first-issue` labels and add tasks:

Go to **Issues** and create:
- "Add Python 3.13 support to docker_manager.py"
- "Write tests for OpenClaw Telegram commands"
- "Document Logic Ladder architecture"
- "Enhance error messages in API responses"

Label them with:
- `good first issue` (GitHub recognizes this!)
- `help wanted`
- `documentation`

This attracts beginner contributors.

---

## Step 9: Add GitHub Badges to README

Update the top of your [README.md](../README.md) with:

```markdown
# Alkemist

[![GitHub License](https://img.shields.io/github/license/yourname/Alkemist)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/yourname/Alkemist?style=social)](https://github.com/yourname/Alkemist/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourname/Alkemist?style=social)](https://github.com/yourname/Alkemist/network/members)

The AI IDE for people who can't send their code to the cloud. 🔐

[Docs](docs/positioning.md) | [Contributing](CONTRIBUTING.md) | [Docker Hub](https://hub.docker.com/r/yourname/alkemist-server)
```

---

## Step 10: Announce on Social Media (Optional)

```
🚀 Just open-sourced Alkemist, the AI IDE for enterprises.

✅ 100% local execution (no cloud)
✅ Privacy-first architecture
✅ Intelligent 4-stage reasoning
✅ Built for regulated industries

GitHub: github.com/yourname/Alkemist
Docker: hub.docker.com/r/yourname/alkemist-*

Help us build the future! 🔓
```

Post on:
- Twitter/X
- LinkedIn
- Dev.to
- Hacker News (Show HN)
- r/opensource

---

## Deployment Flow (Public → Users)

```
GitHub (public repo)
    ↓ (Docker Hub publishes)
Docker Hub (public images)
    ↓ (anyone can pull)
User: docker compose up -d
    ↓
Alkemist running locally ✨
```

---

## Checklist Before Going Public

- [ ] Repo is public on GitHub
- [ ] README has privacy positioning
- [ ] CONTRIBUTING.md exists
- [ ] LICENSE is MIT
- [ ] .gitignore is comprehensive
- [ ] Sensitive files removed (.env, keys, data/)
- [ ] Tests pass locally (`poetry run pytest` + `npm test`)
- [ ] Dockerfiles build successfully
- [ ] Docker Hub images published
- [ ] GitHub Sponsorships configured
- [ ] Topics added for discoverability
- [ ] First "good-first-issue" labels created
- [ ] Discussions enabled

---

## Next Steps

1. ✅ Push to public GitHub
2. ✅ Publish Docker images
3. ⏭️ Write a launch blog post
4. ⏭️ Share on social media
5. ⏭️ Reach out to 5 potential customers

**Welcome to the (public) open-source community! 🎉**
