import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import settings


def setup_logging() -> None:
    """Configures structured, multi-destination logging for the application."""
    # Ensure the log directory exists
    log_dir = settings.log_dir_path
    os.makedirs(log_dir, exist_ok=True)

    # Base formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (ReqID: %(request_id)s) - %(message)s"
    )

    from app.core.context import request_id_ctx

    # Filter to inject context-aware request ID into logs
    class RequestIDFilter(logging.Filter):
        def filter(self, record):
            record.request_id = request_id_ctx.get()
            return True

    req_filter = RequestIDFilter()

    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(req_filter)

    # 2. Application Log File Handler (INFO and above)
    app_log_path = os.path.join(log_dir, "app.log")
    app_handler = RotatingFileHandler(
        app_log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    app_handler.addFilter(req_filter)

    # 3. Error Log File Handler (ERROR and above)
    error_log_path = os.path.join(log_dir, "error.log")
    error_handler = RotatingFileHandler(
        error_log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(req_filter)

    # 4. Access Log File Handler (Only for HTTP access logs)
    access_log_path = os.path.join(log_dir, "access.log")
    access_handler = RotatingFileHandler(
        access_log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(formatter)
    access_handler.addFilter(req_filter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)

    # Configure uvicorn loggers
    for logger_name in ["uvicorn", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.propagate = True

    # Setup specific access logger
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers = []
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    access_logger.addHandler(console_handler)
    # Prevent uvicorn.access from propagating to root logger to avoid double logging
    access_logger.propagate = False

    # Also custom access logger for our middleware
    custom_access_logger = logging.getLogger("app.access")
    custom_access_logger.handlers = []
    custom_access_logger.setLevel(logging.INFO)
    custom_access_logger.addHandler(access_handler)
    custom_access_logger.addHandler(console_handler)
    custom_access_logger.propagate = False

    logging.info("Logging infrastructure configured successfully.")
