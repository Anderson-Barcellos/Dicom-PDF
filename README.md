# DICOM to PDF and AI-Powered Medical Reporting System

## 🏥 Overview

An advanced automated medical imaging processing system that seamlessly integrates with Orthanc PACS servers to process DICOM files and generate comprehensive PDF reports with AI-powered medical analysis capabilities. The system is designed for clinical environments requiring automated processing of medical imaging data with intelligent reporting features.

## ✨ Key Features

### 🔄 Core Workflow (Production Ready)
- **Continuous PACS Monitoring**: Real-time monitoring of Orthanc PACS server for new patient studies
- **Multi-User Support**: User-specific patient management and organization system
- **Automated Download & Processing**: Seamless download and processing of DICOM archives (.zip)
- **Intelligent File Extraction**: Advanced ZIP extraction with proper patient naming and organization
- **High-Quality DICOM Conversion**: Converts medical images to optimized JPEG format with medical-grade quality
- **Professional PDF Generation**: Creates A4-formatted reports with 4x2 grid layout per page
- **Automated Cleanup**: Intelligent cleanup of temporary files after processing

### 🖼️ Advanced Image Processing
- **Medical Image Optimization**: Specialized processing for medical imaging requirements
- **Gamma Correction**: Adjustable black level correction for optimal medical image visibility
- **Enhancement Pipeline**: Configurable brightness, contrast, color, and sharpness adjustments
- **Video Detection**: Automatic detection and skipping of video/multiframe DICOM files
- **Modality Support**: Support for various DICOM modalities with appropriate processing
- **Quality Preservation**: Maintains medical image fidelity during conversion process

### 🤖 AI-Powered Medical Reporting
- **GPT-4o Vision OCR**: Advanced OCR using OpenAI's GPT-4o Vision model for medical text extraction
- **Intelligent Medical Analysis**: AI-powered analysis of ultrasound images and findings
- **Professional Report Generation**: Automated generation of structured medical reports using OpenAI's O3 model
- **Medical Terminology Processing**: Specialized handling of medical terminology and measurements
- **Multi-Modal Processing**: Batch processing of multiple images for comprehensive analysis
- **Markdown to PDF Conversion**: Professional formatting of AI-generated reports

### � Robust File Organization
- **Patient-Centric Structure**: Organized patient directories with dedicated subdirectories
- **Separate Asset Management**: Images and reports stored in dedicated folders
- **User-Based Organization**: Multi-user support with user-specific patient management
- **Automatic Directory Creation**: Dynamic creation of required directory structures
- **Clean Workspace Management**: Automated cleanup of temporary processing files

### 🖨️ Printing System (Windows)
- **Windows Integration**: Native Windows printing support using pywin32
- **Printer Management**: Configurable printer selection with fallback options
- **Error Handling**: Comprehensive error handling for printing operations
- **Cross-Platform Awareness**: Graceful degradation on non-Windows platforms

## 🏗️ Project Architecture

```
Dicom-PDF/
├── main.py                    # Main application loop with Orthanc integration
├── environment.yml           # Conda environment configuration
├── .github/workflows/        # CI/CD pipelines
│   ├── python-package-conda.yml
│   └── docker-image.yml
├── DicomManager/             # DICOM processing modules
│   ├── __init__.py
│   ├── DICOM.py             # Advanced DICOM to JPEG conversion
│   └── unzip.py             # ZIP extraction and patient organization
├── PDFMAKER/                # PDF generation system
│   ├── __init__.py
│   └── pdfmaker.py          # A4 layout PDF creator with table formatting
├── OCR/                     # AI-powered OCR and reporting
│   ├── __init__.py
│   ├── gpt_ocr.py           # GPT-4o Vision OCR and O3 report generation
│   └── markdown_to_pdf.py   # Markdown to PDF conversion
├── Users/                   # User management system
│   └── Anders/
│       └── Patients/        # Patient data organization
├── ZIPS/                    # Downloaded DICOM archives
├── Dicoms/                  # Temporary DICOM extraction
└── [Patient Processing Output]
    └── [PatientID]/
        ├── Images/          # Converted JPEG images
        └── Report/          # Generated PDF reports
```

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.10+** (Required for modern AI features)
- **Conda package manager** (Recommended for dependency management)
- **Orthanc PACS server access** (Required for DICOM retrieval)
- **OpenAI API key** (Required for AI-powered features)
- **Windows OS** (Optional, for printing functionality)

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Anderson-Barcellos/Dicom-PDF.git
   cd Dicom-PDF
   ```

2. **Create and activate the Conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate dicom-pdf
   ```

3. **Configure environment variables:**
   ```bash
   # Set OpenAI API key for AI features
   export OPENAI_API_KEY="your-openai-api-key"
   
   # Optional: Configure other environment variables
   export ORTHANC_HOST="http://your-orthanc-server:8042"
   export ORTHANC_USERNAME="your-username"
   export ORTHANC_PASSWORD="your-password"
   ```

