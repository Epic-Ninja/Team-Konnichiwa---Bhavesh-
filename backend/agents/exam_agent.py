from typing import Dict, Any, List

class ExamAgent:
    def __init__(self, name: str = "ExamAgent"):
        self.name = name

    def predict_gpa_and_readiness(self, subjects: List[Dict[str, Any]], streak: int) -> Dict[str, Any]:
        total_progress = sum(s.get("progress", 50) for s in subjects) / max(len(subjects), 1)
        projected_gpa = round(3.5 + (total_progress / 100.0) * 0.45, 2)
        readiness_score = int(total_progress * 1.1)
        if readiness_score > 98: readiness_score = 98

        return {
            "agent": self.name,
            "projected_gpa": f"{projected_gpa} GPA",
            "readiness_percentage": readiness_score,
            "syllabus_coverage": f"{int(total_progress)}%",
            "risk_level": "LOW_RISK" if total_progress > 60 else "MEDIUM_RISK"
        }
