import sys
import logging

WEB_SCRAPPER_DATABASE_SQLITE_IN_MEMORY = 'sqlite:///:memory:'
WEB_SCRAPPER_DATABASE_IN_MEMORY = WEB_SCRAPPER_DATABASE_SQLITE_IN_MEMORY
WEB_SCRAPPER_DATABASE_SQLITE = 'sqlite:///my_local_sqlite_db.db'

WEB_SCRAPPER_DATABASE_TEST = WEB_SCRAPPER_DATABASE_IN_MEMORY
WEB_SCRAPPER_DATABASE_PRODUCTION = WEB_SCRAPPER_DATABASE_SQLITE

WEB_CRAWLER_WEB_PAGE_MAX_TRAVERSAL_DEPTH = 4

WEB_SCRAPPER_LOG_STREAM = sys.stdout
WEB_SCRAPPER_GLOBAL_LOGGER_NAME = 'global'
WEB_SCRAPPER_GLOBAL_LOGGING_LEVEL = logging.DEBUG

def setup_global_logger():
    # Create logger
    logger = logging.getLogger(WEB_SCRAPPER_GLOBAL_LOGGER_NAME)
    logger.setLevel(WEB_SCRAPPER_GLOBAL_LOGGING_LEVEL)
    # Setup to log to stdout
    channel = logging.StreamHandler(WEB_SCRAPPER_LOG_STREAM)
    channel.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(channel)