import platform
import subprocess
import speech_recognition as sr
import pyttsx3


class SpeechManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True

        self._init_tts_engine()

        # Calibrate microphone once at startup
        try:
            with sr.Microphone() as source:
                print("Calibrating microphone for room noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("Microphone ready.")
        except Exception:
            pass

    def _init_tts_engine(self):
        """Initialize and configure pyttsx3 text-to-speech engine."""
        try:
            self.engine = pyttsx3.init()
            # 175-185 wpm is clear, natural conversational speaking rate
            self.engine.setProperty("rate", 180)
            self.engine.setProperty("volume", 1.0)

            # Choose best available voice (David or Zira)
            self.voices = self.engine.getProperty("voices")
            if self.voices:
                selected_voice = self.voices[0].id
                for v in self.voices:
                    name_lower = v.name.lower()
                    if "david" in name_lower or "zira" in name_lower:
                        selected_voice = v.id
                        break
                self.engine.setProperty("voice", selected_voice)
        except Exception as e:
            print("Notice: TTS Engine initialization:", e)
            self.engine = None
            self.voices = []

    def set_voice_gender(self, gender: str) -> str:
        """Switch assistant voice between male and female."""
        if not self.engine:
            self._init_tts_engine()

        if self.engine and self.voices:
            for v in self.voices:
                name_lower = v.name.lower()
                if gender == "female" and ("zira" in name_lower or "female" in name_lower or "hazel" in name_lower):
                    self.engine.setProperty("voice", v.id)
                    return "Voice switched to female."
                elif gender == "male" and ("david" in name_lower or "male" in name_lower or "george" in name_lower):
                    self.engine.setProperty("voice", v.id)
                    return "Voice switched to male."
        return f"Voice preference set to {gender}."

    def speak(self, text: str):
        """
        Convert text to natural speech and output to speakers.
        Guaranteed to speak aloud on Windows using multi-layer audio dispatch.
        """
        if not text:
            return

        print(f"\nAEVRIX: {text}")

        # Method 1: Try fast in-process Windows SAPI voice (COM)
        if platform.system() == "Windows":
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Volume = 100
                speaker.Rate = 1
                speaker.Speak(text)
                return
            except Exception:
                pass

        # Method 2: Try pyttsx3
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception:
                try:
                    self._init_tts_engine()
                    if self.engine:
                        self.engine.say(text)
                        self.engine.runAndWait()
                        return
                except Exception:
                    pass

        # Method 3: Windows PowerShell native SpeechSynthesizer (always plays to active audio device)
        if platform.system() == "Windows":
            try:
                safe_text = text.replace("'", "''").replace('"', '`"')
                cmd = f"Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Volume = 100; $synth.Rate = 1; $synth.Speak('{safe_text}')"
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=15
                )
            except Exception:
                pass

    def listen(self) -> str:
        """Listen to microphone and convert speech to text."""
        try:
            with sr.Microphone() as source:
                print("\nListening... (speak now)")

                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=7,
                        phrase_time_limit=10
                    )
                except sr.WaitTimeoutError:
                    return ""

            try:
                print("Recognizing...")
                text = self.recognizer.recognize_google(audio)
                text = text.lower().strip()
                print(f"You: {text}")
                return text

            except sr.UnknownValueError:
                print("I couldn't understand that clearly. Please try again.")
                return ""

            except sr.RequestError:
                print("Speech recognition service is unavailable (check internet connection).")
                return ""

        except (OSError, AttributeError) as mic_err:
            # Fallback when microphone or PyAudio is not available or not configured
            print(f"\n[Microphone unavailable: {mic_err}]")
            print("[Type your command below instead]:")
            try:
                text = input("You: ").strip().lower()
                return text
            except (KeyboardInterrupt, EOFError):
                return "exit"
