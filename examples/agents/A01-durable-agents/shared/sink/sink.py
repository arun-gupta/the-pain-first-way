"""A tiny idempotent side-effect sink, standard library only.

It stands in for the external systems an agent touches (a payment API, an
email service). POST /effect records an effect unless its idempotency key has
been seen before, in which case it is ignored. GET /effects reports the
totals, so the demo can SHOW exactly-once: charges stay at 1 when the agent
resumes correctly, and climb to 2 when a crash causes a duplicate.

State is in memory. We never crash the sink; only the agent. Restart the sink
deployment to reset between runs.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

effects = []   # list of {"type": ..., "key": ...}
seen = set()   # idempotency keys already applied


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, body):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        if self.path != "/effect":
            return self._reply(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        key = data.get("key")
        if key in seen:
            return self._reply(200, {"status": "duplicate-ignored", "key": key})
        seen.add(key)
        effects.append({"type": data.get("type"), "key": key})
        return self._reply(201, {"status": "recorded", "key": key})

    def do_GET(self):
        if self.path.startswith("/effects"):
            charges = sum(1 for e in effects if e["type"] == "charge")
            return self._reply(200, {"total": len(effects), "charges": charges, "effects": effects})
        return self._reply(404, {"error": "not found"})

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"[sink] listening on :{port}", flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
