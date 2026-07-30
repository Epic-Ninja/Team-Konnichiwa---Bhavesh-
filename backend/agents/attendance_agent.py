from typing import Dict, Any, List

class AttendanceAgent:
    def __init__(self, name: str = "AttendanceAgent"):
        self.name = name

    def evaluate_attendance(self, subjects: List[Dict[str, Any]]) -> Dict[str, Any]:
        risk_subjects = []
        for s in subjects:
            attendance = s.get("attendance", 90)
            if attendance < 75:
                risk_subjects.append({
                    "subject": s.get("title"),
                    "attendance": attendance,
                    "safe_bunks": 0,
                    "required_classes_to_recovery": 3,
                    "status": "CRITICAL_RISK"
                })
        
        has_risk = len(risk_subjects) > 0
        warning_msg = (
            f"Attendance Risk Alert: {risk_subjects[0]['subject']} is at {risk_subjects[0]['attendance']}% "
            f"(Minimum 75% required). Safe bunk allowance remaining: 0 classes."
            if has_risk else "All subject attendance records are above safe 75% thresholds."
        )

        return {
            "agent": self.name,
            "has_risk": has_risk,
            "warning": warning_msg,
            "risk_subjects": risk_subjects
        }
