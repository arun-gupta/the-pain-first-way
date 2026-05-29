"""Support-assistant server -- the prompt lives in three places at once.

The system prompt that governs this assistant's behavior is:
  1. a DEFAULT_PROMPT constant baked into this file, and
  2. overridable by a SYSTEM_PROMPT environment variable (loaded from .env on the box), and
  3. (per the runbook) sometimes pasted in from a Notion doc by whoever last touched it.

Whichever one wins at runtime is whatever happens to be set. There is no version,
no owner, and no history. When a customer reports a regression "two weeks ago,"
nobody can answer: what prompt was actually running that day?
"""
import http.server
import socketserver
import os
import sys

# Source #1: the prompt in code. Looks authoritative. Often isn't what's running.
DEFAULT_PROMPT = "You are a helpful support assistant. End every answer with a ticket link."

PORT = 8080


def effective_prompt():
    # Source #2: a .env override silently wins over the constant above.
    # Nobody committed this. Nobody can see it without shelling into the box.
    return os.environ.get("SYSTEM_PROMPT", DEFAULT_PROMPT)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok\n")
        elif self.path.startswith("/predict"):
            prompt = effective_prompt()
            self.send_response(200)
            self.end_headers()
            # The answer depends entirely on a prompt we cannot pin to a version.
            self.wfile.write(f'answering with prompt: "{prompt}"\n'.encode())
        else:
            # There is no /version endpoint. There is nothing reliable to return.
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[request] {format % args}")


class Server(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    prompt = effective_prompt()
    source = "SYSTEM_PROMPT env var (.env)" if "SYSTEM_PROMPT" in os.environ else "DEFAULT_PROMPT constant"
    print(f"[startup] Effective prompt came from: {source}")
    print(f"[startup] Prompt text: {prompt}")
    print(f"[startup] Version: unknown. Owner: unknown. History: none.", file=sys.stderr)

    with Server(("", PORT), Handler) as httpd:
        print(f"[ready] Support assistant listening on port {PORT}")
        print(f"[ready]   GET /predict -> simulated answer")
        print(f"[ready]   GET /version -> 404 (there is no such thing here)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[shutdown] stopped.")
