"""Decoupled inference server -- serving code only.

Reads weights from /model/weights.txt, which is a shared volume populated
by the init container before this process starts. No source URL, no credentials,
no download logic. This image never changes when the weights source changes.
"""
import http.server
import socketserver
import sys
import os

WEIGHTS_PATH = "/model/weights.txt"
PORT = 8080


def load_weights():
    if not os.path.exists(WEIGHTS_PATH):
        print(f"[startup] ERROR: weights not found at {WEIGHTS_PATH}.", file=sys.stderr)
        print(f"[startup] The init container should have staged them before this server started.", file=sys.stderr)
        sys.exit(1)
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
    model_weights = load_weights()
    print(f"[startup] Weights loaded from {WEIGHTS_PATH}. Preview: {model_weights[:60]}...")
    print(f"[startup] (No source URL or credentials in this image.)")

    with socketserver.TCPServer(("", PORT), InferenceHandler) as httpd:
        httpd.model_weights = model_weights
        print(f"[ready] Inference server listening on port {PORT}")
        print(f"[ready]   GET /health  -> liveness check")
        print(f"[ready]   GET /predict -> simulated inference")
        httpd.serve_forever()
