# Architecture — How Alkemist Works (Technical Deep-Dive)

**For developers who want to understand the system design.**

---

## High-Level Overview

Alkemist has 3 main parts:

```
User
  ↓
[Frontend — Next.js React UI]
  ↓ (REST API calls)
[Backend — FastAPI Server]
  ↓ (spawns)
[Local AI + Docker Sandbox]
  ↓
Result back to user
```

**Everything runs locally.** No cloud calls, no data transmission.

---

## Component 1: Frontend (Next.js + React)

### Location
`alkemist-client/`

### What It Does
- Web-based IDE (code editor, file tree, terminal)
- AI chat sidebar
- Build/run UI
- WebSocket connection to backend for real-time updates

### Tech Stack
- **Framework:** Next.js 15
- **Language:** TypeScript
- **UI:** React 19 + Tailwind CSS
- **Editor:** Monaco (same editor as VS Code)
- **Terminal:** xterm.js (web-based terminal)

### Key Files
- `app/layout.tsx` — Main page wrapper
- `app/page.tsx` — IDE layout
- `components/Editor.tsx` — Code editor
- `components/FileTree.tsx` — Project files
- `components/AIChatSidebar.tsx` — AI chat
- `components/Terminal.tsx` — Web terminal
- `lib/api.ts` — API client (calls backend)
- `lib/websocket.ts` — Real-time communication

### How It Works

1. User types code in the editor → stores locally in React state
2. User asks a question → sends to backend via `POST /ai/chat`
3. Backend responds → WebSocket pushes update
4. Frontend displays result in chat sidebar

---

## Component 2: Backend (FastAPI + LangGraph)

### Location
`alkemist-server/`

### What It Does
- Exposes REST API (create projects, read/write files, run code)
- Handles AI reasoning (Logic Ladder)
- Manages file I/O
- Executes code in Docker
- Stores data in SQLite
- Vector memory in ChromaDB

### Tech Stack
- **Framework:** FastAPI (Python)
- **Async:** asyncio + SQLAlchemy async ORM
- **AI:** LangGraph (state machine for reasoning), Ollama (local LLM)
- **Database:** SQLite (projects/files), ChromaDB (vector search)
- **Execution:** Docker Python SDK
- **Logging:** structlog

### Key Files
- `main.py` — App initialization, routers
- `models/database.py` — SQLAlchemy models (Project, File, etc.)
- `models/schemas.py` — Pydantic request/response schemas
- `routers/projects.py` — Project CRUD
- `routers/files.py` — File operations (read/write/delete)
- `routers/ai.py` — AI reasoning endpoint
- `routers/terminal.py` — Terminal execution
- `ai/logic_ladder.py` — 4-stage reasoning
- `execution/docker_manager.py` — Docker execution

### Request Flow

```
HTTP Request → FastAPI Router
  ↓
(example: POST /projects/{id}/files/read)
  ↓
Router function (async)
  ↓
Database query (if needed)
  ↓
Business logic
  ↓
Return JSON response
```

---

## Component 3: AI Reasoning (Sovern Logic Ladder)

### Location
`alkemist-server/ai/logic_ladder.py`

### What It Does
4-stage reasoning pipeline for intelligent code generation:

#### Stage 1: Awareness
- **Input:** User question + project context
- **Process:** RAG (Retrieval-Augmented Generation)
  - Retrieves relevant code from project
  - Fetches docs/context
  - Formats as context
- **Output:** Question + relevant context

#### Stage 2: Literalist
- **Input:** Question + context
- **Process:** Requirement extraction
  - What is the user REALLY asking?
  - What assumptions are there?
  - What's missing?
- **Output:** Clear requirements + constraints

#### Stage 3: Congress
- **Input:** Clear requirements
- **Process:** Multi-perspective debate
  - **Advocate:** Proposes solution
  - **Skeptic:** Finds problems
  - **Synthesizer:** Combines best parts
- **Output:** Refined solution

#### Stage 4: Judge
- **Input:** Solution from Congress
- **Process:** Final decision
  - Format answer clearly
  - Generate commit message
  - Validate code syntax
- **Output:** Final response + commit message

### Why 4 Stages?

Most AI tools do:
```
User Q → Single LLM call → Answer ❌ (often wrong/incomplete)
```

Alkemist does:
```
User Q → [Awareness] → [Literalist] → [Congress debate] → [Judge] → Answer ✅
```

Result: Better reasoning, auditable decision-making, fewer errors.

### Code Example

