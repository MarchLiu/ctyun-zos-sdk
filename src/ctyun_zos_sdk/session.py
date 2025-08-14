"""Session management for CTyun ZOS SDK."""

import os
from typing import Optional, Dict, Any
from .client import ZOSClient


class ZOSSession:
    """A session stores configuration state and allows you to create service clients."""

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize a ZOS session.
        
        Args:
            aws_access_key_id: Access key ID for authentication
            aws_secret_access_key: Secret access key for authentication
            region_name: AWS region name (used for signing)
            endpoint_url: Custom endpoint URL for ZOS service
            **kwargs: Additional configuration options
        """
        self._access_key = aws_access_key_id or os.environ.get("S3_ACCESS_KEY")
        self._secret_key = aws_secret_access_key or os.environ.get("S3_SECRET_KEY")
        self._region = region_name or os.environ.get("S3_REGION", "huabei-2")
        self._endpoint = endpoint_url or os.environ.get("S3_ENDPOINT", "https://huabei-2.zos.ctyun.cn")
        self._config = kwargs

    def client(self, service_name: str, **kwargs) -> ZOSClient:
        """Create a client for the specified service.
        
        Args:
            service_name: Name of the service (currently only 's3' is supported)
            **kwargs: Additional client configuration
            
        Returns:
            ZOSClient instance
            
        Raises:
            ValueError: If service_name is not 's3'
        """
        if service_name.lower() != "s3":
            raise ValueError(f"Service '{service_name}' is not supported. Only 's3' is supported.")
        
        # Merge session config with client config
        client_config = {
            "access_key": self._access_key,
            "secret_key": self._secret_key,
            "region": self._region,
            "endpoint": self._endpoint,
            **self._config,
            **kwargs
        }
        
        return ZOSClient(**client_config)

    def get_credentials(self) -> Dict[str, str]:
        """Get the current credentials.
        
        Returns:
            Dictionary containing access_key, secret_key, and region
        """
        return {
            "access_key": self._access_key,
            "secret_key": self._secret_key,
            "region": self._region,
            "endpoint": self._endpoint
        }
