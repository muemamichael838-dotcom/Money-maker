import os
import json
import sqlite3
import time
from urllib.parse import urlparse

# Optional Postgres support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

class PersistenceManager:
    def __init__(self):
        # We prefer DATABASE_URL (Supabase/Neon/Render)
        self.db_url = os.environ.get("DATABASE_URL")
        self.conn = None
        self.db_type = "sqlite"

        if self.db_url and HAS_POSTGRES:
            try:
                self._use_postgres()
                print("--- [PERSISTENCE] Linked to External Neural Database (Postgres) ---")
            except Exception as e:
                print(f"--- [PERSISTENCE] Postgres Link Failed: {e}. Falling back to Local SQLite. ---")
                self._use_sqlite()
        else:
            if self.db_url and not HAS_POSTGRES:
                print("--- [PERSISTENCE] Postgres requested but psycopg2 missing. Using SQLite. ---")
            self._use_sqlite()

        self._init_db()

    def _use_postgres(self):
        self.conn = psycopg2.connect(self.db_url)
        self.db_type = "postgres"

    def _use_sqlite(self):
        # Default home in /opt/data for persistence across Docker restarts in Hugging Face Spaces (if mapped)
        home = os.environ.get("MONEY_MAKER_HOME", "/opt/data")
        sqlite_path = os.path.join(home, "memory.db")
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        self.conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.db_type = "sqlite"

    def _init_db(self):
        cur = self.conn.cursor()
        if self.db_type == "postgres":
            # Neural Logs - Supabase/Postgres
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    metadata JSONB
                );
            """)
            # Persistent Memory - Supabase/Postgres
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id SERIAL PRIMARY KEY,
                    key TEXT UNIQUE,
                    value JSONB,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Session Tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    data JSONB,
                    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            # Neural Logs - SQLite
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    metadata TEXT
                );
            """)
            # Persistent Memory - SQLite
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Session Tracking - SQLite
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    data TEXT,
                    last_active DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
        self.conn.commit()

    def log(self, level, message, metadata=None):
        try:
            cur = self.conn.cursor()
            meta_str = json.dumps(metadata) if metadata else None

            if self.db_type == "postgres":
                from psycopg2.extras import Json
                cur.execute(
                    "INSERT INTO logs (level, message, metadata) VALUES (%s, %s, %s)",
                    (level, message, Json(metadata) if metadata else None)
                )
            else:
                cur.execute(
                    "INSERT INTO logs (level, message, metadata) VALUES (?, ?, ?)",
                    (level, message, meta_str)
                )
            self.conn.commit()

            # Write to local file as secondary backup
            home = os.environ.get("MONEY_MAKER_HOME", "/opt/data")
            with open(os.path.join(home, "agent.log"), "a") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\n")
        except Exception as e:
            print(f"Logging Sync Error: {e}")

    def save_memory(self, key, value):
        try:
            cur = self.conn.cursor()
            if self.db_type == "postgres":
                from psycopg2.extras import Json
                cur.execute("""
                    INSERT INTO memory (key, value, updated_at) VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
                """, (key, Json(value)))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, json.dumps(value)))
            self.conn.commit()
        except Exception as e:
            print(f"Memory Sync Error: {e}")

    def get_memory(self, key):
        try:
            cur = self.conn.cursor()
            if self.db_type == "postgres":
                cur.execute("SELECT value FROM memory WHERE key = %s", (key,))
            else:
                cur.execute("SELECT value FROM memory WHERE key = ?", (key,))
            row = cur.fetchone()
            if row:
                res = row[0]
                return json.loads(res) if isinstance(res, str) else res
        except Exception:
            pass
        return None

    def save_session(self, session_id, data):
        try:
            cur = self.conn.cursor()
            if self.db_type == "postgres":
                from psycopg2.extras import Json
                cur.execute("""
                    INSERT INTO sessions (session_id, data, last_active) VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (session_id) DO UPDATE SET data = EXCLUDED.data, last_active = CURRENT_TIMESTAMP
                """, (session_id, Json(data)))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO sessions (session_id, data, last_active) VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (session_id, json.dumps(data)))
            self.conn.commit()
        except Exception as e:
            print(f"Session Sync Error: {e}")

if __name__ == "__main__":
    pm = PersistenceManager()
    pm.log("INFO", "Neural Persistence Link Verified.")
