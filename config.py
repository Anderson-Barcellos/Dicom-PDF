"""
Configuration module for DICOM PDF processing system.
Centralizes all configuration settings for Orthanc connection, 
environment validation, and directory structure.
"""

import os
import sys
from typing import Dict, Any, Optional


class Config:
    """Configuration class for DICOM PDF processing system."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        # Orthanc Configuration
        self.orthanc_host = os.getenv("ORTHANC_HOST", "")
        self.orthanc_username = os.getenv("ORTHANC_USERNAME", "orthanc")
        self.orthanc_password = os.getenv("ORTHANC_PASSWORD", "orthanc")
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Directory Structure
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_results_dir = os.path.join(self.base_dir, "test_results")
        self.patients_dir = os.path.join(self.test_results_dir, "Pacientes")
        self.zips_dir = os.path.join(self.test_results_dir, "ZIPS")
        self.dicoms_dir = os.path.join(self.test_results_dir, "Dicoms")
        
        # Processing Configuration
        self.jpeg_quality = 95
        self.ocr_enhancement_enabled = True
        self.medical_report_enabled = True
        
        # Logging Configuration
        self.log_level = "INFO"
        self.detailed_logging = True
        
    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate that all required dependencies and configurations are available.
        
        Returns:
            Dict containing validation results and missing dependencies.
        """
        validation_results = {
            "valid": True,
            "missing_dependencies": [],
            "missing_configurations": [],
            "warnings": []
        }
        
        # Check required Python packages (mapping package names to import names)
        required_packages = {
            "pydicom": "pydicom",
            "Pillow": "PIL",
            "numpy": "numpy",
            "matplotlib": "matplotlib",
            "reportlab": "reportlab",
            "opencv-python": "cv2",
            "pytesseract": "pytesseract",
            "pyorthanc": "pyorthanc",
            "openai": "openai"
        }
        
        for package_name, import_name in required_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                validation_results["missing_dependencies"].append(package_name)
                validation_results["valid"] = False
        
        # Check OpenAI API key
        if not self.openai_api_key:
            validation_results["missing_configurations"].append("OPENAI_API_KEY")
            validation_results["warnings"].append("OpenAI API key not configured. OCR enhancement and medical report generation will be disabled.")
        
        # Check Orthanc configuration
        if not self.orthanc_host:
            validation_results["missing_configurations"].append("ORTHANC_HOST")
            validation_results["warnings"].append("Orthanc host not configured. Using default empty string.")
        
        # Check if tesseract is available
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
        except Exception:
            validation_results["warnings"].append("Tesseract OCR not properly configured. OCR functionality may not work.")
        
        return validation_results
    
    def setup_directories(self) -> None:
        """Create necessary directory structure for testing."""
        directories = [
            self.test_results_dir,
            self.patients_dir,
            self.zips_dir,
            self.dicoms_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_patient_directories(self, patient_name: str) -> Dict[str, str]:
        """
        Get directory paths for a specific patient.
        
        Args:
            patient_name: Name of the patient
            
        Returns:
            Dictionary with patient directory paths
        """
        patient_base_dir = os.path.join(self.patients_dir, patient_name)
        return {
            "base": patient_base_dir,
            "images": os.path.join(patient_base_dir, "Images"),
            "reports": os.path.join(patient_base_dir, "Report")
        }
    
    def print_configuration(self) -> None:
        """Print current configuration settings."""
        print("=== DICOM PDF Test Configuration ===")
        print(f"Orthanc Host: {self.orthanc_host or 'Not configured'}")
        print(f"Orthanc Username: {self.orthanc_username}")
        print(f"OpenAI API Key: {'Configured' if self.openai_api_key else 'Not configured'}")
        print(f"Test Results Directory: {self.test_results_dir}")
        print(f"OCR Enhancement: {'Enabled' if self.ocr_enhancement_enabled else 'Disabled'}")
        print(f"Medical Report Generation: {'Enabled' if self.medical_report_enabled else 'Disabled'}")
        print("=" * 37)


# Global configuration instance
config = Config()