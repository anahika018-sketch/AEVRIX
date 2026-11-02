# PROJECT SYNOPSIS: JARVIS AI DESKTOP ASSISTANT

## 1. Project Title
**JARVIS AI**: An Intelligent Desktop Voice Assistant with Intent Understanding, Desktop Automation, SQLite Persistence, and a Real-Time Cyberpunk GUI Dashboard.

---

## 2. Executive Summary
JARVIS AI is a modular, production-ready desktop intelligence system designed to automate everyday operating system workflows, maintain persistent productivity data, understand natural speech through an Intent Classification Engine, and provide a secure, personalized human-computer interface.

Originally conceived as a speech-to-text script, the system has undergone a major architectural expansion. All eight capabilities previously listed under **Future Scope** have been promoted into **Fully Implemented Core Architecture**:

| Previous "Future Scope" Item | New Status | Implementation Module |
| :--- | :--- | :--- |
| **1. Natural Language / Intent Understanding** | ✅ **IMPLEMENTED** | `assistant/nlp.py` (`IntentEngine`, `IntentResult`) |
| **2. Native Desktop Automation** | ✅ **IMPLEMENTED** | `assistant/automation.py` (`DesktopAutomation`) |
| **3. Scheduled Reminders & Timers** | ✅ **IMPLEMENTED** | `assistant/reminders.py` (`ReminderService`) |
| **4. SQLite Database Persistence** | ✅ **IMPLEMENTED** | `assistant/database.py` (`DatabaseManager`, `jarvis.db`) |
| **5. Personalization & User Profiles** | ✅ **IMPLEMENTED** | `assistant/personalization.py` (`PersonalizationManager`) |
| **6. Real-Time GUI Dashboard** | ✅ **IMPLEMENTED** | `assistant/gui.py` (`JarvisGUI` with live visualizer) |
| **7. Usage Analytics & Telemetry** | ✅ **IMPLEMENTED** | `assistant/analytics.py` (`AnalyticsTracker`) |
| **8. Security & Permission Layer** | ✅ **IMPLEMENTED** | `assistant/security.py` (`SecurityManager`) |

---

## 3. Implemented System Architecture

```text
                                  +-----------------------+
                                  |   User Voice / Text   |
                                  +-----------+-----------+
                                              |
                                              v
                              +---------------+---------------+
                              |    Jarvis Desktop Dashboard   |
                              |   (Real-time Canvas Waveform) |
                              +---------------+---------------+
                                              |
                                              v
                              +---------------+---------------+
                              |   SpeechManager (STT & TTS)   |
                              |  - Google Speech Recognition  |
                              |  - Multi-tier Windows Voice   |
                              +---------------+---------------+
                                              |
                                              v
                              +---------------+---------------+
                              |    IntentEngine (NLP Core)    |
                              |  - Slot extraction & temporal |
                              |  - Regex / semantic matcher   |
                              +---------------+---------------+
                                              |
                                              v
                              +---------------+---------------+
                              |        CommandHandler         |
                              +-------+---------------+-------+
                                      |               |
         +----------------------------+               +----------------------------+
         |                            |               |                            |
         v                            v               v                            v
+------------------+         +------------------+   +------------------+  +------------------+
| DesktopAutomation|         | SecurityManager  |   | ReminderService  |  |  Multi-Tier AI   |
| - Volume / Media |         | - Confirmation   |   | - Daemon Thread  |  | - GPT-4o-mini    |
| - Screenshots    |         | - Destructive    |   | - Audio & GUI    |  | - Pollinations   |
| - Apps / Lock    |         | - Audit Log      |   |   Alarm Triggers |  | - Wikipedia      |
+------------------+         +------------------+   +------------------+  +------------------+
         |                            |                       |                    |
         +----------------------------+-----------------------+--------------------+
                                      |
                                      v
                        +-------------+-------------+
                        |  SQLite Database Manager  |
                        |       (jarvis.db)         |
                        | - Profile & Preferences   |
                        | - Notes & Reminders       |
                        | - Interaction Analytics   |
                        | - Security Audit Trails   |
                        +---------------------------+
```

