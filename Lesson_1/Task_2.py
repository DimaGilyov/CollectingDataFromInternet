import requests
import json


def get_files_list(folder_name, token):
    """Просмотр содержимого на яндекс диске"""

    headers = {'Authorization': f'OAuth {token}'}
    req = requests.get(f'https://cloud-api.yandex.net/v1/disk/resources?path={folder_name}', headers=headers)
    return req.json() if req.status_code == 200 else {}


if __name__ == '__main__':
    """Яндекс Диск"""

    TOKEN = ''
    folder = '/TestFolder/'
    files = get_files_list(folder, TOKEN)
    if files:
        with open('yandex_drive.json', 'w', encoding='UTF-8') as file:
            json.dump(files, file)
