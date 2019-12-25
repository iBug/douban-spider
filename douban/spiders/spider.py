import os
import itertools
import re
import scrapy
from ..items import DoubanItem


usersPath = os.path.abspath(__file__)
while not os.path.exists(os.path.join(usersPath, "users.txt")):
    oldPath = usersPath
    usersPath = os.path.dirname(usersPath)
    if usersPath == oldPath:
        # We're at the root of the directory tree
        raise FileNotFoundError("No users.txt found")
# One numeric user ID per line, please
with open(os.path.join(usersPath, "users.txt"), "r") as f:
    users = [int(line) for line in f]

book_urls = [f"https://book.douban.com/people/{user}/collect?mode=list" for user in users]
movie_urls = [f"https://movie.douban.com/people/{user}/collect?mode=list" for user in users]


class DoubanSpider(scrapy.Spider):
    name = 'doubanspider'
    start_urls = itertools.chain.from_iterable(zip(book_urls, movie_urls))

    def start_requests(self):
        return [scrapy.FormRequest(
            "https://accounts.douban.com/j/mobile/login/basic",
            formdata={'ck': "", 'name': "+33629474120", 'password': "taokystrong1", 'ticket': ""},
            callback=self.start_crawl,
        )]

    def start_crawl(self, response):
        yield from map(scrapy.Request, self.start_urls)

    def parse(self, response):
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
        for item in response.css('#content div.article ul > li.item'):
            itemId = int(item.xpath('@id').get().lstrip("list"))
            rating = None
            ratingList = item.css('div.date > span')
            if ratingList:
                rating = ratingList[0].xpath('@class').get()
                rating = int(re.search(r"rating(\d*)-t", rating).group(1))
            ret = DoubanItem()
            ret['user'] = userId
            ret['item'] = itemId
            ret['rating'] = rating
            yield ret

        for nextPage in response.css('#content div.article div.paginator > span.next > a'):
            yield response.follow(nextPage, self.parse)
