"""
FeedbackAgent: reviews a student's code file and gives TA-style feedback.
Differs from BaseAgent only in (a) its index card and (b) how it assembles
the prompt in process_request.
"""

from .base_agent import BaseAgent


class FeedbackAgent(BaseAgent):
    def __init__(self, **overrides):
        super().__init__(
            name="FeedbackAgent",
            role="code reviewer",
            system_message=(
                "You are a teaching assistant for an introductory engineering "
                "lab course. Students submit Python code; you review it."
            ),
            instructions=(
                "Read the submitted code. Give feedback in this format:\n"
                "1. What works\n"
                "2. Bugs or logic errors (quote the line)\n"
                "3. One suggestion to improve style or clarity\n"
                "Do NOT rewrite the whole program. Be concise and encouraging."
            ),
            **overrides,   # lets a caller change model/temperature/etc.
        )

    def process_request(self, input_request: str) -> str:
        # ---- assemble the prompt (this is the "memory by concatenation" pattern)
        parts = []
        if self.previous_input:
            parts.append(f"Previous submission:\n{self.previous_input}")
            parts.append(f"Your previous feedback:\n{self.previous_response}")
        parts.append(f"Current submission:\n{input_request}")
        prompt = "\n\n".join(parts)

        # ---- send it
        response = self.generate_response(prompt)

        # ---- remember this turn for next time
        self.previous_input = input_request
        self.previous_response = response

        # ---- expose the assembled prompt so the test script can save it
        self.last_prompt = prompt
        return response
