# Idun Playground

Dark-mode Azure AI Foundry–style playground for the **NatureLM-Idun-5-MoE** agent.
Renders the full tool-agent trajectory (reasoning steps + tool calls) live, not
just chat text.

> The Idun SDK / playground are neutral, reusable components. They are not
> affiliated with or endorsed by Microsoft or any specific tenant — point them
> at your own Foundry deployment via a token you supply.

## What it does

- **Agent trace panel** — every step (reasoning, tool call w/ query + status)
  renders progressively as the agent works.
- **Live telemetry terminal** — request/response log, latency, model used.
- **Prompt packs** — load curated prompts, run them directly.
- **Export** — dump the full trajectory as JSON or Markdown.
- **Side-by-side diff** — compare two prompt runs (shared / unique tool queries).

## Run locally (no Docker)

```bash
pip install -r requirements.txt     # pulls idun-sdk>=0.1.21
idun login                           # device-code login -> ~/foundry_token.txt
python3 router.py                   # http://127.0.0.1:9001/playground.html
```

The router binds to **loopback only** by default (`127.0.0.1`) so the
Foundry-backed endpoint is never exposed on your LAN.

## Endpoints (served by `router.py`)

| Endpoint | Method | Body | Returns |
| --- | --- | --- | --- |
| `/api/chat` | POST | `{messages:[{role,content}]`, `max_tokens` | `{choices, steps, model}` — full answer |
| `/api/chat/stream` | POST | same | newline-delimited JSON: `step` (per step, with `index`) then `done` |
| `/api/diff` | POST | `{prompt_a, prompt_b, max_tokens}` | `{trace_a, trace_b, shared_queries, only_a, only_b}` |
| `/api/export` | POST | `{messages:[{role,content}]` or `{prompt}`, `format: json\|md` | `{format, content}` — full trajectory as JSON or Markdown |
| `/api/packs` | POST | `{}` | `{packs:[{name,title,description,count}]}` |
| `/api/run` | POST | `{pack, key, max_tokens}` | `{choices, steps, model}` — run a bundled prompt pack |

> Note the escaped `\|` in the `format` column above — both `json` and `md` are
> accepted; anything else returns HTTP 400.

## Cloud-ready (Docker)

A `Dockerfile`, `.dockerignore` and `deploy.sh` are included.

```bash
idun login                          # ensure a fresh token exists
./deploy.sh                         # builds image, runs container on :9001
```

The container binds on `0.0.0.0:9001` *inside* the container. `deploy.sh`
publishes it on **loopback only** (`127.0.0.1:9001`) and passes the Foundry
token as a runtime secret (`-e FOUNDRY_TOKEN=...`) — the token is **never
baked into the image**.

**For remote hosting:** put a TLS-terminating reverse proxy (nginx/Caddy) in
front of the container and do **not** publish port 9001 to the public internet
directly. The router has no auth layer of its own beyond the Foundry token, so
the proxy is your perimeter (add auth there if untrusted users can reach it).

### Environment variables

| Var | Default | Meaning |
| --- | --- | --- |
| `FOUNDRY_TOKEN` | (none) | Access token for the Foundry Responses API. Required. |
| `BIND_HOST` | `127.0.0.1` | Host the router binds to. Set `0.0.0.0` inside a container. |
| `PORT` | `9001` | Listen port (code default; not yet env-overridable without editing). |

## Security notes

- The token lives **server-side** (router / container env). The browser never
  sees it.
- A bare `python3 router.py` is loopback-only. Only `BIND_HOST=0.0.0.0` (or
  `deploy.sh`) exposes it, and that is meant to sit behind a proxy.
- Expired token + no refresh context => the router fails fast with a clear
  error (no interactive device-code hang).
