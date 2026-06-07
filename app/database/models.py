import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Call(Base):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vapi_call_id = Column(String(64), unique=True, nullable=False, index=True)
    caller_number = Column(String(20), nullable=True)
    called_number = Column(String(20), nullable=True)
    status = Column(String(20), default="in_progress")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    recording_url = Column(Text, nullable=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vapi_call_id = Column(String(64), nullable=False, index=True)
    caller_number = Column(String(20), nullable=True)
    caller_name = Column(String(100), nullable=True)
    message_content = Column(Text, nullable=False)
    is_urgent = Column(Boolean, default=False)
    callback_time = Column(String(100), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vapi_call_id = Column(String(64), nullable=False, index=True)
    caller_number = Column(String(20), nullable=True)
    caller_name = Column(String(100), nullable=True)
    appointment_time = Column(DateTime, nullable=True)
    purpose = Column(Text, nullable=True)
    status = Column(String(20), default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)