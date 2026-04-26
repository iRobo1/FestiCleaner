from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RobotReading(Base):
    __tablename__ = "robot_readings"

    id = Column(Integer, primary_key=True, index=True)
    battery = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=True)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class CleanedCell(Base):
    __tablename__ = "cleaned_cells"

    id = Column(Integer, primary_key=True, index=True)
    grid_x = Column(Integer, nullable=False)
    grid_y = Column(Integer, nullable=False)
    cell_size = Column(Float, default=0.5)
    timestamp = Column(DateTime, default=datetime.utcnow)

class CameraFrame(Base):
    __tablename__ = "camera_frames"

    id = Column(Integer, primary_key=True, index=True)
    frame_data = Column(String, nullable=False)  # Base64 encoded image
    timestamp = Column(DateTime, default=datetime.utcnow)
    position_x = Column(Float)
    position_y = Column(Float)

class MapSnapshot(Base):
    __tablename__ = "map_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    grid_state = Column(String, nullable=False)  # JSON of grid
    coverage_percent = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
