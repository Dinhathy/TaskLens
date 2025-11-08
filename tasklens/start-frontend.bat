@echo off
echo ================================
echo Starting TaskLens Frontend
echo ================================
echo.

REM Navigate to frontend directory
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Dependencies not installed. Installing now...
    call npm install
)

REM Start Vite dev server
echo Starting Vite dev server...
echo Frontend will be available at: http://localhost:8080
echo.

npm run dev
