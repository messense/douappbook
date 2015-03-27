# -*- coding: utf-8 -*-
import scrapy


class BookItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    url = scrapy.Field()
    cover = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()


class RatingItem(scrapy.Item):
    id = scrapy.Field()
    book_id = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    rating = scrapy.Field()
    vote = scrapy.Field()
    comment = scrapy.Field()
