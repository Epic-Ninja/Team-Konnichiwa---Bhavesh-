from typing import Dict, Any, List
import os
import re
import json
import sqlite3
from .gemini_service import GeminiAPIService

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "studypilot.db")

class QuizFlashcardAgent:
    def __init__(self, name: str = "QuizFlashcardAgent"):
        self.name = name
        self.gemini = GeminiAPIService()
        self.uploaded_decks: Dict[str, Dict[str, Any]] = {}

    def generate_quiz(self, subject: str = "Architecture 101") -> Dict[str, Any]:
        if subject in self.uploaded_decks and "quiz" in self.uploaded_decks[subject]:
            return {
                "agent": self.name,
                "subject": subject,
                "api_used": "Dynamic PDF Ingestion Engine",
                "questions": self.uploaded_decks[subject]["quiz"]
            }

        subject_quizzes = {
            "Architecture 101": [
                {
                    "id": 1,
                    "question": "Which socio-political movement heavily influenced British Brutalist architecture post-WWII?",
                    "options": [
                        "A) Post-War Welfare State Housing & Material Transparency",
                        "B) Victorian Industrial Revivalism",
                        "C) High-Tech Structural Expressionism"
                    ],
                    "correct_index": 0,
                    "explanation": "Brutalism in post-war Britain was deeply connected to social democracy and the welfare state, prioritizing honest materials like unadorned concrete."
                },
                {
                    "id": 2,
                    "question": "What is the primary aesthetic characteristic of 'Béton Brut'?",
                    "options": [
                        "A) Highly polished marble facade",
                        "B) Raw concrete with visible wood-grain formwork impressions",
                        "C) Reflective glass curtain wall"
                    ],
                    "correct_index": 1,
                    "explanation": "Béton brut leaves shuttering marks and wood grain exposed on the concrete surface."
                }
            ],
            "History of Urban Planning": [
                {
                    "id": 1,
                    "question": "Who pioneered the 19th Century 'Garden Cities' urban planning concept?",
                    "options": [
                        "A) Ebenezer Howard",
                        "B) Le Corbusier",
                        "C) Jane Jacobs"
                    ],
                    "correct_index": 0,
                    "explanation": "Ebenezer Howard published 'Garden Cities of To-morrow' in 1898 to combine town benefits with rural open space."
                }
            ],
            "Structural Mechanics II": [
                {
                    "id": 1,
                    "question": "In Finite Element Analysis (FEA), what matrix connects node displacements to applied nodal forces?",
                    "options": [
                        "A) Global Stiffness Matrix [K]",
                        "B) Mass Damping Matrix [M]",
                        "C) Thermal Coefficient Matrix [T]"
                    ],
                    "correct_index": 0,
                    "explanation": "The global stiffness matrix equation [F] = [K][u] relates forces [F] to displacements [u]."
                }
            ]
        }

        questions = subject_quizzes.get(subject, subject_quizzes["Architecture 101"])
        return {
            "agent": self.name,
            "subject": subject,
            "api_used": "Python Subject Engine",
            "questions": questions
        }

    def generate_flashcards(self, subject: str = "Architecture 101") -> List[Dict[str, Any]]:
        if subject in self.uploaded_decks and "flashcards" in self.uploaded_decks[subject]:
            return self.uploaded_decks[subject]["flashcards"]

        cards = {
            "Architecture 101": [
                {
                    "id": 1, 
                    "concept": "Béton Brut & Material Transparency", 
                    "definition": "Béton brut (raw concrete) leaves shuttering marks and wood-grain formwork exposed after cast removal. It expresses structural honesty by refusing decorative cladding.",
                    "takeaway": "Pioneered by Le Corbusier in Unité d'Habitation to convey civic accessibility, structural integrity, and post-war democratic architecture.",
                    "memory_score": 92
                },
                {
                    "id": 2, 
                    "concept": "Fenestration Ratios & Daylighting", 
                    "definition": "The precise spatial arrangement, proportioning, and thermal glazing specifications of window openings across a building facade.",
                    "takeaway": "Determines interior solar heat gain coefficients, passive cross-ventilation, and visual connection to exterior micro-climates.",
                    "memory_score": 85
                }
            ],
            "History of Urban Planning": [
                {
                    "id": 1, 
                    "concept": "Ebenezer Howard Three Magnets Diagram", 
                    "definition": "A foundational 1898 urban model contrasting 'Town' (high wages, overcrowding), 'Country' (nature, low wages), and 'Town-Country' (combining economic opportunity with open greenbelts).",
                    "takeaway": "Led to self-contained satellite towns of 32,000 residents encircled by agricultural greenbelts to stop industrial sprawl.",
                    "memory_score": 94
                }
            ],
            "Structural Mechanics II": [
                {
                    "id": 1, 
                    "concept": "FEA Matrix Displacement Formulation", 
                    "definition": "Mathematical formulation relating applied nodal forces [F] to node displacements [u] via global stiffness matrix [K]: [F] = [K][u].",
                    "takeaway": "Used in 3D CAD stress simulation software to model structural frame deflection, shear strain, and dynamic wind pressure.",
                    "memory_score": 96
                }
            ]
        }
        return cards.get(subject, cards["Architecture 101"])

    def process_uploaded_notes(self, file_name: str, file_text: str, subject: str = "General") -> Dict[str, Any]:
        text_clean = file_text.strip()
        
        raw_sentences = [s.strip() for s in re.split(r'[\n\.\?\!]+', text_clean) if len(s.strip()) > 15 and not s.strip().startswith('[Page')]
        if len(raw_sentences) < 3:
            raw_sentences = [
                f"Core theoretical fundamentals of {subject} in document {file_name}.",
                f"Analytical evaluation of key {subject} syllabus principles.",
                f"Practical project implementation framework."
            ]

        s1 = raw_sentences[0]
        s2 = raw_sentences[1] if len(raw_sentences) > 1 else raw_sentences[0]
        s3 = raw_sentences[2] if len(raw_sentences) > 2 else raw_sentences[0]

        concept1 = " ".join(s1.split()[:5]).title()
        concept2 = " ".join(s2.split()[:5]).title()
        concept3 = " ".join(s3.split()[:5]).title()

        summary = (
            f"PDF Document Analysis ('{file_name}'):\n"
            f"• Core Concept: {s1[:120]}\n"
            f"• Key Definition: {s2[:120]}\n"
            f"• Practical Focus: {s3[:120]}"
        )

        quiz = [
            {
                "id": 1,
                "question": f"Based on '{file_name}': What statement accurately describes {concept1}?",
                "options": [f"A) {s1[:90]}", f"B) {s2[:90]}", "C) Discarded historical hypothesis"],
                "correct_index": 0,
                "explanation": f"Extracted directly from '{file_name}': \"{s1[:120]}\""
            },
            {
                "id": 2,
                "question": f"According to '{file_name}': Which mechanism explains {concept2}?",
                "options": [f"A) {s2[:90]}", f"B) Alternative theory unrelated to {subject}", "C) Variable calculation error"],
                "correct_index": 0,
                "explanation": f"Extracted directly from '{file_name}': \"{s2[:120]}\""
            }
        ]

        flashcards = [
            {
                "id": 1,
                "concept": concept1,
                "definition": s1,
                "takeaway": f"Primary takeaway: {s1[:140]}",
                "memory_score": 95
            },
            {
                "id": 2,
                "concept": concept2,
                "definition": s2,
                "takeaway": f"Practical application: {s2[:140]}",
                "memory_score": 88
            }
        ]

        # 3. Dedicated Google Gemini AI High-Quality To-Do Task Generator
        generated_tasks = []
        if self.gemini.is_configured() and len(text_clean) > 20:
            prompt_tasks = (
                f"You are an expert AI Academic Coach generating high-quality, specific, non-repetitive study tasks from the syllabus document '{file_name}' for subject '{subject}'.\n"
                f"DOCUMENT TEXT:\n\"\"\"\n{text_clean[:2500]}\n\"\"\"\n\n"
                f"Generate 3 distinct, highly actionable study tasks for a student. Avoid generic phrases like 'Study Topic' or 'Review concepts'.\n"
                f"Return ONLY raw JSON list of 3 items with structure:\n"
                f'[\n'
                f'  {{"title": "Actionable specific task title (e.g. Master Schrodinger Wave Equation Derivation)", "tag": "#THEORY", "priority": "High", "due_date": "TODAY", "estimate": "1.5h", "bg_color": "bg-[#e5e2e1]"}},\n'
                f'  {{"title": "Actionable practice task title (e.g. Solve Quantum Tunneling Problem Set 2)", "tag": "#PRACTICE", "priority": "High", "due_date": "OCT 28", "estimate": "2h", "bg_color": "bg-accent-indigo/15"}},\n'
                f'  {{"title": "Actionable synthesis task title (e.g. Draft Case Study Summary & Formula Sheet)", "tag": "#SYNTHESIS", "priority": "Med", "due_date": "OCT 31", "estimate": "1h", "bg_color": "bg-accent-emerald/15"}}\n'
                f']\n'
            )
            raw_t = self.gemini.generate_content(prompt_tasks)
            if raw_t:
                try:
                    js_t = raw_t.strip()
                    if "```json" in js_t: js_t = js_t.split("```json")[1].split("```")[0].strip()
                    elif "```" in js_t: js_t = js_t.split("```")[1].split("```")[0].strip()
                    parsed_t = json.loads(js_t)
                    if isinstance(parsed_t, list) and len(parsed_t) >= 2:
                        generated_tasks = parsed_t
                except Exception as e:
                    print(f"Gemini Task Generation parse fallback: {e}")

        # Fallback NLP Cleaner if Gemini response unavailable
        if not generated_tasks:
            clean_t1 = re.sub(r'^(Unit|Chapter|Section|\d+[\.\:]\s*)+', '', concept1, flags=re.IGNORECASE).strip()
            clean_t2 = re.sub(r'^(Unit|Chapter|Section|\d+[\.\:]\s*)+', '', concept2, flags=re.IGNORECASE).strip()
            clean_t3 = re.sub(r'^(Unit|Chapter|Section|\d+[\.\:]\s*)+', '', concept3, flags=re.IGNORECASE).strip()

            generated_tasks = [
                {"title": f"Master Core Theory: {clean_t1} ({subject})", "tag": "#THEORY", "priority": "High", "due_date": "TODAY", "estimate": "1.5h", "bg_color": "bg-[#e5e2e1]"},
                {"title": f"Solve Problem Set: {clean_t2}", "tag": "#PRACTICE", "priority": "High", "due_date": "OCT 28", "estimate": "2h", "bg_color": "bg-accent-indigo/15"},
                {"title": f"Draft Analytical Outline: {clean_t3}", "tag": "#SYNTHESIS", "priority": "Med", "due_date": "OCT 31", "estimate": "1h", "bg_color": "bg-accent-emerald/15"}
            ]

        # Save Subject & To-Do Tasks into SQLite DB (with deduplication)
        import time
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Auto-add subject if not already present
            cursor.execute("SELECT COUNT(*) FROM subjects WHERE title = ?;", (subject,))
            if cursor.fetchone()[0] == 0:
                sub_id = f"s_{int(time.time())}"
                cursor.execute("""
                    INSERT INTO subjects (id, title, module, progress, attendance, credits, next_lesson, image_url)
                    VALUES (?, ?, 'MODULE 01', 0, 92, 4.0, 'Unit Overview & Revision', '');
                """, (sub_id, subject))

            for t in generated_tasks:
                cursor.execute("SELECT COUNT(*) FROM tasks WHERE title = ?;", (t["title"],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO tasks (title, tag, priority, due_date, completed, estimate, bg_color)
                        VALUES (?, ?, ?, ?, 0, ?, ?);
                    """, (t["title"], t["tag"], t.get("priority", "High"), t.get("due_date", "TODAY"), t.get("estimate", "1.5h"), t.get("bg_color", "bg-[#e5e2e1]")))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error inserting generated tasks & subject into SQLite DB: {e}")

        # Calendar Milestones
        calendar_events = [
            {"day": 31, "title": f"{subject} Midterm Studio Review", "type": "EXAM", "time": "09:00 AM - 11:30 AM", "details": f"Midterm review on {concept1} and {concept2} extracted from {file_name}."},
            {"day": 13, "title": f"{subject} Module Submission", "type": "SUBMISSION", "time": "02:00 PM - 04:00 PM", "details": f"Full portfolio draft submission for {subject} based on {file_name}."}
        ]

        # Daily Planner Timetable
        daily_planner = [
            {
                "id": 401,
                "time_slot": "09:00 AM - 11:30 AM (PEAK FOCUS)",
                "activity": f"Deep Focus: {concept1} ({subject})",
                "subject": subject,
                "reasoning": f"Morning peak focus window allocated for high-weight syllabus topic extracted from {file_name}.",
                "status": "PROPOSED",
                "reminder": "🔔 15 mins before (08:45 AM)"
            },
            {
                "id": 402,
                "time_slot": "02:00 PM - 04:00 PM",
                "activity": f"Module Practice Sprint: {concept2}",
                "subject": subject,
                "reasoning": f"Targeted problem set sprint for uploaded document {file_name}.",
                "status": "PROPOSED",
                "reminder": "🔔 15 mins before (01:45 PM)"
            },
            {
                "id": 403,
                "time_slot": "05:00 PM - 06:00 PM",
                "activity": f"Active Recall & Flashcards: {concept3}",
                "subject": subject,
                "reasoning": "Spaced repetition review to maximize exam retention.",
                "status": "PROPOSED",
                "reminder": "🔔 10 mins before (04:50 PM)"
            }
        ]

        result_payload = {
            "file_name": file_name,
            "subject": subject,
            "summary": summary,
            "quiz": quiz,
            "flashcards": flashcards,
            "tasks": generated_tasks,
            "calendar_events": calendar_events,
            "daily_planner": daily_planner
        }

        self.uploaded_decks[subject] = result_payload
        return result_payload
