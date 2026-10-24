@echo off
title  Voice Assistant
color 0b
echo ========================================================
echo             Aevrix VOICE ASSISTANT LAUNCHER
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b
)

:: Check if virtual environment exists, if not offer or create
if not exist "venv\" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Install requirements if needed
if not exist "requirements_installed.flag" (
    echo [INFO] Installing required libraries from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo Done > requirements_installed.flag
        echo [INFO] Dependencies installed successfully!
    ) else (
        echo [WARNING] Some dependencies had warnings or issues during install.
        echo If PyAudio failed on Windows, run:
        echo   pip install pipwin
        echo   pipwin install pyaudio
    )
    echo.
)

:: Launch Aevrix
echo [INFO] Starting Aevrix...
echo.
python main.py

echo.
echo ========================================================
echo Aevrix session closed. Press any key to exit.
echo ========================================================
pause >nul
