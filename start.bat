@echo off
title TruthLens Launcher
color 0A
echo.
echo  ==========================================
echo   TruthLens ^| Starting Backend + Frontend
echo  ==========================================
echo.

:: ── Backend ───────────────────────────────────
echo  [1/2] Starting FastAPI backend on :8000 ...
start "TruthLens Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

:: wait a moment for backend to boot
timeout /t 3 /nobreak >nul

:: ── Frontend ──────────────────────────────────
echo  [2/2] Starting Next.js frontend on :3000 ...
start "TruthLens Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

:: wait a moment then open browser
timeout /t 5 /nobreak >nul
echo.
echo  Opening http://localhost:3000 in your browser...
start http://localhost:3000

echo.
echo  Both servers are running. Close this window anytime.
pause
