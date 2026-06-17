@echo off
echo ========================================================
echo   PHONOS.AI - DEVELOPMENT SERVER LAUNCHER
echo ========================================================
echo.

echo [1/2] Launching FastAPI Backend (Port 8000)...
start "Phonos.ai Backend (FastAPI)" cmd /k "cd apps\api && set PYTHONPATH=. && .\.venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching Next.js Frontend (Port 3000)...
start "Phonos.ai Frontend (Next.js)" cmd /k "cd apps\web && npm run dev"

echo.
echo Servers are booting up in separate terminal windows!
echo - Frontend will be available at: http://localhost:3000
echo - Backend API will be available at: http://localhost:8000
echo - API Docs will be available at: http://localhost:8000/docs
echo.
pause
