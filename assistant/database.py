import os
import sqlite3
import datetime
from typing import Dict, Any, List, Optional
from config import DATABASE_PATH, DEFAULT_ASSISTANT_NAME, DEFAULT_USER_NAME, DEFAULT_SECURITY_LEVEL


class DatabaseManager:
    """
    Manages persistent SQLite storage for Jarvis:
    - User Profile & Personalization
    - Reminders & Timers
    - Notes & Quick Memos
    - Usage Analytics & Interaction Logs
    - Security Audit Trail
    - Custom Command Aliases
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates tables and populates default settings if not already present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. User Profile & Preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)

            # 2. Reminders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    remind_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    notified INTEGER DEFAULT 0
                )
            """)

            # 3. Notes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TEXT NOT NULL,
                    is_archived INTEGER DEFAULT 0
                )
            """)

            # 4. Usage Analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    raw_command TEXT,
                    intent TEXT,
                    category TEXT,
                    execution_time_ms REAL,
                    success INTEGER DEFAULT 1
                )
            """)

            # 5. Security Audit Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    details TEXT
                )
            """)

            # 6. Custom Command Aliases / Shortcuts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_aliases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_phrase TEXT UNIQUE NOT NULL,
                    target_command TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Seed default profile values if empty
            cursor.execute("SELECT COUNT(*) as count FROM user_profile")
            if cursor.fetchone()["count"] == 0:
                defaults = {
                    "user_name": DEFAULT_USER_NAME,
                    "assistant_name": DEFAULT_ASSISTANT_NAME,
                    "personality": "Jarvis",
                    "voice_gender": "male",
                    "default_city": "London",
                    "security_level": DEFAULT_SECURITY_LEVEL,
                    "theme": "dark"
                }
                now = datetime.datetime.now().isoformat()
                for k, v in defaults.items():
                    cursor.execute(
                        "INSERT INTO user_profile (key, value, updated_at) VALUES (?, ?, ?)",
                        (k, str(v), now)
                    )
            conn.commit()

    # =========================================================================
    # USER PROFILE & PERSONALIZATION
    # =========================================================================

    def get_profile(self) -> Dict[str, str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_profile")
            rows = cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}

    def get_profile_field(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_profile_field(self, key: str, value: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO user_profile (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """, (key, str(value), now))
            conn.commit()

    # =========================================================================
    # REMINDERS
    # =========================================================================

    def add_reminder(self, title: str, remind_at: datetime.datetime) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()
            remind_str = remind_at.isoformat()
            cursor.execute("""
                INSERT INTO reminders (title, remind_at, created_at, status, notified)
                VALUES (?, ?, ?, 'pending', 0)
            """, (title, remind_str, now))
            conn.commit()
            return cursor.lastrowid

    def get_pending_due_reminders(self) -> List[Dict[str, Any]]:
        """Returns reminders that are due right now or past due and haven't been notified yet."""
        now = datetime.datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reminders
                WHERE status = 'pending' AND remind_at <= ? AND notified = 0
                ORDER BY remind_at ASC
            """, (now,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_all_reminders(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reminders
                ORDER BY remind_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def mark_reminder_notified(self, reminder_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reminders
                SET notified = 1, status = 'completed'
                WHERE id = ?
            """, (reminder_id,))
            conn.commit()

    def delete_reminder(self, reminder_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_completed_reminders(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reminders WHERE status = 'completed'")
            conn.commit()

    # =========================================================================
    # NOTES
    # =========================================================================

    def add_note(self, content: str, category: str = "general") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            cursor.execute("""
                INSERT INTO notes (content, category, created_at)
                VALUES (?, ?, ?)
            """, (content, category, now))
            conn.commit()
            return cursor.lastrowid

    def get_recent_notes(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notes
                WHERE is_archived = 0
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def delete_note(self, note_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all_notes(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes")
            count = cursor.rowcount
            conn.commit()
            return count

    # =========================================================================
    # USAGE ANALYTICS
    # =========================================================================

    def log_interaction(self, raw_command: str, intent: str, category: str, execution_time_ms: float, success: bool = True):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO usage_logs (timestamp, raw_command, intent, category, execution_time_ms, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (now, raw_command, intent, category, execution_time_ms, 1 if success else 0))
            conn.commit()

    def get_analytics_summary(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total commands
            cursor.execute("SELECT COUNT(*) as total FROM usage_logs")
            total_commands = cursor.fetchone()["total"]

            # Success rate
            cursor.execute("SELECT COUNT(*) as successful FROM usage_logs WHERE success = 1")
            successful_commands = cursor.fetchone()["successful"]
            success_rate = (successful_commands / total_commands * 100) if total_commands > 0 else 100.0

            # Today's commands
            today_prefix = datetime.date.today().isoformat()
            cursor.execute("SELECT COUNT(*) as today_count FROM usage_logs WHERE timestamp LIKE ?", (f"{today_prefix}%",))
            today_count = cursor.fetchone()["today_count"]

            # Average response time (ms)
            cursor.execute("SELECT AVG(execution_time_ms) as avg_time FROM usage_logs")
            avg_time = cursor.fetchone()["avg_time"] or 0.0

            # Top 5 Intents
            cursor.execute("""
                SELECT intent, COUNT(*) as count
                FROM usage_logs
                WHERE intent IS NOT NULL AND intent != ''
                GROUP BY intent
                ORDER BY count DESC
                LIMIT 5
            """)
            top_intents = [dict(r) for r in cursor.fetchall()]

            # Top Categories
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM usage_logs
                WHERE category IS NOT NULL AND category != ''
                GROUP BY category
                ORDER BY count DESC
                LIMIT 5
            """)
            top_categories = [dict(r) for r in cursor.fetchall()]

            return {
                "total_commands": total_commands,
                "today_count": today_count,
                "success_rate": round(success_rate, 1),
                "avg_response_time_ms": round(avg_time, 1),
                "top_intents": top_intents,
                "top_categories": top_categories
            }

    def get_recent_interactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM usage_logs
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    # =========================================================================
    # SECURITY AUDIT TRAIL
    # =========================================================================

    def log_security_event(self, action: str, description: str, status: str, details: str = ""):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO security_audit_log (timestamp, action, description, status, details)
                VALUES (?, ?, ?, ?, ?)
            """, (now, action, description, status, details))
            conn.commit()

    def get_security_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM security_audit_log
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    # =========================================================================
    # CUSTOM COMMAND ALIASES
    # =========================================================================

    def add_custom_alias(self, trigger_phrase: str, target_command: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO custom_aliases (trigger_phrase, target_command, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(trigger_phrase) DO UPDATE SET target_command = excluded.target_command
            """, (trigger_phrase.lower().strip(), target_command.strip(), now))
            conn.commit()

    def get_custom_aliases(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM custom_aliases ORDER BY trigger_phrase ASC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def resolve_alias(self, command: str) -> Optional[str]:
        cmd_clean = command.lower().strip()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT target_command FROM custom_aliases WHERE trigger_phrase = ?", (cmd_clean,))
            row = cursor.fetchone()
            if row:
                return row["target_command"]
        return None
