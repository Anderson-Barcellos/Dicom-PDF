import os
import time

from openai import OpenAI


class GPTClient:
    """Simple wrapper around the OpenAI ChatCompletion API."""

    def __init__(self, model: str = "gpt-3.5-turbo", max_retries: int = 3, rate_limit: float = 1.0) -> None:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
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
                response = self.client.chat.completions.create(model=self.model, messages=messages)
                self._last_call = time.time()
                return response.choices[0].message.content.strip()
            except Exception as exc:  # pragma: no cover - network failure
                if attempt == self.max_retries - 1:
                    print(f"OpenAI request failed: {exc}")
                    return line
                time.sleep(2 ** attempt)
        return line

    def generate_medical_report(self, ocr_findings: str, patient_name: str) -> str:
        """Generate a comprehensive medical report based on OCR findings from ultrasound images."""
        self._wait_rate_limit()
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um radiologista especializado em ultrassom. Com base nos achados "
                    "extraídos por OCR de imagens de ultrassom, gere um relatório médico "
                    "estruturado e completo. O relatório deve incluir:\n"
                    "1. IDENTIFICAÇÃO DO PACIENTE\n"
                    "2. DADOS DO EXAME\n"
                    "3. TÉCNICA UTILIZADA\n"
                    "4. ACHADOS PRINCIPAIS\n"
                    "5. MEDIDAS BIOMÉTRICAS (se disponíveis)\n"
                    "6. IMPRESSÃO DIAGNÓSTICA\n"
                    "7. RECOMENDAÇÕES\n\n"
                    "Use linguagem médica apropriada e mantenha um tom profissional."
                ),
            },
            {
                "role": "user",
                "content": f"Paciente: {patient_name}\n\nAchados de OCR:\n{ocr_findings}\n\nGere o relatório médico completo."
            },
        ]
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model, 
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.3
                )
                self._last_call = time.time()
                return response.choices[0].message.content.strip()
            except Exception as exc:  # pragma: no cover - network failure
                if attempt == self.max_retries - 1:
                    print(f"OpenAI request failed for medical report: {exc}")
                    return f"Relatório médico automático não disponível.\n\nAchados do OCR:\n{ocr_findings}"
                time.sleep(2 ** attempt)
        return f"Relatório médico automático não disponível.\n\nAchados do OCR:\n{ocr_findings}"
