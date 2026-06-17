@echo off
echo ========================================================
echo   FONE.AI - DEVELOPMENT SERVER LAUNCHER
echo ========================================================
echo.

echo [1/3] Starting Database Services (Docker)...
docker-compose up -d
echo.

echo [2/3] Launching FastAPI Backend (Port 8000)...
start "Fone.ai Backend (FastAPI)" cmd /k "cd apps\api && set PYTHONPATH=. && set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fone_ai && .\.venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching Next.js Frontend (Port 3000)...
start "Fone.ai Frontend (Next.js)" cmd /k "cd apps\web && npm run dev"

echo.
echo Servers are booting up in separate terminal windows!
echo - Frontend will be available at: http://localhost:3000
echo - Backend API will be available at: http://localhost:8000
echo.
pause
