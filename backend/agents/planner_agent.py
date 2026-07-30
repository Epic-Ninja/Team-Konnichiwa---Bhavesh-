from typing import Dict, Any, List

class PlannerAgent:
    def __init__(self, name: str = "PlannerAgent"):
        self.name = name

    def generate_daily_briefing(self, user_name: str, available_hours: float = 2.5) -> Dict[str, Any]:
        first_name = user_name.split(' ')[0] if user_name else "Student"
        briefing_text = (
            f"Good morning, {first_name}. You have {available_hours} available study hours today. "
            f"Your peak focus window starts at 09:00 AM. If you complete 2 chapters of Brutalist Textures, "
            f"you will finish the midterm roadmap 4 days early."
        )
        return {
            "agent": self.name,
            "briefing": briefing_text,
            "available_hours": available_hours,
            "peak_window": "09:00 AM - 11:30 AM",
            "projected_finish_delta_days": 4
        }

    def generate_roadmap(self, subject_title: str) -> List[Dict[str, Any]]:
        return [
            {"unit": "Unit 1", "topic": "Historical Roots of Modernism", "status": "COMPLETED", "hours": 3.0},
            {"unit": "Unit 2", "topic": "Béton Brut & Material Transparency", "status": "IN_PROGRESS", "hours": 4.0},
            {"unit": "Unit 3", "topic": "Post-War Welfare Housing in Britain", "status": "UPCOMING", "hours": 3.5},
            {"unit": "Unit 4", "topic": "Brutalist Urban Planning Case Studies", "status": "UPCOMING", "hours": 5.0}
        ]
