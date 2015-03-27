# -*- coding: utf-8 -*-
from douappbook.items import BookItem, RatingItem
from douappbook.models import Book, Rating


class DouAppBookPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            Book.upsert_book(item)
        elif isinstance(item, RatingItem):
            Rating.upsert_rating(item)
        return item
