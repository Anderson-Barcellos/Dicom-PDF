
## Project Overview

This project processes ultrasound DICOM files, extracts and converts them  into images!
The process finishes with a 4x2 (8 images) grid layout pdf file page. ALso, in Obstetrical Exams you can create growth charts.
It combines image processing with advanced biometrical analysis to provide a complete view of fetal development.

## Key Components

### 1. DICOM Processing (`DicomManager/DICOM.py`)

- **Class: DICOM2JPEG**
  - Converts DICOM files to JPEG format
  - Enhances image quality (contrast, brightness, sharpness)
  - Identifies and separates Structured Report (SR) DICOM files

### 2. Biometrical Data Extraction (`SR/SR2DATA.py`)

- **Function: ExtractSR**
  - Extracts biometrical measurements from DICOM SR files
  - Processes key measurements: Head Circumference, Biparietal Diameter, Abdominal Circumference, Femur Length, Estimated Fetal Weight

- **Function: pdf_report**
  - Generates a PDF report containing measurement data and growth charts
  - Organizes plots in a two-per-page layout

### 3. Growth Chart Generation (`SR/SR2PLOT.py`)

- **Function: create_other_plots**
  - Creates individual growth charts for each biometric measurement
  - Plots patient data against standard percentile curves (10th, 50th, 90th)
  - Uses a dark theme for better visibility

### 4. PDF Generation (`PDFMAKER/pdfmaker.py`)

- **Class: MkPDF**
  - Creates a grid layout of ultrasound images
  - Incorporates biometrical data and growth charts into the report

### 5. AI-Enhanced OCR and Reporting (`utils/gpt_client.py`, `utils/ocr.py`)

- **Enhanced OCR Processing**:
  - Uses advanced image preprocessing and Tesseract OCR
  - AI-powered text correction with GPT to fix OCR errors
  - Improved accuracy for medical terminology and measurements

- **Intelligent Medical Report Generation**:
  - Automatically generates comprehensive medical reports using LLM
  - Structured format with patient identification, findings, measurements, and recommendations
  - Professional medical language and terminology

### 6. Main Execution (`main.py`)

- Orchestrates the entire process:
  - Unzips DICOM files
  - Converts DICOM to JPEG
  - Performs enhanced OCR with AI correction
  - Generates comprehensive medical reports
  - Extracts biometrical data
  - Generates growth charts
  - Creates the final PDF report

## Workflow

1. **DICOM Extraction**: Unzip and organize DICOM files
2. **Image Conversion**: Convert DICOM images to JPEG format
3. **Enhanced OCR Processing**: Extract text from ultrasound images with AI-enhanced accuracy
4. **Data Extraction**: Extract biometrical data from SR DICOM files
5. **Comprehensive Report Generation**: Use LLM to generate complete medical reports based on OCR findings
6. **Chart Generation**: Create growth charts for each biometric measurement
7. **Report Compilation**: Generate a PDF report with images, measurements, and charts
8. **PDF Merging**: Combine multiple PDFs if necessary

### Patient Folder Organization

All converted data resides under the `Pacientes` directory. For each new patient
a folder named after the patient is created with the following structure:

- `Images` – JPEG images converted from DICOM files arranged in PDF grid layout
- `Report` – OCR extracted text files and AI-generated comprehensive medical reports

The original DICOM files continue to be downloaded to the shared `Dicoms` folder.

## Key Features

1. **Comprehensive Data Processing**: Handles both image and structured report DICOM files
2. **Enhanced Visualization**: Improves ultrasound image quality for better analysis
3. **AI-Enhanced OCR**: Uses GPT to improve OCR accuracy and correct extraction errors
4. **Intelligent Medical Reporting**: Automatically generates comprehensive medical reports using LLM
5. **Biometrical Analysis**: Extracts and visualizes key fetal measurements
6. **Growth Assessment**: Plots fetal measurements against standard growth curves
7. **Customized Reporting**: Generates professional PDF reports with images and charts
8. **Structured File Organization**: Individual patient folders with organized Images and Report subfolders
9. **Robust Testing & Validation Framework**: Includes utilities for validating each processing step, logging, and automated test execution (see below)
10. **Automated & Interactive Testing**: Test framework allows for both automated and interactive patient testing, including CI/CD integration

