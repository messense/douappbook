# -*- coding: utf-8 -*-
from scrapy.command import ScrapyCommand

from douappbook.models import Book, Rating, CrawledBook


class Command(ScrapyCommand):

    def short_desc(self):
        return 'Create database tables'

    def run(self, args, opts):
        Book.create_table()
        Rating.create_table()
        CrawledBook.create_table()
