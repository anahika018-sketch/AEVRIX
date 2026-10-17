"""
System Diagnostics and Environment Checker for Jarvis.
Run this script to verify your setup:
    python check_env.py
"""

import sys
import os

print("\n" + "=" * 50)
print("     JARVIS ENVIRONMENT & DEPENDENCY CHECK")
print("=" * 50)

# 1. Python Version
py_ver = sys.version.split()[0]
print(f"[+] Python Version: {py_ver}")

# 2. Text-to-Speech (pyttsx3)
try:
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    print(f"[✓] Text-to-Speech (pyttsx3): OK ({len(voices)} voice(s) detected)")
except Exception as e:
    print(f"[!] Text-to-Speech (pyttsx3): Not available ({e}).")
    print("    -> Jarvis will automatically fall back to native Windows SAPI voice.")

# 3. Speech Recognition
try:
    import speech_recognition as sr
    print(f"[✓] SpeechRecognition: OK (v{sr.__version__})")
except ImportError:
    print("[X] SpeechRecognition: Not installed.")
    print("    -> Run: pip install SpeechRecognition")

# 4. Microphone & PyAudio
try:
    import pyaudio
    import speech_recognition as sr
    mics = sr.Microphone.list_microphone_names()
    print(f"[✓] PyAudio & Microphone: OK ({len(mics)} audio input device(s) found)")
except Exception as e:
    print(f"[!] PyAudio / Microphone: Not available ({e}).")
    print("    -> Jarvis will work in Text Input Mode.")
    print("    -> To enable microphone on Windows, run:")
    print("       pip install pipwin")
    print("       pipwin install pyaudio")

# 5. Wikipedia
try:
    import wikipedia
    print("[✓] Wikipedia API: OK")
except ImportError:
    print("[!] Wikipedia: Not installed (pip install wikipedia)")

# 6. Requests (Weather)
try:
    import requests
    print("[✓] Requests (Weather API): OK")
except ImportError:
    print("[!] Requests: Not installed (pip install requests)")

# 7. System Stats (psutil)
try:
    import psutil
    print(f"[✓] System Monitor (psutil): OK")
except ImportError:
    print("[!] psutil: Not installed (pip install psutil)")

# 8. Screenshots (Pillow)
try:
    from PIL import ImageGrab
    print("[✓] Pillow (Screenshot utility): OK")
except ImportError:
    print("[!] Pillow: Not installed (pip install pillow)")

print("=" * 50)
print("Diagnostics complete! You can run 'python main.py' to launch Jarvis.")
print("=" * 50 + "\n")
