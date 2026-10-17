"""
General conversational and utility commands for Jarvis:
Greetings, Time, Date, Jokes, Quotes, Calculations, and Assistant Info.
"""

import datetime
import random
import re
import config
from core.voice import speak

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the Python programmer not respond? Because they were caught in an infinite loop.",
    "There are 10 types of people in the world: those who understand binary, and those who don't.",
    "Why do Java programmers wear glasses? Because they don't C sharp!",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "What is an algorithm? Word used by programmers when they don't want to explain what they did.",
    "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves!",
    "Debugging is like being the detective in a crime movie where you are also the murderer."
]

QUOTES = [
    "The secret of getting ahead is getting started. - Mark Twain",
    "It always seems impossible until it's done. - Nelson Mandela",
    "Talk is cheap. Show me the code. - Linus Torvalds",
    "The best way to predict the future is to invent it. - Alan Kay",
    "Simplicity is the soul of efficiency. - Austin Freeman",
    "Make it work, make it right, make it fast. - Kent Beck"
]

def greet_user():
    """Greet the user based on the current hour of the day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = f"Good morning {config.USER_NAME}."
    elif 12 <= hour < 18:
        greeting = f"Good afternoon {config.USER_NAME}."
    elif 18 <= hour < 22:
        greeting = f"Good evening {config.USER_NAME}."
    else:
        greeting = f"Hello {config.USER_NAME}, working late tonight?"

    speak(f"{greeting} I am {config.ASSISTANT_NAME}. How may I assist you today?")

def get_time():
    """Announce current time."""
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}.")

def get_date():
    """Announce current date and day."""
    now = datetime.datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {now}.")

def tell_joke():
    """Tell a random joke."""
    joke = random.choice(JOKES)
    speak(joke)

def give_quote():
    """Recite an inspiring quote."""
    quote = random.choice(QUOTES)
    speak(quote)

def assistant_info():
    """Introduce Jarvis and explain capabilities."""
    info = (
        f"I am {config.ASSISTANT_NAME}, your personal desktop voice assistant built in Python. "
        "I can open websites, search Google and YouTube, summarize Wikipedia articles, "
        "check the weather, manage quick notes, check system battery and CPU, "
        "take screenshots, calculate math, tell jokes, and answer your daily questions."
    )
    speak(info)

def calculate_expression(command: str):
    """Safely calculate simple arithmetic expressions from natural speech."""
    # Clean up words to symbols
    expr = command.lower()
    for word in ["calculate", "what is", "compute", "how much is", "solve", "equals"]:
        expr = expr.replace(word, "")

    expr = expr.replace("plus", "+")
    expr = expr.replace("minus", "-")
    expr = expr.replace("times", "*")
    expr = expr.replace("multiplied by", "*")
    expr = expr.replace("into", "*")
    expr = expr.replace("divided by", "/")
    expr = expr.replace("over", "/")
    expr = expr.replace("power of", "**")
    expr = expr.replace("to the power", "**")
    expr = expr.replace("x", "*")

    # Keep only digits and safe math operators
    expr = re.sub(r"[^0-9+\-*/(). ]", "", expr).strip()

    if not expr:
        speak("I couldn't identify a valid math expression to calculate.")
        return

    try:
        # Evaluate using restricted eval
        result = eval(expr, {"__builtins__": None}, {})
        # Format floating points nicely
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        speak(f"The answer is {result}.")
    except ZeroDivisionError:
        speak("Division by zero is undefined.")
    except Exception:
        speak("Sorry, I couldn't compute that calculation.")
