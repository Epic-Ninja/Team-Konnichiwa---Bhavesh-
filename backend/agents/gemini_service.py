import os
import json
import ssl
import time
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

class GeminiAPIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.ssl_context = ssl._create_unverified_context()

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        if not self.is_configured():
            return None

        # Prioritize fast, high-rate-limit models
        models = ["gemini-flash-lite-latest", "gemini-2.0-flash", "gemini-flash-latest"]
        key = self.api_key

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if system_instruction:
            payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

        data = json.dumps(payload).encode("utf-8")

        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=12) as response:
                    if response.status == 200:
                        resp_json = json.loads(response.read().decode("utf-8"))
                        candidates = resp_json.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "")
                                if text and len(text.strip()) > 0:
                                    return text.strip()
            except urllib.error.HTTPError as e:
                print(f"Gemini API ({model}) HTTP {e.code}: {e.reason}")
                if e.code == 429:
                    time.sleep(1)
            except Exception as e:
                print(f"Gemini API Error ({model}): {e}")

        return None
