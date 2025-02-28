from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, BigInteger, ForeignKey
from datetime import datetime
from .database import Base

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(Text)
    channel = Column(Text)
    upload_date = Column(Date)
    duration = Column(Integer)
    view_count = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

class Subtitle(Base):
    __tablename__ = "subtitles"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, ForeignKey("videos.video_id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    subtitle_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)