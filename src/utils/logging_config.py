"""Structured logging configuration for RiskLens AI."""
import logging
import sys
import re

SENSITIVE_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),
    re.compile(r"GEMINI_API_KEY=[^\s]+", re.IGNORECASE),
    re.compile(r"Bearer\s+[^\s]+", re.IGNORECASE)
]


class SensitiveFilter(logging.Filter):
    """Filter out any accidentally emitted API keys or secrets from log lines."""
    def filter(self, record):
        if isinstance(record.msg, str):
            for pattern in SENSITIVE_PATTERNS:
                record.msg = pattern.sub("[REDACTED_SECRET]", record.msg)
        return True


def setup_logging():
    """Setup structured application logging."""
    logger = logging.getLogger()
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveFilter())
    logger.addHandler(handler)
    return logger
