"""Naive inference server -- weight download baked into startup.

On startup this server downloads a "model weights" file from a hardcoded URL.
The download source, credentials, and download logic all live here.
Change the source and you change this file and rebuild the image.

Simulates a model inference endpoint. The "model" is a small text file.
"""
import http.server
import socketserver
import urllib.request
import os
import time

# The weights source is hardcoded here.
# On a real server this might be an S3 URL, a GCS path, or a HuggingFace repo.
# Changing it means editing this file and rebuilding the image.
WEIGHTS_URL = "https://raw.githubusercontent.com/arun-gupta/the-pain-first-way/main/examples/05-cold-start/after/weights.txt"
WEIGHTS_PATH = "/tmp/weights.txt"
PORT = 8080


def download_weights():
    print(f"[startup] Downloading weights from {WEIGHTS_URL} ...")
    start = time.time()
    urllib.request.urlretrieve(WEIGHTS_URL, WEIGHTS_PATH)
    elapsed = time.time() - start
    print(f"[startup] Weights downloaded in {elapsed:.2f}s -> {WEIGHTS_PATH}")


def load_weights():
    with open(WEIGHTS_PATH) as f:
        return f.read().strip()


class InferenceHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
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
    print(f"[startup] Model loaded. Weights preview: {model_weights[:60]}...")

    with socketserver.TCPServer(("", PORT), InferenceHandler) as httpd:
        httpd.model_weights = model_weights
        print(f"[ready] Inference server listening on port {PORT}")
        print(f"[ready]   GET /health  -> liveness check")
        print(f"[ready]   GET /predict -> simulated inference")
        httpd.serve_forever()
