"""
1) Написать приложение, которое собирает основные новости с сайта yandex-новости.
   Для парсинга использовать XPath. Структура данных должна содержать:
    - название источника;
    - наименование новости;
    - ссылку на новость;
    - дата публикации.
2) Сложить собранные новости в БД
"""

from lxml import html
import requests
from pymongo import MongoClient


def update_news(db_name, news_dict):
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    news = db.news
    for news_item in news_dict:
        news.update_one({'title': f'{news_item["title"]}'}, {'$set': news_item}, upsert=True)


def request_to_yandex():
    url = "https://yandex.ru/news/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}
    response = requests.get(url, headers=headers)

    root = html.fromstring(response.text)
    titles = root.xpath("//h2[@class='mg-card__title']/text()")
    links = root.xpath("//h2[@class='mg-card__title']/../@href")
    sources = root.xpath("//h2[@class='mg-card__title']/../../../../..//a[@class='mg-card__source-link']/text()")
    times = root.xpath("//h2[@class='mg-card__title']/../../../../..//span[@class='mg-card-source__time']/text()")

    news_list = []
    for i in range(len(titles)):
        title = titles[i]
        link = links[i]
        source = sources[i]
        time = times[i]
        news = {"title": title, "link": link, "source": source, "time": time}
        news_list.append(news)

    return news_list


if __name__ == "__main__":
    yandex_news = request_to_yandex()
    update_news("yandex", yandex_news)
