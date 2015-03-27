# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

import furl
from scrapy import Request

from douappbook.spiders import DoubanAppSpider
from douappbook.items import BookItem, RatingItem


class FeedSpider(DoubanAppSpider):
    name = "feed"
    allowed_domains = ["douban.com"]
    api_endpoint = 'tag/3/items'

    def start_requests(self):
        url = self.get_api_url(
            self.api_endpoint,
            start=0,
            count=15
        )
        yield Request(url, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        if not res:
            return
        start = res['start']
        count = res['count']
        items = res['items']
        if count <= 0 or not items:
            return

        for item in items:
            foreign_type = item['doulist_item']['foreign_type']
            if foreign_type != 'book':
                continue

            foreign_item = item['doulist_item']['foreign_item']
            if not foreign_item['author']:
                continue

            book = BookItem()
            book['id'] = int(foreign_item['id'])
            book['title'] = foreign_item['title']
            book['author'] = foreign_item['author'][0]
            book['url'] = foreign_item['url']
            book['cover'] = foreign_item['pic']['normal']
            book['rating'] = foreign_item['rating']['value']
            book['rating_count'] = foreign_item['rating']['count']
            yield book

            endpoint = 'book/%d/interests' % book['id']
            rating_url = self.get_api_url(
                endpoint,
                start=0,
                count=20
            )
            yield Request(rating_url, callback=self.parse_rating)
            if self.settings['DEBUG']:
                break

        if not self.settings['DEBUG']:
            url = self.get_api_url(
                self.api_endpoint,
                start=start + count,
                count=15
            )
            yield Request(url, callback=self.parse)

    def parse_rating(self, response):
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
                count=20
            )
            yield Request(url, callback=self.parse_rating)
