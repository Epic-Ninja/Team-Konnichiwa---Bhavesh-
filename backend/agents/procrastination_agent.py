from typing import Dict, Any

class ProcrastinationBurnoutAgent:
    def __init__(self, name: str = "ProcrastinationBurnoutAgent"):
        self.name = name

    def evaluate_wellbeing(self, streak_days: int, completed_task_ratio: float) -> Dict[str, Any]:
        is_procrastinating = completed_task_ratio < 0.5
        is_burnout_risk = streak_days > 30 and completed_task_ratio > 0.95

        if is_procrastinating:
            status = "PROCRASTINATION_DETECTED"
            recommendation = "Break tasks into 15-minute micro-sprints. Start with a 5-minute low-effort quiet reading."
        elif is_burnout_risk:
            status = "BURNOUT_RISK_HIGH"
            recommendation = "You have maintained an intense streak over 30 days. Take a mandatory 1-hour walk or meditation break."
        else:
            status = "BALANCED_RHYTHM"
            recommendation = "Workload and focus breaks are in optimal harmony. Maintain current 25-minute pomodoro cadence."

        return {
            "agent": self.name,
            "wellbeing_status": status,
            "recommendation": recommendation,
            "procrastination_index": round(1.0 - completed_task_ratio, 2),
            "burnout_risk_score": 12 if not is_burnout_risk else 65
        }
