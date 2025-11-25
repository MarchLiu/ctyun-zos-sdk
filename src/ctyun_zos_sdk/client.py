"""Main client for CTyun ZOS SDK."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union, BinaryIO, Generator
from urllib.parse import urlparse

import httpx
from botocore.awsrequest import AWSRequest
from botocore.auth import SigV4Auth
from botocore.credentials import Credentials

from .exceptions import ZOSError, ZOSClientError, ZOSServerError


class ZOSClient:
    """Client for interacting with CTyun Object Storage (ZOS)."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        endpoint: str,
        verify_ssl: bool = True,
        timeout: float = 30.0,
        **kwargs
    ):
        """Initialize the ZOS client.
        
        Args:
            access_key: Access key ID for authentication
            secret_key: Secret access key for authentication
            region: AWS region name (used for signing)
            endpoint: ZOS service endpoint URL
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
            **kwargs: Additional configuration options
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.endpoint = endpoint.rstrip('/')
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
        # Create credentials and auth objects
        self.credentials = Credentials(access_key, secret_key)
        self.auth = SigV4Auth(self.credentials, "s3", region)
        
        # Create httpx client
        self.http_client = httpx.Client(
            verify=verify_ssl,
            timeout=timeout,
            **kwargs
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        if hasattr(self, 'http_client'):
            self.http_client.close()

    def _build_url(self, bucket: str, key: str) -> str:
        """Build the full URL for an S3 operation.
        
        Args:
            bucket: Bucket name
            key: Object key
            
        Returns:
            Full URL for the operation
        """
        return f"{self.endpoint}/{bucket}/{key}"

    def _get_headers(self, method: str, content: Optional[bytes] = None, **kwargs) -> Dict[str, str]:
        """Generate headers for an S3 request.
        
        Args:
            method: HTTP method
            content: Request content for calculating SHA256
            **kwargs: Additional headers
            
        Returns:
            Dictionary of headers
        """
        headers = {
            "x-amz-date": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            **kwargs
        }
        
        if content:
            # Calculate SHA256 hash for signed payloads
            sha256_hash = hashlib.sha256(content).hexdigest()
            headers["x-amz-content-sha256"] = sha256_hash
        else:
            # Use UNSIGNED-PAYLOAD for requests without body (like GET)
            headers["x-amz-content-sha256"] = "UNSIGNED-PAYLOAD"
            
        return headers

    def _sign_request(self, method: str, url: str, headers: Dict[str, str], data: Optional[bytes] = None) -> Dict[str, str]:
        """Sign the request using AWS SigV4.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            data: Request data
            
        Returns:
            Signed headers
        """
        request = AWSRequest(
            method=method,
            url=url,
            data=data,
            headers=headers
        )
        
        self.auth.add_auth(request)
        return dict(request.headers)

    def get_object(self, Bucket: str, Key: str, **kwargs) -> Dict[str, Any]:
        """Get an object from S3.
        
        Args:
            Bucket: Bucket name
            Key: Object key
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary containing the object data
            
        Raises:
            ZOSError: If the request fails
        """
        url = self._build_url(Bucket, Key)
        headers = self._get_headers("GET")
        if "Range" in kwargs:
            headers["Range"] = kwargs["Range"]
        signed_headers = self._sign_request("GET", url, headers)
        
        try:
            response = self.http_client.get(url, headers=signed_headers)
            response.raise_for_status()
            
            result = {
                "Body": response.content,
                "ContentLength": len(response.content),
                "ContentType": response.headers.get("content-type"),
                "ETag": response.headers.get("etag"),
                "LastModified": response.headers.get("last-modified"),
                "Metadata": self._parse_metadata(response.headers),
                "ResponseMetadata": {
                    "HTTPStatusCode": response.status_code,
                    "HTTPHeaders": dict(response.headers)
                }
            }
            if "Range" in kwargs:
                result["ContentLength"] = int(result.get("content-length", result.get("Content-Length")))
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise ZOSServerError(f"Server error: {e.response.status_code}") from e
            else:
                raise ZOSClientError(f"Client error: {e.response.status_code}") from e
        except Exception as e:
            raise ZOSError(f"Request failed: {str(e)}") from e

            
    def head_object(self, Bucket: str, Key: str, **kwargs) -> Dict[str, Any]:
        """Get an object Header from S3 asynchronously.
        
        Args:
            Bucket: Bucket name
            Key: Object key
            **kwargs: Additional parameters
        """
        url = self._build_url(Bucket, Key)
        headers = self._get_headers("HEAD")
        if "Range" in kwargs:
            headers["Range"] = kwargs["Range"]
        signed_headers = self._sign_request("HEAD", url, headers)
        response = self.http_client.head(url, headers=signed_headers)
        return response.headers

    def put_object(self, Bucket: str, Key: str, Body: Union[str, bytes, BinaryIO], **kwargs) -> Dict[str, Any]:
        """Put an object to S3.
        
        Args:
            Bucket: Bucket name
            Key: Object key
            Body: Object content
            **kwargs: Additional parameters (ContentType, Metadata, etc.)
            
        Returns:
            Response dictionary
            
        Raises:
            ZOSError: If the request fails
        """
        url = self._build_url(Bucket, Key)
        
        # Convert body to bytes
        if isinstance(Body, str):
            body_bytes = Body.encode('utf-8')
        elif isinstance(Body, bytes):
            body_bytes = Body
        elif hasattr(Body, 'read'):
            body_bytes = Body.read()
        else:
            body_bytes = str(Body).encode('utf-8')
        
        # Prepare headers
        headers = self._get_headers("PUT", body_bytes)
        if "ContentType" in kwargs:
            headers["Content-Type"] = kwargs["ContentType"]
        
        # Add metadata headers
        metadata = kwargs.get("Metadata", {})
        for key, value in metadata.items():
            headers[f"x-amz-meta-{key.lower()}"] = value
        
        signed_headers = self._sign_request("PUT", url, headers, body_bytes)
        
        try:
            response = self.http_client.put(url, content=body_bytes, headers=signed_headers)
            response.raise_for_status()
            
            return {
                "ETag": response.headers.get("etag"),
                "ResponseMetadata": {
                    "HTTPStatusCode": response.status_code,
                    "HTTPHeaders": dict(response.headers)
                }
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise ZOSServerError(f"Server error: {e.response.status_code}") from e
            else:
                raise ZOSClientError(f"Client error: {e.response.status_code}") from e
        except Exception as e:
            raise ZOSError(f"Request failed: {str(e)}") from e

    def delete_object(self, Bucket: str, Key: str, **kwargs) -> Dict[str, Any]:
        """Delete an object from S3.
        
        Args:
            Bucket: Bucket name
            Key: Object key
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
            
        Raises:
            ZOSError: If the request fails
        """
        url = self._build_url(Bucket, Key)
        headers = self._get_headers("DELETE")
        signed_headers = self._sign_request("DELETE", url, headers)
        
        try:
            response = self.http_client.delete(url, headers=signed_headers)
            response.raise_for_status()
            
            return {
                "ResponseMetadata": {
                    "HTTPStatusCode": response.status_code,
                    "HTTPHeaders": dict(response.headers)
                }
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise ZOSServerError(f"Server error: {e.response.status_code}") from e
            else:
                raise ZOSClientError(f"Client error: {e.response.status_code}") from e
        except Exception as e:
            raise ZOSError(f"Request failed: {str(e)}") from e

    def list_objects_v2(self, Bucket: str, Prefix: str = "", **kwargs) -> Dict[str, Any]:
        """List objects in a bucket.
        
        Args:
            Bucket: Bucket name
            Prefix: Object key prefix
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary containing object list
            
        Raises:
            ZOSError: If the request fails
        """
        # Build query parameters
        params = {}
        if Prefix:
            params["prefix"] = Prefix
        if "MaxKeys" in kwargs:
            params["max-keys"] = str(kwargs["MaxKeys"])
        if "ContinuationToken" in kwargs:
            params["continuation-token"] = kwargs["ContinuationToken"]
        
        # Build URL with query parameters
        base_url = f"{self.endpoint}/{Bucket}"
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{base_url}?{query_string}"
        else:
            url = base_url
        
        headers = self._get_headers("GET")
        signed_headers = self._sign_request("GET", url, headers)
        
        try:
            response = self.http_client.get(url, headers=signed_headers)
            response.raise_for_status()
            
            # Parse XML response (simplified)
            content = response.text
            # In a real implementation, you'd parse the XML properly
            # For now, return a basic structure
            
            return {
                "Contents": [],  # Would contain parsed object info
                "ResponseMetadata": {
                    "HTTPStatusCode": response.status_code,
                    "HTTPHeaders": dict(response.headers)
                }
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise ZOSServerError(f"Server error: {e.response.status_code}") from e
            else:
                raise ZOSClientError(f"Client error: {e.response.status_code}") from e
        except Exception as e:
            raise ZOSError(f"Request failed: {str(e)}") from e

    def _parse_metadata(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Parse metadata from response headers.
        
        Args:
            headers: Response headers
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        for key, value in headers.items():
            if key.lower().startswith("x-amz-meta-"):
                metadata_key = key[11:]  # Remove "x-amz-meta-" prefix
                metadata[metadata_key] = value
        return metadata

    def put_access_policy(self, Bucket: str, key: str, Policy: str, **kwargs) -> Dict[str, Any]:
        """Set object ACL synchronously.

        Supports both canned ACLs via the ``x-amz-acl`` header and full ACL
        policies by sending the ACL XML in the request body.

        Args:
            Bucket: Bucket name
            key: Object key
            Policy: Either a canned ACL name (e.g. "private", "public-read")
                or a full ACL XML string per S3 ``PutObjectAcl``.
            **kwargs: Additional parameters
        """
        # Target the ACL subresource
        url = f"{self._build_url(Bucket, key)}?acl"

        # Determine whether this is a canned ACL or a full ACL XML
        canned_acls = {
            "private",
            "public-read",
            "public-read-write",
            "authenticated-read",
            "bucket-owner-read",
            "bucket-owner-full-control",
            "log-delivery-write",
        }

        is_canned = Policy in canned_acls
        body_bytes = None if is_canned else Policy.encode("utf-8")

        # Prepare headers; attach x-amz-acl for canned ACL
        headers = self._get_headers("PUT", body_bytes)
        if is_canned:
            headers["x-amz-acl"] = Policy

        signed_headers = self._sign_request("PUT", url, headers, body_bytes)

        try:
            response = self.http_client.put(
                url,
                headers=signed_headers,
                content=b"" if body_bytes is None else body_bytes,
            )
            response.raise_for_status()
            return {
                "ResponseMetadata": {
                    "HTTPStatusCode": response.status_code,
                    "HTTPHeaders": dict(response.headers),
                }
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise ZOSServerError(f"Server error: {e.response.status_code}") from e
            else:
                raise ZOSClientError(f"Client error: {e.response.status_code}") from e
        except Exception as e:
            raise ZOSError(f"Request failed: {str(e)}") from e

    def get_access_policy(self, Bucket: str, key: str, **kwargs) -> Dict[str, Any]:
        """Get object ACL (``?acl``) synchronously.

        Returns the raw ACL XML in ``Body`` along with response metadata.

        Args:
            Bucket: Bucket name
            key: Object key
            **kwargs: Additional parameters
        """
        url = f"{self._build_url(Bucket, key)}?acl"
        headers = self._get_headers("GET")
        signed_headers = self._sign_request("GET", url, headers)
        try:
            response = self.http_client.get(url, headers=signed_headers)
            response.raise_for_status()
            return {
                "Body": response.text,
                "ResponseMetadata": {
                    "HTTPStatusCode": response.status_code,
                    "HTTPHeaders": dict(response.headers),
                }
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise ZOSServerError(f"Server error: {e.response.status_code}") from e
            else:
                raise ZOSClientError(f"Client error: {e.response.status_code}") from e
        except Exception as e:
            raise ZOSError(f"Request failed: {str(e)}") from e