@echo off
echo IntelliFlow Logistics AI - Windows Startup Script
echo =============================================

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if virtual environment exists, create if not
if not exist intelliflow_env (
    echo Creating virtual environment...
    python -m venv intelliflow_env
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call intelliflow_env\Scripts\activate

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

:: Run Windows fixes
echo Running Windows fixes...
call fix-windows.bat

:: Start services
echo.
echo Starting services...
echo.
echo IMPORTANT: Two command windows will open:
echo 1. Backend API (FastAPI)
echo 2. Frontend Dashboard (Streamlit)
echo.
echo Please do not close these windows while using the application.
echo.
echo Press any key to start the services...
pause >nul

:: Start backend in a new window
start cmd /k "title IntelliFlow Backend && call intelliflow_env\Scripts\activate && python -m backend.api.main"

:: Wait a moment for backend to start
timeout /t 5 /nobreak >nul

:: Start frontend in a new window
start cmd /k "title IntelliFlow Frontend && call intelliflow_env\Scripts\activate && streamlit run frontend/dashboard.py"

:: Open browser
echo.
echo Opening dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:8501

echo.
echo Services started successfully!
echo.
echo - Frontend Dashboard: http://localhost:8501
echo - Backend API: http://localhost:9000
echo - API Documentation: http://localhost:9000/docs
echo.
echo Press any key to exit this script (services will continue running)...
pause >nul