import os

from dotenv import load_dotenv

from config import EXIT_COMMANDS, WAKE_WORDS
from assistant.speech import SpeechManager
from assistant.commands import CommandHandler
from assistant.ai import AIManager


def remove_wake_word(command):

    for wake_word in WAKE_WORDS:

        if command.startswith(wake_word):

            command = command[
                len(wake_word):
            ].strip()

            return command

    return command


def main():

    # Load .env
    load_dotenv()

    speech = SpeechManager()
    commands = CommandHandler()
    ai = AIManager()

    speech.speak(
        "Hello. I am Jarvis. How can I help you?"
    )

    while True:

        try:

            command = speech.listen()

            if not command:
                continue

            # Remove wake word
            command = remove_wake_word(command)

            if not command:
                speech.speak(
                    "Yes? How can I help?"
                )
                continue

            # -------------------------
            # EXIT
            # -------------------------

            if any(
                exit_command in command
                for exit_command in EXIT_COMMANDS
            ):

                speech.speak(
                    "Goodbye. Have a great day."
                )

                break

            # -------------------------
            # NORMAL COMMANDS
            # -------------------------

            response = commands.handle(command, speech)

            if response:

                speech.speak(response)

                continue

            # -------------------------
            # AI & WEB SEARCH FALLBACK
            # -------------------------

            response = ai.ask(command)
            if response:
                speech.speak(response)

        except KeyboardInterrupt:

            print("\nJARVIS stopped.")

            break

        except Exception as error:

            print("ERROR:", error)

            speech.speak(
                "Something went wrong."
            )


if __name__ == "__main__":
    main()
