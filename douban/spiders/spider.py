import os
import time
import re
import scrapy
import requests
from urllib.parse import urlparse
from ..items import DoubanItem


control_url = "https://spserver.taokystrong.com"
# Suicide after first 302 / 403
alive = True


class DoubanSpider(scrapy.Spider):
    name = 'doubanspider'

    def start_requests(self):
        return [scrapy.FormRequest(
            "https://accounts.douban.com/j/mobile/login/basic",
            formdata={'ck': "", 'name': "+33629474120", 'password': "taokystrong1", 'ticket': ""},
            callback=self.start_crawl,
        )]

    def start_crawl(self, response):
        while alive:
            response = requests.get(control_url + "/get_url")
            if response.status_code != 200:
                time.sleep(5)
                continue
            yield scrapy.Request(response.text.strip('{["]}\n\t '))

    def closed(*args, **kwargs):
        # Scrapy 1.7+: Called when spider is closed
        if os.environ.get('SHUTDOWN_ON_ERROR'):
            os.system('poweroff')

    def parse(self, response):
        if response.status in [302, 403]:
            # Send the same URL back
            response = requests.post(control_url + "/add_url", json={'url': response.request.url})
            # Should stop now
            alive = False

        try:
            userId = response.css('#db-usr-profile div.pic img').xpath('@src').get()
            userId = int(re.search(r"/u(\d+)", userId).group(1))
        except AttributeError:
            # User has canceled their account, retry from URL
            try:
                userId = int(re.search(r"/people/(\d+)/collect", response.request.url).group(1))
            except AttributeError:
                # We're really unlucky now
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
        requests.post(control_url + "/add_records", json=items)

        for nextPage in response.css('#content div.article div.paginator > span.next > a'):
            nextUrl = nextPage.xpath('@href').get()
            nextUrl = urlparse.urljoin(response.request.url, nextUrl)
            response = requests.post(control_url + "/add_url", json={'url': nextUrl})
