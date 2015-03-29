# -*- coding: utf-8 -*-
from douappbook.items import BookItem, RatingItem
from douappbook.models import Book, Rating, CrawledBook


class DouAppBookPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            Book.upsert_book(item)
            crawled_book = CrawledBook.get_book(item['id'])
            if crawled_book:
                rating_count = crawled_book['rating_count']
            else:
                rating_count = 0
            CrawledBook.upsert_book(item['id'], rating_count)
        elif isinstance(item, RatingItem):
            Rating.upsert_rating(item)
            book_rating_ids = Rating.get_book_rating_ids()
            if item['id'] not in book_rating_ids:
                crawled_book = CrawledBook.get_book(item['book_id'])
                if crawled_book:
                    rating_count = crawled_book['rating_count'] + 1
                else:
                    rating_count = 1
                CrawledBook.upsert_book(item['book_id'], rating_count)
        return item
