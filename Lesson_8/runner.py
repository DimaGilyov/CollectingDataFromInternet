from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from instagram import settings
from scrapy.settings import Settings

from instagram.spiders.insta import InstaSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaSpider)
    process.start()

