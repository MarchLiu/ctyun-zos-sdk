#!/usr/bin/env python3
"""Async CTyun ZOS operations test script."""

import sys
import os
import asyncio

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_async_operations():
    """Test async CTyun ZOS operations."""
    try:
        from ctyun_zos_sdk import AsyncZOSClient
        
        print("=== Testing Async CTyun ZOS Operations ===")
        
        # Create async client
        client = AsyncZOSClient(
            access_key=os.environ["S3_ACCESS_KEY"],
            secret_key=os.environ["S3_SECRET_KEY"],
            region=os.environ.get("S3_REGION", "huabei-2"),
            endpoint=os.environ.get("S3_ENDPOINT", "https://huabei-2.zos.ctyun.cn")
        )
        
        bucket_name = os.environ.get("S3_BUCKET", "pq-devel")
        print(f"Using bucket: {bucket_name}")
        
        async with client:
            # Test file operations
            test_key = "sdk-test/async-test-file.txt"
            test_content = "Hello from Async CTyun ZOS SDK!"
            
            print(f"\n1. Async uploading test file: {test_key}")
            
            # Upload file
            response = await client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType="text/plain",
                Metadata={
                    "created-by": "ctyun-zos-sdk-async",
                    "test": "true"
                }
            )
            
            print(f"   ✓ Async upload successful! ETag: {response['ETag']}")
            
            # Download file
            print(f"\n2. Async downloading test file: {test_key}")
            
            response = await client.get_object(
                Bucket=bucket_name,
                Key=test_key
            )
            
            downloaded_content = response['Body'].decode('utf-8')
            print(f"   ✓ Async download successful!")
            print(f"   Content: {downloaded_content}")
            print(f"   Content length: {response['ContentLength']}")
            
            # Verify content
            if downloaded_content == test_content:
                print("   ✓ Content verification passed")
            else:
                print("   ❌ Content verification failed")
                return False
            
            # Delete file
            print(f"\n3. Async deleting test file: {test_key}")
            
            response = await client.delete_object(
                Bucket=bucket_name,
                Key=test_key
            )
            
            print(f"   ✓ Async delete successful!")
            
            # Verify deletion
            print(f"\n4. Verifying async deletion: {test_key}")
            
            try:
                await client.get_object(Bucket=bucket_name, Key=test_key)
                print("   ❌ File still exists after deletion")
                return False
            except Exception as e:
                if "404" in str(e) or "NoSuchKey" in str(e):
                    print("   ✓ File successfully deleted")
                else:
                    print(f"   ⚠ Unexpected error during verification: {e}")
        
        print("\n🎉 All async operations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Async operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_concurrent_operations():
    """Test concurrent async operations."""
    try:
        from ctyun_zos_sdk import AsyncZOSClient
        
        print("\n=== Testing Concurrent Async Operations ===")
        
        client = AsyncZOSClient(
            access_key=os.environ["S3_ACCESS_KEY"],
            secret_key=os.environ["S3_SECRET_KEY"],
            region=os.environ.get("S3_REGION", "huabei-2"),
            endpoint=os.environ.get("S3_ENDPOINT", "https://huabei-2.zos.ctyun.cn")
        )
        
        bucket_name = os.environ.get("S3_BUCKET", "pq-devel")
        
        async with client:
            # Create multiple upload tasks
            upload_tasks = []
            for i in range(3):
                task = client.put_object(
                    Bucket=bucket_name,
                    Key=f"sdk-test/concurrent-test-{i}.txt",
                    Body=f"Concurrent test content {i}",
                    ContentType="text/plain"
                )
                upload_tasks.append(task)
            
            print("Uploading 3 files concurrently...")
            
            # Execute all uploads concurrently
            results = await asyncio.gather(*upload_tasks)
            print(f"✓ Concurrent uploads completed! {len(results)} files uploaded.")
            
            # Clean up - delete all files concurrently
            delete_tasks = []
            for i in range(3):
                task = client.delete_object(
                    Bucket=bucket_name,
                    Key=f"sdk-test/concurrent-test-{i}.txt"
                )
                delete_tasks.append(task)
            
            await asyncio.gather(*delete_tasks)
            print("✓ Concurrent deletes completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Concurrent operations test failed: {e}")
        return False

async def main():
    """Main async test function."""
    print("CTyun ZOS SDK - Async Operations Test")
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
    
    # Test async operations
    if not await test_async_operations():
        return 1
    
    # Test concurrent operations
    if not await test_concurrent_operations():
        return 1
    
    print("\n🎉 All async tests completed successfully!")
    print("The Async CTyun ZOS SDK is working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
