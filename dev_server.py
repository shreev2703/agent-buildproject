"""
Local stand-in for Vercel (its Windows dev tooling is broken).
Serves index.html at "/" and routes everything else to api/agent.py's handler,
exactly as Vercel would. Run:  python dev_server.py  ->  http://localhost:3000
"""

from http.server import HTTPServer
from pathlib import Path

from api.agent import handler as AgentHandler


class DevHandler(AgentHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = Path("public/index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()           # /api/agent heartbeat


if __name__ == "__main__":
    print("dev server on http://localhost:3000  (Ctrl+C to stop)")
    HTTPServer(("localhost", 3000), DevHandler).serve_forever()
