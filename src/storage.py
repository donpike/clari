import sqlite3
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime

class Storage:
    def __init__(self):
        self.db_path = Path('data/tasks.db')
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    input_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    result JSON,
                    priority INTEGER DEFAULT 0
                )
            """)

    def save_task(self, task):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks 
                (id, type, input_path, status, created_at, result, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.type,
                str(task.input_path),
                task.status,
                task.created_at,
                json.dumps(task.result) if task.result else None,
                task.priority
            ))

    def get_pending_tasks(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in 
                   conn.execute("SELECT * FROM tasks WHERE status='pending' ORDER BY priority DESC")] 