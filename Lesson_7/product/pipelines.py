from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class ProductPipeline:
    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.products_db = client["products"]

    def process_item(self, item, spider):
        collection = self.products_db[spider.name]
        collection.update_one({'url': f'{item["url"]}'}, {'$set': item}, upsert=True)
        return item


class ProductImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        photos = item["photos"]
        if photos:
            for img in photos:
                try:
                    yield Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item["photos"] = [result[1] for result in results if result[0]]
        return item
