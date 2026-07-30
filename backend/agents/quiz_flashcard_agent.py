from typing import Dict, Any, List

class QuizFlashcardAgent:
    def __init__(self, name: str = "QuizFlashcardAgent"):
        self.name = name

    def generate_quiz(self, topic: str = "Architecture 101") -> Dict[str, Any]:
        return {
            "agent": self.name,
            "topic": topic,
            "questions": [
                {
                    "id": 1,
                    "question": "Which socio-political movement heavily influenced British Brutalist architecture post-WWII?",
                    "options": [
                        "A) Post-War Welfare State Housing & Material Transparency",
                        "B) Victorian Industrial Revivalism",
                        "C) High-Tech Structural Expressionism"
                    ],
                    "correct_index": 0,
                    "explanation": "Brutalism in post-war Britain was deeply connected to social democracy and the welfare state, prioritizing low-cost, honest materials like unadorned concrete."
                }
            ]
        }

    def generate_flashcards(self, subject: str = "Architecture 101") -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "concept": "Béton Brut",
                "definition": "Raw concrete left unfinished after formwork removal, revealing seam lines and grain texture.",
                "memory_score": 88
            },
            {
                "id": 2,
                "concept": "Fenestration Pattern",
                "definition": "The arrangement, proportion, and design of windows and openings in a building facade.",
                "memory_score": 75
            }
        ]
