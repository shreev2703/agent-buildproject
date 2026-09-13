"""
BaseAgent: the "index card + phone line to the AI" that every agent shares.

Subclasses only need to:
  1. pass their own system_message / instructions to __init__
  2. implement process_request(), which assembles the prompt and calls
     generate_response()
"""

import logging
import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from google import genai
from google.genai import types

# the SDK logs a noisy "AFC" hint on every call; we do not use that feature
logging.getLogger("google_genai.models").setLevel(logging.WARNING + 1)


class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        role: str,
        system_message: str,
        instructions: str,
        knowledge_base: str = "",
        model: str = "gemini-3.6-flash",
        temperature: float = 0.2,
        seed: int | None = 42,
    ):
        # --- identity: labels for humans/orchestrator, the AI never sees these
        self.name = name
        self.role = role

        # --- the index card: text that shapes how the AI behaves
        self.system_message = system_message
        self.instructions = instructions
        self.knowledge_base = knowledge_base

        # --- which model, and the randomness controls
        self.model = model
        self.temperature = temperature
        self.seed = seed

        # --- sticky note: "standby" | "processing" | "done" | "error"
        self.status = "standby"

        # --- tiny memory of the last turn (used by process_request in subclasses)
        self.previous_input: str = ""
        self.previous_response: str = ""

        # --- API key: read from environment. load_dotenv() copies .env into
        #     the environment locally; on Vercel the dashboard sets it directly.
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set (check your .env)")
        self.client = genai.Client(api_key=api_key)

    # ------------------------------------------------------------------ status
    def update_status(self, new_status: str) -> None:
        self.status = new_status

    def get_status(self) -> str:
        return self.status

    # ------------------------------------------------------------- the index card
    def build_system_prompt(self) -> str:
        """Glue system_message + instructions + knowledge_base into one block.
        This is what goes in the API's *system* slot."""
        parts = [self.system_message, self.instructions]
        if self.knowledge_base:
            parts.append(f"Reference material:\n{self.knowledge_base}")
        return "\n\n".join(parts)

    # ------------------------------------------------------ the phone line to AI
    def generate_response(self, prompt: str) -> str:
        """The ONLY method that touches the network.
        prompt  -> goes in the user slot
        system  -> goes in the system slot (the rules)
        """
        self.update_status("processing")
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.build_system_prompt(),
                    temperature=self.temperature,
                    seed=self.seed,
                ),
            )
            self.update_status("done")
            return response.text or ""
        except Exception as e:
            self.update_status("error")
            raise

    # ------------------------------------------ each subclass fills this in
    @abstractmethod
    def process_request(self, input_request: str) -> str:
        """Assemble the full prompt from input_request (+ any memory),
        call generate_response(), remember the turn, return the text."""
        ...
