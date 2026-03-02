# Alkemist Curated Runtime Pack — Installer Matrix

This document defines a safe, non-marketplace-first install model for tools/extensions used by Alkemist agents.

## Principles

- **Curated by default**: only vetted components from Alkemist registry in MVP.
- **Container-first execution**: agent build/test/run actions prefer sandboxed runtimes.
- **Soft recommendations**: suggested by project type, never hard-locked.
- **Graceful fallback**: if components are missing, agents still run in local-only mode.

## Install Modes

| Mode | Intent | Installs | Best For |
|---|---|---|---|
| `full-pack` | One-click complete setup | All curated language + container components | New users, fastest onboarding |
| `selective-pack` | User chooses from safe catalog | Selected curated components only | Power users with custom stacks |
| `minimal-local` | No additional components | Base model + local system tools only | Air-gapped/local-only workflows |

## Curated Component Catalog (MVP)

### Core Runtime

- `docker-engine` (or compatible runtime)
- `docker-compose`
- `git`
- `nodejs-lts`
- `python-3.12+`

### Language Packs

#### TypeScript / Next.js pack

- `npm`
- `typescript`
- `eslint`
- `prettier`
- `jest`

#### Python / FastAPI pack

- `poetry`
- `pytest`
- `ruff` (optional in MVP)
- `mypy` (optional in MVP)

#### Swift / iOS pack (host-dependent)

- `xcodebuild` (macOS only)
- `notarytool` (macOS only)
- signing profile checks

## Capability Flags

Each component maps to explicit capabilities used by agents.

- `fs.read`, `fs.write`
- `terminal.exec.local`
- `terminal.exec.container`
- `network.none`, `network.restricted`, `network.full`
- `build.run`, `build.test`, `build.package`
- `release.ios.archive`, `release.ios.submit`

## Recommended Add-ons by Program Type (Not Locked)

| Program Type | Suggested Pack | Suggested Tools |
|---|---|---|
| Next.js / React | TypeScript pack | ESLint, Prettier, Jest |
| FastAPI / Python | Python pack | Poetry, Pytest |
| Full-stack TS + Python | TS + Python packs | ESLint + Pytest + Docker |
| Swift / iOS | Swift pack (+ Core Runtime) | xcodebuild, notarytool |
| AI app | Python or TS base + Core Runtime | tracing/eval tools later phase |

Users can always install outside suggestions in `selective-pack` mode.

## Agent Behavior Contract

### Visionary

- Recommends stack + install mode based on app idea.
- Produces plain-language trade-offs for `full-pack` vs `minimal-local`.

### Engineer

- Asks clarifying questions.
- Outputs:
  - README draft (optional toggle)
  - Contractor handoff plan (optional toggle)
- Validates required capabilities before execution.

### Contractor

- Executes with currently available capabilities.
- If a required capability is missing:
  1. Raises one concise prerequisite note.
  2. Suggests one-click install from curated catalog.
  3. Continues with partial/local fallback where possible.

### Finisher

- Focuses on UI polish and consistency.
- Uses available toolchain; does not block on optional extras.

## Sandboxing Policy

### Default

- Run agent code actions in **ephemeral container workspace**.
- Canonical project remains unchanged until user applies a patch.

### Safety Controls

- Read-only base image layers.
- CPU/memory/time limits.
- Restricted network by default.
- Scoped env vars (no raw secrets by default).
- Explicit permission elevation for release/deploy actions.

### Apply Flow

1. Agent edits in sandbox clone.
2. Generate patch + test/build report.
3. User reviews diffs.
4. User applies selected changes to main workspace.

## Installer Manifest Schema (Proposed)

```json
{
  "mode": "full-pack",
  "components": [
    "docker-engine",
    "docker-compose",
    "git",
    "nodejs-lts",
    "python-3.12",
    "poetry",
    "typescript",
    "eslint",
    "prettier",
    "jest",
    "pytest"
  ],
  "capabilities": [
    "fs.read",
    "fs.write",
    "terminal.exec.container",
    "build.run",
    "build.test"
  ],
  "sandbox": {
    "enabled": true,
    "network": "restricted",
    "cpu_limit": "2",
    "memory_limit": "4g",
    "timeout_sec": 900
  }
}
```

## Installer UX Copy (Suggested)

- **Install All (Recommended)**: "Set up all curated language and container components for the smoothest agent workflow."
- **Choose Components**: "Select only the curated tools you want. You can add more later."
- **Local Only**: "No extra installs. Agents use local model/tools and adapt to what’s available."

## Phase Plan

1. **Phase 1**: Curated catalog + 3 install modes + capability checks.
2. **Phase 2**: Sandbox patch/apply flow + resource policies.
3. **Phase 3**: Program-type recommendation ranking.
4. **Phase 4**: Optional advanced external sources behind warnings.

## Out of Scope (MVP)

- Open extension marketplace installs by default.
- Unvetted remote script execution.
- Automatic permission elevation without user confirmation.
