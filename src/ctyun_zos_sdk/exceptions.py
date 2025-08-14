"""Exception classes for CTyun ZOS SDK."""


class ZOSError(Exception):
    """Base exception for CTyun ZOS SDK."""
    pass


class ZOSClientError(ZOSError):
    """Exception raised when a client-side error occurs."""
    pass


class ZOSServerError(ZOSError):
    """Exception raised when a server-side error occurs."""
    pass
