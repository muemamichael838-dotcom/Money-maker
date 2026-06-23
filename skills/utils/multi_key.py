import os

class MultiKeyManager:
    def __init__(self, env_var_name):
        self.keys = os.environ.get(env_var_name, "").split(",")
        self.keys = [k.strip() for k in self.keys if k.strip()]
        self.index = 0

    def get_key(self):
        if not self.keys:
            return os.environ.get(env_var_name.replace("_KEYS", "_KEY"))

        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

    def rotate_on_error(self):
        """Called when a key fails to move to the next one."""
        if not self.keys: return
        self.index = (self.index + 1) % len(self.keys)

def get_rotated_key(env_var_name):
    pool = os.environ.get(env_var_name, "").split(",")
    pool = [k.strip() for k in pool if k.strip()]
    if not pool:
        return os.environ.get(env_var_name.replace("_KEYS", "_KEY"))
    # For stateless functions, we might need a more persistent way to track index,
    # but for simple skill calls, we pick one.
    import random
    return random.choice(pool)
