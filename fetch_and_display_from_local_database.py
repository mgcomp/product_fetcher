from database_def import DbInterface, Product
import settings
import logging
import pprint
import json
settings.setup_global_logger()
# Create logger
logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

try:
    # Create in memory sqlite db
    db = DbInterface(settings.WEB_SCRAPPER_DATABASE_PRODUCTION, create_tables = False, turn_on_logging = False)

    dbSession = db.getSession()

    logger.info("\n\n\nTEST 1\n\n\n\n")
    for prod in dbSession.query(Product).filter(Product.price < 100):
        print(prod)

    logger.info("\n\n\nTEST 2\n\n\n\n")
    for prod in dbSession.query(Product).filter(Product.price < 100).filter(Product.price > 90):
        print(prod)

    logger.info("\n\n\nTEST 3\n\n\n\n")
    for prod in dbSession.query(Product).filter(Product.url.contains('perilla')).filter(Product.price > 90):
        print(prod)
        pprint.pprint(json.loads(str(prod.description)))

except Exception as err:
    logger.error("have a problem:{0}".format(err))