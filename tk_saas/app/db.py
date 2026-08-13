import sqlite3


class Database:
    def __init__(self, path="tk_saas.db"):
        self.path = path
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def add_item(self, item):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO items (name,value) VALUES (?,?)", (item.name, item.value))
        self.conn.commit()
        return cur.lastrowid

    def get_items(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id,name,value,created_at FROM items ORDER BY id DESC")
        rows = cur.fetchall()
        return [dict(r) for r in rows]
