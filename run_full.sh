#!/usr/bin/env bash
# Festival Robot — full local demo (backend + fake arduino + frontend dev server).
# Streams logs from all three into stdout with prefixes; Ctrl+C tears them all down.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT/app/backend"
FRONTEND_DIR="$ROOT/app/frontend"
ARDUINO_MODE="${ARDUINO_MODE:-normal}"

LOG_DIR="$ROOT/.run-logs"
mkdir -p "$LOG_DIR"

# ---------- pre-flight checks ------------------------------------------------

require() {
  command -v "$1" >/dev/null 2>&1 || { echo "✗ missing: $1"; exit 1; }
}
require python
require bun

port_busy() {
  lsof -Pi ":$1" -sTCP:LISTEN -t >/dev/null 2>&1
}

for port in 8000 5173; do
  if port_busy "$port"; then
    echo "✗ port $port already in use — kill it: lsof -ti :$port | xargs kill -9"
    exit 1
  fi
done

# ---------- launch -----------------------------------------------------------

PIDS=()
cleanup() {
  echo
  echo "→ stopping demo..."
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  echo "✓ stopped"
}
trap cleanup EXIT INT TERM

prefix() {
  local tag="$1"
  sed -u "s/^/[$tag] /"
}

echo "→ backend  (uvicorn :8000)"
( cd "$BACKEND_DIR" && python main.py 2>&1 | prefix backend ) &
PIDS+=($!)

# Wait for backend to be reachable before starting the rest.
for _ in $(seq 1 40); do
  if curl -sf http://localhost:8000/health >/dev/null 2>&1; then break; fi
  sleep 0.25
done
if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
  echo "✗ backend never came up on :8000 — check the [backend] log lines above"
  exit 1
fi
echo "  ready."

echo "→ fake arduino  (mode=$ARDUINO_MODE, 1 Hz)"
( cd "$BACKEND_DIR" && python fake_arduino.py --mode "$ARDUINO_MODE" --interval 1.0 2>&1 | prefix arduino ) &
PIDS+=($!)

echo "→ frontend  (vite :5173)"
( cd "$FRONTEND_DIR" && bun run dev 2>&1 | prefix frontend ) &
PIDS+=($!)

echo
echo "  open  http://localhost:5173"
echo "  api   http://localhost:8000/docs"
echo "  Ctrl+C to stop everything."
echo

wait
