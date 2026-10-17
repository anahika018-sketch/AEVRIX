"""
Voice Engine: Handles Speech Recognition (STT) and Speech Synthesis (TTS).
Includes robust fallbacks for Windows SAPI and keyboard input.
"""

import sys
import os
import subprocess
import config
from utils.ui import (
    print_jarvis,
    print_user,
    print_status,
    print_error,
    print_listening,
    clear_listening,
    Colors
)

# --- Text-to-Speech Engine Initialization ---
_tts_engine = None
_tts_type = "none"

try:
    import pyttsx3
    try:
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", config.VOICE_RATE)
        _tts_engine.setProperty("volume", config.VOICE_VOLUME)

        # Set voice gender if possible
        voices = _tts_engine.getProperty("voices")
        if voices:
            target_voice = None
            for v in voices:
                name_lower = v.name.lower()
                if config.VOICE_GENDER == "female" and ("zira" in name_lower or "female" in name_lower):
                    target_voice = v.id
                    break
                elif config.VOICE_GENDER == "male" and ("david" in name_lower or "male" in name_lower):
                    target_voice = v.id
                    break
            if target_voice:
                _tts_engine.setProperty("voice", target_voice)
        _tts_type = "pyttsx3"
    except Exception as e:
        print_status(f"pyttsx3 driver notice ({e}). Switching to native Windows voice engine.")
        _tts_engine = None
except ImportError:
    print_status("pyttsx3 not installed. Will use native Windows speech.")

if _tts_engine is None and os.name == "nt":
    _tts_type = "sapi"


def speak(text: str) -> None:
    """
    Speaks the given text and prints it to the console.
    """
    if not text:
        return

    print_jarvis(text)

    # Perform audio speech
    if _tts_type == "pyttsx3" and _tts_engine:
        try:
            _tts_engine.say(text)
            _tts_engine.runAndWait()
            return
        except Exception:
            pass

    # Fallback for Windows: native PowerShell SAPI voice (built-in, zero dependencies)
    if os.name == "nt":
        try:
            # Escape single quotes in text for PowerShell
            safe_text = text.replace("'", "''")
            cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_text}')"
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15
            )
        except Exception:
            pass


# --- Speech-to-Text Engine Initialization ---
_sr_module = None
_mic_available = False
_recognizer = None

try:
    import speech_recognition as sr
    _sr_module = sr
    _recognizer = sr.Recognizer()
    _recognizer.energy_threshold = config.ENERGY_THRESHOLD
    _recognizer.dynamic_energy_threshold = True

    # Test microphone availability
    try:
        with sr.Microphone() as source:
            _mic_available = True
    except Exception as mic_err:
        _mic_available = False
except ImportError:
    _sr_module = None
    _mic_available = False


class VoiceAssistant:
    def __init__(self):
        self.input_mode = config.INPUT_MODE
        if self.input_mode == "voice" and not _mic_available:
            print_status(
                "Microphone or PyAudio not detected. Switching to Text Input mode.\n"
                "Tip: To enable voice recognition, run: pip install pyaudio"
            )
            self.input_mode = "text"

    def calibrate_mic(self):
        """Calibrate microphone for ambient background noise."""
        if self.input_mode == "voice" and _mic_available and _sr_module and _recognizer:
            try:
                print_status("Calibrating microphone for ambient room noise... Please wait a second.")
                with _sr_module.Microphone() as source:
                    _recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print_status("Microphone calibrated successfully.")
            except Exception as e:
                print_error(f"Could not calibrate microphone: {e}")

    def listen(self) -> str:
        """
        Listens for audio input from the user or prompts for keyboard input.
        Returns the recognized string in lowercase.
        """
        if self.input_mode == "text" or not _mic_available:
            return self._listen_text()
        else:
            return self._listen_voice()

    def _listen_text(self) -> str:
        """Prompts for typed command in terminal."""
        try:
            user_input = input(f"{Colors.GREEN}{Colors.BOLD}[YOU - Type command]:{Colors.RESET} ").strip()
            return user_input.lower()
        except (KeyboardInterrupt, EOFError):
            return "exit"

    def _listen_voice(self) -> str:
        """Listens via microphone and recognizes with Google Speech API."""
        print_listening()
        try:
            with _sr_module.Microphone() as source:
                audio = _recognizer.listen(
                    source,
                    timeout=config.LISTEN_TIMEOUT,
                    phrase_time_limit=config.PHRASE_TIME_LIMIT
                )
            clear_listening()
            print_status("Processing audio...")

            text = _recognizer.recognize_google(audio)
            print_user(text)
            return text.lower().strip()

        except _sr_module.WaitTimeoutError:
            clear_listening()
            return ""

        except _sr_module.UnknownValueError:
            clear_listening()
            # Speech was unintelligible
            return ""

        except _sr_module.RequestError as e:
            clear_listening()
            print_error(f"Speech recognition service unreachable ({e}). Switching to text mode.")
            self.input_mode = "text"
            return ""

        except Exception as e:
            clear_listening()
            print_error(f"Microphone input error: {e}. Switching to text mode.")
            self.input_mode = "text"
            return ""

    def toggle_input_mode(self, mode: str = None) -> str:
        """Toggle or set the current input mode ('voice' or 'text')."""
        if mode in ("voice", "text"):
            self.input_mode = mode
        else:
            self.input_mode = "text" if self.input_mode == "voice" else "voice"

        if self.input_mode == "voice" and not _mic_available:
            self.input_mode = "text"
            speak("Microphone is not available on this device. Remaining in text input mode.")
        else:
            speak(f"Switched to {self.input_mode} input mode.")
        return self.input_mode

    def set_voice_gender(self, gender: str):
        """Set voice gender to 'male' or 'female' if pyttsx3 is available."""
        if _tts_engine:
            voices = _tts_engine.getProperty("voices")
            for v in voices:
                name_lower = v.name.lower()
                if gender == "female" and ("zira" in name_lower or "female" in name_lower or "hazel" in name_lower):
                    _tts_engine.setProperty("voice", v.id)
                    speak("Voice changed to female.")
                    return
                elif gender == "male" and ("david" in name_lower or "male" in name_lower or "george" in name_lower):
                    _tts_engine.setProperty("voice", v.id)
                    speak("Voice changed to male.")
                    return
        speak(f"Voice preference set to {gender}.")
