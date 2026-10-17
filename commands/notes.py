"""
Notes management commands for Jarvis:
Take quick notes, read saved notes, and clear notes.
"""

import datetime
import config
from core.voice import speak
from utils.ui import Colors

def take_note(note_text: str):
    """Save a timestamped note to notes.txt."""
    clean_text = note_text.strip()
    if not clean_text:
        speak("What would you like me to write down in your notes?")
        return

    # Strip trigger words
    for prefix in ["take a note that", "take a note", "write down that", "write down", "note that", "remember that"]:
        if clean_text.lower().startswith(prefix):
            clean_text = clean_text[len(prefix):].strip()
            break

    if not clean_text:
        speak("I didn't catch the content of the note.")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    entry = f"[{timestamp}] {clean_text}\n"

    try:
        with open(config.NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        speak(f"I have saved that to your notes: {clean_text}")
    except Exception as e:
        speak(f"Failed to save note: {e}")

def read_notes():
    """Read saved notes aloud and display them in console."""
    if not config.NOTES_FILE.exists():
        speak("You have no saved notes yet.")
        return

    try:
        with open(config.NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if not lines:
            speak("Your notes list is currently empty.")
            return

        print(f"\n{Colors.CYAN}{Colors.BOLD}=== YOUR SAVED NOTES ==={Colors.RESET}")
        for i, line in enumerate(lines, 1):
            print(f" {i}. {line}")
        print(f"{Colors.CYAN}========================{Colors.RESET}\n")

        speak(f"You have {len(lines)} notes saved. Here are your notes.")
        # Speak the last 3 most recent notes to avoid very long speeches
        recent = lines[-3:]
        for line in recent:
            # strip timestamp from speech for natural flow
            text_part = line.split("]", 1)[-1].strip() if "]" in line else line
            speak(text_part)

        if len(lines) > 3:
            speak(f"Plus {len(lines) - 3} older notes shown on your screen.")
    except Exception as e:
        speak(f"Could not read notes: {e}")

def clear_notes():
    """Clear all saved notes."""
    try:
        with open(config.NOTES_FILE, "w", encoding="utf-8") as f:
            f.write("")
        speak("All notes have been cleared.")
    except Exception as e:
        speak(f"Failed to clear notes: {e}")