## Testing & Validation Framework

A comprehensive test framework is included to ensure the reliability and reproducibility of the DICOM PDF processing pipeline.

### Main Components

- **test_single_patient.py**: Run the full pipeline for a selected patient, interactively or by ID.
- **test_utils.py**: Utility functions for validation, logging, and file integrity checks.
- **run_automated_test.py**: Script for automated testing (CI/CD).
- **validate_test_framework.py**: Validates the test framework and environment.
- **TEST_README.md**: Full documentation for the test framework.

### Features

- **Interactive Patient Selection**: List and select patients from Orthanc for testing.
- **Step-by-Step Validation**: Each processing step is validated with detailed logs.
- **Automated Test Reports**: Generates JSON reports for each test run.
- **File Structure Validation**: Ensures all expected files and folders are created.
- **Quality Checks**: Validates image quality, OCR accuracy, and report structure.
- **Comprehensive Logging**: Logs to both file and console for easy debugging.

### Expected Folder Structure

test_results/
├── Pacientes

## Technical Details

### Libraries Used

- pydicom: For reading DICOM files
- Pillow (PIL): For image processing
- matplotlib: For creating growth charts
- reportlab: For generating PDF reports
- numpy: For numerical operations
- scipy: For interpolation in growth charts

### Development Environment

This repository includes an optional Conda configuration. To create the
environment, run:

```bash
conda env create -f environment.yml
conda activate dicom-pdf
```

You can then execute the main script or run your tests.

### OCR Engine Setup

This project relies on the `tesseract-ocr` engine for its OCR capabilities.
Ensure the engine is available in your system so that the functions in
`utils/ocr.py` work properly. On most Linux distributions you can install it
using `apt`:

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

If `tesseract` is not in your `PATH`, configure `pytesseract.pytesseract.tesseract_cmd`
accordingly.

### Docker Setup

To build a Docker image with all Python dependencies, run from the repository root:

```bash
docker build -t dicom-pdf .
```

Execute the container with:

```bash
docker run --rm dicom-pdf
```

### Data Processing

- Extracts and processes various fetal measurements:
  - Head Circumference (HC)
  - Biparietal Diameter (BPD)
  - Abdominal Circumference (AC)
  - Femur Length (FL)
  - Estimated Fetal Weight (EFW)

### Visualization

- Growth charts use a dark theme for better contrast
- Each chart includes 10th, 50th, and 90th percentile lines
- Patient's specific measurement is highlighted on each chart

### PDF Generation

- Combines ultrasound images in a grid layout
- Includes a summary of all biometrical measurements
- Presents growth charts for each measurement
- Optimized for A4 paper size

## Recent Improvements

### ✅ Implemented Features (v2.0)

1. **Individual Patient Folder Structure**: Each patient now has a dedicated folder named with their patient name and surname inside the "Pacientes" directory, with organized subfolders:
   - `Images` – Contains PDF grid layout images converted from DICOM files
   - `Report` – Contains extracted OCR text and AI-generated comprehensive medical reports

2. **Enhanced OCR Processing**: Improved OCR accuracy using GPT-based text enhancement to correct extraction errors and improve readability.

3. **AI-Powered Medical Report Generation**: Integrated LLM (GPT) to automatically generate comprehensive, structured medical reports based on OCR findings, including:
   - Patient identification
   - Exam data and technique
   - Main findings and biometric measurements
   - Diagnostic impressions
   - Clinical recommendations

### Future Enhancements

1. Integration with PACS systems for direct DICOM retrieval
2. Advanced image preprocessing for improved OCR accuracy
3. Multi-language support for international use
4. Web-based interface for easier access and management
5. Real-time collaboration features for healthcare teams

## Conclusion

This project provides a comprehensive solution for processing fetal ultrasound data, combining image analysis with advanced biometrical assessments. It offers healthcare professionals a powerful tool for monitoring fetal growth and development, enhancing the quality of prenatal care.

![image](https://github.com/user-attachments/assets/95487a15-4532-4c99-9655-c86285aa45bc)
