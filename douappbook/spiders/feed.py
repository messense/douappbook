# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

from scrapy import Request

from douappbook.spiders import DoubanAppSpider
from douappbook.items import BookItem


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
            if self.settings['DEBUG']:
                break

        if not self.settings['DEBUG']:
            url = self.get_api_url(
                self.api_endpoint,
                start=start + count,
                count=15
            )
            yield Request(url, callback=self.parse)
