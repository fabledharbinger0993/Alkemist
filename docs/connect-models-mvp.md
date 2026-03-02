# Connect Models — MVP Spec

This spec defines a simple, auditable, provider-flexible connection flow for Alkemist.

## UX Goals

- Let users connect models in under 60 seconds.
- Keep setup easy for local Ollama users.
- Allow optional cloud providers (Claude, Grok, OpenAI-compatible, custom).
- Keep secrets out of plain text config.
- Make every connection and switch auditable.

## Connect Models Window

## Sections

1. **Provider Type**
   - Ollama
   - Anthropic (Claude)
   - xAI (Grok)
   - OpenAI-compatible
   - Custom

2. **Connection Fields (dynamic by provider)**
   - Endpoint URL
   - API key/token (stored in secure store only)
   - Optional custom auth header name
   - Optional organization/project id

3. **Model Discovery**
   - Button: `Fetch Models`
   - Dropdown/list with model tags
   - Test button: `Send Test Prompt`

4. **Persona Mapping**
   - Visionary / Engineer / Contractor / Finisher defaults

5. **Audit & Privacy**
   - Toggle `Log prompt content` (default off)
   - Always log metadata (provider/model/timing/result)

## Data Files

- Provider profile schema: [docs/schemas/model-provider-profile.schema.json](docs/schemas/model-provider-profile.schema.json)
- Audit event schema: [docs/schemas/audit-log-event.schema.json](docs/schemas/audit-log-event.schema.json)

## Example Provider Profile

```json
{
  "version": "v1",
  "active_profile_id": "local-ollama",
  "profiles": [
    {
      "id": "local-ollama",
      "name": "Local Ollama",
      "provider_type": "ollama",
      "endpoint": "http://localhost:11434",
      "auth": {
        "type": "none"
      },
      "models": [
        {
          "name": "llama3.2:1b",
          "recommended_for": ["visionary", "finisher"]
        },
        {
          "name": "qwen2.5-coder:7b",
          "recommended_for": ["engineer", "contractor"]
        }
      ],
      "capabilities": {
        "chat": true,
        "streaming": true,
        "tool_calling": false,
        "json_mode": false,
        "reasoning_trace": false
      },
      "enabled": true
    }
  ],
  "persona_defaults": {
    "visionary": { "profile_id": "local-ollama", "model": "llama3.2:1b" },
    "engineer": { "profile_id": "local-ollama", "model": "qwen2.5-coder:7b" },
    "contractor": { "profile_id": "local-ollama", "model": "qwen2.5-coder:7b" },
    "finisher": { "profile_id": "local-ollama", "model": "llama3.2:1b" }
  }
}
```

## Example Audit Log Event (JSONL)

```json
{
  "version": "v1",
  "event_id": "evt_01JQZ7JY8N8M18Y3Q4R2S6X8W9",
  "timestamp": "2026-03-02T14:15:08.441Z",
  "actor": { "type": "user", "id": "local-user", "display_name": "Owner" },
  "event_type": "provider.switch",
  "result": "success",
  "resource": { "kind": "provider", "id": "local-ollama", "name": "Local Ollama" },
  "provider": {
    "profile_id": "local-ollama",
    "provider_type": "ollama",
    "endpoint": "http://localhost:11434",
    "model": "qwen2.5-coder:7b"
  },
  "persona": "engineer",
  "request": {
    "request_id": "req_01JQZ7K2M5M50PN8R0KQ8B4SJD",
    "prompt_hash": "sha256:4abf...",
    "prompt_logged": false,
    "latency_ms": 802
  },
  "security": {
    "secrets_redacted": true,
    "sandboxed": true,
    "network_mode": "restricted"
  }
}
```

## Security Requirements

- Secrets MUST be stored in OS keychain/secure store, not profile JSON.
- Custom endpoints require explicit consent and warning.
- Provider switching and model installs must emit audit events.
- “One-click install model” allowlist should remain curated in MVP.

## MVP Implementation Phases

1. **Profile CRUD + secure secrets**
2. **Connection test + model fetch**
3. **Persona default mapping**
4. **Audit log writer + JSONL export**
5. **Optional plugin/provider marketplace later**
