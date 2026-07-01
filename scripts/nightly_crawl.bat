@echo off
REM MuunganoGPT — nightly official source crawl
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0nightly_crawl.ps1"
exit /b %ERRORLEVEL%
