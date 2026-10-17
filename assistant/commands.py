import datetime
import os
import platform
import subprocess
import webbrowser


class CommandHandler:

    def handle(self, command, speech=None):

        command = command.lower().strip()

        # -------------------------
        # VOICE SWITCHING
        # -------------------------

        if "female voice" in command or "voice to female" in command:
            if speech:
                return speech.set_voice_gender("female")
            return "Voice switched to female."

        if "male voice" in command or "voice to male" in command:
            if speech:
                return speech.set_voice_gender("male")
            return "Voice switched to male."

        # -------------------------
        # GREETINGS & SMALL TALK
        # -------------------------

        if any(w in command.split() for w in ["hello", "hi", "hey"]) or any(g in command for g in ["good morning", "good afternoon", "good evening"]):
            return "Hello! How can I assist you today?"

        if "how are you" in command:
            return "I am doing great, thank you! All systems are running smoothly. How can I help?"

        if "who are you" in command:
            return (
                "I am Jarvis, your desktop voice assistant. I can open websites and apps, "
                "tell you the time and date, check the weather, calculate math, tell jokes, and answer your questions."
            )

        # -------------------------
        # HELP & COMMANDS LIST
        # -------------------------

        if any(w in command for w in ["help", "what can you do", "commands list", "what can i ask"]):
            print("""
======================== WHAT JARVIS CAN DO ========================
 [Apps]       open chrome, open notepad, open calculator, open cmd
 [Websites]   open youtube, open google, open github, open chatgpt
 [Media]      play [song/artist], youtube [search]
 [Search]     search for [query], google [query]
 [Info]       what time is it, what date is today, weather [city]
 [Knowledge]  who is [person], what is [concept], explain [topic]
 [Math]       calculate 45 * 12, what is 100 divided by 4
 [Fun]        tell me a joke, inspire me, flip a coin, roll a dice
 [Notes]      take a note [text], read notes, clear notes
 [System]     system information, shutdown, exit
=====================================================================
""")
            return "I have printed the full list of commands on your screen. You can ask for time, weather, open apps, search the web, ask general questions, and much more."

        # -------------------------
        # JOKES & FUN
        # -------------------------

        if "joke" in command:
            import random
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "Why did the Python programmer not respond? Because they were caught in an infinite loop.",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves!",
                "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
                "Why do Java programmers wear glasses? Because they don't C sharp!"
            ]
            return random.choice(jokes)

        if any(w in command for w in ["quote", "inspire", "motivat"]):
            import random
            quotes = [
                "The secret of getting ahead is getting started. Mark Twain.",
                "It always seems impossible until it's done. Nelson Mandela.",
                "Talk is cheap. Show me the code. Linus Torvalds.",
                "The best way to predict the future is to invent it. Alan Kay.",
                "Simplicity is the soul of efficiency. Austin Freeman."
            ]
            return random.choice(quotes)

        if "flip a coin" in command or "flip coin" in command:
            import random
            return f"The coin landed on {random.choice(['Heads', 'Tails'])}."

        if "roll a dice" in command or "roll dice" in command:
            import random
            return f"You rolled a {random.randint(1, 6)}."

        # -------------------------
        # MATH CALCULATION
        # -------------------------

        if any(w in command for w in ["calculate", "how much is", "what is"]) and any(
            op in command for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided", "into", "multiplied"]
        ):
            import re
            expr = command
            for prefix in ["calculate", "what is", "how much is", "solve"]:
                expr = expr.replace(prefix, "")
            expr = (
                expr.replace("plus", "+")
                .replace("minus", "-")
                .replace("times", "*")
                .replace("multiplied by", "*")
                .replace("into", "*")
                .replace("divided by", "/")
                .replace("over", "/")
            )
            expr = re.sub(r"[^0-9+\-*/(). ]", "", expr).strip()
            if expr:
                try:
                    result = eval(expr, {"__builtins__": None}, {})
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    return f"The answer is {result}."
                except Exception:
                    pass

        # -------------------------
        # NOTES
        # -------------------------

        if any(command.startswith(p) for p in ["take a note", "write down", "note that", "remember that"]):
            content = ""
            for p in ["take a note that", "take a note", "write down that", "write down", "note that", "remember that"]:
                if command.startswith(p):
                    content = command[len(p):].strip()
                    break
            if content:
                with open("notes.txt", "a", encoding="utf-8") as f:
                    now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    f.write(f"[{now}] {content}\n")
                return f"I have saved that to your notes: {content}"
            return "What would you like me to write down?"

        if any(w in command for w in ["read notes", "show notes", "what are my notes", "view notes"]):
            if os.path.exists("notes.txt"):
                with open("notes.txt", "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                if lines:
                    recent = lines[-3:]
                    return f"You have {len(lines)} notes. Here are the latest: " + "; ".join(recent)
                return "Your notes file is empty."
            return "You don't have any notes saved yet."

        if any(w in command for w in ["clear notes", "delete notes"]):
            if os.path.exists("notes.txt"):
                with open("notes.txt", "w", encoding="utf-8") as f:
                    f.write("")
                return "All your notes have been cleared."
            return "You have no notes to clear."

        # -------------------------
        # TIME
        # -------------------------

        if "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")

            return f"The current time is {current_time}."

        # -------------------------
        # DATE
        # -------------------------

        if "date" in command:
            current_date = datetime.datetime.now().strftime(
                "%A, %d %B %Y"
            )

            return f"Today is {current_date}."

        # -------------------------
        # WEATHER
        # -------------------------

        if "weather" in command or "temperature" in command:
            import urllib.parse
            import re
            city = ""
            match = re.search(r"(?:in|for|at) ([a-zA-Z\s]+)", command)
            if match:
                city = match.group(1).strip()

            target = (
                f"https://wttr.in/{urllib.parse.quote(city)}?format=%C,+temperature+%t,+humidity+%h"
                if city
                else "https://wttr.in/?format=%C,+temperature+%t,+humidity+%h"
            )
            try:
                import requests
                resp = requests.get(target, timeout=5, headers={"User-Agent": "curl/7.68.0"})
                if resp.status_code == 200 and resp.text.strip():
                    loc = f" in {city.title()}" if city else ""
                    return f"The current weather{loc} is {resp.text.strip()}."
            except Exception:
                pass
            return "I couldn't fetch the weather right now. Please check your internet connection."

        # -------------------------
        # CALCULATOR
        # -------------------------

        if any(w in command for w in ["calculator", "calc"]):
            if platform.system() == "Windows":
                subprocess.Popen(["calc.exe"])
                return "Opening Calculator."

        # -------------------------
        # CHROME & BROWSERS
        # -------------------------

        if any(w in command for w in ["open chrome", "chrome", "google chrome"]):
            if platform.system() == "Windows":
                subprocess.Popen(["cmd.exe", "/c", "start chrome"])
                return "Opening Google Chrome."

        if any(w in command for w in ["open edge", "edge", "microsoft edge"]):
            if platform.system() == "Windows":
                subprocess.Popen(["cmd.exe", "/c", "start msedge"])
                return "Opening Microsoft Edge."

        # -------------------------
        # NOTEPAD & TOOLS
        # -------------------------

        if "notepad" in command:
            if platform.system() == "Windows":
                subprocess.Popen(["notepad.exe"])
                return "Opening Notepad."

        if any(w in command for w in ["task manager", "open task manager"]):
            if platform.system() == "Windows":
                subprocess.Popen(["taskmgr.exe"])
                return "Opening Task Manager."

        if any(w in command for w in ["command prompt", "open cmd", "terminal"]):
            if platform.system() == "Windows":
                subprocess.Popen(["cmd.exe"])
                return "Opening Command Prompt."

        # -------------------------
        # YOUTUBE
        # -------------------------

        if command.startswith("play ") or "play on youtube" in command or command.startswith("youtube "):
            query = command.replace("play on youtube", "").replace("play", "").replace("youtube", "").strip()
            if query:
                url = (
                    "https://www.youtube.com/results?search_query="
                    + query.replace(" ", "+")
                )
                webbrowser.open(url)
                return f"Searching YouTube for {query}."
            else:
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube."

        if any(w in command for w in ["open youtube", "go to youtube", "youtube"]):
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube."

        # -------------------------
        # GOOGLE
        # -------------------------

        if any(w in command for w in ["open google", "go to google"]):
            webbrowser.open("https://www.google.com")
            return "Opening Google."

        # -------------------------
        # GITHUB
        # -------------------------

        if any(w in command for w in ["open github", "go to github", "github"]):
            webbrowser.open("https://github.com")
            return "Opening GitHub."

        # -------------------------
        # COMMON WEBSITES
        # -------------------------

        web_shortcuts = {
            "chatgpt": "https://chatgpt.com",
            "wikipedia": "https://www.wikipedia.org",
            "reddit": "https://www.reddit.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "amazon": "https://www.amazon.com",
            "instagram": "https://www.instagram.com",
            "gmail": "https://mail.google.com",
            "twitter": "https://twitter.com",
        }

        for site, url in web_shortcuts.items():
            if f"open {site}" in command or command == site:
                webbrowser.open(url)
                return f"Opening {site.capitalize()}."

        if "thank you" in command or "thanks" in command:
            return "You are very welcome! Let me know if you need anything else."

        # -------------------------
        # SEARCH GOOGLE
        # -------------------------

        for prefix in ["search for ", "search ", "google "]:
            if command.startswith(prefix):
                query = command[len(prefix):].strip()
                if query:
                    url = (
                        "https://www.google.com/search?q="
                        + query.replace(" ", "+")
                    )
                    webbrowser.open(url)
                    return f"Searching Google for {query}."

        # -------------------------
        # SYSTEM INFO
        # -------------------------

        if any(w in command for w in ["system info", "system information"]):
            system = platform.system()
            version = platform.version()
            return f"You are running {system}. Version {version}."

        return None
