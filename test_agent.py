import subprocess
import json

def chat_with_agent(prompt):
    # Using one-shot mode for simplicity in this bridge
    cmd = ["python3", "-m", "hermes_cli.main", "-z", prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

print(chat_with_agent("Who are you?"))
