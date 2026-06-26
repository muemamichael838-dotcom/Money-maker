import os
import time
import requests
from persistence_manager import PersistenceManager

class TelegramBot:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.allowed_users = os.environ.get("TELEGRAM_ALLOWED_USERS", "").split(",")
        self.pm = PersistenceManager()

    def poll(self):
        if not self.token:
            self.pm.log("WARNING", "Telegram Token missing. Bot inactive.")
            return

        self.pm.log("INFO", "Telegram Bot active and polling.")
        offset = 0
        while True:
            try:
                resp = requests.get(f"https://api.telegram.org/bot{self.token}/getUpdates?offset={offset}&timeout=30")
                if resp.status_code == 200:
                    data = resp.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        msg = update.get("message", {})
                        user_id = str(msg.get("from", {}).get("id"))
                        text = msg.get("text")

                        if user_id in self.allowed_users:
                            # Forward command to Money Maker Engine (Simplified for this script)
                            self.pm.log("INFO", f"Telegram Command from {user_id}: {text}")
                            requests.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                                         json={"chat_id": user_id, "text": f"Money Maker 🤑: Processing '{text}'..."})
                        else:
                            self.pm.log("SECURITY", f"Unauthorized Telegram access attempt by {user_id}")

            except Exception as e:
                self.pm.log("ERROR", f"Telegram Polling Error: {e}")

            time.sleep(1)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.poll()
