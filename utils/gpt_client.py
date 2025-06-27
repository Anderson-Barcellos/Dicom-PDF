import os
import time

import openai


class GPTClient:
    """Simple wrapper around the OpenAI ChatCompletion API."""

    def __init__(self, model: str = "gpt-3.5-turbo", max_retries: int = 3, rate_limit: float = 1.0) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.max_retries = max_retries
        self.rate_limit = rate_limit
        self._last_call = 0.0

    def _wait_rate_limit(self) -> None:
        """Ensure we respect a minimal interval between API calls."""
        elapsed = time.time() - self._last_call
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def enhance_text(self, line: str) -> str:
        """Send a single OCR line to the API and return the enhanced text."""
        self._wait_rate_limit()
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente que corrige erros de OCR em linhas de "
                    "relatórios de ultrassom. Retorne somente a linha corrigida."
                ),
            },
            {"role": "user", "content": line},
        ]
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(model=self.model, messages=messages)
                self._last_call = time.time()
                return response.choices[0].message["content"].strip()
            except Exception as exc:  # pragma: no cover - network failure
                if attempt == self.max_retries - 1:
                    print(f"OpenAI request failed: {exc}")
                    return line
                time.sleep(2 ** attempt)
        return line
