import logging
import sys

from app.core.config import settings


def setup_logging():
    level = logging.DEBUG if settings.debug else logging.INFO
    fmt = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

    logging.basicConfig(
        level=level,
        format=fmt,
        stream=sys.stderr,
    )
