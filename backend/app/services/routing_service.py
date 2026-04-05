from sqlalchemy.orm import Session
from app.models import Employee

def suggest_best_employee(db: Session, department: str, ticket_text: str):
    # 1. Filter by Department and Availability
    available_employees = db.query(Employee).filter(
        Employee.department == department,
        Employee.availability == "Available",
        Employee.is_active == True
    ).all()
    
    if not available_employees:
        return None
        
    # 2. Simple Skill Match (Check if ticket text contains employee skills)
    best_match = None
    highest_score = -1
    
    for emp in available_employees:
        score = 0
        emp_skills = [s.strip().lower() for s in emp.skills.split(",")]
        
        for skill in emp_skills:
            if skill in ticket_text.lower():
                score += 1
                
        # 3. Incorporate Load balancing (Penalty for high current load)
        final_score = score - (emp.current_ticket_load * 0.5)
        
        if final_score > highest_score:
            highest_score = final_score
            best_match = emp
            
    # Fallback to least loaded employee in department if no skills match
    if not best_match and available_employees:
        best_match = min(available_employees, key=lambda x: x.current_ticket_load)
        
    return best_match