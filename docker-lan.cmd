@echo off
REM From PowerShell in project root run:  .\docker-lan.cmd   (leading .\ required)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\docker-up-lan.ps1" %*
