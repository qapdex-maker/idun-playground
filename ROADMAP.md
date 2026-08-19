# Idun Roadmap

Status quo, nah, mittelfristig und Vision für das Idun-Projekt
(SDK + Playground + Docs). Stand: 2026-08-19.

## Status quo (erledigt, live)

1. **idun-sdk 1.0.15** — Python-Client + CLI (`idun login|chat|trace`),
   Entra Device-Code-Auth, steps-Relay. E2E verifiziert.
   - **PyPI:** `pip install idun-sdk` → 1.0.15 released, METADATA neutral.
   - **CI:** grün (GitHub Actions, pytest matrix 3.8–3.14 + ruff==0.15.10).
   - **MCP:** `idun_mcp.py` exponiert `IdunClient.complete()`; serverInfo
     Version aus `__version__` (1.0.15, kein Hardcode-Drift mehr).
2. **Tenant-agnostic by default** — `idun/client.py` liest Foundry-Koords aus
   `~/.idun/config.toml` `[defaults]` (Fallback nach Env). **Keine** hartkodierten
   Tenant-Werte im shipped Code. `config.example.toml` als neutrale Vorlage.
3. **idun-playground** — Dark-Mode im ai.azure.com-Look, Agent-Trace-Panel,
   Live/Demo-Badge via `GET /api/health`, Demo-Fallback ohne Token/Account.
4. **Demo-Mode ist erstklassig** — Router liefert bei fehlendem
   Token/Resource aufgezeichnete Traces (model `demo-replay`, volle Steps),
   kein Crash, UI markiert `DEMO-REPLAY`.
5. **Öffentliche Demo (GitHub Pages)** — `https://qapdex-maker.github.io/idun-playground/`
   zeigt 8 aufgezeichnete Contoso-Traces **statisch, ohne Backend, ohne Account**.
   Trace baut sich Schritt-für-Schritt auf (650 ms) mit weichem Fade-In.
   Kostenlos, teilbar, offen für Nicht-QMFI-Nutzer.

## Phase 2 — Nächste Schritte (nah)

1. **Async finalisieren** — `asyncio`-Variante + CLI-Flag `--async`
   (`async_client.py` ist da, nutzt `run_in_executor` für 3.8-Kompat).
2. **Token-Auto-Rotation im CLI** — `idun login` speichert Refresh-Context,
   CLI erneuert `FOUNDRY_TOKEN` vor Ablauf (vorhandenes
   `rotate_foundry_token.sh` einbinden).
3. **Contoso-Prompt-Packs** — kuratierte Demo-Prompts als JSON ladbar
   (Backend-Router `/api/packs` bereits vorhanden).
4. **Docs** — Microsoft-Learn-Stil aktualisieren; "eigene Resource nötig,
   Demo ohne Account" explizit dokumentieren.

## Phase 3 — Mittelfristig

1. **PR #4249 (NatureLM-Idun-5-MoE Connector)** — **PAUSIERT.**
   Wartet auf Azure RBAC `agents/write` (~70€ One-Time-Role, von dir nicht
   gezahlt). Live-Test gegen QMFI daher LIVE-BLOCKER; echte Connector-
   Verifikation nur durch Endnutzer mit eigenem Foundry möglich.
2. **365-Kalendereintrag** — wartet auf Exchange-Lizenz (Graph Device-Code
   bereit; 401 = keine Mailbox).
3. **Trace-Export** — Agent-Trajectory als JSON/Markdown speicherbar.
4. **Side-by-Side-Trace** — zwei Prompt-Läufe vergleichen (Tool-Timeline-Diff;
   `/api/diff` bereits vorhanden, Demo-Diff offline).

## Phase 4 — Vision

1. **Idun als Backend** in die Hermes WebUI-Preview einhängen.
2. **Wiederverwendbare Tool-Agent-Visualisierung** (Komponente) für andere
   Foundry-Agents.
3. **SSE-Streaming** im Playground statt Poll — Schritte erscheinen live.

## Showcase (Contoso Expo)

`expo.html` (Booth-Seite) + Router `/api/expo` + 8 Contoso-Demos +
Live/Demo-Toggle + Kiosk-Modus liegen im Playground-Repo. Expo-spezifisches
Booth-Branding ist optional; der Kern (Demo zeigen ohne Account) ist bereits
über die öffentliche GitHub Pages abgedeckt.

---

### Blocker (ehrlich)
- **PR #4249:** organisatorisch/finanziell pausiert (70€ RBAC, nicht gezahlt).
  Kein Code-Bug. Wird erst fortgesetzt, wenn RBAC gesetzt wird.
- **QMFI-Live-Test:** selber Blocker (403 RBAC). Offline + Demo + fremde
  Foundry-Ressourcen funktionieren; nur der QMFI-Live-Pfad ist gesperrt.
