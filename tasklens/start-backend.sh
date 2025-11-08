#!/bin/bash

echo "================================"
echo "Starting TaskLens Backend"
echo "================================"
echo ""

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "  cd backend"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please create .env from .env.example and add your NVIDIA_API_KEY"
    exit 1
fi

# Start FastAPI server
echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""

# Run from backend directory so Python can find core and services modules
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
