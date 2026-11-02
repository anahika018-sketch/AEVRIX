import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = os.path.join(BASE_DIR, "jarvis.db")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
NOTES_FILE = os.path.join(BASE_DIR, "notes.txt")

# Ensure necessary directories exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Assistant Identity Defaults
DEFAULT_ASSISTANT_NAME = "Jarvis"
DEFAULT_USER_NAME = "Sir"
WAKE_WORDS = [
    "jarvis",
    "hey jarvis",
    "aevrix",
    "hey aevrix",
    "assistant"
]

EXIT_COMMANDS = [
    "exit",
    "quit",
    "shutdown",
    "goodbye",
    "stop listening",
    "close"
]

# Security Settings
# Levels: "RELAXED" (auto-approve), "STANDARD" (confirm destructive), "STRICT" (confirm all system/desktop actions)
DEFAULT_SECURITY_LEVEL = "STANDARD"

CRITICAL_ACTIONS = {
    "system_shutdown": "Shut down the computer",
    "system_restart": "Restart the computer",
    "system_sleep": "Put the computer to sleep",
    "lock_workstation": "Lock the workstation screen",
    "empty_recycle_bin": "Permanently empty the Recycle Bin",
    "clear_all_notes": "Delete all saved notes",
    "clear_database": "Reset the assistant database",
    "run_terminal_command": "Execute command in terminal"
}

# Personalities
PERSONALITIES = {
    "Jarvis": "Concise, polite, highly efficient, and respectful AI assistant.",
    "Friendly": "Warm, enthusiastic, cheerful, and encouraging companion.",
    "Professional": "Formal, objective, crisp, and direct executive assistant.",
    "Witty": "Clever, humorous, sarcastic with playful banter."
}

# GUI Dashboard Settings
GUI_TITLE = "JARVIS AI // Advanced Desktop Assistant"
GUI_THEME = "dark"
GUI_ACCENT_COLOR = "#00d2ff"
GUI_BG_DARK = "#0a0f18"
GUI_CARD_BG = "#121b2a"
GUI_TEXT_COLOR = "#e2e8f0"
