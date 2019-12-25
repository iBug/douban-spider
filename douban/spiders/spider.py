import os
import time
import re
import scrapy
import requests
from urllib.parse import urljoin
from ..items import DoubanItem


control_url = os.environ.get("CONTROL_URL", "https://spserver.taokystrong.com")


class DoubanSpider(scrapy.Spider):
    name = 'doubanspider'

    def __init__(self):
        # Suicide after first 302 / 403
        self.alive = True
        # Failure count
        self.fc = 0

    def start_requests(self):
        return [scrapy.FormRequest(
            "https://accounts.douban.com/j/mobile/login/basic",
            formdata={'ck': "", 'name': "+33629474120", 'password': "taokystrong1", 'ticket': ""},
            callback=self.start_crawl,
        )]

    def start_crawl(self, response):
        while self.alive:
            response = requests.get(control_url + "/get_job")
            if response.status_code != 200:
                if self.fc >= 5:
                    self.alive = False
                time.sleep(5)
                self.fc += 1
                continue
            self.fc = 0
            jobs = response.json()
            meta = {'dont_redirect': True}
            if isinstance(jobs, list):
                for job in jobs:
                    yield scrapy.Request(job, meta=meta)
            elif jobs:
                yield scrapy.Request(jobs, meta=meta)
            else:
                break

    def closed(*args, **kwargs):
        # Scrapy 1.7+: Called when spider is closed
        if os.environ.get('SHUTDOWN_ON_ERROR'):
            os.system('poweroff')

    def parse(self, response):
        if response.status in [302, 403]:
            # Should stop now
            self.alive = False

        try:
            userId = response.css('#db-usr-profile div.pic img').xpath('@src').get()
            userId = int(re.search(r"/u(\d+)", userId).group(1))
        except (TypeError, AttributeError):
            # User has canceled their account, retry from URL
            try:
                userId = int(re.search(r"/people/(\d+)/collect", response.request.url).group(1))
            except AttributeError:
                # We're really unlucky now
                requests.post(control_url + "/complete_job", json={
                    'oldUrl': response.request.url,
                    'newUrl': None,
                    'items': [],
                })
                return
        items = []
        for item in response.css('#content div.article ul > li.item'):
            itemId = int(item.xpath('@id').get().lstrip("list"))
            rating = 0
            ratingList = item.css('div.date > span')
            if ratingList:
                rating = ratingList[0].xpath('@class').get()
                rating = int(re.search(r"rating(\d*)-t", rating).group(1))
            items.append({
                'user': userId,
                'item': itemId,
                'rating': rating,
            })
            ret = DoubanItem()
            ret['user'] = userId
            ret['item'] = itemId
            ret['rating'] = rating
            yield ret

        nextUrl = None
        for nextPage in response.css('#content div.article div.paginator > span.next > a'):
            nextUrl = nextPage.xpath('@href').get()
            nextUrl = urljoin(response.request.url, nextUrl)
            # We're not expecting multiple "next page"s
            break
        requests.post(control_url + "/complete_job", json={
            'oldUrl': response.request.url,
            'newUrl': nextUrl,
            'items': items,
        })
