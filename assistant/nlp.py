import re
import datetime
from typing import Dict, Any, Optional, Tuple


class IntentResult:
    """Represents a classified user intent with confidence and extracted slot parameters."""
    def __init__(self, intent: str, confidence: float, category: str, slots: Dict[str, Any] = None):
        self.intent = intent
        self.confidence = confidence
        self.category = category
        self.slots = slots or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "category": self.category,
            "slots": self.slots
        }

    def __repr__(self):
        return f"<IntentResult intent='{self.intent}' confidence={self.confidence:.2f} slots={self.slots}>"


class IntentEngine:
    """
    Natural Language Understanding & Intent Classification Engine.
    Provides semantic intent classification and entity slot filling
    for the voice assistant without external model dependencies.
    """

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        # Time expression regexes for reminders
        self.rel_time_pattern = re.compile(
            r"(?:in\s+)?(?:(\d+)\s*(?:hours?|hrs?))?\s*(?:(\d+)\s*(?:minutes?|mins?))?\s*(?:(\d+)\s*(?:seconds?|secs?))?",
            re.IGNORECASE
        )
        self.at_time_pattern = re.compile(
            r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
            re.IGNORECASE
        )

    def parse(self, text: str) -> IntentResult:
        """
        Main entry point: analyzes raw user input text and returns
        the detected intent, confidence score, and extracted slots.
        """
        if not text:
            return IntentResult("UNKNOWN", 0.0, "unknown")

        cleaned = text.strip().lower()

        # 1. Exit Commands
        if any(cleaned == cmd or cleaned.startswith(cmd + " ") for cmd in ["exit", "quit", "shutdown assistant", "goodbye", "stop listening", "terminate"]):
            return IntentResult("EXIT", 1.0, "system")

        # 2. Security & High-Privilege Desktop Controls
        if any(w in cleaned for w in ["shut down my pc", "shutdown computer", "turn off computer", "power off pc"]):
            return IntentResult("SYSTEM_SHUTDOWN", 0.95, "security")

        if any(w in cleaned for w in ["restart pc", "restart computer", "reboot system", "reboot pc"]):
            return IntentResult("SYSTEM_RESTART", 0.95, "security")

        if any(w in cleaned for w in ["lock workstation", "lock screen", "lock pc", "lock computer"]):
            return IntentResult("LOCK_SCREEN", 0.95, "security")

        if any(w in cleaned for w in ["empty recycle bin", "clean recycle bin", "empty trash"]):
            return IntentResult("EMPTY_RECYCLE_BIN", 0.95, "security")

        # 3. Reminders & Alarms (Temporal extraction)
        reminder_match = self._match_reminder(cleaned)
        if reminder_match:
            return reminder_match

        if any(cleaned.startswith(p) for p in ["list reminders", "show reminders", "what are my reminders", "my reminders", "check reminders"]):
            return IntentResult("LIST_REMINDERS", 0.95, "productivity")

        if any(cleaned.startswith(p) for p in ["clear reminders", "clear all reminders", "delete reminders"]):
            return IntentResult("CLEAR_REMINDERS", 0.95, "productivity")

        # 4. Personalization & Identity
        name_match = re.search(r"(?:call me|my name is|set user name to)\s+([a-zA-Z0-9_\-\s]+)", cleaned)
        if name_match:
            user_name = name_match.group(1).strip().title()
            return IntentResult("SET_USER_NAME", 0.95, "personalization", {"user_name": user_name})

        if any(cleaned == q for q in ["what is my name", "who am i", "do you know my name"]):
            return IntentResult("GET_USER_NAME", 0.95, "personalization")

        assistant_name_match = re.search(r"(?:change your name to|your name is|rename yourself to)\s+([a-zA-Z0-9_\-\s]+)", cleaned)
        if assistant_name_match:
            new_name = assistant_name_match.group(1).strip().title()
            return IntentResult("SET_ASSISTANT_NAME", 0.95, "personalization", {"assistant_name": new_name})

        persona_match = re.search(r"(?:set personality to|change personality to|switch personality to)\s+([a-zA-Z]+)", cleaned)
        if persona_match:
            persona = persona_match.group(1).strip().capitalize()
            return IntentResult("SET_PERSONALITY", 0.95, "personalization", {"personality": persona})

        # 5. Usage Analytics
        if any(w in cleaned for w in ["usage analytics", "show analytics", "my stats", "usage stats", "how many commands", "system analytics"]):
            return IntentResult("ANALYTICS_QUERY", 0.95, "analytics")

        # 6. Security Audit Query
        if any(w in cleaned for w in ["security audit", "security logs", "show audit log", "view security logs"]):
            return IntentResult("SECURITY_LOGS_QUERY", 0.95, "security")

        # 7. Desktop Automation: Volume & Media Controls
        vol_match = self._match_volume(cleaned)
        if vol_match:
            return vol_match

        if any(w in cleaned for w in ["take screenshot", "capture screen", "screenshot", "screen shot", "take a screen shot"]):
            return IntentResult("SCREENSHOT", 0.95, "automation")

        if any(w in cleaned for w in ["media play", "media pause", "pause music", "resume music", "play pause"]):
            return IntentResult("MEDIA_PLAY_PAUSE", 0.95, "automation")

        if any(w in cleaned for w in ["next track", "next song", "skip song", "next music"]):
            return IntentResult("MEDIA_NEXT", 0.95, "automation")

        if any(w in cleaned for w in ["previous track", "previous song", "prev song"]):
            return IntentResult("MEDIA_PREV", 0.95, "automation")

        # 8. Notes Management
        note_match = self._match_note(cleaned)
        if note_match:
            return note_match

        if any(w in cleaned for w in ["read notes", "show notes", "what are my notes", "view notes", "list notes"]):
            return IntentResult("READ_NOTES", 0.95, "notes")

        if any(w in cleaned for w in ["clear notes", "delete all notes", "clear all notes"]):
            return IntentResult("CLEAR_NOTES", 0.95, "notes")

        # 9. Voice Gender Selection
        if any(w in cleaned for w in ["female voice", "voice to female", "switch to female"]):
            return IntentResult("VOICE_CHANGE", 0.95, "settings", {"gender": "female"})
        if any(w in cleaned for w in ["male voice", "voice to male", "switch to male"]):
            return IntentResult("VOICE_CHANGE", 0.95, "settings", {"gender": "male"})

        # 10. Time & Date
        if any(cleaned == q or cleaned.startswith(q) for q in ["what time is it", "tell me the time", "current time", "what's the time", "time please"]):
            return IntentResult("TIME_QUERY", 0.95, "info")
        if any(cleaned == q or cleaned.startswith(q) for q in ["what date is today", "what is today's date", "tell me the date", "what's today's date", "current date"]):
            return IntentResult("DATE_QUERY", 0.95, "info")

        # 11. Weather
        if "weather" in cleaned or "temperature" in cleaned:
            loc = self._extract_weather_location(cleaned)
            return IntentResult("WEATHER_QUERY", 0.90, "info", {"location": loc})

        # 12. App Launch
        app_match = self._match_app_launch(cleaned)
        if app_match:
            return app_match

        # 13. Web Navigation & Play
        if cleaned.startswith("play ") or "play on youtube" in cleaned or cleaned.startswith("youtube "):
            query = cleaned.replace("play on youtube", "").replace("play", "").replace("youtube", "").strip()
            return IntentResult("MEDIA_PLAY_YOUTUBE", 0.90, "web", {"query": query})

        web_match = self._match_web_open(cleaned)
        if web_match:
            return web_match

        # 14. Search Engines
        for prefix in ["search for ", "search ", "google "]:
            if cleaned.startswith(prefix):
                query = cleaned[len(prefix):].strip()
                return IntentResult("WEB_SEARCH", 0.90, "web", {"query": query})

        # 15. Math Calculation
        if any(w in cleaned for w in ["calculate", "how much is", "what is"]) and any(
            op in cleaned for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided", "multiplied"]
        ):
            return IntentResult("MATH_CALCULATION", 0.90, "math", {"expression": cleaned})

        # 16. Small Talk & Greetings
        if any(cleaned == w or cleaned.startswith(w + " ") for w in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return IntentResult("GREETING", 0.95, "conversation")

        if "how are you" in cleaned:
            return IntentResult("STATUS_QUERY", 0.90, "conversation")

        if "who are you" in cleaned or "what is your name" in cleaned:
            return IntentResult("IDENTITY_QUERY", 0.90, "conversation")

        if any(w in cleaned for w in ["help", "what can you do", "commands list", "what can i ask"]):
            return IntentResult("HELP", 0.95, "help")

        if "joke" in cleaned:
            return IntentResult("JOKE", 0.90, "fun")

        if any(w in cleaned for w in ["quote", "inspire", "motivat"]):
            return IntentResult("QUOTE", 0.90, "fun")

        if "flip a coin" in cleaned or "flip coin" in cleaned:
            return IntentResult("COIN_FLIP", 0.95, "fun")

        if "roll a dice" in cleaned or "roll dice" in cleaned:
            return IntentResult("DICE_ROLL", 0.95, "fun")

        if any(w in cleaned for w in ["system info", "system information"]):
            return IntentResult("SYSTEM_INFO", 0.95, "system")

        # Fallback to AI General Knowledge
        return IntentResult("GENERAL_AI", 0.70, "ai", {"query": cleaned})

    # =========================================================================
    # HELPER PARSERS
    # =========================================================================

    def _match_reminder(self, text: str) -> Optional[IntentResult]:
        patterns = [
            r"remind me\s+(?:to\s+)?(.+?)\s+in\s+(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)",
            r"remind me\s+in\s+(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)\s+(?:to\s+)?(.+)",
            r"set a reminder\s+(?:to\s+)?(.+?)\s+in\s+(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)",
            r"set a reminder\s+in\s+(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)\s+(?:to\s+)?(.+)"
        ]

        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                groups = m.groups()
                if len(groups) == 3:
                    if groups[1].isdigit(): # Pattern 1 & 3: task, num, unit
                        task = groups[0].strip()
                        amount = int(groups[1])
                        unit = groups[2].lower()
                    else: # Pattern 2 & 4: num, unit, task
                        amount = int(groups[0])
                        unit = groups[1].lower()
                        task = groups[2].strip()

                    delta_seconds = self._to_seconds(amount, unit)
                    due_time = datetime.datetime.now() + datetime.timedelta(seconds=delta_seconds)

                    return IntentResult("SET_REMINDER", 0.95, "productivity", {
                        "task": task,
                        "seconds": delta_seconds,
                        "due_time": due_time
                    })

        # Generic reminder without duration parsed yet
        if text.startswith("remind me to ") or text.startswith("set reminder to "):
            task = re.sub(r"^(remind me to|set reminder to)\s+", "", text).strip()
            # Default to 5 minutes
            due_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
            return IntentResult("SET_REMINDER", 0.80, "productivity", {
                "task": task,
                "seconds": 300,
                "due_time": due_time
            })

        return None

    def _to_seconds(self, amount: int, unit: str) -> int:
        if "sec" in unit:
            return amount
        if "min" in unit:
            return amount * 60
        if "hour" in unit or "hr" in unit:
            return amount * 3600
        return amount * 60

    def _match_volume(self, text: str) -> Optional[IntentResult]:
        if any(w in text for w in ["mute audio", "mute sound", "mute volume", "mute"]):
            return IntentResult("VOLUME_MUTE", 0.95, "automation", {"action": "mute"})
        if any(w in text for w in ["unmute audio", "unmute sound", "unmute volume", "unmute"]):
            return IntentResult("VOLUME_UNMUTE", 0.95, "automation", {"action": "unmute"})
        if any(w in text for w in ["volume up", "increase volume", "louder", "turn up sound"]):
            return IntentResult("VOLUME_UP", 0.95, "automation", {"action": "up"})
        if any(w in text for w in ["volume down", "decrease volume", "lower volume", "quieter"]):
            return IntentResult("VOLUME_DOWN", 0.95, "automation", {"action": "down"})

        m = re.search(r"(?:set volume to|change volume to|volume)\s+(\d{1,3})(?:\s*%)?", text)
        if m:
            level = max(0, min(100, int(m.group(1))))
            return IntentResult("VOLUME_SET", 0.95, "automation", {"action": "set", "level": level})

        return None

    def _match_note(self, text: str) -> Optional[IntentResult]:
        for prefix in ["take a note that ", "take a note ", "write down that ", "write down ", "note that ", "remember that "]:
            if text.startswith(prefix):
                content = text[len(prefix):].strip()
                return IntentResult("TAKE_NOTE", 0.95, "notes", {"content": content})
        return None

    def _match_app_launch(self, text: str) -> Optional[IntentResult]:
        apps = {
            "calculator": ["calculator", "calc"],
            "notepad": ["notepad", "text editor"],
            "chrome": ["chrome", "google chrome"],
            "edge": ["edge", "microsoft edge"],
            "terminal": ["cmd", "command prompt", "terminal", "powershell"],
            "taskmgr": ["task manager", "taskmgr", "activity monitor"],
            "explorer": ["file explorer", "explorer", "my files", "files"],
            "vscode": ["code", "vs code", "visual studio code"],
            "settings": ["windows settings", "pc settings", "settings"]
        }

        for app_id, triggers in apps.items():
            if any(text == f"open {t}" or text == f"launch {t}" or text == t for t in triggers):
                return IntentResult("APP_LAUNCH", 0.95, "automation", {"app_id": app_id})

        return None

    def _match_web_open(self, text: str) -> Optional[IntentResult]:
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "chatgpt": "https://chatgpt.com",
            "wikipedia": "https://www.wikipedia.org",
            "reddit": "https://www.reddit.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "amazon": "https://www.amazon.com",
            "instagram": "https://www.instagram.com",
            "gmail": "https://mail.google.com",
            "twitter": "https://twitter.com"
        }

        for site, url in sites.items():
            if f"open {site}" in text or text == site or f"go to {site}" in text:
                return IntentResult("WEB_OPEN", 0.95, "web", {"site": site, "url": url})

        return None

    def _extract_weather_location(self, text: str) -> str:
        m = re.search(r"(?:in|for|at)\s+([a-zA-Z\s]+)", text)
        if m:
            return m.group(1).strip()
        return ""
