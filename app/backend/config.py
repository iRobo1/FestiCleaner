import os
from typing import Optional

class Settings:
    """Application configuration"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./robot_data.db")

    # Camera (optimized for hackathon demo - Full HD)
    CAMERA_ID: int = int(os.getenv("CAMERA_ID", "0"))
    CAMERA_WIDTH: int = int(os.getenv("CAMERA_WIDTH", "1920"))
    CAMERA_HEIGHT: int = int(os.getenv("CAMERA_HEIGHT", "1080"))
    CAMERA_JPEG_QUALITY: int = int(os.getenv("CAMERA_JPEG_QUALITY", "85"))

    # Robot
    GRID_SIZE: int = int(os.getenv("GRID_SIZE", "20"))
    CELL_SIZE: float = float(os.getenv("CELL_SIZE", "0.5"))

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Arduino
    ARDUINO_PORT: str = os.getenv("ARDUINO_PORT", "/dev/ttyUSB0")
    ARDUINO_BAUDRATE: int = int(os.getenv("ARDUINO_BAUDRATE", "9600"))

settings = Settings()
