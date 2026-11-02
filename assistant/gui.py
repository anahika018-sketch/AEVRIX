import os
import time
import math
import threading
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from config import GUI_TITLE, GUI_THEME, GUI_ACCENT_COLOR, GUI_BG_DARK, GUI_CARD_BG, GUI_TEXT_COLOR, PERSONALITIES
from assistant.database import DatabaseManager
from assistant.automation import DesktopAutomation
from assistant.reminders import ReminderService
from assistant.personalization import PersonalizationManager
from assistant.security import SecurityManager
from assistant.analytics import AnalyticsTracker
from assistant.commands import CommandHandler
from assistant.speech import SpeechManager


class JarvisGUI:
    """
    Futuristic Desktop Dashboard & Visual Interface for Jarvis AI.
    Single-window unified architecture: all interactions, answers,
    waveforms, and tools live inside one single clean dashboard.
    """

    def __init__(
        self,
        command_handler: CommandHandler,
        speech_manager: SpeechManager,
        db: DatabaseManager,
        automation: DesktopAutomation,
        reminders: ReminderService,
        personalization: PersonalizationManager,
        security: SecurityManager,
        analytics: AnalyticsTracker
    ):
        self.cmd = command_handler
        self.speech = speech_manager
        self.db = db
        self.automation = automation
        self.reminders = reminders
        self.personalization = personalization
        self.security = security
        self.analytics = analytics

        # 1. Main Root Window
        self.root = tk.Tk()
        self.root.title(GUI_TITLE)
        self.root.geometry("980x720")
        self.root.minsize(860, 620)
        self.root.configure(bg=GUI_BG_DARK)

        # Bring window directly to front
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)
        self.root.focus_force()

        # State flags
        self.current_state = "IDLE"  # IDLE, LISTENING, PROCESSING, SPEAKING
        self.is_listening_active = False
        self.anim_phase = 0.0

        # Hook reminder alert callback into GUI
        self.reminders.on_trigger_callback = self._on_reminder_triggered

        self._apply_styles()
        self._build_ui()
        self._start_visualizer_loop()

    def _apply_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Configure custom notebook tabs
        try:
            style.configure("TNotebook", background=GUI_BG_DARK, borderwidth=0)
            style.configure("TNotebook.Tab", background=GUI_CARD_BG, foreground="#94a3b8", padding=[14, 8], font=("Segoe UI", 10, "bold"))
            style.map("TNotebook.Tab",
                background=[("selected", GUI_ACCENT_COLOR)],
                foreground=[("selected", "#0f172a")]
            )
            style.configure("TFrame", background=GUI_BG_DARK)
            style.configure("TLabel", background=GUI_BG_DARK, foreground=GUI_TEXT_COLOR, font=("Segoe UI", 10))
        except Exception:
            pass

    def _build_ui(self):
        # 1. Top Bar
        top_bar = tk.Frame(self.root, bg="#0d1522", height=60, padx=16, pady=8)
        top_bar.pack(fill="x", side="top")

        # Brand / Identity
        self.lbl_title = tk.Label(
            top_bar,
            text="JARVIS AI // PERSONAL INTELLIGENCE SYSTEM",
            font=("Segoe UI", 12, "bold"),
            fg=GUI_ACCENT_COLOR,
            bg="#0d1522"
        )
        self.lbl_title.pack(side="left")

        # Live State Indicator
        self.lbl_status = tk.Label(
            top_bar,
            text="[ONLINE] SYSTEM STANDBY",
            font=("Consolas", 10, "bold"),
            fg="#22c55e",
            bg="#0d1522",
            padx=12,
            pady=4
        )
        self.lbl_status.pack(side="right")

        # 2. Dynamic Audio Waveform Canvas
        self.canvas_wave = tk.Canvas(self.root, height=70, bg="#06090e", highlightthickness=0)
        self.canvas_wave.pack(fill="x", side="top", pady=2)

        # 3. Main Tabbed Notebook (Unified Single Window)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=8)

        # Tabs
        self.tab_chat = ttk.Frame(self.notebook)
        self.tab_reminders = ttk.Frame(self.notebook)
        self.tab_notes = ttk.Frame(self.notebook)
        self.tab_automation = ttk.Frame(self.notebook)
        self.tab_analytics = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_chat, text="  Live Console  ")
        self.notebook.add(self.tab_reminders, text="  Reminders  ")
        self.notebook.add(self.tab_notes, text="  Notes Vault  ")
        self.notebook.add(self.tab_automation, text="  Automation  ")
        self.notebook.add(self.tab_analytics, text="  Analytics  ")
        self.notebook.add(self.tab_settings, text="  Settings & Security  ")

        # Build tabs
        self._build_chat_tab()
        self._build_reminders_tab()
        self._build_notes_tab()
        self._build_automation_tab()
        self._build_analytics_tab()
        self._build_settings_tab()

    # =========================================================================
    # TAB 1: LIVE CHAT / CONSOLE (Single view where all answers appear)
    # =========================================================================

    def _build_chat_tab(self):
        frame = tk.Frame(self.tab_chat, bg=GUI_BG_DARK, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # Transcript Area
        self.txt_transcript = tk.Text(
            frame,
            bg="#090d16",
            fg="#e2e8f0",
            insertbackground="#38bdf8",
            font=("Consolas", 10),
            wrap="word",
            relief="flat",
            padx=12,
            pady=12
        )
        self.txt_transcript.pack(fill="both", expand=True, side="top")

        scroll = tk.Scrollbar(self.txt_transcript, command=self.txt_transcript.yview)
        scroll.pack(side="right", fill="y")
        self.txt_transcript.configure(yscrollcommand=scroll.set)

        # Tag Styles
        self.txt_transcript.tag_config("user", foreground="#38bdf8", font=("Consolas", 10, "bold"))
        self.txt_transcript.tag_config("jarvis", foreground="#4ade80", font=("Consolas", 10, "bold"))
        self.txt_transcript.tag_config("system", foreground="#fbbf24", font=("Consolas", 9, "italic"))

        # Input Row
        input_bar = tk.Frame(frame, bg="#0d1522", height=45, pady=8)
        input_bar.pack(fill="x", side="bottom")

        self.entry_cmd = tk.Entry(
            input_bar,
            bg="#162235",
            fg="#ffffff",
            insertbackground="#00d2ff",
            font=("Segoe UI", 11),
            relief="flat"
        )
        self.entry_cmd.pack(side="left", fill="both", expand=True, padx=(4, 8), ipady=5)
        self.entry_cmd.bind("<Return>", lambda e: self._on_send_command())

        self.btn_send = tk.Button(
            input_bar,
            text="Execute",
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=16,
            command=self._on_send_command
        )
        self.btn_send.pack(side="left", padx=4)

        self.btn_mic = tk.Button(
            input_bar,
            text="[MIC] Speak",
            bg="#0f766e",
            fg="#ffffff",
            activebackground="#115e59",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=14,
            command=self._on_mic_toggle
        )
        self.btn_mic.pack(side="left", padx=4)

        user_name = self.personalization.get_user_name()
        self._append_transcript("System", f"Jarvis AI Dashboard initialized for {user_name}. Ready for voice or text commands.\n", "system")

    # =========================================================================
    # TAB 2: REMINDERS
    # =========================================================================

    def _build_reminders_tab(self):
        frame = tk.Frame(self.tab_reminders, bg=GUI_BG_DARK, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        add_frame = tk.LabelFrame(frame, text=" Add New Reminder ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        add_frame.pack(fill="x", side="top", pady=(0, 12))

        tk.Label(add_frame, text="Task:", bg=GUI_CARD_BG, fg=GUI_TEXT_COLOR).pack(side="left", padx=(0, 6))
        self.ent_rem_title = tk.Entry(add_frame, bg="#1a2638", fg="#ffffff", font=("Segoe UI", 10), width=35, relief="flat")
        self.ent_rem_title.pack(side="left", padx=(0, 16), ipady=3)

        tk.Label(add_frame, text="Time (in minutes):", bg=GUI_CARD_BG, fg=GUI_TEXT_COLOR).pack(side="left", padx=(0, 6))
        self.ent_rem_mins = tk.Entry(add_frame, bg="#1a2638", fg="#ffffff", font=("Segoe UI", 10), width=6, relief="flat")
        self.ent_rem_mins.insert(0, "5")
        self.ent_rem_mins.pack(side="left", padx=(0, 16), ipady=3)

        btn_add_rem = tk.Button(
            add_frame,
            text="+ Set Reminder",
            bg="#0284c7",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            command=self._on_add_reminder_manual
        )
        btn_add_rem.pack(side="left")

        list_frame = tk.Frame(frame, bg=GUI_BG_DARK)
        list_frame.pack(fill="both", expand=True)

        self.list_reminders = tk.Listbox(
            list_frame,
            bg="#090d16",
            fg="#e2e8f0",
            selectbackground="#0284c7",
            font=("Consolas", 10),
            relief="flat",
            padx=10,
            pady=10
        )
        self.list_reminders.pack(fill="both", expand=True, side="left")

        btn_box = tk.Frame(frame, bg=GUI_BG_DARK, pady=8)
        btn_box.pack(fill="x", side="bottom")

        tk.Button(btn_box, text="Refresh List", bg="#1e293b", fg="#cbd5e1", relief="flat", command=self._refresh_reminders_list).pack(side="left", padx=(0, 8))
        tk.Button(btn_box, text="Clear Completed", bg="#334155", fg="#cbd5e1", relief="flat", command=lambda: (self.reminders.clear_all(), self._refresh_reminders_list())).pack(side="left")

        self._refresh_reminders_list()

    # =========================================================================
    # TAB 3: NOTES VAULT
    # =========================================================================

    def _build_notes_tab(self):
        frame = tk.Frame(self.tab_notes, bg=GUI_BG_DARK, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        add_frame = tk.LabelFrame(frame, text=" Quick Note Creation ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        add_frame.pack(fill="x", side="top", pady=(0, 12))

        self.ent_note = tk.Entry(add_frame, bg="#1a2638", fg="#ffffff", font=("Segoe UI", 10), relief="flat")
        self.ent_note.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=4)
        self.ent_note.bind("<Return>", lambda e: self._on_add_note_manual())

        tk.Button(add_frame, text="+ Save Note", bg="#0284c7", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, command=self._on_add_note_manual).pack(side="left")

        self.list_notes = tk.Listbox(
            frame,
            bg="#090d16",
            fg="#e2e8f0",
            selectbackground="#0284c7",
            font=("Segoe UI", 10),
            relief="flat",
            padx=10,
            pady=10
        )
        self.list_notes.pack(fill="both", expand=True)

        btn_box = tk.Frame(frame, bg=GUI_BG_DARK, pady=8)
        btn_box.pack(fill="x", side="bottom")

        tk.Button(btn_box, text="Refresh Notes", bg="#1e293b", fg="#cbd5e1", relief="flat", command=self._refresh_notes_list).pack(side="left", padx=(0, 8))
        tk.Button(btn_box, text="Wipe All Notes", bg="#b91c1c", fg="#ffffff", relief="flat", command=self._on_wipe_notes).pack(side="right")

        self._refresh_notes_list()

    # =========================================================================
    # TAB 4: DESKTOP AUTOMATION
    # =========================================================================

    def _build_automation_tab(self):
        frame = tk.Frame(self.tab_automation, bg=GUI_BG_DARK, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        # Audio Controls
        sec_audio = tk.LabelFrame(frame, text=" Audio & Media Control ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=14, pady=12)
        sec_audio.pack(fill="x", pady=(0, 12))

        tk.Button(sec_audio, text="[MUTE] Audio", bg="#1e293b", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("VOLUME_MUTE")).pack(side="left", padx=4)
        tk.Button(sec_audio, text="[-] Vol Down", bg="#1e293b", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("VOLUME_DOWN")).pack(side="left", padx=4)
        tk.Button(sec_audio, text="[+] Vol Up", bg="#1e293b", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("VOLUME_UP")).pack(side="left", padx=4)
        tk.Button(sec_audio, text="[>] Play / Pause", bg="#0284c7", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("MEDIA_PLAY_PAUSE")).pack(side="left", padx=4)
        tk.Button(sec_audio, text="[>>] Next Track", bg="#1e293b", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("MEDIA_NEXT")).pack(side="left", padx=4)

        # Screen & Power
        sec_power = tk.LabelFrame(frame, text=" Screen & System Actions ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=14, pady=12)
        sec_power.pack(fill="x", pady=(0, 12))

        tk.Button(sec_power, text="[CAPTURE] Screenshot", bg="#0f766e", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("SCREENSHOT")).pack(side="left", padx=4)
        tk.Button(sec_power, text="[LOCK] Lock Screen", bg="#4338ca", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("LOCK_SCREEN")).pack(side="left", padx=4)
        tk.Button(sec_power, text="[PURGE] Recycle Bin", bg="#b45309", fg="#ffffff", relief="flat", padx=12, command=lambda: self._dispatch_gui_action("EMPTY_RECYCLE_BIN")).pack(side="left", padx=4)

        # Quick Launchers
        sec_apps = tk.LabelFrame(frame, text=" Quick Application Launcher ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=14, pady=12)
        sec_apps.pack(fill="x", pady=(0, 12))

        for app_id, label in [("notepad", "Notepad"), ("calculator", "Calculator"), ("chrome", "Chrome"), ("vscode", "VS Code"), ("taskmgr", "Task Manager"), ("explorer", "File Explorer")]:
            tk.Button(sec_apps, text=f"[APP] {label}", bg="#1e293b", fg="#e2e8f0", relief="flat", padx=10, pady=4,
                      command=lambda a=app_id: self._dispatch_app_launch(a)).pack(side="left", padx=4, pady=4)

    # =========================================================================
    # TAB 5: USAGE ANALYTICS
    # =========================================================================

    def _build_analytics_tab(self):
        frame = tk.Frame(self.tab_analytics, bg=GUI_BG_DARK, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        cards_frame = tk.Frame(frame, bg=GUI_BG_DARK)
        cards_frame.pack(fill="x", pady=(0, 14))

        self.kpi_total = self._create_kpi_card(cards_frame, "TOTAL COMMANDS", "0", "#38bdf8")
        self.kpi_today = self._create_kpi_card(cards_frame, "COMMANDS TODAY", "0", "#4ade80")
        self.kpi_rate = self._create_kpi_card(cards_frame, "SUCCESS RATE", "100%", "#facc15")
        self.kpi_avg = self._create_kpi_card(cards_frame, "AVG LATENCY", "0 ms", "#c084fc")

        detail_frame = tk.Frame(frame, bg=GUI_BG_DARK)
        detail_frame.pack(fill="both", expand=True)

        sec_intents = tk.LabelFrame(detail_frame, text=" Top Recognized Intents ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        sec_intents.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.list_top_intents = tk.Listbox(sec_intents, bg="#090d16", fg="#e2e8f0", font=("Consolas", 10), relief="flat")
        self.list_top_intents.pack(fill="both", expand=True)

        sec_recent = tk.LabelFrame(detail_frame, text=" Recent Execution History ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        sec_recent.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self.list_recent_logs = tk.Listbox(sec_recent, bg="#090d16", fg="#e2e8f0", font=("Consolas", 9), relief="flat")
        self.list_recent_logs.pack(fill="both", expand=True)

        tk.Button(frame, text="Refresh Analytics", bg="#0284c7", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", command=self._refresh_analytics).pack(side="bottom", anchor="e", pady=8)

        self._refresh_analytics()

    def _create_kpi_card(self, parent, title, val, color):
        card = tk.Frame(parent, bg=GUI_CARD_BG, padx=16, pady=12, highlightthickness=1, highlightbackground="#1e293b")
        card.pack(side="left", fill="both", expand=True, padx=4)

        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#94a3b8", bg=GUI_CARD_BG).pack(anchor="w")
        lbl_val = tk.Label(card, text=val, font=("Segoe UI", 16, "bold"), fg=color, bg=GUI_CARD_BG)
        lbl_val.pack(anchor="w", pady=(4, 0))
        return lbl_val

    # =========================================================================
    # TAB 6: SETTINGS, PERSONALIZATION & SECURITY
    # =========================================================================

    def _build_settings_tab(self):
        frame = tk.Frame(self.tab_settings, bg=GUI_BG_DARK, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        sec_profile = tk.LabelFrame(frame, text=" User Profile & Personalization ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=14, pady=12)
        sec_profile.pack(fill="x", pady=(0, 12))

        # User Name
        row1 = tk.Frame(sec_profile, bg=GUI_CARD_BG)
        row1.pack(fill="x", pady=4)
        tk.Label(row1, text="User Name:", width=18, anchor="w", bg=GUI_CARD_BG, fg=GUI_TEXT_COLOR).pack(side="left")
        self.ent_user_name = tk.Entry(row1, bg="#1a2638", fg="#ffffff", font=("Segoe UI", 10), relief="flat")
        self.ent_user_name.insert(0, self.personalization.get_user_name())
        self.ent_user_name.pack(side="left", padx=8, ipady=2)

        # Assistant Name
        row2 = tk.Frame(sec_profile, bg=GUI_CARD_BG)
        row2.pack(fill="x", pady=4)
        tk.Label(row2, text="Assistant Name:", width=18, anchor="w", bg=GUI_CARD_BG, fg=GUI_TEXT_COLOR).pack(side="left")
        self.ent_asst_name = tk.Entry(row2, bg="#1a2638", fg="#ffffff", font=("Segoe UI", 10), relief="flat")
        self.ent_asst_name.insert(0, self.personalization.get_assistant_name())
        self.ent_asst_name.pack(side="left", padx=8, ipady=2)

        # Personality Dropdown
        row3 = tk.Frame(sec_profile, bg=GUI_CARD_BG)
        row3.pack(fill="x", pady=4)
        tk.Label(row3, text="Personality Tone:", width=18, anchor="w", bg=GUI_CARD_BG, fg=GUI_TEXT_COLOR).pack(side="left")
        self.var_persona = tk.StringVar(value=self.personalization.get_personality())
        opt_persona = ttk.Combobox(row3, textvariable=self.var_persona, values=list(PERSONALITIES.keys()), state="readonly", width=16)
        opt_persona.pack(side="left", padx=8)

        # Security Level Dropdown
        row4 = tk.Frame(sec_profile, bg=GUI_CARD_BG)
        row4.pack(fill="x", pady=4)
        tk.Label(row4, text="Security Level:", width=18, anchor="w", bg=GUI_CARD_BG, fg=GUI_TEXT_COLOR).pack(side="left")
        self.var_security = tk.StringVar(value=self.security.get_security_level())
        opt_sec = ttk.Combobox(row4, textvariable=self.var_security, values=["RELAXED", "STANDARD", "STRICT"], state="readonly", width=16)
        opt_sec.pack(side="left", padx=8)

        tk.Button(
            sec_profile,
            text="Save Preferences",
            bg="#0284c7",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=14,
            command=self._on_save_preferences
        ).pack(anchor="e", pady=8)

        # Security Audit Log View
        sec_audit = tk.LabelFrame(frame, text=" Security Audit Trail ", bg=GUI_CARD_BG, fg=GUI_ACCENT_COLOR, font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        sec_audit.pack(fill="both", expand=True)

        self.list_audit = tk.Listbox(sec_audit, bg="#090d16", fg="#e2e8f0", font=("Consolas", 9), relief="flat")
        self.list_audit.pack(fill="both", expand=True)

        self._refresh_audit_logs()

    # =========================================================================
    # DYNAMIC VISUALIZER
    # =========================================================================

    def _start_visualizer_loop(self):
        def update_wave():
            try:
                w = self.canvas_wave.winfo_width() or 900
                h = self.canvas_wave.winfo_height() or 70
                mid_y = h / 2

                self.canvas_wave.delete("wave")
                self.anim_phase += 0.15

                # Dynamic amplitude and frequency based on state
                if self.current_state == "LISTENING":
                    amp = 20.0
                    freq = 0.05
                    color = "#38bdf8"
                    status_txt = "[LISTENING] Speak now..."
                    status_color = "#38bdf8"
                elif self.current_state == "PROCESSING":
                    amp = 12.0
                    freq = 0.10
                    color = "#facc15"
                    status_txt = "[PROCESSING] Analyzing command..."
                    status_color = "#facc15"
                elif self.current_state == "SPEAKING":
                    amp = 24.0
                    freq = 0.08
                    color = "#4ade80"
                    status_txt = "[SPEAKING] Jarvis responding..."
                    status_color = "#4ade80"
                else:
                    amp = 4.0
                    freq = 0.02
                    color = "#1e293b"
                    status_txt = "[ONLINE] SYSTEM STANDBY"
                    status_color = "#22c55e"

                self.lbl_status.config(text=status_txt, fg=status_color)

                points = []
                for x in range(0, w, 6):
                    y = mid_y + math.sin(x * freq + self.anim_phase) * amp
                    points.extend([x, y])

                if len(points) >= 4:
                    self.canvas_wave.create_line(points, fill=color, width=2, smooth=True, tags="wave")
            except Exception:
                pass

            self.root.after(40, update_wave)

        self.root.after(100, update_wave)

    # =========================================================================
    # EVENT DISPATCHERS & HANDLERS
    # =========================================================================

    def _append_transcript(self, sender: str, text: str, tag: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_transcript.insert("end", f"[{timestamp}] {sender}: ", tag)
        self.txt_transcript.insert("end", f"{text}\n")
        self.txt_transcript.see("end")

    def _on_send_command(self):
        cmd_text = self.entry_cmd.get().strip()
        if not cmd_text:
            return
        self.entry_cmd.delete(0, "end")
        self._dispatch_command_async(cmd_text)

    def _dispatch_command_async(self, cmd_text: str):
        user_name = self.personalization.get_user_name()
        self._append_transcript(user_name, cmd_text, "user")
        self.current_state = "PROCESSING"

        def worker():
            try:
                res = self.cmd.handle(cmd_text, self.speech)
                asst_name = self.personalization.get_assistant_name()
                if res:
                    self.root.after(0, lambda: self._append_transcript(asst_name, res, "jarvis"))
                    self.current_state = "SPEAKING"
                    self.speech.speak(res)
            except Exception as e:
                self.root.after(0, lambda: self._append_transcript("Error", str(e), "system"))
            finally:
                self.current_state = "IDLE"
                self.root.after(0, self._refresh_analytics)
                self.root.after(0, self._refresh_notes_list)
                self.root.after(0, self._refresh_reminders_list)
                self.root.after(0, self._refresh_audit_logs)

        threading.Thread(target=worker, daemon=True).start()

    def _on_mic_toggle(self):
        if self.is_listening_active:
            return

        def listen_worker():
            self.is_listening_active = True
            self.current_state = "LISTENING"
            self.btn_mic.config(bg="#b91c1c", text="[LISTENING...]")

            try:
                spoken_text = self.speech.listen()
                if spoken_text:
                    self.root.after(0, lambda: self._dispatch_command_async(spoken_text))
            finally:
                self.is_listening_active = False
                self.current_state = "IDLE"
                self.btn_mic.config(bg="#0f766e", text="[MIC] Speak")

        threading.Thread(target=listen_worker, daemon=True).start()

    def _dispatch_gui_action(self, intent_type: str):
        actions = {
            "VOLUME_MUTE": "mute volume",
            "VOLUME_DOWN": "volume down",
            "VOLUME_UP": "volume up",
            "MEDIA_PLAY_PAUSE": "play pause",
            "MEDIA_NEXT": "next track",
            "SCREENSHOT": "take screenshot",
            "LOCK_SCREEN": "lock workstation",
            "EMPTY_RECYCLE_BIN": "empty recycle bin"
        }
        if intent_type in actions:
            self._dispatch_command_async(actions[intent_type])

    def _dispatch_app_launch(self, app_id: str):
        self._dispatch_command_async(f"open {app_id}")

    def _on_add_reminder_manual(self):
        title = self.ent_rem_title.get().strip()
        mins_str = self.ent_rem_mins.get().strip()
        if not title:
            return
        mins = int(mins_str) if mins_str.isdigit() else 5
        due_time = datetime.datetime.now() + datetime.timedelta(minutes=mins)
        self.reminders.create_reminder(title, due_time)
        self.ent_rem_title.delete(0, "end")
        self._refresh_reminders_list()
        self._append_transcript("System", f"Reminder added: '{title}' in {mins} minutes.", "system")

    def _on_add_note_manual(self):
        content = self.ent_note.get().strip()
        if not content:
            return
        self.db.add_note(content)
        self.ent_note.delete(0, "end")
        self._refresh_notes_list()
        self._append_transcript("System", "Note saved to vault.", "system")

    def _on_wipe_notes(self):
        if messagebox.askyesno("Confirm Wipe", "Are you sure you want to delete all saved notes?"):
            count = self.db.clear_all_notes()
            self._refresh_notes_list()
            self._append_transcript("Security", f"Wiped {count} notes from vault.", "system")

    def _on_reminder_triggered(self, reminder_data: dict):
        title = reminder_data.get("title", "Reminder")
        self.root.after(0, lambda: self._append_transcript("ALARM", f"[ALERT] Reminder Triggered: {title}!", "system"))
        self.speech.speak(f"Reminder: {title}")

    def _refresh_reminders_list(self):
        self.list_reminders.delete(0, "end")
        for r in self.reminders.get_active_reminders():
            status_tag = "[DONE]" if r["status"] == "completed" else "[PENDING]"
            time_part = r["remind_at"][11:16] if len(r["remind_at"]) >= 16 else r["remind_at"]
            self.list_reminders.insert("end", f"{status_tag} [{time_part}] {r['title']} (Status: {r['status']})")

    def _refresh_notes_list(self):
        self.list_notes.delete(0, "end")
        for n in self.db.get_recent_notes(limit=30):
            self.list_notes.insert("end", f"* [{n['created_at']}] {n['content']}")

    def _refresh_analytics(self):
        data = self.analytics.get_dashboard_data()
        summary = data["summary"]
        self.kpi_total.config(text=str(summary["total_commands"]))
        self.kpi_today.config(text=str(summary["today_count"]))
        self.kpi_rate.config(text=f"{summary['success_rate']}%")
        self.kpi_avg.config(text=f"{summary['avg_response_time_ms']} ms")

        self.list_top_intents.delete(0, "end")
        for item in summary["top_intents"]:
            self.list_top_intents.insert("end", f"{item['intent']:<22} : {item['count']} times")

        self.list_recent_logs.delete(0, "end")
        for log in data["recent_logs"]:
            mark = "[OK]" if log["success"] else "[ERR]"
            time_part = log["timestamp"][11:19] if len(log["timestamp"]) >= 19 else log["timestamp"]
            self.list_recent_logs.insert("end", f"{mark} [{time_part}] {log['raw_command']} -> {log['intent']} ({log['execution_time_ms']}ms)")

    def _refresh_audit_logs(self):
        self.list_audit.delete(0, "end")
        for log in self.db.get_security_audit_logs(limit=30):
            time_part = log["timestamp"][11:19] if len(log["timestamp"]) >= 19 else log["timestamp"]
            self.list_audit.insert("end", f"[{time_part}] {log['status']:<12} | {log['action']} - {log['description']}")

    def _on_save_preferences(self):
        user_name = self.ent_user_name.get().strip() or "Sir"
        asst_name = self.ent_asst_name.get().strip() or "Jarvis"
        persona = self.var_persona.get()
        sec_level = self.var_security.get()

        self.personalization.set_user_name(user_name)
        self.personalization.set_assistant_name(asst_name)
        self.personalization.set_personality(persona)
        self.security.set_security_level(sec_level)

        self.lbl_title.config(text=f"{asst_name.upper()} AI // PERSONAL INTELLIGENCE SYSTEM")
        messagebox.showinfo("Saved", "Preferences and Security policies successfully updated!")
        self._refresh_audit_logs()

    def run(self):
        """Starts Tkinter main loop."""
        self.root.mainloop()
