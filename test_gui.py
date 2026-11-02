"""
Direct GUI Diagnostic Launcher
Verifies the Tkinter UI opens cleanly without microphone or speech delays.
"""
from assistant.database import DatabaseManager
from assistant.automation import DesktopAutomation
from assistant.reminders import ReminderService
from assistant.personalization import PersonalizationManager
from assistant.security import SecurityManager
from assistant.analytics import AnalyticsTracker
from assistant.ai import AIManager
from assistant.speech import SpeechManager
from assistant.commands import CommandHandler
from assistant.gui import JarvisGUI

def test_launch():
    print("Initializing components for GUI test...")
    db = DatabaseManager()
    automation = DesktopAutomation()
    personalization = PersonalizationManager(db)
    security = SecurityManager(db)
    analytics = AnalyticsTracker(db)
    ai = AIManager()
    speech = SpeechManager()
    reminders = ReminderService(db)
    reminders.start()

    commands = CommandHandler(
        db=db,
        automation=automation,
        reminders=reminders,
        personalization=personalization,
        security=security,
        analytics=analytics,
        ai=ai
    )

    print("Launching Jarvis GUI Dashboard window...")
    gui = JarvisGUI(
        command_handler=commands,
        speech_manager=speech,
        db=db,
        automation=automation,
        reminders=reminders,
        personalization=personalization,
        security=security,
        analytics=analytics
    )
    gui.run()
    reminders.stop()

if __name__ == "__main__":
    test_launch()
