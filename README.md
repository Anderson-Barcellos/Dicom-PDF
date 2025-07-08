
## 🏥 Overview

An automated medical imaging processing system that connects to Orthanc PACS servers, processes DICOM files, and generates comprehensive PDF reports with automatic Windows printing capabilities.

## ✅ Implemented Features

### 🔄 Core Workflow (Fully Functional)
- **Continuous Monitoring Loop**: Automatically monitors Orthanc PACS server for new patients
- **Automated Download**: Downloads DICOM archives (.zip) from Orthanc server
- **File Extraction**: Extracts DICOM files from compressed archives
- **DICOM to JPEG Conversion**: Converts medical images to high-quality JPEG format
- **PDF Generation**: Organizes images in A4-formatted tables and generates PDF reports
- **Windows Auto-Printing**: Automatic printing on Windows systems (EPSON L3250 Series supported)

### 🖼️ Image Processing
- **High-Quality Conversion**: Maintains medical image fidelity during DICOM to JPEG conversion
- **Gamma Correction**: Adjustable black level correction for optimal image visibility
- **Enhancement Options**: Configurable brightness, contrast, color, and sharpness adjustments
- **A4 Layout**: Smart image arrangement in 4x2 grid layout per PDF page

### 📁 File Organization
- **Patient-Based Structure**: Automatic creation of organized patient directories
- **Separate Folders**: Images and reports stored in dedicated subdirectories
- **Clean Workspace**: Automatic cleanup of temporary DICOM files after processing

### 🖨️ Printing System
- **Windows Integration**: Native Windows printing support using pywin32
- **Printer Selection**: Configurable printer selection with fallback to default
- **Error Handling**: Comprehensive error handling for printing operations
- **Cross-Platform Awareness**: Graceful degradation on non-Windows platforms

## 🚧 Pending Features

### 📊 DICOM Structured Report (SR) Processing
- **SR Data Extraction**: Parse measurements and biometric data from DICOM SR files
- **Measurement Visualization**: Generate plots and charts from extracted measurements
- **Enhanced Reports**: Integrate SR data into PDF reports

### 🔍 OCR & Text Processing
- **OCR Integration**: Extract text from medical images using Tesseract
- **Text Enhancement**: AI-powered text improvement using OpenAI GPT
- **Medical Report Generation**: Automated medical report creation from OCR text

### 🤖 AI Integration
- **GPT Client**: OpenAI integration for medical text processing
- **Intelligent Analysis**: AI-powered image and text analysis capabilities
- **Report Enhancement**: Automated medical terminology and formatting improvements

## 🏗️ Project Structure

```
Dicom-PDF/
├── main.py                    # Main application loop
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── environment.yml           # Conda environment setup
├── DicomManager/             # DICOM processing modules
│   ├── DICOM.py             # DICOM to JPEG conversion
│   └── unzip.py             # Archive extraction
├── PDFMAKER/                # PDF generation
│   └── pdfmaker.py          # A4 layout PDF creator
├── SR/                      # Structured Report processing (pending)
│   ├── SR2DATA.py           # SR data extraction
│   └── SR2PLOT.py           # Measurement visualization
├── utils/                   # Utility modules
│   ├── gpt_client.py        # OpenAI integration (pending)
│   └── ocr.py              # OCR processing (pending)
├── ZIPS/                    # Downloaded archives storage
├── Dicoms/                  # Temporary DICOM extraction
└── Patients/               # Organized patient data
    └── [PatientID]/
        ├── Images/         # Converted JPEG images
        └── Report/         # Generated PDF reports
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows OS (for printing functionality)
- Access to Orthanc PACS server

### Installation
```bash
# Clone the repository
git clone [repository-url]
cd Dicom-PDF

# Install dependencies
pip install -r requirements.txt

# Or using conda
conda env create -f environment.yml
conda activate dicom-pdf
```

### Configuration
1. Update Orthanc server credentials in `main.py`
2. Configure printer name in `imprimir_arquivo()` function
3. Adjust image processing parameters in `DICOM2JPEG` class

### Usage
```bash
python main.py
```

The system will:
1. Connect to the Orthanc server
2. Monitor for new patients every 20 seconds
3. Process new DICOM archives automatically
4. Generate PDFs and print them automatically

## 🔧 Configuration Options

### Image Processing
- **Gamma Correction**: Adjust `black_gamma` parameter (default: 0.8)
- **JPEG Quality**: Set compression quality (default: 99)
- **Enhancements**: Configure brightness, contrast, color, sharpness

### PDF Layout
- **Grid Size**: 4 rows × 2 columns per page
- **Page Format**: A4 with optimized margins
- **Image Sizing**: Automatic aspect ratio preservation

### Printing
- **Default Printer**: EPSON L3250 Series
- **Windows Only**: Automatic fallback on other platforms
- **Error Handling**: Comprehensive logging and error recovery

## 📋 System Requirements

### Required
- Python 3.8+
- PIL/Pillow for image processing
- pydicom for DICOM handling
- reportlab for PDF generation
- pyorthanc for PACS integration

### Windows Printing
- pywin32 (Windows only)
- Compatible printer drivers

### Pending Features Dependencies
- tesseract-ocr (for OCR functionality)
- openai (for AI text processing)
- matplotlib/plotly (for SR visualization)

## 🤝 Contributing

This project is under active development. The core workflow is stable and production-ready, while advanced features (OCR, AI integration, SR processing) are being implemented.

## 📝 Example

![DICOM-PDF](https://github.com/user-attachments/assets/95487a15-4532-4c99-9655-c86285aa45bc)
