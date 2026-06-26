#!/bin/bash
# Launch script for Pantry Pilot (FastAPI Backend + Svelte Frontend)

# Function to stop both processes on exit
cleanup() {
  echo -e "\n🛑 Shutting down Pantry Pilot servers..."
  if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
  fi
  if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null
  fi
  exit
}

# Trap Ctrl+C (SIGINT) and terminal termination (SIGTERM)
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Pantry Pilot Google ADK API Backend..."
source backend/venv/bin/activate
python backend/main.py &
BACKEND_PID=$!

# Wait a brief moment for backend port to bind
sleep 1.5

echo "⚡ Starting Pantry Pilot Svelte Frontend..."
npm run dev &
FRONTEND_PID=$!

echo "=================================================="
echo "🎯 Both servers are now running."
echo "   - Frontend: http://localhost:5173"
echo "   - Backend:  http://localhost:8000"
echo "🛑 Press Ctrl+C to terminate both servers safely."
echo "=================================================="

# Wait for background jobs to complete
wait
