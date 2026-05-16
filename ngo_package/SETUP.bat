@echo off
title NGO Donation Chatbot - First Time Setup
color 0B

echo.
echo  ==========================================
echo   YUVA NGO - First Time Setup
echo  ==========================================
echo.

:: ── Check Python ──
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed!
    echo.
    echo  1. Go to https://python.org/downloads
    echo  2. Download the latest version
    echo  3. During install, CHECK "Add Python to PATH"
    echo  4. Rerun this file after installing
    echo.
    pause
    exit
)

echo  [OK] Python found:
python --version
echo.

:: ── Check Node.js ──
node --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Node.js is not installed!
    echo.
    echo  1. Go to https://nodejs.org
    echo  2. Download the LTS version
    echo  3. Install it, then rerun this file
    echo.
    pause
    exit
)

echo  [OK] Node.js found:
node --version
echo.

:: ── Clean broken Puppeteer Chrome cache (common issue) ──
echo  Cleaning Puppeteer browser cache to avoid conflicts...
if exist "%USERPROFILE%\.cache\puppeteer\chrome" (
    rmdir /s /q "%USERPROFILE%\.cache\puppeteer\chrome"
    echo  [OK] Old Puppeteer cache cleared.
) else (
    echo  [OK] No old cache found, skipping.
)
echo.

:: ── Detect system browser ──
echo  Detecting available browser...
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo  [OK] Microsoft Edge found - will be used automatically.
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo  [OK] Microsoft Edge found - will be used automatically.
) else if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo  [OK] Google Chrome found - will be used automatically.
) else (
    echo  [WARN] No system browser found.
    echo  Installing Puppeteer's own Chrome browser...
    cd /d "%~dp0whatsapp-service"
    call npx puppeteer browsers install chrome
    cd /d "%~dp0"
)
echo.

:: ── Install Python packages ──
echo  Installing Python packages (fastapi, uvicorn, pandas, etc.)...
python -m pip install --upgrade pip -q
python -m pip install fastapi "uvicorn[standard]" pandas openpyxl requests watchdog -q
if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to install Python packages.
    echo  Try running this file as Administrator.
    pause
    exit
)
echo  [OK] Python packages installed.
echo.

:: ── Install Node packages ──
echo  Installing WhatsApp service packages...
cd /d "%~dp0whatsapp-service"
call npm install
if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to install Node packages.
    pause
    exit
)
cd /d "%~dp0"
echo  [OK] Node packages installed.
echo.

echo  ==========================================
echo   Setup Complete!
echo  ==========================================
echo.
echo  Now run START.bat to launch the app.
echo.
pause
