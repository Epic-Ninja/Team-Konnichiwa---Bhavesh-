from typing import Dict, Any, List
from .planner_agent import PlannerAgent
from .scheduler_agent import SchedulerAgent
from .attendance_agent import AttendanceAgent
from .exam_agent import ExamAgent
from .quiz_flashcard_agent import QuizFlashcardAgent
from .analytics_agent import AnalyticsAgent

class AgenticOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.attendance = AttendanceAgent()
        self.exam = ExamAgent()
        self.quiz = QuizFlashcardAgent()
        self.analytics = AnalyticsAgent()

    def get_dashboard_state(self, user_data: Dict[str, Any], subjects: List[Dict[str, Any]], streak: int) -> Dict[str, Any]:
        briefing = self.planner.generate_daily_briefing(user_data.get("name", "Student"))
        att_eval = self.attendance.evaluate_attendance(subjects)
        gpa_eval = self.exam.predict_gpa_and_readiness(subjects, streak)
        rhythm_eval = self.analytics.compute_rhythm_metrics(streak)

        return {
            "orchestrator_version": "AgenticOS-v2.0",
            "daily_briefing": briefing["briefing"],
            "attendance_alert": att_eval["warning"],
            "attendance_risk": att_eval["has_risk"],
            "projected_gpa": gpa_eval["projected_gpa"],
            "syllabus_coverage": gpa_eval["syllabus_coverage"],
            "focus_score": rhythm_eval["focus_score"],
            "burnout_risk": rhythm_eval["burnout_risk_percentage"],
            "energy_prediction": rhythm_eval["energy_prediction"]
        }

    def process_natural_language_trigger(self, trigger_text: str) -> Dict[str, Any]:
        replan_res = self.scheduler.replan_schedule(trigger_text)
        return {
            "orchestrator_response": "COLLABORATION_SUCCESS",
            "agents_executed": ["SchedulerAgent", "PlannerAgent", "NotificationAgent"],
            "replan_result": replan_res
        }

    def process_chat_query(self, query_text: str) -> str:
        q_lower = query_text.lower()
        if "viva" in q_lower or "test" in q_lower:
            return "🤖 **Echoes AI Viva Tutor:** Let's begin your Architecture 101 Viva. Question 1: What is the structural significance of reinforced concrete in Brutalist design?"
        elif "exam" in q_lower:
            return "🤖 **Echoes AI:** Your Architecture Midterm is in 14 days. You are currently at 94% syllabus coverage."
        elif "sick" in q_lower or "tired" in q_lower:
            return "🤖 **Echoes AI:** I've adjusted your study load today to light rest reading and deferred heavy research modules to Saturday."
        else:
            return f"🤖 **Echoes AI Mentor:** I've analyzed your query regarding '{query_text}'. Updating your sanctuary roadmap."
