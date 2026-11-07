@echo off
rem Double-click to fetch finished videos into Documents\Animated Long Video 1st Channel
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0fetch_videos.ps1" %*
pause
