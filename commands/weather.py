"""
Live Weather updates for Jarvis using the free wttr.in weather service.
Requires no API key.
"""

import urllib.parse
from core.voice import speak
from utils.ui import print_status

try:
    import requests
except ImportError:
    requests = None

def get_weather(city: str = ""):
    """Fetch and announce real-time weather information for any city."""
    if requests is None:
        speak("The requests module is needed for live weather. Please run pip install requests.")
        return

    clean_city = city.strip()
    if not clean_city:
        target_url = "https://wttr.in/?format=j1"
        display_city = "your current location"
    else:
        encoded_city = urllib.parse.quote(clean_city)
        target_url = f"https://wttr.in/{encoded_city}?format=j1"
        display_city = clean_city.title()

    speak(f"Checking current weather for {display_city}...")

    try:
        response = requests.get(target_url, timeout=6, headers={"User-Agent": "JarvisVoiceAssistant/1.0"})
        if response.status_code == 200:
            data = response.json()
            current = data.get("current_condition", [{}])[0]
            temp_c = current.get("temp_C", "unknown")
            feels_c = current.get("FeelsLikeC", "unknown")
            humidity = current.get("humidity", "unknown")
            desc_list = current.get("weatherDesc", [{}])
            description = desc_list[0].get("value", "clear") if desc_list else "clear"

            report = (
                f"In {display_city}, it is currently {description.lower()} with a temperature "
                f"of {temp_c} degrees Celsius, feels like {feels_c} degrees, "
                f"and humidity at {humidity} percent."
            )
            speak(report)
        else:
            speak(f"Could not retrieve weather data for {display_city}.")
    except Exception as e:
        speak("I was unable to connect to the weather service. Please check your internet connection.")
