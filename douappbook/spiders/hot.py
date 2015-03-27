# -*- coding: utf-8 -*-
import scrapy


class HotSpider(scrapy.Spider):
    name = "hot"
    allowed_domains = ["douban.com"]
    start_urls = (
        'http://www.douban.com/',
    )

    def parse(self, response):
        pass
