import logging
from logging.handlers import RotatingFileHandler
from typing import Iterable, Optional

# Configure logging to output to a file and console, and redact sensitive values
class RedactFilter(logging.Filter):
    def __init__(self, secrets: Optional[Iterable[str]] = None):
        super().__init__()
        self.secrets = [s for s in (secrets or []) if s]

    def _redact(self, text: str) -> str:
        if not text:
            return text
        for s in self.secrets:
            text = text.replace(s, "[REDACTED]")
        return text

    def filter(self, record: logging.LogRecord) -> bool:
        # redact message and args to avoid secrets leaking via formatting
        try:
            if isinstance(record.msg, str):
                record.msg = self._redact(record.msg)
            if record.args:
                try:
                    if isinstance(record.args, tuple):
                        record.args = tuple(self._redact(str(a)) if isinstance(a, str) else a for a in record.args)
                    else:
                        # sometimes args can be a single value
                        record.args = self._redact(str(record.args)) if isinstance(record.args, str) else record.args
                except Exception:
                    # fallback: remove args only if redaction fails
                    record.args = ()
        except Exception:
            pass
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
    root = logging.getLogger()
    root.setLevel(level)
    for h in list(root.handlers):
        root.removeHandler(h)

    fmt = "%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt)

    redact_filter = RedactFilter(secrets=secrets)

    if not console_only:
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(redact_filter)
        root.addHandler(file_handler)

    if console or console_only:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(redact_filter)
        root.addHandler(console_handler)