import time
from typing import Dict, Any, List
from assistant.database import DatabaseManager


class AnalyticsTracker:
    """
    Usage Analytics & Telemetry Engine:
    - Tracks command frequency, category distribution, response latencies, and success metrics
    - Generates spoken summaries and structured data for the GUI Dashboard
    """

    def __init__(self, db: DatabaseManager):
        self.db = db

    def record_turn(
        self,
        raw_command: str,
        intent: str,
        category: str,
        start_time: float,
        success: bool = True
    ):
        """Records an execution event with elapsed milliseconds."""
        duration_ms = (time.time() - start_time) * 1000.0
        self.db.log_interaction(
            raw_command=raw_command,
            intent=intent,
            category=category,
            execution_time_ms=round(duration_ms, 2),
            success=success
        )

    def get_spoken_summary(self) -> str:
        """Constructs a natural language summary of assistant usage."""
        summary = self.db.get_analytics_summary()
        total = summary["total_commands"]
        today = summary["today_count"]
        rate = summary["success_rate"]
        avg_ms = summary["avg_response_time_ms"]

        if total == 0:
            return "No interactions have been recorded yet."

        top_intent_str = ""
        if summary["top_intents"]:
            top = summary["top_intents"][0]
            top_intent_str = f" Your most common request is {top['intent']} with {top['count']} uses."

        return (
            f"You have issued a total of {total} commands, with {today} recorded today. "
            f"The system success rate is {rate} percent, averaging {avg_ms} milliseconds per response."
            f"{top_intent_str}"
        )

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Provides full metrics payload for GUI Dashboard rendering."""
        summary = self.db.get_analytics_summary()
        recent = self.db.get_recent_interactions(limit=15)
        return {
            "summary": summary,
            "recent_logs": recent
        }
