# -*- coding: utf-8 -*-
import scrapy


class FeedSpider(scrapy.Spider):
    name = "feed"
    allowed_domains = ["douban.com"]
    start_urls = (
        'http://www.douban.com/',
    )

    def parse(self, response):
        pass
