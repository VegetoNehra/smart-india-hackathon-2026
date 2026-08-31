from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Region(Base):
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    level = Column(String)  # E.g., 'State', 'District', 'Block'
    parent_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    # Self-referential relationship for hierarchy (State -> District -> Block)
    parent = relationship("Region", remote_side=[id], back_populates="children")
    children = relationship("Region", back_populates="parent", cascade="all, delete-orphan")
    
    forecasts = relationship("Forecast", back_populates="region", cascade="all, delete-orphan")
    advisories = relationship("Advisory", back_populates="region", cascade="all, delete-orphan")

class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    date = Column(DateTime, default=datetime.utcnow)
    
    onset_prob = Column(Float)
    break_spell_risk = Column(Float)
    heavy_rain_prob = Column(Float)
    confidence = Column(Float)
    
    region = relationship("Region", back_populates="forecasts")

class Advisory(Base):
    __tablename__ = "advisories"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    crop = Column(String)
    advisory_type = Column(String)  # E.g., 'SOWING', 'IRRIGATION'
    title = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    region = relationship("Region", back_populates="advisories")
