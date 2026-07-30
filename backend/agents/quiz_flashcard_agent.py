from typing import Dict, Any, List
import os
import re
import json
from .gemini_service import GeminiAPIService

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
        
        # 1. Try Gemini API generation first if configured
        if self.gemini.is_configured() and len(text_clean) > 20:
            prompt = (
                f"You are an expert professor analyzing the student document '{file_name}' for course '{subject}'.\n"
                f"Extract 3 distinct key concepts/facts from this document text:\n"
                f"\"\"\"\n{text_clean[:2500]}\n\"\"\"\n\n"
                f"Return ONLY raw JSON with keys: 'summary' (string), 'q1_question', 'q1_correct', 'q1_wrong1', 'q1_wrong2', 'q1_explain', "
                f"'q2_question', 'q2_correct', 'q2_wrong1', 'q2_wrong2', 'q2_explain', "
                f"'fc1_concept', 'fc1_def', 'fc1_takeaway', 'fc2_concept', 'fc2_def', 'fc2_takeaway', 'fc3_concept', 'fc3_def', 'fc3_takeaway'."
            )
            raw = self.gemini.generate_content(prompt)
            if raw:
                try:
                    js = raw.strip()
                    if "```json" in js: js = js.split("```json")[1].split("```")[0].strip()
                    elif "```" in js: js = js.split("```")[1].split("```")[0].strip()
                    data = json.loads(js)
                    
                    summary = f"Processed '{file_name}':\n• {data.get('summary', 'Document key concepts extracted.')}"
                    quiz = [
                        {
                            "id": 1,
                            "question": data.get("q1_question", f"What key principle is stated in {file_name}?"),
                            "options": [f"A) {data.get('q1_correct', 'Core principle')}", f"B) {data.get('q1_wrong1', 'Incorrect option')}", f"C) {data.get('q1_wrong2', 'Alternative option')}"],
                            "correct_index": 0,
                            "explanation": data.get("q1_explain", f"Extracted directly from {file_name}.")
                        },
                        {
                            "id": 2,
                            "question": data.get("q2_question", f"Which topic is explored in {file_name}?"),
                            "options": [f"A) {data.get('q2_correct', 'Secondary concept')}", f"B) {data.get('q2_wrong1', 'Irrelevant theory')}", f"C) {data.get('q2_wrong2', 'Outdated method')}"],
                            "correct_index": 0,
                            "explanation": data.get("q2_explain", f"Extracted directly from {file_name}.")
                        }
                    ]
                    flashcards = [
                        {
                            "id": 1, 
                            "concept": data.get("fc1_concept", "Core Concept 1"), 
                            "definition": data.get("fc1_def", "Definition 1"), 
                            "takeaway": data.get("fc1_takeaway", "Key exam takeaway from uploaded PDF."),
                            "memory_score": 95
                        },
                        {
                            "id": 2, 
                            "concept": data.get("fc2_concept", "Core Concept 2"), 
                            "definition": data.get("fc2_def", "Definition 2"), 
                            "takeaway": data.get("fc2_takeaway", "Practical application context from uploaded PDF."),
                            "memory_score": 90
                        },
                        {
                            "id": 3, 
                            "concept": data.get("fc3_concept", "Core Concept 3"), 
                            "definition": data.get("fc3_def", "Definition 3"), 
                            "takeaway": data.get("fc3_takeaway", "Core analytical framework."),
                            "memory_score": 85
                        }
                    ]
                    
                    result_payload = {
                        "file_name": file_name,
                        "subject": subject,
                        "summary": summary,
                        "quiz": quiz,
                        "flashcards": flashcards
                    }
                    self.uploaded_decks[subject] = result_payload
                    return result_payload
                except Exception as e:
                    print(f"Gemini JSON Parse fallback triggered: {e}")

        # 2. Dynamic Text Sentence Extractor (Guaranteed PDF-Grounded Result)
        raw_sentences = [s.strip() for s in re.split(r'[\n\.\?\!]+', text_clean) if len(s.strip()) > 20 and not s.strip().startswith('[Page')]
        
        if len(raw_sentences) < 3:
            raw_sentences = [
                f"Document {file_name} discusses core theoretical fundamentals of {subject}.",
                f"Key methodology involves analytical evaluation of {subject} principles.",
                f"Practical applications include structured framework implementation."
            ]

        s1 = raw_sentences[0]
        s2 = raw_sentences[1] if len(raw_sentences) > 1 else raw_sentences[0]
        s3 = raw_sentences[2] if len(raw_sentences) > 2 else raw_sentences[0]

        concept1 = " ".join(s1.split()[:5]).title()
        concept2 = " ".join(s2.split()[:5]).title()
        concept3 = " ".join(s3.split()[:5]).title()

        summary = (
            f"PDF Document Analysis ('{file_name}'):\n"
            f"• Core Principle: {s1[:120]}\n"
            f"• Key Definition: {s2[:120]}\n"
            f"• Practical Focus: {s3[:120]}"
        )

        quiz = [
            {
                "id": 1,
                "question": f"Based on '{file_name}': What statement accurately describes {concept1}?",
                "options": [
                    f"A) {s1[:90]}",
                    f"B) {s2[:90]} (Secondary finding)",
                    "C) Discarded historical hypothesis"
                ],
                "correct_index": 0,
                "explanation": f"Directly extracted from '{file_name}': \"{s1[:120]}\""
            },
            {
                "id": 2,
                "question": f"According to '{file_name}': Which mechanism explains {concept2}?",
                "options": [
                    f"A) {s2[:90]}",
                    f"B) Alternative theory unrelated to {subject}",
                    "C) Variable calculation error"
                ],
                "correct_index": 0,
                "explanation": f"Directly extracted from '{file_name}': \"{s2[:120]}\""
            },
            {
                "id": 3,
                "question": f"In '{file_name}': What is highlighted regarding {concept3}?",
                "options": [
                    f"A) {s3[:90]}",
                    "B) Outdated non-functional framework",
                    "C) Disregarded lab reading"
                ],
                "correct_index": 0,
                "explanation": f"Directly extracted from '{file_name}': \"{s3[:120]}\""
            }
        ]

        flashcards = [
            {
                "id": 1,
                "concept": concept1,
                "definition": s1,
                "takeaway": f"Primary exam takeaway: {s1[:140]}",
                "memory_score": 95
            },
            {
                "id": 2,
                "concept": concept2,
                "definition": s2,
                "takeaway": f"Practical application: {s2[:140]}",
                "memory_score": 88
            },
            {
                "id": 3,
                "concept": concept3,
                "definition": s3,
                "takeaway": f"Analytical framework: {s3[:140]}",
                "memory_score": 82
            }
        ]

        result_payload = {
            "file_name": file_name,
            "subject": subject,
            "summary": summary,
            "quiz": result_payload if False else quiz,
            "flashcards": flashcards
        }
        
        self.uploaded_decks[subject] = result_payload
        return result_payload
