import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

def analyze_ticket(ticket_text: str) -> dict:
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an advanced internal AI ticketing system. 
    Analyze this ticket: "{ticket_text}"
    
    Return ONLY a JSON object matching this schema exactly.
    {{
        "category": "Billing | Bug | Access | HR | Server | DB | Feature | Other",
        "summary": "2-3 sentence summary",
        "severity": "Critical | High | Medium | Low",
        "resolution_type": "Auto-resolve | Assign",
        "sentiment": "Frustrated | Neutral | Polite",
        "department": "Engineering | HR | Finance | IT | Marketing | Legal | Product",
        "confidence_score": 95.5,
        "estimated_resolution_time": "2 hours",
        "auto_response": "Professional response if auto-resolving, else null"
    }}

    Decision Rules:
    1. If the issue is a simple FAQ (password reset, policy info, leave application), set resolution_type to "Auto-resolve" and write a helpful auto_response.
    2. If it requires a human (bug, server down, complex billing), set resolution_type to "Assign" and auto_response to null.
    """
    
    try:
        # 🚀 THE FIX: Force the model to output strict JSON natively
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "category": "Other", 
            "summary": "AI processing failed. Manual review required.", 
            "severity": "Medium",
            "resolution_type": "Assign", 
            "sentiment": "Neutral", 
            "department": "IT",
            "confidence_score": 0.0, 
            "estimated_resolution_time": "24 hours", 
            "auto_response": None
        }