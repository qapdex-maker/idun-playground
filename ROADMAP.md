# Idun Roadmap

Status quo, nahe, mittelfristige und Vision-Ziele für das Idun-Projekt
(SDK + Playground + Docs).

## Status quo (erledigt, live auf GitHub)

1. **idun-sdk** — Python-Client + CLI (`idun login|chat|trace`), Entra
   Device-Code-Auth, steps-Relay. E2E verifiziert (trace = 21 Schritte).
2. **idun-playground** — Dark-Mode im ai.azure.com-Look, Agent-Trace-Panel,
   Live-Telemetrie-Terminal. Live im Edge-Recording bestätigt.
3. **Docs** in beiden Repos + Microsoft-Learn-Stil (`docs/playground.md`).
4. Repos gepusht, `.gitignore` sauber, keine offenen lokalen Diffs.

## Phase 2 — Nächste Schritte (nah)

1. **MCP-Server-Wrapper (2.1)** — `idun_mcp.py` exponiert
   `IdunClient.complete()` als Tool für fremde Agents (FastMCP/`mcp`).
   SDK ist gekapselt, kein CLI-Touch nötig.
2. **Async finalisieren** — echte `asyncio`-Variante + CLI-Flag `--async`.
3. **Test-Suite** — `pytest` statt nur `test.sh`; GitHub Actions CI läuft
   `test.sh` bei jedem Push (offline).
4. **PyPI-Publish** — `pip install idun-sdk` (`setup.py` liegt, braucht
   `python -m build` + `twine`).
5. **Token-Auto-Rotation im CLI** — `idun login` speichert Refresh-Context,
   CLI erneuert `FOUNDRY_TOKEN` vor Ablauf (vorhandenes
   `rotate_foundry_token.sh` einbinden).
6. **Contoso-Prompt-Packs** — kuratierte Demo-Prompts als JSON ladbar.

## Phase 3 — Mittelfristig

1. **PR #4249** bei Microsoft Learn einreichen (NatureLM-Idun-5-MoE Connector,
   independent publisher) — wartet auf Review.
2. **365-Kalendereintrag** — sobald die Exchange-Lizenz nachgerüstet ist
   (Graph Device-Code liegt bereit; 401 = keine Mailbox).
3. **Trace-Export** — Agent-Trajectory als JSON/Markdown speicherbar
   (für Docs/PR-Anhänge).
4. **Side-by-Side-Trace** — zwei Prompt-Läufe nebeneinander vergleichen
   (Tool-Timeline-Diff).

## Phase 4 — Vision

1. **Idun als Backend** in die Hermes WebUI-Preview einhängen.
2. **Wiederverwendbare Tool-Agent-Visualisierung** (Komponente) für andere
   Foundry-Agents.
3. **Streaming (SSE)** im Playground statt Poll — Schritte erscheinen
   zeichengenau live.

## Phase 7 — Contoso Expo 2027 (Showcase)

1. **Expo-Showcase `expo.html`** — eigene Booth-Seite im Foundry-Look
   (Hero + Live-Stage + Demo-Galerie). Lädt Demo-Prompts live aus
   `/api/expo` und startet sie gegen den Agent (progressive Trace-Viz).
2. **Router `/api/expo`** — flatten alle Prompt-Packs zu Demo-Einträgen
   (pack, key, title, prompt, preview). Offline (kein Token nötig), also
   lädt die Galerie selbst ohne Live-Creds.
3. **`/api/packs` um `keys` erweitert** — Playground-Pack-Picker startet
   jetzt den echten ersten Prompt (kein 404 mehr über `firstKey`).
4. **Nav-Link** Playground → Expo; Expo ↔ Playground / Trace Diff.
5. **Expo-Interaktion (korrigiert):** Demo-Auswahl über Dropdown + expliziter
   „Live starten"-Button (kein Auto-Start beim Klick → keine Überlastung).
6. **Offline-Demo-Modus (Booth-fest):** Bei abgelaufenem/exakt keinem
   FOUNDRY_TOKEN liefert der Router aufgezeichnete Contoso-Traces im
   identischen step/done-NDJSON-Format zurück (router.py +
   demo_traces.py). UI zeigt volle Antwort + Schritte + „DEMO-REPLAY"-Badge.
   Live-Lauf greift automatisch, sobald ein gültiges Token vorhanden ist.
7. **Fehler-/Retry-Robustheit:** /api/diff + /api/chat/stream geben bei
   abgelaufenem Token die saubere `No valid FOUNDRY_TOKEN`-Meldung zurück
   (kein nackter HTTP-500 mehr); Frontend zeigt „idun login" an. Transiente
   5xx/429 werden im Frontend 2–3× wiederholt. Antwort wird bei `done` voll
   gerendert + ins Bild gescrollt (kein „zeigt nur die Zeit, dann nix").
   8. **Contoso-Demo-Erweiterung:** 8 Demos im contoso_pack
   (sustainability_summary, esg_check, web_research, competitor_compare,
   supply_chain_dashboard, product_passport, net_zero_roadmap,
   stakeholder_report) — jeweils mit aufgezeichnetem Replay-Trace in
   demo_traces.py.
   9. **Live/Demo-Umschalter (Topbar):** geteilter mode-toggle.js/.css in
   Expo/Playground/Diff. DEMO erzwingt Replays (kein Netzwerk), LIVE
   versucht den echten Lauf (Router fällt bei abgelaufenem Token auf Demo
   zurück). Modus persistiert in localStorage.
