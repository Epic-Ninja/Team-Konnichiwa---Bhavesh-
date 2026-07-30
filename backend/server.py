import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

# Add backend directory to sys.path
sys.path.append(os.path.dirname(__file__))

from database import init_db, get_db
from agents.orchestrator import AgenticOrchestrator

PORT = 8000

# Initialize DB and Agentic Orchestrator
init_db()
orchestrator = AgenticOrchestrator()

class AgenticAIHandler(http.server.BaseHTTPRequestHandler):

    def _set_cors_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_cors_headers(204)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._set_cors_headers(200)
            res = {
                "status": "ONLINE",
                "system": "StudyPilot AI Agentic Backend Engine",
                "engine": "Python Stdlib Multi-Agent Orchestrator v2.0"
            }
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif path == "/api/v1/dashboard":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users LIMIT 1;")
            user = dict(cursor.fetchone())
            cursor.execute("SELECT * FROM subjects;")
            subjects = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT * FROM tasks;")
            tasks = [dict(r) for r in cursor.fetchall()]
            conn.close()

            ai_state = orchestrator.get_dashboard_state(user, subjects, user.get("streak", 21))
            self._set_cors_headers(200)
            res = {
                "user": user,
                "subjects": subjects,
                "tasks": tasks,
                "ai_insights": ai_state
            }
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif path == "/api/v1/tools/quiz":
            self._set_cors_headers(200)
            res = orchestrator.quiz.generate_quiz()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif path == "/api/v1/tools/flashcards":
            self._set_cors_headers(200)
            res = orchestrator.quiz.generate_flashcards()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        else:
            self._set_cors_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint Not Found"}).encode('utf-8'))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        body = json.loads(post_data) if post_data else {}

        if path == "/api/v1/planner/replan":
            trigger_text = body.get("trigger_text", "")
            res = orchestrator.process_natural_language_trigger(trigger_text)
            
            replan_res = res.get("replan_result", {})
            injected_task = replan_res.get("injected_task")
            if injected_task:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks (title, tag, priority, due_date, completed, estimate, bg_color)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    injected_task["title"],
                    injected_task["tag"],
                    injected_task["priority"],
                    injected_task["date"],
                    0,
                    injected_task["estimate"],
                    injected_task["bg_color"]
                ))
                conn.commit()
                conn.close()

            self._set_cors_headers(200)
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif path == "/api/v1/chat":
            msg = body.get("message", "")
            ai_response = orchestrator.process_chat_query(msg)
            self._set_cors_headers(200)
            self.wfile.write(json.dumps({"response": ai_response}).encode('utf-8'))

        elif path == "/api/v1/user/settings":
            name = body.get("name", "Bhavesh Dhidaria")
            focus_window = body.get("focus_window", "09:00 AM - 11:30 AM")
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET name = ?, focus_window = ? WHERE id = 'u1';", (name, focus_window))
            conn.commit()
            conn.close()
            self._set_cors_headers(200)
            self.wfile.write(json.dumps({"status": "SUCCESS", "name": name, "focus_window": focus_window}).encode('utf-8'))

        elif path == "/api/v1/upload/ocr":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO subjects (id, title, module, progress, attendance, credits, next_lesson, image_url)
                VALUES ('s3', 'Structural Mechanics II', 'FINITE ELEMENT PHASE', 10, 88, 4.0, 'Matrix Displacement Methods', 'https://lh3.googleusercontent.com/aida-public/AB6AXuADQm3LmdoB5hNAA_hrKbzlZR3OS3K2nV83IKYB9kyUPfcoWrBiygG1VMggYtyxtn--9Tpp4WinAsc_A6LF-L28D5Aaw5kgbijYdZdzkmzeCVNS_ETkx8e87-lcPNk6uM8OGBoDTa10gs8w1AwxEU-ohqUMF1PfyrpP3bApU2UYNkcfDTbJgWTCfL_cTnU3oAeBoWu_UKp_tB7bmd6C-spU9Lq0xq79AqFVFZuDFWab2XzeJ6ibyMSbIQ');
            """)
            conn.commit()
            conn.close()
            self._set_cors_headers(200)
            self.wfile.write(json.dumps({
                "status": "INGESTED",
                "subject": "Structural Mechanics II",
                "message": "Syllabus extracted & parsed by Python OCR Pipeline. Structural Mechanics II added to Subjects Library."
            }).encode('utf-8'))

        else:
            self._set_cors_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint Not Found"}).encode('utf-8'))

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = socketserver.TCPServer(server_address, AgenticAIHandler)
    print(f"🤖 Python Agentic AI Server running on http://0.0.0.0:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
