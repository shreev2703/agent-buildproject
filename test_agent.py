"""
Run one agent on one file. Prints the response and saves three artifacts:
  outputs/<agent>_<timestamp>_input.txt    - the raw file we fed it
  outputs/<agent>_<timestamp>_prompt.txt   - the assembled prompt (user slot)
  outputs/<agent>_<timestamp>_output.txt   - what the model said
"""

import sys
from datetime import datetime
from pathlib import Path

from agents.feedback_agent import FeedbackAgent
from agents.utils import file_to_string


def save(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main(file_path: str) -> None:
    agent = FeedbackAgent()
    source = file_to_string(file_path)

    print(f"[{agent.name}] status: {agent.get_status()}")
    print(f"[{agent.name}] sending {file_path} to {agent.model} ...\n")

    response = agent.process_request(source)

    print("=" * 60)
    print(response)
    print("=" * 60)
    print(f"\n[{agent.name}] status: {agent.get_status()}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path("outputs")
    out.mkdir(exist_ok=True)
    base = f"{agent.name}_{stamp}"
    save(out / f"{base}_input.txt", source)
    save(out / f"{base}_prompt.txt", agent.last_prompt)
    save(out / f"{base}_output.txt", response)
    print(f"saved -> outputs/{base}_*.txt")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "samples/buggy_average.py")
