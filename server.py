#!/usr/bin/env python3
"""Local proxy + multi-backend LLM router for the Hermes WebUI workspace.

Serves /home/www statically and routes POST /api/chat to one of three
backends, selected by the `model` field in the request body:

  model prefix     backend
  ------------     ------------------------------------------------
  foundry:*  or   Azure AI Foundry Agent Service (OpenAI Responses
  NatureLM*        protocol), e.g. foundry:NatureLM-Idun-5-MoE
  aoai:*      or   Azure OpenAI (api-key from env)
  gpt-4o / ...
  cloudflare:* or  Cloudflare AI Gateway (default)
  (none)

No secrets are hardcoded: tokens come from env vars
(FOUNDRY_TOKEN, AZURE_OPENAI_API_KEY) or are passed through via headers.
"""
import os
import sys
import json
from http.server import HTTPServer, ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
CLOUDFLARE_URL = "https://gateway.ai.cloudflare.com/v1/1d43130db88e4898f15cdb909dc74e8c/cfut-gateway/compat/chat/completions"
FOUNDRY_BASE = "https://qmfi-research-project-resource.services.ai.azure.com"
FOUNDRY_PROJECT = "qmfi-research-project"
FOUNDRY_API_VERSION = "2025-05-15-preview"
# Backend request timeout (seconds). Foundry agents can take minutes on complex
# prompts, so this is generous and overridable via env (FOUNDRY_TIMEOUT).
REQUEST_TIMEOUT = int(os.environ.get("FOUNDRY_TIMEOUT", "600"))
AZURE_OPENAI_URL = "https://qmfi-research-project-resource.openai.azure.com/openai/v1/chat/completions"


def _route(model: str) -> str:
    m = (model or "").lower()
    if m.startswith("foundry:") or m.startswith("naturelm"):
        return "foundry"
    if m.startswith("aoai:") or m in ("gpt-4o", "gpt-4o-mini", "gpt-35-turbo"):
        return "aoai"
    if m.startswith("cfut:") or m.startswith("dynamic/"):
        return "cloudflare"
    return "cloudflare"


