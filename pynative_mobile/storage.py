import os
import json
import sqlite3
import threading
from typing import Any, Optional


class Storage:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or os.path.join(os.getcwd(), "pynative_storage.db")
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self._lock = threading.Lock()
        self.conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()

    def save(self, key: str, value: Any) -> None:
        with self._lock:
            self.conn.execute(
                "REPLACE INTO kv (key,value) VALUES (?,?)", (key, json.dumps(value))
            )
            self.conn.commit()

    def load(self, key: str) -> Any:
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM kv WHERE key=?", (key,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def delete(self, key: str) -> None:
        with self._lock:
            self.conn.execute("DELETE FROM kv WHERE key=?", (key,))
            self.conn.commit()
