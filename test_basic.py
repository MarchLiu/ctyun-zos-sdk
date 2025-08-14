#!/usr/bin/env python3
"""Basic test script to verify package functionality."""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from ctyun_zos_sdk import ZOSClient, ZOSSession, ZOSError
        print("✓ Successfully imported main classes")
        
        from ctyun_zos_sdk.async_client import AsyncZOSClient
        print("✓ Successfully imported AsyncZOSClient")
        
        from ctyun_zos_sdk.exceptions import ZOSClientError, ZOSServerError
        print("✓ Successfully imported exception classes")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_client_creation():
    """Test client creation."""
    try:
        from ctyun_zos_sdk import ZOSClient, ZOSSession
        
        client = ZOSClient(
            access_key="test_key",
            secret_key="test_secret",
            region="test-region",
            endpoint="https://test.com"
        )
        print("✓ Successfully created ZOSClient")
        
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            region_name="test-region",
            endpoint_url="https://test.com"
        )
        print("✓ Successfully created ZOSSession")
        
        return True
    except Exception as e:
        print(f"✗ Client creation failed: {e}")
        return False

def test_session_client_creation():
    """Test creating client from session."""
    try:
        from ctyun_zos_sdk import ZOSSession
        
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            region_name="test-region",
            endpoint_url="https://test.com"
        )
        
        client = session.client('s3')
        print("✓ Successfully created client from session")
        
        return True
    except Exception as e:
        print(f"✗ Session client creation failed: {e}")
        return False

def test_unsupported_service():
    """Test that unsupported services raise appropriate error."""
    try:
        from ctyun_zos_sdk import ZOSSession
        
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret"
        )
        
        try:
            session.client('ec2')
            print("✗ Should have raised error for unsupported service")
            return False
        except ValueError as e:
            if "not supported" in str(e):
                print("✓ Correctly raised error for unsupported service")
                return True
            else:
                print(f"✗ Unexpected error message: {e}")
                return False
                
    except Exception as e:
        print(f"✗ Test setup failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running basic functionality tests...\n")
    
    tests = [
        test_imports,
        test_client_creation,
        test_session_client_creation,
        test_unsupported_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Package is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
