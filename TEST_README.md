# Test Single Patient - DICOM PDF Processing

This module provides comprehensive testing functionality for the DICOM PDF processing pipeline without depending on the main monitoring loop.

## Files

- `test_single_patient.py` - Main test script for processing individual patients
- `config.py` - Configuration management for Orthanc connection and environment settings
- `test_utils.py` - Utility functions for validation, logging, and testing

## Features

### 1. Environment Validation
- Validates all required Python dependencies
- Checks OpenAI API key configuration
- Validates Orthanc connection parameters
- Verifies Tesseract OCR installation

### 2. Orthanc Integration
- Connects to configured Orthanc server
- Lists available patients
- Downloads patient archives
- Provides interactive patient selection

### 3. Complete Processing Pipeline
- Downloads ZIP files from Orthanc
- Extracts and converts DICOM to JPEG
- Performs OCR with optional GPT enhancement
- Generates medical reports using AI
- Creates PDF with 4x2 image layout

### 4. File Validation
- Validates directory structure
- Checks file integrity
- Validates PDF quality
- Validates OCR content

### 5. Comprehensive Logging
- Detailed step-by-step logging
- Error tracking and reporting
- Test execution reports
- JSON-formatted results

## Usage

### Configuration

Set environment variables:
```bash
export ORTHANC_HOST="your-orthanc-server"
export ORTHANC_USERNAME="orthanc"
export ORTHANC_PASSWORD="orthanc"
export OPENAI_API_KEY="your-openai-key"
```

### Running Tests

```bash
# Show configuration
python test_single_patient.py --config

# Interactive patient selection
python test_single_patient.py

# Test specific patient
python test_single_patient.py PATIENT_ID
```

### Expected Output Structure

```
test_results/
├── Pacientes/
│   └── [patient_name]/
│       ├── Images/
│       │   ├── [patient_name]0.jpeg
│       │   ├── [patient_name]1.jpeg
│       │   └── ...
│       └── Report/
│           ├── [patient_name]_ocr.txt
│           ├── [patient_name]_report.txt
│           └── [patient_name].pdf
├── ZIPS/
│   └── [patient_id].zip
├── Dicoms/
│   └── [temporary_files]
├── test_execution.log
└── test_report.json
```

## Validation Criteria

### Success Criteria
- [x] Environment validation passed
- [x] Orthanc connection established
- [x] Patient archive downloaded
- [x] DICOM to JPEG conversion successful
- [x] OCR extraction completed
- [x] Medical report generated (if OpenAI configured)
- [x] PDF created with proper layout
- [x] All files saved in correct structure

### Quality Checks
1. **Image Quality**: JPEG images are clear and properly converted
2. **OCR Accuracy**: Text extraction from ultrasound images
3. **Report Structure**: Medical report follows expected format
4. **PDF Layout**: 4x2 grid layout with proper formatting
5. **File Organization**: Correct directory structure maintained

## Error Handling

The test system includes comprehensive error handling:
- Network connection failures
- File system errors
- OCR processing errors
- AI service failures
- PDF generation issues

All errors are logged with detailed context for troubleshooting.

## Dependencies

Required Python packages (see requirements.txt):
- pydicom
- Pillow
- numpy
- matplotlib
- reportlab
- opencv-python
- pytesseract
- pyorthanc
- openai

System dependencies:
- tesseract-ocr

## Configuration Options

The system can be configured through environment variables or by modifying `config.py`:

- `ORTHANC_HOST`: Orthanc server hostname/IP
- `ORTHANC_USERNAME`: Orthanc username (default: "orthanc")
- `ORTHANC_PASSWORD`: Orthanc password (default: "orthanc")
- `OPENAI_API_KEY`: OpenAI API key for GPT enhancement
- OCR enhancement can be disabled in config
- Medical report generation can be disabled in config

## Troubleshooting

1. **Connection Issues**: Check Orthanc server configuration and network connectivity
2. **OCR Failures**: Ensure tesseract is properly installed
3. **AI Enhancement Issues**: Verify OpenAI API key and quota
4. **PDF Generation**: Check file permissions and disk space
5. **Missing Files**: Review logs for processing errors

## Output Files

### Test Execution Log
Contains detailed step-by-step execution log with timestamps.

### Test Report (JSON)
Comprehensive test results including:
- Test session metadata
- Individual test results
- Validation outcomes
- Error details
- Performance metrics

### Patient Files
For each processed patient:
- Original DICOM files (temporary)
- Converted JPEG images
- OCR text files
- AI-generated medical reports
- Final PDF report