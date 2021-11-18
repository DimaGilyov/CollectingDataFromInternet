# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    _id = scrapy.Field()
    username = scrapy.Field()
    collection_name = scrapy.Field()
    users = scrapy.Field()
