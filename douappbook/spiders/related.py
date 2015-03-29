# -*- coding: utf-8 -*-
import random
try:
    import simplejson as json
except ImportError:
    import json

import furl
from scrapy import Request

from douappbook.spiders import DoubanAppSpider
from douappbook.items import BookItem
from douappbook.models import Book


class RelatedSpider(DoubanAppSpider):
    name = "related"
    allowed_domains = ["douban.com"]

    def start_requests(self):
        book_ids = Book.get_book_ids()
        random.shuffle(book_ids)
        for book_id in book_ids:
            endpoint = 'book/%d/related_doulists' % book_id
            url = self.get_api_url(
                endpoint,
                start=0,
                count=50
            )
            yield Request(url, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        start = res['start']
        count = res['count']
        total = res['total']
        doulists = res['doulists']
        if not doulists:
            return
        for doulist in doulists:
            list_id = doulist['id']
            endpoint = 'doulist/%s/items' % list_id
            url = self.get_api_url(
                endpoint,
                start=0,
                count=50
            )
            yield Request(url, callback=self.parse_doulist)
            if self.settings['DEBUG']:
                break

        if start + count < total and not self.settings['DEBUG']:
            _url = furl.furl(response.url)
            _url.args['start'] = start + count
            url = _url.url
            yield Request(url, callback=self.parse)

    def parse_doulist(self, response):
        res = json.loads(response.body_as_unicode())
        start = res['start']
        count = res['count']
        total = res['total']
        items = res['items']
        if not items:
            return
        for item in items:
            foreign_type = item['foreign_type']
            if foreign_type != 'book':
                continue

            foreign_item = item['foreign_item']
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

        if start + count < total and not self.settings['DEBUG']:
            _url = furl.furl(response.url)
            _url.args['start'] = start + count
            url = _url.url
            yield Request(url, callback=self.parse_doulist)
