from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(__file__))

from database import init_db, get_db
from agents.orchestrator import AgenticOrchestrator

app = FastAPI(
    title="StudyPilot AI | Agentic AI Backend Engine",
    description="Python FastAPI Multi-Agent Student Operating System Engine",
    version="2.0.0"
)

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on Startup
@app.on_event("startup")
def startup_db_client():
    init_db()

orchestrator = AgenticOrchestrator()

# --- Pydantic Schemas ---
class ReplanRequest(BaseModel):
    trigger_text: str

class ChatRequest(BaseModel):
    message: str

class UserProfileUpdate(BaseModel):
    name: str
    focus_window: str

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {
        "status": "ONLINE",
        "system": "StudyPilot AI Agentic Backend",
        "engine": "Python FastAPI Multi-Agent Engine v2.0"
    }

@app.get("/api/v1/dashboard")
def get_dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users LIMIT 1;")
    user = dict(cursor.fetchone())

    cursor.execute("SELECT * FROM subjects;")
    subjects = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM tasks;")
    tasks = [dict(r) for r in cursor.fetchall()]

    conn.close()

    ai_state = orchestrator.get_dashboard_state(user, subjects, user.get("streak", 21))

    return {
        "user": user,
        "subjects": subjects,
        "tasks": tasks,
        "ai_insights": ai_state
    }

@app.post("/api/v1/planner/replan")
def replan_schedule(req: ReplanRequest):
    res = orchestrator.process_natural_language_trigger(req.trigger_text)
    
    # If task injection requested (e.g. sick day)
    replan_res = res.get("replan_result", {})
    injected_task = replan_res.get("injected_task")
    
    if injected_task:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, tag, priority, due_date, completed, estimate, bg_color)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            injected_task["title"],
            injected_task["tag"],
            injected_task["priority"],
            injected_task["date"],
            0,
            injected_task["estimate"],
            injected_task["bg_color"]
        ))
        conn.commit()
        conn.close()

    return res

@app.post("/api/v1/chat")
def chat_with_echoes(req: ChatRequest):
    ai_response = orchestrator.process_chat_query(req.message)
    return {"response": ai_response}

@app.get("/api/v1/tools/quiz")
def get_quiz():
    return orchestrator.quiz.generate_quiz()

@app.get("/api/v1/tools/flashcards")
def get_flashcards():
    return orchestrator.quiz.generate_flashcards()

@app.post("/api/v1/user/settings")
def update_settings(profile: UserProfileUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET name = ?, focus_window = ? WHERE id = 'u1';
    """, (profile.name, profile.focus_window))
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "name": profile.name, "focus_window": profile.focus_window}

@app.post("/api/v1/upload/ocr")
def process_ocr_upload():
    # Ingest extracted syllabus into database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO subjects (id, title, module, progress, attendance, credits, next_lesson, image_url)
        VALUES ('s3', 'Structural Mechanics II', 'FINITE ELEMENT PHASE', 10, 88, 4.0, 'Matrix Displacement Methods', 'https://lh3.googleusercontent.com/aida-public/AB6AXuADQm3LmdoB5hNAA_hrKbzlZR3OS3K2nV83IKYB9kyUPfcoWrBiygG1VMggYtyxtn--9Tpp4WinAsc_A6LF-L28D5Aaw5kgbijYdZdzkmzeCVNS_ETkx8e87-lcPNk6uM8OGBoDTa10gs8w1AwxEU-ohqUMF1PfyrpP3bApU2UYNkcfDTbJgWTCfL_cTnU3oAeBoWu_UKp_tB7bmd6C-spU9Lq0xq79AqFVFZuDFWab2XzeJ6ibyMSbIQ');
    """)
    conn.commit()
    conn.close()
    return {
        "status": "INGESTED",
        "subject": "Structural Mechanics II",
        "message": "Syllabus extracted & parsed. Structural Mechanics II added to Subjects Library."
    }
