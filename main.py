#!/usr/bin/python3

import sys
import os
import re
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


ua = UserAgent()
control_url = "https://gjpqy.taokystrong.com"
log_file = open("spider.log", "a")


def log(s):
    global log_file
    print(s, file=sys.stderr)
    print(s, file=log_file)


def get_item(job_id, user, item_type='book', page=0):
    item_name = ['book', 'movie'][item_type]
    url = f"https://{item_type}.douban.com/people/{user}/collect"
    params = {
        'sort': "time",
        'start': str(page * 30),
        'filter': "all",
        'mode': "list",
        'tags_sort': "count",
    }
    headers = {
        'User-Agent': ua.random,
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9,en-US,en;q=0.8",
        'Referer': "https://www.douban.com/",
    }
    response = requests.get(url, params=params, headers=headers, allow_redirects=False)
    if response.status_code in [302, 403]:
        # Kill
        with open("should_reboot", "w") as f:
            pass
        os._exit(1)
    elif response.status_code == 404:
        # TODO: report user 404
        return
    elif response.status_code != 200:
        log(f"<{response.status_code}> {url!r}, params={params}, headers={headers}")
        return
    soup = BeautifulSoup(response.text, features='lxml')

    total = soup.select_one("#content div.article div.mode > span.subject-num")
    if not total:
        # Error
        log("No total number available")
        return
    total = int(re.search(r"(\d+)$", total.text.strip()).group(1))
    items = []
    for item in soup.select("#content div.article ul > li.item"):
        itemId = item['id'].lstrip("list")
        rating = 0
        ratingContainer = item.select("div.date > span")
        for ratingItem in ratingContainer:
            rating = " ".join(ratingItem['class'])
            rating = int(re.search(r"rating(\d*)-t", rating).group(1))
        items.append({'item': itemId, 'rating': rating})

    result = {
        'id': job_id,
        'user': user,
        'type': item_type,
        'total': total,
        'page': page,
        'items': items,
    }
    try:
        requests.post(control_url + "/add-result", json=result)
    except Exception:
        pass
    return result


def main():
    while True:
        jobs = requests.get(control_url + "/get-jobs").json()
        for job in jobs:
            get_item(job['id'], job['user'], job['type'], job['page'])


if __name__ == "__main__":
    main()