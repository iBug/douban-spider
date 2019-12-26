import os
import time
import re
import scrapy
import requests
from urllib.parse import urljoin
from ..items import DoubanItem


control_url = os.environ.get("CONTROL_URL", "https://aspqm.taokystrong.com")


class DoubanSpider(scrapy.Spider):
    name = 'doubanspider'
    start_urls = """
https://movie.douban.com/people/dengyigeren/collect?start=6120&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/grinch/collect?start=5370&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/1256612/collect?start=6000&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/a371623866/collect?start=6360&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/1320272/collect?start=6270&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/glim/collect?start=5640&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/luoying6/collect?start=6150&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/funkerv/collect?start=5070&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/ljq513/collect?start=6960&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/mafeisan/collect?start=6600&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/sun1987/collect?start=5130&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/ayumiH/collect?start=7140&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/vivifyvivi/collect?start=6090&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/Yeatsilence/collect?start=5850&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/2040298/collect?start=6150&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/haight/collect?start=6210&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/wendan/collect?start=6090&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/louxing/collect?start=5550&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/RiveGauche/collect?start=6240&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/laomianren/collect?start=6900&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/lsd_XY/collect?start=6120&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/flowermumu/collect?start=5550&sort=time&rating=all&filter=all&mode=list
https://movie.douban.com/people/vyajana/collect?start=6570&sort=time&rating=all&filter=all&mode=list
    """.strip().split()

    def __init__(self):
        # Suicide after first 302 / 403
        self.alive = True
        # Failure count
        self.fc = 0

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
        yield response.follow(nextUrl, self.parse)
