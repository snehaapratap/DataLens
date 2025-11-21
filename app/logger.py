import logging
from logging.handlers import RotatingFileHandler
import sys

logger = logging.getLogger("datalens")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("datalens.log", maxBytes=5_000_000, backupCount=3)
fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(fmt)
logger.addHandler(handler)
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(fmt)
logger.addHandler(stdout)
