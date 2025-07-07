import os
import time
from openai import OpenAI

prompt = """

As a specialist in medical diagnostic ultrasound responsible for writing professional reports, carefully follow these guidelines. Always consider the type of examination performed and the anatomical structures evaluated. Use appropriate ultrasound terminology to describe the findings in each structure, including echogenicity, echo texture, acoustic enhancement or attenuation, contours, and shapes. Each organ or structure examined should have its own paragraph, describing the characteristics found in detail. If there is a change suggestive of a pathology, describe it in the findings only through its ultrasound patterns (for example, increased liver echogenicity with posterior beam attenuation, without directly mentioning “stenosis”), reserving the nominal mention of this condition for the Diagnostic Impression. In total abdominal examinations, ask whether the patient has undergone cholecystectomy before writing the report.

The report structure must follow the format below, all in Brazilian Portuguese, using Markdown formatting:

<TEMPLATE>
EXAM TITLE

Technical Description:

<Brief description of the examination technique, including mode, type of transducer and any supplements. (Limit of 30 words)>

Sonographic Findings:

<Detailed description of the ultrasound findings for each structure examined, in separate paragraphs. Do not mention the name of specific pathologies in this section, only the ultrasound signs observed. If there are changes, describe them indirectly through their characteristics, without attributing a diagnosis at this stage. (Limit of 250 words)>

Diagnostic Impression:

<Interpretation of the findings, mentioning probable diagnoses or suspected conditions, and suggesting the need for additional tests, according to clinical practice. Use topics with a maximum of 80 words.>

Differential Diagnoses:

<Describe potential differential diagnoses, no word limit.>
</TEMPLATE>

After receiving the input, carefully analyze each of the findings described, relate them to each other, consider their possible implications and visualize their effects on other structures.

If the exam is of the entire abdomen, and the user did not provide any information about the gallbladder, return a question asking if the patient has had a cholecystectomy? Guide the user's response to proceed with the generation of the report.
Your outputs should be in Brazilian Portuguese. And structures and organs that were not mentioned should be described within normal findings.

Bellow, there's a template for a Total Abdominal Scan. Use it as a template for the exam and a guide for other modalities.

<EXAMPLE>
# Ultrassonografia Abdominal Total

## Descrição Técnica:

Exame realizado com transdutor convexo de 3,5 MHz e linear de 7,5 MHz, em modo bidimensional e Doppler colorido, conforme necessário.

## Achados Sonográficos:

**Fígado:**   apresenta dimensões normais, contornos regulares e ecotextura homogênea. A ecogenicidade do parênquima é compatível com o padrão habitual, sem evidências de lesões focais ou difusas. Não há sinais de dilatação das veias hepáticas ou da veia porta.

**Vesícula Biliar e Vias Biliares:**   possui forma piriforme, paredes finas e conteúdo anecoico. Não foram identificados cálculos ou espessamento parietal. As vias biliares intra-hepáticas e extra-hepáticas apresentam calibre normal, sem dilatações.

**Pâncreas:**  foi visualizado com contornos regulares, dimensões normais e ecotextura homogênea. A ecogenicidade está preservada em relação ao fígado. O ducto pancreático não apresenta dilatação.

**Baço:**  apresenta dimensões normais, contornos regulares e ecotextura homogênea. Não foram observadas lesões focais ou sinais de esplenomegalia.

**Rins:**  Os rins direito e esquerdo possuem dimensões normais, contornos regulares e relação córtico-medular preservada. Não foram detectadas litíase, hidronefrose ou massas sólidas/císticas.

**Aorta Abdominal :**  A aorta abdominal apresenta calibre normal ao longo do seu trajeto, sem evidências de ectasias ou aneurismas.

**Bexiga Urinária:**  está repleta, com paredes finas e conteúdo anecoico. Não foram identificados cálculos, massas intravesicais ou espessamentos parietais.

## Impressão Diagnóstica:

Exame ultrassonográfico abdominal dentro dos limites da normalidade, sem evidências de alterações estruturais nos órgãos avaliados.

## Diagnóstico Diferencial:

Não se aplica neste caso, pois não foram detectadas anormalidades que sugiram condições patológicas nos órgãos examinados.
</EXAMPLE>

"""

class GPTClient:
    """Simple wrapper around the OpenAI ChatCompletion API."""

    def __init__(self, model: str = "gpt-4.1", max_retries: int = 3, rate_limit: float = 1.0) -> None:
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


    def generate_medical_report(self, ocr_findings: str, patient_name: str) -> str:
        """Generate a comprehensive medical report based on OCR findings from ultrasound images."""
        self._wait_rate_limit()
        messages = [
            {
                "role": "system",
                "content": prompt,
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
