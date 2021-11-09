# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:
    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.books_db = client["books"]

    def process_item(self, item, spider):
        name, authors = self.get_book_name_and_authors_from_title(item["title"])
        price, discount_price = self.get_prices(item["price"], item["price_old"], item["price_new"])

        new_item = {"name": name, "authors": authors, "price": price, "discount_price": discount_price,
                    "url": item["url"], "rate": float(item["rate"])}

        collection = self.books_db[spider.name]
        collection.update_one({'url': f'{new_item["url"]}'}, {'$set': new_item}, upsert=True)
        return new_item

    def get_book_name_and_authors_from_title(self, title: str):
        authors_and_book_name = title.split(":")
        authors = [author.strip() for author in authors_and_book_name[0].split(",")]
        name = authors_and_book_name[1].strip()
        return name, authors

    def get_prices(self, price, price_old, price_new):
        discount_price = 0
        if not price:
            price = price_old
            discount_price = price_new
        return float(price), float(discount_price)
