import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Iterable, Optional

from config import Config


class Database:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._init_connection()
        self.setup_database()

    def _init_connection(self) -> None:
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row

    @contextmanager
    def get_connection(self):
        with self._lock:
            try:
                yield self._connection
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise

    def setup_database(self) -> None:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS volunteer_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    creator_id TEXT NOT NULL,
                    creator_username TEXT NOT NULL,
                    claimed_by TEXT,
                    claimed_by_username TEXT,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    # Volunteer tasks
    def create_volunteer_task(self, title: str, creator_id: str, creator_username: str) -> int:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO volunteer_tasks (title, creator_id, creator_username)
                VALUES (?, ?, ?)
                """,
                (title, creator_id, creator_username),
            )
            return cur.lastrowid

    def get_all_volunteer_tasks(self) -> list[sqlite3.Row]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM volunteer_tasks ORDER BY status ASC, created_at DESC")
            return cur.fetchall()

    def get_volunteer_task_by_id(self, task_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM volunteer_tasks WHERE id = ?", (task_id,))
            return cur.fetchone()

    def join_volunteer_task(self, task_id: int, user_id: str, username: str) -> bool:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM volunteer_tasks WHERE id = ?", (task_id,))
            row = cur.fetchone()
            if not row or row["status"] != "open":
                return False
            cur.execute(
                """
                UPDATE volunteer_tasks
                SET claimed_by = ?, claimed_by_username = ?, status = 'claimed', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'open'
                """,
                (user_id, username, task_id),
            )
            return cur.rowcount > 0

    def leave_volunteer_task(self, task_id: int, user_id: str) -> bool:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT claimed_by FROM volunteer_tasks WHERE id = ?",
                (task_id,),
            )
            row = cur.fetchone()
            if not row or row["claimed_by"] != str(user_id):
                return False
            cur.execute(
                """
                UPDATE volunteer_tasks
                SET claimed_by = NULL, claimed_by_username = NULL, status = 'open', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (task_id,),
            )
            return cur.rowcount > 0

    def remove_volunteer_task(self, task_id: int) -> bool:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM volunteer_tasks WHERE id = ?", (task_id,))
            return cur.rowcount > 0

    def get_user_volunteer_status(self, user_id: str) -> dict[str, list[sqlite3.Row]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM volunteer_tasks WHERE creator_id = ? ORDER BY created_at DESC",
                (user_id,),
            )
            created = cur.fetchall()
            cur.execute(
                "SELECT * FROM volunteer_tasks WHERE claimed_by = ? ORDER BY updated_at DESC",
                (user_id,),
            )
            joined = cur.fetchall()
            return {"created": created, "joined": joined}


db = Database(Config.DATABASE_PATH)


__all__ = ["db", "Database"]

