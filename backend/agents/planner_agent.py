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

    def ingest_timetable_and_goals(self, timetable: Any, assignments: Any, goals: Dict[str, Any]) -> Dict[str, Any]:
        target_gpa = goals.get("target_gpa", "3.92 GPA")
        intensity = goals.get("intensity", "Balanced")
        custom_timetable = goals.get("timetable_text", "")
        custom_assignments = goals.get("assignments_text", "")

        plan_items = []

        if custom_timetable or custom_assignments:
            plan_items.append({
                "id": 201,
                "time_slot": "09:00 AM - 11:30 AM (PEAK FOCUS)",
                "activity": f"Ingested Timetable Focus: {custom_timetable[:60] if custom_timetable else 'Structural FEA Calculations'}",
                "subject": "Core Enrolled Subject",
                "reasoning": f"Scheduled during morning peak focus window to hit target {target_gpa} under {intensity} intensity.",
                "status": "PROPOSED",
                "reminder": "🔔 15 mins before (08:45 AM)"
            })
            plan_items.append({
                "id": 202,
                "time_slot": "02:00 PM - 04:00 PM",
                "activity": f"Ingested Assignment Priority: {custom_assignments[:60] if custom_assignments else 'History of Urban Planning Draft'}",
                "subject": "Priority Assignment",
                "reasoning": f"Priority deadline task ingested from your submission list.",
                "status": "PROPOSED",
                "reminder": "🔔 15 mins before (01:45 PM)"
            })
            plan_items.append({
                "id": 203,
                "time_slot": "05:00 PM - 06:00 PM",
                "activity": "Active Recall & Flashcard Revision Sprint",
                "subject": "Syllabus Review",
                "reasoning": "Spaced repetition review to prevent memory decay.",
                "status": "PROPOSED",
                "reminder": "🔔 10 mins before (04:50 PM)"
            })
        else:
            plan_items = [
                {
                    "id": 101,
                    "time_slot": "09:00 AM - 11:00 AM (PEAK FOCUS)",
                    "activity": "Deep Work: Structural Mechanics FEA Matrix",
                    "subject": "Structural Mechanics II",
                    "reasoning": f"Scheduled in morning peak focus window to hit target {target_gpa}.",
                    "status": "PROPOSED",
                    "reminder": "🔔 15 mins before (08:45 AM)"
                },
                {
                    "id": 102,
                    "time_slot": "02:00 PM - 03:30 PM",
                    "activity": "History of Urban Planning Assignment Draft",
                    "subject": "History of Urban Planning",
                    "reasoning": "Priority deadline approaching in 3 days. Attendance at 74% requires active submission.",
                    "status": "PROPOSED",
                    "reminder": "🔔 15 mins before (01:45 PM)"
                },
                {
                    "id": 103,
                    "time_slot": "05:00 PM - 06:00 PM",
                    "activity": "Architecture 101 Brutalist Flashcards Review",
                    "subject": "Architecture 101",
                    "reasoning": "Spaced repetition memory score decay check (Béton Brut concept).",
                    "status": "PROPOSED",
                    "reminder": "🔔 10 mins before (04:50 PM)"
                }
            ]

        return {
            "agent": self.name,
            "goals": goals,
            "plan_status": "PROPOSED",
            "progress_percentage": 0,
            "reminders_count": len(plan_items),
            "generated_plan": plan_items
        }

    def generate_roadmap(self, subject_title: str) -> List[Dict[str, Any]]:
        return [
            {"unit": "Unit 1", "topic": "Historical Roots of Modernism", "status": "COMPLETED", "hours": 3.0},
            {"unit": "Unit 2", "topic": "Béton Brut & Material Transparency", "status": "IN_PROGRESS", "hours": 4.0},
            {"unit": "Unit 3", "topic": "Post-War Welfare Housing in Britain", "status": "UPCOMING", "hours": 3.5},
            {"unit": "Unit 4", "topic": "Brutalist Urban Planning Case Studies", "status": "UPCOMING", "hours": 5.0}
        ]
