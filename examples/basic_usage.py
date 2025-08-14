#!/usr/bin/env python3
"""Basic usage example for CTyun ZOS SDK."""

import os
from ctyun_zos_sdk import ZOSSession, ZOSClient


def basic_usage_example():
    """Demonstrate basic usage of the SDK."""
    
    # Method 1: Using ZOSSession (recommended)
    session = ZOSSession(
        aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
        region_name="huabei-2",
        endpoint_url="https://huabei-2.zos.ctyun.cn"
    )
    
    s3_client = session.client('s3')
    
    # Upload a file
    bucket_name = "your-bucket"
    object_key = "example/test.txt"
    content = "Hello, CTyun ZOS!"
    
    try:
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=content,
            ContentType="text/plain"
        )
        print(f"Upload successful! ETag: {response['ETag']}")
        
        # Download the file
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key
        )
        print(f"Downloaded content: {response['Body'].decode('utf-8')}")
        
        # Delete the file
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=object_key
        )
        print("File deleted successfully!")
        
    except Exception as e:
        print(f"Error: {e}")


def direct_client_usage():
    """Demonstrate direct client usage."""
    
    # Method 2: Direct client instantiation
    client = ZOSClient(
        access_key=os.environ.get("S3_ACCESS_KEY"),
        secret_key=os.environ.get("S3_SECRET_KEY"),
        region="huabei-2",
        endpoint="https://huabei-2.zos.ctyun.cn"
    )
    
    # Use context manager for automatic cleanup
    with client:
        bucket_name = "your-bucket"
        object_key = "example/direct-usage.txt"
        
        try:
            # Upload with metadata
            response = client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body="Direct client usage example",
                ContentType="text/plain",
                Metadata={
                    "created-by": "ctyun-zos-sdk",
                    "example": "true"
                }
            )
            print(f"Upload successful! ETag: {response['ETag']}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("=== Basic Usage Example ===")
    basic_usage_example()
    
    print("\n=== Direct Client Usage Example ===")
    direct_client_usage()
