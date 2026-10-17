"""
Web and Search commands for Jarvis:
Opening websites, Google search, YouTube play, and Wikipedia summaries.
"""

import webbrowser
import urllib.parse
import config
from core.voice import speak
from utils.ui import print_status

# Try to import wikipedia
try:
    import wikipedia
except ImportError:
    wikipedia = None

def open_website(site_name: str) -> bool:
    """Open known shortcut website or URL."""
    site_key = site_name.strip().lower()

    if site_key in config.WEB_SHORTCUTS:
        url = config.WEB_SHORTCUTS[site_key]
        speak(f"Opening {site_name}.")
        webbrowser.open(url)
        return True

    # If it's a domain name (e.g. reddit.com or https://...)
    if site_key.startswith("http://") or site_key.startswith("https://"):
        speak(f"Opening {site_name}.")
        webbrowser.open(site_key)
        return True

    if "." in site_key and not " " in site_key:
        speak(f"Opening {site_name}.")
        webbrowser.open(f"https://{site_key}")
        return True

    return False

def search_google(query: str):
    """Perform a Google search."""
    clean_query = query.strip()
    if not clean_query:
        speak("What would you like me to search for on Google?")
        return

    encoded = urllib.parse.quote(clean_query)
    url = f"https://www.google.com/search?q={encoded}"
    speak(f"Searching Google for {clean_query}.")
    webbrowser.open(url)

def play_youtube(query: str):
    """Search and play videos or music on YouTube."""
    clean_query = query.strip()
    if not clean_query:
        speak("What video or music would you like to play on YouTube?")
        return

    encoded = urllib.parse.quote(clean_query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    speak(f"Searching YouTube for {clean_query}.")
    webbrowser.open(url)

def search_wikipedia(query: str):
    """Fetch a concise 2-sentence summary from Wikipedia."""
    clean_query = query.strip()
    if not clean_query:
        speak("What topic would you like to look up on Wikipedia?")
        return

    if wikipedia is None:
        speak("Wikipedia package is not installed. Performing a Google search instead.")
        search_google(clean_query)
        return

    speak(f"Searching Wikipedia for {clean_query}...")
    try:
        # Set language
        wikipedia.set_lang("en")
        summary = wikipedia.summary(clean_query, sentences=2, auto_suggest=True)
        speak(summary)
    except wikipedia.DisambiguationError as e:
        options = e.options[:3]
        speak(f"There are multiple topics matching '{clean_query}'. For example: {', '.join(options)}. Please be more specific.")
    except wikipedia.PageError:
        speak(f"I couldn't find a Wikipedia page for '{clean_query}'. Searching Google instead.")
        search_google(clean_query)
    except Exception as e:
        speak("Sorry, I had trouble reaching Wikipedia.")
        search_google(clean_query)