4. **Set up user configuration:**
   Create a `Users/users.json` file with your user configuration:
   ```json
   {
     "Anders": {
       "AET": "YOUR_AET",
       "patients": [],
       "patients_names": []
     }
   }
   ```

## 🎯 Usage

### Basic Operation
```bash
python main.py
```

The system will:
1. Connect to the configured Orthanc PACS server
2. Monitor for new patients every 10 seconds
3. Download and process new DICOM archives automatically
4. Generate comprehensive PDF reports with AI analysis
5. Organize all outputs in user-specific directories

### Processing Flow
1. **PACS Monitoring**: Continuous monitoring of Orthanc server for new studies
2. **Archive Download**: Automatic download of patient DICOM archives
3. **File Extraction**: Intelligent extraction and organization of DICOM files
4. **Image Conversion**: High-quality DICOM to JPEG conversion with medical optimization
5. **PDF Generation**: Creation of professional A4-formatted reports
6. **AI Analysis**: GPT-4o Vision OCR extraction and O3-powered medical report generation
7. **Report Compilation**: Final PDF compilation with AI-generated medical insights

## 🔧 Configuration Options

### Image Processing Parameters
```python
# DICOM to JPEG conversion settings
DICOM2JPEG(
    dcm_path="Dicoms",
    jpeg_path="Images",
    black_gamma=0.75,           # Gamma correction for medical images
    enhancements={
        'brightness': 1.2,      # Brightness adjustment
        'color': 1.0,           # Color enhancement
        'contrast': 1.5,        # Contrast optimization
        'sharpness': 1.5        # Sharpness enhancement
    },
    jpeg_quality=99             # High-quality JPEG output
)
```

### PDF Layout Configuration
- **Grid Layout**: 4 rows × 2 columns per page
- **Page Format**: A4 with optimized margins
- **Image Sizing**: Automatic aspect ratio preservation
- **Multi-Page Support**: Automatic pagination for multiple images

### AI Processing Settings
- **OCR Model**: GPT-4o Vision for medical text extraction
- **Report Generation**: OpenAI O3 for professional medical reports
- **Batch Processing**: Configurable batch size for image processing
- **Medical Terminology**: Specialized medical vocabulary handling

## 📋 System Requirements

### Core Dependencies
- **Python 3.10+**: Modern Python for AI features
- **pydicom**: DICOM file handling and processing
- **Pillow (PIL)**: Advanced image processing
- **reportlab**: Professional PDF generation
- **pyorthanc**: Orthanc PACS integration
- **numpy**: Numerical processing for medical images
- **opencv**: Computer vision for image enhancement

### AI & ML Dependencies
- **openai**: OpenAI API integration for GPT-4o Vision and O3
- **pytesseract**: OCR capabilities (backup option)
- **scipy**: Scientific computing for image processing
- **matplotlib**: Plotting capabilities for future SR features

### Optional Dependencies
- **pywin32**: Windows printing support
- **rich**: Enhanced terminal output
- **tabulate**: Table formatting utilities

## 🚧 Future Enhancements

### Planned Features
- **DICOM Structured Report (SR) Processing**: Automated extraction and visualization of measurements
- **Enhanced AI Analysis**: Integration of specialized medical AI models
- **Multi-Modal Support**: Support for additional DICOM modalities
- **Real-Time Monitoring**: WebSocket-based real-time updates
- **Database Integration**: Patient data persistence and search capabilities

### Technical Improvements
- **Docker Containerization**: Complete containerization for easy deployment
- **API Development**: REST API for external integrations
- **Security Enhancements**: Advanced authentication and authorization
- **Performance Optimization**: Parallel processing and caching mechanisms

## 🧪 Testing & CI/CD

The project includes comprehensive testing and continuous integration:

- **GitHub Actions**: Automated testing with conda environments
- **Docker Support**: Containerized deployment options
- **Code Quality**: Automated linting and code quality checks
- **Cross-Platform Testing**: Linux-based testing environment

## 🤝 Contributing

This project is actively maintained and welcomes contributions. The core workflow is production-ready, while advanced features are continuously being developed.

### Development Guidelines
1. Follow the existing code structure and documentation patterns
2. Ensure all medical imaging processing maintains quality standards
3. Test thoroughly with sample DICOM files
4. Update documentation for new features

## 📝 Example Output

The system generates professional medical reports with AI-enhanced analysis:

![DICOM-PDF Example](https://github.com/user-attachments/assets/95487a15-4532-4c99-9655-c86285aa45bc)

## 📄 License

This project is licensed under the MIT License - see the license file for details.

## 👥 Authors

- **Anderson Barcellos** - Initial development and AI integration
- **Contributors** - See GitHub contributors for complete list

## 🔗 Related Projects

- [Orthanc PACS Server](https://www.orthanc-server.com/)
- [pydicom](https://github.com/pydicom/pydicom)
- [OpenAI API](https://openai.com/api/)
