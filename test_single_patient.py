#!/usr/bin/env python3
"""
Single Patient Test Script for DICOM PDF Processing System.

This script allows testing the complete DICOM processing pipeline for a single patient
without depending on the main monitoring loop. It provides comprehensive validation
and detailed logging of each processing step.

Usage:
    python test_single_patient.py [patient_id]
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import config
from test_utils import TestLogger, OrthancValidator, FileValidator, TestReporter
from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
from PDFMAKER.pdfmaker import MkPDF
from utils.ocr import extract_ultrasound_text
from utils.gpt_client import GPTClient


class SinglePatientTester:
    """Main class for testing single patient processing."""
    
    def __init__(self):
        """Initialize tester with all required components."""
        # Setup configuration and directories
        config.setup_directories()
        
        # Initialize components
        self.logger = TestLogger()
        self.orthanc_validator = OrthancValidator(self.logger)
        self.file_validator = FileValidator(self.logger)
        self.test_reporter = TestReporter(self.logger)
        
        # Test results container
        self.test_results = {
            "test_session": {
                "started": datetime.now().isoformat(),
                "configuration": self._get_config_summary()
            },
            "tests": []
        }
    
    def _get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for reporting."""
        return {
            "orthanc_host": config.orthanc_host or "Not configured",
            "openai_configured": bool(config.openai_api_key),
            "test_results_dir": config.test_results_dir,
            "ocr_enhancement": config.ocr_enhancement_enabled,
            "medical_report": config.medical_report_enabled
        }
    
    def validate_environment(self) -> bool:
        """
        Validate environment setup and dependencies.
        
        Returns:
            True if environment is valid, False otherwise.
        """
        self.logger.step("Environment Validation", "STARTED")
        
        validation_results = config.validate_environment()
        
        test_result = {
            "name": "Environment Validation",
            "passed": validation_results["valid"],
            "timestamp": datetime.now().isoformat(),
            "details": validation_results
        }
        
        if not validation_results["valid"]:
            self.logger.error("Environment validation failed")
            for dep in validation_results["missing_dependencies"]:
                self.logger.error(f"Missing dependency: {dep}")
            
            test_result["issues"] = validation_results["missing_dependencies"]
        
        for warning in validation_results["warnings"]:
            self.logger.warning(warning)
        
        self.test_results["tests"].append(test_result)
        self.logger.step("Environment Validation", "COMPLETED")
        
        return validation_results["valid"]
    
    def connect_orthanc(self) -> bool:
        """
        Test Orthanc connection.
        
        Returns:
            True if connection successful, False otherwise.
        """
        self.logger.step("Orthanc Connection Test", "STARTED")
        
        success = self.orthanc_validator.validate_connection()
        
        test_result = {
            "name": "Orthanc Connection",
            "passed": success,
            "timestamp": datetime.now().isoformat(),
            "issues": [] if success else ["Failed to connect to Orthanc server"]
        }
        
        self.test_results["tests"].append(test_result)
        self.logger.step("Orthanc Connection Test", "COMPLETED")
        
        return success
    
    def list_patients(self) -> Optional[Dict[str, Any]]:
        """
        List available patients and allow selection.
        
        Returns:
            Selected patient information or None if no selection.
        """
        self.logger.step("Patient Listing", "STARTED")
        
        patients = self.orthanc_validator.get_patients_list()
        
        if not patients:
            self.logger.error("No patients found in Orthanc")
            return None
        
        print(f"\nFound {len(patients)} patients in Orthanc:")
        print("-" * 50)
        
        # Display patients with details
        patient_details = []
        for i, patient_id in enumerate(patients, 1):
            patient_info = self.orthanc_validator.get_patient_info(patient_id)
            
            if patient_info:
                patient_name = patient_info.get('MainDicomTags', {}).get('PatientName', 'Unknown')
                patient_birth = patient_info.get('MainDicomTags', {}).get('PatientBirthDate', 'Unknown')
                study_count = len(patient_info.get('Studies', []))
                
                print(f"{i:2d}. ID: {patient_id}")
                print(f"    Name: {patient_name}")
                print(f"    Birth Date: {patient_birth}")
                print(f"    Studies: {study_count}")
                print()
                
                patient_details.append({
                    "index": i,
                    "id": patient_id,
                    "name": patient_name,
                    "birth_date": patient_birth,
                    "study_count": study_count,
                    "info": patient_info
                })
        
        # Allow user selection
        try:
            choice = input(f"Select patient (1-{len(patients)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                self.logger.info("User cancelled patient selection")
                return None
            
            patient_index = int(choice) - 1
            if 0 <= patient_index < len(patient_details):
                selected_patient = patient_details[patient_index]
                self.logger.info(f"Selected patient: {selected_patient['id']} - {selected_patient['name']}")
                return selected_patient
            else:
                self.logger.error("Invalid patient selection")
                return None
                
        except (ValueError, KeyboardInterrupt):
            self.logger.error("Invalid input or user cancelled")
            return None
    
    def process_patient(self, patient_info: Dict[str, Any]) -> bool:
        """
        Process a single patient through the complete pipeline.
        
        Args:
            patient_info: Patient information dictionary
            
        Returns:
            True if processing successful, False otherwise.
        """
        patient_id = patient_info["id"]
        patient_name = patient_info["name"]
        
        self.logger.step(f"Processing Patient {patient_id}", "STARTED")
        
        try:
            # Step 1: Download patient archive
            if not self._download_patient_archive(patient_id):
                return False
            
            # Step 2: Extract and convert DICOM files
            if not self._extract_and_convert_dicom(patient_id, patient_name):
                return False
            
            # Step 3: Validate generated files
            if not self._validate_generated_files(patient_name):
                return False
            
            self.logger.step(f"Processing Patient {patient_id}", "COMPLETED")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing patient {patient_id}: {str(e)}")
            return False
    
    def _download_patient_archive(self, patient_id: str) -> bool:
        """Download patient archive from Orthanc."""
        self.logger.step(f"Downloading archive for patient {patient_id}")
        
        archive_data = self.orthanc_validator.download_patient_archive(patient_id)
        
        if not archive_data:
            self.logger.error(f"Failed to download archive for patient {patient_id}")
            return False
        
        # Save archive to test results directory
        zip_path = os.path.join(config.zips_dir, f"{patient_id}.zip")
        
        try:
            with open(zip_path, "wb") as f:
                f.write(archive_data)
            
            self.logger.info(f"Archive saved to: {zip_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save archive: {str(e)}")
            return False
    
    def _extract_and_convert_dicom(self, patient_id: str, patient_name: str) -> bool:
        """Extract DICOM files and convert to JPEG."""
        self.logger.step(f"Extracting and converting DICOM files for {patient_name}")
        
        try:
            # Use modified version of Extract_Convert_Img function
            return self._process_dicom_pipeline(f"{patient_id}.zip", patient_name)
            
        except Exception as e:
            self.logger.error(f"Error in DICOM processing: {str(e)}")
            return False
    
    def _process_dicom_pipeline(self, zip_filename: str, patient_name: str) -> bool:
        """
        Process DICOM pipeline similar to Extract_Convert_Img but with test modifications.
        
        Args:
            zip_filename: ZIP file name
            patient_name: Patient name for folder creation
            
        Returns:
            True if processing successful, False otherwise.
        """
        try:
            # Extract the file
            zip_path = os.path.join(config.zips_dir, zip_filename)
            unzipper = Unzipper(zip_filename, config.dicoms_dir)
            unzipper.unzipper()
            
            # Create patient directories in test results
            patient_dirs = config.get_patient_directories(patient_name)
            for dir_path in patient_dirs.values():
                os.makedirs(dir_path, exist_ok=True)
            
            # Convert DICOM to JPEG
            self.logger.step("Converting DICOM to JPEG")
            dicom2jpeg = DICOM2JPEG(config.dicoms_dir, patient_dirs["images"])
            dicom2jpeg.converter()
            
            # Initialize GPT client if available
            gpt = None
            if config.openai_api_key and config.ocr_enhancement_enabled:
                gpt = GPTClient()
            
            # Extract and enhance OCR text from all images
            self.logger.step("Performing OCR on converted images")
            all_ocr_findings = []
            txt_path = os.path.join(patient_dirs["reports"], f"{patient_name}_ocr.txt")
            
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                for img in os.listdir(patient_dirs["images"]):
                    if img.lower().endswith((".jpeg", ".jpg", ".png", ".bmp")):
                        img_path = os.path.join(patient_dirs["images"], img)
                        
                        try:
                            text, _ = extract_ultrasound_text(img_path)
                            enhanced_lines = []
                            
                            for line in text.splitlines():
                                if line.strip():
                                    if gpt:
                                        try:
                                            enhanced_line = gpt.enhance_text(line)
                                            enhanced_lines.append(enhanced_line)
                                            all_ocr_findings.append(enhanced_line)
                                        except Exception as e:
                                            self.logger.warning(f"GPT enhancement failed for line: {str(e)}")
                                            enhanced_lines.append(line)
                                            all_ocr_findings.append(line)
                                    else:
                                        enhanced_lines.append(line)
                                        all_ocr_findings.append(line)
                                else:
                                    enhanced_lines.append("")
                            
                            txt_file.write(f"# {img}\n" + "\n".join(enhanced_lines) + "\n")
                            
                        except Exception as e:
                            self.logger.warning(f"OCR failed for {img}: {str(e)}")
            
            # Generate comprehensive medical report
            if all_ocr_findings and gpt and config.medical_report_enabled:
                self.logger.step("Generating medical report")
                try:
                    combined_findings = "\n".join(all_ocr_findings)
                    medical_report = gpt.generate_medical_report(combined_findings, patient_name)
                    
                    report_path = os.path.join(patient_dirs["reports"], f"{patient_name}_report.txt")
                    with open(report_path, "w", encoding="utf-8") as report_file:
                        report_file.write(medical_report)
                        
                except Exception as e:
                    self.logger.warning(f"Medical report generation failed: {str(e)}")
            
            # Create PDF
            self.logger.step("Creating PDF report")
            MkPDF(f"test_patient_{patient_name}", patient_dirs["images"], patient_dirs["reports"])
            
            # Cleanup temporary DICOM files
            dicom2jpeg.eliminate_dcm()
            
            self.logger.info("DICOM processing pipeline completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in DICOM processing pipeline: {str(e)}")
            return False
    
    def _validate_generated_files(self, patient_name: str) -> bool:
        """Validate all generated files for the patient."""
        self.logger.step(f"Validating generated files for {patient_name}")
        
        # Validate directory structure
        structure_validation = self.file_validator.validate_patient_structure(patient_name)
        
        test_result = {
            "name": f"File Structure Validation - {patient_name}",
            "passed": structure_validation["validation_passed"],
            "timestamp": datetime.now().isoformat(),
            "details": structure_validation,
            "issues": structure_validation["issues"]
        }
        
        self.test_results["tests"].append(test_result)
        
        # Validate PDF quality
        patient_dirs = config.get_patient_directories(patient_name)
        pdf_path = os.path.join(patient_dirs["reports"], f"{patient_name}.pdf")
        
        pdf_validation = self.file_validator.validate_pdf_quality(pdf_path)
        
        pdf_test_result = {
            "name": f"PDF Quality Validation - {patient_name}",
            "passed": len(pdf_validation["issues"]) == 0,
            "timestamp": datetime.now().isoformat(),
            "details": pdf_validation,
            "issues": pdf_validation["issues"]
        }
        
        self.test_results["tests"].append(pdf_test_result)
        
        # Validate OCR content
        ocr_path = os.path.join(patient_dirs["reports"], f"{patient_name}_ocr.txt")
        ocr_validation = self.file_validator.validate_ocr_content(ocr_path)
        
        ocr_test_result = {
            "name": f"OCR Content Validation - {patient_name}",
            "passed": len(ocr_validation["issues"]) == 0,
            "timestamp": datetime.now().isoformat(),
            "details": ocr_validation,
            "issues": ocr_validation["issues"]
        }
        
        self.test_results["tests"].append(ocr_test_result)
        
        # Overall validation result
        overall_success = (
            structure_validation["validation_passed"] and
            len(pdf_validation["issues"]) == 0 and
            len(ocr_validation["issues"]) == 0
        )
        
        if overall_success:
            self.logger.info(f"✅ All files validated successfully for {patient_name}")
        else:
            self.logger.warning(f"⚠️ Some validation issues found for {patient_name}")
        
        return overall_success
    
    def run_full_test(self, patient_id: Optional[str] = None) -> bool:
        """
        Run complete test suite for a single patient.
        
        Args:
            patient_id: Specific patient ID to test, or None for interactive selection
            
        Returns:
            True if all tests passed, False otherwise.
        """
        self.logger.info("Starting single patient test execution")
        config.print_configuration()
        
        # Step 1: Validate environment
        if not self.validate_environment():
            self.logger.error("Environment validation failed. Cannot continue.")
            return False
        
        # Step 2: Connect to Orthanc
        if not self.connect_orthanc():
            self.logger.error("Orthanc connection failed. Cannot continue.")
            return False
        
        # Step 3: Select patient
        if patient_id:
            # Use specified patient ID
            patient_info = self.orthanc_validator.get_patient_info(patient_id)
            if not patient_info:
                self.logger.error(f"Patient {patient_id} not found")
                return False
            
            selected_patient = {
                "id": patient_id,
                "name": patient_info.get('MainDicomTags', {}).get('PatientName', 'Unknown'),
                "info": patient_info
            }
        else:
            # Interactive selection
            selected_patient = self.list_patients()
            if not selected_patient:
                self.logger.error("No patient selected. Cannot continue.")
                return False
        
        # Step 4: Process patient
        success = self.process_patient(selected_patient)
        
        # Step 5: Generate final report
        self.test_results["test_session"]["completed"] = datetime.now().isoformat()
        self.test_results["test_session"]["duration"] = str(
            datetime.fromisoformat(self.test_results["test_session"]["completed"]) -
            datetime.fromisoformat(self.test_results["test_session"]["started"])
        )
        
        report_path = self.test_reporter.generate_test_report(self.test_results)
        self.test_reporter.print_test_summary(self.test_results)
        
        self.logger.info(f"Test execution completed. Report saved to: {report_path}")
        
        return success


def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(
        description="Test DICOM PDF processing pipeline for a single patient"
    )
    parser.add_argument(
        "patient_id",
        nargs="?",
        help="Specific patient ID to test (optional - will prompt for selection if not provided)"
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show configuration and exit"
    )
    
    args = parser.parse_args()
    
    if args.config:
        config.print_configuration()
        return
    
    # Create and run tester
    tester = SinglePatientTester()
    success = tester.run_full_test(args.patient_id)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()