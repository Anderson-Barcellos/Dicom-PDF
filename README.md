
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

### 5. Main Execution (`main.py`)

- Orchestrates the entire process:
  - Unzips DICOM files
  - Converts DICOM to JPEG
  - Extracts biometrical data
  - Generates growth charts
  - Creates the final PDF report

## Workflow

1. **DICOM Extraction**: Unzip and organize DICOM files
2. **Image Conversion**: Convert DICOM images to JPEG format
3. **Data Extraction**: Extract biometrical data from SR DICOM files
4. **Chart Generation**: Create growth charts for each biometric measurement
5. **Report Compilation**: Generate a PDF report with images, measurements, and charts
6. **PDF Merging**: Combine multiple PDFs if necessary

### Patient Folder Organization

All converted data resides under the `Pacientes` directory. For each new patient
a folder named after the patient is created with the following structure:

- `IMAGENS` – JPEG images converted from DICOM files
- `DOCUMENTOS` – generated PDFs and OCR text files

The original DICOM files continue to be downloaded to the shared `Dicoms` folder.

## Key Features

1. **Comprehensive Data Processing**: Handles both image and structured report DICOM files
2. **Enhanced Visualization**: Improves ultrasound image quality for better analysis
3. **Biometrical Analysis**: Extracts and visualizes key fetal measurements
4. **Growth Assessment**: Plots fetal measurements against standard growth curves
5. **Customized Reporting**: Generates professional PDF reports with images and charts

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

## Future Improvements

1. Implement an individual patient folder inside the "main" Patients folder. Each will be named with the patients name and surname, and will store a folder with the PDF gridlayout images on "Images", and the extracted text from OCRing the US images in a .txt in "Report".
2. Improve OCR results, and apply a LLM do generate a complete report based on findings.
## Conclusion

This project provides a comprehensive solution for processing fetal ultrasound data, combining image analysis with advanced biometrical assessments. It offers healthcare professionals a powerful tool for monitoring fetal growth and development, enhancing the quality of prenatal care.

![image](https://github.com/user-attachments/assets/95487a15-4532-4c99-9655-c86285aa45bc)
