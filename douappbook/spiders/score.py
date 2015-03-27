# -*- coding: utf-8 -*-
import scrapy


class ScoreSpider(scrapy.Spider):
    name = "score"
    allowed_domains = ["douban.com"]
    start_urls = (
        'http://www.douban.com/',
    )

    def parse(self, response):
        pass
