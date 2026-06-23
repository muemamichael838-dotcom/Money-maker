import os
import json
import psycopg2
from supabase import create_client, Client

class PersistenceManager:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.postgres_url = os.environ.get("POSTGRES_URL")

        self.supabase: Client = None
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)

        self.conn = None
        if self.postgres_url:
            self.conn = psycopg2.connect(self.postgres_url)
            self._init_db()

    def _init_db(self):
        with self.conn.cursor() as cur:
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
            self.conn.commit()

    def log(self, level, message, metadata=None):
        print(f"[{level}] {message}")
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO logs (level, message, metadata) VALUES (%s, %s, %s)",
                            (level, message, json.dumps(metadata)))
                self.conn.commit()

        if self.supabase:
            self.supabase.table("logs").insert({"level": level, "message": message, "metadata": metadata}).execute()

    def save_memory(self, key, value):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO memory (key, value, updated_at) VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
                """, (key, json.dumps(value)))
                self.conn.commit()

        if self.supabase:
            self.supabase.table("memory").upsert({"key": key, "value": value}).execute()

    def get_memory(self, key):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT value FROM memory WHERE key = %s", (key,))
                row = cur.fetchone()
                if row:
                    return row[0]

        if self.supabase:
            res = self.supabase.table("memory").select("value").eq("key", key).execute()
            if res.data:
                return res.data[0]["value"]
        return None

if __name__ == "__main__":
    pm = PersistenceManager()
    pm.log("INFO", "Persistence Manager initialized")
