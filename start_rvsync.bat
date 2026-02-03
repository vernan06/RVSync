@echo off
cd /d "%~dp0"

echo ==============================================
echo       🚀 Starting RVSync Platform 🚀
echo ==============================================
echo.

:: Check for virtual environment
set "VENV_PYTHON=.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    echo [Info] Found Virtual Environment. Using it.
    set "PY_CMD=%VENV_PYTHON%"
) else (
    echo [Warning] .venv not found. Using global System Python.
    set "PY_CMD=python"
)

echo [1/3] Starting Backend API (Port 8080)...
start "RVSync Backend" /min cmd /k "cd backend && %PY_CMD% -m uvicorn app.main:app --host 0.0.0.0 --port 8080"

echo [2/3] Starting Frontend App (Port 3000)...
start "RVSync Frontend" /min cmd /k "cd frontend && %PY_CMD% -m http.server 3000"

echo [3/3] Opening Dashboard in Browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ✅ Success! The platform is running.
echo.
echo    Backend:  http://localhost:8080/docs
echo    Frontend: http://localhost:3000
echo.
echo    (Close the minimized command windows to stop the servers)
pause
