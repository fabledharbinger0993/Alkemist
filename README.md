# Alkemist

**The AI IDE that keeps your code private.** 🔐

An AI-powered coding environment that runs completely on your computer — no cloud, no subscriptions, no data sent anywhere.

---

## What is Alkemist?

Alkemist is an IDE (Integrated Development Environment) with AI built in. It helps you:

- 📝 **Write & edit code** — Python, TypeScript, Go, Rust, Bash
- 🤖 **Get AI suggestions** — Running on your computer (no paid API calls)
- 🧪 **Run & test code** — Safely in isolated containers
- 💬 **Chat with AI** — Via web UI or Telegram
- 🔐 **Keep data private** — Your code never leaves your computer

**Unlike Cursor or GitHub Copilot,** which send your code to cloud servers, Alkemist stays 100% local.

**Perfect for:**
- 🏥 Healthcare companies (HIPAA compliance)
- 💰 Banks & finance (PCI-DSS compliance)
- 🔒 Defense contractors & government
- 🚀 Startups with secret code
- 👥 Any team that won't share code with vendors

---

## Get Started (3 Minutes)

### Option 1: Docker (Easiest)

```bash
git clone https://github.com/fabledharbinger0993/Alkemist.git
cd Alkemist
docker compose up -d
```

Open browser: **http://localhost:3000**

Done! ✨

**Useful commands:**
```bash
docker compose ps         # Check status
docker compose logs -f    # View logs
docker compose down       # Stop
```

### Option 2: Without Docker

See [Getting Started Guide](docs/getting-started.md).

---

## Why Alkemist?

| Feature | Alkemist | Cursor | Copilot |
|---------|----------|--------|---------|
| Runs locally | ✅ | ❌ | ❌ |
| Hospital-safe | ✅ | ❌ | ❌ |
| Free | ✅ | ❌ ($20/mo) | ❌ ($20/mo) |
| Open source | ✅ | ❌ | ❌ |
| Code stays private | ✅ | ❌ | ❌ |

**The bottom line:** If you can't send code outside your company, Alkemist is the only option.

---

## What Can You Do?

| What | How |
|------|-----|
| Write code | Use the web-based editor |
| Get AI help | Ask questions, get suggestions |
| Run code | Execute safely in containers |
| Control from phone | Send commands via Telegram |
| Stay compliant | Never send  code to the cloud |

---

## Docs

### 👤 For Users
| Guide | Read If |
|-------|---------|
| [Hold My Hand](docs/hold-my-hand.md) | You need help installing git/Docker/Python |
| [Getting Started](docs/getting-started.md) | You want step-by-step setup |
| [How It Works](docs/how-it-works.md) | You want to understand the AI |
| [Quick Reference](docs/quick-reference.md) | You need command copy-paste reference |

### 👨‍💻 For Developers
| Guide | Read If |
|-------|---------|
| [Contributing](CONTRIBUTING.md) | You want to add features |
| [Development Setup](docs/development-setup.md) | You want to develop Alkemist locally |
| [Architecture](docs/architecture.md) | You want to understand how it works inside |

### 🏢 For Companies
| Guide | Read If |
|-------|---------|
| [Why We Built This](docs/positioning.md) | You want business context & roadmap |

### 🔧 For Maintainers (Project Admins)
| Guide | Read If |
|-------|---------|
| [Launch Checklist](docs/LAUNCH_CHECKLIST.md) | You're releasing a new version |
| [Docker Hub Publishing](docs/docker-hub-publishing.md) | You're publishing images to Docker Hub |
| [GitHub Public Setup](docs/github-public-setup.md) | You're setting up a public GitHub repo |

---

## Links

- 💻 [GitHub](https://github.com/fabledharbinger0993/Alkemist)
- 🐳 [Docker Hub](https://hub.docker.com/r/fabledharbinger0993/alkemist-server)
- 📚 [Full Docs](docs/)
- 🤝 [Contributing](CONTRIBUTING.md)
- ⚖️ [License](LICENSE) (MIT)

---

## Questions?

- 📖 Check the [docs](docs/)
- 🐛 [Report bug](https://github.com/fabledharbinger0993/Alkemist/issues)
- 💬 [Ask question](https://github.com/fabledharbinger0993/Alkemist/discussions)
- ⭐ [Like it? Star us!](https://github.com/fabledharbinger0993/Alkemist)

---

**Privacy first. Control always. No compromise.** 🔐
