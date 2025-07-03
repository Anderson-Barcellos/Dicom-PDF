import json
import os
import time
from pyorthanc import Orthanc
from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
from PDFMAKER.pdfmaker import MkPDF
from utils.ocr import extract_ultrasound_text
from utils.gpt_client import GPTClient

try:
    import win32print  # noqa: F401
    import win32api  # noqa: F401
    WINDOWS_PRINTING_AVAILABLE = True
except ImportError:  # pragma: no cover - not available on Linux
    WINDOWS_PRINTING_AVAILABLE = False


def sleep_with_while(seconds: int) -> None:
    start_time = time.time()
    while time.time() - start_time < seconds:
        remaining_time = seconds - (time.time() - start_time)
        print(f"Faltam {int(remaining_time)} segundos...")
        time.sleep(1)
    print("Tempo finalizado!")


# Same as main.Extract_Convert_Img but reused here

def extract_convert_img(file: str) -> str:
    unzipper = Unzipper(f"{file}", "./Dicoms")
    unzipper.unzipper()
    name = unzipper.name
    patient_name = name[15:]

    base_dir = os.path.join("Pacientes", patient_name)
    images_dir = os.path.join(base_dir, "IMAGENS")
    docs_dir = os.path.join(base_dir, "DOCUMENTOS")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    dicom2jpeg = DICOM2JPEG("./Dicoms", images_dir)
    dicom2jpeg.converter()

    gpt = GPTClient()

    txt_path = os.path.join(docs_dir, f"{patient_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        for img in os.listdir(images_dir):
            if img.lower().endswith((".jpeg", ".jpg", ".png", ".bmp")):
                img_path = os.path.join(images_dir, img)
                text, _ = extract_ultrasound_text(img_path)
                enhanced_lines = []
                for line in text.splitlines():
                    if line.strip():
                        enhanced_lines.append(gpt.enhance_text(line))
                    else:
                        enhanced_lines.append("")
                txt_file.write(f"# {img}\n" + "\n".join(enhanced_lines) + "\n")

    MkPDF(name, images_dir, docs_dir)
    dicom2jpeg.eliminate_dcm()

    return os.path.join(docs_dir, f"{patient_name}.pdf")


def verify_process(pdf_path: str) -> None:
    patient_name = os.path.splitext(os.path.basename(pdf_path))[0]
    docs_dir = os.path.dirname(pdf_path)
    txt_path = os.path.join(docs_dir, f"{patient_name}.txt")

    if os.path.exists(pdf_path) and os.path.exists(txt_path):
        print(f"✅ {patient_name}: PDF e laudo armazenados em {docs_dir}.")
    else:
        print(f"❌ {patient_name}: arquivos ausentes em {docs_dir}.")


orthanc = Orthanc("", "orthanc", "orthanc")
try:
    while True:
        with open('patients.json') as json_file:
            patients = json.load(json_file)

        latest_patients = orthanc.get_patients()
        if patients == latest_patients:
            print("Nenhum novo paciente encontrado, Anders.... Procurando")
            sleep_with_while(20)
        else:
            new_patients = [p for p in latest_patients if p not in patients]
            for patient in new_patients:
                response = orthanc.get_patients_id_archive(str(patient))
                with open(f"ZIPS/{patient}.zip", "wb") as f:
                    f.write(response)
                pdf_path = extract_convert_img(f"{patient}.zip")
                verify_process(pdf_path)

            patients = latest_patients
            with open('patients.json', 'w') as json_file:
                json.dump(patients, json_file)
            sleep_with_while(15)
except Exception as e:
    print(e)
