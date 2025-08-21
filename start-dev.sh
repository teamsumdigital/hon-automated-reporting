#!/bin/bash

# Stop existing processes
echo "Stopping existing servers..."
pkill -f "python main.py" 2>/dev/null
pkill -f "python3 main.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start backend
echo "Starting backend on port 8007..."
cd backend && python3 main.py &
BACKEND_PID=$!

# Start frontend  
echo "Starting frontend on port 3007..."
cd frontend && npm run dev &
FRONTEND_PID=$!

# Keep script running and handle cleanup
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait