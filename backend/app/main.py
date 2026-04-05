from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timezone, timedelta
import asyncio
from contextlib import asynccontextmanager

from app.database import engine, Base, get_db
from app.models import User, Ticket, Employee, TicketLog
from app.schemas import TicketCreate, TicketUpdateStatus, EmployeeCreate
from app.services.ai_service import analyze_ticket
from app.services.routing_service import suggest_best_employee

# Create DB tables
Base.metadata.create_all(bind=engine)

# WebSockets Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Background Escalation Task
async def escalation_check():
    while True:
        await asyncio.sleep(3600)  # Check every hour
        db = next(get_db())
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=2)
        
        # Find Critical/High tickets unassigned or stuck in "New" for > 2 hours
        stuck_tickets = db.query(Ticket).filter(
            Ticket.status == "New",
            Ticket.severity.in_(["Critical", "High"]),
            Ticket.created_at < time_threshold
        ).all()

        for ticket in stuck_tickets:
            # Re-route logic
            new_assignee = suggest_best_employee(db, ticket.department, ticket.original_text)
            if new_assignee:
                ticket.assigned_employee_id = new_assignee.id
                ticket.status = "Assigned"
                new_assignee.current_ticket_load += 1
                
                log = TicketLog(ticket_id=ticket.id, action="Auto-Escalation: Reassigned", notes="Ticket breached 2-hour SLA.")
                db.add(log)
        
        db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background escalation loop
    task = asyncio.create_task(escalation_check())
    yield
    task.cancel()

app = FastAPI(title="Advanced AI Ticketing System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WEBSOCKETS ---
@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Can handle incoming WS data if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# --- TICKETS (Module 1, 2, 3, 5) ---
@app.post("/tickets")
async def create_ticket(ticket_in: TicketCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Module 1: AI Analysis
    ai_result = analyze_ticket(ticket_in.text)
    
    db_ticket = Ticket(
        original_text=ticket_in.text,
        user_id=1, # Hardcoded for demo, normally from JWT auth
        category=ai_result.get("category"),
        summary=ai_result.get("summary"),
        severity=ai_result.get("severity"),
        resolution_type=ai_result.get("resolution_type"),
        sentiment=ai_result.get("sentiment"),
        department=ai_result.get("department"),
        confidence_score=ai_result.get("confidence_score"),
        estimated_resolution_time=ai_result.get("estimated_resolution_time")
    )
    
    # Module 2 & 3: Auto-resolve OR Assign
    if ai_result.get("resolution_type") == "Auto-resolve":
        db_ticket.status = "Resolved"
        db_ticket.auto_response = ai_result.get("auto_response")
    else:
        assignee = suggest_best_employee(db, db_ticket.department, ticket_in.text)
        if assignee:
            db_ticket.assigned_employee_id = assignee.id
            db_ticket.status = "Assigned"
            assignee.current_ticket_load += 1
        else:
            db_ticket.status = "New" # Needs manual assignment
            
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Module 5: Lifecycle Log
    log = TicketLog(ticket_id=db_ticket.id, action="Ticket Created & Analyzed by AI")
    db.add(log)
    db.commit()
    
    # Real-time Broadcast
    background_tasks.add_task(manager.broadcast, f"New Ticket #{db_ticket.id} created: {db_ticket.summary}")
    
    return db_ticket

@app.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: int, update_data: TicketUpdateStatus, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    ticket.status = update_data.status
    
    # Decrease load if resolved/closed
    if update_data.status in ["Resolved", "Closed"] and ticket.assigned_employee_id:
        emp = db.query(Employee).filter(Employee.id == ticket.assigned_employee_id).first()
        if emp and emp.current_ticket_load > 0:
            emp.current_ticket_load -= 1

    log = TicketLog(ticket_id=ticket.id, action=f"Status updated to {update_data.status}", notes=update_data.notes)
    db.add(log)
    db.commit()
    
    background_tasks.add_task(manager.broadcast, f"Ticket #{ticket.id} updated to {update_data.status}")
    return {"message": "Ticket updated"}


# --- EMPLOYEE DIRECTORY (Module 4) ---
@app.post("/employees")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = Employee(**employee.model_dump())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.is_active == True).all()


# --- ANALYTICS DASHBOARD (Module 6) ---
@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total_open = db.query(Ticket).filter(Ticket.status.in_(["New", "Assigned", "In Progress", "Pending Info"])).count()
    total_resolved = db.query(Ticket).filter(Ticket.status == "Resolved").count()
    total_autoresolved = db.query(Ticket).filter(Ticket.resolution_type == "Auto-resolve").count()
    
    dept_load = db.query(Ticket.department, func.count(Ticket.id)).filter(
        Ticket.status.in_(["New", "Assigned", "In Progress"])
    ).group_by(Ticket.department).all()

    top_categories = db.query(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category).order_by(func.count(Ticket.id).desc()).limit(5).all()
    
    return {
        "metrics": {
            "total_open": total_open,
            "total_resolved": total_resolved,
            "total_autoresolved": total_autoresolved,
        },
        "department_load": dict(dept_load),
        "top_categories": dict(top_categories)
    }