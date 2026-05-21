"""Batching-aware inference server -- concurrent requests, Prometheus metrics.

Uses ThreadingMixIn so multiple requests run in parallel, up to MAX_CONCURRENT.
A semaphore enforces the concurrency limit. /metrics exposes in-flight count and
total requests so KEDA can scale on the right signal instead of CPU.
"""
import http.server
import socketserver
import threading
import time
import os

PORT = int(os.environ.get("PORT", 8080))
MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", 4))

_lock = threading.Lock()
_in_flight = 0
_total = 0
_semaphore = threading.Semaphore(MAX_CONCURRENT)


def _inc():
    global _in_flight, _total
    with _lock:
        _in_flight += 1
        _total += 1
        return _in_flight, _total


def _dec():
    global _in_flight
    with _lock:
        _in_flight -= 1
        return _in_flight


class InferenceHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        elif self.path == "/predict":
            _semaphore.acquire()
            try:
                in_flight, total = _inc()
                print(f"[batch] {in_flight}/{MAX_CONCURRENT} requests in flight (total={total})")
                start = time.time()
                time.sleep(0.5)
                elapsed = time.time() - start
                in_flight = _dec()
                print(f"[batch] {in_flight}/{MAX_CONCURRENT} requests in flight after completion")

                self.send_response(200)
                self.end_headers()
                response = f"prediction: total={total} elapsed={elapsed:.3f}s\n"
                self.wfile.write(response.encode())
            finally:
                _semaphore.release()

        elif self.path == "/metrics":
            with _lock:
                in_flight = _in_flight
                total = _total
            tps = in_flight * 150
            body = (
                f"# HELP inference_requests_in_flight Current concurrent inference requests\n"
                f"# TYPE inference_requests_in_flight gauge\n"
                f"inference_requests_in_flight {in_flight}\n"
                f"# HELP inference_requests_total Total inference requests served\n"
                f"# TYPE inference_requests_total counter\n"
                f"inference_requests_total {total}\n"
                f"# HELP inference_tokens_per_second Estimated tokens per second\n"
                f"# TYPE inference_tokens_per_second gauge\n"
                f"inference_tokens_per_second {tps}\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(body.encode())

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    print(f"[ready] Batching inference server listening on port {PORT}")
    print(f"[ready]   MAX_CONCURRENT={MAX_CONCURRENT} (set via env var)")
    print(f"[ready]   GET /health  -> liveness check")
    print(f"[ready]   GET /predict -> simulated inference (concurrent)")
    print(f"[ready]   GET /metrics -> Prometheus metrics")
    with ThreadingServer(("", PORT), InferenceHandler) as httpd:
        httpd.serve_forever()
