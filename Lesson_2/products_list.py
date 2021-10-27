"""
Необходимо собрать информацию по продуктам питания с сайта:
Список протестированных продуктов на сайте Росконтроль.рф https://roscontrol.com/category/produkti/
Приложение должно анализировать несколько страниц сайта (вводим через input или аргументы).

Получившийся список должен содержать:
1) Наименование продукта.
2) Все параметры (Безопасность, Натуральность, Пищевая ценность, Качество) Не забываем преобразовать к цифрам
3) Общую оценку
4) Сайт, откуда получена информация.
Общий результат можно вывести с помощью dataFrame через Pandas. Сохраните в json либо csv.
"""

import requests
from bs4 import BeautifulSoup as bs
import json

host = 'https://roscontrol.com'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}


def get_categories(url):
    response = requests.get(url, headers=headers)
    dom = bs(response.text, 'html.parser')
    categories = dom.find(attrs={'class': 'testlab-category'}).find_all('a')

    categories_dict = dict()
    for i, category in enumerate(categories, start=1):
        href = host + category['href']
        name = str(category.find('div', attrs={'class': 'catalog__category-name'}).text).strip()
        categories_dict[i] = {'name': name, 'href': href}

    return categories_dict


def select_category(categories_dict):
    while True:
        for k, v in categories_dict.items():
            print(f'{k}) {v["name"]}')

        try:
            category_number = int(input(f'\nВведите номер категории от 1 до {len(categories_dict)}: '))
            return categories_dict[category_number]
        except (KeyError, ValueError):
            input(f'Не верный номер категории. Нажмите ENTER')


def get_products(category_url, page_num=1):
    response = requests.get(category_url, headers=headers)
    dom = bs(response.text, 'html.parser')
    root = dom.find(attrs={'class': 'AJAX_root'})

    second_products_list = []
    if page_num == 1:
        page_pagination = root.find(attrs={'class': 'page-pagination'})
        if page_pagination:
            pages = page_pagination.find_all('a', attrs={'class': 'page-num'})
            for page in pages:
                try:
                    page_number = int(page.text)
                    if page_number > 1:
                        page_url = host + page['href']
                        products = get_products(page_url, page_number)
                        second_products_list = second_products_list + products
                except Exception as ex:
                    print(f"#ERROR {page_num} {ex} -> {page.text}")
                    continue

    first_products_list = []
    grid = root.find(attrs={'class': 'grid-row'})
    if grid:
        products_grid = grid.findChildren(recursive=False)
        for product_item in products_grid:
            product = {}
            try:
                product['URL'] = category_url
                product['Продукт'] = str(product_item.find('div', attrs={'class': 'product__item-link'}).text)
            except:
                print(f"#ERROR page {page_num} product__item-link {product['Продукт']}")
                print(product_item)
            else:
                try:
                    product['Общая оценка'] = int(product_item.find('div', attrs={'class': 'rate'}).text)
                except:
                    print(f"#ERROR page {page_num} rate, {product['Продукт']}")
                    product['Общая оценка'] = None

                ratings_block = product_item.find(attrs={'class': 'rating-block'})
                if ratings_block:
                    ratings_block_items = ratings_block.findChildren(recursive=False)
                    for rating_item in ratings_block_items:
                        try:
                            characteristic_name = rating_item.find(attrs={'class': 'text'}).text
                            characteristic_rating = int(rating_item.find('i')['data-width'])
                            product[characteristic_name] = characteristic_rating
                        except:
                            print(f"#ERROR {page_num} ratings_block, {product['Продукт']}")

                first_products_list.append(product)

    return first_products_list + second_products_list


if __name__ == '__main__':
    url = host + '/category/produkti/'
    for _ in range(2):
        categories_dict = get_categories(url)
        selected_category = select_category(categories_dict)
        print(f"Вы выбрали категорию: {selected_category['name']}")
        url = selected_category['href']

    products = get_products(url)

    print(f'Количество продуктов: {len(products)}')
    with open('products.json', 'w', encoding='UTF-8') as file:
        json.dump(products, file, ensure_ascii=False)
