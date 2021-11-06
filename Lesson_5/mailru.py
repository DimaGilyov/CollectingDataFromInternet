"""
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и с
ложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pymongo import MongoClient

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
actions = ActionChains(driver)
wait = WebDriverWait(driver, 10)


def update_mails(db_name, items):
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    mail = db.mails
    for item in items:
        mail.update_one({'link': f'{item["link"]}'}, {'$set': item}, upsert=True)


def login_to_mail(e_mail, pswd):
    driver.get("https://mail.ru/")
    driver.implicitly_wait(10)

    login = driver.find_element(By.NAME, "login")
    login.send_keys(e_mail)

    enter_password_button = driver.find_element(By.XPATH, "//button[@data-testid='enter-password']")
    enter_password_button.click()
    driver.implicitly_wait(10)

    password = driver.find_element(By.NAME, "password")
    password.send_keys(pswd)

    login_to_email_button = driver.find_element(By.XPATH, "//button[@data-testid='login-to-mail']")
    login_to_email_button.click()
    driver.implicitly_wait(10)
    print("Ящик залогинен")


def get_mails():
    previous_mails = []
    has_next_email = True
    all_mails = dict()
    while has_next_email:
        mails = driver.find_elements(By.XPATH, "//a[contains(@href, 'inbox')]")
        driver.implicitly_wait(10)
        has_next_email = True if len(previous_mails) == 0 else mails[-1] != previous_mails[-1]

        for mail in mails:
            link = mail.get_attribute("href")
            if link != "https://e.mail.ru/inbox/" and link:
                contact = mail.find_element(By.CLASS_NAME, "ll-crpt").text
                data = mail.find_element(By.CLASS_NAME, "llc__item_date").get_attribute("title")
                title = mail.find_element(By.CLASS_NAME, "ll-sj__normal").text

                email_data = {"contact": contact, "data": data, "title": title, "link": link}
                all_mails[link] = email_data

        for _ in range(2):
            element = wait.until(ec.element_to_be_clickable(mails[-1]))
            actions.move_to_element(element)
            actions.perform()

        previous_mails = mails

    return all_mails.values()


if __name__ == "__main__":
    e_mail = ""
    pswd = ""

    login_to_mail(e_mail, pswd)
    mails = get_mails()
    update_mails("mailru", mails)
    print(f"mails count {len(mails)}")
    driver.close()
