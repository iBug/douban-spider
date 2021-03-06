#!/usr/bin/python3

import os
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as BS


ua = UserAgent()


def get_item(user, item_type='book', offset=0):
    url = f"https://{item_type}.douban.com/people/{user}/collect"
    params = {
        'sort': "time",
        'start': str(offset),
        'filter': "all",
        'mode': "list",
        'tags_sort': "count",
    }
    headers = {
        'X-Forwarded-For': '127.0.0.1',
        'X-Real-IP': '127.0.0.1',
        'User-Agent': ua.random,
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Invalid response code: {response.status_code} when accessing {url} with params={params} and headers={headers}")
    # Save the page for later analysis
    filename = os.path.join("pages", item_type, f"{user}-{offset}.html")
    with open(filename, "w") as f:
        f.write(response.text())
    return filename

if __name__ == "__main__":
    get_item('1000030')