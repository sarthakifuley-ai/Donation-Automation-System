@echo off
title NGO Donation Chatbot - Stopping...
color 0C

echo.
echo  ==========================================
echo   Stopping NGO Donation Chatbot...
echo  ==========================================
echo.

:: Kill the WhatsApp service window
taskkill /fi "WindowTitle eq WhatsApp Service*" /f >nul 2>&1

:: Kill the Python server window
taskkill /fi "WindowTitle eq Python Server*" /f >nul 2>&1

:: Also kill any leftover node or uvicorn processes
taskkill /im node.exe /f >nul 2>&1
taskkill /im python.exe /f >nul 2>&1

echo  All services stopped successfully.
echo.
echo  You can now close this window.
echo.
pause
