import datetime
from typing import Dict, Any, List
from assistant.database import DatabaseManager
from config import PERSONALITIES


class PersonalizationManager:
    """
    Manages custom user identity, assistant tone/personality,
    greetings, and custom command shortcuts.
    """

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_user_name(self) -> str:
        return self.db.get_profile_field("user_name", "Sir")

    def set_user_name(self, name: str) -> str:
        self.db.set_profile_field("user_name", name)
        return f"I will address you as {name}."

    def get_assistant_name(self) -> str:
        return self.db.get_profile_field("assistant_name", "Jarvis")

    def set_assistant_name(self, name: str) -> str:
        self.db.set_profile_field("assistant_name", name)
        return f"My name is now updated to {name}."

    def get_personality(self) -> str:
        return self.db.get_profile_field("personality", "Jarvis")

    def set_personality(self, persona: str) -> str:
        if persona in PERSONALITIES:
            self.db.set_profile_field("personality", persona)
            return f"Personality mode switched to {persona}. {PERSONALITIES[persona]}"
        valid = ", ".join(PERSONALITIES.keys())
        return f"Available personalities are: {valid}."

    def generate_greeting(self) -> str:
        """Constructs a personalized greeting based on time of day, user name, and persona."""
        user = self.get_user_name()
        persona = self.get_personality()
        hour = datetime.datetime.now().hour

        if hour < 12:
            time_of_day = "Good morning"
        elif hour < 17:
            time_of_day = "Good afternoon"
        else:
            time_of_day = "Good evening"

        if persona == "Jarvis":
            return f"{time_of_day}, {user}. All systems are fully operational. How may I be of service?"
        elif persona == "Friendly":
            return f"{time_of_day}, {user}! It is wonderful to see you today. What can we do together?"
        elif persona == "Professional":
            return f"{time_of_day}, {user}. Jarvis assistant initialized and standing by for your commands."
        elif persona == "Witty":
            return f"{time_of_day}, {user}! I was resting my circuits, but for you, I am ready to work."
        return f"{time_of_day}, {user}. How can I help you today?"

    def add_alias(self, trigger: str, target: str) -> str:
        self.db.add_custom_alias(trigger, target)
        return f"Shortcut registered: Whenever you say '{trigger}', I will run '{target}'."

    def get_all_aliases(self) -> List[Dict[str, Any]]:
        return self.db.get_custom_aliases()
