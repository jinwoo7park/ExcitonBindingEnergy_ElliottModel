#!/bin/bash

# 백엔드와 프론트엔드를 동시에 실행하는 스크립트

echo "🚀 Starting F-sum Rule Fitting services..."

# 백엔드 실행 (백그라운드)
echo "📡 Starting FastAPI backend on port 8000..."
python3 api.py &
BACKEND_PID=$!

# 잠시 대기
sleep 2

# 프론트엔드 실행
echo "🎨 Starting React frontend on port 3000..."
cd /workspace
pnpm dev &
FRONTEND_PID=$!

echo "✅ Services started!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# 종료 시그널 처리
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# 프로세스가 종료될 때까지 대기
wait
