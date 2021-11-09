import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = [
        'https://www.labirint.ru/search/%D0%BF%D1%80%D0%B8%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D1%8F/?stype=0&russianonly=1']

    def parse(self, response: HtmlResponse):
        next_page_link = response.xpath("//a[@class='pagination-next__text']/@href").get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)

        books_links = response.xpath("//a[@class='product-title-link']/@href").getall()
        for book_link in books_links:
            yield response.follow(book_link, callback=self.parse_book_info)

    def parse_book_info(self, response: HtmlResponse):
        url = response.url
        title = response.xpath("//h1/text()").get()
        price = response.xpath("//span[@class='buying-price-val-number']/text()").get()
        price_old = response.xpath("//span[@class='buying-priceold-val-number']/text()").get()
        price_new = response.xpath("//span[@class='buying-pricenew-val-number']/text()").get()
        rate = response.xpath("//div[@id='rate']/text()").get()

        yield BookparserItem(url=url, title=title, price=price, price_old=price_old, price_new=price_new, rate=rate)