```python
# In logic_ladder.py
async def logic_ladder_run(state: State) -> dict:
    """Execute all 4 stages."""
    
    # Stage 1: Awareness
    state["steps"].append({
        "stage": "awareness",
        "context": retrieve_context(state["query"])
    })
    
    # Stage 2: Literalist
    state["steps"].append({
        "stage": "literalist",
        "requirements": extract_requirements(state)
    })
    
    # Stage 3: Congress
    advocate_response = await node_advocate(state)
    skeptic_feedback = await node_skeptic(advocate_response)
    synthesized = await node_synthesizer(advocate_response, skeptic_feedback)
    
    # Stage 4: Judge
    final_response = await node_judge(synthesized)
    
    return final_response
```

---

## Component 4: Execution (Docker Sandbox)

### Location
`alkemist-server/execution/docker_manager.py`

### What It Does
Safely runs user code in isolated Docker containers:

```
User: "Run this Python code"
  ↓
Create container with python:3.12-slim
  ↓
Copy code into container
  ↓
Execute python main.py
  ↓
Capture output/errors
  ↓
Stop container
  ↓
Return results
```

### Supported Languages
- Python (`python:3.12-slim`)
- TypeScript/JavaScript (`node:22-slim`)
- Go (`golang:1.22-alpine`)
- Rust (`rust:1.82-slim`)
- Bash (`alpine:latest`)

### Safety Features
- **Isolation:** Each project gets its own container
- **Timeout:** Code kills after 60 seconds
- **Resource limits:** Memory/CPU bounded
- **Cleanup:** Containers auto-deleted after run

### Code Example

```python
# In docker_manager.py
async def run_project(project_id: str, language: str) -> ExecutionResult:
    """Run code in isolated container."""
    
    # Find free port for port mapping
    port = _find_free_port()
    
    # Get Docker image for language
    image = LANGUAGE_IMAGES[language]
    
    # Create & run container
    container = self._client.containers.run(
        image,
        command=LANGUAGE_COMMANDS[language],
        volumes={project_path: "/project"},
        working_dir="/project",
        timeout=EXECUTION_TIMEOUT_SECONDS,
        detach=False,  # Wait for completion
    )
    
    # Capture output
    output = container.logs()
    
    # Cleanup
    container.remove()
    
    return ExecutionResult(success=True, output=output)
```

---

## Component 5: Storage (SQLite + ChromaDB)

### SQLite (Project Data)

**Location:** `data/Alkemist.db`

**Schema:**
```sql
-- Projects
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    language TEXT NOT NULL,
    created_at DATETIME
);

-- Files
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    path TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at DATETIME
);
```

**Usage:**
- Store project metadata
- Store file contents
- Track updates
- Audit logs

### ChromaDB (Vector Memory)

**Location:** Docker container @ localhost:8001

**Purpose:**
- Vector embeddings of code
- Semantic search ("find similar code")
- RAG context retrieval
- Fast lookups for Awareness stage

**Example:**
```python
# Store code embedding
collection.add(
    ids=["file_123"],
    embeddings=[[0.1, 0.2, ...]],  # Embedding vector
    documents=["def get_user(): ..."],
    metadatas={"project": "proj_1"}
)

# Retrieve similar code
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],
    n_results=5
)
```

---

## Data Flow Example: "Write a function to read a file"

### Step 1: User Asks (Frontend)
```javascript
// Editor.tsx
const response = await api.post(`/ai/chat`, {
    project_id: "proj_123",
    message: "Write a Python function to read a file",
    model: "mistral"
});
```

### Step 2: Backend Receives (FastAPI)
```python
# routers/ai.py
@router.post("/projects/{project_id}/chat")
async def ai_chat(project_id: str, request: ChatRequest):
    # Validate project exists
    project = db.query(Project).filter_by(id=project_id).first()
    
    # Call Logic Ladder
    result = await logic_ladder_run(
        query=request.message,
        project=project,
        model="mistral"
    )
    
    return {"response": result.response}
```

### Step 3: Logic Ladder Runs (4 Stages)

**Stage 1 - Awareness:**
```python
context = retrieve_context(
    project=project,
    query="write function to read file"
)
# Returns: existing Python files, error handling patterns
```

**Stage 2 - Literalist:**
```python
requirements = extract_requirements(
    query="Write a Python function to read a file",
    context=context
)
# Returns: "Need function, accepts filename, returns content, handle errors"
```

**Stage 3 - Congress:**
```python
# Advocate proposes
advocate: "def read_file(name): return open(name).read()"

# Skeptic challenges
skeptic: "No error handling! What if file doesn't exist?"

# Synthesizer combines
synthesizer: "def read_file(name):\n  try:\n    return open(name).read()\n  except FileNotFoundError: ..."
```

