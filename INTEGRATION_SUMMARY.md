# Integration Summary - Festival Robot Backend

## ✅ Completed Integration

Your FastAPI backend has been fully integrated into the HackUPC-2026 project with advanced features:

### 📊 What Was Added

#### 1. **Real-Time Camera Streaming**
- HTTP Motion JPEG stream endpoint (`/api/camera/stream`)
- WebSocket real-time feed (`/ws/camera`)
- Frame capture & storage in database
- Base64 encoded frames for API responses
- Configurable resolution (640x480 default)

#### 2. **SQL Database (SQLite)**
- **RobotReading** - Telemetry history (battery, temp, position)
- **CleanedCell** - Grid cells marked as cleaned with timestamps
- **CameraFrame** - Camera snapshots stored as base64
- **MapSnapshot** - Map state snapshots over time
- Automatic table creation on startup
- Persistent data across restarts

#### 3. **Real-Time WebSocket APIs**
- `/ws/camera` - Continuous frame stream with timestamps
- `/ws/telemetry` - Live robot status (battery, temp, position)
- JSON message format for easy client integration

#### 4. **Enhanced REST Endpoints**
All telemetry endpoints now backed by SQL database:
- `GET /api/history/telemetry` - Query historical readings
- `GET /api/db/cleaned-cells` - Query cleaned grid cells
- `GET /api/camera/snapshots` - Get historical snapshots
- `GET /api/stats` - Overall statistics

### 📁 Project Structure

```
HackUPC-2026/
├── app/
│   ├── backend/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── database.py          # Database initialization
│   │   ├── camera.py            # Camera streaming module
│   │   ├── config.py            # Configuration
│   │   ├── utils.py             # Utility functions
│   │   ├── requirements.txt     # Dependencies
│   │   ├── .env.example         # Environment template
│   │   └── robot_data.db        # SQLite (auto-generated)
│   └── frontend/
│       └── index.html           # Dashboard with WebSocket client
├── BACKEND_README.md            # Detailed backend documentation
├── INTEGRATION_SUMMARY.md       # This file
└── README.md                    # Original project README
```

### 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   cd app/backend
   pip install -r requirements.txt
   ```

2. **Run the backend:**
   ```bash
   python main.py
   ```

3. **Open the dashboard:**
   - Open `http://localhost:8000` for API root
   - Open `app/frontend/index.html` in a browser for real-time dashboard
   - Swagger docs: `http://localhost:8000/docs`

### 🎥 Camera Features

- **Motion JPEG Stream** - Works with HTML5 `<img>` or video players
- **WebSocket Stream** - Low-latency continuous updates
- **Snapshot Capture** - Store frames with location metadata
- **Base64 Encoding** - Easy integration with APIs/web clients

### 💾 Database Features

- **Automatic Creation** - Tables created on first run
- **Persistent Storage** - Data survives restarts
- **Historical Queries** - Filter by limit, duration, timestamp
- **Spatial Data** - Position tracked with each reading/snapshot
- **No External DB** - SQLite embedded, no setup required

### 🔌 API Examples

**Get Real-Time Camera:**
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/camera");
ws.onmessage = (e) => {
  const { data, timestamp } = JSON.parse(e.data);
  img.src = "data:image/jpeg;base64," + data;
};
```

**Get Real-Time Telemetry:**
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
ws.onmessage = (e) => {
  const { data } = JSON.parse(e.data);
  console.log(data.battery, data.temperature);
};
```

**Stream Camera (HTTP):**
```html
<img src="http://localhost:8000/api/camera/stream" />
```

### ⚙️ Configuration

Edit `config.py` or set environment variables:
- `CAMERA_ID` - Webcam device ID (default: 0)
- `GRID_SIZE` - Map grid dimensions (default: 20x20)
- `CELL_SIZE` - Cell size in meters (default: 0.5m)
- `ARDUINO_PORT` - Serial port for Arduino (default: /dev/ttyUSB0)
- `DATABASE_URL` - SQLite database location

### 📊 Dashboard Features

Interactive web dashboard (`app/frontend/index.html`) includes:
- ✅ Real-time robot status (battery, temp, position)
- ✅ Live camera feed (WebSocket)
- ✅ Grid-based map visualization
- ✅ Coverage statistics
- ✅ Snapshot capture button
- ✅ Session timer
- ✅ Dark mode interface

### 🔧 Tech Stack

- **FastAPI** - Modern async Python framework
- **SQLAlchemy** - ORM for database operations
- **OpenCV** - Camera capture and processing
- **Pydantic** - Data validation
- **WebSocket** - Real-time bidirectional communication
- **SQLite** - Embedded database

### 📝 Next Steps

1. Upload Arduino sketch to your Uno 8
2. Connect camera and sensors
3. Test endpoints with `curl` or Postman
4. Use the dashboard to monitor live data
5. Integrate with your cleaning robot firmware

### 🐛 Troubleshooting

- **Camera not found:** Check `CAMERA_ID` in config or use `ls /dev/video*`
- **Arduino not responding:** Verify port with `ls /dev/ttyUSB*`
- **WebSocket connection refused:** Ensure backend is running on port 8000
- **Database locked:** Delete `robot_data.db` to reset (data will be lost)

### 📖 Documentation

- `BACKEND_README.md` - Complete API reference and setup guide
- `app/backend/main.py` - Inline code documentation
- Interactive API docs at `http://localhost:8000/docs`

---

**Status:** ✅ Integration Complete  
**Database:** ✅ SQLite with 4 tables  
**Camera Streaming:** ✅ HTTP + WebSocket  
**Real-Time APIs:** ✅ WebSocket telemetry  
**Frontend Dashboard:** ✅ Included  
**Hardware Ready:** ✅ Arduino sketch in HACKUPF folder
