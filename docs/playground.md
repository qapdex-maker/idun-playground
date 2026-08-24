---
title: Router Playground
description: Local multi-backend LLM router and Studio-style playground for the NatureLM-Idun-5-MoE agent — Contoso prompt lab, API reference, auth guide, and live telemetry.
author: Idun SDK
ms.author: idun-sdk
ms.date: 2026-08-24
ms.topic: how-to
---

# Router Playground

The **Router Playground** is a local, single-process web UI that exercises the
`NatureLM-Idun-5-MoE` agent (and two sibling backends) through a small
multi-backend LLM router. It is the fastest way to try Contoso-style prompts
against the live Foundry agent without writing any client code.

This article is part of the Microsoft Learn-style documentation set. Use the
table of contents to navigate between the endpoint reference, the auth guide,
and the FAQ.

## In this article

- [What is the Router Playground](#what-is-the-router-playground)
- [Architecture](#architecture)
- [Start the router](#start-the-router)
- [Open the playground](#open-the-playground)
- [Backends and status](#backends-and-status)
- [Live telemetry](#live-telemetry)
- [Troubleshooting](#troubleshooting)

## What is the Router Playground

The playground serves four Studio-style pages that all talk to one local
router process (`router.py`, listening on `127.0.0.1:9001`):

| Page | File | Purpose |
| --- | --- | --- |
| Contoso Prompt Lab | `playground.html` | Chat against any backend with canned Contoso examples + **agent trace** |
| API reference | `api-reference.html` | Endpoint docs + live **Try it** panel |
| Auth guide | `auth-guide.html` | Device-code flow + live token-status probe |
| FAQ | `faq.html` | Searchable Q&A |

All four pages use the **Azure AI Foundry dark theme** (deep anthracite
`#0e0e12` with foundry-purple `#8b5cf6` accent). A `light_mode` toggle in the
top bar persists the choice in `localStorage`.

No secrets are embedded in the HTML. The router holds the credentials
(`FOUNDRY_TOKEN`, `AZURE_OPENAI_API_KEY`, `cf-aig-authorization`) server-side,
so the browser never sees a token and suffers no CORS exposure.

## Architecture

| Layer | Component | Notes |
| --- | --- | --- |
| UI | `*.html` (Tailwind, no build step) | Studio/paper look; Contoso (Segoe UI) + Foundry (Playfair Display) type |
| Router | `router.py` (ThreadingHTTPServer) | Selects backend by `model` prefix; 600 s timeout; structured 403 body |
| Identity | Microsoft Entra ID | Device-code bearer token; scope `https://ai.azure.com/.default` |
| Backend A | Azure AI Foundry | `foundry:NatureLM-Idun-5-MoE` → agent via OpenAI responses protocol |
| Backend B | Azure OpenAI | `aoai:gpt-4o` (requires `AZURE_OPENAI_API_KEY`) |
| Backend C | Cloudflare AI Gateway | `cfut:*` → `dynamic/Idun-Instruct-VL-BitNet` (requires `cf-aig-authorization`) |

The Foundry backend sends the verified request shape:

```json
{
  "model": "model-router",
  "input": "Your prompt here",
  "max_output_tokens": 4096
}
```

> [!IMPORTANT]
> When the agent is in the URL path, the request body **must** set
> `"model": "model-router"`. Using the agent name returns `invalid_payload`.
> The router builds this shape automatically from a normal chat `messages` array.

## Agent trace

`NatureLM-Idun-5-MoE` is a **tool agent**: it reasons, then calls `web_search`
and `memory_search` before answering. The router surfaces the full trajectory,
not just the final text:

- The playground renders every step in the **AGENT TRACE** panel — reasoning
  blocks (`psychology` icon) interleaved with `web_search` tool calls
  (`public` icon) showing the live query and status (`SUCHT…` / `✓ DONE`).
- The router response includes a `steps` array (`kind: reasoning | tool`) plus
  the concatenated final `text`.

This makes Idun a visible, auditable agent rather than a black-box chatbot
wheel: you can watch which searches it ran to reach the answer.

## Start the router

Set the credentials, then start the router (it reads `FOUNDRY_TOKEN`,
`FOUNDRY_TIMEOUT`, and `AZURE_OPENAI_API_KEY` from the environment):

```bash
export FOUNDRY_TOKEN="$(cat ~/foundry_token.txt)"
export FOUNDRY_TIMEOUT=600
cd workspace/webapp
python3 run_router.py
# Serving on http://127.0.0.1:9001/
```

The router uses `ThreadingHTTPServer`, so concurrent requests (health pings
plus a prompt) do not block each other. The Foundry timeout is intentionally
generous — complex Contoso prompts can take minutes.

## Open the playground

Open `http://127.0.0.1:9001/playground.html` in a browser. Pick a backend from
the dropdown, choose a Contoso example (or type your own prompt), and select
**Senden**. The answer appears below; latency is shown in the status card.

## Backends and status

The status card shows live reachability for each backend:

- **Foundry** — green when the Entra token is valid (HTTP 200 from the agent).
- **Azure OpenAI** — degraded until `AZURE_OPENAI_API_KEY` is supplied.
- **Cloudflare** — degraded until a valid `cf-aig-authorization` token is set.

A 403 from Foundry is surfaced as a structured JSON error:

```json
{
  "error": "upstream auth rejected (token expired or invalid)",
  "status": 403,
  "backend": "foundry",
  "hint": "rotate FOUNDRY_TOKEN via device_code_login.py"
}
```

## Live telemetry

The telemetry terminal at the bottom of the playground is **real**, not
synthetic. It logs:

- Startup events (router ready, telemetry live).
- A periodic health ping to the Foundry path every 30 s, showing the true
  HTTP status and latency.
- Every prompt you send, with its backend, HTTP status, and latency — including
  the verbatim 403 error if the token has expired.

This makes the "unknown 403" failure mode observable: when the token lapses,
the stream prints `ERR: foundry 403 — upstream auth rejected …` instead of a
silent empty response.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ERR: foundry 403` in telemetry | Entra token expired | Re-run `scripts/rotate_foundry_token.py` (device-code) and restart the router |
| `AOAI` stays degraded | `AZURE_OPENAI_API_KEY` unset | Export the key and restart the router |
| `Cloudflare` stays degraded | `cf-aig-authorization` expired | Supply a fresh Cloudflare account API token |
| Prompt returns in ~190 s | Expected | Foundry agent latency on complex prompts; timeout is 600 s |

## Next steps

- See [Endpoint reference](endpoint-reference.md) for the full request/response shape.
- See [Authenticate](how-to-auth.md) to rotate the Entra token.
- See [FAQ](faq.md) for the `model-router` requirement and Termux caveats.
