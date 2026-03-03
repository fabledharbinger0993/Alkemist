# 🚀 Alkemist Public Launch Checklist

> ⚙️ **For Project Maintainers Only** — This guide is for the core team releasing Alkemist publicly.

Complete this checklist to launch Alkemist as a public, open-source project.

## Phase 1: Code & Documentation ✅ (Done)

- [x] Created `CONTRIBUTING.md` — Clear contributor guidelines
- [x] Created `docs/positioning.md` — "Why Alkemist?" positioning document
- [x] Enhanced `README.md` — Privacy-focused, Docker-first approach
- [x] Created `docs/docker-hub-publishing.md` — Step-by-step Docker Hub guide
- [x] Created `docs/github-public-setup.md` — GitHub public repo setup
- [x] Created `Dockerfiles` — Backend (Python) and Frontend (Next.js)
- [x] Updated `docker-compose.yml` — Full stack (backend, frontend, ChromaDB, Ollama)
- [x] Created `.dockerignore` files — Lean, optimized images
- [x] Created `scripts/publish-to-docker-hub.sh|bat` — One-click publishing

---

## Phase 2: GitHub Public Repo (10 min)

### Step 1: Make Repo Public
- [ ] Go to your GitHub repo **Settings → Visibility**
- [ ] Change to **Public**
- [ ] Confirm

### Step 2: Verify Essential Files
- [ ] ✅ `LICENSE` file exists (MIT)
- [ ] ✅ `README.md` enhanced with privacy positioning
- [ ] ✅ `CONTRIBUTING.md` created
- [ ] ✅ `.gitignore` configured for Python/Node.js

### Step 3: Add Topics
- [ ] Go to repo **About** (click gear, top right)
- [ ] Add topics: `ai`, `ide`, `privacy`, `open-source`, `python`, `typescript`
- [ ] Save

### Step 4: Set Up Sponsorships (Optional)
- [ ] Go to **Settings → Sponsor this project**
- [ ] Enable GitHub Sponsors
- [ ] Add sponsor tiers ($5, $25, $100/month)
- [ ] Write sponsorship message

### Step 5: Enable Discussions (Community)
- [ ] Go to **Settings → Features**
- [ ] Enable ✅ **Discussions**
- [ ] Customize categories (Q&A, Feature Requests, Announcements)

### Step 6: Create First Good Issues
- [ ] Create 3-5 issues labeled `good first issue`
- [ ] Examples:
  - "Add Kotlin support to docker_manager.py"
  - "Write tests for OpenClaw Telegram integration"
  - "Improve Logic Ladder documentation"

---

## Phase 3: Docker Hub Publishing (15 min)

