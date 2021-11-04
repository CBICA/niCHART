from pathlib import Path

from pyguitemp.logging import logger

VERSION = "0.0.1"
APP_NAME = Path(__file__).parent.stem
logger.app_name = APP_NAME
