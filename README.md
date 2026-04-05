# 🚀 Advanced AI Ticketing System

An intelligent, full-stack internal ticketing platform that leverages Google's Gemini AI to read, analyze, auto-resolve, and intelligently route incoming support tickets. 

**Live Frontend (Netlify):** [https://ticketing-ai.netlify.app/](https://ticketing-ai.netlify.app/)
**Live Backend API (Render):** [https://ticket-tracking-arth-nxt-ai-app-backend.onrender.com](https://ticket-tracking-arth-nxt-ai-app-backend.onrender.com)
**📺 Demo Video:** [Watch on Loom](https://www.loom.com/share/f66729a0354a4608beb504d9bc5751c7)

---

## ✨ Core Features

* **🧠 AI Ticket Intake (Module 1):** Every ticket is analyzed by Gemini 1.5 Flash to determine category, severity, sentiment, and resolution path.
* **🤖 Auto-Resolution Engine (Module 2):** Simple FAQs and policy questions are automatically resolved with a helpful, AI-generated response.
* **🧭 Intelligent Routing (Module 3):** Complex issues are assigned to specific departments based on AI analysis.
* **👨‍💼 Smart Employee Directory (Module 4):** Suggests the best human assignee based on skill matching, current ticket load, and availability.
* **🔄 Ticket Lifecycle & Escalation (Module 5):** Tracks ticket status from 'New' to 'Closed'. Includes an automated background task that escalates High/Critical tickets if left unassigned for 2 hours.
* **📊 Analytics Dashboard (Module 6):** Real-time metrics on department loads, top categories, and auto-resolution success rates.
* **⚡ Real-Time Notifications:** Uses WebSockets to instantly push updates to the frontend without a page refresh.

---

## 🛠️ Tech Stack

**Frontend:**
* React.js (Vite)
* Tailwind CSS

**Backend:**
* Python 3.12
* FastAPI
* SQLite (Local) / PostgreSQL (Production)
* SQLAlchemy (ORM)
* Pydantic (Data Validation)

**AI Integration:**
* Google Generative AI SDK (`gemini-1.5-flash`)

---

## 💻 Local Setup Instructions

### Prerequisites
* Python 3.12+
* A valid Google Gemini API Key

### 1. Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root of the `backend` folder and add your Gemini key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
5. Start the server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   *The API will be available at `http://127.0.0.1:8000`*

### 2. Frontend Setup
1. Open a **new** terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The app will be available at `http://localhost:5173`*

---

## 🚧 Known Limitations & Future Improvements
* **Ephemeral Database on Free Tier:** Currently, the live deployment uses an SQLite database. Because free-tier hosting (like Render) uses ephemeral file systems, database records (tickets, employees) reset upon server spin-down. *Fix: Migrate to a managed PostgreSQL database.*
* **Authentication:** Currently, user IDs are hardcoded for demonstration purposes. *Fix: Implement the full JWT-based login flow outlined in the architecture.*
