#!/usr/bin/env bash
#
# deploy.sh — build + run the Idun Playground container locally.
#
# The Foundry token is passed at runtime as a secret (docker -e), NEVER baked
# into the image. Generate a fresh token first:
#     idun login          # writes ~/foundry_token.txt
# then run:
#     ./deploy.sh
#
# The container binds on 0.0.0.0:9001 *inside* the container. For real hosting
# put a TLS reverse proxy (nginx/Caddy) in front and do NOT publish 9001 to
# the public internet directly — the router has no auth layer of its own.
set -euo pipefail

IMAGE="idun-playground:local"
CONTAINER="idun-playground"
TOKEN_FILE="${FOUNDRY_TOKEN_FILE:-$HOME/foundry_token.txt}"

if [[ ! -f "$TOKEN_FILE" ]]; then
  echo "ERROR: no token at $TOKEN_FILE" >&2
  echo "Run 'idun login' first (writes the token file), then re-run deploy.sh." >&2
  exit 1
fi

TOKEN="$(python3 - "$TOKEN_FILE" <<'PY'
import json, sys
try:
    print(json.load(open(sys.argv[1])).get("access_token", ""))
except Exception as e:
    print("", end="")
PY
)"

if [[ -z "$TOKEN" ]]; then
  echo "ERROR: token file present but no access_token inside (login expired?)" >&2
  exit 1
fi

echo ">> Building $IMAGE ..."
docker build -t "$IMAGE" .

echo ">> (Re)starting container $CONTAINER on :9001 ..."
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" -p 127.0.0.1:9001:9001 \
  -e FOUNDRY_TOKEN="$TOKEN" \
  -e BIND_HOST=0.0.0.0 \
  "$IMAGE"

echo ">> Playground up at http://localhost:9001/playground.html"
echo ">> (Published on loopback only; front with a reverse proxy for remote access.)"
