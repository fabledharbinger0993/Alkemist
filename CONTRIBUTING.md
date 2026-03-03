# Contributing to Alkemist

Thank you for wanting to help! We're building the AI IDE for developers who value privacy.

---

## How to Help

### You Don't Need Coding Skills For:
- 📝 Writing docs (lots of people find our docs confusing!)
- 🐛 Reporting bugs (describe what went wrong)
- 💡 Suggesting features (tell us what you'd love to see)
- ❓ Answering questions on [GitHub Discussions](https://github.com/yourname/Alkemist/discussions)

### You Should Know Coding For:
- 🎨 Building UI features
- 🐍 Fixing bugs in the backend
- 🧪 Writing tests
- 🚀 Adding new languages/frameworks

---

## Getting Set Up (for Coding)

### Backend Development

```bash
cd alkemist-server
pip install poetry
poetry install          # Install all dependencies
poetry run pytest       # Make sure tests pass (should see ✅ 73 tests passing)
poetry run uvicorn main:app --reload --port 8000   # Start the server
```

### Frontend Development

```bash
cd alkemist-client
npm install
npm run dev             # Start dev server at http://localhost:3000
npm run type-check      # Check for TypeScript errors
npm run lint            # Check for code style issues
npm test                # Run tests
```

---

## What to Work On

### Easy (Great Starting Points)
- Add docs or improve existing ones
- Fix typos or unclear messages
- Improve error messages
- Add tests for existing code
- Report bugs you find

### Medium
- Add a new language to docker_manager.py (it's simpler than you think!)
- Add a new command to Telegram bot
- Improve the web UI styling

### Hard
- Redesign the AI reasoning stages
- Add new features to the Logic Ladder
- Optimize Docker execution

---

## Steps to Contribute Code

1. **Fork** the repo (click "Fork" on GitHub)

2. **Clone your copy:**
   ```bash
   git clone https://github.com/yourname/Alkemist.git
   cd Alkemist
   ```

3. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
   (Names like `feature/python-support` or `fix/telegram-timeout`)

4. **Make changes** and test them locally

5. **Run validation:**
   ```bash
   # Backend
   cd alkemist-server && poetry run pytest
   
   # Frontend
   cd alkemist-client && npm run type-check && npm run lint
   ```

6. **Commit with a clear message:**
   ```bash
   git commit -m "Add support for Python 3.12"
   ```

7. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** on GitHub
   - Describe what you did in 1-2 sentences
   - Say why you made the change
   - Link to any related issues

---

## Code Standards

### Python
- Type annotations required: `def get_files(path: str) -> list[str]:`
- Use async for FastAPI: `async def get_data() -> dict:`
- Tests go in `alkemist-server/tests/`

### TypeScript/React
- Functional components, no class components
- Type props: `interface Props { name: string; }>`
- Tailwind CSS for styling

### All Code
- Keep functions short and readable
- Add comments for tricky parts
- One feature per commit

---

## Before You Submit

```bash
# Backend
cd alkemist-server
poetry run pytest -v

# Frontend
cd alkemist-client
npm run type-check
npm run lint
npm test
```

**All tests must pass.** If one fails, fix it before submitting.

---

## Commit Messages (Simple Rules)

✅ Good:
```
Add support for Rust projects
Fix timeout issue in Telegram bot
Improve docs for setup
```

❌ Bad:
```
updated stuff
Fix
WIP - testing
```

---

## Questions?

- 📖 Check [the docs](docs/)
- 💬 Ask on [GitHub Discussions](https://github.com/yourname/Alkemist/discussions)
- 🐛 Found a bug? [Open an issue](https://github.com/yourname/Alkemist/issues)

---

## Thank You! 🙏

Every contribution helps build privacy into software development. You're awesome! 🚀
