# -*- coding: utf-8 -*-
import random
try:
    import simplejson as json
except ImportError:
    import json

import furl
from scrapy import Request

from douappbook.spiders import DoubanAppSpider
from douappbook.items import RatingItem
from douappbook.models import CrawledBook


class RatingSpider(DoubanAppSpider):
    name = "rating"
    allowed_domains = ["douban.com"]

    def start_requests(self):
        book_ids = CrawledBook.get_book_ids()
        # randomize book ids
        random.shuffle(book_ids)
        for book_id in book_ids:
            endpoint = 'book/%d/interests' % book_id
            url = self.get_api_url(
                endpoint,
                start=0,
                count=50
            )
            yield Request(url, callback=self.parse)
            if self.settings['DEBUG']:
                break

    def parse(self, response):
        api_url = furl.furl(response.url)
        book_id = int(api_url.path.segments[3])

        res = json.loads(response.body_as_unicode())
        start = res['start']
        count = res['count']
        total = res['total']
        interests = res['interests']
        for item in interests:
            rating = RatingItem()
            rating['id'] = item['id']
            rating['book_id'] = book_id
            rating['user_id'] = item['user']['id']
            rating['username'] = item['user']['uid']
            rating['rating'] = item['rating']['value']
            rating['vote'] = item['vote_count']
            rating['comment'] = item['comment']
            yield rating

        if start + count < total and not self.settings['DEBUG']:
            endpoint = 'book/%d/interests' % book_id
            url = self.get_api_url(
                endpoint,
                start=start + count,
                count=50
            )
            yield Request(url, callback=self.parse)
