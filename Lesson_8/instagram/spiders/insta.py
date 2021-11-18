import re
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse

from instagram.items import UserItem


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    friendships_url = "https://i.instagram.com/api/v1/friendships/"

    username = ''
    enc_password = ''
    users_for_parse = ["tapaevadaniya", "onliskill_udm"]
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
        followers_url = self.generate_followers_url(userid, 12)
        yield response.follow(followers_url, callback=self.parse_subscriptions,
                              cb_kwargs={"userid": userid, "username": username,
                                         "url_generator": self.generate_followers_url,
                                         "subscription_description": "followers"})

        following_url = self.generate_following_url(userid, 12)
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
        print(subscription_description, ", users_count: ", len(users), ", url: ", response.url)
        print("users: ", users)

        new_users = list()
        for user in users:
            new_users.append(
                {"_id": user.get("pk"),
                 "full_name": user.get("full_name"),
                 "username": user.get("username"),
                 "profile_pic_url": user.get("profile_pic_url")})

        yield UserItem(_id=userid, username=username, users=new_users,
                       collection_name=subscription_description)

    def generate_followers_url(self, userid, count, max_id=None):
        variables = {"count": count, "max_id": max_id}
        if not max_id:
            variables.pop("max_id")
        return f"{self.friendships_url}{userid}/followers/?{urlencode(variables)}&search_surface=follow_list_page"

    def generate_following_url(self, userid, count, max_id=None):
        variables = {"count": count, "max_id": max_id}
        if not max_id:
            variables.pop("max_id")
        return f"{self.friendships_url}{userid}/following/?{urlencode(variables)}"

    def get_userid(self, html_text, username):
        matched = re.search(f"\"id\":\"\\d+\",\"username\":\"{username}\"", html_text).group()
        return matched.split(",")[0].split(":")[1].replace("\"", "")

    def get_csrf_token(self, html_text):
        matched = re.search("\"csrf_token\":\"\\w+\"", html_text).group()
        return matched.split(":").pop().replace("\"", "")
