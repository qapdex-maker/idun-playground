# IDEA α — "Idun Matrix" (Doc × Question Pivot)

Concept note for the Idun product direction. Status: concept, not yet built.
Last sync: 2026-08-19.

## The core idea
A user loads **N documents** (contracts, reports, specs, PDF extracts) and a list
of **M questions**. Idun answers every (document, question) pair and returns an
**N × M matrix** — one cell per pairing — where each cell carries:
- the answer (short, extracted)
- the source citation (which sentence/section it came from)
- a status flag: GREEN = answer found, RED = contradiction/wrong, GRAY = no info

This is the "revolutionary" part vs. a normal chatbot: not ONE answer, but a
**pivot table over your whole document set**, filterable like a spreadsheet.

## Why Idun fits (no rebuild needed)
- `IdunClient.complete()` already does tool-calls + reasoning + citations.
- The retrieval step is a thin layer we add: chunk the doc, embed/keyword-search,
  feed top chunks as context to `complete()`. (SDK has no native retrieval yet —
  see Gap below.)
- Tenant-agnostic `.default` config → the Matrix app configures its OWN Foundry
  resource, exactly like the playground demo principle ("open for non-QMFI users").
- Demo mode: ship recorded (doc, question) → cell traces so the UI works with no
  account, same as `traces.json` today.

## Three product slices (ranked)
1. **α-core — Pivot Matrix**: N docs × M questions → N×M grid, each cell cited.
   Lowest effort, highest "wow". THIS is IDEA α.
2. **β — PocketPal-Idun Bridge**: a mobile PWA that runs a small local model for
   quick questions and delegates complex matrix jobs to Idun via the SDK.
3. **γ — Clause Drift**: compare Doc A vs a standard / Doc B, flag deviations as
   a matrix. **BUILT** in SDK 1.0.21 (`idun.diff_docs` / `idun matrix diff-docs`).

## UI direction (neon, consistent with landing page + playground)
- Reuse the IDUN-40 outrun look: sun/grid/stars/CRT, plastic cartridge.
- The matrix itself = a grid of glowing cells. Color code:
  - GREEN cell  → answer found + cited
  - RED cell    → contradiction / answer conflicts with another doc
  - GRAY cell   → no information in that document
- Hover/click a cell → side panel shows the full answer + source snippet
  (reuses the TraceViz row styling: reasoning=purple, tool=cyan, query=orange).

## Technical shape (MVP)
- Frontend: static HTML/JS PWA (no app store), neon-styled like playground.
- Doc ingest: paste text or upload .txt/.md; split into chunks (~1500 chars).
- Question list: one per line in a textarea.
- Engine: for each (doc, question): call Idun `complete()` with a retrieval prompt
  that says "answer from the provided context only; cite the source; if absent
  say NO INFO". Parse the cell from the response.
- Demo data: `matrix_demo.json` (recorded cells) so it renders without a token.

## Gaps to close before real build
- [ ] Retrieval helper in idun-sdk (chunk + search) — or a small `idun/retrieve.py`.
- [ ] Cell parser (extract answer + citation + status from `complete()` output).
- [ ] Concurrency: N×M calls can be many — batch / rate-limit (respect Foundry RPM).
- [ ] PDF ingest (extract text) — start with .txt/.md, add PDF later.
- [ ] Tenant config UI in the app (reuse `.default` template).

## Out of scope (for now)
- β local-model execution, γ drift comparison, fine-tuning, multi-tenant hosting.

## Next step
Build `matrix.html` (neon MVP) that renders `matrix_demo.json` as the glowing
N×M grid, then wire the real SDK call behind a "Run" button (tenant-agnostic).
