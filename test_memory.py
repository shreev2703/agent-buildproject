"""
Two turns with ONE agent object, so the second prompt carries the first turn.
Compare outputs/*_turn1_prompt.txt with *_turn2_prompt.txt.
"""

from datetime import datetime
from pathlib import Path

from agents.feedback_agent import FeedbackAgent
from agents.utils import file_to_string

agent = FeedbackAgent()          # created ONCE -> memory persists across turns
out = Path("outputs")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for turn, path in enumerate(["samples/buggy_average.py", "samples/fixed_average.py"], start=1):
    print(f"\n--- turn {turn}: {path} ---")
    response = agent.process_request(file_to_string(path))
    print(response)
    (out / f"{agent.name}_{stamp}_turn{turn}_prompt.txt").write_text(agent.last_prompt, encoding="utf-8")
    (out / f"{agent.name}_{stamp}_turn{turn}_output.txt").write_text(response, encoding="utf-8")
    print(f"[prompt length: {len(agent.last_prompt)} chars]")
