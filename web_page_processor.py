from database_def import DbInterface, Product
import logging
import settings

class WebPageProcessor:

    def __init__(self, dbInterface):
        assert isinstance(dbInterface, DbInterface)
        self.__dbInterface = dbInterface
        self.__session = self.__dbInterface.getSession()
        self.__logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

    def isLinkValid(self,base_url, found_url):
        """
        Checks if this is a valid link in the web page
        :param base_url: url of the web page currently processed
        :param found_url: url found on the web page with url == base_url
        :return: true if found_url should be visited
        """

        # Assuming all the relative links are valid. There may be javascript redirections which is missed here.
        # For an example of javascript redirections, see lcwaikiki web page.
        return found_url.startswith('/')

    def getCompleteLinkUrl(self, base_url, found_url):
        """
        This function is here for convenience, in case extra processing is needed
        :param base_url: url of the web page currently processed
        :param found_url: url found on the web page with url == base_url
        :return: concatenation of base_url + found_url.
        """
        assert self.isLinkValid(base_url, found_url)
        return base_url + found_url

    def isProductPage(self, html):
        """
        Checks if the html includes a product specification
        :param html: text html content of the page
        :return: true if html includes product info
        """
        pass

    def _getProductFromPage(self, url, html):
        """
        Extracts product from html
        :param html: html from which product will be extracted
        :return: Product
        """
        raise NotImplementedError("Must extend WebPageProcessor for web page specific product extraction!")

    def processProduct(self, url, html):
        """
        Extract product information and insert it into db
        :param html: html of the web page that has product info
        :return: None
        """
        try:
            prod = self._getProductFromPage(url, html)
            # if same product exitst, update it
            prod_in_db = self.__session.query(Product).filter_by(code = prod.code).first()
            if prod_in_db is None:
                self.__session.add(prod)
            else:
                prod_in_db.url = prod.url
                prod_in_db.name = prod.name
                prod_in_db.picture_url_large = prod.picture_url_large
                prod_in_db.picture_url_small = prod.picture_url_small
                prod_in_db.description = prod.description
                prod_in_db.price = prod.price
            self.__session.commit()
        except Exception as err:
            self.__logger.error("Error trying to process product info in page={0}:{1}".format(url, err))
