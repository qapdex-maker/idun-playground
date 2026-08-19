#!/usr/bin/env python3
"""Idun Matrix Bridge — minimal local server (IDEA β: PocketPal-Bridge).

Serves a mobile web UI (matrix_app.html) and a JSON API that runs the Idun SDK
`idun matrix` flow server-side (the SDK is Python, not browser-runnable).

Tenant-agnostic: the client supplies its OWN Foundry resource (endpoint + token)
via the /matrix request body — never hardcoded to QMFI.

Run:  python3 matrix_server.py --port 8000
Then open http://localhost:8000/matrix_app.html

Endpoints:
  GET  /                      -> index redirect
  GET  /matrix_app.html       -> the PWA
  GET  /matrix_demo.json      -> recorded demo (no account needed)
  POST /matrix                -> {docs:{name:text}, questions:[...], foundry:{endpoint,token,project,agent}}
                                 returns {questions, documents, cells:{q:{doc:cell}}}
"""
import json, os, tempfile, sys, base64, shutil
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# allow running from repo root where idun-sdk may be installed or sibling
sys.path.insert(0, os.path.expanduser("~/idun-sdk"))
try:
    from idun.matrix import build_matrix
    from idun.client import IdunClient
except Exception as e:  # pragma: no cover
    build_matrix = None
    print("WARNING: idun-sdk not importable:", e)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(302, b"", "text/plain")
            self.send_header("Location", "/matrix_app.html")
            self.end_headers()
            return
        if path == "/matrix_app.html":
            self._send_file("matrix_app.html", "text/html")
            return
        if path == "/matrix_demo.json":
            self._send_file("matrix_demo.json", "application/json")
            return
        self._send(404, json.dumps({"error": "not found"}))

    def _send_file(self, name, ctype):
        try:
            with open(os.path.join(os.path.dirname(__file__), name), "rb") as f:
                self._send(200, f.read(), ctype)
        except FileNotFoundError:
            self._send(404, json.dumps({"error": name + " missing"}))

    def do_POST(self):
        if urlparse(self.path).path != "/matrix":
            self._send(404, json.dumps({"error": "not found"}))
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            req = json.loads(raw)
        except Exception as e:
            self._send(400, json.dumps({"error": "bad json: " + str(e)}))
            return
        docs_raw = req.get("docs", {})
        # decode any base64-encoded uploads (browser sends pdf as base64)
        docs = {}
        tmp_files = []
        for name, content in docs_raw.items():
            if name.endswith("__b64"):
                continue
            if isinstance(content, str) and docs_raw.get(name + "__b64"):
                # write temp file with original extension
                ext = os.path.splitext(name)[1] or ".pdf"
                fd, path = tempfile.mkstemp(suffix=ext)
                with os.fdopen(fd, "wb") as f:
                    f.write(base64.b64decode(content))
                tmp_files.append(path)
                # extract text via ingest
                try:
                    from idun.ingest import extract_text
                    docs[name] = extract_text(path)
                except Exception as e:
                    docs[name] = "[extract failed: %s]" % e
            else:
                docs[name] = content
        questions = req.get("questions", [])
        foundry = req.get("foundry", {})
        if not build_matrix:
            self._send(500, json.dumps({"error": "idun-sdk not available on server"}))
            return
        if not docs or not questions:
            self._send(400, json.dumps({"error": "need docs and questions"}))
            return
        try:
            client = IdunClient(
                endpoint=foundry.get("endpoint"),
                token=foundry.get("token"),
                project=foundry.get("project"),
                agent=foundry.get("agent"),
            )
            cells = build_matrix(client, docs, questions)
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}))
            return
        finally:
            for tf in tmp_files:
                try: shutil.rmtree(os.path.dirname(tf), ignore_errors=True)
                except Exception: pass
        self._send(200, json.dumps({
            "questions": questions,
            "documents": list(docs.keys()),
            "cells": cells,
        }))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    print(f"Idun Matrix Bridge on http://localhost:{args.port}/matrix_app.html")
    HTTPServer(("0.0.0.0", args.port), Handler).serve_forever()
