import os
import time
import datetime
import webbrowser
from typing import Optional

from assistant.database import DatabaseManager
from assistant.nlp import IntentEngine, IntentResult
from assistant.automation import DesktopAutomation
from assistant.reminders import ReminderService
from assistant.personalization import PersonalizationManager
from assistant.security import SecurityManager
from assistant.analytics import AnalyticsTracker
from assistant.ai import AIManager


class CommandHandler:
    """
    Unified Command Orchestrator:
    Binds Intent Understanding, Desktop Automation, Reminders, SQLite Persistence,
    Personalization, Security/Permissions, and Analytics into a single pipeline.
    """

    def __init__(
        self,
        db: DatabaseManager,
        automation: DesktopAutomation,
        reminders: ReminderService,
        personalization: PersonalizationManager,
        security: SecurityManager,
        analytics: AnalyticsTracker,
        ai: AIManager
    ):
        self.db = db
        self.automation = automation
        self.reminders = reminders
        self.personalization = personalization
        self.security = security
        self.analytics = analytics
        self.ai = ai
        self.nlp = IntentEngine()

    def handle(self, command: str, speech=None) -> Optional[str]:
        if not command:
            return None

        start_time = time.time()
        raw_input = command.strip()

        # 1. Check for Pending Security Confirmations ("confirm" / "cancel")
        sec_response = self.security.handle_confirmation_response(raw_input)
        if sec_response:
            self.analytics.record_turn(raw_input, "SECURITY_CONFIRMATION", "security", start_time, True)
            return sec_response

        # 2. Check Custom Command Aliases
        alias_target = self.db.resolve_alias(raw_input)
        if alias_target:
            raw_input = alias_target

        # 3. Intent Understanding & Slot Extraction
        intent_res: IntentResult = self.nlp.parse(raw_input)
        intent = intent_res.intent
        category = intent_res.category
        slots = intent_res.slots

        response_text = ""
        success = True

        try:
            # ---------------------------------------------------------
            # EXIT
            # ---------------------------------------------------------
            if intent == "EXIT":
                user = self.personalization.get_user_name()
                response_text = f"Goodbye, {user}. Shutting down services."

            # ---------------------------------------------------------
            # GREETINGS & PERSONALIZATION
            # ---------------------------------------------------------
            elif intent == "GREETING":
                response_text = self.personalization.generate_greeting()

            elif intent == "SET_USER_NAME":
                user_name = slots.get("user_name", "Sir")
                response_text = self.personalization.set_user_name(user_name)

            elif intent == "GET_USER_NAME":
                user = self.personalization.get_user_name()
                response_text = f"You are {user}."

            elif intent == "SET_ASSISTANT_NAME":
                name = slots.get("assistant_name", "Jarvis")
                response_text = self.personalization.set_assistant_name(name)

            elif intent == "SET_PERSONALITY":
                persona = slots.get("personality", "Jarvis")
                response_text = self.personalization.set_personality(persona)

            elif intent == "IDENTITY_QUERY":
                asst_name = self.personalization.get_assistant_name()
                user = self.personalization.get_user_name()
                persona = self.personalization.get_personality()
                response_text = (
                    f"I am {asst_name}, your desktop AI assistant configured in {persona} mode for {user}. "
                    "I feature desktop automation, reminders, intent parsing, analytics, and security controls."
                )

            elif intent == "STATUS_QUERY":
                user = self.personalization.get_user_name()
                diag = self.automation.get_system_diagnostics()
                battery = diag.get("battery_percent", "")
                bat_str = f" Battery is at {battery}." if battery and battery != "N/A" else ""
                response_text = f"All systems are functioning nominally, {user}.{bat_str} Ready for your commands."

            # ---------------------------------------------------------
            # REMINDERS & ALARMS
            # ---------------------------------------------------------
            elif intent == "SET_REMINDER":
                task = slots.get("task", "Reminder")
                due_time = slots.get("due_time", datetime.datetime.now() + datetime.timedelta(minutes=5))
                rem_info = self.reminders.create_reminder(task, due_time)
                response_text = f"Reminder set: I will alert you to '{task}' at {rem_info['formatted_time']}."

            elif intent == "LIST_REMINDERS":
                rems = self.reminders.get_active_reminders()
                pending = [r for r in rems if r["status"] == "pending"]
                if not pending:
                    response_text = "You have no pending reminders."
                else:
                    titles = [f"'{r['title']}' at {r['remind_at'][11:16]}" for r in pending[:4]]
                    response_text = f"You have {len(pending)} active reminders: " + "; ".join(titles)

            elif intent == "CLEAR_REMINDERS":
                self.reminders.clear_all()
                response_text = "Cleared all completed reminders."

            # ---------------------------------------------------------
            # NOTES
            # ---------------------------------------------------------
            elif intent == "TAKE_NOTE":
                content = slots.get("content", "")
                if content:
                    self.db.add_note(content)
                    response_text = f"Saved to your notes: '{content}'."
                else:
                    response_text = "What note would you like me to record?"

            elif intent == "READ_NOTES":
                recent = self.db.get_recent_notes(limit=3)
                if not recent:
                    response_text = "Your notes are currently empty."
                else:
                    items = [f"'{n['content']}'" for n in recent]
                    response_text = f"Here are your latest notes: " + "; ".join(items)

            elif intent == "CLEAR_NOTES":
                # Security Gated Action
                _, msg = self.security.check_and_execute(
                    "clear_all_notes",
                    lambda: f"Cleared {self.db.clear_all_notes()} notes.",
                    "User requested to wipe all saved notes"
                )
                response_text = msg

            # ---------------------------------------------------------
            # DESKTOP AUTOMATION: VOLUME & MEDIA
            # ---------------------------------------------------------
            elif intent == "VOLUME_MUTE":
                response_text = self.automation.mute_volume()

            elif intent == "VOLUME_UNMUTE":
                response_text = self.automation.mute_volume()

            elif intent == "VOLUME_UP":
                response_text = self.automation.volume_up()

            elif intent == "VOLUME_DOWN":
                response_text = self.automation.volume_down()

            elif intent == "VOLUME_SET":
                level = slots.get("level", 50)
                response_text = self.automation.set_volume_percent(level)

            elif intent == "MEDIA_PLAY_PAUSE":
                response_text = self.automation.media_play_pause()

            elif intent == "MEDIA_NEXT":
                response_text = self.automation.media_next()

            elif intent == "MEDIA_PREV":
                response_text = self.automation.media_prev()

            elif intent == "SCREENSHOT":
                ok, path = self.automation.take_screenshot()
                if ok:
                    filename = os.path.basename(path)
                    response_text = f"Screenshot saved as {filename}."
                else:
                    response_text = path

            # ---------------------------------------------------------
            # SECURITY & HIGH-PRIVILEGE SYSTEM ACTIONS
            # ---------------------------------------------------------
            elif intent == "LOCK_SCREEN":
                _, msg = self.security.check_and_execute(
                    "lock_workstation",
                    self.automation.lock_workstation,
                    "Lock workstation screen"
                )
                response_text = msg

            elif intent == "EMPTY_RECYCLE_BIN":
                _, msg = self.security.check_and_execute(
                    "empty_recycle_bin",
                    self.automation.empty_recycle_bin,
                    "Purge Recycle Bin"
                )
                response_text = msg

            elif intent == "SYSTEM_SHUTDOWN":
                _, msg = self.security.check_and_execute(
                    "system_shutdown",
                    self.automation.shutdown_system,
                    "System shutdown requested"
                )
                response_text = msg

            elif intent == "SYSTEM_RESTART":
                _, msg = self.security.check_and_execute(
                    "system_restart",
                    self.automation.restart_system,
                    "System reboot requested"
                )
                response_text = msg

            elif intent == "SECURITY_LOGS_QUERY":
                logs = self.db.get_security_audit_logs(limit=3)
                if not logs:
                    response_text = "No security events logged yet."
                else:
                    recent = [f"{l['action']} ({l['status']})" for l in logs]
                    sec_level = self.security.get_security_level()
                    response_text = f"Security level is {sec_level}. Recent events: " + ", ".join(recent)

            # ---------------------------------------------------------
            # USAGE ANALYTICS
            # ---------------------------------------------------------
            elif intent == "ANALYTICS_QUERY":
                response_text = self.analytics.get_spoken_summary()

            # ---------------------------------------------------------
            # APP LAUNCHER & WEB NAVIGATION
            # ---------------------------------------------------------
            elif intent == "APP_LAUNCH":
                app_id = slots.get("app_id", "")
                response_text = self.automation.launch_app(app_id)

            elif intent == "WEB_OPEN":
                site = slots.get("site", "")
                url = slots.get("url", "https://google.com")
                webbrowser.open(url)
                response_text = f"Opening {site.capitalize()}."

            elif intent == "MEDIA_PLAY_YOUTUBE":
                query = slots.get("query", "")
                if query:
                    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    webbrowser.open(url)
                    response_text = f"Playing {query} on YouTube."
                else:
                    webbrowser.open("https://www.youtube.com")
                    response_text = "Opening YouTube."

            elif intent == "WEB_SEARCH":
                query = slots.get("query", "")
                if query:
                    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
                    response_text = f"Searching Google for {query}."

            # ---------------------------------------------------------
            # TIME, DATE & WEATHER
            # ---------------------------------------------------------
            elif intent == "TIME_QUERY":
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                response_text = f"The time is {current_time}."

            elif intent == "DATE_QUERY":
                current_date = datetime.datetime.now().strftime("%A, %d %B %Y")
                response_text = f"Today is {current_date}."

            elif intent == "WEATHER_QUERY":
                loc = slots.get("location", "")
                if not loc:
                    loc = self.db.get_profile_field("default_city", "London")
                response_text = self._fetch_weather(loc)

            # ---------------------------------------------------------
            # MATH CALCULATION
            # ---------------------------------------------------------
            elif intent == "MATH_CALCULATION":
                expr = slots.get("expression", "")
                response_text = self._evaluate_math(expr)

            # ---------------------------------------------------------
            # VOICE CONFIGURATION
            # ---------------------------------------------------------
            elif intent == "VOICE_CHANGE":
                gender = slots.get("gender", "male")
                if speech:
                    response_text = speech.set_voice_gender(gender)
                else:
                    response_text = f"Voice preference changed to {gender}."

            # ---------------------------------------------------------
            # HELP & UTILITIES
            # ---------------------------------------------------------
            elif intent == "HELP":
                response_text = (
                    "Available features: Voice recognition, Intent understanding, Desktop automation "
                    "(volume, screenshots, app launching), SQLite notes and reminders, Personalization, "
                    "Security permissions, and live Usage Analytics."
                )

            elif intent == "JOKE":
                import random
                jokes = [
                    "Why do programmers prefer dark mode? Because light attracts bugs!",
                    "Why did the Python programmer not respond? Because they were caught in an infinite loop.",
                    "There are 10 types of people in the world: those who understand binary, and those who don't.",
                    "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves!"
                ]
                response_text = random.choice(jokes)

            elif intent == "QUOTE":
                import random
                quotes = [
                    "The secret of getting ahead is getting started. Mark Twain.",
                    "Talk is cheap. Show me the code. Linus Torvalds.",
                    "Simplicity is the soul of efficiency. Austin Freeman."
                ]
                response_text = random.choice(quotes)

            elif intent == "COIN_FLIP":
                import random
                response_text = f"The coin landed on {random.choice(['Heads', 'Tails'])}."

            elif intent == "DICE_ROLL":
                import random
                response_text = f"You rolled a {random.randint(1, 6)}."

            elif intent == "SYSTEM_INFO":
                diag = self.automation.get_system_diagnostics()
                response_text = f"Operating System: {diag['os']}. Architecture: {diag['machine']}."

            # ---------------------------------------------------------
            # FALLBACK: MULTI-TIER AI
            # ---------------------------------------------------------
            else:
                ai_answer = self.ai.ask(raw_input)
                response_text = ai_answer or "I could not find an answer to that."

        except Exception as err:
            success = False
            response_text = f"An error occurred while executing command: {err}"

        # Record Interaction in Usage Analytics
        self.analytics.record_turn(raw_input, intent, category, start_time, success)

        return response_text

    def _evaluate_math(self, expr: str) -> str:
        import re
        for p in ["calculate", "what is", "how much is", "solve"]:
            expr = expr.replace(p, "")
        expr = (
            expr.replace("plus", "+")
            .replace("minus", "-")
            .replace("times", "*")
            .replace("multiplied by", "*")
            .replace("into", "*")
            .replace("divided by", "/")
            .replace("over", "/")
        )
        clean_expr = re.sub(r"[^0-9+\-*/(). ]", "", expr).strip()
        if clean_expr:
            try:
                res = eval(clean_expr, {"__builtins__": None}, {})
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                return f"The answer is {res}."
            except Exception:
                pass
        return "I could not calculate that mathematical expression."

    def _fetch_weather(self, city: str) -> str:
        import urllib.parse
        import requests
        target = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C,+temperature+%t,+humidity+%h"
        try:
            resp = requests.get(target, timeout=4, headers={"User-Agent": "curl/7.68.0"})
            if resp.status_code == 200 and resp.text.strip():
                return f"Weather for {city.title()}: {resp.text.strip()}."
        except Exception:
            pass
        return f"Could not fetch weather data for {city} right now."
