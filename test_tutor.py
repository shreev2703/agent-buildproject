import sys
from agents.tutor_agent import TutorAgent

question = sys.argv[1] if len(sys.argv) > 1 else "Why does my average() function need len(values)? What does len do?"
agent = TutorAgent()
print(agent.process_request(question))
