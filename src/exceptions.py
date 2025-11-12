"""
exceptions.py - Custom exception classes for Billy application.

This module defines a hierarchy of domain-specific exceptions used throughout Billy.
All exceptions inherit from BillyError, allowing callers to catch application-level
errors separately from unexpected exceptions.

Exception hierarchy:
- BillyError (base)
  - APIError (API/network failures)
    - APIAuthenticationError (401 - invalid credentials)
    - UserNotFoundError (404 - user doesn't exist)
    - UserNotClearedError (user exists but not authorized)
    - TransactionSubmissionError (submission failed)
  - FileError (file operation failures)
    - BillyFileNotFoundError (missing or unreadable file)
    - InvalidFileError (bad format or missing columns)
    - EmptyFileError (file has no content)
  - ValidationError (transaction validation failed)
  - ConfigError (configuration missing/invalid)

Notes:
- APIError subclasses optionally store status_code and response_message for context.
- Granular exception types allow main() to map errors to specific exit codes.
- All exceptions preserve original context via "raise ... from e" in callers.

Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu
Editor: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

from typing import Optional


class BillyError(Exception):
    """
    Base exception for all Billy application errors.

    This is the top-level exception class. Catching BillyError allows callers to
    distinguish application-level errors from unexpected Python exceptions.
    """

    pass


class APIError(BillyError):
    """
    Raised when ILLiad API calls fail.

    This is the base class for all API-related errors. Subclasses provide more
    specific error types (authentication, not found, etc.) for granular handling.

    Attributes:
        status_code: HTTP status code from the API response (if available).
        response_message: The server's error message from the response body (if available).
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_message: Optional[str] = None,
    ) -> None:
        """
        Initialize an APIError with optional HTTP context.

        Args:
            message: Human-readable error message for the user.
            status_code: HTTP status code (e.g., 500). Optional.
            response_message: Server response body message. Optional.
        """
        self.status_code = status_code
        self.response_message = response_message
        super().__init__(message)


class APIAuthenticationError(APIError):
    """
    Raised when API authentication fails (HTTP 401).

    This occurs when the API key is invalid, expired, or missing.
    The user should check their config (.env) and API credentials.
    """

    pass


class UserNotFoundError(APIError):
    """
    Raised when a user does not exist in ILLiad (HTTP 404).

    This occurs when check_user queries for an email address that has no
    corresponding ILLiad account. The user should verify the email address
    or create an account in ILLiad.
    """

    pass


class UserNotClearedError(APIError):
    """
    Raised when a user exists in ILLiad but is not cleared to place requests.

    This occurs when the user's "Cleared" status is "No" in ILLiad.
    An ILLiad administrator must approve the user before they can request materials.
    """

    pass


class TransactionSubmissionError(APIError):
    """
    Raised when a transaction submission to ILLiad fails.

    This occurs when the API returns a server error (5xx) or when network/connection
    issues prevent the request from reaching the server. Client errors (4xx) are
    returned as error strings instead to allow per-entry error recording.
    """

    pass


class FileError(BillyError):
    """
    Base exception for file operation errors.

    This is the parent class for all file-related failures (missing files,
    invalid formats, etc.). Catching FileError allows callers to handle all
    file issues uniformly.
    """

    pass


class BillyFileNotFoundError(FileError):
    """
    Raised when an input file is missing or cannot be read.

    This occurs when:
    - The file does not exist in DATA_FILES_DIR.
    - The file exists but cannot be opened due to permissions or encoding issues.

    The user should verify the filename and file permissions.
    """

    pass


class InvalidFileError(FileError):
    """
    Raised when an input file format is invalid or missing required columns.

    This occurs when:
    - The file is neither CSV nor RIS format.
    - A CSV file is missing required columns (e.g., "Item Type").
    - The file is corrupted or malformed (CSV parsing fails).

    The user should verify the file format and contents.
    """

    pass


class EmptyFileError(FileError):
    """
    Raised when an input file contains no content.

    This occurs when a file exists but is empty (0 bytes) or contains only whitespace.
    The user should verify that the file has been populated with citation data.
    """

    pass


class ValidationError(BillyError):
    """
    Raised when a transaction fails validation.

    This occurs when a transaction is missing required fields (e.g., ExternalUserId,
    RequestType) or when field values are empty. The transaction will not be submitted
    until the error is corrected in the source data.
    """

    pass


class ConfigError(BillyError):
    """
    Raised when application configuration is invalid or missing.

    This occurs when:
    - Required environment variables are not set in .env.
    - Configuration values are malformed or invalid (e.g., invalid pickup locations).

    The user should verify the .env file and config.py settings.
    """

    pass