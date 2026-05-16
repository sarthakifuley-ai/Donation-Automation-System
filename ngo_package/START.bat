@echo off
title YUVA NGO - Starting...
color 0A
cd /d "%~dp0"

echo.
echo  ==========================================
echo   YUVA Rural Association - Donation Chatbot
echo  ==========================================
echo.

:: ── Check Node.js ──────────────────────────────────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Node.js is not installed!
    echo.
    echo  Please install Node.js from https://nodejs.org
    echo  Download the LTS version and install it.
    echo.
    pause
    exit
)
echo  [OK] Node.js found.

:: ── Check Python ───────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed!
    echo.
    echo  Please install Python from https://python.org
    echo  During install, CHECK "Add Python to PATH"
    echo.
    pause
    exit
)
echo  [OK] Python found.
echo.

:: ── Install Node packages if missing ───────────────────────────────────────
if not exist "%~dp0whatsapp-service\node_modules\whatsapp-web.js" (
    echo  Installing WhatsApp packages (first time only, please wait)...
    cd /d "%~dp0whatsapp-service"
    call npm install
    if errorlevel 1 (
        echo.
        echo  [ERROR] npm install failed. Check your internet connection.
        pause
        exit
    )
    cd /d "%~dp0"
    echo  [OK] WhatsApp packages installed.
    echo.
)

:: ── Install Python packages if missing ─────────────────────────────────────
python -c "import fastapi, uvicorn, pandas, openpyxl, requests, watchdog" >nul 2>&1
if errorlevel 1 (
    echo  Installing Python packages (first time only, please wait)...
    python -m pip install fastapi "uvicorn[standard]" pandas openpyxl requests watchdog -q
    if errorlevel 1 (
        echo.
        echo  [ERROR] Python packages failed to install.
        echo  Try running this file as Administrator.
        pause
        exit
    )
    echo  [OK] Python packages installed.
    echo.
)

:: ── Clean broken Puppeteer cache if chrome.exe is missing ──────────────────
if exist "%USERPROFILE%\.cache\puppeteer\chrome" (
    if not exist "%USERPROFILE%\.cache\puppeteer\chrome\win64-146.0.7680.153\chrome-win64\chrome.exe" (
        echo  Cleaning broken browser cache...
        rmdir /s /q "%USERPROFILE%\.cache\puppeteer\chrome" >nul 2>&1
    )
)

:: ── Start WhatsApp Service ──────────────────────────────────────────────────
echo  Starting WhatsApp Service...
start "WhatsApp Service" cmd /k "cd /d %~dp0whatsapp-service && node index.js"

:: ── Wait for WhatsApp service to initialize ────────────────────────────────
echo  Waiting for services to start...
timeout /t 6 /nobreak >nul

:: ── Start Python Server ─────────────────────────────────────────────────────
echo  Starting Python Server...
start "Python Server" cmd /k "cd /d %~dp0 && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: ── Wait for Python server ──────────────────────────────────────────────────
timeout /t 5 /nobreak >nul

:: ── Open website ────────────────────────────────────────────────────────────
echo  Opening website...
start "" "%~dp0frontend\index.html"

echo.
echo  ==========================================
echo   Everything is running!
echo  ==========================================
echo.
echo  FIRST TIME: Look at the "WhatsApp Service" window.
echo  If a QR code appears, scan it with WhatsApp:
echo    Phone: WhatsApp - Menu - Linked Devices - Link a Device
echo.
echo  After scanning once, you never need to scan again.
echo.
echo  To STOP everything, run STOP.bat
echo.
pause
