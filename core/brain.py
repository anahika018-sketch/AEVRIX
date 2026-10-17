"""
Brain of Jarvis:
Parses user commands, recognizes intents, routes actions, and provides helpful responses.
"""

import re
import config
from core.voice import speak, VoiceAssistant
from commands import general, web, weather, system, notes
from utils.ui import Colors

def display_help():
    """Print and speak available commands."""
    help_text = f"""
{Colors.CYAN}{Colors.BOLD}==================== JARVIS COMMANDS GUIDE ===================={Colors.RESET}
 {Colors.GREEN}● General:{Colors.RESET}
   - "hello" / "how are you" / "who are you"
   - "what time is it" / "what is today's date"
   - "tell me a joke" / "give me a quote"
   - "calculate 45 * 12" / "what is 120 divided by 4"

 {Colors.GREEN}● Web & Media:{Colors.RESET}
   - "open youtube" / "open google" / "open github" / "open chatgpt"
   - "play bohemian rhapsody" / "youtube lofi hip hop"
   - "search for machine learning tutorials" / "google best sci-fi movies"
   - "who is albert einstein" / "wikipedia artificial intelligence"

 {Colors.GREEN}● Information & Weather:{Colors.RESET}
   - "weather" / "weather in London" / "weather in Tokyo"

 {Colors.GREEN}● Productivity & Notes:{Colors.RESET}
   - "take a note buy groceries" / "remember that meeting at 3pm"
   - "read notes" / "show my notes"
   - "clear notes"

 {Colors.GREEN}● System Control:{Colors.RESET}
   - "battery" / "system stats" / "cpu usage"
   - "take screenshot"
   - "lock computer" / "lock screen"
   - "open notepad" / "open calculator" / "open cmd"

 {Colors.GREEN}● Assistant Settings:{Colors.RESET}
   - "switch to text mode" / "switch to voice mode"
   - "set voice to female" / "set voice to male"
   - "exit" / "quit" / "bye"
{Colors.CYAN}{Colors.BOLD}================================================================{Colors.RESET}
"""
    print(help_text)
    speak("Here are the commands you can give me. You can ask for time, search the web, check weather, take notes, and more.")


def clean_command(command: str) -> str:
    """Remove wake words and normalize punctuation."""
    cmd = command.strip().lower()
    for wake in config.WAKE_WORDS:
        if cmd.startswith(wake):
            cmd = cmd[len(wake):].strip()
            break
    # Remove leading/trailing punctuation
    cmd = cmd.strip(",.!? ")
    return cmd


