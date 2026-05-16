@echo off
title Change WhatsApp Account
color 0E

echo.
echo  ==========================================
echo   Change WhatsApp Account
echo  ==========================================
echo.
echo  This will log out the current WhatsApp account
echo  so you can scan a new QR code with a different number.
echo.
set /p confirm="Are you sure? Type YES and press Enter: "

if /i not "%confirm%"=="YES" (
    echo  Cancelled. No changes made.
    pause
    exit
)

:: Stop services first
taskkill /fi "WindowTitle eq WhatsApp Service*" /f >nul 2>&1
taskkill /im node.exe /f >nul 2>&1
timeout /t 2 /nobreak >nul

:: Delete saved WhatsApp session
if exist "whatsapp-service\.wwebjs_auth" (
    rmdir /s /q "whatsapp-service\.wwebjs_auth"
    echo  Old WhatsApp session deleted.
) else (
    echo  No session found, already logged out.
)

echo.
echo  Done! Now run START.bat and scan the QR code
echo  with the new WhatsApp number.
echo.
pause
