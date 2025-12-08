"""
Structured logging configuration for production.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(environment: str = "development", log_level: str = None):
    """
    Configure structured logging for the application.
    
    Args:
        environment: Application environment (development, production)
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)
    """
    # Determine log level
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        level = logging.DEBUG if environment == "development" else logging.INFO

    # Create logs directory
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if environment == "production":
        # Use JSON formatter for production (better for log aggregation)
        try:
            from pythonjsonlogger import jsonlogger
            formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d"
            )
        except ImportError:
            # Fallback to standard formatter if jsonlogger not available
            class CustomFormatter(logging.Formatter):
                def format(self, record):
                    # Add request_id if missing (for third-party library logs)
                    if not hasattr(record, 'request_id'):
                        record.request_id = 'N/A'
                    return super().format(record)
            
            formatter = CustomFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
    else:
        # Human-readable format for development
        # Use a custom formatter that handles missing request_id
        class CustomFormatter(logging.Formatter):
            def format(self, record):
                # Add request_id if missing (for third-party library logs)
                if not hasattr(record, 'request_id'):
                    record.request_id = 'N/A'
                return super().format(record)
        
        formatter = CustomFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation for production
    if environment == "production":
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        
        # Use JSON formatter for file logs in production
        try:
            from pythonjsonlogger import jsonlogger
            file_formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d"
            )
        except ImportError:
            class CustomFormatter(logging.Formatter):
                def format(self, record):
                    # Add request_id if missing (for third-party library logs)
                    if not hasattr(record, 'request_id'):
                        record.request_id = 'N/A'
                    return super().format(record)
            
            file_formatter = CustomFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    # Suppress pymongo debug logs that don't have request_id
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    logging.info(f"Logging configured for {environment} environment", extra={"request_id": "startup"})

