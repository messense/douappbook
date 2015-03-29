# -*- coding: utf-8 -*-
from __future__ import with_statement, print_function
import os
import sys
try:
    import simplejson as json
except ImportError:
    import json

from scrapy import Request

from douappbook.spiders import DoubanAppSpider
from douappbook.items import BookItem
from douappbook.models import Book


class BookInfoSpider(DoubanAppSpider):
    name = "bookinfo"
    allowed_domains = ["douban.com"]

    def __init__(self, idfile=None, *args, **kwargs):
        super(BookInfoSpider, self).__init__(*args, **kwargs)
        if idfile and not os.path.isabs(idfile):
            cwd = os.getcwd()
            idfile = os.path.join(cwd, idfile)
        if not idfile or not os.path.exists(idfile):
            print('%s file does not exist' % idfile)
            sys.exit(1)

        crawled_ids = Book.get_book_ids()
        self.api_endpoints = []
        with open(idfile) as f:
            for l in f:
                bkid = int(l.strip())
                if bkid in crawled_ids:
                    continue
                self.api_endpoints.append('book/%d' % bkid)

    def start_requests(self):
        for endpoint in self.api_endpoints:
            url = self.get_api_url(endpoint)
            yield Request(url, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        book = BookItem()
        book['id'] = int(res['id'])
        book['title'] = res['title']
        book['author'] = res['author'][0]
        book['url'] = res['url']
        book['cover'] = res['pic']['normal']
        book['rating'] = res['rating']['value']
        book['rating_count'] = res['rating']['count']
        yield book
