import logging
import sys


def setup_logging() -> None:
    """Configures structured logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Silence third-party logging chatter
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
