# Self-built Review (P2, IGNITE prep)

idun-playground uses the **self-built PR reviewer** from idun-sdk
(`idun-multi review`) as a quality signal. CodeRabbit does NOT auto-review this
repo (<10 stars — see ARCHIVE.md), so this fills that gap with tooling we
control (Datenhoheit, kein Drittpartei-SaaS).

## Local (pre-commit, advisory)

```bash
cp scripts/precommit_review.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook runs `idun-multi review` in dry-run mode and **never blocks** the
commit (exit 0). It needs `idun-multi` on PATH + at least one LLM provider
credential (`idun-multi login`).

## CI (optional, token-gated)

`.github/workflows/review.yml` runs the reviewer on PRs **only if** the repo
secret `IDUN_REVIEW_TOKEN` is set. Without the secret the job is skipped, so a
PR never fails just because no token is configured. The review job is
`continue-on-error: true` — findings are advisory, not blocking.

To enable: add a repo secret `IDUN_REVIEW_TOKEN` (any provider key the
reviewer can use, e.g. an OpenAI key) and the next PR will get a self-built
review comment.

## Why self-built, not CodeRabbit

See `docs/code-review-options.md` in idun-sdk. Short version: data sovereignty
+ Termux-friendly + no third-party SaaS ingesting our diffs.
