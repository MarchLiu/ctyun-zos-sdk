#!/usr/bin/env python3
"""Asynchronous usage example for CTyun ZOS SDK."""

import asyncio
import os
from ctyun_zos_sdk import AsyncZOSClient


async def async_usage_example():
    """Demonstrate asynchronous usage of the SDK."""
    
    # Create async client
    client = AsyncZOSClient(
        access_key=os.environ.get("S3_ACCESS_KEY"),
        secret_key=os.environ.get("S3_SECRET_KEY"),
        region="huabei-2",
        endpoint="https://huabei-2.zos.ctyun.cn"
    )
    
    # Use async context manager
    async with client:
        bucket_name = "your-bucket"
        object_key = "example/async-test.txt"
        
        try:
            # Upload file asynchronously
            response = await client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body="Async upload test content",
                ContentType="text/plain"
            )
            print(f"Async upload successful! ETag: {response['ETag']}")
            
            # Download file asynchronously
            response = await client.get_object(
                Bucket=bucket_name,
                Key=object_key
            )
            print(f"Async download successful! Content: {response['Body'].decode('utf-8')}")
            
            # Delete file asynchronously
            response = await client.delete_object(
                Bucket=bucket_name,
                Key=object_key
            )
            print("Async delete successful!")
            
        except Exception as e:
            print(f"Error: {e}")


async def concurrent_operations():
    """Demonstrate concurrent operations."""
    
    client = AsyncZOSClient(
        access_key=os.environ.get("S3_ACCESS_KEY"),
        secret_key=os.environ.get("S3_SECRET_KEY"),
        region="huabei-2",
        endpoint="https://huabei-2.zos.ctyun.cn"
    )
    
    async with client:
        bucket_name = "your-bucket"
        
        # Create multiple upload tasks
        upload_tasks = []
        for i in range(5):
            task = client.put_object(
                Bucket=bucket_name,
                Key=f"concurrent/test-{i}.txt",
                Body=f"Content for file {i}",
                ContentType="text/plain"
            )
            upload_tasks.append(task)
        
        try:
            # Execute all uploads concurrently
            results = await asyncio.gather(*upload_tasks)
            print(f"Concurrent uploads completed! {len(results)} files uploaded.")
            
            # Clean up - delete all files concurrently
            delete_tasks = []
            for i in range(5):
                task = client.delete_object(
                    Bucket=bucket_name,
                    Key=f"concurrent/test-{i}.txt"
                )
                delete_tasks.append(task)
            
            await asyncio.gather(*delete_tasks)
            print("Concurrent deletes completed!")
            
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main async function."""
    print("=== Async Usage Example ===")
    await async_usage_example()
    
    print("\n=== Concurrent Operations Example ===")
    await concurrent_operations()


if __name__ == "__main__":
    asyncio.run(main())