### Step 1: Create Docker Hub Account
- [ ] Go to [hub.docker.com](https://hub.docker.com)
- [ ] Sign up (free)
- [ ] Note your username

### Step 2: Create Repositories
- [ ] Create public repo `alkemist-server`
- [ ] Create public repo `alkemist-client`
- [ ] Add descriptions:
  - Server: "Alkemist Backend — Local AI-native IDE, FastAPI + LangGraph"
  - Client: "Alkemist Frontend — Next.js IDE UI with Monaco editor"

### Step 3: Publish Images
Choose one method:

**Method A: Automated Script (1 min)**
```bash
chmod +x scripts/publish-to-docker-hub.sh
./scripts/publish-to-docker-hub.sh <your-username> 0.1.0
```

**Method B: Manual (see [docs/docker-hub-publishing.md](docs/docker-hub-publishing.md))**
```bash
docker build -t <username>/alkemist-server:0.1.0 ./alkemist-server
docker push <username>/alkemist-server:0.1.0
# ... repeat for client
```

### Step 4: Verify
- [ ] Visit your Docker Hub profile
- [ ] Confirm both images appear with correct tags
- [ ] Test pulling locally: `docker pull <username>/alkemist-server:0.1.0`

---

## Phase 4: Update Documentation (5 min)

- [ ] Update `README.md` with your GitHub repo URL
- [ ] Update `README.md` with your Docker Hub username
- [ ] Update `docker-compose.yml` to reference your public images (optional)

Example:
```yaml
backend:
  image: yourname/alkemist-server:0.1.0  # ← Your Docker Hub image
```

---

## Phase 5: Git Commits & Tags (5 min)

```bash
cd /workspaces/Alkemist

# Commit all changes
git add -A
git commit -m "feat: Dockerfile, Docker Hub publishing, and public launch docs"

# Create version tag
git tag -a v0.1.0 -m "Alkemist v0.1.0 — Privacy-first AI IDE, public launch"
git push origin main
git push origin v0.1.0
```

- [ ] Commit message is clear
- [ ] Tag created (v0.1.0)
- [ ] Pushed to GitHub

---

## Phase 6: Social Media Announcement (Optional but Recommended)

### Twitter/X Post
```
🚀 Excited to announce Alkemist — the AI IDE for people who can't send their code to the cloud.

✅ 100% local execution
✅ HIPAA/PCI-DSS compliant
✅ Open source (MIT)
✅ Powered by Sovern Logic Ladder

GitHub: github.com/yourname/Alkemist
Docker: hub.docker.com/r/yourname

Help us build privacy-first AI development! 🔓
```

**Post on:**
- [ ] Twitter/X
- [ ] LinkedIn
- [ ] Dev.to article
- [ ] Reddit r/opensource
- [ ] Hacker News (Show HN)

### Blog Post (Optional)
- [ ] Write "Why We Built Alkemist" blog post
- [ ] Include positioning strategy
- [ ] Link to GitHub and Docker Hub
- [ ] Promote on social media

---

## Phase 7: Community Engagement

- [ ] Monitor GitHub Issues/Discussions
- [ ] Respond to first contributors
- [ ] Welcome PR comments
- [ ] Update changelog with releases

```bash
# Example: Create initial release
git tag -a v0.1.0 -m "Initial public release"
git push origin v0.1.0
```

Then on GitHub: **Releases → Create Release from tag → Auto-generate release notes**

---

## Phase 8: Optional Enhancements

### Continuous Integration (GitHub Actions)
- [ ] Create `.github/workflows/tests.yml` — Run tests on push
- [ ] Create `.github/workflows/docker-publish.yml` — Auto-push to Docker Hub on release

### Documentation Site
- [ ] Enable GitHub Pages
- [ ] Generate site from markdown docs

### Security
- [ ] Add `SECURITY.md` vulnerability reporting policy
- [ ] Enable branch protection (main branch) → require PR reviews

### Badges
Add to README:
```markdown
[![GitHub License](https://img.shields.io/github/license/yourname/Alkemist)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/yourname/Alkemist?style=social)](https://github.com/yourname/Alkemist)
[![Docker Pulls](https://img.shields.io/docker/pulls/yourname/alkemist-server)](https://hub.docker.com/r/yourname/alkemist-server)
```

---

## Quick Verification Commands

```bash
# Test local Docker Compose
docker compose up -d
docker compose ps
curl http://localhost:8000/health

# Test public images (after publishing)
docker pull yourname/alkemist-server:0.1.0
docker pull yourname/alkemist-client:0.1.0

# View Docker Hub
open https://hub.docker.com/r/yourname/alkemist-server
open https://hub.docker.com/r/yourname/alkemist-client

# View GitHub
open https://github.com/yourname/Alkemist
```

---

## Timeline Estimate

| Phase | Tasks | Time |
|-------|-------|------|
| Phase 1 | Documentation & Dockerfiles | ✅ Done |
| Phase 2 | GitHub public setup | 10 min |
| Phase 3 | Docker Hub publishing | 15 min |
| Phase 4 | Documentation updates | 5 min |
| Phase 5 | Git commits & tags | 5 min |
| Phase 6 | Social media announcement | 20 min |
| **Total** | **All Phases** | **~1 hour** |

---

## Post-Launch (30 days)

- [ ] Monitor GitHub stars & forks
- [ ] Engage with first contributors
- [ ] Fix any bugs reported
- [ ] Write case study blog post
- [ ] Reach out to 5 enterprise prospects

---

## Success Metrics (90 days)

- ⭐ **GitHub Stars:** 100+
- 👥 **Contributors:** 5+
- 🐳 **Docker Pulls:** 500+
- 💬 **Issues/Discussions:** 20+
- 📧 **Email Inquiries:** 3-5 from enterprises

---

**You're ready to launch! 🚀**

Next step: Complete Phase 2 (Make GitHub public) and Phase 3 (Publish Docker Hub).

Questions? See [docs/](docs/) for detailed guides.
