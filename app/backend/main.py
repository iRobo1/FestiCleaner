from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Generator
import numpy as np
import json
import base64
import uvicorn
import asyncio

from database import init_db, get_db
from models import RobotReading, CleanedCell, CameraFrame, MapSnapshot
from camera import CameraStream
from config import settings
import cv2
import os

# Optional Socket.IO bridge to the Arduino. We import lazily so the backend
# still boots cleanly on a checkout where `python-socketio` isn't installed.
try:
    import socketio as sio_lib  # type: ignore[import-untyped]
    _SIO_AVAILABLE = True
except ImportError:
    sio_lib = None  # type: ignore[assignment]
    _SIO_AVAILABLE = False

app = FastAPI(title="Festival Robot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Position(BaseModel):
    x: float
    y: float

class TelemetryReading(BaseModel):
    battery: float
    temperature: float
    humidity: Optional[float] = None
    position: Position
    timestamp: Optional[datetime] = None

# In-memory state (cache)
robot_state = {
    "battery": 85.0,
    "temperature": 22.5,
    "humidity": 55.0,
    "position": {"x": 0.0, "y": 0.0},
    "is_active": True,
}

# Map configuration
GRID_SIZE = settings.GRID_SIZE
CELL_SIZE = settings.CELL_SIZE
map_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

# Camera instance (initialized at startup)
camera: Optional[CameraStream] = None

# WebSocket connections for real-time streaming
active_connections: List[WebSocket] = []

# ── Arduino Socket.IO bridge ─────────────────────────────────────────────────
# When ARDUINO_HOST is set we keep a long-lived Socket.IO client connected to
# the device's WebUI brick (port 7000 by default). /api/robot/shutdown and
# /api/robot/start emit a "power" event on that socket so the device can
# react however it wants. If the connection fails or python-socketio isn't
# installed, we just log and keep going — the dashboard's soft-shutdown
# (in-process is_active flag) still works.
ARDUINO_HOST = os.getenv("ARDUINO_HOST", "").strip()
ARDUINO_WEBUI_PORT = int(os.getenv("ARDUINO_WEBUI_PORT", "7000"))
arduino_sio = (
    sio_lib.Client(reconnection=True, reconnection_delay=2, logger=False)
    if _SIO_AVAILABLE
    else None
)


def signal_arduino(event: str, payload) -> bool:
    """Best-effort Socket.IO emit to the Arduino. Never raises."""
    if not arduino_sio or not arduino_sio.connected:
        return False
    try:
        arduino_sio.emit(event, payload)
        return True
    except Exception as e:
        print(f"⚠ failed to signal Arduino ({event}): {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize database and camera on startup"""
    global camera

    init_db()
    print("✓ Database initialized")

    camera = CameraStream(
        camera_id=settings.CAMERA_ID,
        width=settings.CAMERA_WIDTH,
        height=settings.CAMERA_HEIGHT,
        jpeg_quality=settings.CAMERA_JPEG_QUALITY
    )

    if camera.connect():
        print(f"✓ Camera connected (ID: {settings.CAMERA_ID}, {settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT})")
        camera.start_streaming()
    else:
        print("✗ Camera not available (will use demo mode)")

    if not _SIO_AVAILABLE:
        print("ℹ python-socketio not installed — Arduino bridge disabled "
              "(pip install 'python-socketio[client]==5.11.0' to enable)")
    elif ARDUINO_HOST:
        url = f"http://{ARDUINO_HOST}:{ARDUINO_WEBUI_PORT}"
        try:
            arduino_sio.connect(url, wait_timeout=2)
            print(f"✓ Arduino Socket.IO bridge connected → {url}")
        except Exception as e:
            print(f"✗ Arduino Socket.IO bridge unreachable ({url}): {e}")
    else:
        print("ℹ ARDUINO_HOST not set — running without device signal bridge")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources"""
    camera.disconnect()
    if arduino_sio and arduino_sio.connected:
        try:
            arduino_sio.disconnect()
        except Exception:
            pass

# ============= Robot Telemetry Endpoints =============

@app.get("/")
def read_root():
    return {"msg": "Festival Robot Backend"}

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/robot/status")
def get_status():
    """Get current robot status"""
    return robot_state

@app.post("/api/robot/shutdown")
def shutdown_robot():
    """Mark the robot as offline. Telemetry POSTs are rejected with 423 until
    /api/robot/start is called. If ARDUINO_HOST is configured, also emits a
    `power=False` Socket.IO event to the device — what the device does with
    that signal is up to its own code."""
    robot_state["is_active"] = False
    robot_state["last_update"] = datetime.now().isoformat()
    signaled = signal_arduino("power", False)
    return {
        "is_active": False,
        "shutdown_at": robot_state["last_update"],
        "device_signaled": signaled,
    }


@app.post("/api/robot/start")
def start_robot():
    """Re-arm the robot. Telemetry POSTs are accepted again. If ARDUINO_HOST
    is configured, also emits `power=True` to the device."""
    robot_state["is_active"] = True
    robot_state["last_update"] = datetime.now().isoformat()
    signaled = signal_arduino("power", True)
    return {
        "is_active": True,
        "started_at": robot_state["last_update"],
        "device_signaled": signaled,
    }


@app.post("/api/robot/telemetry")
def post_telemetry(reading: TelemetryReading, db: Session = Depends(get_db)):
    """Accept and store telemetry data from robot.
    Returns 423 Locked while the robot is in shutdown state."""
    if not robot_state.get("is_active", True):
        raise HTTPException(status_code=423, detail="Robot is powered off")

    robot_state["battery"] = reading.battery
    robot_state["temperature"] = reading.temperature
    if reading.humidity is not None:
        robot_state["humidity"] = reading.humidity
    robot_state["position"] = reading.position.dict()
    robot_state["last_update"] = datetime.now().isoformat()

    # Store in database
    db_reading = RobotReading(
        battery=reading.battery,
        temperature=reading.temperature,
        humidity=reading.humidity,
        position_x=reading.position.x,
        position_y=reading.position.y,
        timestamp=reading.timestamp or datetime.utcnow()
    )
    db.add(db_reading)
    db.commit()

    update_map(reading.position, db)
    return {"acknowledged": True, "id": db_reading.id}

@app.get("/api/history/telemetry")
def get_telemetry_history(limit: int = 100, db: Session = Depends(get_db)):
    """Get historical telemetry data from database"""
    readings = db.query(RobotReading).order_by(RobotReading.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "battery": r.battery,
            "temperature": r.temperature,
            "position": {"x": r.position_x, "y": r.position_y},
            "timestamp": r.timestamp.isoformat()
        }
        for r in reversed(readings)
    ]

# ============= Map Endpoints =============

@app.get("/api/map")
def get_map(db: Session = Depends(get_db)):
    """Get current map state"""
    cleaned_cells = np.count_nonzero(map_grid)
    total_cells = GRID_SIZE * GRID_SIZE
    coverage = (cleaned_cells / total_cells) * 100

    return {
        "grid": map_grid.tolist(),
        "cleaned_cells": int(cleaned_cells),
        "total_area_m2": (GRID_SIZE * CELL_SIZE) ** 2,
        "coverage_percent": round(coverage, 2),
        "cell_size_m": CELL_SIZE,
        "grid_dimensions": {"width": GRID_SIZE, "height": GRID_SIZE}
    }

@app.post("/api/map/update")
def update_map_endpoint(position: Position, db: Session = Depends(get_db)):
    """Update map with current position"""
    update_map(position, db)
    cleaned = np.count_nonzero(map_grid)
    coverage = (cleaned / (GRID_SIZE * GRID_SIZE)) * 100
    return {"updated": True, "coverage_percent": round(coverage, 2)}

def update_map(position: Position, db: Session = Depends(get_db)):
    """Mark cell as cleaned in the map grid and store in database"""
    grid_x = int(position.x / CELL_SIZE)
    grid_y = int(position.y / CELL_SIZE)

    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
        map_grid[grid_y, grid_x] = 1

        # Store cleaned cell in database
        cleaned_cell = CleanedCell(
            grid_x=grid_x,
            grid_y=grid_y,
            cell_size=CELL_SIZE
        )
        db.add(cleaned_cell)
        db.commit()

# ============= Camera Streaming Endpoints =============

@app.get("/api/camera/frame")
def get_camera_frame():
    """Get current camera frame as base64 encoded JPEG"""
    frame_b64 = camera.get_frame_base64_string()
    if not frame_b64:
        raise HTTPException(status_code=503, detail="Camera not available")

    return {
        "frame": frame_b64,
        "timestamp": datetime.now().isoformat(),
        "format": "jpeg",
        "encoding": "base64"
    }

@app.get("/api/camera/stream")
def camera_stream():
    """Stream camera video feed as Motion JPEG"""
    def video_generator():
        while True:
            if camera.current_frame is None:
                continue

            _, buffer = cv2.imencode('.jpg', camera.current_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                   + frame_bytes + b'\r\n')

    return StreamingResponse(video_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/camera/snapshot")
def get_snapshot(db: Session = Depends(get_db)):
    """Capture and store a snapshot"""
    frame_b64 = camera.get_frame_base64_string()
    if not frame_b64:
        raise HTTPException(status_code=503, detail="Camera not available")

    # Store in database
    snapshot = CameraFrame(
        frame_data=frame_b64,
        position_x=robot_state["position"]["x"],
        position_y=robot_state["position"]["y"]
    )
    db.add(snapshot)
    db.commit()

    return {
        "id": snapshot.id,
        "timestamp": snapshot.timestamp.isoformat(),
        "position": {"x": snapshot.position_x, "y": snapshot.position_y}
    }

@app.get("/api/camera/snapshots")
def get_snapshots(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent snapshots"""
    snapshots = db.query(CameraFrame).order_by(CameraFrame.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": s.id,
            "frame": s.frame_data,
            "timestamp": s.timestamp.isoformat(),
            "position": {"x": s.position_x, "y": s.position_y}
        }
        for s in reversed(snapshots)
    ]

# ============= WebSocket Real-Time Streaming =============

@app.websocket("/ws/camera")
async def websocket_camera(websocket: WebSocket):
    """WebSocket endpoint for real-time camera streaming"""
    await websocket.accept()
    active_connections.append(websocket)

    def send_frame(frame):
        """Callback to send frame to WebSocket client"""
        _, buffer = cv2.imencode('.jpg', frame)
        frame_b64 = base64.b64encode(buffer).decode('utf-8')
        try:
            import asyncio
            asyncio.run(websocket.send_json({
                "type": "frame",
                "data": frame_b64,
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass

    camera.register_callback(send_frame)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry streaming"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            await websocket.send_json({
                "type": "telemetry",
                "data": robot_state,
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# ============= Database Query Endpoints =============

@app.get("/api/db/cleaned-cells")
def get_cleaned_cells(limit: int = 100, db: Session = Depends(get_db)):
    """Get cleaned cells from database"""
    cells = db.query(CleanedCell).order_by(CleanedCell.timestamp.desc()).limit(limit).all()
    return [
        {
            "grid_x": c.grid_x,
            "grid_y": c.grid_y,
            "timestamp": c.timestamp.isoformat()
        }
        for c in reversed(cells)
    ]

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_readings = db.query(RobotReading).count()
    total_cleaned_cells = db.query(CleanedCell).count()
    total_snapshots = db.query(CameraFrame).count()

    return {
        "total_telemetry_readings": total_readings,
        "total_cleaned_cells": total_cleaned_cells,
        "total_camera_snapshots": total_snapshots,
        "map_coverage_percent": (total_cleaned_cells / (GRID_SIZE * GRID_SIZE)) * 100
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
