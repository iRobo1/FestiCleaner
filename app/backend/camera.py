import cv2
import base64
import threading
from typing import Optional, Callable
from datetime import datetime

class CameraStream:
    """Real-time camera streaming from robot"""

    def __init__(self, camera_id: int = 0, width: int = 1280, height: int = 720, jpeg_quality: int = 70):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.jpeg_quality = jpeg_quality
        self.cap = None
		
        self.is_streaming = False
        self.current_frame = None
        self.stream_thread = None
        self.callbacks = []

    def connect(self) -> bool:
        """Initialize camera connection"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.is_streaming = True
            return True
        except Exception as e:
            print(f"Failed to connect to camera: {e}")
            self.is_streaming = False
            return False

    def disconnect(self):
        """Close camera connection"""
        self.is_streaming = False
        if self.cap:
            self.cap.release()

    def get_frame_base64(self) -> Optional[str]:
        """Get current frame as base64 encoded JPEG"""
        if not self.cap or not self.current_frame is not None:
            return None

        _, buffer = cv2.imencode('.jpg', self.current_frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        return base64.b64encode(buffer).decode('utf-8')

    def start_streaming(self):
        """Start background thread for continuous frame capture"""
        def capture():
            while self.is_streaming:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                    # Notify all callbacks
                    for callback in self.callbacks:
                        callback(frame)

        self.stream_thread = threading.Thread(target=capture, daemon=True)
        self.stream_thread.start()

    def register_callback(self, callback: Callable):
        """Register callback function when new frame arrives"""
        self.callbacks.append(callback)

    def capture_snapshot(self) -> Optional[bytes]:
        """Capture a single frame as JPEG bytes"""
        if self.current_frame is None:
            return None
        _, buffer = cv2.imencode('.jpg', self.current_frame)
        return buffer.tobytes()

    def get_frame_base64_string(self) -> Optional[str]:
        """Get current frame as base64 string for API responses"""
        data = self.capture_snapshot()
        if data:
            return base64.b64encode(data).decode('utf-8')
        return None

# Global camera instance (initialized with config values in main.py)
camera: Optional[CameraStream] = None
