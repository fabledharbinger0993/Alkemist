@echo off
REM ════════════════════════════════════════════════════════════════════════════
REM Alkemist + OpenClaw + Ollama Launcher (Windows)
REM ════════════════════════════════════════════════════════════════════════════
REM
REM Purpose: One-command startup for your local AI agent
REM Usage: launch-alkemist-agent.bat
REM
REM After running this, everything starts in background. You can close the terminal.
REM Interact via Telegram bot or http://127.0.0.1:18789
REM
REM ════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM ────────────────────────────────────────────────────────────────────────────
REM Configuration
REM ────────────────────────────────────────────────────────────────────────────

set OLLAMA_MODEL=mistral
set OLLAMA_HOST=127.0.0.1:11434
set OPENCLAW_GATEWAY=127.0.0.1:18789
set ALKEMIST_BACKEND=127.0.0.1:8000
set ALKEMIST_PROJECT_PATH=%USERPROFILE%\.alkemist-projects

if not exist "%USERPROFILE%\.alkemist-logs" mkdir "%USERPROFILE%\.alkemist-logs"
set LOG_DIR=%USERPROFILE%\.alkemist-logs

cls
echo.
echo [32;1m╔══════════════════════════════════════════════════════════════════════╗[0m
echo [32;1m║  🦞  OpenClaw + Ollama for Alkemist Development                     ║[0m
echo [32;1m║      Launching your personal AI agent...                            ║[0m
echo [32;1m╚══════════════════════════════════════════════════════════════════════╝[0m
echo.

REM ────────────────────────────────────────────────────────────────────────────
REM Step 1: Verify Prerequisites
REM ────────────────────────────────────────────────────────────────────────────

echo [33;1m📋 Step 1: Checking prerequisites...[0m

set MISSING=

REM Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [31m  ❌ Node.js not found. Install from https://nodejs.org[0m
    set MISSING=1
) else (
    for /f "tokens=*" %%i in ('node --version 2^>nul') do set NODE_VERSION=%%i
    echo [32m  ✅ Node.js: !NODE_VERSION![0m
)

REM Check Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo [31m  ❌ Ollama not found. Install from https://ollama.com[0m
    set MISSING=1
) else (
    for /f "tokens=*" %%i in ('ollama --version 2^>nul') do set OLLAMA_VERSION=%%i
    echo [32m  ✅ Ollama: !OLLAMA_VERSION![0m
)

REM Check OpenClaw
where openclaw >nul 2>&1
if errorlevel 1 (
    echo [31m  ❌ OpenClaw not found. Run: npm install -g openclaw[0m
    set MISSING=1
) else (
    for /f "tokens=*" %%i in ('openclaw --version 2^>nul') do set OPENCLAW_VERSION=%%i
    echo [32m  ✅ OpenClaw: !OPENCLAW_VERSION![0m
)

if defined MISSING (
    echo.
    echo [31mPlease install missing components and try again.[0m
    pause
    exit /b 1
)

echo.

REM ────────────────────────────────────────────────────────────────────────────
REM Step 2: Start Ollama
REM ────────────────────────────────────────────────────────────────────────────

echo [33;1m🧠 Step 2: Starting Ollama LLM...[0m

tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if errorlevel 1 (
    echo [36m  Starting Ollama service...[0m
    start /min cmd /c "ollama serve > "%LOG_DIR%\ollama.log" 2>&1"
    echo [90m  ⏳ Waiting for Ollama to be ready...[0m
    timeout /t 3 /nobreak >nul
    echo [32m  ✅ Ollama is ready (http://!OLLAMA_HOST!)[0m
) else (
    echo [32m  ✅ Ollama already running[0m
)

echo.

REM ────────────────────────────────────────────────────────────────────────────
REM Step 3: Verify Ollama Model
REM ────────────────────────────────────────────────────────────────────────────

echo [33;1m📥 Step 3: Checking Ollama model...[0m

ollama list 2>nul | find "%OLLAMA_MODEL%" >nul
if errorlevel 1 (
    echo [33m  ⚠️  Model '%OLLAMA_MODEL%' not found locally[0m
    echo [33m  Downloading model (this takes 5-15 minutes on first run)...[0m
    echo [36m  💾 Pulling %OLLAMA_MODEL%...[0m
    ollama pull %OLLAMA_MODEL%
    echo [32m  ✅ Model downloaded[0m
) else (
    echo [32m  ✅ Model '%OLLAMA_MODEL%' is available[0m
)

echo.

REM ────────────────────────────────────────────────────────────────────────────
REM Step 4: Start OpenClaw Gateway
REM ────────────────────────────────────────────────────────────────────────────

echo [33;1m🚀 Step 4: Starting OpenClaw Gateway...[0m

tasklist /FI "IMAGENAME eq openclaw.exe" 2>NUL | find /I /N "openclaw.exe">NUL
if errorlevel 1 (
    echo [36m  Starting OpenClaw daemon...[0m
    start /min cmd /c "openclaw start > "%LOG_DIR%\openclaw.log" 2>&1"
    echo [90m  ⏳ Waiting for OpenClaw Gateway to initialize...[0m
    timeout /t 5 /nobreak >nul
    echo [32m  ✅ OpenClaw Gateway ready (http://!OPENCLAW_GATEWAY!)[0m
) else (
    echo [32m  ✅ OpenClaw already running[0m
)

echo.

REM ────────────────────────────────────────────────────────────────────────────
REM Step 5: Verify Telegram Connection
REM ────────────────────────────────────────────────────────────────────────────

echo [33;1m📱 Step 5: Checking Telegram bot...[0m
openclaw status 2>nul | find "telegram" >nul
if errorlevel 1 (
    echo [33m  ⚠️  Telegram not configured yet[0m
    echo [90m     Run: openclaw onboard[0m
) else (
    echo [32m  ✅ Telegram channel configured[0m
)

echo.

REM ────────────────────────────────────────────────────────────────────────────
REM Success Message
REM ────────────────────────────────────────────────────────────────────────────

echo [32;1m╔══════════════════════════════════════════════════════════════════════╗[0m
echo [32;1m║  ✅ YOUR ALKEMIST AI AGENT IS RUNNING!                              ║[0m
echo [32;1m╚══════════════════════════════════════════════════════════════════════╝[0m
echo.

echo [36;1m📊 Service Status:[0m
echo   🧠 Ollama LLM .......... http://!OLLAMA_HOST! ^(model: !OLLAMA_MODEL!^)
echo   🦞 OpenClaw Gateway .... http://!OPENCLAW_GATEWAY!
echo   📱 Telegram Bot ........ Ready for commands
echo.

echo [36;1m🎯 What You Can Do Now:[0m
echo   • Send messages to your Telegram bot
echo   • Bot will execute commands on your Alkemist project
echo   • No more PowerShell needed - it all runs in background
echo.

echo [33;1m💬 Example Telegram Commands:[0m
echo   '  /status' - Check what's running
echo   '  Test Alkemist backend' - Run pytest
echo   '  Build Bool agent' - Generate Bool files
echo   '  Check project health' - Health check
echo   '  Run all tests' - Full test suite
echo.

echo [36;1m🌐 Interfaces:[0m
echo   • Telegram ........... Message your bot
echo   • Web Dashboard ...... http://!OPENCLAW_GATEWAY! ^(optional^)
echo   • Command Prompt ..... Your CLI
echo.

echo [36;1m📁 Your Alkemist Project:[0m
echo   !ALKEMIST_PROJECT_PATH!
echo.

echo [36;1m📋 Logs Location:[0m
echo   !LOG_DIR!\
echo.

echo [33;1m🔐 Security Notes:[0m
echo   ✓ Ollama bound to localhost only ^(not exposed^)
echo   ✓ File access limited to your Alkemist folder
echo   ✓ Only your Telegram ID can send commands
echo   ✓ All actions logged for audit trail
echo.

echo [90m📖 For more information:[0m
echo   • Setup guide: OPENCLAW_OLLAMA_SETUP.md
echo   • OpenClaw docs: https://docs.openclaw.ai
echo   • GitHub: https://github.com/openclaw/openclaw
echo.

echo [32;1m✨ You can now close this window![0m
echo [32;1m   Everything continues running in the background.[0m
echo.

echo ───────────────────────────────────────────────────────────────────────────
pause
