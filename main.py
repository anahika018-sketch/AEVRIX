import sys
from dotenv import load_dotenv

from config import EXIT_COMMANDS, WAKE_WORDS
from assistant.database import DatabaseManager
from assistant.automation import DesktopAutomation
from assistant.reminders import ReminderService
from assistant.personalization import PersonalizationManager
from assistant.security import SecurityManager
from assistant.analytics import AnalyticsTracker
from assistant.ai import AIManager
from assistant.speech import SpeechManager
from assistant.commands import CommandHandler


def remove_wake_word(command: str) -> str:
    for wake_word in WAKE_WORDS:
        if command.startswith(wake_word):
            command = command[len(wake_word):].strip()
            return command
    return command


def run_cli_loop(commands: CommandHandler, speech: SpeechManager, personalization: PersonalizationManager, reminders: ReminderService):
    """Headless voice-activated CLI loop."""
    user_name = personalization.get_user_name()
    asst_name = personalization.get_assistant_name()
    greeting = personalization.generate_greeting()

    print(f"\n========================================================")
    print(f"       {asst_name.upper()} AI ASSISTANT // CLI MODE")
    print(f"========================================================")
    print(f"User: {user_name} | Persona: {personalization.get_personality()}")
    print("Voice activation active. Speak your command or type 'exit'.\n")

    speech.speak(greeting)

    while True:
        try:
            raw_spoken = speech.listen()
            if not raw_spoken:
                continue

            command = remove_wake_word(raw_spoken)
            if not command:
                speech.speak("Yes? I am listening.")
                continue

            # Exit Check
            if any(exit_cmd == command or command.startswith(exit_cmd + " ") for exit_cmd in EXIT_COMMANDS):
                bye = f"Goodbye, {user_name}. Have a productive day."
                print(f"\n{asst_name}: {bye}")
                speech.speak(bye)
                break

            # Execute via Unified Command Pipeline
            response = commands.handle(command, speech)
            if response:
                speech.speak(response)

        except KeyboardInterrupt:
            print(f"\n{asst_name} stopped by user.")
            break
        except Exception as e:
            print("System Exception:", e)
            speech.speak("An unexpected error occurred.")

    reminders.stop()


def main():
    load_dotenv()

    # 1. Option: CLI Terminal Mode
    if "--cli" in sys.argv or "--terminal" in sys.argv:
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
        run_cli_loop(commands, speech, personalization, reminders)
        return

    # 2. Option: Tkinter Desktop Window Mode
    if "--desktop" in sys.argv or "--gui" in sys.argv:
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
        from assistant.gui import JarvisGUI
        app = JarvisGUI(
            command_handler=commands,
            speech_manager=speech,
            db=db,
            automation=automation,
            reminders=reminders,
            personalization=personalization,
            security=security,
            analytics=analytics
        )
        app.run()
        reminders.stop()
        return

    # 3. Default: Launch Modern ChatGPT / Gemini-Style Dark Web Frontend
    from server import start_server
    start_server(port=5000, auto_open=True)


if __name__ == "__main__":
    main()
