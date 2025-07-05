#!/usr/bin/env python3
"""
Example script showing automated usage of the test framework.
This can be used as a template for automated testing or CI/CD integration.
"""

import os
import sys
import argparse
from datetime import datetime

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import config
from test_single_patient import SinglePatientTester


def run_automated_test(patient_id=None, skip_validation=False):
    """
    Run automated test with minimal user interaction.
    
    Args:
        patient_id: Specific patient ID to test
        skip_validation: Skip environment validation
    
    Returns:
        Test success status
    """
    print(f"🤖 Automated DICOM PDF Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Create tester
    tester = SinglePatientTester()
    
    # Environment validation
    if not skip_validation:
        print("📋 Validating environment...")
        if not tester.validate_environment():
            print("❌ Environment validation failed")
            return False
        print("✅ Environment validation passed")
    
    # Test Orthanc connection
    print("🌐 Testing Orthanc connection...")
    if not tester.connect_orthanc():
        print("❌ Orthanc connection failed")
        return False
    print("✅ Orthanc connection successful")
    
    # Get patient info
    if patient_id:
        print(f"👤 Testing specific patient: {patient_id}")
        patient_info = tester.orthanc_validator.get_patient_info(patient_id)
        if not patient_info:
            print(f"❌ Patient {patient_id} not found")
            return False
        
        selected_patient = {
            "id": patient_id,
            "name": patient_info.get('MainDicomTags', {}).get('PatientName', 'Unknown'),
            "info": patient_info
        }
    else:
        print("👥 Getting available patients...")
        patients = tester.orthanc_validator.get_patients_list()
        
        if not patients:
            print("❌ No patients found")
            return False
        
        # Select first patient for automated testing
        first_patient_id = patients[0]
        patient_info = tester.orthanc_validator.get_patient_info(first_patient_id)
        
        selected_patient = {
            "id": first_patient_id,
            "name": patient_info.get('MainDicomTags', {}).get('PatientName', 'Unknown'),
            "info": patient_info
        }
        
        print(f"📝 Selected patient: {selected_patient['id']} - {selected_patient['name']}")
    
    # Process patient
    print("⚙️ Processing patient...")
    success = tester.process_patient(selected_patient)
    
    if success:
        print("✅ Patient processing completed successfully")
    else:
        print("❌ Patient processing failed")
    
    # Generate final report
    print("📊 Generating final report...")
    tester.test_results["test_session"]["completed"] = datetime.now().isoformat()
    report_path = tester.test_reporter.generate_test_report(tester.test_results)
    
    # Print summary
    tester.test_reporter.print_test_summary(tester.test_results)
    
    print(f"\n📄 Full report available at: {report_path}")
    
    return success


def main():
    """Main entry point for automated testing."""
    parser = argparse.ArgumentParser(
        description="Automated DICOM PDF processing test"
    )
    parser.add_argument(
        "--patient-id",
        help="Specific patient ID to test (optional)"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip environment validation"
    )
    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Only check configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Configuration check mode
    if args.config_check:
        print("🔧 Configuration Check")
        print("=" * 30)
        config.print_configuration()
        
        validation_results = config.validate_environment()
        print(f"\nEnvironment Valid: {validation_results['valid']}")
        
        if validation_results['missing_dependencies']:
            print(f"Missing Dependencies: {validation_results['missing_dependencies']}")
        
        if validation_results['missing_configurations']:
            print(f"Missing Configurations: {validation_results['missing_configurations']}")
        
        if validation_results['warnings']:
            print("Warnings:")
            for warning in validation_results['warnings']:
                print(f"  - {warning}")
        
        return
    
    # Run automated test
    try:
        success = run_automated_test(
            patient_id=args.patient_id,
            skip_validation=args.skip_validation
        )
        
        if success:
            print("🎉 Automated test completed successfully!")
        else:
            print("💥 Automated test failed!")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()