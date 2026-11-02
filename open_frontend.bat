@echo off
title Aevrix AI Web Assistant
cd /d "%~dp0"

echo [1/2] Opening in Google Chrome...
start chrome "http://localhost:5000" 2>nul || start msedge "http://localhost:5000" 2>nul || start "" "http://localhost:5000"

echo [2/2] Starting backend server...
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe server.py
) else (
    python server.py
)
pause
