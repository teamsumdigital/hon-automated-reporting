#!/bin/bash

# Script to activate virtual environment and start HON backend server

echo "🚀 Starting HON Automated Reporting Backend Server"

# Change to backend directory
cd /Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/backend

# Try different virtual environments
if [ -d "venv_new/bin" ]; then
    echo "📦 Using venv_new virtual environment"
    source venv_new/bin/activate
elif [ -d "venv/bin" ]; then
    echo "📦 Using venv virtual environment"
    source venv/bin/activate
elif [ -d "env/bin" ]; then
    echo "📦 Using env virtual environment"
    source env/bin/activate
elif [ -d ".venv/bin" ]; then
    echo "📦 Using .venv virtual environment"
    source .venv/bin/activate
else
    echo "❌ No virtual environment found!"
    echo "Available directories:"
    ls -la | grep -E "(venv|env)"
    exit 1
fi

echo "✅ Virtual environment activated"
echo "🐍 Python path: $(which python)"
echo "📦 Pip path: $(which pip)"

# Install dependencies if needed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "🔧 Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Check if server is already running
if curl -s http://localhost:8007/health > /dev/null; then
    echo "⚠️ Server is already running on port 8007"
    echo "✅ Backend ready at http://localhost:8007"
else
    echo "🚀 Starting server on port 8007..."
    python -m uvicorn main:app --reload --port 8007
fi