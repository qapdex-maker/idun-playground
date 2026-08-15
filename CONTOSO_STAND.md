# Contoso Expo 2027 — Arbeitsstand (Snapshot)

Stand: 2026-08-15 · Repos: `idun-playground` + `idun-sdk` (beide gepusht)

## Was fertig ist
- **Contoso Expo 2027 Booth** (`expo.html`): Dropdown-Demo-Picker + expliziter
  „Live starten"-Button (kein Auto-Start → keine Überlastung).
- **8 Contoso-Demos** im Prompt-Pack (`idun-sdk/idun/data/prompt_packs/contoso_pack.json`):
  sustainability_summary, esg_check, web_research, competitor_compare,
  supply_chain_dashboard, product_passport, net_zero_roadmap, stakeholder_report.
- **Offline-Demo-Modus**: `idun-playground/demo_traces.py` hält aufgezeichnete
  Replays; Router liefert sie im identischen step/done-NDJSON zurück, wenn kein
  gültiger FOUNDRY_TOKEN da ist. UI zeigt „DEMO-REPLAY"-Badge.
- **Live/Demo-Umschalter** (`mode-toggle.js/.css`): in allen Topbars, persistiert
  in localStorage. **Default = LIVE** (Router fällt bei Token-Fehler auf Demo zurück).
- **Kiosk/Vollbild** (`kiosk.js/.css`): Button + `?kiosk=1`, blendet Chrome aus,
  füllt die Bühne rahmenlos. Esc / Exit verlässt.
- **Booth-Branding** (`brand.js/.css`): Foundry-Logo + „Contoso Expo 2027"
  Wasserzeichen unten rechts (bleibt im Kiosk sichtbar).
- **Robustheit**: /api/diff + /api/chat/stream geben saubere Token-Meldung
  statt nacktem 500; transient 5xx/429 werden 2–3× wiederholt; Antwort wird bei
  `done` voll gerendert + ins Bild gescrollt.

## Letzte Commits
- idun-playground `e8ffef` — feat(ui): booth branding watermark + clearer demo hint
- idun-playground `84b5989` — feat(ui): default LIVE mode + kiosk fullscreen booth mode
- idun-playground `2537469` — feat(expo): 8 Contoso demos + shared Live/Demo mode toggle
- idun-sdk `ec41ea2` — feat(pack): expand Contoso pack to 8 demos + update tests

## Bekannter Blocker
- `~/foundry_token.txt` ist abgelaufen (Datei vom 03.08). LIVE-Modus zeigt daher
  automatisch Demo-Replay. Für echte Live-Ergebnisse: `idun login` ausführen.

## Nächste optionalen Schritte
- Automatische Demo-Rotation im Kiosk-Modus.
- Blueprint-Repo `azure-agent-blueprint` evolvieren (siehe ROADMAP / Anfrage).
