#!/bin/bash

# Script para reiniciar el servidor FastAPI de forma rápida
echo "🔄 Stopping portfolio backend server..."
pkill -f "uvicorn.*app.main:app" || echo "No server running"

echo "⏱️  Waiting 2 seconds..."
sleep 2

echo "🚀 Starting portfolio backend server..."
cd /home/miki/portfolio-backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &

echo "✅ Server started! Check status with: curl -I http://localhost:8000/"
echo "📋 Logs: tail -f /home/miki/portfolio-backend/server.log"