"""
Test utilities for DICOM PDF processing system.
Provides validation, logging, and testing helper functions.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pyorthanc import Orthanc
from config import config


class TestLogger:
    """Enhanced logging system for test execution."""
    
    def __init__(self, name: str = "DicomPdfTest"):
        """Initialize logger with custom formatting."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.log_level))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_file = os.path.join(config.test_results_dir, "test_execution.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def step(self, step_name: str, status: str = "STARTED"):
        """Log a processing step."""
        self.logger.info(f"[{status}] {step_name}")


class OrthancValidator:
    """Validates Orthanc connection and patient data."""
    
    def __init__(self, logger: TestLogger):
        """Initialize with logger."""
        self.logger = logger
        self.orthanc = None
    
    def validate_connection(self) -> bool:
        """
        Validate connection to Orthanc server.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            self.logger.step("Validating Orthanc connection")
            self.orthanc = Orthanc(
                config.orthanc_host,
                config.orthanc_username,
                config.orthanc_password
            )
            
            # Test connection by getting system info
            system_info = self.orthanc.get_system()
            self.logger.info(f"Connected to Orthanc: {system_info.get('Name', 'Unknown')}")
            self.logger.info(f"Orthanc Version: {system_info.get('Version', 'Unknown')}")
            
            self.logger.step("Orthanc connection validation", "SUCCESS")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Orthanc: {str(e)}")
            self.logger.step("Orthanc connection validation", "FAILED")
            return False
    
    def get_patients_list(self) -> List[str]:
        """
        Get list of available patients from Orthanc.
        
        Returns:
            List of patient IDs.
        """
        if not self.orthanc:
            raise RuntimeError("Orthanc connection not established")
        
        try:
            self.logger.step("Retrieving patients list")
            patients = self.orthanc.get_patients()
            self.logger.info(f"Found {len(patients)} patients in Orthanc")
            return patients
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve patients: {str(e)}")
            return []
    
    def get_patient_info(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific patient.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Patient information dictionary or None if not found.
        """
        if not self.orthanc:
            raise RuntimeError("Orthanc connection not established")
        
        try:
            patient_info = self.orthanc.get_patients_id(patient_id)
            return patient_info
            
        except Exception as e:
            self.logger.error(f"Failed to get patient info for {patient_id}: {str(e)}")
            return None
    
    def download_patient_archive(self, patient_id: str) -> Optional[bytes]:
        """
        Download patient archive from Orthanc.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Archive content as bytes or None if failed.
        """
        if not self.orthanc:
            raise RuntimeError("Orthanc connection not established")
        
        try:
            self.logger.step(f"Downloading archive for patient {patient_id}")
            response = self.orthanc.get_patients_id_archive(patient_id)
            self.logger.info(f"Downloaded {len(response)} bytes for patient {patient_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to download archive for {patient_id}: {str(e)}")
            return None


