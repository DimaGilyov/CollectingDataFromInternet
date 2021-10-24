import requests
import json


def get_repositories(username):
    return requests.get(f'https://api.github.com/users/{username}/repos').json()


if __name__ == '__main__':
    username = ''
    repositories = get_repositories(username)
    with open('repositories.json', 'w', encoding='UTF-8') as file:
        json.dump(repositories, file)
