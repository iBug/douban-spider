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
    headers = {'User-Agent': ua.random}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Invalid response code: {response.status_code}")
    # Save the page for later analysis
    with open(os.path.join("pages", item_type, f"{user}-{offset}.html"), "w") as f:
        f.write(response.text())
    return True
