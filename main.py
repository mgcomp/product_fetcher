from database_def import DbInterface
from web_page_cache import WebPageCache
from recursive_page_crawler import WebPageCrawler
from vestel_web_page_processor import VestelPageProcessor
import settings
import logging


settings.setup_global_logger()
# Create logger
logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

# Create in memory sqlite db
db = DbInterface(settings.WEB_SCRAPPER_DATABASE_PRODUCTION, create_tables = True, turn_on_logging = False)

vp = VestelPageProcessor(db)

webPageExpirationTimeInSeconds = 7*24*60*60
wpCache = WebPageCache(db, webPageExpirationTimeInSeconds)
url = "https://www.vestel.com.tr"
crawler = WebPageCrawler(url, vp, wpCache)
crawler.process()