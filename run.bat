@echo off
title AEVRIX AI - Voice & Intelligence Assistant
color 0b
cd /d "%~dp0"

echo =======================================================================
echo         AEVRIX AI // CHATGPT & GEMINI STYLE VOICE FRONTEND
echo =======================================================================
echo.

:: 1. Verify Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not found in your system PATH!
    echo Please download and install Python from: https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

:: 2. Setup Virtual Environment (venv) if not already created
if not exist "venv\" (
    echo [SETUP] Creating isolated Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
)

:: 3. Activate Virtual Environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: 4. Install Dependencies if needed
if not exist "requirements_installed.flag" (
    echo [SETUP] Installing required dependencies...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo Done > requirements_installed.flag
        echo [OK] All dependencies installed successfully!
    ) else (
        echo [WARNING] Some dependencies had install warnings.
    )
    echo.
)

:: 5. Launch in Google Chrome & Start Server
echo [LAUNCH] Opening Google Chrome to Aevrix AI...
start chrome "http://localhost:5000" 2>nul || start msedge "http://localhost:5000" 2>nul

echo [LAUNCH] Starting Aevrix backend engine...
echo.
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) else (
    python main.py
)

echo.
echo =======================================================================
echo Aevrix session closed. Press any key to exit.
echo =======================================================================
pause >nul
