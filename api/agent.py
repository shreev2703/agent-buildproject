"""
Serverless entry point. Vercel maps this file to the URL  /api/agent

POST /api/agent   body: {"agent": "feedback" | "tutor", "input": "..."}
                  reply: {"agent": "...", "response": "..."}
GET  /api/agent   reply: a small "alive" message (handy for checking deploys)

Stateless on purpose: a new agent object is built for every request, so
there is no memory between calls. (Memory would have to live in a DB.)
"""

import json
from http.server import BaseHTTPRequestHandler

from agents.feedback_agent import FeedbackAgent
from agents.tutor_agent import TutorAgent

AGENTS = {
    "feedback": FeedbackAgent,
    "tutor": TutorAgent,
}


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, {"ok": True, "agents": list(AGENTS)})

    def do_POST(self):
        # --- read the JSON body
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "body must be JSON"})

        agent_name = data.get("agent", "feedback")
        user_input = (data.get("input") or "").strip()

        if agent_name not in AGENTS:
            return self._send(400, {"error": f"unknown agent '{agent_name}'"})
        if not user_input:
            return self._send(400, {"error": "'input' is required"})

        # --- build a fresh agent and run it
        try:
            agent = AGENTS[agent_name]()          # reads GEMINI_API_KEY from env
            response = agent.process_request(user_input)
        except Exception as e:                    # never leak a stack trace to the client
            return self._send(500, {"error": str(e)})

        self._send(200, {"agent": agent.name, "response": response})
