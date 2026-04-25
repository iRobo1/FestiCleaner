#!/bin/bash

# Festival Robot Demo - Hackathon Edition
# Run this for a quick 3-minute demo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  🤖 Festival Robot Backend - Hackathon Demo            ║"
echo "║  Settings: 1920×1080 (Full HD), 3-minute demo mode    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8000 already in use!"
    echo "   Kill existing process: lsof -ti :8000 | xargs kill -9"
    exit 1
fi

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Start backend
echo "1️⃣  Starting Backend Server..."
cd "$SCRIPT_DIR/app/backend"
python main.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend started
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "   ✓ Backend running on http://localhost:8000"
echo ""

# Start fake Arduino
echo "2️⃣  Starting Fake Arduino Simulator..."
echo "   Mode: normal (demo-optimized)"
echo "   Duration: 3 minutes (180 seconds)"
echo "   Update rate: 1 Hz"
echo ""
echo "   You will see:"
echo "   • Battery: 95% → ~65% (visible drain for judges)"
echo "   • Position: Random walk across 10×10m area"
echo "   • Map: Grows as robot moves (grid coverage)"
echo ""

python fake_arduino.py \
    --mode normal \
    --duration 180 \
    --interval 1.0

echo ""
echo "3️⃣  Demo Complete! ✓"
echo ""
echo "Demo Results:"
echo "   • 180 telemetry readings sent"
echo "   • ~30% of map covered (demo-optimized)"
echo "   • Database: robot_data.db"
echo ""

# Cleanup
echo "🧹 Cleaning up..."
kill $BACKEND_PID 2>/dev/null || true
wait $BACKEND_PID 2>/dev/null || true

echo ""
echo "📊 What judges saw:"
echo "   • Real-time robot telemetry dashboard"
echo "   • Live camera feed (or placeholder)"
echo "   • Dynamic map building as robot moves"
echo "   • Battery & temperature monitoring"
echo ""
echo "🎉 Ready for next demo run!"
echo ""
