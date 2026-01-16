"""
logging_utils.py - Logging configuration and redaction utilities.

This module provides centralized logging setup for Billy. It configures file and/or console
handlers with optional secret redaction. The RedactFilter class ensures sensitive values
(API keys) are never logged, preventing accidental leaks in log files.

Notes:
- RedactFilter redacts both the log message and its formatting arguments to ensure secrets
  cannot leak through either channel.
- setup_logging clears existing handlers before adding new ones to avoid duplicate logs
  when called multiple times.
- By default, logging goes to file only; pass console=True or console_only=True to
  enable console output.

Author: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

import logging
from logging.handlers import RotatingFileHandler
from typing import Iterable, Optional

class RedactFilter(logging.Filter):
    """
    Filter that redacts sensitive values from log records.

    This filter replaces all occurrences of configured secrets (e.g., API keys) with
    [REDACTED] in both the log message and its formatting arguments. This ensures
    sensitive values never appear in log output, even if passed as format arguments.

    Attributes:
        secrets: Iterable of string values to redact from logs.
    """

    def __init__(self, secrets: Optional[Iterable[str]] = None):
        """
        Initialize the redaction filter.

        Args:
            secrets: Iterable of secret strings to redact. None or empty values are filtered out.
        """
        super().__init__()
        # Filter out None and empty strings so we don't redact empty values.
        self.secrets = [s for s in (secrets or []) if s]

    def _redact(self, text: str) -> str:
        """
        Replace all secret occurrences in text with [REDACTED].

        Args:
            text: String to redact.

        Returns:
            Redacted string with all secrets replaced.
        """
        if not text:
            return text
        for s in self.secrets:
            text = text.replace(s, "[REDACTED]")
        return text

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Redact secrets from a log record (message and arguments).

        This method is called by the logging framework for each log record. We redact
        both the message template and its formatting arguments to ensure secrets cannot
        leak through either path.

        Args:
            record: LogRecord to filter and redact.

        Returns:
            True - always allow the record through after redaction.
        """

        try:
            # Redact the message template itself (for secrets in format string)
            if isinstance(record.msg, str):
                record.msg = self._redact(record.msg)
            
            # Redact formatting arguments
            if record.args:
                try:
                    if isinstance(record.args, tuple):
                        # For tuple args, redact each element that is a string.
                        record.args = tuple(
                            self._redact(a) if isinstance(a, str) else 
                            self._redact(str(a)) if a is not None else a 
                            for a in record.args
                        )
                    else:
                        # For single-value args, redact if it's a string.
                        record.args = self._redact(str(record.args)) if isinstance(record.args, str) else record.args
                except Exception:
                    # Defensive: if redaction fails, clear args to avoid leak
                    record.args = ()
        except Exception:
            # Defensive: if anything fails, still allow the record through
            pass
        
        # Always return True so the record is processed 
        return True
    

def setup_logging(
    *,
    log_file: str = "billy.log",
    level: int = logging.INFO,
    console: bool = False,
    console_only: bool = False,
    secrets: Optional[Iterable[str]] = None,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5
) -> None:
    """
    Configure the root logger with file and/or console handlers.

    This function sets up Billy's logging infrastructure. By default, logs are written to
    a rotating file; pass console=True to also output to stderr, or console_only=True to
    output to console only.

    All handlers are configured with secret redaction to prevent sensitive values from 
    leaking into logs.

    Args:
        log_file: Path to the log file. Ignored if console_only=True.
        level: Logging level defaults to INFO.
        console: If True, add a console handler in addition to the file handler.
        console_only: If True, only add a console handler (no file handler). Overrides console.
        secrets: Iterable of secret strings to redact from all log output (API keys).
        max_bytes: Maximum size of a log file before rotation (default 5 MB).
        backup_count: Number of rotated backups to keep (default 5).

    Notes:
        - Clears all existing handlers on the root logger before adding new ones.
          This prevents duplicate logs if setup_logging is called multiple times.
        - The redaction filter is applied to all handlers to ensure secrets are
          redacted consistently everywhere.
    """

    root = logging.getLogger()
    root.setLevel(level)

    # Clear any existing handlers to avoid duplicates
    for h in list(root.handlers):
        root.removeHandler(h)

    # Define a consistent log format: timestamp, level, function name, line number, message
    fmt = "%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt)

    # Create a redaction filter with the provided secrets
    redact_filter = RedactFilter(secrets=secrets)

    # Add file handler unless console_only is specified
    if not console_only:
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(redact_filter)
        root.addHandler(file_handler)
    
    # Add console handler if specified
    if console or console_only:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(redact_filter)
        root.addHandler(console_handler)