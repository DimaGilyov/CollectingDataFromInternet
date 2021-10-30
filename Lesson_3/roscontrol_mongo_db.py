"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
   которая будет добавлять только новые вакансии/продукты в вашу базу.

2. Напишите запрос для поиска продуктов с рейтингом не ниже введенного или качеством не ниже введенного
   (то есть цифра вводится одна, а запрос проверяет оба поля)
"""

from roscontrol import get_products_data
from pymongo import MongoClient
from pprint import pprint


def connect_to_db():
    client = MongoClient('localhost', 27017)
    return client['roscontrol']


def update_products_data(products_list):
    products = roscontrol_db.products
    for product in products_list:
        products.update_one({'Продукт': f'{product["Продукт"]}'}, {'$set': product}, upsert=True)


def find_products_on_rate(min_rate):
    products = roscontrol_db.products
    return list(products.find({'$and': [{'Общая оценка': {'$gte': min_rate}}, {'Качество': {'$gte': min_rate}}]}))


if __name__ == '__main__':
    products_list = get_products_data()
    roscontrol_db = connect_to_db()
    update_products_data(products_list)

    products_list = find_products_on_rate(82)
    pprint(products_list)
