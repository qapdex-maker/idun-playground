# Idun Roadmap

Status quo, nah, mittelfristig und Vision für das Idun-Projekt
(SDK + Playground + Docs). Stand: 2026-08-19 (update 2).

## Status quo (erledigt, live)

1. **idun-sdk 1.0.17** — Python-Client + CLI, Entra Device-Code-Auth,
   steps-Relay, 17-provider registry, 16-bit retro console, MCP server.
   - GitHub `main` (ba78c14): README/CHANGELOG/pyproject updated.
   - CI: grün (pytest 3.8–3.14 + ruff==0.15.10; Termux job removed).
   - **PyPI:** 1.0.16 live; 1.0.17 built + pushed to GitHub, upload
     pending valid token (403 on all tried tokens).
2. **Tenant-agnostic by default** — Foundry coords from `~/.idun/config.toml`
   `[defaults]`. No hardcoded tenant in shipped code. Neutral `config.example.toml`.
3. **idun-playground** — Dark Foundry look, Agent-Trace-Panel,
   Live/Demo-Badge via `GET /api/health`, Demo-Fallback without token/account.
4. **Demo-Mode erstklassig** — Router serves recorded traces (model
   `demo-replay`) when no token; no crash; UI marks DEMO-REPLAY.
5. **Public Demo (GitHub Pages)** — 8 Contoso traces, **fully English**,
   static, no backend/account: https://qapdex-maker.github.io/idun-playground/
6. **Landing page (qapdex-maker.github.io)** — IDUN-40 neon-outrun console
   (reverted to 4bf945b per preference). Live.
7. **Async + Token rotation + Prompt packs** — `--async` CLI fixed
   (acomplete), auto-rotation in auth.py, 8 contoso prompt packs.

## Phase 2 — Nächste Schritte (nah)

1. **PyPI 1.0.17 upload** — pending valid token (currently 403).
2. **Docs** — Microsoft-Learn style: "own resource needed, demo without
   account" explicit (partially done in playground README).
3. **Trace-Export** — Agent trajectory as JSON/Markdown (offline).
4. **Side-by-Side-Trace** — compare two prompt runs (Tool-Timeline-Diff;
   `/api/diff` present).

## Phase 3 — Mittelfristig

1. **PR #4249 (Connector)** — PAUSED. Waits on Azure RBAC `agents/write`
   (~70 EUR one-time, not paid). LIVE-BLOCKER.
2. **365 calendar** — waits on Exchange license (Graph Device-Code ready).
3. **SSE streaming** in playground instead of poll.

## Phase 4 — Vision

1. **Idun as backend** in Hermes WebUI preview.
2. **Reusable tool-agent visualization** component for other Foundry agents.
3. **Mobile app (PocketPal-hybrid, doc-matrix)** — noted as future direction.

## Showcase (Contoso Expo)

`expo.html` + `/api/expo` + 8 Contoso demos + Live/Demo toggle + Kiosk mode
in playground repo. Public GitHub Pages already covers "demo without account".

---

### Blocker (honest)
- **PR #4249:** org/financial pause (70 EUR RBAC). No code bug.
- **PyPI 1.0.17:** token/permission issue (403). Build is correct.
- **QMFI live test:** same RBAC 403. Offline + demo + external Foundry work.
