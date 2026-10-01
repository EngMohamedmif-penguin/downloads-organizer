@echo off
setlocal
cd /d "%~dp0"
python -m pip install watchdog
python downloads_organizer_gui.py
if errorlevel 1 pause
