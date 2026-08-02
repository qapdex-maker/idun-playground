# Idun Playground — minimal container image.
# Stdlib-only router (http.server) + idun-sdk. No Flask/FastAPI.
FROM python:3.12-slim

WORKDIR /app

# Install dependency first (better layer caching).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app.
COPY . .

# The router binds inside the container on 0.0.0.0; the FOUNDRY_TOKEN is
# injected at runtime as a secret (never baked into the image — see deploy.sh).
ENV BIND_HOST=0.0.0.0
EXPOSE 9001

# Expect FOUNDRY_TOKEN at runtime: `docker run -e FOUNDRY_TOKEN=...`
# Put a TLS-terminating reverse proxy (nginx/Caddy) in front — the router has
# no built-in auth beyond the Foundry token.
CMD ["python3", "router.py"]