def _forward_to_foundry(payload: dict, token: str) -> bytes:
    # model "foundry:<agentId>" -> agent_id; bare "foundry" -> default agent
    model = payload.get("model", "")
    agent_id = model.split(":", 1)[1] if ":" in model else "NatureLM-Idun-5-MoE"
    url = (
        f"{FOUNDRY_BASE}/api/projects/{FOUNDRY_PROJECT}/agents/{agent_id}"
        f"/endpoint/protocols/openai/responses?api-version={FOUNDRY_API_VERSION}"
    )
    # Build the OpenAI "responses" protocol shape the agent expects:
    #   {"model": "model-router", "input": "<prompt string>", "max_output_tokens": N}
    # model MUST be "model-router" (not the agent name) when the agent is in the URL.
    messages = payload.get("messages", [])
    prompt_text = ""
    for m in messages:
        if isinstance(m, dict) and m.get("content"):
            prompt_text += m["content"] + "\n"
    prompt_text = prompt_text.strip()
    fpayload = {
        "model": "model-router",
        "input": prompt_text,
        # High default so Idun's full answer is returned (not truncated at 256).
        # Overridable per-request via max_output_tokens.
        "max_output_tokens": payload.get("max_output_tokens", 4096),
    }
    req = Request(
        url,
        data=json.dumps(fpayload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        data = json.loads(resp.read())
    text = ""
    steps = []  # normalized agent trajectory: {kind, ...}
    for o in data.get("output", []):
        otype = o.get("type")
        if otype == "message" and o.get("role") == "assistant":
            t = "".join(c.get("text", "") for c in o.get("content", []) if c.get("type") == "output_text")
            if t:
                text += t + "\n\n"
                steps.append({"kind": "reasoning", "text": t})
        elif otype == "web_search_call":
            action = o.get("action") or {}
            q = action.get("query") or (action.get("queries") or [""])[0] if action.get("queries") else action.get("query") or ""
            steps.append({
                "kind": "tool",
                "tool": "web_search",
                "query": q,
                "status": o.get("status", "unknown"),
                "id": o.get("id"),
            })
        elif otype == "message":
            # user/other messages: keep text if any
            t = "".join(c.get("text", "") for c in o.get("content", []) if c.get("type") == "output_text")
            if t:
                text += t + "\n\n"
                steps.append({"kind": "message", "text": t})
        # other item types (function_call_output etc.) -> ignore for now
    # shape back into OpenAI-compatible chat completion for the WebUI,
    # plus a 'steps' array carrying the agent's tool-use trajectory.
    out = {
        "choices": [{"message": {"role": "assistant", "content": text.strip()}, "finish_reason": "stop"}],
        "object": "chat.completion",
        "model": data.get("model", agent_id),
        "steps": steps,
    }
    return json.dumps(out).encode("utf-8")


def _forward_to_aoai(payload: dict, api_key: str) -> bytes:
    req = Request(
        AZURE_OPENAI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read()


def _forward_to_cloudflare(body: bytes, token: str, model_override: str | None = None) -> bytes:
    if model_override:
        try:
            p = json.loads(body)
            p["model"] = model_override
            body = json.dumps(p).encode("utf-8")
        except json.JSONDecodeError:
            pass
    req = Request(
        CLOUDFLARE_URL,
        data=body,
        headers={"cf-aig-authorization": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read()


class ProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path == "/api/ps":
            try:
                import sys as _sys
                _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "htop"))
                import htop as _htop
                procs = _htop.get_processes()[:50]
                body = json.dumps(procs).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return
        # everything else -> static file (SimpleHTTPRequestHandler default)
        return super().do_GET()

    def _send(self, code, body: bytes, extra_headers: dict = None):
        """Write a response, silently ignoring client-aborted connections
        (BrokenPipeError / ConnectionResetError) so they don't spam the log."""
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            if extra_headers:
                for k, v in extra_headers.items():
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = b""
        try:
            body = self.rfile.read(length) if length > 0 else b""
        except Exception as e:
            self._send(400, json.dumps({"error": "failed to read request body", "detail": str(e)}).encode("utf-8"))
            return
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send(400, json.dumps({"error": "invalid JSON"}).encode("utf-8"))
            return

        token = self.headers.get("cf-aig-authorization", "")
        backend = _route(payload.get("model", ""))

        try:
            if backend == "foundry":
                tok = os.environ.get("FOUNDRY_TOKEN") or token
                if not tok:
                    raise RuntimeError("FOUNDRY_TOKEN not set for foundry backend")
                out = _forward_to_foundry(payload, tok)
            elif backend == "aoai":
                key = os.environ.get("AZURE_OPENAI_API_KEY") or self.headers.get("x-aoai-key", "")
                if not key:
                    raise RuntimeError("AZURE_OPENAI_API_KEY not set for aoai backend")
                out = _forward_to_aoai(payload, key)
            else:
                if not token:
                    raise RuntimeError("cf-aig-authorization header required for cloudflare")
                override = "dynamic/Idun-Instruct-VL-BitNet" if (payload.get("model","").lower().startswith("cfut:")) else None
                out = _forward_to_cloudflare(body, token, override)
            self._send(200, out, extra_headers={"X-Backend": backend})
        except HTTPError as e:
            raw = b""
            try:
                raw = e.read() or b""
            except Exception:
                raw = b""
            # Foundry frequently returns an empty body on 401/403; turn that into
            # a structured JSON error so the playground can display it instead of
            # an opaque empty 403.
            if not raw.strip():
                detail = "upstream returned no body"
                if e.code in (401, 403):
                    detail = "upstream auth rejected (token expired or invalid)"
                raw = json.dumps({
                    "error": detail,
                    "status": e.code,
                    "backend": backend,
                    "hint": "rotate FOUNDRY_TOKEN via device_code_login.py" if e.code in (401, 403) else None,
                }).encode("utf-8")
            # Flatten upstream error bodies so the WebUI gets a readable
            # "error" string, not a nested object that renders as [object Object].
            try:
                upstream = json.loads(raw.decode("utf-8")) if raw.strip() else {}
            except Exception:
                upstream = {}
            if isinstance(upstream, dict) and "error" in upstream:
                ev = upstream["error"]
                if isinstance(ev, dict):
                    msg = ev.get("message") or ev.get("code") or ev.get("type") or json.dumps(ev)
                else:
                    msg = str(ev)
                raw = json.dumps({
                    "error": msg,
                    "status": e.code,
                    "backend": backend,
                    "type": (upstream.get("error") or {}).get("type") if isinstance(upstream.get("error"), dict) else None,
                }).encode("utf-8")
            self._send(e.code, raw)
        except Exception as e:
            self._send(502, json.dumps({"error": str(e), "backend": backend}).encode("utf-8"))

    def log_message(self, format, *args):
        sys.stdout.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))
        sys.stdout.flush()


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("ROUTER_PORT", "9001"))), ProxyHandler)
    print("Serving on http://127.0.0.1:9001/ (Ctrl+C to stop)")
    print("Router: foundry:* / NatureLM* -> Foundry | aoai:* / gpt-4o -> Azure OpenAI | else -> Cloudflare")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
