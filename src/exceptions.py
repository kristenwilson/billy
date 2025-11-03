class BillyError(Exception):
    """Base exception for Billy application errors."""
    pass

class APIError(BillyError):
    """Raised when API calls fail."""
    def __init__(self, message: str, status_code: int = None, response_message: str = None):
        self.status_code = status_code
        self.response_message = response_message
        super().__init__(message)

class UserNotFoundError(APIError):
    """Raised when user doesn't exist in ILLiad."""
    pass

class UserNotClearedError(APIError):
    """Raised when user exists but isn't cleared for requests."""
    pass

class APIAuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass

class TransactionSubmissionError(APIError):
    """Raised when transaction submission fails."""
    pass

# File / validation related exceptions
class FileError(BillyError):
    """Base class for file operation errors."""
    pass

class BillyFileNotFoundError(FileError):
    """Raised when input file is missing."""
    pass

class InvalidFileError(FileError):
    """Raised when file format is invalid (not CSV/RIS or missing required columns)."""
    pass

class EmptyFileError(FileError):
    """Raised when input file is empty."""
    pass

class ValidationError(BillyError):
    """Raised when transaction validation fails."""
    pass

class ConfigError(BillyError):
    """Raised when configuration is invalid or missing."""
    pass