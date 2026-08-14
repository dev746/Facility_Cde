import os
from dotenv import load_dotenv
load_dotenv()
from query.intent import parse_intent

print("RESULT:", parse_intent("why is the llm failing"))
