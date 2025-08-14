"""Configuration management for CTyun ZOS SDK."""

import os
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for CTyun ZOS SDK."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_file: Optional path to .env file
        """
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        if self.config_file and Path(self.config_file).exists():
            self._load_env_file(self.config_file)
    
    def _load_env_file(self, file_path: str):
        """Load environment variables from .env file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if key and value != 'your_access_key_here':
                            os.environ[key] = value
        except Exception as e:
            print(f"Warning: Could not load config file {file_path}: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return os.environ.get(key, default)
    
    def get_required(self, key: str) -> str:
        """Get required configuration value.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
            
        Raises:
            ValueError: If required configuration is missing
        """
        value = self.get(key)
        if not value:
            raise ValueError(f"Required configuration '{key}' is not set. "
                           f"Please set the {key} environment variable or "
                           f"add it to your .env file.")
        return value
    
    def get_access_key(self) -> str:
        """Get access key from configuration."""
        return self.get_required("S3_ACCESS_KEY")
    
    def get_secret_key(self) -> str:
        """Get secret key from configuration."""
        return self.get_required("S3_SECRET_KEY")
    
    def get_region(self, default: str = "huabei-2") -> str:
        """Get region from configuration."""
        return self.get("S3_REGION", default)
    
    def get_endpoint(self, default: str = "https://huabei-2.zos.ctyun.cn") -> str:
        """Get endpoint from configuration."""
        return self.get("S3_ENDPOINT", default)
    
    def get_bucket(self) -> Optional[str]:
        """Get bucket from configuration."""
        return self.get("S3_BUCKET")
    
    def get_verify_ssl(self, default: bool = True) -> bool:
        """Get SSL verification setting from configuration."""
        value = self.get("S3_VERIFY_SSL", str(default))
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_timeout(self, default: float = 30.0) -> float:
        """Get timeout from configuration."""
        value = self.get("S3_TIMEOUT", str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "access_key": self.get_access_key(),
            "secret_key": self.get_secret_key(),
            "region": self.get_region(),
            "endpoint": self.get_endpoint(),
            "bucket": self.get_bucket(),
            "verify_ssl": self.get_verify_ssl(),
            "timeout": self.get_timeout()
        }
    
    def validate(self) -> bool:
        """Validate that required configuration is present.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If required configuration is missing
        """
        try:
            self.get_access_key()
            self.get_secret_key()
            return True
        except ValueError as e:
            raise ValueError(f"Configuration validation failed: {e}")


def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from file and environment variables.
    
    Args:
        config_file: Optional path to .env file
        
    Returns:
        Config instance
    """
    return Config(config_file)


def get_default_config() -> Config:
    """Get default configuration (from environment variables only)."""
    return Config()
