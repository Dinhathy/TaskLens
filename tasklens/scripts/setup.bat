@echo off
echo ================================
echo TaskLens Backend Setup Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python detected
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/5] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/5] Installing dependencies...
pip install -r requirements.txt
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [5/5] Creating .env file from template...
    copy .env.example .env
    echo.
    echo ================================
    echo IMPORTANT: Configure your API key
    echo ================================
    echo Edit .env file and add your NVIDIA_API_KEY
    echo Get your API key from: https://build.nvidia.com/
    echo.
) else (
    echo [5/5] .env file already exists
)

echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit .env and add your NVIDIA_API_KEY
echo 2. Run: venv\Scripts\activate
echo 3. Run: python test_setup.py
echo 4. Run: uvicorn main:app --reload
echo.
echo The server will be available at http://localhost:8000
echo API docs will be at http://localhost:8000/docs
echo.

pause
