# DICOM to PDF and AI-Powered Reporting System

This project is an automated pipeline designed to process medical DICOM files from an Orthanc server. It converts DICOM images into JPEG format, compiles them into a structured PDF report, extracts data from DICOM Structured Reports (SR), and leverages AI to generate insightful medical reports from image data.

## 🌟 Key Features

- **Automated Orthanc Integration**: Continuously monitors an Orthanc server for new patient studies, automatically downloading and processing the data.
- **DICOM to JPEG Conversion**: Converts DICOM files to high-quality JPEGs, with options for image enhancement to improve visual clarity.
- **Structured PDF Generation**: Arranges the generated JPEG images into a clean, grid-based (4x2) PDF document suitable for clinical review.
- **DICOM SR Analysis**: Extracts biometrical data from DICOM Structured Report (SR) files, generates growth charts, and compiles them into a separate, detailed PDF report.
- **AI-Enhanced Reporting**:
    - **OCR**: Uses Tesseract to extract textual information from ultrasound images.
    - **Pathology & Doppler Analysis**: Intelligently parses OCR text to identify potential pathologies and extract quantitative Doppler ultrasound parameters.
    - **GPT-Powered Summaries**: Utilizes a GPT model to generate professional, formatted medical reports based on the extracted findings.
- **Configuration Management**: A centralized configuration system (`config.py`) allows for easy setup of Orthanc credentials, OpenAI API keys, and directory paths using environment variables.
- **Modular Architecture**: The codebase is organized into distinct modules for DICOM handling (`DicomManager`), PDF creation (`PDFMAKER`), Structured Reporting (`SR`), and utilities (`utils`), promoting maintainability and scalability.

##  workflow

1.  **Monitor & Download**: The system connects to a configured Orthanc server and polls for new patient studies.
2.  **Unzip & Organize**: When a new study is found, its corresponding ZIP archive is downloaded and extracted into a structured directory.
3.  **Image Conversion**: All DICOM (`.dcm`) images within the study are converted into high-quality JPEG images.
4.  **PDF Compilation**: The JPEG images are compiled into a primary PDF report with a 4x2 grid layout.
5.  **SR Data Processing**: If DICOM SR files are present, biometrical data is extracted, plotted onto growth charts, and a secondary PDF report is generated.
6.  **AI Analysis (Optional)**:
    - Text is extracted from images via OCR.
    - The extracted text is analyzed to identify medical terms, measurements, and pathologies.
    - The findings are sent to an AI model to generate a structured, human-readable medical report.

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.10+
- Conda package manager
- Tesseract OCR engine installed on your system.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Dicom-PDF.git
    cd Dicom-PDF
    ```

2.  **Create and activate the Conda environment:**
    The `environment.yml` file contains all the necessary dependencies.
    ```bash
    conda env create -f environment.yml
    conda activate dicom-pdf
    ```
    Alternatively, for a pip-based setup, you can use `requirements.txt` (though Conda is recommended for managing complex dependencies like `opencv`):
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    The system uses environment variables for sensitive data. You can set them in your shell or use a `.env` file.
    ```bash
    export ORTHANC_HOST="https://your-orthanc-server.com"
    export ORTHANC_USERNAME="your-username"
    export ORTHANC_PASSWORD="your-password"
    export OPENAI_API_KEY="your-openai-api-key"
    ```

## 🚀 Usage

To start the main monitoring service, run the `main.py` script. The application will connect to Orthanc and begin watching for new patients.

```bash
python main.py
```

The project also includes a comprehensive testing framework for processing individual patients without running the full monitoring loop. See the `IMPLEMENTATION_SUMMARY.md` document for more details on this functionality.

---
### Image Reporte Example:

![image](https://github.com/user-attachments/assets/95487a15-4532-4c99-9655-c86285aa45bc)
