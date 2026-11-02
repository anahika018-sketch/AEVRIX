import os
import sys
import time
import json
import platform
import urllib.parse
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = os.path.join(BASE_DIR, "web")

from assistant.database import DatabaseManager
from assistant.automation import DesktopAutomation
from assistant.reminders import ReminderService
from assistant.personalization import PersonalizationManager
from assistant.security import SecurityManager
from assistant.analytics import AnalyticsTracker
from assistant.ai import AIManager
from assistant.commands import CommandHandler

# Shared backend subsystems
db = DatabaseManager()
automation = DesktopAutomation()
personalization = PersonalizationManager(db)
security = SecurityManager(db)
analytics = AnalyticsTracker(db)
ai = AIManager()
reminders = ReminderService(db)
reminders.start()

commands = CommandHandler(
    db=db,
    automation=automation,
    reminders=reminders,
    personalization=personalization,
    security=security,
    analytics=analytics,
    ai=ai
)


class AevrixWebHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/reminders":
            self._set_headers(200)
            data = reminders.get_active_reminders()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/notes":
            self._set_headers(200)
            data = db.get_recent_notes(limit=50)
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/analytics":
            self._set_headers(200)
            data = analytics.get_dashboard_data()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/profile":
            self._set_headers(200)
            data = db.get_profile()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/favicon.ico":
            self._set_headers(204)
            return

        # Static Files
        if path in ["/", "/index.html"]:
            filepath = os.path.join(WEB_DIR, "index.html")
            mime = "text/html; charset=utf-8"
        elif path == "/style.css":
            filepath = os.path.join(WEB_DIR, "style.css")
            mime = "text/css; charset=utf-8"
        elif path == "/app.js":
            filepath = os.path.join(WEB_DIR, "app.js")
            mime = "application/javascript; charset=utf-8"
        else:
            filepath = os.path.join(WEB_DIR, path.lstrip("/"))
            mime = "text/plain"

        if os.path.exists(filepath) and not os.path.isdir(filepath):
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                self._set_headers(200, mime)
                self.wfile.write(content)
            except Exception as e:
                self._set_headers(500, "text/plain")
                self.wfile.write(str(e).encode("utf-8"))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            payload = {}

        if path == "/api/chat":
            message = payload.get("message", "").strip()
            if not message:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Empty message"}).encode("utf-8"))
                return

            response_text = commands.handle(message)
            if not response_text:
                response_text = "Command executed successfully."

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "response": response_text,
                "status": "ok"
            }).encode("utf-8"))
            return

        if path == "/api/reminders":
            task = payload.get("task", "Reminder")
            minutes = payload.get("minutes", 5)
            due = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            rem_info = reminders.create_reminder(task, due)
            self._set_headers(201)
            self.wfile.write(json.dumps(rem_info, default=str).encode("utf-8"))
            return

        if path == "/api/notes":
            content = payload.get("content", "")
            note_id = db.add_note(content)
            self._set_headers(201)
            self.wfile.write(json.dumps({"id": note_id, "content": content}).encode("utf-8"))
            return

        if path == "/api/profile":
            if "user_name" in payload and payload["user_name"]:
                personalization.set_user_name(payload["user_name"])
            if "assistant_name" in payload and payload["assistant_name"]:
                personalization.set_assistant_name(payload["assistant_name"])
            if "personality" in payload and payload["personality"]:
                personalization.set_personality(payload["personality"])
            if "security_level" in payload and payload["security_level"]:
                security.set_security_level(payload["security_level"])
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "updated"}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(b'{"error": "Not Found"}')

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/reminders/"):
            rem_id = int(path.split("/")[-1])
            db.delete_reminder(rem_id)
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "deleted"}).encode("utf-8"))
            return

        if path.startswith("/api/notes/"):
            note_id = int(path.split("/")[-1])
            db.delete_note(note_id)
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "deleted"}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(b'{"error": "Not Found"}')


def open_browser(url):
    """Opens specifically in Google Chrome for full native Web Speech API support."""
    time.sleep(0.6)
    if platform.system() == "Windows":
        import subprocess

        # 1. Try launching Google Chrome command
        try:
            res = subprocess.run(["cmd.exe", "/c", "start", "chrome", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return
        except Exception:
            pass

        # 2. Check direct Chrome executable locations
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe")
        ]
        for cp in chrome_paths:
            if os.path.exists(cp):
                try:
                    subprocess.Popen([cp, url])
                    return
                except Exception:
                    pass

        # 3. Fallback to Microsoft Edge (Chromium based, full Web Speech API support)
        try:
            subprocess.run(["cmd.exe", "/c", "start", "msedge", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass

        # 4. Default shell open fallback
        try:
            os.system(f'start "" "{url}"')
            return
        except Exception:
            pass

    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


def start_server(port=5000, auto_open=True):
    chosen_port = port
    httpd = None

    for p in [port, 5001, 8000, 8080]:
        try:
            httpd = HTTPServer(("", p), AevrixWebHandler)
            chosen_port = p
            break
        except OSError:
            continue

    if not httpd:
        print("[ERROR] Could not bind to any local port (5000, 5001, 8000, 8080).")
        return

    url = f"http://localhost:{chosen_port}"

    print("\n" + "=" * 62)
    print("      AEVRIX AI // CHATGPT & GEMINI STYLE FRONTEND")
    print("=" * 62)
    print(f"\n[+] Local Server running at: {url}")
    print(f"[+] Opening your browser automatically...")
    print(f"\n👉 If the browser does not open, visit: {url}")
    print("\n[+] Press Ctrl+C in this terminal to stop.")
    print("=" * 62 + "\n")

    if auto_open:
        threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Aevrix server...")
    finally:
        httpd.server_close()
        reminders.stop()


if __name__ == "__main__":
    start_server()
