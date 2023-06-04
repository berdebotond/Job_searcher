# logger for stdout and file output

import logging

from modules.config.config import config

logger = logging.getLogger(__name__)

logger.setLevel(config.LOG_LEVEL)

# handler for stdout
stdout_handler = logging.StreamHandler()

# handler for file output
file_handler = logging.FileHandler(config.PROJECT_NAME + ".log")

# add handlers to logger
logger.addHandler(stdout_handler)
logger.addHandler(file_handler)
