import time
import threading
import datetime
from typing import List, Dict, Any, Callable, Optional
from assistant.database import DatabaseManager


class ReminderService:
    """
    Background scheduler and notification service for reminders:
    - Runs a daemon thread continuously polling SQLite
    - Fires visual and audio alerts when a reminder is due
    - Supports callback integration with SpeechManager and GUI Dashboard
    """

    def __init__(self, db: DatabaseManager, on_trigger_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.db = db
        self.on_trigger_callback = on_trigger_callback
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Starts the background reminder monitoring thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="ReminderMonitor")
        self._thread.start()

    def stop(self):
        """Stops the reminder monitor."""
        self._running = False

    def _monitor_loop(self):
        while self._running:
            try:
                due_reminders = self.db.get_pending_due_reminders()
                for rem in due_reminders:
                    rem_id = rem["id"]
                    title = rem["title"]

                    # Mark notified first to avoid double triggers
                    self.db.mark_reminder_notified(rem_id)

                    # Trigger alert callback
                    if self.on_trigger_callback:
                        try:
                            self.on_trigger_callback(rem)
                        except Exception as cb_err:
                            print(f"[Reminder Trigger Error]: {cb_err}")
                    else:
                        print(f"\n🔔 [REMINDER ALERT]: {title.upper()}!")

            except Exception as e:
                print(f"[Reminder Service Exception]: {e}")

            time.sleep(3)

    def create_reminder(self, title: str, remind_at: datetime.datetime) -> Dict[str, Any]:
        """Creates a new reminder in SQLite."""
        rem_id = self.db.add_reminder(title, remind_at)
        formatted_time = remind_at.strftime("%I:%M %p")
        return {
            "id": rem_id,
            "title": title,
            "remind_at": remind_at,
            "formatted_time": formatted_time
        }

    def get_active_reminders(self) -> List[Dict[str, Any]]:
        return self.db.get_all_reminders(limit=20)

    def clear_all(self):
        self.db.clear_completed_reminders()
