import os
import re
import scrapy
from ..items import DoubanItem


usersPath = os.path.abspath(__file__)
while not os.path.exists(os.path.join(usersPath, "users.txt")):
    usersPath = os.path.dirname(usersPath)
# One numeric user ID per line, please
with open(os.path.join(usersPath, "users.txt"), "r") as f:
    users = [int(line) for line in f]

book_urls = [f"https://book.douban.com/people/{user}/collect?mode=list" for user in users]
movie_urls = [f"https://movie.douban.com/people/{user}/collect?mode=list" for user in users]


class DoubanSpider(scrapy.Spider):
    name = 'doubanspider'
    start_urls = book_urls + movie_urls
    download_delay = 1  # 1 second between requests

    # These URLs are for testing only
    #start_urls = ["https://ustc.ibugone.com/data/book/1000030-0.html"]
    #start_urls = ["https://ustc.ibugone.com/data/movie/1000030-0.html"]

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        'Referer': "https://www.douban.com/",
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        userId = response.css('#db-usr-profile div.pic img').xpath('@src').get()
        userId = int(re.search(r"/u(\d+)", userId).group(1))
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
