"""
ELARA — Database Models
SQLAlchemy ORM models for all ELARA data.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Astronaut(Base):
    __tablename__ = "astronauts"

    id                  = Column(Integer, primary_key=True, index=True)
    astronaut_id        = Column(String, unique=True, index=True)
    name                = Column(String)
    voice_pitch_base    = Column(Float)
    sleep_base          = Column(Float)
    latency_base        = Column(Float)
    resilience_factor   = Column(Float)
    tqs_vulnerability   = Column(Float)
    created_at          = Column(DateTime, default=datetime.utcnow)


class DailyAssessment(Base):
    __tablename__ = "daily_assessments"

    id                          = Column(Integer, primary_key=True, index=True)
    astronaut_id                = Column(String, index=True)
    mission_day                 = Column(Integer)
    mission_phase               = Column(String)
    health_index                = Column(Float)
    health_status               = Column(String)
    cognitive_load_score        = Column(Float)
    cognitive_readiness_score   = Column(Float)
    risk_level                  = Column(String)
    tqs_probability             = Column(Float)
    voice_stress_score          = Column(Float)
    sleep_disruption_score      = Column(Float)
    cognitive_latency_score     = Column(Float)
    linguistic_drift_score      = Column(Float)
    alerts                      = Column(Text)   # JSON string
    explanations                = Column(Text)   # JSON string
    created_at                  = Column(DateTime, default=datetime.utcnow)


class InterventionLog(Base):
    __tablename__ = "intervention_logs"

    id                  = Column(Integer, primary_key=True, index=True)
    astronaut_id        = Column(String, index=True)
    mission_day         = Column(Integer)
    condition           = Column(String)
    intervention_id     = Column(String)
    intervention_title  = Column(String)
    intervention_type   = Column(String)
    effectiveness       = Column(String, default="PENDING")
    created_at          = Column(DateTime, default=datetime.utcnow)


class MissionSession(Base):
    __tablename__ = "mission_sessions"

    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(String, unique=True, index=True)
    current_day     = Column(Integer, default=1)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)