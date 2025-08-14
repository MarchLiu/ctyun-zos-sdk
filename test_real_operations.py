#!/usr/bin/env python3
"""Real CTyun ZOS operations test script.
This script tests actual file upload, download, and delete operations.
"""

import sys
import os
import tempfile
import hashlib
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_operations():
    """Test real CTyun ZOS operations."""
    try:
        from ctyun_zos_sdk import ZOSSession
        
        print("=== Testing Real CTyun ZOS Operations ===")
        
        # Create session
        session = ZOSSession()
        s3_client = session.client('s3')
        
        # Get bucket name from environment
        bucket_name = os.environ.get("S3_BUCKET", "pq-devel")
        print(f"Using bucket: {bucket_name}")
        
        # Test file operations
        test_key = "sdk-test/test-file.txt"
        test_content = "Hello from CTyun ZOS SDK! This is a test file."
        test_content_bytes = test_content.encode('utf-8')
        
        print(f"\n1. Uploading test file: {test_key}")
        print(f"   Content: {test_content}")
        
        # Upload file
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType="text/plain",
            Metadata={
                "created-by": "ctyun-zos-sdk",
                "test": "true",
                "version": "0.1.0"
            }
        )
        
        print(f"   ✓ Upload successful! ETag: {response['ETag']}")
        
        # Download file
        print(f"\n2. Downloading test file: {test_key}")
        
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=test_key
        )
        
        downloaded_content = response['Body'].decode('utf-8')
        print(f"   ✓ Download successful!")
        print(f"   Content: {downloaded_content}")
        print(f"   Content length: {response['ContentLength']}")
        print(f"   Content type: {response['ContentType']}")
        print(f"   ETag: {response['ETag']}")
        
        # Check metadata
        if response['Metadata']:
            print(f"   Metadata: {response['Metadata']}")
        
        # Verify content
        if downloaded_content == test_content:
            print("   ✓ Content verification passed")
        else:
            print("   ❌ Content verification failed")
            return False
        
        # Delete file
        print(f"\n3. Deleting test file: {test_key}")
        
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=test_key
        )
        
        print(f"   ✓ Delete successful!")
        
        # Verify deletion by trying to download (should fail)
        print(f"\n4. Verifying deletion: {test_key}")
        
        try:
            s3_client.get_object(Bucket=bucket_name, Key=test_key)
            print("   ❌ File still exists after deletion")
            return False
        except Exception as e:
            if "404" in str(e) or "NoSuchKey" in str(e):
                print("   ✓ File successfully deleted")
            else:
                print(f"   ⚠ Unexpected error during verification: {e}")
        
        print("\n🎉 All real operations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Real operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bucket_listing():
    """Test bucket listing operation."""
    try:
        from ctyun_zos_sdk import ZOSSession
        
        print("\n=== Testing Bucket Listing ===")
        
        session = ZOSSession()
        s3_client = session.client('s3')
        
        bucket_name = os.environ.get("S3_BUCKET", "pq-devel")
        
        print(f"Listing objects in bucket: {bucket_name}")
        
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix="sdk-test/",
            MaxKeys=10
        )
        
        print(f"✓ List operation successful")
        print(f"Response metadata: {response['ResponseMetadata']}")
        
        # Note: Contents might be empty if no objects with that prefix
        if 'Contents' in response and response['Contents']:
            print(f"Found {len(response['Contents'])} objects:")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("No objects found with prefix 'sdk-test/'")
        
        return True
        
    except Exception as e:
        print(f"❌ Bucket listing test failed: {e}")
        return False

def main():
    """Main test function."""
    print("CTyun ZOS SDK - Real Operations Test")
    print("=" * 50)
    
    # Check configuration
    required_vars = ['S3_ACCESS_KEY', 'S3_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables and try again.")
        return 1
    
    print("✓ Configuration verified")
    
    # Test real operations
    if not test_real_operations():
        return 1
    
    # Test bucket listing
    if not test_bucket_listing():
        return 1
    
    print("\n🎉 All tests completed successfully!")
    print("The CTyun ZOS SDK is working correctly with real operations!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
