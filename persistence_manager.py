import os
import json
import psycopg2
import sqlite3

class PersistenceManager:
    def __init__(self):
        self.postgres_url = os.environ.get("POSTGRES_URL")
        self.sqlite_path = "/opt/data/memory.db"

        # Self-saving: prefer local postgres or sqlite
        self.conn = None
        if self.postgres_url:
            try:
                self.conn = psycopg2.connect(self.postgres_url)
                self._init_db("postgres")
            except Exception:
                self._use_sqlite()
        else:
            self._use_sqlite()

    def _use_sqlite(self):
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        self.conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        self._init_db("sqlite")

    def _init_db(self, db_type):
        placeholder = "%s" if db_type == "postgres" else "?"
        cur = self.conn.cursor()

        if db_type == "postgres":
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    metadata JSONB
                );
                CREATE TABLE IF NOT EXISTS memory (
                    id SERIAL PRIMARY KEY,
                    key TEXT UNIQUE,
                    value JSONB,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    metadata TEXT
                );
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
            if hasattr(self.conn, 'psycopg2'): # Rough check
                cur.execute("INSERT INTO logs (level, message, metadata) VALUES (%s, %s, %s)",
                            (level, message, json.dumps(metadata)))
            else:
                cur.execute("INSERT INTO logs (level, message, metadata) VALUES (?, ?, ?)",
                            (level, message, json.dumps(metadata)))
            self.conn.commit()
        except Exception:
            pass

    def save_memory(self, key, value):
        try:
            cur = self.conn.cursor()
            val_str = json.dumps(value)
            # Generic upsert
            if os.environ.get("POSTGRES_URL"):
                cur.execute("""
                    INSERT INTO memory (key, value, updated_at) VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
                """, (key, val_str))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, val_str))
            self.conn.commit()
        except Exception:
            pass

    def get_memory(self, key):
        try:
            cur = self.conn.cursor()
            if os.environ.get("POSTGRES_URL"):
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
