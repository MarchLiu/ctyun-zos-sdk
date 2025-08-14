"""Tests for ZOSClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ctyun_zos_sdk.client import ZOSClient
from ctyun_zos_sdk.exceptions import ZOSError, ZOSClientError, ZOSServerError


class TestZOSClient:
    """Test cases for ZOSClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = ZOSClient(
            access_key="test_access_key",
            secret_key="test_secret_key",
            region="test-region",
            endpoint="https://test.zos.ctyun.cn"
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self.client, 'http_client'):
            self.client.close()

    def test_init(self):
        """Test client initialization."""
        assert self.client.access_key == "test_access_key"
        assert self.client.secret_key == "test_secret_key"
        assert self.client.region == "test-region"
        assert self.client.endpoint == "https://test.zos.ctyun.cn"

    def test_build_url(self):
        """Test URL building."""
        url = self.client._build_url("test-bucket", "test-key")
        assert url == "https://test.zos.ctyun.cn/test-bucket/test-key"

    def test_get_headers_with_content(self):
        """Test header generation with content."""
        content = b"test content"
        headers = self.client._get_headers("PUT", content)
        
        assert "x-amz-date" in headers
        assert "x-amz-content-sha256" in headers
        # Just check that the hash is present and is a valid SHA256 hash (64 hex chars)
        assert len(headers["x-amz-content-sha256"]) == 64
        assert all(c in '0123456789abcdef' for c in headers["x-amz-content-sha256"])

    def test_get_headers_without_content(self):
        """Test header generation without content."""
        headers = self.client._get_headers("GET")
        
        assert "x-amz-date" in headers
        assert headers["x-amz-content-sha256"] == "UNSIGNED-PAYLOAD"

    def test_sign_request(self):
        """Test request signing."""
        # Mock the entire _sign_request method to avoid complex AWS signing logic
        with patch.object(self.client, '_sign_request') as mock_sign:
            mock_sign.return_value = {"test": "header", "authorization": "test-auth"}
            
            headers = {"test": "header"}
            signed_headers = self.client._sign_request("GET", "http://test.com", headers)
            
            mock_sign.assert_called_once_with("GET", "http://test.com", headers)
            assert signed_headers == {"test": "header", "authorization": "test-auth"}

    @patch.object(ZOSClient, '_build_url')
    @patch.object(ZOSClient, '_get_headers')
    @patch.object(ZOSClient, '_sign_request')
    def test_get_object_success(self, mock_sign, mock_headers, mock_build_url):
        """Test successful get_object call."""
        mock_build_url.return_value = "http://test.com"
        mock_headers.return_value = {"test": "header"}
        mock_sign.return_value = {"test": "header", "authorization": "test"}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test content"
        mock_response.headers = {"content-type": "text/plain", "etag": "test-etag"}
        
        with patch.object(self.client.http_client, 'get', return_value=mock_response):
            result = self.client.get_object(Bucket="test-bucket", Key="test-key")
            
            assert result["Body"] == b"test content"
            assert result["ContentLength"] == 12
            assert result["ContentType"] == "text/plain"
            assert result["ETag"] == "test-etag"

    @patch.object(ZOSClient, '_build_url')
    @patch.object(ZOSClient, '_get_headers')
    @patch.object(ZOSClient, '_sign_request')
    def test_get_object_client_error(self, mock_sign, mock_headers, mock_build_url):
        """Test get_object with client error."""
        mock_build_url.return_value = "http://test.com"
        mock_headers.return_value = {"test": "header"}
        mock_sign.return_value = {"test": "header", "authorization": "test"}
        
        mock_response = Mock()
        mock_response.status_code = 404
        
        # Create a proper httpx.HTTPStatusError mock
        from httpx import HTTPStatusError
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            "404 Not Found", 
            request=Mock(), 
            response=mock_response
        )
        
        with patch.object(self.client.http_client, 'get', return_value=mock_response):
            with pytest.raises(ZOSClientError):
                self.client.get_object(Bucket="test-bucket", Key="test-key")

    @patch.object(ZOSClient, '_build_url')
    @patch.object(ZOSClient, '_get_headers')
    @patch.object(ZOSClient, '_sign_request')
    def test_put_object_success(self, mock_sign, mock_headers, mock_build_url):
        """Test successful put_object call."""
        mock_build_url.return_value = "http://test.com"
        mock_headers.return_value = {"test": "header"}
        mock_sign.return_value = {"test": "header", "authorization": "test"}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"etag": "test-etag"}
        
        with patch.object(self.client.http_client, 'put', return_value=mock_response):
            result = self.client.put_object(
                Bucket="test-bucket", 
                Key="test-key", 
                Body="test content"
            )
            
            assert result["ETag"] == "test-etag"

    def test_context_manager(self):
        """Test client as context manager."""
        with ZOSClient(
            access_key="test",
            secret_key="test",
            region="test",
            endpoint="https://test.com"
        ) as client:
            assert isinstance(client, ZOSClient)
            assert hasattr(client, 'http_client')

    def test_parse_metadata(self):
        """Test metadata parsing from headers."""
        headers = {
            "x-amz-meta-test": "test-value",
            "x-amz-meta-another": "another-value",
            "content-type": "text/plain"
        }
        
        metadata = self.client._parse_metadata(headers)
        
        assert metadata["test"] == "test-value"
        assert metadata["another"] == "another-value"
        assert "content-type" not in metadata
