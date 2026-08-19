# Idun — Archive (Completed Work)

Snapshot of everything finished across the Idun project
(idun-sdk, idun-playground, qapdex-maker.github.io).
Generated: 2026-08-19.

## Releases
- **idun-sdk 1.0.17** — pushed to GitHub `main` (commit ba78c14).
  - Version bump 1.0.16 -> 1.0.17 (static version in pyproject.toml).
  - README + CHANGELOG updated (version badge, CI description corrected:
    Termux/aarch64 job removed, ruff pinned to 0.15.10).
  - `pyproject.toml` PEP 517 build-system (merged via PR #8).
  - Wheel built + METADATA verified (Version: 1.0.17).
  - **PyPI upload: LIVE** — https://pypi.org/project/idun-sdk/1.0.17/ (uploaded with
    `pypi-`-prefixed token; all prior 403s were missing the `pypi-` prefix).
- **idun-sdk 1.0.16** — PyPI live (was 1.0.15 before). Added --async CLI fix,
  token auto-rotation + prompt-packs docs, CI green (termux job removed).

## Tenant-agnostic cleanup (idun-playground)
- Removed hardcoded QMFI values: deleted legacy `server.py` (had hardcoded
  qmfi-research-project-resource URL), neutralized `auth-guide.html`
  (tenant GUID -> <your-tenant-guid>), `api-reference.html` (QMFI URL ->
  <your-resource>), `playground.html` (resource/project -> placeholders),
  `docs/playground.md` (author QMFI-Research -> Idun SDK),
  `DEMOS_INVENTORY.md` (tenant admin roles stripped).
- PR #6 merged. Verified no tenant-leak remains (except ROADMAP context + test fixtures).

## Demo localization
- `traces.json` fully translated EN (was DE/EN mixed). Verified on GitHub Pages.

## Landing page (qapdex-maker.github.io)
- Reverted to `4bf945b` (IDUN-40 device frame, hard power-on flash, mixed
  font hierarchy) per user preference. Boot/cartridge/soft-flash experiments
  removed.
- Live: https://qapdex-maker.github.io/

## CodeRabbit review
- Both repos reviewed (own static review). PR #6 (playground) + PR #8 (sdk)
  opened; CodeRabbit triggered but does NOT auto-review (<10 repo stars).
  Own review found + fixed the only real finding (QMFI hardcode in server.py).

## Still open / paused
- **PR #4249 (Connector):** PAUSED — 70 EUR Azure RBAC `agents/write` not paid.
- **PyPI 1.0.17 upload:** blocked on valid token (see above).
- **365 calendar:** waiting on Exchange license.
