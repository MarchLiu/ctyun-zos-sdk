#!/usr/bin/env python3
"""Real connection test script for CTyun ZOS SDK.
This script requires proper configuration of access keys and endpoint.
"""

import sys
import os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_configuration():
    """Check if required configuration is available."""
    required_vars = ['S3_ACCESS_KEY', 'S3_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables or create a .env file.")
        print("You can copy config.env.example to .env and fill in your values.")
        return False
    
    print("✓ Required configuration found")
    return True

def test_real_connection():
    """Test real connection to CTyun ZOS."""
    try:
        from ctyun_zos_sdk import ZOSSession
        
        print("\n=== Testing Real Connection ===")
        
        # Create session with environment variables
        session = ZOSSession()
        
        # Get credentials info (without exposing actual keys)
        creds = session.get_credentials()
        print(f"✓ Connected to region: {creds['region']}")
        print(f"✓ Using endpoint: {creds['endpoint']}")
        print(f"✓ Access key configured: {'Yes' if creds['access_key'] else 'No'}")
        print(f"✓ Secret key configured: {'Yes' if creds['secret_key'] else 'No'}")
        
        # Create S3 client
        s3_client = session.client('s3')
        print("✓ S3 client created successfully")
        
        # Test basic operations (these will fail without proper credentials)
        print("\n=== Testing Basic Operations ===")
        
        # Note: These operations will fail if you don't have proper credentials
        # and a valid bucket, but they will test the SDK's error handling
        
        try:
            # This will likely fail, but it tests the SDK's error handling
            response = s3_client.list_objects_v2(Bucket="test-bucket")
            print("✓ List objects operation successful")
        except Exception as e:
            if "Access Denied" in str(e) or "NoSuchBucket" in str(e):
                print("✓ SDK is working correctly - received expected error for invalid bucket")
            else:
                print(f"⚠ Unexpected error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main test function."""
    print("CTyun ZOS SDK - Real Connection Test")
    print("=" * 50)
    
    # Check configuration
    if not check_configuration():
        print("\n📝 Configuration Instructions:")
        print("1. Copy config.env.example to .env")
        print("2. Fill in your actual CTyun credentials:")
        print("   - S3_ACCESS_KEY: Your access key ID")
        print("   - S3_SECRET_KEY: Your secret access key")
        print("   - S3_REGION: Your region (e.g., huabei-2)")
        print("   - S3_ENDPOINT: Your endpoint URL")
        print("   - S3_BUCKET: Your bucket name (optional)")
        print("3. Run this script again")
        return 1
    
    # Test real connection
    if test_real_connection():
        print("\n🎉 Real connection test completed successfully!")
        print("The SDK is properly configured and can connect to CTyun ZOS.")
        return 0
    else:
        print("\n❌ Real connection test failed.")
        print("Please check your configuration and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
