@echo off
title νόησις Launcher
color 0A

echo ========================================
echo   νόησις Local Development Launcher
echo ========================================
echo.

REM Get the directory where this batch file is located
set WORKSPACE=%~dp0

echo Workspace: %WORKSPACE%
echo.
echo Starting servers...
echo.

REM Start site server on port 8000
start "Site Server - Port 8000" cmd /k "cd /d "%WORKSPACE%site" && python -m http.server 8000"

REM Wait for first server
timeout /t 2 /nobreak >nul

REM Start canvas server on port 8001  
start "Canvas Server - Port 8001" cmd /k "cd /d "%WORKSPACE%canvas" && python -m http.server 8001"

REM Wait for servers to initialize
echo Waiting for servers to start...
timeout /t 4 /nobreak >nul

echo.
echo Opening browsers...
echo.

REM Open landing page
start "" "http://localhost:8000"

REM Wait a moment
timeout /t 1 /nobreak >nul

REM Open Canvas IDE
start "" "http://localhost:8001"

echo.
echo ========================================
echo   SERVERS RUNNING:
echo.
echo   Landing Page: http://localhost:8000
echo   Canvas IDE:   http://localhost:8001
echo.
echo   Two terminal windows opened.
echo   Close those windows to stop servers.
echo ========================================
echo.
echo Press any key to exit this launcher...
pause >nul
