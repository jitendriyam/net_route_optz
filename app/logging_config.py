import logging

from app.settings import settings


def configure_logging() -> None:
    """Configure consistent application logging for local and container execution."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("app").setLevel(level)
