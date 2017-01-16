from web_page_processor import WebPageProcessor
from database_def import DbInterface, Product
from bs4 import BeautifulSoup
import settings
import json
from urllib.parse import urlparse

class VestelPageProcessor(WebPageProcessor):

    def __init__(self, dbInterface):
        super().__init__(dbInterface)

    @staticmethod
    def __getProductHtml(html):
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find_all('div', {'class' : 'product-preview'})
        res = [str(tag) for tag in tags]
        return res

    @staticmethod
    def __getTechnicalInfo(html):
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find_all('div', { 'class' :'container technical-info-list'})
        assert len(tags) <=1
        specs = []
        if len(tags) == 0 :
            return specs

        spec_tag = tags[0]

        all_li = spec_tag.find_all('li')
        for li in all_li:
            mdivs = li.find_all('div', recursive = False)
            spec_div = None
            value_div = None
            for mdiv in mdivs:
                if mdiv.get('class', '') == ['spec']:
                    spec_div = mdiv

                if mdiv.get('class', '') == ['value']:
                    value_div = mdiv

            if spec_div is not None  and value_div is not None:
                specs.append({'spec': spec_div.text, 'value' : value_div.text})

        return specs

    def isProductPage(self, html):
        return len(self.__getProductHtml(html)) > 0

    def __getProductCodeFromSoup(self,soup):
        tags = soup.findAll('h1')
        for tag in tags:
            return tag.text.strip()

    def __getPictureFromSoup(self, soup):
        carousel = soup.findAll('div',{'class':'prod-carousels'})
        if len(carousel) == 0:
            return ""
        for mtag in carousel[0].find_all('img'):
            return mtag['src']


    def __getProductPriceFromSoup(self, soup):
        tags = soup.findAll('span', {'class' : 'discounted'})
        for tag in tags:
            tag_text = tag.text.strip().split()[0]
            assert isinstance(tag_text, str)
            tag_text = tag_text.replace('.','')
            tag_text = tag_text.replace(',','.')
            return float(tag_text)

    def __getProductDescriptionFromSoup(self,soup):
        tags = soup.findAll('ul', {'class' : 'short-specs'})
        for tag in tags:
            return "\n".join([x for x in [text.strip() for text in tag.text.split("\n")] if len(x)>0])

    def _getProductFromPage(self, url, html):

        productList = self.__getProductHtml(html)
        assert len(productList) == 1
        prod_html = productList[0]
        soup = BeautifulSoup(prod_html, 'html.parser')
        product_code = self.__getProductCodeFromSoup(soup)
        price =  self.__getProductPriceFromSoup(soup)
        short_spec = self.__getProductDescriptionFromSoup(soup)
        technical_info = self.__getTechnicalInfo(html)
        description = {'short_spec': short_spec, 'technical_info': technical_info}
        img_url = self.__getPictureFromSoup(soup)
        if img_url.startswith('/'):
            urlp = urlparse(url)
            img_url = urlp.scheme + "://" + urlp.netloc + img_url

        prod = Product(code = product_code,
                       url = url,
                       name = product_code,
                       picture_url_large = img_url,
                       picture_url_small = img_url,
                       description = json.dumps(description),
                       price = price)
        return prod

if __name__ == "__main__":

    import logging
    import sys
    from web_page_cache import WebPageCache

    settings.setup_global_logger()
    # Create logger
    logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

    # Create in memory sqlite db
    db = DbInterface(settings.WEB_SCRAPPER_DATABASE_TEST, create_tables = True, turn_on_logging = True)

    wpCache = WebPageCache(db, 1000000)
    #url = "https://www.vestel.com.tr/vestel-nf480-ex-buzdolabi"
    url = "https://www.vestel.com.tr/toshiba-satellite-c55-c-1h7-15-6-notebook"
    html = wpCache.getWebPage(url)

    vp = VestelPageProcessor(db)
    print("IsProductPage = ",vp.isProductPage(html))
    if vp.isProductPage(html):
        vp.processProduct(url,html)