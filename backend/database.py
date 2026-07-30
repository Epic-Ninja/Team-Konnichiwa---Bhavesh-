import sqlite3
import json
import os
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "studypilot.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        university TEXT,
        branch TEXT,
        semester TEXT,
        target_gpa TEXT,
        focus_window TEXT,
        streak INTEGER DEFAULT 21,
        xp INTEGER DEFAULT 1420,
        level INTEGER DEFAULT 4,
        onboarded INTEGER DEFAULT 1
    );
    """)

    # Subjects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        module TEXT,
        progress INTEGER DEFAULT 0,
        attendance INTEGER DEFAULT 92,
        credits REAL DEFAULT 4.0,
        next_lesson TEXT,
        image_url TEXT
    );
    """)

    # Tasks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        tag TEXT,
        priority TEXT DEFAULT 'High',
        due_date TEXT,
        completed INTEGER DEFAULT 0,
        estimate TEXT DEFAULT '2h',
        bg_color TEXT DEFAULT 'bg-[#e5e2e1]'
    );
    """)

    # AI Memory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_type TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Agent Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT,
        action TEXT,
        rationale TEXT,
        confidence_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed Default User if empty
    cursor.execute("SELECT COUNT(*) as count FROM users;")
    if cursor.fetchone()['count'] == 0:
        cursor.execute("""
        INSERT INTO users (id, name, email, university, branch, semester, target_gpa, focus_window, streak, xp, level, onboarded)
        VALUES ('u1', 'Bhavesh Dhidaria', 'bhavesh@university.edu', 'School of Architecture & Planning', 'B.Arch', '6th Semester', '3.92 GPA', '09:00 AM - 11:30 AM', 21, 1420, 4, 1);
        """)

        cursor.execute("""
        INSERT INTO subjects (id, title, module, progress, attendance, credits, next_lesson, image_url)
        VALUES 
        ('s1', 'Architecture 101', 'MODULE 04', 68, 92, 4.0, 'The Ethics of Concrete', 'https://lh3.googleusercontent.com/aida-public/AB6AXuC1TYbAa3h5JEdyF9MZt7HQ-ebpCyBCWImT_FEjfDX3iGeNza0CNJRda5UQ0DP315ExdEzYIV2NZNYbrjMOKWLbqwO_I22qgrqyeUWhQZqoKG4Lgobc3D7AGmwOF7YUHZVXb8LXRkDiohW_9HmKufA7i1q-hqwwob_ahUoNdnlkuqHuFeMhVmxpd4uMUQkxOoSVfnErUBl0Ydv-T_kwa3-I2wxckF_Ccjyqc_xUiDKXsGXJJbulZepAWw'),
        ('s2', 'History of Urban Planning', 'SEMINAR PHASE', 45, 74, 3.0, '19th Century Garden Cities', 'https://lh3.googleusercontent.com/aida-public/AB6AXuDxnBY0CPOtrtDjoNB4G6Ke7oADINc5ciiTjfJ7rANb2vjhDrvwHbharRrsi0XWA2fvyuqny_mE2c8ix5X7_jicdXuL3DycZY6GY20a9wMygQmmI2FR865Md0Y3llYVAqF1oQOwqK_v-tWZZhu1wdoxAaoAWoswTzXaAfJNLQzUaVhc95pziOQtB9AeTe6ZIQfw-hVH04ryJ_GXz3wLMAa1wwnrcMu-SmMEECgDexZj9F8UMT0A3jcsHA');
        """)

        cursor.execute("""
        INSERT INTO tasks (title, tag, priority, due_date, completed, estimate, bg_color)
        VALUES 
        ('Audit the ''Ma'' (Negative Space) in UI flow.', '#RESEARCH', 'High', 'TODAY', 1, '3h', 'bg-[#e5e2e1]'),
        ('Finalize clay-tone palette for navigation states.', '#ASSET', 'Med', 'OCT 25', 0, '1.5h', 'bg-accent-olive/15'),
        ('Draft spatial theory research module outline.', '#OUTLINE', 'High', 'OCT 26', 0, '2h', 'bg-accent-clay/15');
        """)

        cursor.execute("""
        INSERT INTO ai_memories (memory_type, content)
        VALUES 
        ('PREFERENCE', 'User prefers morning focus windows between 9:00 AM and 11:30 AM.'),
        ('HABIT', 'User completes 85% of tasks scheduled before noon.');
        """)

    conn.commit()
    conn.close()

import time
def add_subject(title: str, module: str = "CORE MODULE", progress: int = 50, attendance: int = 90, credits: float = 4.0):
    conn = get_db()
    cursor = conn.cursor()
    subject_id = f"s_{int(time.time())}"
    cursor.execute("""
        INSERT INTO subjects (id, title, module, progress, attendance, credits, next_lesson, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (subject_id, title, module, progress, attendance, credits, "Unit Overview & Revision", ""))
    conn.commit()
    conn.close()
    return {"id": subject_id, "title": title, "module": module, "progress": progress, "attendance": attendance}