**Stage 4 - Judge:**
```python
final = format_response(synthesizer_response)
# Returns:
# """Here's a function to read a file:
# def read_file(filename):
#     try:
#         with open(filename, 'r') as f:
#             return f.read()
#     except FileNotFoundError:
#         print(f"File {filename} not found")
#         return None
# """
```

### Step 4: Response to Frontend
```json
{
  "response": "Here's a function to read a file...",
  "code_suggestion": "def read_file(filename): ...",
  "commit_message": "Add file reading utility function"
}
```

### Step 5: Frontend Displays
- Shows response in chat
- User can copy/apply code
- Adds to editor automatically

---

## API Endpoints

### Projects
```
GET    /projects              — List all projects
POST   /projects              — Create project
GET    /projects/{id}         — Get project details
DELETE /projects/{id}         — Delete project
```

### Files
```
GET    /projects/{id}/files         — List files
POST   /projects/{id}/files         — Create file
GET    /projects/{id}/files/{path}  — Read file
PUT    /projects/{id}/files/{path}  — Update file
DELETE /projects/{id}/files/{path}  — Delete file
```

### AI
```
POST   /projects/{id}/chat          — Ask AI question
GET    /projects/{id}/ai/status     — AI status
```

### Execution
```
POST   /projects/{id}/build         — Build project
POST   /projects/{id}/run           — Run project
GET    /projects/{id}/logs          — Get execution logs
```

---

## Deployment

### Docker Compose Stack

```yaml
services:
  backend:           # FastAPI server (port 8000)
  frontend:          # Next.js app (port 3000)
  chromadb:          # Vector DB (port 8001)
  ollama:            # Local LLM (port 11434)
```

### Networking

- **Frontend → Backend:** HTTP/REST (port 3000 → 8000)
- **Backend → Ollama:** HTTP (8000 → 11434)
- **Backend → ChromaDB:** REST API (8000 → 8001)
- **Backend → Docker:** Unix socket (`/var/run/docker.sock`)

---

## Security

### What's Protected?

✅ **Code never leaves your computer** — All processing local  
✅ **Docker isolation** — Each project in separate container  
✅ **No telemetry** — No data collection  
✅ **HTTPS ready** — Can add SSL/TLS in production  

### What's NOT Protected?

⚠️ **Open to localhost only** — Binds to 127.0.0.1 (can't be accessed remotely)  
⚠️ **No authentication** — Single-user, local development  
⚠️ **Docker access** — Anyone with local access can run commands  

### Production Hardening

For production deployment, add:
- Authentication (JWT, etc.)
- HTTPS/SSL
- Rate limiting
- Input validation
- Network isolation

---

## Performance

### Frontend
- Next.js serves static assets (fast)
- Monaco editor optimized for large files
- Real-time websocket updates (low latency)

### Backend
- Async FastAPI (handles concurrent requests)
- SQLite for small projects (good for local dev)
- ChromaDB vector search (fast semantic queries)
- LLM inference depends on your CPU/GPU

### Docker
- Container startup: ~2-3 seconds
- Code execution: depends on code complexity
- Cleanup: ~1 second

---

## Extending Alkemist

### Add a New Language

Edit `execution/docker_manager.py`:

```python
LANGUAGE_IMAGES["kotlin"] = "eclipse-temurin:21-jdk"
LANGUAGE_COMMANDS["kotlin"] = ["sh", "-c", "kotlinc main.kt && java -cp . MainKt"]
```

### Add a New Reasoning Stage

Edit `ai/logic_ladder.py`:

```python
async def node_validator(state: State):
    """New validation stage."""
    return {"validation": "..."}

# Add to logic_ladder workflow...
```

### Add a New API Endpoint

Create `routers/custom.py`:

```python
@router.get("/custom/hello")
async def hello():
    return {"message": "Hello from custom endpoint"}
```

Register in `main.py`:
```python
from routers import custom
app.include_router(custom.router)
```

---

## Monitoring

### Logs
```bash
# Backend
docker compose logs -f backend

# Frontend
# Check browser console (F12)

# All services
docker compose logs -f
```

### Metrics
```bash
# Docker stats
docker stats

# Database size
du -sh data/Alkemist.db

# Disk usage
du -sh .
```

---

## Next Steps

- 🚀 [Getting Started](getting-started.md) — Run Alkemist
- 💻 [Development Setup](development-setup.md) — Develop it
- 📖 [Contributing](../CONTRIBUTING.md) — Help improve it

---

**Questions?** Ask on [GitHub Discussions](https://github.com/yourname/Alkemist/discussions). 🙌
