from pprint import pprint

from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from instagram import settings
from scrapy.settings import Settings

from instagram.spiders.insta import InstaSpider


def print_subscriber(collection_name, username):
    collection = instagram_db[collection_name]
    items = list(collection.find({"username": username}))
    for user in items:
        print(f"*****{user['username']} {collection_name}*****")
        pprint(user[collection_name])
        print(end="\n\n")


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaSpider)
    process.start()

    client = MongoClient("localhost", 27017)
    instagram_db = client["instagram"]

    # Написать запрос к базе, который вернет список подписчиков только указанного пользователя
    print_subscriber("followers", "onliskill_udm")

    # Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
    print_subscriber("following", "onliskill_udm")