---

## 4. Key Functional Modules

### 4.1. Intent Understanding (`assistant/nlp.py`)
- Analyzes unstructured natural language without external heavyweight model downloads.
- Maps user utterances to strongly-typed intents: `APP_LAUNCH`, `VOLUME_CONTROL`, `SET_REMINDER`, `TAKE_NOTE`, `WEATHER_QUERY`, `LOCK_SCREEN`, `SECURITY_QUERY`, `ANALYTICS_QUERY`, etc.
- Features slot-filling for relative time intervals (`"in 10 minutes"`, `"in 2 hours"`), numeric levels (`"volume 70%"`), application identifiers, and notes content.

### 4.2. Native Desktop Automation (`assistant/automation.py`)
- Hardware audio simulation using Windows virtual key events (`VK_VOLUME_MUTE`, `VK_VOLUME_UP`, `VK_VOLUME_DOWN`).
- Media control: Play/Pause, Next Track, Previous Track.
- Screen capture: Timestamped PNG generation saved directly to the `screenshots/` directory.
- Operating system management: Workstation locking (`LockWorkStation`), Recycle Bin purging, and system shutdown/restart.
- Telemetry: Live battery percentage and power status.

### 4.3. Scheduled Reminders & Timers (`assistant/reminders.py`)
- Multi-threaded background daemon polling SQLite for due alerts every 3 seconds.
- Dispatches spoken voice notifications and updates the GUI live transcript.
- Full CRUD support: view pending reminders, mark as done, or purge completed alerts.

### 4.4. SQLite Database Persistence (`assistant/database.py`)
- ACID-compliant local storage in `jarvis.db`.
- Structured relational schemas:
  - `user_profile`: User name, assistant name, personality, voice gender, default city, security policy.
  - `reminders`: Due timestamps, task titles, completion statuses.
  - `notes`: Timestamped memos, category tagging, search index.
  - `usage_logs`: Raw utterances, classified intents, response latencies (ms), success flags.
  - `security_audit_log`: High-privilege events, authorization outcomes, status timestamps.
  - `custom_aliases`: User-defined macro shortcuts.

### 4.5. Personalization & User Profiles (`assistant/personalization.py`)
- Dynamic greeting generator adapting to user name, time of day (morning, afternoon, evening), and personality tone (`Jarvis`, `Friendly`, `Professional`, `Witty`).
- Persistent name changes (`"Call me Tony"`).
- User macro alias registry (`"work mode"` &rarr; `"open github"`).

### 4.6. Futuristic GUI Dashboard (`assistant/gui.py`)
- Built using Python's standard `tkinter` with a cyber-dark theme (`#0a0f18` background, `#00d2ff` neon accents).
- Dynamic canvas audio wave visualizer reflecting assistant states: `IDLE`, `LISTENING`, `PROCESSING`, and `SPEAKING`.
- 6 interactive tabs: Live Console, Reminders Manager, Notes Vault, Automation Quick-Bar, Telemetry Analytics, and Settings & Security.

### 4.7. Usage Analytics & Telemetry (`assistant/analytics.py`)
- Measures execution duration in milliseconds for every command.
- Real-time KPI aggregation: Total interactions, daily usage, success percentage, top recognized intents.
- Available visually in the GUI and via voice query (`"Jarvis, show my usage analytics"`).

### 4.8. Security & Permission Layer (`assistant/security.py`)
- Policy engine with 3 security levels: `RELAXED`, `STANDARD`, and `STRICT`.
- Two-step verification interceptor for destructive operations (system shutdown, restart, recycle bin purge, mass note deletion).
- Immutable security audit logging for compliance and safety.

---

## 5. Execution & Single-Click Optimization
- **Windows Batch Launcher (`run.bat`)**: Automatically verifies Python, provisions an isolated virtual environment (`venv`), installs dependencies, and boots the system with one double-click.
- **Dual Execution Modes**:
  - `python main.py` &rarr; Launches the complete GUI Dashboard + Voice Assistant.
  - `python main.py --cli` &rarr; Launches in headless, lightweight terminal mode.