def process_command(raw_command: str, assistant: VoiceAssistant) -> bool:
    """
    Routes the user command to the appropriate handler.
    Returns:
        bool: False if assistant should exit, True to continue listening.
    """
    if not raw_command:
        return True

    cmd = clean_command(raw_command)
    if not cmd:
        return True

    # 1. Exit Commands
    if cmd in ["exit", "quit", "bye", "goodbye", "stop", "terminate", "shutdown", "close"]:
        speak(f"Goodbye {config.USER_NAME}. Have a wonderful day ahead!")
        return False

    # 2. Help Commands
    if cmd in ["help", "commands", "options", "what can you do", "help me"]:
        display_help()
        return True

    # 3. Mode & Voice Settings
    if "text mode" in cmd or "switch to text" in cmd:
        assistant.toggle_input_mode("text")
        return True

    if "voice mode" in cmd or "switch to voice" in cmd:
        assistant.toggle_input_mode("voice")
        return True

    if "female voice" in cmd or "change voice to female" in cmd:
        assistant.set_voice_gender("female")
        return True

    if "male voice" in cmd or "change voice to male" in cmd:
        assistant.set_voice_gender("male")
        return True

    # 4. Greetings and Small Talk
    if cmd in ["hello", "hi", "hey", "greetings"]:
        general.greet_user()
        return True

    if "how are you" in cmd:
        speak(f"All systems are operational and running at peak performance, {config.USER_NAME}. How can I assist you?")
        return True

    if "who are you" in cmd or "what is your name" in cmd:
        general.assistant_info()
        return True

    if "thank you" in cmd or "thanks" in cmd:
        speak(f"You're very welcome, {config.USER_NAME}! Always here to help.")
        return True

    # 5. Time and Date
    if any(q in cmd for q in ["what time", "current time", "the time", "time please"]):
        general.get_time()
        return True

    if any(q in cmd for q in ["what is today's date", "what date", "today's date", "what day is today", "what day is it"]):
        general.get_date()
        return True

    # 6. Jokes & Quotes
    if "joke" in cmd:
        general.tell_joke()
        return True

    if "quote" in cmd or "inspire" in cmd or "motivat" in cmd:
        general.give_quote()
        return True

    # 7. Math Calculations
    if any(cmd.startswith(prefix) for prefix in ["calculate", "what is", "compute", "solve"]) and any(
        op in cmd for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided", "multiplied", "into"]
    ):
        general.calculate_expression(cmd)
        return True

    # 8. Weather
    if "weather" in cmd or "temperature" in cmd:
        city = ""
        match = re.search(r"weather (?:in|for|at) ([a-zA-Z\s]+)", cmd)
        if match:
            city = match.group(1).strip()
        weather.get_weather(city)
        return True

    # 9. Notes Management
    if any(cmd.startswith(p) for p in ["take a note", "write down", "note that", "remember that"]):
        notes.take_note(cmd)
        return True

    if any(phrase in cmd for phrase in ["read notes", "show notes", "my notes", "view notes", "list notes"]):
        notes.read_notes()
        return True

    if "clear notes" in cmd or "delete notes" in cmd:
        notes.clear_notes()
        return True

    # 10. System Commands
    if "battery" in cmd:
        system.get_battery_status()
        return True

    if "cpu" in cmd or "system stats" in cmd or "ram" in cmd or "memory usage" in cmd:
        system.get_system_stats()
        return True

    if "screenshot" in cmd or "capture screen" in cmd:
        system.take_screenshot()
        return True

    if "lock screen" in cmd or "lock computer" in cmd or "lock pc" in cmd or "lock workstation" in cmd:
        system.lock_screen()
        return True

    # 11. Media / YouTube
    if cmd.startswith("play ") or "play on youtube" in cmd or cmd.startswith("youtube "):
        query = cmd.replace("play on youtube", "").replace("play", "").replace("youtube", "").strip()
        web.play_youtube(query)
        return True

    # 12. Open Application or Website
    if cmd.startswith("open "):
        target = cmd[5:].strip()

        # Check desktop apps first (notepad, calc, cmd, etc.)
        if system.launch_app(target):
            return True

        # Check known web shortcuts or domain
        if web.open_website(target):
            return True

        # If not known, treat as Google search or open site
        speak(f"Searching web for {target}.")
        web.search_google(target)
        return True

    # 13. Search Google
    if cmd.startswith("search for ") or cmd.startswith("search ") or cmd.startswith("google "):
        query = cmd.replace("search for", "").replace("search", "").replace("google", "").strip()
        web.search_google(query)
        return True

    # 14. Wikipedia / Information
    if cmd.startswith("wikipedia "):
        query = cmd[10:].strip()
        web.search_wikipedia(query)
        return True

    if cmd.startswith("who is ") or cmd.startswith("who was ") or cmd.startswith("tell me about ") or cmd.startswith("what is "):
        # Remove trigger
        for p in ["who is", "who was", "tell me about", "what is"]:
            if cmd.startswith(p):
                query = cmd[len(p):].strip()
                break
        web.search_wikipedia(query)
        return True

    # 15. Fallback for unrecognized commands
    speak(f"I'm not sure how to handle '{cmd}'. Would you like me to search Google for it?")
    user_choice = input(f"{Colors.YELLOW}[SYSTEM] Search Google for '{cmd}'? (y/n): {Colors.RESET}").strip().lower()
    if user_choice in ["y", "yes"]:
        web.search_google(cmd)

    return True
