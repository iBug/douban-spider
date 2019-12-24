import regex
import scrapy


with open("users.txt", "r") as f:
    users = [int(line) for line in f]

book_urls = [f"https://book.douban.com/people/{user}/collect" for user in users]
movie_urls = [f"https://movie.douban.com/people/{user}/collect" for user in users]


class BookSpider(scrapy.Spider):
    name = 'bookspider'
    start_urls = book_urls
    start_urls = ["https://ustc.ibugone.com/data/book/1000030-0.html"]

    def parse(self, response):
        userId = response.css('#db-usr-profile div.pic img').xpath('@src').get()
        userId = int(regex.search(r"/u(\d+)", userId).group(1))
        for item in response.css('#content div.article li.item'):
            itemId = int(item.xpath('@id').get().lstrip("list"))
            rating = None
            ratingList = item.css('div.date > span')
            if ratingList:
                rating = ratingList[0].xpath('@class').get()
                rating = int(regex.search(r"rating(\d*)-t", rating).group(1))
            yield {'user': userId, 'item': itemId, 'rating': rating}

        #for next_page in response.css('a.next-posts-link'):
        #    yield response.follow(next_page, self.parse)
