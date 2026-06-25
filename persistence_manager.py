import os
import json
import sqlite3

class PersistenceManager:
    def __init__(self):
        self.postgres_url = os.environ.get("POSTGRES_URL")
        self.sqlite_path = os.path.join(os.environ.get("MONEY_MAKER_HOME", "/opt/data"), "memory.db")

        self.conn = None
        self.db_type = None

        if self.postgres_url:
            try:
                import psycopg2
                self.conn = psycopg2.connect(self.postgres_url)
                self.db_type = "postgres"
                print("Using Postgres backend.")
            except Exception as e:
                print(f"Postgres connection failed: {e}. Falling back to SQLite.")
                self._use_sqlite()
        else:
            self._use_sqlite()

        self._init_db()

    def _use_sqlite(self):
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        self.conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        self.db_type = "sqlite"
        print(f"Using SQLite backend at {self.sqlite_path}")

    def _init_db(self):
        cur = self.conn.cursor()
        if self.db_type == "postgres":
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    metadata JSONB
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id SERIAL PRIMARY KEY,
                    key TEXT UNIQUE,
                    value JSONB,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            # SQLite requires separate calls or executescript
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
            if self.db_type == "postgres":
                cur.execute("INSERT INTO logs (level, message, metadata) VALUES (%s, %s, %s)",
                            (level, message, json.dumps(metadata)))
            else:
                cur.execute("INSERT INTO logs (level, message, metadata) VALUES (?, ?, ?)",
                            (level, message, json.dumps(metadata)))
            self.conn.commit()
        except Exception as e:
            print(f"Logging error: {e}")

    def save_memory(self, key, value):
        try:
            cur = self.conn.cursor()
            val_str = json.dumps(value)
            if self.db_type == "postgres":
                cur.execute("""
                    INSERT INTO memory (key, value, updated_at) VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
                """, (key, val_str))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, val_str))
            self.conn.commit()
        except Exception as e:
            print(f"Memory save error: {e}")

    def get_memory(self, key):
        try:
            cur = self.conn.cursor()
            if self.db_type == "postgres":
                cur.execute("SELECT value FROM memory WHERE key = %s", (key,))
            else:
                cur.execute("SELECT value FROM memory WHERE key = ?", (key,))
            row = cur.fetchone()
            if row:
                return json.loads(row[0])
        except Exception:
            pass
        return None

if __name__ == "__main__":
    pm = PersistenceManager()
    pm.log("INFO", "Self-Saving Persistence Initialized")
