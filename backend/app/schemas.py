from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AIAnalysisResult(BaseModel):
    category: str
    summary: str
    severity: str
    resolution_type: str
    sentiment: str
    department: str
    confidence_score: float
    estimated_resolution_time: str
    auto_response: Optional[str] = None

class TicketCreate(BaseModel):
    text: str

class TicketUpdateStatus(BaseModel):
    status: str
    notes: Optional[str] = None

class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str
    role: str
    skills: str
    availability: str = "Available"