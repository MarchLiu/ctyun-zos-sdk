# CTyun ZOS SDK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-ctyun--zos--sdk-blue.svg)](https://pypi.org/project/ctyun-zos-sdk/)

A boto3-compatible SDK for CTyun Object Storage (ZOS) with httpx backend. This SDK provides both synchronous and asynchronous interfaces for interacting with CTyun's S3-compatible object storage service.

## Features

- **boto3-compatible API**: Familiar interface for developers already using AWS S3
- **Dual interfaces**: Both synchronous and asynchronous clients
- **httpx backend**: Modern HTTP client with better performance and features
- **CTyun-specific optimizations**: Handles CTyun ZOS service requirements
- **Proper signing**: AWS SigV4 authentication with CTyun-specific header handling
- **Type hints**: Full type annotations for better development experience

## Installation

### From PyPI (recommended)

```bash
pip install ctyun-zos-sdk
```

### From source

```bash
git clone https://github.com/your-org/ctyun-zos-sdk.git
cd ctyun-zos-sdk
pip install -e .
```

## Quick Start

### Basic Usage

```python
import os
from ctyun_zos_sdk import ZOSSession

# Create a session
session = ZOSSession(
    aws_access_key_id=os.environ["S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET_KEY"],
    region_name="huabei-2",
    endpoint_url="https://huabei-2.zos.ctyun.cn"
)

# Get S3 client
s3_client = session.client('s3')

# Upload a file
response = s3_client.put_object(
    Bucket="your-bucket",
    Key="example/test.txt",
    Body="Hello, CTyun ZOS!",
    ContentType="text/plain"
)
print(f"Upload successful! ETag: {response['ETag']}")

# Download a file
response = s3_client.get_object(
    Bucket="your-bucket",
    Key="example/test.txt"
)
print(f"Content: {response['Body'].decode('utf-8')}")
```

### Asynchronous Usage

```python
import asyncio
import os
from ctyun_zos_sdk import AsyncZOSClient

async def main():
    async with AsyncZOSClient(
        access_key=os.environ["S3_ACCESS_KEY"],
        secret_key=os.environ["S3_SECRET_KEY"],
        region="huabei-2",
        endpoint="https://huabei-2.zos.ctyun.cn"
    ) as client:
        
        # Upload file asynchronously
        response = await client.put_object(
            Bucket="your-bucket",
            Key="async-test.txt",
            Body="Async upload content"
        )
        print(f"Upload successful! ETag: {response['ETag']}")

# Run the async function
asyncio.run(main())
```

### Direct Client Usage

```python
from ctyun_zos_sdk import ZOSClient

# Create client directly
client = ZOSClient(
    access_key="your_access_key",
    secret_key="your_secret_key",
    region="huabei-2",
    endpoint="https://huabei-2.zos.ctyun.cn"
)

# Use context manager for automatic cleanup
with client:
    response = client.put_object(
        Bucket="your-bucket",
        Key="direct-test.txt",
        Body="Direct client usage"
    )
    print(f"Upload successful! ETag: {response['ETag']}")
```

## Configuration

### Environment Variables

You can configure the SDK using environment variables:

```bash
export S3_ACCESS_KEY="your_access_key"
export S3_SECRET_KEY="your_secret_key"
export S3_REGION="huabei-2"
export S3_ENDPOINT="https://huabei-2.zos.ctyun.cn"
```

### Supported Regions

- `huabei-2` - 华北2
- `huadong-1` - 华东1
- `huadong-2` - 华东2
- `huanan-1` - 华南1
- `huanan-2` - 华南2

## API Reference

### ZOSSession

The main session class for managing configuration and creating clients.

```python
session = ZOSSession(
    aws_access_key_id="your_key",
    aws_secret_access_key="your_secret",
    region_name="huabei-2",
    endpoint_url="https://huabei-2.zos.ctyun.cn"
)

# Create S3 client
s3_client = session.client('s3')
```

### ZOSClient

Synchronous client for S3 operations.

#### Methods

- `get_object(Bucket, Key, **kwargs)` - Download an object
- `put_object(Bucket, Key, Body, **kwargs)` - Upload an object
- `delete_object(Bucket, Key, **kwargs)` - Delete an object
- `list_objects_v2(Bucket, Prefix="", **kwargs)` - List objects in a bucket

#### Parameters

- `Bucket` (str): Bucket name
- `Key` (str): Object key
- `Body` (str/bytes/file): Object content for uploads
- `ContentType` (str): MIME type of the object
- `Metadata` (dict): Custom metadata for the object

### AsyncZOSClient

Asynchronous client with the same interface as ZOSClient.

```python
async with AsyncZOSClient(...) as client:
    response = await client.put_object(...)
    response = await client.get_object(...)
```

## Examples

See the `examples/` directory for more detailed examples:

- `examples/basic_usage.py` - Basic synchronous operations
- `examples/async_usage.py` - Asynchronous operations and concurrency

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/ctyun-zos-sdk.git
cd ctyun-zos-sdk

# Install development dependencies
make install-dev

# Install package in development mode
make dev-install
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run linting checks
make lint

# Format code
make format
```

### Building and Publishing

```bash
# Build package
make build

# Check package metadata
make check

# Upload to test PyPI
make upload-test

# Upload to PyPI
make upload
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on the verified examples in the `verified/` directory
- Uses boto3's authentication and signing mechanisms
- Built with httpx for modern HTTP client capabilities

## Support

For issues and questions:

- Create an issue on GitHub
- Check the examples in the `examples/` directory
- Review the verified examples in the `verified/` directory
