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

    # These URLs are for testing only
    #start_urls = ["https://ustc.ibugone.com/data/book/1000030-0.html"]
    #start_urls = ["https://ustc.ibugone.com/data/movie/1000030-0.html"]

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
