"""
TutorAgent: explains a concept or a piece of code to a student.
Stateless on purpose: each question is independent, so no memory block.
"""

from .base_agent import BaseAgent


class TutorAgent(BaseAgent):
    def __init__(self, **overrides):
        super().__init__(
            name="TutorAgent",
            role="tutor",
            system_message=(
                "You are a patient tutor for first-year engineering students. "
                "You explain, you do not grade."
            ),
            instructions=(
                "The student will give you code or a question. Explain the key "
                "idea in plain language, using one small analogy if it helps. "
                "Max 150 words. Never give a full solution to an assignment."
            ),
            knowledge_base=(
                "Course context: Python 3, no external libraries. Students have "
                "covered variables, loops, functions, and lists. NOT yet covered: "
                "classes, exceptions, file I/O."
            ),
            temperature=0.7,   # a bit more variety is fine for explanations
            **overrides,
        )

    def process_request(self, input_request: str) -> str:
        prompt = f"Student asks:\n{input_request}"
        self.last_prompt = prompt
        return self.generate_response(prompt)
