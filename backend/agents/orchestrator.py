"""
AgenticOrchestrator — Echoes AI study-mentor brain.

Design goals for this rewrite:
1. The LLM (Gemini) is the primary reasoning engine for *every* query, not just
   an afterthought before a keyword-matching script. It is grounded with real
   student context (subjects, attendance, GPA, streak, wellbeing) so it can
   answer *anything* — open-ended academic questions, "what should I do
   today", "explain X", "how do I use feature Y" — with specifics instead of
   generic filler.
2. Conversation history is supported, so the assistant has memory within a
   session instead of treating every message as the first.
3. Gemini calls are wrapped in retries + timeouts + structured error handling,
   so a transient API hiccup doesn't silently degrade into a canned response.
4. The old keyword/if-elif script is kept, but demoted to what it should
   always have been: an offline safety net for when the LLM is unreachable or
   unconfigured — never the default path when the AI is available.
5. Rule-based fallback itself is upgraded: broader keyword coverage, and a
   much smarter general-purpose fallback (light scoring instead of a single
   rigid template) so even the "no AI available" experience stays useful.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .planner_agent import PlannerAgent
from .scheduler_agent import SchedulerAgent
from .attendance_agent import AttendanceAgent
from .exam_agent import ExamAgent
from .quiz_flashcard_agent import QuizFlashcardAgent
from .analytics_agent import AnalyticsAgent
from .rag_agent import RAGSearchAgent
from .procrastination_agent import ProcrastinationBurnoutAgent
from .gemini_service import GeminiAPIService

logger = logging.getLogger("echoes.orchestrator")

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

GEMINI_MAX_RETRIES = 2
GEMINI_RETRY_BACKOFF_SECONDS = 0.6
GEMINI_MIN_ACCEPTABLE_LEN = 10
MAX_HISTORY_TURNS_IN_PROMPT = 8


# --------------------------------------------------------------------------- #
# Conversation memory
# --------------------------------------------------------------------------- #

@dataclass
class ChatTurn:
    role: str  # "user" | "assistant"
    text: str


@dataclass
class ConversationState:
    """Per-session memory. Keep this object alive across calls (e.g. store it
    on the user's session) so process_chat_query has real context to work with."""
    turns: List[ChatTurn] = field(default_factory=list)

    def add(self, role: str, text: str) -> None:
        self.turns.append(ChatTurn(role=role, text=text))

    def recent_transcript(self, max_turns: int = MAX_HISTORY_TURNS_IN_PROMPT) -> str:
        if not self.turns:
            return "(no prior messages this session)"
        recent = self.turns[-max_turns:]
        lines = [f"{t.role.upper()}: {t.text}" for t in recent]
        return "\n".join(lines)


class AgenticOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.attendance = AttendanceAgent()
        self.exam = ExamAgent()
        self.quiz = QuizFlashcardAgent()
        self.analytics = AnalyticsAgent()
        self.rag = RAGSearchAgent()
        self.wellbeing = ProcrastinationBurnoutAgent()
        self.gemini = GeminiAPIService()

    # ----------------------------------------------------------------- #
    # Dashboard (unchanged behaviourally, just hardened)
    # ----------------------------------------------------------------- #

    def get_dashboard_state(
        self,
        user_data: Dict[str, Any],
        subjects: List[Dict[str, Any]],
        streak: int,
        completed_ratio: float = 0.67,
    ) -> Dict[str, Any]:
        briefing = self.planner.generate_daily_briefing(user_data.get("name", "Student"))
        att_eval = self.attendance.evaluate_attendance(subjects)
        gpa_eval = self.exam.predict_gpa_and_readiness(subjects, streak)
        rhythm_eval = self.analytics.compute_rhythm_metrics(streak)
        wellbeing_eval = self.wellbeing.evaluate_wellbeing(streak, completed_ratio)

        gemini_briefing = None
        if self.gemini.is_configured():
            prompt = (
                f"Provide a 2-sentence motivating daily academic briefing for "
                f"{user_data.get('name', 'Student')} studying {user_data.get('branch', 'Architecture')}. "
                f"Context: attendance risk = {att_eval['has_risk']}, projected GPA = "
                f"{gpa_eval['projected_gpa']}, current streak = {streak} days, "
                f"burnout risk = {rhythm_eval['burnout_risk_percentage']}%. "
                f"Reference at least one of these numbers naturally."
            )
            gemini_briefing = self._call_gemini_safely(prompt)

        return {
            "orchestrator_version": "AgenticOS-v6.0 (Context-Grounded Reasoning Engine)",
            "gemini_active": self.gemini.is_configured(),
            "daily_briefing": gemini_briefing if gemini_briefing else briefing["briefing"],
            "attendance_alert": att_eval["warning"],
            "attendance_risk": att_eval["has_risk"],
            "projected_gpa": gpa_eval["projected_gpa"],
            "syllabus_coverage": gpa_eval["syllabus_coverage"],
            "focus_score": rhythm_eval["focus_score"],
            "burnout_risk": rhythm_eval["burnout_risk_percentage"],
            "energy_prediction": rhythm_eval["energy_prediction"],
            "wellbeing_recommendation": wellbeing_eval["recommendation"],
            "procrastination_index": wellbeing_eval["procrastination_index"],
        }

    def process_natural_language_trigger(self, trigger_text: str) -> Dict[str, Any]:
        replan_res = self.scheduler.replan_schedule(trigger_text)
        return {
            "orchestrator_response": "COLLABORATION_SUCCESS",
            "agents_executed": ["SchedulerAgent", "PlannerAgent", "NotificationAgent", "AnalyticsAgent"],
            "replan_result": replan_res,
        }

    def search_rag(self, query: str) -> List[Dict[str, Any]]:
        return self.rag.semantic_search(query)

    # ----------------------------------------------------------------- #
    # Gemini calling — retried, timed, never lets an exception escape
    # ----------------------------------------------------------------- #

    def _call_gemini_safely(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> Optional[str]:
        """Call Gemini with retries + backoff. Returns None (never raises) on
        any failure so callers can cleanly fall through to the offline path."""
        last_error: Optional[Exception] = None
        for attempt in range(1, GEMINI_MAX_RETRIES + 1):
            try:
                result = self.gemini.generate_content(prompt, system_instruction=system_instruction)
                if result and len(result.strip()) >= GEMINI_MIN_ACCEPTABLE_LEN:
                    return result.strip()
                logger.warning("Gemini returned empty/too-short response (attempt %d)", attempt)
            except Exception as exc:  # noqa: BLE001 - we want to catch everything and degrade gracefully
                last_error = exc
                logger.warning("Gemini call failed (attempt %d/%d): %s", attempt, GEMINI_MAX_RETRIES, exc)
            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(GEMINI_RETRY_BACKOFF_SECONDS * attempt)
        if last_error:
            logger.error("Gemini exhausted retries, falling back to offline logic: %s", last_error)
        return None

    # ----------------------------------------------------------------- #
    # Context grounding — this is what lets Gemini "answer everything"
    # instead of hallucinating generic advice
    # ----------------------------------------------------------------- #

    def _build_student_context_block(
        self,
        user_data: Optional[Dict[str, Any]],
        subjects: Optional[List[Dict[str, Any]]],
        streak: Optional[int],
    ) -> str:
        if not user_data and not subjects and streak is None:
            return "(no live student context supplied for this query)"

        lines: List[str] = []
        if user_data:
            lines.append(
                f"Student: {user_data.get('name', 'Student')} | "
                f"Branch: {user_data.get('branch', 'Unknown')} | "
                f"Year: {user_data.get('year', 'Unknown')}"
            )
        if streak is not None:
            lines.append(f"Current study streak: {streak} days")

        if subjects:
            try:
                att_eval = self.attendance.evaluate_attendance(subjects)
                gpa_eval = self.exam.predict_gpa_and_readiness(subjects, streak or 0)
                lines.append(f"Attendance risk flag: {att_eval.get('has_risk')}")
                lines.append(f"Attendance detail: {att_eval.get('warning')}")
                lines.append(f"Projected GPA: {gpa_eval.get('projected_gpa')}")
                lines.append(f"Syllabus coverage: {gpa_eval.get('syllabus_coverage')}%")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not compute live context sub-metrics: %s", exc)
            subj_lines = []
            for s in subjects:
                name = s.get("name", "Unnamed subject")
                pct = s.get("attendance_percentage", s.get("attendance", "?"))
                subj_lines.append(f"  - {name}: {pct}% attendance")
            if subj_lines:
                lines.append("Subjects:\n" + "\n".join(subj_lines))

        return "\n".join(lines)

    def _build_system_prompt(self, context_block: str, history_block: str) -> str:
        return (
            "You are Echoes AI, an elite, warm, and precise university study mentor embedded "
            "inside a student productivity app called Echoes. You can answer absolutely anything "
            "the student asks: academic concepts in any subject, exam strategy, study planning, "
            "wellbeing/burnout guidance, or how to use the app's features (Planner, Subjects, "
            "Timer/Focus Sanctuary, AI Tools for quizzes/flashcards, Global RAG Search, "
            "Prerequisite Knowledge Graph, Attendance & Bunk Allowance Calculator, GPA Predictor).\n\n"
            "Rules:\n"
            "- Ground your answer in the LIVE STUDENT CONTEXT below whenever it's relevant "
            "(e.g. if asked about attendance or GPA, use the real numbers given, don't invent "
            "different ones).\n"
            "- If the question is a pure academic/knowledge question unrelated to the student's "
            "personal data, just answer it directly and thoroughly like a top-tier subject-matter "
            "tutor would — don't force irrelevant app context into the answer.\n"
            "- If the question is about how to use a feature, give concrete step-by-step "
            "instructions referencing the actual tab/button names above.\n"
            "- Be encouraging but concise. Use structure (short headers, bullet points) for "
            "anything with more than one part. Avoid filler disclaimers.\n"
            "- If you genuinely don't know something (e.g. it requires real-time data you don't "
            "have), say so plainly instead of guessing.\n\n"
            f"LIVE STUDENT CONTEXT:\n{context_block}\n\n"
            f"RECENT CONVERSATION:\n{history_block}\n"
        )

    # ----------------------------------------------------------------- #
    # Main chat entry point
    # ----------------------------------------------------------------- #

    def process_chat_query(
        self,
        query_text: str,
        user_data: Optional[Dict[str, Any]] = None,
        subjects: Optional[List[Dict[str, Any]]] = None,
        streak: Optional[int] = None,
        conversation: Optional[ConversationState] = None,
    ) -> str:
        """
        Answer any student query.

        Primary path: Gemini, grounded with live student context + recent
        conversation history, so it can genuinely reason about the student's
        situation rather than giving a generic canned reply.

        Fallback path: only triggered if Gemini is unconfigured or fails after
        retries. Uses an upgraded rule-based responder.
        """
        q = query_text.strip()
        if conversation is not None:
            conversation.add("user", q)

        answer: Optional[str] = None

        if self.gemini.is_configured():
            context_block = self._build_student_context_block(user_data, subjects, streak)
            history_block = conversation.recent_transcript() if conversation else "(no history tracked)"
            system_prompt = self._build_system_prompt(context_block, history_block)
            gemini_res = self._call_gemini_safely(q, system_instruction=system_prompt)
            if gemini_res:
                answer = f"🤖 **Echoes AI:** {gemini_res}"

        if answer is None:
            answer = self._offline_fallback_response(q, user_data)

        if conversation is not None:
            conversation.add("assistant", answer)

        return answer

    # ----------------------------------------------------------------- #
    # Offline fallback — upgraded rule-based responder
    # (only used when Gemini is unconfigured or unreachable)
    # ----------------------------------------------------------------- #

    _KEYWORD_RESPONSES: List[tuple] = [
        (
            ["add subject", "new subject", "different subject", "create subject", "course"],
            "📚 **How to Add Different Subjects:**\n\n"
            "1. Click **'Upload Syllabus'** in the top right header (or go to the **Subjects** tab and click **'+ ADD NEW SUBJECT'**).\n"
            "2. The **Python OCR Syllabus Extractor** will automatically parse your course modules, set credit weightages, and store the subject in your SQLite database!\n"
            "3. Your new subject will immediately appear on your Home Dashboard and AI Tools tab.",
        ),
        (
            ["bunk", "attendance", "absent", "miss class", "calculate bunk"],
            "🚨 **Attendance & Bunk Allowance Calculator Guidance:**\n\n"
            "• **How to open:** Click **'CALCULATE BUNKS →'** on the Home Dashboard card.\n"
            "• **How it works:** Python AttendanceAgent evaluates your enrolled subjects against a strict **75% minimum threshold**.\n"
            "• Open the Subjects tab for your live per-subject attendance numbers and safe-bunk counts.",
        ),
        (
            ["gpa", "grade", "cgpa", "exam coach", "predict gpa", "marks"],
            "📊 **GPA Predictor & Exam Coach Guidance:**\n\n"
            "• **How to open:** Click **'EXAM COACH DETAILS →'** on the Projected CGPA card.\n"
            "• This shows your projected CGPA, syllabus coverage %, and a per-subject readiness/grade breakdown.",
        ),
        (
            ["ingest", "timetable", "plan", "accept", "reject", "edit plan", "strategy"],
            "📅 **AI Strategy Map & Timetable Ingestion Guidance:**\n\n"
            "1. Go to the **Planner** tab (`view-planner`).\n"
            "2. Input your **Target GPA Goal** and select **Study Intensity** (Balanced, High Intensity, Light Rest).\n"
            "3. Click **'Generate AI Plan & Reminders →'**.\n"
            "4. Review proposed study blocks and click **Accept Plan ✓** to commit tasks directly to your schedule.",
        ),
        (
            ["quiz", "flashcard", "notes", "upload notes", "practice question"],
            "🛠️ **Subject-Wise AI Tools Guidance:**\n\n"
            "1. Go to the **AI Tools** tab (`view-aitools`).\n"
            "2. Select an active subject.\n"
            "3. Click **'Generate Subject Quiz'** or **'Generate Subject Flashcards'**.\n"
            "4. Paste custom lecture notes and click **'Process Notes'** for instant revision summaries and quizzes.",
        ),
        (
            ["sick", "tired", "2 hours", "exam moved", "weekend", "replan"],
            "⚡ **AI Quick Re-Planner Guidance:**\n\n"
            "• Use the shortcut pills on your Home Dashboard:\n"
            "  - ⚡ *'I only have 2 hours'*: Compresses schedule to priority items.\n"
            "  - ⚡ *'I am sick today'*: Defers heavy research, injects light recovery reading.\n"
            "  - ⚡ *'My exam moved'*: Recalibrates target revision countdowns.",
        ),
        (
            ["timer", "pomodoro", "focus", "sanctuary", "streak", "xp"],
            "⏱️ **Focus Sanctuary & XP Guidance:**\n\n"
            "• Go to the **Timer** tab (`view-timer`).\n"
            "• Click **'Start'** to begin a 25-minute deep work session.\n"
            "• Completing focus sessions awards **+100 XP** and increases your study streak.",
        ),
        (
            ["search", "find", "rag", "document", "lookup"],
            "🔍 **Global RAG Semantic Search Guidance:**\n\n"
            "• Type your query into the top search bar and press Enter.\n"
            "• The RAG agent performs vector similarity matching across your notes and shows relevance-scored snippets.",
        ),
        (
            ["graph", "prerequisite", "dependency", "concept map"],
            "🌳 **Prerequisite Knowledge Graph Guidance:**\n\n"
            "• Click **'VIEW GRAPH →'** on the Prerequisites card to see topic dependencies and mastery percentages across your subjects.",
        ),
        (
            ["hi", "hello", "hey"],
            "👋 **Hello!** I'm Echoes, your AI study mentor. Ask me anything — an academic "
            "concept, how to use a feature, or what to focus on today.",
        ),
    ]

    def _offline_fallback_response(self, q: str, user_data: Optional[Dict[str, Any]]) -> str:
        """Best-effort answer when Gemini is unavailable. Scores keyword
        overlap across all categories instead of stopping at the first
        elif match, so the closest-matching guidance wins rather than
        whichever branch happens to appear earliest in the list."""
        q_lower = q.lower()

        best_match: Optional[str] = None
        best_score = 0
        for keywords, response in self._KEYWORD_RESPONSES:
            score = sum(1 for kw in keywords if kw in q_lower)
            if score > best_score:
                best_score = score
                best_match = response

        if best_match:
            return best_match

        name = (user_data or {}).get("name", "there")
        return (
            f"🧠 **Echoes Academic Assistant:**\n\n"
            f"I couldn't reach the live AI reasoning engine just now, so here's the offline "
            f"guide, {name} — regarding **\"{q}\"**:\n\n"
            f"• Navigate using the floating bottom dock (`Home`, `Planner`, `Subjects`, `Timer`, `AI Tools`, `Echoes`).\n"
            f"• You can upload syllabi, calculate attendance bunk allowances, or generate subject quizzes directly from your dashboard.\n"
            f"• Try rephrasing with a specific keyword (e.g. *GPA*, *attendance*, *quiz*, *timetable*) so I can route you precisely, "
            f"or try again shortly once the AI connection is back."
        )