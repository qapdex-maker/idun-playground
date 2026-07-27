#!/usr/bin/env python3
"""Idun router — stdlib HTTP server for the playground UI.

Serves the static playground (playground.html, diff.html, assets/) and
exposes the agent endpoints the UI calls:
  POST /api/chat          -> { choices:[{message:{content}}], steps:[...] }
  POST /api/chat/stream   -> SSE-style newline-delimited JSON events
                             (step / token / done / error)
  POST /api/diff          -> { trace_a, trace_b, n_steps_a, n_steps_b,
                               shared_queries, only_a, only_b, same_answer }

Stdlib-only (http.server + the idun SDK). No flask/fastapi. Runs on :9001.
Foundry creds stay server-side (FOUNDRY_TOKEN / idun login), the browser
never sees them.

NOTE: the Foundry Responses shape we use returns a complete output[] array,
not a token stream. /api/chat/stream therefore emits one 'step' event per
parsed step and a final 'done' event with the full answer — honest progressive
rendering, not fake per-token streaming.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from functools import partial

import idun
from idun import IdunClient, load_token, diff_traces

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 9001


def _client():
    tok = load_token() or os.environ.get("FOUNDRY_TOKEN")
    if not tok:
        raise RuntimeError("No FOUNDRY_TOKEN. Run `idun login` or export FOUNDRY_TOKEN.")
    return IdunClient(token=tok)


def _step_to_dict(s):
    return {"kind": s.kind, "text": s.text, "tool": s.tool,
            "query": s.query, "status": s.status, "id": s.id}


def _result_to_payload(res):
    return {
        "choices": [{"message": {"role": "assistant", "content": res.text}}],
        "steps": [_step_to_dict(s) for s in res.steps],
        "model": res.model,
    }


def _run_complete(prompt, max_tokens=4096):
    return _client().complete(prompt, max_output_tokens=max_tokens)


class Handler(BaseHTTPRequestHandler):
    # Security headers applied to EVERY response (static, errors, API) via the
    # BaseHTTPRequestHandler.end_headers() hook — not just CORS paths.
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    # Reject requests whose Host header does not match our listener, to
    # prevent DNS-rebinding / Host-spoofing against the local agent endpoint.
    # Exact authority match only — substrings (localhost.attacker.example) bypass
    # the check, so we compare parsed host:port, not substrings.
    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0].strip().lower()
        allowed = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "[::]"}
        return host in allowed

    def _body(self, max_bytes=1 << 20):  # 1 MiB cap, anti-DoS
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        if length > max_bytes:
            raise ValueError("payload too large")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _static(self, path):
        # map "/" -> playground.html
        rel = path.lstrip("/")
        if rel == "":
            rel = "playground.html"
        full = os.path.join(HERE, rel)
        # prevent path traversal
        if not os.path.abspath(full).startswith(os.path.abspath(HERE)):
            self.send_error(403)
            return
        if not os.path.isfile(full):
            self.send_error(404)
            return
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".svg": "image/svg+xml",
            ".js": "application/javascript",
            ".css": "text/css",
            ".json": "application/json",
        }.get(os.path.splitext(full)[1], "application/octet-stream")
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if not self._host_ok():
            self.send_error(403, "Host not allowed")
            return
        self._static(urlparse(self.path).path)

    def do_POST(self):
        if not self._host_ok():
            self.send_error(403, "Host not allowed")
            return
        route = urlparse(self.path).path
        try:
            if route == "/api/chat":
                body = self._body()
                prompt = (body.get("messages") or [{}])[-1].get("content", "")
                max_tokens = body.get("max_tokens", 4096)
                res = _run_complete(prompt, max_tokens)
                self._json(_result_to_payload(res))
            elif route == "/api/chat/stream":
                body = self._body()
                prompt = (body.get("messages") or [{}])[-1].get("content", "")
                max_tokens = body.get("max_tokens", 4096)
                res = _run_complete(prompt, max_tokens)
                # SSE-style stream: steps first, then done with full answer
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
                self._cors()
                self.end_headers()
                for s in res.steps:
                    ev = json.dumps({"type": "step", "step": _step_to_dict(s)},
                                    ensure_ascii=False) + "\n"
                    self.wfile.write(ev.encode("utf-8"))
                done = json.dumps({"type": "done", "answer": res.text,
                                   "steps": [_step_to_dict(s) for s in res.steps]},
                                  ensure_ascii=False) + "\n"
                self.wfile.write(done.encode("utf-8"))
            elif route == "/api/diff":
                body = self._body()
                pa = body.get("prompt_a", "")
                pb = body.get("prompt_b", "")
                max_tokens = body.get("max_tokens", 4096)
                ra = _run_complete(pa, max_tokens)
                rb = _run_complete(pb, max_tokens)
                d = diff_traces(ra, rb)
                d["trace_a"] = [_step_to_dict(s) for s in ra.steps]
                d["trace_b"] = [_step_to_dict(s) for s in rb.steps]
                self._json(d)
            else:
                self.send_error(404)
        except RuntimeError as e:
            try:
                self._json({"error": str(e)}, code=500)
            except BrokenPipeError:
                pass  # client disconnected before we could respond
        except BrokenPipeError:
            pass  # client closed the connection (e.g. request timeout)
        except Exception as e:  # noqa: BLE001 - surface as JSON, not HTML traceback
            try:
                self._json({"error": f"{type(e).__name__}: {e}"}, code=500)
            except BrokenPipeError:
                pass

    def log_message(self, fmt, *args):
        # quieter than default
        pass


def main():
    # Bind to loopback only — this is a local agent router, not a public server.
    # Avoids exposing the Foundry-backed endpoint on all interfaces (Ruff S104).
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Idun router on http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
