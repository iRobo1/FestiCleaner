# Festival Robot Backend - Integrated

FastAPI backend for Arduino Uno 8 outdoor cleaning robot with **real-time camera streaming**, **SQL database**, and **WebSocket support**.

## Features

✅ **Robot Telemetry** - Battery, temperature, position tracking  
✅ **Real-Time Camera Streaming** - Motion JPEG and WebSocket feeds  
✅ **SQL Database** - SQLite with SQLAlchemy ORM  
✅ **Map Building** - Grid-based cleaned area tracking  
✅ **Historical Data** - Persistent telemetry and snapshots  
✅ **WebSocket API** - Live telemetry and camera updates  

## Setup

### Install Dependencies
```bash
cd app/backend
pip install -r requirements.txt
```

### Run Backend
```bash
python main.py
```

Server runs on `http://localhost:8000`

## API Endpoints

### Robot Status
- `GET /api/robot/status` - Current battery, temp, position
- `POST /api/robot/telemetry` - Send sensor data
- `GET /api/history/telemetry` - Historical readings

### Map
- `GET /api/map` - Current map state and coverage
- `POST /api/map/update` - Update map with position
- `GET /api/db/cleaned-cells` - Cleaned cells from DB

### Camera (Real-Time)
- `GET /api/camera/frame` - Latest frame (base64 JPEG)
- `GET /api/camera/stream` - Motion JPEG stream (HTTP)
- `GET /api/camera/snapshot` - Capture & store snapshot
- `GET /api/camera/snapshots` - Recent snapshots from DB
- `WebSocket /ws/camera` - Real-time frame stream

### Telemetry (Real-Time)
- `WebSocket /ws/telemetry` - Real-time robot data

### Stats
- `GET /api/stats` - Overall statistics
- `GET /health` - Health check

## Database

SQLite database stores:
- **robot_readings** - Telemetry history
- **cleaned_cells** - Cleaned grid cells with timestamps
- **camera_frames** - Camera snapshots (base64)
- **map_snapshots** - Map state over time

Database created automatically on startup: `robot_data.db`

## Real-Time Streaming

### Camera Stream (HTTP)
```bash
# Motion JPEG stream - works in HTML <img src="/api/camera/stream" />
# or video players that support mjpeg
```

### WebSocket - Camera Feed
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/camera");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type === "frame"
  // data.data = base64 encoded JPEG
  // data.timestamp = ISO timestamp
};
```

### WebSocket - Telemetry
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.data.battery
  // data.data.temperature
  // data.data.position
  // data.data.is_active
};
```

## Testing

### Get Status
```bash
curl http://localhost:8000/api/robot/status
```

### Send Telemetry
```bash
curl -X POST http://localhost:8000/api/robot/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "battery": 85,
    "temperature": 22.5,
    "position": {"x": 1.5, "y": 2.0}
  }'
```

### Get Camera Frame
```bash
curl http://localhost:8000/api/camera/frame
```

### Stream Camera (Terminal)
```bash
ffplay http://localhost:8000/api/camera/stream
```

### Interactive API Docs
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration

Set via environment variables (see `config.py`):
```bash
export DATABASE_URL="sqlite:///./robot_data.db"
export CAMERA_ID=0
export CAMERA_WIDTH=640
export CAMERA_HEIGHT=480
export GRID_SIZE=20
export CELL_SIZE=0.5
export ARDUINO_PORT="/dev/ttyUSB0"
export ARDUINO_BAUDRATE=9600
```

## Hardware Integration

### Arduino Uno 8
1. Upload `arduino_sketch.ino` (in HACKUPF folder)
2. Connect sensors:
   - DHT22 temperature on pin 2
   - Battery voltage divider on A0
   - GPS/position data on pins 3-4
3. Device sends JSON via serial: `{"battery": XX, "temperature": XX, "x": XX, "y": XX}`

### Camera
- Webcam on `/dev/video0` (or set `CAMERA_ID`)
- USB camera recommended

## Project Structure
```
app/backend/
├── main.py           # FastAPI application
├── models.py         # SQLAlchemy models
├── database.py       # Database setup
├── camera.py         # Camera streaming
├── config.py         # Configuration
├── utils.py          # Utilities
├── requirements.txt  # Python dependencies
└── robot_data.db     # SQLite database (generated)
```

## Performance Notes

- Camera frames: ~10-15 FPS typical
- WebSocket updates: 1-second intervals
- Grid resolution: 0.5m per cell (10m × 10m total area)
- Motion JPEG compression: Quality 80/100

## Next Steps

- [ ] Add frontend dashboard
- [ ] Implement path optimization
- [ ] Add obstacle detection
- [ ] Mobile app
- [ ] Cloud sync
