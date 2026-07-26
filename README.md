# idun-playground

Azure AI Foundry **dark-mode playground** for the **NatureLM-Idun-5-MoE** agent (codename *Idun*) — built in the `ai.azure.com` visual style: deep anthracite (`#0e0e12`) background, foundry-purple (`#8b5cf6`) accent, glow buttons, light-mode toggle (persisted in `localStorage`).

Idun is a **tool agent** (it calls `web_search` / `memory_search`). The playground surfaces the full **agent trajectory**, not just the final text:

- **Agent Trace panel** — every reasoning step and `web_search` tool call (with the live query + status) is rendered as a vertical step stream. No black-box chatbot wheel.
- **Live telemetry terminal** — real router logs (health pings, prompt events, verbatim 403s), not synthetic.
- **Backend status** — Foundry / Azure OpenAI / Cloudflare reachability with green/orange dots.

## Files

| File | Purpose |
| --- | --- |
| `playground.html` | Contoso prompt lab + agent trace + telemetry (dark Foundry theme) |
| `api-reference.html` | Endpoint docs + live **Try it** panel |
| `auth-guide.html` | Device-code flow + live token-status probe |
| `faq.html` | Searchable Q&A |
| `server.py` | Multi-backend router (ThreadingHTTPServer, port 9001) — holds credentials server-side |
| `backends.json` | Backend configuration |

## Run

```bash
export FOUNDRY_TOKEN="$(cat ~/foundry_token.txt)"
export FOUNDRY_TIMEOUT=600
cd idun-playground
python3 server.py
# open http://127.0.0.1:9001/playground.html
```

No secrets in the HTML — the router reads `FOUNDRY_TOKEN` (and `AZURE_OPENAI_API_KEY`,
`cf-aig-authorization`) server-side, so the browser never sees a token.

For a Python client + CLI against the same agent, see the companion repo
[idun-sdk](https://github.com/qapdex-maker/idun-sdk).
