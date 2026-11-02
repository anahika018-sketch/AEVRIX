import os
import platform
import subprocess
import datetime
import ctypes
from typing import Tuple, Dict, Any
from config import SCREENSHOTS_DIR


class DesktopAutomation:
    """
    Handles native Windows desktop automation:
    - Volume & audio control (mute, unmute, set level, volume up/down)
    - Media playback keys (play/pause, next, previous)
    - Screen capture & screenshot management
    - Workstation lock & power management
    - System health diagnostics (CPU, Memory, Battery)
    - App & window management
    """

    # Virtual-Key codes for Windows user32.dll
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_PLAY_PAUSE = 0xB3

    def __init__(self):
        self.os_type = platform.system()
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    def _press_key(self, vk_code: int):
        """Simulates a Windows hardware key press and release."""
        if self.os_type == "Windows":
            try:
                user32 = ctypes.windll.user32
                user32.keybd_event(vk_code, 0, 0, 0) # Key down
                user32.keybd_event(vk_code, 0, 2, 0) # Key up
            except Exception as e:
                print("Key event notice:", e)

    # =========================================================================
    # AUDIO & VOLUME CONTROL
    # =========================================================================

    def mute_volume(self) -> str:
        self._press_key(self.VK_VOLUME_MUTE)
        return "Audio mute toggled."

    def volume_up(self, steps: int = 3) -> str:
        for _ in range(steps):
            self._press_key(self.VK_VOLUME_UP)
        return "Volume increased."

    def volume_down(self, steps: int = 3) -> str:
        for _ in range(steps):
            self._press_key(self.VK_VOLUME_DOWN)
        return "Volume decreased."

    def set_volume_percent(self, percent: int) -> str:
        """Sets Windows master volume using nircmd or PowerShell audio bridge."""
        if self.os_type != "Windows":
            return "Volume control is supported on Windows."

        level = max(0, min(100, percent))
        # Use PowerShell script to adjust sound volume smoothly
        try:
            # Multi-tap volume keys to achieve approximate level or use Windows SAPI sound interface
            # 50 down taps resets to 0, then percent/2 taps sets target
            for _ in range(50):
                self._press_key(self.VK_VOLUME_DOWN)
            steps_up = int(level / 2)
            for _ in range(steps_up):
                self._press_key(self.VK_VOLUME_UP)
            return f"Master volume set to approximately {level} percent."
        except Exception as e:
            return f"Could not adjust volume: {e}"

    # =========================================================================
    # MEDIA KEYS
    # =========================================================================

    def media_play_pause(self) -> str:
        self._press_key(self.VK_MEDIA_PLAY_PAUSE)
        return "Media playback toggled."

    def media_next(self) -> str:
        self._press_key(self.VK_MEDIA_NEXT_TRACK)
        return "Skipped to next media track."

    def media_prev(self) -> str:
        self._press_key(self.VK_MEDIA_PREV_TRACK)
        return "Returned to previous media track."

    # =========================================================================
    # SCREENSHOT CAPTURE
    # =========================================================================

    def take_screenshot(self) -> Tuple[bool, str]:
        """Captures a full screenshot and saves it to the screenshots directory."""
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{now}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)

        # Method 1: Try PIL ImageGrab
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            return True, filepath
        except Exception:
            pass

        # Method 2: Try Windows PowerShell .NET Graphics
        if self.os_type == "Windows":
            try:
                ps_script = f"""
                Add-Type -AssemblyName System.Windows.Forms
                Add-Type -AssemblyName System.Drawing
                $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
                $bitmap.Save('{filepath}', [System.Drawing.Imaging.ImageFormat]::Png)
                $graphics.Dispose()
                $bitmap.Dispose()
                """
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], timeout=6, stdout=subprocess.DEVNULL)
                if os.path.exists(filepath):
                    return True, filepath
            except Exception:
                pass

        return False, "Could not capture screenshot (missing graphics library)."

    # =========================================================================
    # SYSTEM LOCK & POWER (Gated by Security Layer)
    # =========================================================================

    def lock_workstation(self) -> str:
        if self.os_type == "Windows":
            try:
                ctypes.windll.user32.LockWorkStation()
                return "Workstation locked successfully."
            except Exception as e:
                return f"Failed to lock workstation: {e}"
        return "Lock workstation is only supported on Windows."

    def empty_recycle_bin(self) -> str:
        if self.os_type == "Windows":
            try:
                # Flags: 7 = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
                flags = 7
                result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
                if result == 0:
                    return "Recycle Bin has been emptied."
                return "Recycle Bin is already empty."
            except Exception:
                # Fallback to PowerShell
                try:
                    subprocess.run(["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], timeout=5)
                    return "Recycle Bin cleared."
                except Exception as e:
                    return f"Failed to empty recycle bin: {e}"
        return "Empty recycle bin is only supported on Windows."

    def shutdown_system(self) -> str:
        if self.os_type == "Windows":
            subprocess.Popen(["shutdown", "/s", "/t", "30"])
            return "System shutdown initiated. Shutting down in 30 seconds. Type 'shutdown /a' in command prompt to abort."
        return "Shutdown is only supported on Windows."

    def restart_system(self) -> str:
        if self.os_type == "Windows":
            subprocess.Popen(["shutdown", "/r", "/t", "30"])
            return "System restart initiated. Rebooting in 30 seconds."
        return "Restart is only supported on Windows."

    # =========================================================================
    # APP LAUNCHER
    # =========================================================================

    def launch_app(self, app_id: str) -> str:
        if self.os_type != "Windows":
            return "App launch is configured for Windows."

        app_map = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "terminal": "cmd.exe",
            "taskmgr": "taskmgr.exe",
            "explorer": "explorer.exe",
            "settings": "ms-settings:"
        }

        if app_id in app_map:
            target = app_map[app_id]
            if target.startswith("ms-settings:"):
                os.system(f"start {target}")
            else:
                subprocess.Popen([target])
            return f"Opening {app_id.capitalize()}."

        if app_id == "chrome":
            subprocess.Popen(["cmd.exe", "/c", "start chrome"])
            return "Opening Google Chrome."

        if app_id == "edge":
            subprocess.Popen(["cmd.exe", "/c", "start msedge"])
            return "Opening Microsoft Edge."

        if app_id == "vscode":
            subprocess.Popen(["cmd.exe", "/c", "code ."])
            return "Opening Visual Studio Code."

        return f"Unknown application '{app_id}'."

    # =========================================================================
    # SYSTEM DIAGNOSTICS & HEALTH
    # =========================================================================

    def get_system_diagnostics(self) -> Dict[str, Any]:
        """Collects live CPU, Memory, and Battery telemetry."""
        data = {
            "os": f"{platform.system()} {platform.release()}",
            "machine": platform.machine(),
            "cpu_percent": "N/A",
            "battery_percent": "N/A",
            "is_charging": False
        }

        # Check battery via Windows SYSTEM_POWER_STATUS
        if self.os_type == "Windows":
            try:
                class SYSTEM_POWER_STATUS(ctypes.Structure):
                    _fields_ = [
                        ('ACLineStatus', ctypes.c_byte),
                        ('BatteryFlag', ctypes.c_byte),
                        ('BatteryLifePercent', ctypes.c_byte),
                        ('Reserved1', ctypes.c_byte),
                        ('BatteryLifeTime', ctypes.c_ulong),
                        ('BatteryFullLifeTime', ctypes.c_ulong)
                    ]
                status = SYSTEM_POWER_STATUS()
                if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
                    if status.BatteryLifePercent != 255:
                        data["battery_percent"] = f"{status.BatteryLifePercent}%"
                        data["is_charging"] = (status.ACLineStatus == 1)
            except Exception:
                pass

        return data
