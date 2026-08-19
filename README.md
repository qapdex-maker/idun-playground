# Idun Playground

A self-hostable, stdlib-only web playground for the **Idun** agent on Azure AI
Foundry — render the full agent trajectory (reasoning + tool calls) in the
browser, side-by-side trace diffs, and export to JSON / Markdown.

**No account needed to try it.** Out of the box the playground runs in **demo
mode**: it serves recorded, real agent trajectories (full tool traces) so anyone
can see how Idun reasons — without an Azure AI Foundry subscription. To make live
calls, point it at *your own* Foundry resource (see below). The package ships
**no tenant** — every operator brings their own resource.

## Quick start (demo mode, zero config)

```bash
cd idun-playground
python3 run_router.py          # serves on http://127.0.0.1:9001
# open http://127.0.0.1:9001/playground.html
```

The backend status panel shows a **DEMO MODE** badge. Every prompt replays a
recorded trace. Nothing leaves your machine.

## Live mode (your own Azure AI Foundry resource)

1. Copy the neutral config template and fill in **your** values:
   ```bash
   cp ~/.idun/config.toml ~/.idun/config.toml    # if not present yet
   # edit idun_base / idun_project / idun_agent
   ```
   (`config.example.toml` in the **idun-sdk** repo is the source template.
   The playground reads `~/.idun/config.toml` `[defaults] idun_base /
   idun_project / idun_agent`, or the env vars `IDUN_BASE` / `IDUN_PROJECT` /
   `IDUN_AGENT`.)
2. Authenticate (Entra device-code, token is stored locally only):
   ```bash
   idun login --backend azure
   ```
3. Restart the router. The badge flips to **LIVE** and prompts hit your resource.

## How it works

- `router.py` — stdlib `http.server` (no Flask). Endpoints:
  - `GET  /playground.html` — the UI
  - `GET  /api/health` — `{ configured, has_token, live, demo, mode }`
  - `POST /api/chat` — `{ choices:[{message:{content}}], steps:[...] }`
  - `POST /api/chat/stream` — newline-delimited JSON `step`/`done` events
  - `POST /api/diff` — side-by-side trace diff
  - `POST /api/packs`, `/api/run`, `/api/export`
- `run_router.py` — thin launcher: loads Foundry coords from
  `~/.idun/config.toml` (+ token from `~/foundry_token.txt`) into the
  environment **before** importing `router.py`, so the SDK resolves them. No
  tenant-specific values are hard-coded here.
- `demo_traces.py` — the recorded trajectories used in demo mode.

## Demo mode is honest

If no token and no resource are configured, the router **never** contacts a
network and **never** errors out — it replays a recorded trace (model
`demo-replay`, full steps). The UI labels it `DEMO-REPLAY`. This keeps the tool
open to everyone, including users with no Foundry account.

## Tenant-agnostic (hard rule)

The playground and SDK ship **no bundled tenant or resource**. Live calls
require the operator to supply their own Azure AI Foundry resource via config or
environment. Public-facing text refers to "Idun" / "your tenant account", never
a specific tenant name.

## Requirements

- Python ≥ 3.8 (stdlib only — `idun` SDK must be installed: `pip install idun-sdk`)
- No third-party web framework.

## Docker (optional)

```bash
docker build -t idun-playground .
docker run -p 9001:9001 -e BIND_HOST=0.0.0.0 idun-playground
```
In a container set `BIND_HOST=0.0.0.0` and put a TLS-terminating reverse proxy
in front — the router itself has no auth layer beyond the Foundry token.
## Idun Matrix (IDEA α / β)

A Doc × Question pivot built on the idun-sdk. Recorded demo + a tenant-agnostic
bridge PWA:

- **Demo matrix (no account):** <https://qapdex-maker.github.io/idun-playground/matrix.html>
- **Matrix Bridge PWA (PocketPal-style):** <https://qapdex-maker.github.io/idun-playground/matrix_app.html>
  uploads documents (txt/md/pdf) + questions and talks to a local
  `matrix_server.py` that runs `idun matrix` against *your* Azure AI Foundry resource.
- **Concept note:** <https://github.com/qapdex-maker/idun-playground/blob/main/DOC_MATRIX_CONCEPT.md>
