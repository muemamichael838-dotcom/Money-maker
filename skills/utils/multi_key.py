import os
import random
from persistence_manager import PersistenceManager

pm = PersistenceManager()

class MultiKeyManager:
    def __init__(self, env_var_name):
        self.env_var_name = env_var_name
        self.keys = []
        self._refresh_keys()

    def _refresh_keys(self):
        # Get from env
        env_keys = os.environ.get(self.env_var_name, "").split(",")
        # Get from persistent memory
        saved_settings = pm.get_memory("api_settings") or {}

        # Mapping env var names to settings keys
        mapping = {
            "GROQ_API_KEYS": "groq",
            "HUGGINGFACE_API_KEYS": "hf",
            "GOOGLE_API_KEYS": "google",
            "ODDS_API_KEYS": "odds"
        }

        setting_key = mapping.get(self.env_var_name)
        saved_keys = []
        if setting_key and setting_key in saved_settings:
            saved_keys = saved_settings[setting_key].split(",")

        self.keys = [k.strip() for k in (env_keys + saved_keys) if k.strip()]

    def get_key(self):
        self._refresh_keys()
        if not self.keys:
            return None
        return random.choice(self.keys)

    def rotate_on_error(self):
        """Logic for manual rotation if needed by a skill."""
        self._refresh_keys()
