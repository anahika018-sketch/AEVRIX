"""
System control commands for Jarvis:
Battery, CPU/RAM stats, Screenshot, Screen Lock, and System App launch.
"""

import os
import sys
import datetime
import subprocess
import config
from core.voice import speak
from utils.ui import print_status

# Try optional imports
try:
    import psutil
except ImportError:
    psutil = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

def get_battery_status():
    """Check battery percentage and charging state."""
    if psutil is None:
        speak("psutil is required for battery info. Install it via pip install psutil.")
        return

    battery = psutil.sensors_battery()
    if battery is None:
        speak("This computer doesn't appear to have a battery, or it is running on a desktop power supply.")
        return

    percent = battery.percent
    plugged = battery.power_plugged
    status = "plugged in and charging" if plugged else "running on battery power"
    speak(f"Battery is at {percent} percent, and the device is currently {status}.")

def get_system_stats():
    """Check CPU and RAM usage."""
    if psutil is None:
        speak("psutil is required for system stats. Install it via pip install psutil.")
        return

    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    speak(f"CPU utilization is at {cpu_usage} percent, and RAM usage is at {ram.percent} percent.")

def take_screenshot():
    """Capture screen and save to data/screenshots folder."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = config.SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"

    if ImageGrab is not None:
        try:
            image = ImageGrab.grab()
            image.save(filepath)
            speak(f"Screenshot captured and saved to {filepath.name}.")
            return
        except Exception as e:
            print_status(f"Pillow screenshot error: {e}")

    # Fallback to Windows PowerShell System.Drawing
    if os.name == "nt":
        try:
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $Screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $Bitmap = New-Object System.Drawing.Bitmap $Screen.Width, $Screen.Height
            $Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
            $Graphics.CopyFromScreen($Screen.Location, [System.Drawing.Point]::Empty, $Screen.Size)
            $Bitmap.Save('{filepath}')
            $Graphics.Dispose()
            $Bitmap.Dispose()
            """
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], timeout=10)
            if filepath.exists():
                speak(f"Screenshot captured and saved to {filepath.name}.")
                return
        except Exception:
            pass

    speak("Unable to capture screenshot. Please install Pillow with pip install pillow.")

def lock_screen():
    """Lock the Windows workstation immediately."""
    speak("Locking your computer screen now.")
    if os.name == "nt":
        import ctypes
        ctypes.windll.user32.LockWorkStation()
    else:
        speak("Screen lock is currently supported on Windows.")

def launch_app(app_name: str) -> bool:
    """Open common built-in Windows applications."""
    app = app_name.lower().strip()
    apps_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",
        "command prompt": "cmd.exe",
        "task manager": "taskmgr.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
    }

    if app in apps_map:
        speak(f"Opening {app}.")
        try:
            subprocess.Popen(apps_map[app])
            return True
        except Exception:
            try:
                os.system(f"start {apps_map[app]}")
                return True
            except Exception as e:
                speak(f"Could not open {app}: {e}")
                return False
    return False
