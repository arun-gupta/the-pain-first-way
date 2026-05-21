"""Sequential inference server -- one request at a time, GPU idle between them.

Each request blocks the server for 0.5s (simulated GPU work). While one request
is processing, every other request waits. The GPU idles between requests.
This is the pattern that produces 30% utilization at p50 load.
"""
import http.server
import socketserver
import time
import os

PORT = int(os.environ.get("PORT", 8080))

request_count = 0


class InferenceHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global request_count

        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        elif self.path == "/predict":
            request_count += 1
            n = request_count

            print(f"[processing] request {n}")
            start = time.time()
            time.sleep(0.5)
            elapsed = time.time() - start

            self.send_response(200)
            self.end_headers()
            response = f"prediction: request={n} elapsed={elapsed:.3f}s\n"
            self.wfile.write(response.encode())

            print(f"[idle] waiting for next request")

            if n % 5 == 0:
                print(f"[utilization] GPU: ~30% (idle between requests)")

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), InferenceHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"[ready] Sequential inference server listening on port {PORT}")
        print(f"[ready]   GET /health  -> liveness check")
        print(f"[ready]   GET /predict -> simulated inference (sequential)")
        httpd.serve_forever()
