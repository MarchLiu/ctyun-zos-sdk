"""Tests for ZOSSession."""

import os
import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ctyun_zos_sdk.session import ZOSSession


class TestZOSSession:
    """Test cases for ZOSSession."""

    def test_init_with_parameters(self):
        """Test session initialization with explicit parameters."""
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            region_name="test-region",
            endpoint_url="https://test.zos.ctyun.cn"
        )
        
        assert session._access_key == "test_key"
        assert session._secret_key == "test_secret"
        assert session._region == "test-region"
        assert session._endpoint == "https://test.zos.ctyun.cn"

    def test_init_with_environment_variables(self):
        """Test session initialization with environment variables."""
        with patch.dict(os.environ, {
            "S3_ACCESS_KEY": "env_key",
            "S3_SECRET_KEY": "env_secret",
            "S3_REGION": "env-region",
            "S3_ENDPOINT": "https://env.zos.ctyun.cn"
        }):
            session = ZOSSession()
            
            assert session._access_key == "env_key"
            assert session._secret_key == "env_secret"
            assert session._region == "env-region"
            assert session._endpoint == "https://env.zos.ctyun.cn"

    def test_init_with_mixed_parameters(self):
        """Test session initialization with mixed parameters and environment variables."""
        with patch.dict(os.environ, {
            "S3_ACCESS_KEY": "env_key",
            "S3_SECRET_KEY": "env_secret"
        }):
            session = ZOSSession(
                region_name="explicit-region",
                endpoint_url="https://explicit.zos.ctyun.cn"
            )
            
            assert session._access_key == "env_key"
            assert session._secret_key == "env_secret"
            assert session._region == "explicit-region"
            assert session._endpoint == "https://explicit.zos.ctyun.cn"

    def test_client_s3_service(self):
        """Test creating S3 client."""
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            region_name="test-region",
            endpoint_url="https://test.zos.ctyun.cn"
        )
        
        with patch('ctyun_zos_sdk.session.ZOSClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            client = session.client('s3')
            
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["access_key"] == "test_key"
            assert call_kwargs["secret_key"] == "test_secret"
            assert call_kwargs["region"] == "test-region"
            assert call_kwargs["endpoint"] == "https://test.zos.ctyun.cn"

    def test_client_unsupported_service(self):
        """Test creating client for unsupported service."""
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret"
        )
        
        with pytest.raises(ValueError, match="Service 'ec2' is not supported"):
            session.client('ec2')

    def test_client_with_additional_kwargs(self):
        """Test creating client with additional configuration."""
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret"
        )
        
        with patch('ctyun_zos_sdk.session.ZOSClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            client = session.client('s3', timeout=60, verify_ssl=False)
            
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["timeout"] == 60
            assert call_kwargs["verify_ssl"] == False

    def test_get_credentials(self):
        """Test getting session credentials."""
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            region_name="test-region",
            endpoint_url="https://test.zos.ctyun.cn"
        )
        
        credentials = session.get_credentials()
        
        assert credentials == {
            "access_key": "test_key",
            "secret_key": "test_secret",
            "region": "test-region",
            "endpoint": "https://test.zos.ctyun.cn"
        }

    def test_client_case_insensitive_service_name(self):
        """Test that service names are case-insensitive."""
        session = ZOSSession(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret"
        )
        
        with patch('ctyun_zos_sdk.session.ZOSClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Should work with uppercase
            client = session.client('S3')
            mock_client_class.assert_called_once()
            
            # Reset mock
            mock_client_class.reset_mock()
            
            # Should work with mixed case
            client = session.client('s3')
            mock_client_class.assert_called_once()
