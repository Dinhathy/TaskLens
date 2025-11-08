#!/bin/bash

echo "================================"
echo "Starting TaskLens Frontend"
echo "================================"
echo ""

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not installed. Installing now..."
    npm install
fi

# Start Vite dev server
echo "Starting Vite dev server..."
echo "Frontend will be available at: http://localhost:8080"
echo ""

npm run dev
