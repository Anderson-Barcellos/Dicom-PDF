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
    images_dir = os.path.join(base_dir, "Images")
    reports_dir = os.path.join(base_dir, "Report")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    dicom2jpeg = DICOM2JPEG("./Dicoms", images_dir)
    dicom2jpeg.converter()

    gpt = GPTClient()

    # Extract and enhance OCR text from all images
    all_ocr_findings = []
    report_path = os.path.join(reports_dir, f"{patient_name}_report.txt")
    with open(report_path, "w", encoding="utf-8") as report_file:
        for img in os.listdir(images_dir):
            if img.lower().endswith((".jpeg", ".jpg", ".png", ".bmp")):
                img_path = os.path.join(images_dir, img)
                text, _ = extract_ultrasound_text(img_path) # OCR

                for line in text:
                    if line.strip():
                        all_ocr_findings.append(line)
                    else:
                        all_ocr_findings.append("")
            report_file.write(f"# {img}\n" + "\n".join(all_ocr_findings) + "\n")

    MkPDF(name)
    dicom2jpeg.eliminate_dcm()
    
    # Return the path to the generated PDF
    return os.path.join(reports_dir, f"{patient_name}.pdf")

def ocr_images(name: str) -> None:
    """
    Process OCR for images in a patient's folder.
    This function is currently not implemented but preserved for future use.
    """
    pass


def verify_process(pdf_path: str) -> None:
    patient_name = os.path.splitext(os.path.basename(pdf_path))[0]
    reports_dir = os.path.dirname(pdf_path)
    ocr_txt_path = os.path.join(reports_dir, f"{patient_name}_report.txt")
    img_report_txt_path = os.path.join(reports_dir, f"{patient_name}_img_report.txt")

    if os.path.exists(pdf_path) and os.path.exists(ocr_txt_path):
        if os.path.exists(img_report_txt_path):
            print(f"✅ {patient_name}: PDF, OCR e relatório médico armazenados em {reports_dir}.")
        else:
            print(f"⚠️ {patient_name}: PDF e OCR armazenados, mas relatório médico ausente em {reports_dir}.")
    else:
        print(f"❌ {patient_name}: arquivos ausentes em {reports_dir}.")

def main():
    orthanc = Orthanc("https://ultrassom.ai", "anders", "andi110386")
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
                    extract_convert_img(f"{patient}.zip")
                    verify_process(f"Pacientes/{patient}/Report/{patient}.pdf")

                patients = latest_patients
                with open('patients.json', 'w') as json_file:
                    json.dump(patients, json_file)
                sleep_with_while(15)
    except Exception as e:
        print(e)
