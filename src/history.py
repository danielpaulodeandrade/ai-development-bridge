import os
import json
from datetime import datetime

class HistoryLogger:
    def __init__(self):
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.history_file = os.path.join(self.logs_dir, "history.jsonl")

    def log_interaction(self, platform: str, prompt: str, response: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "platform": platform,
            "prompt": prompt,
            "response": response
        }
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

history_logger = HistoryLogger()
