@echo off
REM Wrapper to run the PowerShell testlocally script from Explorer or cmd.exe
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0testlocally.ps1"