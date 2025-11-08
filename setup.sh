#!/bin/bash

echo "================================"
echo "TaskLens Backend Setup Script"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

echo "[1/5] Python detected"
python3 --version
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[2/5] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[2/5] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "[5/5] Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "================================"
    echo "IMPORTANT: Configure your API key"
    echo "================================"
    echo "Edit .env file and add your NVIDIA_API_KEY"
    echo "Get your API key from: https://build.nvidia.com/"
    echo ""
else
    echo "[5/5] .env file already exists"
fi

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your NVIDIA_API_KEY"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python test_setup.py"
echo "4. Run: uvicorn main:app --reload"
echo ""
echo "The server will be available at http://localhost:8000"
echo "API docs will be at http://localhost:8000/docs"
echo ""
