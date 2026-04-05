from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="employee") # admin or employee

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String, index=True)
    role = Column(String)
    skills = Column(String) # Comma-separated
    availability = Column(String, default="Available") # Available, Busy, On Leave
    current_ticket_load = Column(Integer, default=0)
    average_resolution_time = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    original_text = Column(Text)
    
    # AI Output
    category = Column(String)
    summary = Column(String)
    severity = Column(String)
    resolution_type = Column(String)
    sentiment = Column(String)
    department = Column(String)
    confidence_score = Column(Float)
    estimated_resolution_time = Column(String)
    
    # Lifecycle
    status = Column(String, default="New") # New, Assigned, In Progress, Pending Info, Resolved, Closed
    assigned_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    auto_response = Column(Text, nullable=True)
    is_helpful = Column(Boolean, nullable=True) # User feedback for auto-resolve
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    logs = relationship("TicketLog", back_populates="ticket")

class TicketLog(Base):
    __tablename__ = "ticket_logs"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    action = Column(String)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = relationship("Ticket", back_populates="logs")