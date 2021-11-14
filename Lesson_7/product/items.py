import scrapy
from itemloaders.processors import MapCompose
from itemloaders.processors import TakeFirst


def process_price(value):
    try:
        value = float(value)
    except Exception as e:
        print(e)
    finally:
        return value


class ProductItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    photos = scrapy.Field()
