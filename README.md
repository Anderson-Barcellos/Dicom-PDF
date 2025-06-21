# Ultrasound DICOM Image to PDF  

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

### Printing Support (Windows Only)

The automatic printing feature relies on the `pywin32` library. Printing from
`main.py` is therefore available only on Windows systems. Users on other
platforms should generate the PDF and print it manually.

### Development Environment

This repository includes an optional Conda configuration. To create the
environment and install Python and Node.js dependencies, run:

```bash
conda env create -f environment.yml
conda activate dicom-pdf
npm install --prefix webapp
```

You can then build the frontend and execute the main script or run your tests.

### Docker Setup

To build a Docker image that includes the compiled interface and all Python
dependencies, run from the repository root:

```bash
docker build -t dicom-pdf .
```

Execute the container with:

```bash
docker run --rm -p 4173:4173 dicom-pdf
```

Once started, the project runs `main.py`. To preview the web interface without
containerization, run:

```bash
npm run preview --prefix webapp
```

The frontend will be available at [http://localhost:4173](http://localhost:4173).

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

1. Implement machine learning for automated measurement verification
2. Add support for 3D/4D ultrasound data
3. Develop a user-friendly interface for easier operation
4. Integrate with hospital information systems for seamless data flow
5. Implement multi-language support for international use

## Conclusion

This project provides a comprehensive solution for processing fetal ultrasound data, combining image analysis with advanced biometrical assessments. It offers healthcare professionals a powerful tool for monitoring fetal growth and development, enhancing the quality of prenatal care.

![image](https://github.com/user-attachments/assets/95487a15-4532-4c99-9655-c86285aa45bc)
