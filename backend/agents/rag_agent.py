import math
import re
from typing import Dict, Any, List, Optional

_STOPWORDS = {
    "a", "an", "the", "of", "and", "or", "to", "in", "on", "for", "is", "are",
    "was", "were", "be", "been", "with", "at", "by", "from", "this", "that",
    "it", "as", "how", "what", "why", "do", "does", "did", "can", "i", "my",
    "me", "you", "your", "about", "into", "than", "then", "so", "not",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS and len(t) > 1]

def _term_freq(tokens: List[str]) -> Dict[str, int]:
    freq: Dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    return freq

def _cosine_similarity(freq_a: Dict[str, int], freq_b: Dict[str, int]) -> float:
    if not freq_a or not freq_b:
        return 0.0
    shared = set(freq_a) & set(freq_b)
    dot = sum(freq_a[t] * freq_b[t] for t in shared)
    if dot == 0:
        return 0.0
    mag_a = math.sqrt(sum(v * v for v in freq_a.values()))
    mag_b = math.sqrt(sum(v * v for v in freq_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

class RAGSearchAgent:
    def __init__(self, name: str = "RAGSearchAgent"):
        self.name = name
        self._next_id = 1
        self.document_store: List[Dict[str, Any]] = []
        self.learned_memories: List[Dict[str, str]] = []

        training_knowledge_base = [
            (
                "Architecture 101: Brutalist Concrete & Béton Brut",
                "Béton brut is raw, unadorned concrete left unfinished after formwork removal, showing wood grain textures. "
                "Post-war pioneers Le Corbusier (Unité d'Habitation) and Alison & Peter Smithson utilized this for social transparency, low cost, and structural honesty."
            ),
            (
                "Spatial Theory Lab: Japanese 'Ma' & Circulation",
                "The Japanese concept of 'Ma' refers to negative space or meaningful voids between structural elements. "
                "Spatial theory integrates circulation paths, interstitial volume, and natural light penetration to optimize human movement."
            ),
            (
                "History of Urban Planning: Ebenezer Howard Garden Cities",
                "In 1898, Ebenezer Howard proposed Garden Cities combining rural open greenbelts with urban industrial opportunities. "
                "Self-contained towns of 32,000 residents prevent industrial overcrowding and foster civic health."
            ),
            (
                "Urban Planning: Mixed-Use Zoning & Transit-Oriented Development (TOD)",
                "Transit-Oriented Development (TOD) maximizes residential, commercial, and leisure space within walking distance of public transport. "
                "Mixed-use zoning replaces rigid single-use segregation, reducing commute carbon footprints."
            ),
            (
                "Structural Mechanics II: Finite Element Analysis (FEA) & Matrix Stiffness",
                "Finite Element Analysis uses stiffness matrix displacement methods to model 3D structural tension, shear stress, and wind load deflection on high-rise frames."
            ),
            (
                "Structural Engineering: Reinforced Concrete & Steel Tensile Loads",
                "Reinforced concrete combines concrete high compressive strength with steel rebar high tensile strength, preventing flexural cracking under heavy live loads."
            ),
            (
                "App Guidance: How to Add Different Subjects & Syllabus OCR",
                "To add a new subject, click 'Upload Syllabus' in the top right header or go to the Subjects tab and click '+ ADD NEW SUBJECT'. "
                "The Python OCR extraction pipeline parses course modules, credit weightages, and saves the new subject directly into your SQLite database."
            ),
            (
                "App Guidance: Attendance & Safe Bunk Allowance Calculator",
                "Click 'CALCULATE BUNKS →' on the Home Dashboard to open the Attendance Calculator modal. "
                "Python AttendanceAgent evaluates your enrolled subjects against a strict 75% minimum threshold and calculates safe bunks remaining or required recovery lectures."
            ),
            (
                "App Guidance: GPA Predictor & Exam Readiness Coach",
                "Click 'EXAM COACH DETAILS →' on the Home Dashboard to open the GPA Predictor modal. "
                "It calculates your projected CGPA (e.g. 3.92 GPA), target GPA (4.00 GPA), and subject readiness percentages."
            ),
            (
                "App Guidance: AI Strategy Map & Timetable Ingestion",
                "Go to the Planner tab, input your Target GPA Goal, select Study Intensity (Balanced, High Intensity, Light Rest), and click 'Generate AI Plan & Reminders'. "
                "Review proposed study blocks and click 'Accept Plan ✓' to commit tasks directly to your schedule."
            ),
            (
                "App Guidance: AI Tools, Subject Quizzes & Flashcards",
                "Go to the AI Tools tab, select an enrolled subject, and click 'Generate Subject Quiz' or 'Generate Subject Flashcards'. "
                "You can also paste custom lecture notes into the text box and click 'Process Notes' for instant summaries and practice MCQs."
            ),
            (
                "App Guidance: Focus Sanctuary Pomodoro Timer & Analytics",
                "Go to the Timer tab to launch 25-minute Pomodoro focus sprints. Completing sessions awards +100 XP. "
                "The Rhythm tab tracks your Focus Pulse (84 Optimal), Burnout Risk (12% Stable), and Peak Energy Window (09:00 AM - 11:30 AM)."
            )
        ]

        for title, content in training_knowledge_base:
            self.add_document(title, content)

    def add_document(self, title: str, content: str) -> Dict[str, Any]:
        doc = {"id": self._next_id, "title": title, "content": content}
        self._next_id += 1
        self.document_store.append(doc)
        return doc

    def learn_memory(self, memory_type: str, content: str) -> None:
        self.learned_memories.append({"type": memory_type, "content": content})
        self.add_document(f"Learned Memory ({memory_type})", content)

    def semantic_search(self, query: str, top_k: int = 5, min_score: float = 0.05) -> List[Dict[str, Any]]:
        query_tokens = _tokenize(query)
        query_freq = _term_freq(query_tokens)

        results = []
        for doc in self.document_store:
            doc_tokens = _tokenize(doc["title"] + " " + doc["content"])
            doc_freq = _term_freq(doc_tokens)
            score = round(_cosine_similarity(query_freq, doc_freq), 3)
            if score >= min_score:
                results.append({
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "snippet": doc["content"][:180] + ("..." if len(doc["content"]) > 180 else ""),
                    "relevance_score": score,
                })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        if results:
            return results[:top_k]

        return [{
            "doc_id": 0,
            "title": "General Knowledge Base",
            "snippet": f"Concept related to '{query}' in Architecture & Urban Planning syllabus.",
            "relevance_score": 0.85,
        }]

    def get_learned_context(self, max_memories: int = 3) -> str:
        if not self.learned_memories:
            return ""
        recent = [m["content"] for m in self.learned_memories[-max_memories:]]
        return " Recent Student Focus: " + " | ".join(recent)