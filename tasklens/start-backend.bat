@echo off
echo ================================
echo Starting TaskLens Backend
echo ================================
echo.

REM Navigate to backend directory
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Please run setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env from .env.example and add your NVIDIA_API_KEY
    exit /b 1
)

REM Start FastAPI server
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.

REM Run from backend directory so Python can find core and services modules
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
