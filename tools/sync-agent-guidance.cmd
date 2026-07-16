@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync-agent-guidance.ps1" -ProjectRoot "%CD%" %*
exit /b %ERRORLEVEL%
