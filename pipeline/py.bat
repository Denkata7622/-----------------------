@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONLEGACYWINDOWSSTDIO=0
"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" %*