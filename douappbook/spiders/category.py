# -*- coding: utf-8 -*-
import scrapy


class CategorySpider(scrapy.Spider):
    name = "category"
    allowed_domains = ["douban.com"]
    start_urls = (
        'http://www.douban.com/',
    )

    def parse(self, response):
        pass
