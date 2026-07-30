from typing import Dict, Any, List

class SchedulerAgent:
    def __init__(self, name: str = "SchedulerAgent"):
        self.name = name

    def replan_schedule(self, trigger_text: str) -> Dict[str, Any]:
        text_lower = trigger_text.lower()
        if "sick" in text_lower:
            rationale = "Illness detected. Paused heavy research modules and scheduled a 30-min tea ritual recovery reading."
            action_taken = "REDUCE_WORKLOAD_ADD_RECOVERY"
            new_task = {
                "id": 999,
                "title": "Rest & Quiet Tea Ritual Reading (30m)",
                "tag": "#RECOVERY",
                "priority": "Low",
                "date": "TODAY",
                "completed": 0,
                "estimate": "0.5h",
                "bg_color": "bg-accent-emerald/20"
            }
            return {
                "agent": self.name,
                "action": action_taken,
                "rationale": rationale,
                "confidence_score": 0.98,
                "injected_task": new_task
            }
        elif "2 hours" in text_lower or "hours" in text_lower:
            rationale = "Workload compressed to 2h peak focus window. Non-critical asset tasks deferred to tomorrow."
            return {
                "agent": self.name,
                "action": "COMPRESS_PEAK_WINDOW",
                "rationale": rationale,
                "confidence_score": 0.95
            }
        elif "exam" in text_lower:
            rationale = "Exam date shifted earlier. Midterm practice review sessions moved up 2 days."
            return {
                "agent": self.name,
                "action": "SHIFT_EXAM_PREP_EARLIER",
                "rationale": rationale,
                "confidence_score": 0.96
            }
        else:
            rationale = f"Rebuilt schedule around trigger: '{trigger_text}'. Workload balanced."
            return {
                "agent": self.name,
                "action": "OPTIMIZE_WEEKLY_CALENDAR",
                "rationale": rationale,
                "confidence_score": 0.92
            }
