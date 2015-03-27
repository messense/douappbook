# -*- coding: utf-8 -*-
import scrapy
import furl


class DoubanAppSpider(scrapy.Spider):

    API_BASE_URL = 'https://frodo.douban.com:443/api/v2/'
    DEFAULT_PARAMS = {
        'alt': 'json',
        'apikey': '0ab215a8b1977939201640fa14c66bab',
        'version': '2.4.1',
    }

    def get_api_url(self, endpoint, **params):
        _url = furl.furl(self.API_BASE_URL)
        querys = self.DEFAULT_PARAMS.copy()
        if params:
            querys.update(params)
        _url.add(path=endpoint.split('/'), args=querys)
        return _url.url
