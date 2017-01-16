from database_def import DbInterface, WebPageItem
from datetime import datetime, timedelta
import requests
import logging
import settings

class WebPageCache:
    """
        This class uses uses given dbInterface as the cache to web pages.
        When a requested page is in db, it is not fetched from web url target, else
        it is fetched from web target, and database is updated with that data
    """
    def __init__(self, dbInterface, timeOutInSeconds):
        self.__logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

        assert isinstance(dbInterface, DbInterface)
        assert dbInterface is not None
        assert isinstance(timeOutInSeconds, int)
        assert timeOutInSeconds > 0

        self.__dbInterface = dbInterface
        self.__dbSession = None
        self.__timeout = timedelta(seconds=timeOutInSeconds)

    def getWebPage(self, url):
        """"
        This function checks if html of the given url is in the database. If it is, it will return corresponding
        html. Else, it will first fetch web page, commit it to the database and return html text
        :param url:  url of the requested web page
        :return: html in string form corresponding to given url, None if url cannot be resolved
        """
        self.__logger.debug("WebPageCache: getting web page for url:{0}".format(url))
        if self.__dbSession is None:
            self.__dbSession = self.__dbInterface.getSession()

        webPageRecord = self.__dbSession.query(WebPageItem).filter_by(url = url).first()

        currentTime = datetime.now()
        if webPageRecord is None or self.__timeout < currentTime - webPageRecord.fetch_time :
            self.__logger.debug("cannot find web page({0}) in database.Querying!".format(url))
            try:
                html_text = requests.get(url,
                                     headers={'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1)'}).text
                if html_text is None:
                    return None
                if webPageRecord is None:
                    webPageRecord = WebPageItem(url = url, fetch_time = currentTime, html_text = html_text)
                    self.__dbSession.add(webPageRecord)
                else:
                    webPageRecord.fetch_time = currentTime
                    webPageRecord.html_text = html_text
                self.__dbSession.commit()
            except Exception as err:
                self.__logger.error("Error occured trying to fetch web page at url:{0}:{1}".format(url, err))
                return None

        return webPageRecord.html_text



if __name__ == "__main__":
    import time

    settings.setup_global_logger()
    # Create logger
    logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

    # Create in memory sqlite db
    db = DbInterface(settings.WEB_SCRAPPER_DATABASE_TEST, create_tables = True, turn_on_logging = True)

    expireInSeconds = 10
    webCache = WebPageCache(db, expireInSeconds)
    logger.info("Trying to fetch from invalid url!")
    assert None == webCache.getWebPage("http://mxreredocs.python-requeststrtr.org/en/master/user/quickstart/")

    logger.info("Fetching web page from cache. It should get it from web!")
    assert None != webCache.getWebPage("http://docs.python-requests.org/en/master/user/quickstart/")

    logger.info("Fetching web page from cache. It should return from database!")
    webCache.getWebPage("http://docs.python-requests.org/en/master/user/quickstart/")
    time.sleep(expireInSeconds*1.1)

    logger.info("Fetching web page from cache. It should get if from web, since it is expired!")
    webCache.getWebPage("http://docs.python-requests.org/en/master/user/quickstart/")

