import os
import json
import sqlite3

class PersistenceManager:
    def __init__(self):
        # We force SQLite for Render Free Tier compatibility
        self.sqlite_path = os.path.join(os.environ.get("MONEY_MAKER_HOME", "/opt/data"), "memory.db")
        self.conn = None
        self.db_type = "sqlite"
        self._use_sqlite()
        self._init_db()

    def _use_sqlite(self):
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        self.conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        print(f"Using lightweight SQLite backend at {self.sqlite_path}")

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                message TEXT,
                metadata TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def log(self, level, message, metadata=None):
        print(f"[{level}] {message}")
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO logs (level, message, metadata) VALUES (?, ?, ?)",
                        (level, message, json.dumps(metadata)))
            self.conn.commit()
        except Exception as e:
            print(f"Logging error: {e}")

    def save_memory(self, key, value):
        try:
            cur = self.conn.cursor()
            val_str = json.dumps(value)
            cur.execute("""
                INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, val_str))
            self.conn.commit()
        except Exception as e:
            print(f"Memory save error: {e}")

    def get_memory(self, key):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT value FROM memory WHERE key = ?", (key,))
            row = cur.fetchone()
            if row:
                return json.loads(row[0])
        except Exception:
            pass
        return None

if __name__ == "__main__":
    pm = PersistenceManager()
    pm.log("INFO", "Minimal Persistence Initialized")
