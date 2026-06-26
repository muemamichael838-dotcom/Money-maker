from persistence_manager import PersistenceManager

class MultiKeyManager:
    def __init__(self, env_var_name):
        self.env_var_name = env_var_name
        self.pm = PersistenceManager()

    def get_key(self):
        # Prefer DB-stored key if exists
        stored = self.pm.get_memory(f"key_{self.env_var_name}")
        if stored: return stored

        # Fallback to env
        import os
        keys = os.environ.get(self.env_var_name, "").split(",")
        return keys[0] if keys else None

    def rotate_on_error(self):
        import os
        keys = os.environ.get(self.env_var_name, "").split(",")
        if len(keys) > 1:
            # Shift the list in memory if possible or just log it
            self.pm.log("WARNING", f"Rotating keys for {self.env_var_name}")
            # Simple rotation logic: store next key in DB
            current = self.get_key()
            try:
                idx = keys.index(current)
                next_key = keys[(idx + 1) % len(keys)]
                self.pm.save_memory(f"key_{self.env_var_name}", next_key)
            except ValueError:
                self.pm.save_memory(f"key_{self.env_var_name}", keys[0])

if __name__ == "__main__":
    print("Multi-key manager ready.")
