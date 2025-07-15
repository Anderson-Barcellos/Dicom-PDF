#!/usr/bin/env python3
"""
🔍 GPT-4o OCR Module
Este módulo utiliza o GPT-4o da OpenAI para extrair texto e medidas de imagens de ultrassom.
Identifica achados ultrassonográficos, medidas e observações relevantes de cada imagem.
"""

import base64
from pathlib import Path
from openai import OpenAI
import os

LAUDO_PROMPT = """
As a specialist in medical diagnostic ultrasound responsible for writing professional reports, carefully follow these guidelines. Always consider the type of examination performed and the anatomical structures evaluated. Use appropriate ultrasound terminology to describe the findings in each structure, including echogenicity, echo texture, acoustic enhancement or attenuation, contours, and shapes. Each organ or structure examined should have its own paragraph, describing the characteristics found in detail. If there is a change suggestive of a pathology, describe it in the findings only through its ultrasound patterns (for example, increased liver echogenicity with posterior beam attenuation, without directly mentioning "stenosis"), reserving the nominal mention of this condition for the Diagnostic Impression.

Bellow, there's a template of how user's input will be presented to you:

<EXAMPLE>
Paciente: Clarice Padilha
Data do exame: 04-06-2025
Exame: Ultrassonografia de mama
Médico responsável: M.D. Anderson Brum Anderson

Técnica
• Aparelho: HM70 EVO
• Transdutor: linear 5–12 MHz (LN5-12)
• Frequência: 4,7 MHz
• Profundidade: 5,0–6,0 cm
• Ganho: 33–42
• Índice mecânico (MQ): Q/2
• Persistência (P): 100%

Achados
Foi identificada imagem nodular hipoecoica em topografia mamária, com as seguintes medidas obtidas em diferentes planos:
– 0,57 × 0,44 cm (relação de aspecto 1,30)
– 0,48 cm (diâmetro único)
– 0,82 cm (diâmetro único)

</EXAMPLE>

From this data, you can obtain all the information you need to write a professional report.
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

FINAL INSTRUCTIONS:
After receiving the input, carefully analyze each of the findings described, relate them to each other, consider their possible implications and visualize their effects on other structures.
For abdominal exams specifically:
if the user !!!did not!! provide any information about the !!!gallbladder!!, return a question asking if the had performe cholecystectomy? Howerver, if gallbladder is mentioned, do not ask this question.  Your outputs should be in Brazilian Portuguese. And structures and organs that were not mentioned should be described within normal findings.


"""


class GPTVision:
    """
    🩺 GPTVision
    This class performs Optical Character Recognition (OCR) on medical images using OpenAI's GPT-4o Vision model. It is designed to extract textual findings, measurements, and relevant observations from ultrasound images, supporting automated medical reporting workflows. The class handles image encoding, resizing, and communication with the OpenAI API.

    ### 🖥️ Parameters
        - `api_key` (`str`): The OpenAI API key used for authentication and access to GPT-4o Vision.

    ### 🔄 Returns
        - `GPTVision`: An instance of the GPTVision class, ready to process images.

    ### ⚠️ Raises
        - `openai.OpenAIError`: If there is an error communicating with the OpenAI API during OCR operations.
        - `FileNotFoundError`: If the specified image file does not exist.
        - `OSError`: If there is an error opening or processing the image file.

    ### 💡 Example

    >>> ocr = GPTVision(api_key="sk-...")
    >>> text = ocr.extract_text_from_image("Patients/JohnDoe/Images/image1.jpeg")
    'Fígado: dimensões normais, contornos regulares...'
    """

    def __init__(self, api_key: str):
        """
        🗝️ __init__
        Initializes the GPTVision class by setting up the OpenAI client for subsequent OCR operations using the provided API key. This method prepares the instance for image processing and communication with the OpenAI API.

        ### 🖥️ Parameters
            - `api_key` (`str`): The OpenAI API key required for authenticating requests to the OpenAI service.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "o4-mini"
        self.text = ""

    def _encode_image(self, image_path: str) -> str:
        """
        ### 🔐 _encode_image
        Internal method to encode image in base64 format for API transmission.

        ### 🖥️ Parameters
            - `image_path` (`str`): Path to the image file to be encoded.

        ### 🔄 Returns
            - `str`: Base64 encoded string representation of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_text_from_image(self, image_path: str | list[str]) -> str:
        """
        ### 📝 extract_text_from_image
        Extracts text and measurements from a single ultrasound image using GPT-4o Vision.

        ### 🖥️ Parameters
            - `image_path` (`str`): Path to the image file to be processed.

        ### 🔄 Returns
            - `str`: Extracted text from the image, or empty string if processing fails.
        """
        try:
            content = []
            lenght = 0
            # Encode image based on image_path type
            if isinstance(image_path, str):
                base64_image = self._encode_image(image_path)
            elif isinstance(image_path, list):
                base64_image = [self._encode_image(image) for image in image_path]
                lenght = len(base64_image)

            # Add image to content
            if isinstance(base64_image, str):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            if isinstance(base64_image, list):
                for image in base64_image:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}"
                        }
                    })

            # API call
            def _api_call(content: list[dict] | dict) -> str:
                try:
                    # Prepare message for o4-mini
                    response = self.client.chat.completions.create(
                        model="o4-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": """
                                    Voce recebera um texto que é um OCR de achados de ultrassom.

            REGRAS IMPORTANTES:
            1. Analise as  imagens dentro do contexto médico
            2. NÃO mencione que está analisando imagens específicas
            3. Organize o texto de forma fluida e profissional, sem repetir informações

            Abaixo segue um template para que você possa usar como referência para o texto.:

            <EXAMPLE>
    Paciente: Clarice Padilha
    Data do exame: 04-06-2025
    Exame: Ultrassonografia de mama
    Médico responsável: M.D. Anderson Brum Anderson

    Técnica
    • Aparelho: HM70 EVO
    • Transdutor: linear 5–12 MHz (LN5-12)
    • Frequência: 4,7 MHz
    • Profundidade: 5,0–6,0 cm
    • Ganho: 33–42
    • Índice mecânico (MQ): Q/2
    • Persistência (P): 100%

    Achados
    Foi identificada imagem nodular hipoecoica em topografia mamária, com as seguintes medidas obtidas em diferentes planos:
    – 0,57 × 0,44 cm (relação de aspecto 1,30)
    – 0,48 cm (diâmetro único)
    – 0,82 cm (diâmetro único)

    =
            </EXAMPLE>

            Lembre-se: texto limpo, sem referências a arquivos, sem repetições, e sem informacoes diagnosticas.
            """
                            },
                            {
                                "role": "user",
                                "content": content
                            }
                        ],
                        reasoning_effort="high"
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    raise e

            # Call the API
            if lenght <5:
                return _api_call(content) # If there are less than 5 images, call the API with the content
            else:
                api1 = _api_call(content[:4]) # If there are more than 5 images, call the API with the first 4 images and concatenate the results
                api2 = _api_call(content[4:]) # Call the API with the remaining images and concatenate the results
                return api1 + api2 # Return the concatenated text
        except Exception as e:
            print(f"Error: {e}")
            return ""

    def process_patient_images(self, images_folder: str) -> None:
        """
        ### 🔄 process_patient_images
        Processes all images in a patient folder and accumulates the extracted text.

        ### 🖥️ Parameters
            - `images_folder` (`str`): Path to the folder containing patient images.
        """
        try:
            images_path = Path(images_folder)

            # Listar todas as imagens JPEG
            image_files = sorted(
                list(images_path.glob("*.jpeg")) +
                list(images_path.glob("*.jpg"))
            )

            print(f"Processing {len(image_files)} images...")
            bacth_size = 4
            for i in range(0, len(image_files), bacth_size):
                batch = image_files[i:i+bacth_size]
                print(f"Processing image {i}/{len(image_files)}/{bacth_size}:")
                text = self.extract_text_from_image(batch)
                if text:  # Check if text is not empty
                    self.text += text + "\n"

        except Exception as e:
            print(f"Error: {e}")



