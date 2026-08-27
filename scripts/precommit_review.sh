#!/usr/bin/env bash
# Pre-commit review hook (P2, IGNITE prep).
#
# Runs the self-built reviewer in DRY-RUN mode (no GitHub post, no labels).
# It only prints findings locally so you catch obvious issues before pushing.
# It NEVER blocks the commit (exit 0) — treat its output as advisory, like a
# spell-checker. To make it blocking, change the last line to `exit $rc`.
#
# Install as a hook:
#   cp scripts/precommit_review.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Requires idun-sdk installed with idun-multi on PATH and at least one LLM
# provider credential configured (idun-multi login). Without credentials the
# reviewer reports "no providers" and the hook still passes.

set -u
PR="${1:-local}"

echo "== idun-multi review (dry-run) =="
if command -v idun-multi >/dev/null 2>&1; then
  idun-multi review "$PR" 2>&1 || true
  rc=$?
else
  echo "idun-multi not on PATH — skipping review hook."
  rc=0
fi

# Advisory only: always allow the commit.
exit 0
