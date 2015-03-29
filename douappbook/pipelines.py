# -*- coding: utf-8 -*-
from douappbook.items import BookItem, RatingItem
from douappbook.models import Book, Rating, CrawledBook


class DouAppBookPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            Book.upsert_book(item)
            CrawledBook.upsert_book(item['id'], 0)
        elif isinstance(item, RatingItem):
            Rating.upsert_rating(item)
        return item