class FileValidator:
    """Validates generated files and directory structure."""
    
    def __init__(self, logger: TestLogger):
        """Initialize with logger."""
        self.logger = logger
    
    def validate_patient_structure(self, patient_name: str) -> Dict[str, Any]:
        """
        Validate patient directory structure and files.
        
        Args:
            patient_name: Name of the patient
            
        Returns:
            Validation results dictionary.
        """
        self.logger.step(f"Validating file structure for patient {patient_name}")
        
        patient_dirs = config.get_patient_directories(patient_name)
        
        validation_results = {
            "patient_name": patient_name,
            "timestamp": datetime.now().isoformat(),
            "directories": {},
            "files": {},
            "validation_passed": True,
            "issues": []
        }
        
        # Check directories
        for dir_type, dir_path in patient_dirs.items():
            exists = os.path.exists(dir_path)
            validation_results["directories"][dir_type] = {
                "path": dir_path,
                "exists": exists
            }
            
            if not exists:
                validation_results["validation_passed"] = False
                validation_results["issues"].append(f"Missing directory: {dir_path}")
        
        # Check files
        if os.path.exists(patient_dirs["images"]):
            image_files = [f for f in os.listdir(patient_dirs["images"]) 
                          if f.lower().endswith(('.jpeg', '.jpg', '.png', '.bmp'))]
            validation_results["files"]["images"] = {
                "count": len(image_files),
                "files": image_files
            }
            
            if len(image_files) == 0:
                validation_results["issues"].append("No image files found")
        
        if os.path.exists(patient_dirs["reports"]):
            report_files = os.listdir(patient_dirs["reports"])
            validation_results["files"]["reports"] = {
                "count": len(report_files),
                "files": report_files
            }
            
            # Check for expected report files
            expected_files = [
                f"{patient_name}_ocr.txt",
                f"{patient_name}_report.txt",
                f"{patient_name}.pdf"
            ]
            
            for expected_file in expected_files:
                if expected_file not in report_files:
                    validation_results["issues"].append(f"Missing report file: {expected_file}")
        
        return validation_results
    
    def validate_pdf_quality(self, pdf_path: str) -> Dict[str, Any]:
        """
        Validate PDF file quality and structure.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            PDF validation results.
        """
        self.logger.step(f"Validating PDF quality: {pdf_path}")
        
        validation_results = {
            "pdf_path": pdf_path,
            "exists": os.path.exists(pdf_path),
            "file_size": 0,
            "issues": []
        }
        
        if validation_results["exists"]:
            validation_results["file_size"] = os.path.getsize(pdf_path)
            
            if validation_results["file_size"] == 0:
                validation_results["issues"].append("PDF file is empty")
            elif validation_results["file_size"] < 1024:  # Less than 1KB
                validation_results["issues"].append("PDF file suspiciously small")
        else:
            validation_results["issues"].append("PDF file does not exist")
        
        return validation_results
    
    def validate_ocr_content(self, ocr_path: str) -> Dict[str, Any]:
        """
        Validate OCR text file content.
        
        Args:
            ocr_path: Path to OCR text file
            
        Returns:
            OCR validation results.
        """
        self.logger.step(f"Validating OCR content: {ocr_path}")
        
        validation_results = {
            "ocr_path": ocr_path,
            "exists": os.path.exists(ocr_path),
            "content_length": 0,
            "line_count": 0,
            "issues": []
        }
        
        if validation_results["exists"]:
            try:
                with open(ocr_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    validation_results["content_length"] = len(content)
                    validation_results["line_count"] = len(content.splitlines())
                    
                    if validation_results["content_length"] == 0:
                        validation_results["issues"].append("OCR file is empty")
                    elif validation_results["content_length"] < 50:
                        validation_results["issues"].append("OCR content suspiciously short")
                        
            except Exception as e:
                validation_results["issues"].append(f"Error reading OCR file: {str(e)}")
        else:
            validation_results["issues"].append("OCR file does not exist")
        
        return validation_results


class TestReporter:
    """Generates test execution reports."""
    
    def __init__(self, logger: TestLogger):
        """Initialize with logger."""
        self.logger = logger
    
    def generate_test_report(self, test_results: Dict[str, Any]) -> str:
        """
        Generate comprehensive test report.
        
        Args:
            test_results: Test execution results
            
        Returns:
            Path to generated report file.
        """
        self.logger.step("Generating test report")
        
        report_path = os.path.join(config.test_results_dir, "test_report.json")
        
        # Add timestamp and summary
        test_results["report_generated"] = datetime.now().isoformat()
        test_results["summary"] = {
            "total_tests": len(test_results.get("tests", [])),
            "passed_tests": sum(1 for test in test_results.get("tests", []) if test.get("passed", False)),
            "failed_tests": sum(1 for test in test_results.get("tests", []) if not test.get("passed", False))
        }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Test report generated: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate test report: {str(e)}")
            return ""
    
    def print_test_summary(self, test_results: Dict[str, Any]) -> None:
        """Print test summary to console."""
        print("\n" + "="*50)
        print("            TEST EXECUTION SUMMARY")
        print("="*50)
        
        summary = test_results.get("summary", {})
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Passed: {summary.get('passed_tests', 0)}")
        print(f"Failed: {summary.get('failed_tests', 0)}")
        
        if test_results.get("tests"):
            print("\nTest Details:")
            for test in test_results["tests"]:
                status = "✅ PASSED" if test.get("passed", False) else "❌ FAILED"
                print(f"  {status} - {test.get('name', 'Unknown Test')}")
                
                if test.get("issues"):
                    for issue in test["issues"]:
                        print(f"    - {issue}")
        
        print("="*50)