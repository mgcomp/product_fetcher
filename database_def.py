#This file includes database ORM modules for the web scrapper
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import logging
import settings

SQLBase = declarative_base()


class Product(SQLBase):
    __tablename__ = 'Product'

    code = Column(String, primary_key = True)
    url = Column(String, primary_key = True)
    name = Column(String)
    picture_url_large = Column(String)
    picture_url_small = Column(String)
    description = Column(String)
    price = Column(Float)
    def __repr__(self):
        return "<Product(code='{0}', url='{1}', name='{2}', price='{3}')>".format(
            self.code, self.url, self.name, self.price)


class WebPageItem(SQLBase):
    __tablename__ = 'WebPageItem'
    url = Column(String, primary_key = True)
    fetch_time = Column(DateTime)
    html_text = Column(String)

    def __repr__(self):
        return "<WebPageItem(url='{0}', fetch_time={1})>".format(self.url, self.fetch_time)

class DbInterface:
    '''
        This class supports all the database engines that sqlalchemy supports.
        For creating sqlite database, set engine_path = 'sqlite://db_name'
    '''
    def __init__(self, engine_path, create_tables = False, turn_on_logging = False):
        assert isinstance(engine_path, str)
        self.logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)
        self.logger.info("Initializing dbInterface:{0},create_tables={1},logging={2}".format(
            engine_path, create_tables, turn_on_logging))
        self.engine_path = engine_path
        self.engine = create_engine(engine_path, echo = turn_on_logging)
        if create_tables:
            SQLBase.metadata.create_all(self.engine)

    def getSession(self):
        return Session(self.engine)

    def clearAllProducts(self):
        self.logger.debug("Logger deleting all products from:{0}".format(self.engine_path))
        session = self.getSession()
        for prod in session.query(Product):
            session.delete(prod)
        session.commit()

    def clearAllPages(self):
        self.logger.debug("Logger deleting all web pages from:{0}".format(self.engine_path))
        session = self.getSession()
        for page in session.query(WebPageItem):
            session.delete(page)
        session.commit()


if __name__ == '__main__':
    from datetime import datetime

    settings.setup_global_logger()
    # Create logger
    logger = logging.getLogger(settings.WEB_SCRAPPER_GLOBAL_LOGGER_NAME)

    # Create in memory sqlite db
    db = DbInterface(settings.WEB_SCRAPPER_DATABASE_TEST, create_tables = True, turn_on_logging = True)

    session = db.getSession()
    assert isinstance(session, Session)

    p0 = Product(code = "pp0", url = 'www.google.com/P0', name = 'P0', price = 3.4 )
    p1 = Product(code = "pp1", url = 'www.google.com/P1', name = 'P1', price = 3.6 )
    p2 = Product(code = "pp2", url = 'www.google.com/P2', name = 'P2', price = 3.7 )

    logger.info("Adding products to database!")
    session.add(p0)
    session.add(p1)
    session.add(p2)

    logger.info("Commiting products to database!")
    session.commit()


    w0 = WebPageItem(url ='www.google.com/P0', fetch_time = datetime.now(), html_text ='html_for_url0')
    w1 = WebPageItem(url ='www.google.com/P1', fetch_time = datetime.now(), html_text ='html_for_url1')

    logger.info("Adding web pages to database!")
    session.add(w0)
    session.add(w1)

    logger.info("Commiting web pages to database!")
    session.commit()

    logger.info("Querying product by product code!")
    for product0 in session.query(Product).filter_by(code='pp0').all():
        print("Product is:{0}".format(product0))

    print("Product first is:{0}".format(session.query(Product).filter_by(code = 'xcxcx').first()))