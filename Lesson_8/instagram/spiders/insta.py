import json
import re
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse
from copy import deepcopy

from instagram.items import UserItem


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    friendships_url = "https://i.instagram.com/api/v1/friendships/"

    username = 'Onliskill_udm'  # Qw123456789
    enc_password = '#PWD_INSTAGRAM_BROWSER:9:1636996814:AVdQACJHOSulAXqCaWuUYdoaEKze3NmgDMk5sdAz1m6hPyEfuHOqzOw2JPBiG7PZJbStYLEhxlrivC4HFC14TxgVEz8VGIyhwA1Ba3LgZ16sZVWM3LJ6huefN4DvYgnu3W3fsQDN1lGDGp4SyiYN'
    # username = "dimagilev91"
    # enc_password = "#PWD_INSTAGRAM_BROWSER:10:1637092063:Ab1QAMMtttD/DiGMQoe7evZC+0A2pj7Z5RwXr50ZsaXt9JkQWzeNrqsjSh2ENJVzKB2TuO3DwgiczXcnLPMDqtEeSRJn8YNpaK0IIpc3hBvhAJyoHk8nlei1dtFuRDbSP6WwoqJiax7DuDZUCIqz"
    users_for_parse = ["_uvarov_vlad_"]

    def parse(self, response: HtmlResponse):
        csrf_token = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(
            url=self.login_url,
            method="POST",
            formdata={"username": self.username, "enc_password": self.enc_password},
            headers={"x-csrftoken": csrf_token},
            callback=self.login)

    def login(self, response: HtmlResponse):
        json_data = response.json()
        if json_data.get("authenticated"):
            for user_for_parse in self.users_for_parse:
                yield response.follow(f"/{user_for_parse}",
                                      callback=self.parse_user,
                                      cb_kwargs={"username": user_for_parse})

    def parse_user(self, response: HtmlResponse, username):
        userid = self.get_userid(response.text, username)
        followers_url = self.generate_followers_url(userid, 12, 0)
        yield response.follow(followers_url, callback=self.parse_subscriptions,
                              cb_kwargs={"userid": userid, "username": username,
                                         "url_generator": self.generate_followers_url,
                                         "subscription_description": "followers"})

        following_url = self.generate_following_url(userid, 12, 0)
        yield response.follow(following_url, callback=self.parse_subscriptions,
                              cb_kwargs={"userid": userid, "username": username,
                                         "url_generator": self.generate_following_url,
                                         "subscription_description": "following"})

    def parse_subscriptions(self, response: HtmlResponse, userid, username, url_generator, subscription_description):
        next_max_id = response.json().get("next_max_id")
        if next_max_id:
            url = url_generator(userid, 12, next_max_id)
            yield response.follow(url, callback=self.parse_subscriptions,
                                  cb_kwargs={"userid": userid, "username": username, "url_generator": url_generator,
                                             "subscription_description": subscription_description})

        users = response.json().get("users")
        new_users = list()
        for user in users:
            new_users.append(
                {"_id": user.get("pk"),
                 "full_name": user.get("full_name"),
                 "username": user.get("username"),
                 "profile_pic_url": user.get("profile_pic_url")})

        yield UserItem(_id=userid, username=username, users=new_users,
                       collection_name=subscription_description)

    def generate_followers_url(self, userid, count, max_id):
        variables = {"count": count, "max_id": max_id}
        return f"{self.friendships_url}{userid}/followers/?{urlencode(variables)}&search_surface=follow_list_page"

    def generate_following_url(self, userid, count, max_id):
        variables = {"count": count, "max_id": max_id}
        if max_id == 0:
            variables.pop("max_id")
        return f"{self.friendships_url}{userid}/following/?{urlencode(variables)}"

    def get_userid(self, html_text, username):
        matched = re.search(f"\"id\":\"\\d+\",\"username\":\"{username}\"", html_text).group()
        return matched.split(",")[0].split(":")[1].replace("\"", "")

    def get_csrf_token(self, html_text):
        matched = re.search("\"csrf_token\":\"\\w+\"", html_text).group()
        return matched.split(":").pop().replace("\"", "")
