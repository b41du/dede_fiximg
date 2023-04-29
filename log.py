import logging
from config import app_name

logging.basicConfig()
log = logging.getLogger(app_name)
log.setLevel(logging.INFO)
log.info(f'log active')