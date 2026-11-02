# JARVIS AI: Advanced Desktop Voice & Intelligence Assistant 🎙️⚡

An enterprise-grade, modular desktop voice assistant featuring **Natural Language Intent Understanding**, **Windows Desktop Automation**, **Scheduled Reminders**, **SQLite Persistence**, **Personalization & Custom Personas**, a **Futuristic Dark GUI Dashboard**, **Usage Analytics**, and a **Security & Permission Layer**.

---

## 📁 1. Project Architecture & Structure

```text
jarvis/
│
├── main.py                  # Main entry point (GUI Dashboard or CLI mode)
├── config.py                # Configuration constants, paths & security policies
├── requirements.txt         # Project Python dependencies
├── run.bat                  # Single-click Windows runner & environment builder
├── jarvis.db                # SQLite database (auto-generated on first launch)
├── .env                     # Optional OpenAI API key
├── README.md                # Complete documentation
├── SYNOPSIS.md              # Project synopsis & academic report
│
├── screenshots/             # Auto-saved screenshot captures
│
└── assistant/
    ├── __init__.py          # Package exports
    ├── speech.py            # Speech recognition & multi-tier TTS engine
    ├── nlp.py               # Intent understanding & slot extraction engine
    ├── database.py          # SQLite database manager (Profile, Notes, Reminders, Logs)
    ├── automation.py        # Desktop automation (volume, media, lock screen, apps)
    ├── reminders.py         # Background reminder daemon & alert system
    ├── personalization.py   # Profile manager, personalized greetings & aliases
    ├── security.py          # Two-step confirmation layer & security audit logging
    ├── analytics.py         # Usage analytics & telemetry tracking
    ├── commands.py          # Unified command handler & orchestrator
    ├── ai.py                # Multi-tier fallback AI (GPT, Pollinations, Wikipedia, DDG)
    └── gui.py               # Modern Cyberpunk Tkinter GUI Dashboard
```

---

## 🚀 2. Core Implemented Features

### 1. 🧠 Intent Understanding & NLP (`assistant/nlp.py`)
- Analyzes commands semantically using regex and tokenized slot-filling.
- Extracts parameters like durations (`"remind me in 15 minutes to call David"`), volume levels (`"set volume to 60%"`), application names, and search queries.

### 2. 🖥️ Native Desktop Automation (`assistant/automation.py`)
- **Audio Controls**: Mute, unmute, volume up, volume down, set exact percentage.
- **Media Keys**: Play/pause, next track, previous track via Windows virtual keys.
- **Screen & System**: Screenshot capture saved to `screenshots/`, lock workstation, empty Recycle Bin.
- **App Launchers**: Chrome, Edge, VS Code, Notepad, Calculator, Task Manager, File Explorer, Command Prompt.

### 3. ⏰ Scheduled Reminders (`assistant/reminders.py`)
- Background daemon thread checking due reminders from SQLite every 3 seconds.
- Spoken voice notification + visual alert on the GUI console when a reminder triggers.
- Full SQLite persistence across restarts.

### 4. 🗄️ SQLite Database Persistence (`assistant/database.py`)
- Stores user profile settings, saved notes, pending & completed reminders, interaction analytics, and security audit logs in `jarvis.db`.

### 5. 🎭 Personalization & Profiles (`assistant/personalization.py`)
- Dynamic greeting tailored to the user's name and time of day.
- Switchable personalities: `Jarvis`, `Friendly`, `Professional`, `Witty`.
- Custom command shortcuts/aliases (`"work mode"` &rarr; `"open github"`).

### 6. 📊 Real-Time GUI Dashboard (`assistant/gui.py`)
- Cyberpunk dark theme (`#0a0f18` background, `#00d2ff` neon accents).
- Dynamic canvas audio wave visualizer reflecting assistant states: `IDLE`, `LISTENING`, `PROCESSING`, and `SPEAKING`.
- 6 interactive tabs: Live Console, Reminders, Notes Vault, Automation Quick-Bar, Telemetry Analytics, and Settings & Security.

### 7. 📈 Usage Analytics (`assistant/analytics.py`)
- Logs total commands, daily activity, success rates, average response times (ms), and top recognized intents.
- Accessible via voice (`"Jarvis, show analytics"`) or visually in the dashboard.

### 8. 🛡️ Security & Permission Layer (`assistant/security.py`)
- Policy engine with 3 security levels: `RELAXED`, `STANDARD`, and `STRICT`.
- Two-step verification interceptor for destructive operations (system shutdown, restart, recycle bin purge, note wiping).
- Immutable audit log saved to SQLite.

---

## ⚡ 3. Single-Click Execution (Windows)

Simply **double-click** [`run.bat`](file:///c:/Users/ANAHIIKA/OneDrive/Desktop/jarvis/run.bat):
1. Verifies your Python installation.
2. Creates and activates an isolated virtual environment (`venv`).
3. Installs all required packages automatically.
4. Launches the full JARVIS GUI Dashboard & Voice Assistant.

### Or launch manually from terminal:
```bash
# 1. Activate venv
venv\Scripts\activate

# 2. Launch GUI Dashboard (Default)
python main.py

# 3. Launch Headless CLI Mode (Optional)
python main.py --cli
```

---

## 🗣️ 4. Example Voice & Text Commands

| Category | Example Phrases |
| :--- | :--- |
| **Personalization** | *"Jarvis, call me Tony"* / *"Who am I?"* / *"Set personality to Witty"* |
| **Reminders** | *"Jarvis, remind me to drink water in 10 minutes"* / *"List reminders"* |
| **Notes** | *"Take a note that server deployment is at 5 PM"* / *"Read my notes"* |
| **Automation** | *"Mute volume"* / *"Volume up"* / *"Take a screenshot"* / *"Play pause"* |
| **Apps & Web** | *"Open Calculator"* / *"Open Chrome"* / *"Open YouTube"* / *"Search for Python tips"* |
| **System & Security** | *"Lock my screen"* / *"Empty recycle bin"* / *"System info"* / *"Shut down computer"* |
| **Analytics** | *"Jarvis, show my usage analytics"* / *"Security logs"* |
| **AI Knowledge** | *"Explain quantum computing"* / *"What is the capital of Japan?"* |
| **Exit** | *"Exit"* / *"Shutdown assistant"* / *"Goodbye"* |
