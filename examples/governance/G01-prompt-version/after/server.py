"""Support-assistant server -- the prompt is versioned config, mounted at runtime.

There is exactly one source of truth: the files under /etc/prompt, mounted from a
ConfigMap that lives in git. The server reads them and can report, at any moment,
which prompt version it is serving and the exact text of that prompt.

No constant to drift. No .env override. What's running is what's in the ConfigMap,
which is what's in git.
"""
import http.server
import socketserver
import hashlib
import sys
import os

PROMPT_PATH = "/etc/prompt/system_prompt"
VERSION_PATH = "/etc/prompt/version"
PORT = 8080


def read_file(path, label):
    if not os.path.exists(path):
        print(f"[startup] ERROR: {label} not found at {path}.", file=sys.stderr)
        print(f"[startup] The ConfigMap should be mounted before this server starts.", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return f.read().strip()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok\n")
        elif self.path == "/version":
            # The running server reports exactly what it is serving, truthfully.
            s = self.server
            self.send_response(200)
            self.end_headers()
            body = (
                f"prompt_version: {s.version}\n"
                f"prompt_sha256:  {s.prompt_hash}\n"
                f"prompt_text:    {s.prompt}\n"
            )
            self.wfile.write(body.encode())
        elif self.path.startswith("/predict"):
            s = self.server
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                f'[{s.version}] answering with prompt: "{s.prompt}"\n'.encode()
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[request] {format % args}")


class Server(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    prompt = read_file(PROMPT_PATH, "system prompt")
    version = read_file(VERSION_PATH, "prompt version")
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    print(f"[startup] Prompt version: {version}")
    print(f"[startup] Prompt sha256:  {prompt_hash}")
    print(f"[startup] Prompt text:    {prompt}")
    print(f"[startup] Source: ConfigMap mounted at /etc/prompt (versioned in git).")

    with Server(("", PORT), Handler) as httpd:
        httpd.prompt = prompt
        httpd.version = version
        httpd.prompt_hash = prompt_hash
        print(f"[ready] Support assistant listening on port {PORT}")
        print(f"[ready]   GET /version -> the prompt version this pod is serving")
        print(f"[ready]   GET /predict -> simulated answer, stamped with the version")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[shutdown] stopped.")
