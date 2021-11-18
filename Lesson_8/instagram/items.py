import scrapy


class UserItem(scrapy.Item):
    _id = scrapy.Field()
    username = scrapy.Field()
    collection_name = scrapy.Field()
    users = scrapy.Field()
