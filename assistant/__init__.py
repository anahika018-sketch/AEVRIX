"""
Jarvis AI Desktop Assistant Package
Modular Enterprise-Grade Voice Assistant Architecture
"""

from assistant.speech import SpeechManager
from assistant.database import DatabaseManager
from assistant.nlp import IntentEngine, IntentResult
from assistant.automation import DesktopAutomation
from assistant.reminders import ReminderService
from assistant.personalization import PersonalizationManager
from assistant.security import SecurityManager
from assistant.analytics import AnalyticsTracker
from assistant.commands import CommandHandler
from assistant.ai import AIManager

__all__ = [
    "SpeechManager",
    "DatabaseManager",
    "IntentEngine",
    "IntentResult",
    "DesktopAutomation",
    "ReminderService",
    "PersonalizationManager",
    "SecurityManager",
    "AnalyticsTracker",
    "CommandHandler",
    "AIManager"
]
