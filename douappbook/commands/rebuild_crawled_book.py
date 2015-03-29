# -*- coding: utf-8 -*-
from scrapy.command import ScrapyCommand

from douappbook.models import CrawledBook


class Command(ScrapyCommand):

    def short_desc(self):
        return 'Rebuild crawled book table'

    def run(self, args, opts):
        CrawledBook.rebuild()
