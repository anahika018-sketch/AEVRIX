import time
from typing import Dict, Any, Callable, Optional, Tuple
from assistant.database import DatabaseManager
from config import CRITICAL_ACTIONS, DEFAULT_SECURITY_LEVEL


class SecurityManager:
    """
    Security and Permission Layer:
    - Intercepts dangerous actions (shutdown, reboot, recycle bin wipe, note wipe)
    - Implements confirmation workflow (two-step verification via voice or GUI)
    - Maintains an immutable SQLite security audit trail
    """

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.pending_confirmation: Optional[Dict[str, Any]] = None

    def get_security_level(self) -> str:
        return self.db.get_profile_field("security_level", DEFAULT_SECURITY_LEVEL)

    def set_security_level(self, level: str) -> str:
        level_upper = level.upper()
        if level_upper in ["RELAXED", "STANDARD", "STRICT"]:
            self.db.set_profile_field("security_level", level_upper)
            self.db.log_security_event(
                "SECURITY_LEVEL_CHANGE",
                f"Security policy changed to {level_upper}",
                "EXECUTED"
            )
            return f"Security level is now set to {level_upper}."
        return "Invalid security level. Please choose RELAXED, STANDARD, or STRICT."

    def check_and_execute(
        self,
        action_id: str,
        execution_callback: Callable[[], str],
        details: str = ""
    ) -> Tuple[bool, str]:
        """
        Guards an action. Returns (executed_immediately, message).
        If confirmation is needed, stages it in `self.pending_confirmation`.
        """
        sec_level = self.get_security_level()
        action_name = CRITICAL_ACTIONS.get(action_id, action_id)

        # 1. Relaxed mode: execute directly with audit log
        if sec_level == "RELAXED":
            res = execution_callback()
            self.db.log_security_event(action_id, action_name, "EXECUTED", details or res)
            return True, res

        # 2. Standard mode: only confirm destructive actions
        is_destructive = action_id in ["system_shutdown", "system_restart", "empty_recycle_bin", "clear_all_notes"]
        if sec_level == "STANDARD" and not is_destructive:
            res = execution_callback()
            self.db.log_security_event(action_id, action_name, "EXECUTED", details or res)
            return True, res

        # 3. Confirmation required (Standard destructive or Strict mode)
        self.pending_confirmation = {
            "action_id": action_id,
            "action_name": action_name,
            "callback": execution_callback,
            "details": details,
            "expires_at": time.time() + 30 # 30 seconds expiration
        }

        self.db.log_security_event(action_id, action_name, "PENDING_CONFIRMATION", details)
        return False, f"Security confirmation required: Are you sure you want to {action_name.lower()}? Say 'confirm' to proceed or 'cancel' to abort."

    def handle_confirmation_response(self, text: str) -> Optional[str]:
        """Checks if user says confirm or cancel to pending security action."""
        if not self.pending_confirmation:
            return None

        # Check expiration
        if time.time() > self.pending_confirmation["expires_at"]:
            self.db.log_security_event(
                self.pending_confirmation["action_id"],
                self.pending_confirmation["action_name"],
                "EXPIRED"
            )
            self.pending_confirmation = None
            return "Security confirmation request expired."

        cmd = text.lower().strip()
        if any(w in cmd for w in ["confirm", "yes", "proceed", "do it", "approved"]):
            action_info = self.pending_confirmation
            self.pending_confirmation = None
            # Execute callback
            res = action_info["callback"]()
            self.db.log_security_event(action_info["action_id"], action_info["action_name"], "APPROVED", res)
            return f"Action confirmed. {res}"

        if any(w in cmd for w in ["cancel", "no", "abort", "stop", "denied", "never mind"]):
            action_info = self.pending_confirmation
            self.pending_confirmation = None
            self.db.log_security_event(action_info["action_id"], action_info["action_name"], "DENIED", "Cancelled by user")
            return "Security action cancelled."

        return None
