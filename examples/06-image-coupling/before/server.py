"""Inference server that reads config and credentials from environment variables.

Reading from env vars is the right practice in Python -- no credentials in source code.
The problem is where those env vars come from. In the typical containerisation path,
they end up as ENV instructions in the Dockerfile, which bakes them into the image layer.
The image then carries them wherever it goes: registry, CI cache, every node that pulls it.
"""
import http.server
import socketserver
import shutil
import os
import sys
import time

WEIGHTS_SOURCE = os.environ.get("WEIGHTS_SOURCE", "./weights.txt")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

WEIGHTS_PATH = "/tmp/weights.txt"
PORT = 8080


def download_weights():
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print("[startup] ERROR: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set", file=sys.stderr)
        sys.exit(1)
    print(f"[startup] Connecting to {WEIGHTS_SOURCE}")
    print(f"[startup] Using key: {AWS_ACCESS_KEY_ID} (from env var -- but where did that env var come from?)")
    start = time.time()
    shutil.copy(WEIGHTS_SOURCE, WEIGHTS_PATH)
    elapsed = time.time() - start
    print(f"[startup] Weights staged in {elapsed:.3f}s -> {WEIGHTS_PATH}")


def load_weights():
    with open(WEIGHTS_PATH) as f:
        return f.read().strip()


class InferenceHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok\n")
        elif self.path == "/predict":
            self.send_response(200)
            self.end_headers()
            response = f"prediction using model: [{self.server.model_weights[:60]}...]\n"
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[request] {format % args}")


if __name__ == "__main__":
    download_weights()
    model_weights = load_weights()
    print(f"[startup] Model loaded. Preview: {model_weights[:60]}...")

    with socketserver.TCPServer(("", PORT), InferenceHandler) as httpd:
        httpd.model_weights = model_weights
        print(f"[ready] Inference server listening on port {PORT}")
        print(f"[ready]   GET /health  -> liveness check")
        print(f"[ready]   GET /predict -> simulated inference")
        httpd.serve_forever()
