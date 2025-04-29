import logging
import sys

# GET LOGGER
logger = logging.getLogger()

# CREATE FORMATTER
formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

# HANDLERS
sys.stdout.reconfigure(encoding='utf-8')
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('pulsus.log', encoding='utf-8')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# HANDLERS TO THE LOGGER
logger.handlers = [stream_handler, file_handler]

# SET LOG-LEVEL 
logger.setLevel(logging.INFO)