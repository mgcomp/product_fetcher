from web_page_processor import WebPageProcessor
from web_page_cache import WebPageCache
from bs4 import BeautifulSoup
import settings
import logging

class WebPageCrawler:
    """
    Web page crawler searches all the links in the web page. It does a breath first search
    of all the links in the given web page, up to the depth of WEB_CRAWLER_WEB_PAGE_MAX_TRAVERSAL_DEPTH
    It can early stop, if we are at least at depth 2, and we found a lot of prodct pages
    """
    def __init__(self, base_url, pageProcessor, webPageCache):
        self.__logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

        assert isinstance(base_url, str)
        assert isinstance(pageProcessor, WebPageProcessor)
        assert isinstance(webPageCache, WebPageCache)

        self.__pageCache = webPageCache
        self.__pageProcessor = pageProcessor
        self.__url = base_url


    def __getListOfValidUrls(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = [link['href'] for link in soup.findAll('a', href = True)]
        return [self.__pageProcessor.getCompleteLinkUrl(self.__url, link) for link in links
                if self.__pageProcessor.isLinkValid(self.__url, link)]

    def __processPageAndReturnValidUrls(self, current_url, html):
        if self.__pageProcessor.isProductPage(html):
            self.__pageProcessor.processProduct(current_url, html)
            return None
        else:
            # Assuming product page is a leaf page, meaning, it does not list
            # other products, and we can reach products that reachable from here
            # through other means
            return self.__getListOfValidUrls(html)

    def __processUrlList(self, urlList):
        assert isinstance(urlList, list)
        numProductsFound = 0
        childUrls = []

        for url in urlList:
            html = self.__pageCache.getWebPage(url)
            childUrlsFound = self.__processPageAndReturnValidUrls(url,html)

            if childUrlsFound is None:
                numProductsFound += 1
            else:
                assert isinstance(childUrlsFound, list)
                childUrls.extend(childUrlsFound)

        return numProductsFound,childUrls

    def process(self):
        self.__logger.debug("Crawling web page: url={0}".format(self.__url))
        searchDepth = settings.WEB_CRAWLER_WEB_PAGE_MAX_TRAVERSAL_DEPTH
        processedPagesList = {}
        currentUrlList = [self.__url]
        totalProducts = 0
        for currentDepth in range(searchDepth):
            numProducts, childUrls_raw = self.__processUrlList(currentUrlList)

            # Add all the processed pages to processedPagesList
            for processedUrl in currentUrlList:
                processedPagesList[processedUrl] = True

            # remove all the pages that are already processed or duplicate
            childUrls = []
            for url in childUrls_raw:
                stripped_url = url.strip()
                if stripped_url not in processedPagesList and stripped_url not in childUrls:
                    childUrls.append(stripped_url)

            self.__logger.debug("Crawling:raw_url_list_size={0}, non_visited_size={1}".format(
                len(childUrls_raw), len(childUrls)))
            del childUrls_raw

            totalProducts += numProducts
            self.__logger.debug("Crawling: found {0} products and {1} links at depth {2}.(TotalProducts={3})".format(
                    numProducts, len(childUrls), currentDepth, totalProducts))
            # If we are at depth larger than 1 and number of product pages
            # found is at least half of the links, than stop, else, continue
            # down
            if currentDepth > 1 and numProducts > len(currentUrlList)*0.5:
                break
            currentUrlList = childUrls


if __name__ == '__main__':
    from database_def import DbInterface
    from vestel_web_page_processor import VestelPageProcessor
    settings.setup_global_logger()
    # Create logger
    logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

    # Create in memory sqlite db
    db = DbInterface(settings.WEB_SCRAPPER_DATABASE_TEST, create_tables = True, turn_on_logging = False)

    wpCache = WebPageCache(db, 1000000)
    url = "https://www.vestel.com.tr"
    vp = VestelPageProcessor(db)
    crawler = WebPageCrawler(url, vp, wpCache)
    crawler.process()
