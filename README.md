# JARVIS Desktop Voice Assistant 🎙️🤖

A clean, modular, and beginner-friendly desktop voice assistant built in Python.

---

## 📁 1. Project Structure

```text
JARVIS/
│
├── main.py              # Main program entry point & event loop
├── config.py            # Wake words, assistant name & exit commands
├── requirements.txt     # Python libraries needed to run JARVIS
├── .env                 # API keys (never commit to git)
├── .gitignore           # Git ignore rules for .env and venv
├── run.bat              # One-click Windows runner
│
└── assistant/
    ├── __init__.py      # Package indicator
    ├── speech.py        # Speech recognition & text-to-speech (SpeechManager)
    ├── commands.py      # Built-in system, web & desktop commands (CommandHandler)
    └── ai.py            # AI fallback for general questions (AIManager)
```

---

## ⚡ 2. Setup & Installation (VS Code / Windows)

### Step 1: Create Virtual Environment
Open the VS Code terminal in the project directory:
```bash
python -m venv venv
```

### Step 2: Activate the Virtual Environment
On Windows:
```bash
venv\Scripts\activate
```

*(On macOS/Linux, run: `source venv/bin/activate`)*

### Step 3: Install Required Libraries
```bash
pip install -r requirements.txt
```

#### 🛠️ If PyAudio gives an installation error on Windows:
`pyaudio` sometimes requires C++ build tools when installing with standard `pip`. You can easily install pre-compiled binaries instead:

**Solution A (Recommended):**
```bash
pip install pipwin
pipwin install pyaudio
```

**Solution B (Direct Wheel):**
1. Check your Python version (`python --version`, e.g., Python 3.11).
2. Download the matching `.whl` from Christoph Gohlke's unofficial binaries or PyPI.
3. Install via: `pip install PyAudio‑<version>‑cp<python_version>‑win_amd64.whl`.

*(Note: If you run JARVIS without a microphone or PyAudio configured, it automatically falls back to text input mode so you can test all commands immediately!)*

---

## 🔑 3. Configure `.env`

Open [.env](file:///c:/Users/ANAHIIKA/OneDrive/Desktop/jarvis/.env) and enter your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## 🚀 4. Running JARVIS

From your terminal:
```bash
python main.py
```
*(Or simply double-click `run.bat` on Windows!)*

You will hear and see:
> **JARVIS:** Hello. I am Jarvis. How can I help you?

---

## 🗣️ 5. Example Voice Commands

| Category | Example Phrases |
| :--- | :--- |
| **Time & Date** | *"Jarvis, what time is it?"* / *"Jarvis, tell me today's date"* |
| **Web Browsing** | *"Jarvis, open YouTube"* / *"Jarvis, open Google"* / *"Jarvis, open GitHub"* |
| **Search & Media** | *"Jarvis, search for Python tutorials"* / *"Jarvis, play relaxing lofi music"* |
| **Desktop Tools** | *"Jarvis, open Calculator"* / *"Jarvis, open Notepad"* |
| **System Info** | *"Jarvis, system information"* |
| **AI Questions** | *"Jarvis, explain quantum computing"* / *"Jarvis, what is the capital of France?"* |
| **Exit** | *"Jarvis, shutdown"* / *"Jarvis, exit"* / *"Jarvis, goodbye"* |

---

## 🧩 6. How to Add New Commands

Adding a new command is as simple as adding an `if` block in [assistant/commands.py](file:///c:/Users/ANAHIIKA/OneDrive/Desktop/jarvis/assistant/commands.py):

```python
if "flip a coin" in command:
    import random
    result = random.choice(["Heads", "Tails"])
    return f"The coin landed on {result}."
```
