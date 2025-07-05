#!/usr/bin/env python3
"""
Basic validation test for the DICOM PDF test framework.
Tests that all modules can be imported and basic functionality works.
"""

import os
import sys
import tempfile
import shutil

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from config import config
        print("✓ config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from test_utils import TestLogger, OrthancValidator, FileValidator, TestReporter
        print("✓ test_utils module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import test_utils: {e}")
        return False
    
    try:
        from test_single_patient import SinglePatientTester
        print("✓ test_single_patient module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import test_single_patient: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration functionality."""
    print("\nTesting configuration...")
    
    from config import config
    
    # Test directory setup
    original_test_dir = config.test_results_dir
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        config.test_results_dir = temp_dir
        config.patients_dir = os.path.join(temp_dir, "Pacientes")
        config.zips_dir = os.path.join(temp_dir, "ZIPS")
        config.dicoms_dir = os.path.join(temp_dir, "Dicoms")
        
        try:
            config.setup_directories()
            
            # Check if directories were created
            if os.path.exists(config.patients_dir):
                print("✓ Patients directory created successfully")
            else:
                print("✗ Failed to create patients directory")
                return False
            
            if os.path.exists(config.zips_dir):
                print("✓ ZIPS directory created successfully")
            else:
                print("✗ Failed to create ZIPS directory")
                return False
            
            if os.path.exists(config.dicoms_dir):
                print("✓ Dicoms directory created successfully")
            else:
                print("✗ Failed to create dicoms directory")
                return False
            
            # Test patient directory creation
            patient_dirs = config.get_patient_directories("TestPatient")
            expected_dirs = ["base", "images", "reports"]
            
            for dir_type in expected_dirs:
                if dir_type in patient_dirs:
                    print(f"✓ Patient directory '{dir_type}' path generated correctly")
                else:
                    print(f"✗ Patient directory '{dir_type}' path missing")
                    return False
                    
        except Exception as e:
            print(f"✗ Configuration test failed: {e}")
            return False
        finally:
            # Restore original configuration
            config.test_results_dir = original_test_dir
            config.patients_dir = os.path.join(original_test_dir, "Pacientes")
            config.zips_dir = os.path.join(original_test_dir, "ZIPS")
            config.dicoms_dir = os.path.join(original_test_dir, "Dicoms")
    
    return True


def test_logging():
    """Test logging functionality."""
    print("\nTesting logging...")
    
    from test_utils import TestLogger
    
    try:
        logger = TestLogger("TestLogger")
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.debug("Test debug message")
        logger.step("Test step", "SUCCESS")
        print("✓ Logging functionality working correctly")
        return True
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False


def test_environment_validation():
    """Test environment validation."""
    print("\nTesting environment validation...")
    
    from config import config
    
    try:
        validation_results = config.validate_environment()
        
        if isinstance(validation_results, dict):
            print("✓ Environment validation returns proper dictionary")
            
            required_keys = ["valid", "missing_dependencies", "missing_configurations", "warnings"]
            for key in required_keys:
                if key in validation_results:
                    print(f"✓ Validation result contains '{key}' key")
                else:
                    print(f"✗ Validation result missing '{key}' key")
                    return False
            
            print(f"✓ Environment validation completed (valid: {validation_results['valid']})")
            
            if validation_results["warnings"]:
                print("  Warnings:")
                for warning in validation_results["warnings"]:
                    print(f"    - {warning}")
            
            return True
        else:
            print("✗ Environment validation doesn't return dictionary")
            return False
            
    except Exception as e:
        print(f"✗ Environment validation test failed: {e}")
        return False


def test_file_validation():
    """Test file validation functionality."""
    print("\nTesting file validation...")
    
    from test_utils import TestLogger, FileValidator
    
    try:
        logger = TestLogger("TestFileValidator")
        validator = FileValidator(logger)
        
        # Test with non-existent patient
        result = validator.validate_patient_structure("NonExistentPatient")
        
        if isinstance(result, dict):
            print("✓ File validation returns proper dictionary")
            
            if "validation_passed" in result:
                print("✓ File validation includes validation_passed key")
            else:
                print("✗ File validation missing validation_passed key")
                return False
            
            if "issues" in result:
                print("✓ File validation includes issues key")
            else:
                print("✗ File validation missing issues key")
                return False
            
            # Should fail for non-existent patient
            if not result["validation_passed"]:
                print("✓ File validation correctly fails for non-existent patient")
            else:
                print("✗ File validation should fail for non-existent patient")
                return False
            
            return True
        else:
            print("✗ File validation doesn't return dictionary")
            return False
            
    except Exception as e:
        print(f"✗ File validation test failed: {e}")
        return False


def test_main_tester_creation():
    """Test that the main tester can be created."""
    print("\nTesting main tester creation...")
    
    from test_single_patient import SinglePatientTester
    
    try:
        tester = SinglePatientTester()
        print("✓ SinglePatientTester created successfully")
        
        # Test basic properties
        if hasattr(tester, 'logger'):
            print("✓ Tester has logger attribute")
        else:
            print("✗ Tester missing logger attribute")
            return False
            
        if hasattr(tester, 'orthanc_validator'):
            print("✓ Tester has orthanc_validator attribute")
        else:
            print("✗ Tester missing orthanc_validator attribute")
            return False
            
        if hasattr(tester, 'file_validator'):
            print("✓ Tester has file_validator attribute")
        else:
            print("✗ Tester missing file_validator attribute")
            return False
            
        if hasattr(tester, 'test_reporter'):
            print("✓ Tester has test_reporter attribute")
        else:
            print("✗ Tester missing test_reporter attribute")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Main tester creation failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("    DICOM PDF Test Framework Validation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_logging,
        test_environment_validation,
        test_file_validation,
        test_main_tester_creation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✓ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"✗ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED with exception: {e}")
        
        print("-" * 60)
    
    print(f"\nSUMMARY: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Test framework is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)