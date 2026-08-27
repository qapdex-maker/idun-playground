# FAHRPLAN — idun-playground auf SDK-Stand 1.0.34 (bis IGNITE, November)

Stand: 2026-08-27. Ziel: playground konsistent mit idun-sdk 1.0.34 (PyPI +
GitHub live verifiziert) bringen und die IGNITE-2026-Demo (17.–20. Nov,
San Francisco) vorbereiten.

Quelle der Fakten: echte Reads (router.py, setup.py, requirements.txt,
index.html, ignite.html, idun-sdk CHANGELOG 1.0.33/1.0.34).

## Aktueller Stand (vor diesem Fahrplan)

- playground main = `884a644` nach Merge (lokal 9f6d960 + Remote Ignite-Badge).
- playground referenzierte `idun-sdk>=0.1.21` (Pin viel zu alt) und zeigte
  auf der Seite `idun-sdk v1.0.32` (Remote hatte "Bring pages to 1.0.32"
  gemacht). SDK ist aber bereits bei **1.0.34**.
- playground nutzt nur den **Client/Foundry-Teil** des SDK
  (`from idun import IdunClient, load_token, diff_traces, list_packs,
  load_pack, get_prompt`) — nicht `idun_multi` (verify/review/race).

## ERLEDIGT (27.08, lokal committet — Push auf Freigabe)

- [x] Merge lokale + Remote-Divergenz (Fast-Forward, keine Konflikte:
      nur index.html / ignite.html / docs/playground.md betroffen).
- [x] Version-Parität: index.html `v1.0.32` -> `v1.0.34`.
- [x] ignite.html `v1.0.32` -> `v1.0.34` (2 Stellen).
- [x] Dependency-Pin `setup.py` + `requirements.txt`: `>=0.1.21` -> `>=1.0.34`.
- [x] Keine veralteten Version-Refs mehr außer ARCHIVE.md (historisch korrekt).

## Offene Items (bis IGNITE)

### Item P1 — SDK-Feature-Sichtbarkeit auf der playground-Matrix
Status: Vorbereitung.
- Die SDK-Matrix (`idun.providers.support_matrix()`) hat jetzt eine
  **Live-Spalte** (Declared ✓ + Live ✓/✗/?). Die playground `matrix.html`
  / `matrix_app.html` zeigen aber nur die statische Foundry-Sicht.
- [ ] `router.py` um einen Endpunkt `/api/sdk-matrix` erweitern, der
      `idun.providers.support_matrix_text()` rendert (ehrlich: 17 Provider,
      welche live getestet). Demo-mode: gecachte Ausgabe, kein Live-Call.
- [ ] `matrix.html` den neuen Endpunkt pollen und die Live-Spalte zeigen.
- Nutzen: Booth-Besucher sehen auf einen Blick, welche 17 Provider live sind.

### Item P2 — Self-built Review im playground-CI nutzen
Status: Vorbereitung (SDK 1.0.34 liefert `idun-multi review`).
- [ ] `idun-multi review` gegen playground-PRs einsetzen (statt/ergänzend zu
      CodeRabbit, das bei <10 Stars nicht auto-reviewt — siehe ARCHIVE.md).
- [ ] Einen Pre-Commit-Hook oder CI-Step `idun-multi review --dry-run`
      dokumentieren (ohne Token im CI: nur dry-run, keine Posts).

### Item P3 — Ignite-2026 Demo-Robustheit
Status: laufend (ignite.html + Badge schon im Remote).
- [x] Ignite-Badge + ignite.html vorhanden.
- [ ] `router.py` Demo-Mode auf allen Seiten erzwingen (kein Live-Token an
      Booth nötig) — bereits großteils da (`_demo_trace`), aber für
      `matrix.html` + `expo.html` + `trace-viz-demo.html` verifizieren.
- [ ] Offline-Sicherheit aller Demos testen (kein KeyError bei fehlendem
      `IDUN_TOKEN`): ein `scripts/smoke_demos.py` schreiben, das alle Seiten
      gegen `localhost:<port>` GET-tet (Parität zu SDK `scripts/race_smoke.py`).

### Item P4 — Version-Sync automatisieren
Status: Vorbereitung.
- [ ] Ein `scripts/sync_sdk_version.py`, das `idun.__version__` aus dem
      installierten SDK liest und index.html/ignite.html/setup.py/
      requirements.txt auf diese Version abgleicht (verhindert künftig
      driftende Pins wie `>=0.1.21` vs `v1.0.34`).
- [ ] Im README dokumentieren: nach jedem SDK-Release `python scripts/
      sync_sdk_version.py` + Commit + Push.

## Harte Regeln (wie SDK)
- Push GitHub + PyPI NUR auf Auftrag ("Bescheid"/"übertragen").
- GitHub = Wahrheit. Lokale Tests/pyflakes grün vor Push.
- Kein Token/Wert ins Repo / in Commits / in Chat.

## Reihenfolge (bis IGNITE)
1. P1 (SDK-Matrix sichtbar) — Demo-Wert am Booth.
2. P4 (Version-Sync) — verhindert künftigen Drift.
3. P3 (Demo-Robustheit) — Booth muss offline laufen.
4. P2 (Review-CI) — Qualität, nicht booth-kritisch.