class GPTReport:
    """
    🩺 GPTReport
    This class generates medical reports using GPT-4o. It is designed to process OCR findings and produce structured medical reports. The class handles communication with the OpenAI API and formatting of the report.

    ### 🖥️ Parameters
        - `api_key` (`str`): The OpenAI API key used for authentication and access to GPT-4o.
    """

    def __init__(self, api_key: str):
        """
        ### 🗝️ __init__
        Initializes the GPTReport class for generating medical reports.

        ### 🖥️ Parameters
            - `api_key` (`str`): The OpenAI API key required for authenticating requests to the OpenAI service.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "o3"  # ou "o3" quando disponível
        self.generated_report = ""

    def generate_report(self, ocr_text: str) -> str:
        """
        ### 📋 generate_report
        Generates a medical report based on OCR findings.

        ### 🖥️ Parameters
            - `ocr_text` (`str`): The text extracted from OCR processing.

        ### 🔄 Returns
            - `str`: Generated medical report in markdown format.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": LAUDO_PROMPT
                    },
                    {
                        "role": "user",
                        "content": ocr_text
                    }
                ],
                reasoning_effort="medium"
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""


def process_patient_with_ai(patient_name: str, api_key: str) -> None:
    """
    ### 🏥 process_patient_with_ai
    Processes a complete patient: OCR + Report Generation.

    ### 🖥️ Parameters
        - `patient_folder` (`str`): Path to the patient folder.
        - `api_key` (`str`): OpenAI API key.

    ### 🔄 Returns
        - `None`: The function does not return a value.
    """
    patient_path = os.path.join(os.getcwd(), "Users", "Anders", "Patients", patient_name)
    images_folder = os.path.join(patient_path, "Images")
    report_folder = os.path.join(patient_path, "Report")
    os.makedirs(report_folder, exist_ok=True)
    report_file = os.path.join(report_folder, f"{patient_name}.md")

    print(f"\n=== Processing patient: {patient_name} ===")

    # Etapa 1: OCR com GPT-4o
    print("\n1. OCRing images...")
    ocr = GPTVision(api_key)
    ocr.process_patient_images(str(images_folder))
    # Etapa 2: Gerar laudo com o3
    report = GPTReport(api_key)
    print("\n2. Generating medical report...")
    report_text = report.generate_report(ocr.text)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n✅ Process complete! Report saved in: {report_file}")


if __name__ == "__main__":
    # Test the module
    print("GPT OCR module loaded successfully!")
    print("Use process_patient_with_ai() to process a patient")
