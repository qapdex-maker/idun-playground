# idun-playground

Azure AI Foundry **dark-mode playground** for the **NatureLM-Idun-5-MoE** agent (codename *Idun*) — built in the `ai.azure.com` visual style: deep anthracite (`#0e0e12`) background, foundry-purple (`#8b5cf6`) accent, glow buttons, light-mode toggle (persisted in `localStorage`).

Idun is a **tool agent** (it calls `web_search` / `memory_search`). The playground surfaces the full **agent trajectory**, not just the final text:

- **Agent Trace panel** — every reasoning step and `web_search` tool call (with the live query + status) is rendered as a vertical step stream. No black-box chatbot wheel.
- **Live telemetry terminal** — real router logs (health pings, prompt events, verbatim 403s), not synthetic.
- **Backend status** — Foundry / Azure OpenAI / Cloudflare reachability with green/orange dots.

## Files

| File | Purpose |
| --- | --- |
| `playground.html` | Prompt lab + agent trace + telemetry (dark Foundry theme) |
| `diff.html` | Side-by-side trace diff of two prompts |
| `trace-viz.js` / `trace-viz.css` | Reusable trajectory renderer (shared by playground + diff) |
| `router.py` | Stdlib HTTP router (ThreadingHTTPServer, port 9001) — holds credentials server-side |
| `assets/` | Logo SVGs (Foundry + Idun) |

## API (router.py)

| Endpoint | Method | Payload | Returns |
| --- | --- | --- | --- |
| `/api/chat` | POST | `{messages:[{role,content}], max_tokens?}` | `{choices, steps, model}` |
| `/api/chat/stream` | POST | same as `/api/chat` | NDJSON events: `step` / `done` (honest step-wise, not fake token streaming) |
| `/api/diff` | POST | `{prompt_a, prompt_b, max_tokens?}` | `{trace_a, trace_b, shared_queries, only_a, only_b, same_answer}` |
| `/api/export` | POST | `{messages:[{role,content}]` or `{prompt}`, `format: json\|md` | `{format, content}` — full trajectory as JSON or Markdown |
| `/api/packs` | POST | `{}` | `{packs:[{name, title, description, count}]}` |
| `/api/run` | POST | `{pack, key, max_tokens?}` | `{choices, steps, model}` for a bundled prompt |

The router mirrors the companion [idun-sdk](https://github.com/qapdex-maker/idun-sdk) (v0.1.21+) client surface (`export`/`diff`/`packs`/`run`).

## Run

```bash
export FOUNDRY_TOKEN="$(cat ~/foundry_token.txt)"
export FOUNDRY_TIMEOUT=600
cd idun-playground
python3 router.py
# open http://127.0.0.1:9001/playground.html
```

No secrets in the HTML — the router reads `FOUNDRY_TOKEN` server-side, so the browser never sees a token.

## MCP — docs mirror

The playground docs are exposed as a GitMCP server so AI tools can read them live:

```
https://gitmcp.io/qapdex-maker/idun-playground/sse
```

To actually **call** the agent (not just read docs), use the
[idun-sdk MCP server](https://github.com/qapdex-maker/idun-sdk#1-idun-mcp-server-stdlib-only-local)
(`idun_chat` / `idun_trace` over stdio). The recommended stack for a foreign
agent is both: `idun` (invoke) + `idun-playground-docs` (look up the playground
architecture on its own).
